import asyncio
import html
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters,
)

from i18n import DEFAULT_LANG, LANGS, t, tr
from payway import PayWay
from rielpay import RielPay

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x}
# Group ទទួលការកុម្ម៉ង់ (ឧ. -1001234567890)។ សមាជិកក្នុង group អាចចុចប៊ូតុងគ្រប់គ្រងការកុម្ម៉ង់បាន
ORDER_GROUP_ID = int(os.getenv("ORDER_GROUP_ID") or 0)
BOT_TITLE = os.getenv("BOT_TITLE", "SB24 Store")
CONTACT_TEXT = os.getenv("CONTACT_TEXT", "")
ADMIN_LANG = "km"  # សារទៅ admin / group ជាភាសាខ្មែរ

# manual  = រូប QR ABA ផ្ទាល់ខ្លួន + អតិថិជនផ្ញើវិក្កយបត្រ + admin ពិនិត្យ
# rielpay = RielPay (rielpays.com) បង្កើត KHQR និងបញ្ជាក់ការបង់ប្រាក់ដោយស្វ័យប្រវត្តិ
# payway  = ABA PayWay API ផ្ទាល់ (ត្រូវការគណនី merchant PayWay)
PAYMENT_MODE = os.getenv("PAYMENT_MODE", "manual").lower()
AUTO_MODES = ("rielpay", "payway")
QR_LIFETIME_MIN = int(os.getenv("QR_LIFETIME_MIN", "10"))
ABA_QR_IMAGE = BASE_DIR / os.getenv("ABA_QR_IMAGE", "aba_qr.jpg")

# ទំព័របញ្ជូនបន្តទៅ ABA Mobile (ប៊ូតុងតេឡេក្រាមមិនអាចបើក abamobilebank:// ផ្ទាល់បានទេ)
# ឧ. PUBLIC_URL=https://your-app.up.railway.app
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", "8080"))

payway = rielpay = None
if PAYMENT_MODE == "rielpay":
    rielpay = RielPay(os.getenv("RIELPAY_API_KEY", ""))
elif PAYMENT_MODE == "payway":
    payway = PayWay(
        merchant_id=os.getenv("PAYWAY_MERCHANT_ID", ""),
        api_key=os.getenv("PAYWAY_API_KEY", ""),
        sandbox=os.getenv("PAYWAY_SANDBOX", "true").lower() == "true",
    )

SERVICES_FILE = BASE_DIR / "services.json"
# នៅលើ Railway កំណត់ DATA_DIR=/data (Volume) ដើម្បីកុំឱ្យការកុម្ម៉ង់បាត់ពេល redeploy
DATA_DIR = Path(os.getenv("DATA_DIR") or BASE_DIR)
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "orders.json"

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)  # កុំឱ្យ log មាន token
log = logging.getLogger("store")


# ---------- សេវាកម្ម និងទិន្នន័យ ----------
def load_services() -> dict:
    return json.loads(SERVICES_FILE.read_text(encoding="utf-8"))


def find_package(sid: str, pid: str):
    catalog = load_services()
    svc = next((s for s in catalog["services"] if s["id"] == sid), None)
    pkg = next((p for p in svc["packages"] if p["id"] == pid), None) if svc else None
    return svc, pkg, catalog.get("currency", "USD")


def load_data() -> dict:
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    else:
        data = {"orders": {}}
    data.setdefault("langs", {})
    return data


def save_data(data: dict) -> None:
    tmp = DATA_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DATA_FILE)  # សរសេរដោយសុវត្ថិភាព កុំឱ្យ file ខូច


def user_lang(user_id: int) -> str:
    return load_data()["langs"].get(str(user_id), DEFAULT_LANG)


def set_user_lang(user_id: int, lang: str) -> None:
    data = load_data()
    data["langs"][str(user_id)] = lang
    save_data(data)


def new_order_id() -> str:
    # tran_id របស់ PayWay អតិបរមា ២០ តួ
    return "GZ" + datetime.now().strftime("%y%m%d%H%M%S") + f"{secrets.randbelow(100):02d}"


def money(amount: float, currency: str) -> str:
    return f"${amount:,.2f}" if currency.upper() == "USD" else f"{int(amount):,}៛"


def esc(text) -> str:
    return html.escape(str(text))


def status_text(status: str, lang: str) -> str:
    return t(f"status_{status}", lang)


