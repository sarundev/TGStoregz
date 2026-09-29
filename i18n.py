"""អត្ថបទសម្រាប់អតិថិជន ជា ៣ ភាសា: km (ខ្មែរ), en (English), zh (中文)

កែអត្ថបទនៅទីនេះ។ ប្រើ {name} សម្រាប់តម្លៃដែល bot បំពេញ។
"""

LANGS = {"km": "🇰🇭 ខ្មែរ", "en": "🇬🇧 English", "zh": "🇨🇳 中文"}
DEFAULT_LANG = "km"

TEXTS = {
    # ---------- ប៊ូតុង ----------
    "btn_services": {"km": "🚀 សេវាកម្ម", "en": "🚀 Services", "zh": "🚀 服务"},
    "btn_orders": {"km": "📋 ការកុម្ម៉ង់ខ្ញុំ", "en": "📋 My Orders", "zh": "📋 我的订单"},
    "btn_contact": {"km": "📨 ទំនាក់ទំនង", "en": "📨 Contact", "zh": "📨 联系我们"},
    "btn_help": {"km": "💡 ជំនួយ", "en": "💡 Help", "zh": "💡 帮助"},
    "btn_lang": {"km": "🌐 ភាសា", "en": "🌐 Language", "zh": "🌐 语言"},
    "btn_channel": {"km": "📣 Channel របស់យើង", "en": "📣 Our Channel", "zh": "📣 官方频道"},
    "btn_back": {"km": "🏠 ម៉ឺនុយដើម", "en": "🏠 Main Menu", "zh": "🏠 主菜单"},
    "btn_prev_services": {"km": "↩️ សេវាកម្មទាំងអស់", "en": "↩️ All Services", "zh": "↩️ 全部服务"},
    "btn_cancel": {"km": "✖️ បោះបង់", "en": "✖️ Cancel", "zh": "✖️ 取消"},
    "btn_pay": {"km": "💳 បង់ប្រាក់ឥឡូវនេះ · ABA KHQR", "en": "💳 Pay Now · ABA KHQR", "zh": "💳 立即付款 · ABA KHQR"},
    "btn_crypto": {"km": "🪙 បង់ប្រាក់ជាមួយ Crypto", "en": "🪙 Pay with Crypto", "zh": "🪙 使用加密货币付款"},
    "crypto_message": {
        "km": "សួស្តី! ខ្ញុំចង់បង់ប្រាក់ជាមួយ Crypto សម្រាប់៖\n🛒 {service}\n📦 {package}\n💵 {price}\n📝 {info}",
        "en": "Hi! I'd like to pay with crypto for:\n🛒 {service}\n📦 {package}\n💵 {price}\n📝 {info}",
        "zh": "您好！我想用加密货币支付：\n🛒 {service}\n📦 {package}\n💵 {price}\n📝 {info}",
    },
    "btn_cancel_order": {"km": "✖️ បោះបង់ការកុម្ម៉ង់", "en": "✖️ Cancel Order", "zh": "✖️ 取消订单"},
    "btn_check": {"km": "🔄 ពិនិត្យការបង់ប្រាក់", "en": "🔄 Check Payment", "zh": "🔄 查询付款"},
    "btn_open_aba": {"km": "📲 បង់ក្នុង ABA Mobile", "en": "📲 Pay in ABA Mobile", "zh": "📲 在 ABA Mobile 付款"},

    # ---------- ភាសា ----------
    "lang_prompt": {"km": "🌐 សូមជ្រើសរើសភាសា\nPlease choose your language\n请选择语言",
                    "en": "🌐 សូមជ្រើសរើសភាសា\nPlease choose your language\n请选择语言",
                    "zh": "🌐 សូមជ្រើសរើសភាសា\nPlease choose your language\n请选择语言"},
    "lang_set": {"km": "✅ បានប្តូរភាសាជា ខ្មែរ", "en": "✅ Language set to English", "zh": "✅ 语言已设置为中文"},

    # ---------- ម៉ឺនុយ ----------
    "welcome": {
        "km": "✈️ <b>{title}</b>\n\nសេវាកម្មតេឡេក្រាម បង់ប្រាក់ងាយស្រួលតាម <b>ABA KHQR &amp; Crypto</b>។\n\n"
              "<b>{services}</b> — មើល និងកុម្ម៉ង់សេវាកម្ម។\n"
              "<b>{orders}</b> — តាមដានស្ថានភាពការកុម្ម៉ង់។\n"
              "<b>{contact}</b> — ទាក់ទងក្រុមការងារ។\n\n"
              "👇 សូមជ្រើសរើសជម្រើសខាងក្រោម។",
        "en": "✈️ <b>{title}</b>\n\nTelegram services with easy payment via <b>ABA KHQR &amp; Crypto</b>.\n\n"
              "<b>{services}</b> — browse and order services.\n"
              "<b>{orders}</b> — track your order status.\n"
              "<b>{contact}</b> — reach our team.\n\n"
              "👇 Please choose an option below.",
        "zh": "✈️ <b>{title}</b>\n\nTelegram 服务，通过 <b>ABA KHQR 和加密货币</b> 轻松付款。\n\n"
              "<b>{services}</b> — 浏览并订购服务。\n"
              "<b>{orders}</b> — 查看订单状态。\n"
              "<b>{contact}</b> — 联系我们的团队。\n\n"
              "👇 请在下方选择。",
    },
    "help_auto": {
        "km": "<b>{help}</b>\n\n<b>របៀបកុម្ម៉ង់៖</b>\n"
              "១. ចុច <b>{services}</b>\n២. ជ្រើសរើសសេវាកម្ម និងកញ្ចប់\n៣. ផ្ញើព័ត៌មានដែល bot សួរ\n"
              "៤. ពិនិត្យ រួចចុច 💳 បង់ប្រាក់\n៥. Scan QR ហើយបង់ប្រាក់ — bot នឹងបញ្ជាក់ដោយស្វ័យប្រវត្តិ\n"
              "៦. ក្រុមការងារចាប់ផ្តើមធ្វើ ហើយ bot នឹងជូនដំណឹងអ្នករហូតដល់រួចរាល់\n\n"
              "<b>ពាក្យបញ្ជា៖</b>\n/start — បើកម៉ឺនុយដើម\n/language — ប្តូរភាសា",
        "en": "<b>{help}</b>\n\n<b>How to order:</b>\n"
              "1. Tap <b>{services}</b>\n2. Choose a service and package\n3. Send the details the bot asks for\n"
              "4. Check, then tap 💳 Pay\n5. Scan the QR and pay — the bot confirms automatically\n"
              "6. Our team starts work, and the bot keeps you updated until it's done\n\n"
              "<b>Commands:</b>\n/start — open the main menu\n/language — change language",
        "zh": "<b>{help}</b>\n\n<b>如何下单：</b>\n"
              "1. 点击 <b>{services}</b>\n2. 选择服务和套餐\n3. 发送机器人要求的信息\n"
              "4. 确认后点击 💳 付款\n5. 扫描二维码付款 — 机器人会自动确认\n"
              "6. 团队开始处理，机器人会持续通知您直到完成\n\n"
              "<b>命令：</b>\n/start — 打开主菜单\n/language — 更改语言",
    },
    "help_manual": {
        "km": "<b>{help}</b>\n\n<b>របៀបកុម្ម៉ង់៖</b>\n"
              "១. ចុច <b>{services}</b>\n២. ជ្រើសរើសសេវាកម្ម និងកញ្ចប់\n៣. ផ្ញើព័ត៌មានដែល bot សួរ\n"
              "៤. ពិនិត្យ រួចចុច 💳 បង់ប្រាក់\n៥. Scan QR ក្នុង ABA Mobile បង់ប្រាក់ រួចផ្ញើរូបថតវិក្កយបត្រមក bot\n"
              "៦. ក្រុមការងារចាប់ផ្តើមធ្វើ ហើយ bot នឹងជូនដំណឹងអ្នករហូតដល់រួចរាល់\n\n"
              "<b>ពាក្យបញ្ជា៖</b>\n/start — បើកម៉ឺនុយដើម\n/language — ប្តូរភាសា",
        "en": "<b>{help}</b>\n\n<b>How to order:</b>\n"
              "1. Tap <b>{services}</b>\n2. Choose a service and package\n3. Send the details the bot asks for\n"
              "4. Check, then tap 💳 Pay\n5. Scan the QR in ABA Mobile, pay, then send the receipt screenshot to the bot\n"
              "6. Our team starts work, and the bot keeps you updated until it's done\n\n"
              "<b>Commands:</b>\n/start — open the main menu\n/language — change language",
        "zh": "<b>{help}</b>\n\n<b>如何下单：</b>\n"
              "1. 点击 <b>{services}</b>\n2. 选择服务和套餐\n3. 发送机器人要求的信息\n"
              "4. 确认后点击 💳 付款\n5. 在 ABA Mobile 扫码付款，然后把付款截图发给机器人\n"
              "6. 团队开始处理，机器人会持续通知您直到完成\n\n"
              "<b>命令：</b>\n/start — 打开主菜单\n/language — 更改语言",
    },
    "choose_service": {"km": "👇 សូមជ្រើសរើសសេវាកម្ម។", "en": "👇 Please choose a service.", "zh": "👇 请选择服务。"},
    "choose_package": {"km": "👇 សូមជ្រើសរើសកញ្ចប់។", "en": "👇 Please choose a package.", "zh": "👇 请选择套餐。"},
    "choose_from_menu": {"km": "👇 សូមជ្រើសរើសពីម៉ឺនុយ។", "en": "👇 Please choose from the menu.", "zh": "👇 请从菜单中选择。"},
    "no_contact": {"km": "📭 មិនទាន់មានព័ត៌មានទំនាក់ទំនង។", "en": "📭 No contact information yet.", "zh": "📭 暂无联系方式。"},
    "no_orders": {"km": "📭 អ្នកមិនទាន់មានការកុម្ម៉ង់នៅឡើយទេ។", "en": "📭 You have no orders yet.", "zh": "📭 您还没有订单。"},

    # ---------- ការកុម្ម៉ង់ ----------
    "lbl_order": {"km": "លេខកុម្ម៉ង់", "en": "Order No.", "zh": "订单号"},
    "confirm": {
        "km": "📋 <b>សូមពិនិត្យការកុម្ម៉ង់</b>\n\n{summary}\n\nត្រឹមត្រូវហើយឬនៅ? (ចង់កែ — ផ្ញើព័ត៌មានម្តងទៀត)",
        "en": "📋 <b>Please check your order</b>\n\n{summary}\n\nIs this correct? (To change it, just send the details again)",
        "zh": "📋 <b>请确认您的订单</b>\n\n{summary}\n\n信息正确吗？（如需修改，请重新发送信息）",
    },
    "package_gone": {"km": "⚠️ កញ្ចប់នេះលែងមានហើយ។", "en": "⚠️ This package is no longer available.", "zh": "⚠️ 该套餐已下架。"},
    "draft_expired": {"km": "⚠️ ការកុម្ម៉ង់នេះផុតកំណត់ហើយ។ សូមចាប់ផ្តើមម្តងទៀត។",
                      "en": "⚠️ This order has expired. Please start again.",
                      "zh": "⚠️ 此订单已过期，请重新开始。"},
    "order_created": {"km": "🧾 បានបង្កើតការកុម្ម៉ង់ <code>{oid}</code>។ កំពុងរៀបចំ QR…",
                      "en": "🧾 Order <code>{oid}</code> created. Preparing your QR…",
                      "zh": "🧾 订单 <code>{oid}</code> 已创建，正在生成二维码…"},
    "qr_failed": {"km": "⚠️ សូមអភ័យទោស មិនអាចបង្កើត QR បានទេ។ សូមព្យាយាមម្តងទៀត ឬទាក់ទងក្រុមការងារ។",
                  "en": "⚠️ Sorry, we couldn't create the QR. Please try again or contact our team.",
                  "zh": "⚠️ 抱歉，无法生成二维码。请重试或联系我们的团队。"},
    "pay_auto": {
        "km": "💳 <b>បង់ប្រាក់តាម ABA KHQR</b>\n\n{summary}\n\n⏰ QR មានសុពលភាព {minutes} នាទី\n"
              "📱 Scan QR ដោយកម្មវិធីធនាគារណាមួយ (ABA, ACLEDA, Wing…)\n"
              "   ឬចុចប៊ូតុង 📱 ខាងក្រោម\n🤖 bot នឹងបញ្ជាក់ការបង់ប្រាក់ដោយស្វ័យប្រវត្តិ។",
        "en": "💳 <b>Pay with ABA KHQR</b>\n\n{summary}\n\n⏰ This QR is valid for {minutes} minutes\n"
              "📱 Scan the QR with any banking app (ABA, ACLEDA, Wing…)\n"
              "   or tap the 📱 button below\n🤖 The bot will confirm your payment automatically.",
        "zh": "💳 <b>使用 ABA KHQR 付款</b>\n\n{summary}\n\n⏰ 二维码有效期 {minutes} 分钟\n"
              "📱 使用任意银行 App 扫码（ABA、ACLEDA、Wing…）\n"
              "   或点击下方 📱 按钮\n🤖 机器人会自动确认您的付款。",
    },
    "pay_manual": {
        "km": "💳 <b>បង់ប្រាក់តាម ABA KHQR</b>\n\n{summary}\n\n📱 Scan QR ក្នុង ABA Mobile ហើយបង់ <b>{amount}</b>\n"
              "✍️ សូមសរសេរលេខកុម្ម៉ង់ <code>{oid}</code> ក្នុង Remark\n"
              "📸 បន្ទាប់មក ផ្ញើរូបថតវិក្កយបត្រ (screenshot) មកទីនេះ។",
        "en": "💳 <b>Pay with ABA KHQR</b>\n\n{summary}\n\n📱 Scan the QR in ABA Mobile and pay <b>{amount}</b>\n"
              "✍️ Please write order number <code>{oid}</code> in the Remark\n"
              "📸 Then send the receipt screenshot here.",
        "zh": "💳 <b>使用 ABA KHQR 付款</b>\n\n{summary}\n\n📱 在 ABA Mobile 扫码并支付 <b>{amount}</b>\n"
              "✍️ 请在备注 (Remark) 中填写订单号 <code>{oid}</code>\n"
              "📸 然后把付款截图发送到这里。",
    },
    "not_paid_yet": {"km": "⏳ មិនទាន់ទទួលបានការបង់ប្រាក់ទេ។ សូមរង់ចាំបន្តិច។",
                     "en": "⏳ Payment not received yet. Please wait a moment.",
                     "zh": "⏳ 尚未收到付款，请稍候。"},
    "cancelled": {"km": "❌ បានបោះបង់ការកុម្ម៉ង់ <code>{oid}</code>។", "en": "❌ Order <code>{oid}</code> cancelled.",
                  "zh": "❌ 订单 <code>{oid}</code> 已取消。"},
    "cannot_cancel": {"km": "⚠️ ការកុម្ម៉ង់នេះមិនអាចបោះបង់បានទៀតទេ។", "en": "⚠️ This order can no longer be cancelled.",
                      "zh": "⚠️ 此订单已无法取消。"},
    "receipt_received": {"km": "📨 បានទទួលវិក្កយបត្រសម្រាប់ <code>{oid}</code>។\n🔍 ក្រុមការងារកំពុងពិនិត្យ ហើយនឹងបញ្ជាក់ឆាប់ៗនេះ។",
                         "en": "📨 Receipt received for <code>{oid}</code>.\n🔍 Our team is checking it and will confirm soon.",
                         "zh": "📨 已收到订单 <code>{oid}</code> 的付款截图。\n🔍 团队正在核对，稍后确认。"},
    "paid": {"km": "✅ <b>បានទទួលការបង់ប្រាក់ហើយ! អរគុណ។</b>\n\n{summary}\n\n🚀 ក្រុមការងារនឹងចាប់ផ្តើមដំណើរការឆាប់ៗនេះ។",
             "en": "✅ <b>Payment received! Thank you.</b>\n\n{summary}\n\n🚀 Our team will start working on it soon.",
             "zh": "✅ <b>已收到付款！谢谢。</b>\n\n{summary}\n\n🚀 团队将很快开始处理。"},
    "started": {"km": "🚀 ការកុម្ម៉ង់ <code>{oid}</code> កំពុងដំណើរការ។", "en": "🚀 Order <code>{oid}</code> is now in progress.",
                "zh": "🚀 订单 <code>{oid}</code> 正在处理中。"},
    "done": {"km": "✅ <b>ការកុម្ម៉ង់ <code>{oid}</code> រួចរាល់ហើយ!</b>\n\n🙏 អរគុណដែលបានប្រើប្រាស់សេវាកម្មរបស់យើង។",
             "en": "✅ <b>Order <code>{oid}</code> is complete!</b>\n\n🙏 Thank you for using our service.",
             "zh": "✅ <b>订单 <code>{oid}</code> 已完成！</b>\n\n🙏 感谢您使用我们的服务。"},
    "rejected": {"km": "🚫 ការបង់ប្រាក់សម្រាប់ <code>{oid}</code> មិនត្រឹមត្រូវ។\nសូមទាក់ទងក្រុមការងារ ប្រសិនបើអ្នកបានបង់ប្រាក់រួចហើយ។",
                 "en": "🚫 The payment for <code>{oid}</code> could not be verified.\nPlease contact our team if you have already paid.",
                 "zh": "🚫 订单 <code>{oid}</code> 的付款无法核实。\n如果您已付款，请联系我们的团队。"},
    "qr_expired": {"km": "⌛ QR សម្រាប់ការកុម្ម៉ង់ <code>{oid}</code> បានផុតកំណត់។\nសូមកុម្ម៉ង់ម្តងទៀត ប្រសិនបើអ្នកនៅតែចង់បាន។",
                   "en": "⌛ The QR for order <code>{oid}</code> has expired.\nPlease order again if you still want it.",
                   "zh": "⌛ 订单 <code>{oid}</code> 的二维码已过期。\n如仍需要，请重新下单。"},
    "staff_message": {"km": "💬 <b>សារពីក្រុមការងារ</b> (<code>{oid}</code>)\n\n{text}",
                      "en": "💬 <b>Message from our team</b> (<code>{oid}</code>)\n\n{text}",
                      "zh": "💬 <b>来自团队的消息</b>（<code>{oid}</code>）\n\n{text}"},

    # ---------- ស្ថានភាព ----------
    "status_pending": {"km": "⏳ រង់ចាំការបង់ប្រាក់", "en": "⏳ Awaiting payment", "zh": "⏳ 等待付款"},
    "status_review": {"km": "🔍 កំពុងពិនិត្យការបង់ប្រាក់", "en": "🔍 Checking payment", "zh": "🔍 正在核对付款"},
    "status_paid": {"km": "💰 បានបង់ប្រាក់ — រង់ចាំដំណើរការ", "en": "💰 Paid — waiting to start", "zh": "💰 已付款 — 等待处理"},
    "status_working": {"km": "🚀 កំពុងដំណើរការ", "en": "🚀 In progress", "zh": "🚀 处理中"},
    "status_done": {"km": "✅ រួចរាល់", "en": "✅ Completed", "zh": "✅ 已完成"},
    "status_cancelled": {"km": "❌ បានបោះបង់", "en": "❌ Cancelled", "zh": "❌ 已取消"},
    "status_expired": {"km": "⌛ QR ផុតកំណត់", "en": "⌛ QR expired", "zh": "⌛ 二维码已过期"},
    "status_rejected": {"km": "🚫 ការបង់ប្រាក់មិនត្រឹមត្រូវ", "en": "🚫 Payment not verified", "zh": "🚫 付款未通过核实"},

    # ---------- ទំព័របើក ABA Mobile ----------
    "page_opening_title": {"km": "📱 កំពុងបើក ABA Mobile…", "en": "📱 Opening ABA Mobile…", "zh": "📱 正在打开 ABA Mobile…"},
    "page_opening_text": {"km": "បង់ប្រាក់ <b>{amount}</b> សម្រាប់ការកុម្ម៉ង់ {oid}<br>ប្រសិនបើ ABA Mobile មិនបើកដោយស្វ័យប្រវត្តិ សូមចុចប៊ូតុងខាងក្រោម។",
                          "en": "Pay <b>{amount}</b> for order {oid}<br>If ABA Mobile doesn't open automatically, tap the button below.",
                          "zh": "为订单 {oid} 支付 <b>{amount}</b><br>如果 ABA Mobile 没有自动打开，请点击下方按钮。"},
    "page_button": {"km": "បើក ABA Mobile", "en": "Open ABA Mobile", "zh": "打开 ABA Mobile"},
    "page_expired_title": {"km": "⌛ តំណនេះលែងប្រើបានហើយ", "en": "⌛ This link is no longer valid", "zh": "⌛ 此链接已失效"},
    "page_expired_text": {"km": "ការកុម្ម៉ង់នេះបានបង់ ឬផុតកំណត់ហើយ។ សូមត្រឡប់ទៅ bot វិញ។",
                          "en": "This order has been paid or has expired. Please go back to the bot.",
                          "zh": "此订单已付款或已过期，请返回机器人。"},

    # ---------- ពាក្យបញ្ជា (ម៉ឺនុយ /) ----------
    "cmd_start": {"km": "បើកម៉ឺនុយដើម", "en": "Open the main menu", "zh": "打开主菜单"},
    "cmd_language": {"km": "ប្តូរភាសា", "en": "Change language", "zh": "更改语言"},
}


def t(key: str, lang: str, **kwargs) -> str:
    entry = TEXTS[key]
    text = entry.get(lang) or entry[DEFAULT_LANG]
    return text.format(**kwargs) if kwargs else text


def tr(value, lang: str) -> str:
    """តម្លៃពី services.json: អាចជាអក្សរធម្មតា ឬ {"km": …, "en": …, "zh": …}"""
    if isinstance(value, dict):
        return value.get(lang) or value.get(DEFAULT_LANG) or next(iter(value.values()), "")
    return value or ""