def order_names(o: dict, lang: str) -> tuple:
    """ឈ្មោះសេវាកម្ម និងកញ្ចប់ តាមភាសា (ប្រើឈ្មោះដែលបានរក្សាទុក ប្រសិនបើត្រូវបានលុបពី services.json)"""
    svc, pkg, _ = find_package(o["service_id"], o["package_id"])
    return (tr(svc["name"], lang) if svc else o["service_name"],
            tr(pkg["name"], lang) if pkg else o["package_name"])


def order_summary(o: dict, lang: str) -> str:
    service, package = order_names(o, lang)
    return (f"🧾 <b>{t('lbl_order', lang)}:</b> <code>{o['id']}</code>\n"
            f"🛒 {esc(service)}\n"
            f"📦 {esc(package)}\n"
            f"💵 <b>{money(o['price'], o['currency'])}</b>\n"
            f"📝 {esc(o['info'])}")


# ---------- ប៊ូតុង ----------
def main_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_services", lang), callback_data="services")],
        [InlineKeyboardButton(t("btn_orders", lang), callback_data="orders"),
         InlineKeyboardButton(t("btn_contact", lang), callback_data="contact")],
        [InlineKeyboardButton(t("btn_help", lang), callback_data="help"),
         InlineKeyboardButton(t("btn_lang", lang), callback_data="lang")],
    ])


def lang_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(name, callback_data=f"lang:{code}")
                                  for code, name in LANGS.items()]])


def back_button(lang: str) -> list:
    return [InlineKeyboardButton(t("btn_back", lang), callback_data="menu")]


def back_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([back_button(lang)])


def admin_buttons(o: dict):
    oid = o["id"]
    if o["status"] == "review":
        return InlineKeyboardMarkup([[InlineKeyboardButton("✅ ត្រឹមត្រូវ", callback_data=f"adm:approve:{oid}"),
                                      InlineKeyboardButton("🚫 មិនត្រឹមត្រូវ", callback_data=f"adm:reject:{oid}")]])
    if o["status"] == "paid":
        return InlineKeyboardMarkup([[InlineKeyboardButton("🚀 ចាប់ផ្តើមធ្វើ", callback_data=f"adm:start:{oid}")]])
    if o["status"] == "working":
        return InlineKeyboardMarkup([[InlineKeyboardButton("✅ រួចរាល់", callback_data=f"adm:done:{oid}")]])
    return None


# ---------- អត្ថបទ ----------
def welcome_text(lang: str) -> str:
    return t("welcome", lang, title=esc(BOT_TITLE), services=t("btn_services", lang),
             orders=t("btn_orders", lang), contact=t("btn_contact", lang))


def help_text(lang: str) -> str:
    key = "help_auto" if PAYMENT_MODE in AUTO_MODES else "help_manual"
    return t(key, lang, help=t("btn_help", lang), services=t("btn_services", lang))


def customer_line(o: dict) -> str:
    """សម្រាប់ admin: អតិថិជនជានរណា និងប្រើភាសាអ្វី"""
    who = f"@{o['username']}" if o.get("username") else esc(o["user_name"])
    return f"👤 {who} (ID {o['user_id']}) · {LANGS.get(o.get('lang', DEFAULT_LANG), '')}"


# ---------- ការបង់ប្រាក់ ----------
async def notify_admins(bot, text: str, markup=None, photo=None) -> None:
    """ផ្ញើទៅ group ទទួលការកុម្ម៉ង់ (បើមាន) បើមិនដូច្នោះទេ ផ្ញើទៅ admin ម្នាក់ៗ"""
    for admin_id in ([ORDER_GROUP_ID] if ORDER_GROUP_ID else ADMIN_IDS):
        try:
            if photo:
                await bot.send_photo(admin_id, photo, caption=text, parse_mode=ParseMode.HTML, reply_markup=markup)
            else:
                await bot.send_message(admin_id, text, parse_mode=ParseMode.HTML, reply_markup=markup)
        except Exception as e:
            log.warning("Could not notify admin %s: %s", admin_id, e)


async def notify_customer(bot, o: dict, key: str, menu: bool = True, **kwargs) -> None:
    lang = o.get("lang", DEFAULT_LANG)
    try:
        await bot.send_message(o["user_id"], t(key, lang, oid=o["id"], **kwargs), parse_mode=ParseMode.HTML,
                               reply_markup=main_menu(lang) if menu else None)
    except Exception as e:
        log.warning("Could not notify customer %s: %s", o["user_id"], e)


async def mark_paid(bot, oid: str, via: str) -> bool:
    data = load_data()
    o = data["orders"].get(oid)
    # "cancelled": អតិថិជនចុចបោះបង់ តែនៅតែ scan QR បង់ប្រាក់ — នៅតែទទួលយក
    if not o or o["status"] not in ("pending", "review", "cancelled"):
        return False  # បានបញ្ជាក់រួចហើយ (កុំជូនដំណឹងពីរដង)
    o["status"] = "paid"
    o["paid_at"] = datetime.now().isoformat(timespec="seconds")
    o["paid_via"] = via
    save_data(data)

    await notify_customer(bot, o, "paid", summary=order_summary(o, o.get("lang", DEFAULT_LANG)))
    await notify_admins(bot, f"💰 <b>ការកុម្ម៉ង់ថ្មីបានបង់ប្រាក់</b> ({via})\n{customer_line(o)}\n\n"
                             f"{order_summary(o, ADMIN_LANG)}", admin_buttons(o))
    return True


def qr_png(qr_string: str) -> bytes:
    import qrcode
    buf = BytesIO()
    qrcode.make(qr_string, box_size=10, border=3).save(buf, format="PNG")
    return buf.getvalue()


async def create_auto_payment(o: dict) -> dict:
    """ត្រឡប់ {'ref', 'qr_image', 'checkout_url', 'deeplink'}"""
    if PAYMENT_MODE == "rielpay":
        service, package = order_names(o, "en")
        p = await rielpay.create_payment(o["id"], o["price"], o["currency"], QR_LIFETIME_MIN,
                                         f"{service} - {package} ({o['id']})")
        return {"ref": p["id"], "qr_image": qr_png(p["qr_string"]), "checkout_url": p.get("checkout_url"),
                "deeplink": p.get("deeplink")}
    qr = await payway.generate_qr(o["id"], o["price"], o["currency"], QR_LIFETIME_MIN)
    return {"ref": o["id"], "qr_image": qr["qr_image"] or qr_png(qr["qr_string"]), "checkout_url": None,
            "deeplink": qr.get("deeplink")}


async def check_auto_payment(o: dict) -> tuple:
    """ត្រឡប់ (state, amount) — state: paid | pending | expired"""
    if PAYMENT_MODE == "rielpay":
        p = await rielpay.get_payment(o["ref"])
        state = {"paid": "paid", "expired": "expired", "failed": "expired"}.get(p.get("status"), "pending")
        return state, p.get("amount")
    r = await payway.check_transaction(o["ref"])
    return ("paid" if r["paid"] else "pending"), r["amount"]


async def check_payment_once(bot, oid: str) -> str:
    """ពិនិត្យម្តង។ ត្រឡប់ state ចុងក្រោយ"""
    o = load_data()["orders"].get(oid)
    if not o or o["status"] not in WATCHED or not o.get("ref"):
        return "done"
    state, amount = await check_auto_payment(o)
    if state == "paid":
        if amount is not None and float(amount) + 0.001 < o["price"]:
            data = load_data()
            if not data["orders"][oid].get("underpaid_notified"):  # ជូនដំណឹងតែម្តង
                data["orders"][oid]["underpaid_notified"] = True
                save_data(data)
                log.warning("Order %s paid %s but price is %s", oid, amount, o["price"])
                await notify_admins(bot, f"⚠️ ការកុម្ម៉ង់ <code>{oid}</code> បង់ {amount} "
                                         f"តែតម្លៃគឺ {money(o['price'], o['currency'])}។ សូមពិនិត្យ។")
            return "pending"
        await mark_paid(bot, oid, PAYMENT_MODE)
    return state


async def expire_order(bot, oid: str) -> None:
    data = load_data()
    o = data["orders"][oid]
    if o["status"] != "pending":
        return
    o["status"] = "expired"
    save_data(data)
    await notify_customer(bot, o, "qr_expired")


# QR របស់ការកុម្ម៉ង់ដែលបានបោះបង់ នៅតែអាចបង់បាន រហូតដល់ផុតកំណត់
WATCHED = ("pending", "cancelled")


async def poll_payment(bot, oid: str) -> None:
    """ពិនិត្យរៀងរាល់ ៥ វិនាទី រហូតបង់ ឬ QR ផុតកំណត់"""
    while True:
        o = load_data()["orders"].get(oid)
        if not o or o["status"] not in WATCHED:
            return
        if datetime.now() > datetime.fromisoformat(o["expires_at"]) + timedelta(seconds=30):
            break
        try:
            state = await check_payment_once(bot, oid)
            if state == "paid" or state == "done":
                return
            if state == "expired":
                break
        except Exception as e:
            log.warning("Payment check for %s failed: %s", oid, e)
        await asyncio.sleep(5)
    await expire_order(bot, oid)


async def send_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, o: dict) -> None:
    chat_id = update.effective_chat.id
    lang = o.get("lang", DEFAULT_LANG)
    summary = order_summary(o, lang)
    pay_buttons = [InlineKeyboardButton(t("btn_cancel_order", lang), callback_data=f"cancel:{o['id']}")]

    if PAYMENT_MODE in AUTO_MODES:
        try:
            pay = await create_auto_payment(o)
        except Exception as e:
            log.error("generate_qr failed for %s: %s", o["id"], e)
            data = load_data()
            data["orders"][o["id"]]["status"] = "cancelled"
            save_data(data)
            await context.bot.send_message(chat_id, t("qr_failed", lang), reply_markup=main_menu(lang))
            return
        data = load_data()
        data["orders"][o["id"]]["ref"] = pay["ref"]
        data["orders"][o["id"]]["deeplink"] = pay.get("deeplink")
        save_data(data)
        rows = []
        if PUBLIC_URL and pay.get("deeplink"):
            # បើក ABA Mobile ភ្លាមៗ តាមរយៈទំព័របញ្ជូនបន្តរបស់ bot
            rows.append([InlineKeyboardButton(t("btn_open_aba", lang), url=f"{PUBLIC_URL}/aba/{o['id']}")])
        elif pay.get("checkout_url"):
            # គ្មាន PUBLIC_URL ឬគ្មាន deeplink (test mode) — ប្រើទំព័របង់ប្រាក់របស់ RielPay
            rows.append([InlineKeyboardButton(t("btn_open_aba", lang), url=pay["checkout_url"])])
        rows.append(pay_buttons)  # bot ពិនិត្យការបង់ប្រាក់ដោយស្វ័យប្រវត្តិ — មិនចាំបាច់មានប៊ូតុងពិនិត្យ
        await context.bot.send_photo(chat_id, BytesIO(pay["qr_image"]),
                                     caption=t("pay_auto", lang, summary=summary, minutes=QR_LIFETIME_MIN),
                                     parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(rows))
        context.application.create_task(poll_payment(context.bot, o["id"]))
        return

    # manual: QR ផ្ទាល់ខ្លួន + វិក្កយបត្រ
    context.user_data["receipt_for"] = o["id"]
    caption = t("pay_manual", lang, summary=summary, amount=money(o["price"], o["currency"]), oid=o["id"])
    markup = InlineKeyboardMarkup([pay_buttons])
    if ABA_QR_IMAGE.exists():
        with ABA_QR_IMAGE.open("rb") as f:
            await context.bot.send_photo(chat_id, f, caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
    else:
        log.warning("ABA QR image not found: %s", ABA_QR_IMAGE)
        await context.bot.send_message(chat_id, caption, parse_mode=ParseMode.HTML, reply_markup=markup)


# ---------- សម្រាប់អ្នកប្រើប្រាស់ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """រាល់ពេល /start ឱ្យជ្រើសរើសភាសាមុន"""
    context.user_data.clear()
    await update.message.reply_text(t("lang_prompt", DEFAULT_LANG), reply_markup=lang_menu())


async def language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(t("lang_prompt", DEFAULT_LANG), reply_markup=lang_menu())


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    action = q.data
    user = q.from_user

    if action.startswith("adm:"):
        await on_admin_button(update, context)
        return

    if action.startswith("lang:"):
        lang = action.split(":", 1)[1]
        if lang not in LANGS:
            lang = DEFAULT_LANG
        set_user_lang(user.id, lang)
        await q.answer(t("lang_set", lang))
        try:
            await q.edit_message_text(welcome_text(lang), parse_mode=ParseMode.HTML, reply_markup=main_menu(lang))
        except BadRequest:
            await q.message.reply_text(welcome_text(lang), parse_mode=ParseMode.HTML, reply_markup=main_menu(lang))
        return

    lang = user_lang(user.id)

    async def show(text: str, markup: InlineKeyboardMarkup = None) -> None:
        try:
            await q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=markup or back_menu(lang))
        except BadRequest as e:
            if "not modified" in str(e):
                return
            # សារជារូបភាព (QR) កែអត្ថបទមិនបាន — ផ្ញើសារថ្មីជំនួស
            await q.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=markup or back_menu(lang))

    if action.startswith("check:"):
        oid = action.split(":", 1)[1]
        paid = False
        if PAYMENT_MODE in AUTO_MODES:
            try:
                paid = await check_payment_once(context.bot, oid) == "paid"
            except Exception as e:
                log.warning("Manual check for %s failed: %s", oid, e)
        o = load_data()["orders"].get(oid)
        if not paid and o and o["status"] == "pending":
            await q.answer(t("not_paid_yet", lang), show_alert=True)
        else:
            await q.answer()
        return

    await q.answer()

    if action == "menu":
        context.user_data.pop("draft", None)
        await show(welcome_text(lang), main_menu(lang))

    elif action == "lang":
        await show(t("lang_prompt", lang), InlineKeyboardMarkup([*lang_menu().inline_keyboard, back_button(lang)]))

    elif action == "services":
        catalog = load_services()
        rows = [[InlineKeyboardButton(tr(s["name"], lang), callback_data=f"svc:{s['id']}")] for s in catalog["services"]]
        await show(f"<b>{t('btn_services', lang)}</b>\n\n{t('choose_service', lang)}",
                   InlineKeyboardMarkup(rows + [back_button(lang)]))

    elif action.startswith("svc:"):
        sid = action.split(":", 1)[1]
        catalog = load_services()
        svc = next((s for s in catalog["services"] if s["id"] == sid), None)
        if not svc:
            await show(welcome_text(lang), main_menu(lang))
            return
        cur = catalog.get("currency", "USD")
        lines = [f"📦 <b>{esc(tr(p['name'], lang))}</b> — {money(p['price'], cur)}\n    "
                 + esc(tr(p.get("detail", ""), lang)).replace("\n", "\n    ")
                 for p in svc["packages"]]
        rows = [[InlineKeyboardButton(f"{tr(p['name'], lang)} — {money(p['price'], cur)}",
                                      callback_data=f"pkg:{sid}:{p['id']}")] for p in svc["packages"]]
        rows.append([InlineKeyboardButton(f"⬅️ {t('btn_services', lang)}", callback_data="services")])
        await show(f"<b>{esc(tr(svc['name'], lang))}</b>\n\n{esc(tr(svc['description'], lang))}\n\n"
                   + "\n\n".join(lines) + f"\n\n{t('choose_package', lang)}",
                   InlineKeyboardMarkup(rows + [back_button(lang)]))

    elif action.startswith("pkg:"):
        _, sid, pid = action.split(":")
        svc, pkg, cur = find_package(sid, pid)
        if not pkg:
            await show(welcome_text(lang), main_menu(lang))
            return
        context.user_data["draft"] = {"sid": sid, "pid": pid}
        await show(f"<b>{esc(tr(svc['name'], lang))}</b>\n📦 {esc(tr(pkg['name'], lang))} — {money(pkg['price'], cur)}"
                   f"\n\n{esc(tr(svc['ask'], lang))}",
                   InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_cancel", lang), callback_data="menu")]]))

    elif action == "pay":
        draft = context.user_data.pop("draft", None)
        svc, pkg, cur = find_package(draft["sid"], draft["pid"]) if draft else (None, None, None)
        if not pkg or not draft.get("info"):
            await show(t("draft_expired", lang), main_menu(lang))
            return
        o = {"id": new_order_id(), "user_id": user.id, "user_name": user.full_name, "username": user.username,
             "lang": lang, "service_id": svc["id"], "service_name": tr(svc["name"], ADMIN_LANG),
             "package_id": pkg["id"], "package_name": tr(pkg["name"], ADMIN_LANG),
             "price": float(pkg["price"]), "currency": cur,
             "info": draft["info"], "status": "pending", "mode": PAYMENT_MODE,
             "created_at": datetime.now().isoformat(timespec="seconds"),
             "expires_at": (datetime.now() + timedelta(minutes=QR_LIFETIME_MIN)).isoformat(timespec="seconds")}
        data = load_data()
        data["orders"][o["id"]] = o
        save_data(data)
        await show(t("order_created", lang, oid=o["id"]), InlineKeyboardMarkup([]))
        await send_payment(update, context, o)

    elif action.startswith("cancel:"):
        oid = action.split(":", 1)[1]
        data = load_data()
        o = data["orders"].get(oid)
        if o and o["user_id"] == user.id and o["status"] in ("pending", "review"):
            o["status"] = "cancelled"
            save_data(data)
            context.user_data.pop("receipt_for", None)
            await q.message.reply_text(t("cancelled", lang, oid=oid), parse_mode=ParseMode.HTML,
                                       reply_markup=main_menu(lang))
        else:
            await q.message.reply_text(t("cannot_cancel", lang), reply_markup=main_menu(lang))

    elif action == "orders":
        mine = [o for o in load_data()["orders"].values() if o["user_id"] == user.id]
        mine.sort(key=lambda o: o["created_at"], reverse=True)
        blocks = []
        for o in mine[:10]:
            service, package = order_names(o, lang)
            blocks.append(f"🧾 <code>{o['id']}</code> · {status_text(o['status'], lang)}\n"
                          f"    {esc(service)} · {esc(package)} · {money(o['price'], o['currency'])}")
        body = "\n\n".join(blocks) or t("no_orders", lang)
        await show(f"<b>{t('btn_orders', lang)}</b>\n\n{body}")

    elif action == "contact":
        await show(f"<b>{t('btn_contact', lang)}</b>\n\n{esc(CONTACT_TEXT) or t('no_contact', lang)}")

    elif action == "help":
        await show(help_text(lang))


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = user_lang(update.effective_user.id)
    draft = context.user_data.get("draft")
    if not draft:
        await update.message.reply_text(t("choose_from_menu", lang), reply_markup=main_menu(lang))
        return
    svc, pkg, cur = find_package(draft["sid"], draft["pid"])
    if not pkg:
        context.user_data.pop("draft", None)
        await update.message.reply_text(t("package_gone", lang), reply_markup=main_menu(lang))
        return
    draft["info"] = update.message.text.strip()[:1000]
    summary = (f"🛒 {esc(tr(svc['name'], lang))}\n📦 {esc(tr(pkg['name'], lang))}\n"
               f"💵 <b>{money(pkg['price'], cur)}</b>\n📝 {esc(draft['info'])}")
    await update.message.reply_text(
        t("confirm", lang, summary=summary), parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_pay", lang), callback_data="pay")],
            [InlineKeyboardButton(t("btn_cancel", lang), callback_data="menu")],
        ]))


async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """manual mode: អតិថិជនផ្ញើរូបថតវិក្កយបត្រ"""
    lang = user_lang(update.effective_user.id)
    oid = context.user_data.get("receipt_for")
    data = load_data()
    o = data["orders"].get(oid) if oid else None
    if not o or o["status"] != "pending":
        await update.message.reply_text(t("choose_from_menu", lang), reply_markup=main_menu(lang))
        return
    photo = update.message.photo[-1].file_id
    o["status"] = "review"
    o["receipt_file_id"] = photo
    save_data(data)
    context.user_data.pop("receipt_for", None)

    await update.message.reply_text(t("receipt_received", lang, oid=oid), parse_mode=ParseMode.HTML,
                                    reply_markup=main_menu(lang))
    await notify_admins(context.bot, f"🔍 <b>សូមពិនិត្យការបង់ប្រាក់</b>\n{customer_line(o)}\n\n"
                                     f"{order_summary(o, ADMIN_LANG)}", admin_buttons(o), photo=photo)


# ---------- សម្រាប់អ្នកគ្រប់គ្រង (ភាសាខ្មែរ) ----------
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def can_manage(update: Update) -> bool:
    """admin ឬសមាជិកណាមួយក្នុង group ទទួលការកុម្ម៉ង់"""
    return is_admin(update.effective_user.id) or (
        ORDER_GROUP_ID != 0 and update.effective_chat is not None and update.effective_chat.id == ORDER_GROUP_ID)


async def on_admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not can_manage(update):
        await q.answer("⛔️", show_alert=True)
        return
    _, act, oid = q.data.split(":", 2)
    data = load_data()
    o = data["orders"].get(oid)
    if not o:
        await q.answer("រកមិនឃើញការកុម្ម៉ង់", show_alert=True)
        return
    before = o["status"]

    if act == "approve":
        ok = await mark_paid(context.bot, oid, "admin")
        await q.answer("✅ បានបញ្ជាក់" if ok else "បានដំណើរការរួចហើយ")
    elif act == "reject" and o["status"] == "review":
        o["status"] = "rejected"
        save_data(data)
        await notify_customer(context.bot, o, "rejected")
        await q.answer("🚫 បានបដិសេធ")
    elif act == "start" and o["status"] == "paid":
        o["status"] = "working"
        save_data(data)
        await notify_customer(context.bot, o, "started", menu=False)
        await q.answer("🚀 កំពុងដំណើរការ")
    elif act == "done" and o["status"] == "working":
        o["status"] = "done"
        save_data(data)
        await notify_customer(context.bot, o, "done")
        await q.answer("✅ រួចរាល់")
    else:
        await q.answer("ស្ថានភាពបានផ្លាស់ប្តូររួចហើយ")

    # ធ្វើបច្ចុប្បន្នភាពប៊ូតុងលើសាររបស់ admin
    o = load_data()["orders"][oid]
    try:
        await q.edit_message_reply_markup(admin_buttons(o))
    except BadRequest:
        pass
    if o["status"] != before:
        # កត់ត្រាថានរណាបានធ្វើ (មានប្រយោជន៍ពេលមានបុគ្គលិកច្រើននាក់ក្នុង group)
        who = f"@{q.from_user.username}" if q.from_user.username else esc(q.from_user.full_name)
        await q.message.reply_text(f"{status_text(o['status'], ADMIN_LANG)} · <code>{oid}</code> · ដោយ {who}",
                                   parse_mode=ParseMode.HTML)


ADMIN_HELP = (
    "🛠 <b>ពាក្យបញ្ជាអ្នកគ្រប់គ្រង</b>\n\n"
    "/orders — ការកុម្ម៉ង់ដែលកំពុងដំណើរការ\n"
    "/groupid — លេខ group (វាយក្នុង group ទទួលការកុម្ម៉ង់)\n"
    "/msg លេខកុម្ម៉ង់ សារ — ផ្ញើសារទៅអតិថិជន (ឧ. ប្រគល់ Bot)\n\n"
    "ប៊ូតុងលើការកុម្ម៉ង់នីមួយៗ៖\n"
    "✅ ត្រឹមត្រូវ / 🚫 មិនត្រឹមត្រូវ → 🚀 ចាប់ផ្តើមធ្វើ → ✅ រួចរាល់\n\n"
    "កែតម្លៃ និងកញ្ចប់ នៅក្នុង file <code>services.json</code>\n"
    "កែអត្ថបទ ៣ ភាសា នៅក្នុង file <code>i18n.py</code>"
)


async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if can_manage(update):
        await update.message.reply_text(ADMIN_HELP, parse_mode=ParseMode.HTML)


async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not can_manage(update):
        return
    active = [o for o in load_data()["orders"].values() if o["status"] in ("review", "paid", "working")]
    if not active:
        await update.message.reply_text("🎉 គ្មានការកុម្ម៉ង់ដែលត្រូវធ្វើទេ។")
        return
    for o in sorted(active, key=lambda o: o["created_at"])[:20]:
        await update.message.reply_text(f"{status_text(o['status'], ADMIN_LANG)}\n{customer_line(o)}\n\n"
                                        f"{order_summary(o, ADMIN_LANG)}",
                                        parse_mode=ParseMode.HTML, reply_markup=admin_buttons(o))


async def message_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not can_manage(update):
        return
    parts = update.message.text.split(maxsplit=2)
    o = load_data()["orders"].get(parts[1]) if len(parts) == 3 else None
    if not o:
        await update.message.reply_text("របៀបប្រើ៖ /msg លេខកុម្ម៉ង់ សារ")
        return
    await notify_customer(context.bot, o, "staff_message", menu=False, text=esc(parts[2]))
    await update.message.reply_text("✅ បានផ្ញើ។")


async def group_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """វាយ /groupid ក្នុង group ដើម្បីដឹងលេខ ORDER_GROUP_ID"""
    chat = update.effective_chat
    if chat.type == "private":
        await update.message.reply_text("សូមបន្ថែម bot ទៅក្នុង group រួចវាយ /groupid នៅទីនោះ។")
        return
    await update.message.reply_text(
        f"🆔 ORDER_GROUP_ID={chat.id}\n\nដាក់បន្ទាត់នេះក្នុង .env រួច restart bot។"
        + ("\n\n✅ Group នេះកំពុងទទួលការកុម្ម៉ង់។" if chat.id == ORDER_GROUP_ID else ""))


async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"🆔 {update.effective_user.id}")


# ---------- ទំព័របើក ABA Mobile ----------
ABA_PAGE = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ABA Mobile</title>
<style>
  body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       font-family:system-ui,sans-serif;background:#0b3d59;color:#fff;text-align:center}}
  .box{{padding:24px;max-width:360px}}
  a.btn{{display:block;margin:20px 0 12px;padding:16px;border-radius:12px;background:#e21a22;
        color:#fff;font-size:18px;font-weight:700;text-decoration:none}}
  p{{opacity:.85;line-height:1.6}}
</style></head>
<body><div class="box">
  <h2>{title}</h2>
  <p>{text}</p>
  {button}
</div>
{script}
</body></html>"""


async def aba_redirect(request):
    """GET /aba/<order_id> → បើក ABA Mobile ភ្លាមៗ"""
    from aiohttp import web
    o = load_data()["orders"].get(request.match_info["oid"])
    lang = (o or {}).get("lang", DEFAULT_LANG)
    if not o or o["status"] != "pending" or not o.get("deeplink"):
        page = ABA_PAGE.format(lang=lang, title=t("page_expired_title", lang), text=t("page_expired_text", lang),
                               button="", script="")
        return web.Response(text=page, content_type="text/html", status=410)
    link = html.escape(o["deeplink"], quote=True)
    page = ABA_PAGE.format(
        lang=lang, title=t("page_opening_title", lang),
        text=t("page_opening_text", lang, amount=money(o["price"], o["currency"]), oid=o["id"]),
        button=f'<a class="btn" href="{link}">{t("page_button", lang)}</a>',
        script=f"<script>location.href={json.dumps(o['deeplink'])};</script>")
    return web.Response(text=page, content_type="text/html", headers={"Cache-Control": "no-store"})


async def start_web_server(app: Application) -> None:
    from aiohttp import web
    web_app = web.Application()
    web_app.router.add_get("/aba/{oid}", aba_redirect)
    web_app.router.add_get("/", lambda r: web.Response(text="ok"))
    runner = web.AppRunner(web_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    app.bot_data["web_runner"] = runner
    log.info("ABA deeplink page on port %s → %s/aba/<order_id>", PORT, PUBLIC_URL)


async def post_shutdown(app: Application) -> None:
    runner = app.bot_data.get("web_runner")
    if runner:
        await runner.cleanup()


async def post_init(app: Application) -> None:
    # ម៉ឺនុយពាក្យបញ្ជា តាមភាសាកម្មវិធីតេឡេក្រាមរបស់អ្នកប្រើ
    for code in (None, "en", "zh"):
        lang = code or DEFAULT_LANG
        await app.bot.set_my_commands([BotCommand("start", t("cmd_start", lang)),
                                       BotCommand("language", t("cmd_language", lang))], language_code=code)
    if PUBLIC_URL and PAYMENT_MODE in AUTO_MODES:
        await start_web_server(app)
    if PAYMENT_MODE in AUTO_MODES:
        # បន្តពិនិត្យការកុម្ម៉ង់ដែលកំពុងរង់ចាំ បន្ទាប់ពី restart
        now = datetime.now()
        for o in load_data()["orders"].values():
            if (o["status"] in WATCHED and o.get("mode") == PAYMENT_MODE and o.get("ref")
                    and now < datetime.fromisoformat(o["expires_at"]) + timedelta(seconds=30)):
                app.create_task(poll_payment(app.bot, o["id"]))


# ---------- ចាប់ផ្តើម ----------
def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN missing – copy .env.example to .env and add your token")
    if PAYMENT_MODE not in ("manual",) + AUTO_MODES:
        raise SystemExit("PAYMENT_MODE must be manual, rielpay or payway")
    if PAYMENT_MODE == "rielpay" and not os.getenv("RIELPAY_API_KEY"):
        raise SystemExit("PAYMENT_MODE=rielpay needs RIELPAY_API_KEY (sk_...)")
    if PAYMENT_MODE == "payway" and not (payway.merchant_id and payway.api_key):
        raise SystemExit("PAYMENT_MODE=payway needs PAYWAY_MERCHANT_ID and PAYWAY_API_KEY")
    load_services()  # បញ្ឈប់ឥឡូវ ប្រសិនបើ services.json ខុស

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", language_cmd))
    app.add_handler(CommandHandler("myid", my_id))
    app.add_handler(CommandHandler("groupid", group_id))
    app.add_handler(CommandHandler("admin", admin_help))
    app.add_handler(CommandHandler("orders", list_orders))
    app.add_handler(CommandHandler("msg", message_customer))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, on_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, on_text))

    log.info("%s is running (payment mode: %s, orders → %s)…", BOT_TITLE, PAYMENT_MODE,
             f"group {ORDER_GROUP_ID}" if ORDER_GROUP_ID else "admins")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
