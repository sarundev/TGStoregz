"""ABA PayWay: បង្កើត KHQR និងពិនិត្យការបង់ប្រាក់

ឯកសារ API:
  QR API            https://developer.payway.com.kh/qr-api-14530840e0
  Check transaction https://developer.payway.com.kh/check-transaction-14530826e0
"""

import base64
import hashlib
import hmac
from datetime import datetime, timezone

import httpx

SANDBOX_URL = "https://checkout-sandbox.payway.com.kh"
PRODUCTION_URL = "https://checkout.payway.com.kh"

# លំដាប់ field សម្រាប់ hash របស់ generate-qr (តាមឯកសារ ABA)
QR_HASH_FIELDS = [
    "req_time", "merchant_id", "tran_id", "amount", "items", "first_name", "last_name",
    "email", "phone", "purchase_type", "payment_option", "callback_url", "return_deeplink",
    "currency", "custom_fields", "return_params", "payout", "lifetime", "qr_image_template",
]


class PayWayError(Exception):
    pass


class PayWay:
    def __init__(self, merchant_id: str, api_key: str, sandbox: bool = True,
                 qr_template: str = "template3_color"):
        self.merchant_id = merchant_id
        self.api_key = api_key.encode()
        self.base_url = SANDBOX_URL if sandbox else PRODUCTION_URL
        self.qr_template = qr_template

    def _hash(self, text: str) -> str:
        return base64.b64encode(hmac.new(self.api_key, text.encode(), hashlib.sha512).digest()).decode()

    @staticmethod
    def _req_time() -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    async def _post(self, path: str, body: dict) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(self.base_url + path, json=body)
        try:
            return r.json()
        except ValueError:
            raise PayWayError(f"HTTP {r.status_code}: {r.text[:200]}")

    async def generate_qr(self, tran_id: str, amount: float, currency: str = "USD",
                          lifetime_min: int = 10) -> dict:
        """ត្រឡប់ {'qr_string', 'qr_image' (bytes), 'deeplink'}"""
        body = {
            "req_time": self._req_time(),
            "merchant_id": self.merchant_id,
            "tran_id": tran_id,
            "amount": f"{amount:.2f}" if currency.upper() == "USD" else str(int(amount)),
            "purchase_type": "purchase",
            "payment_option": "abapay_khqr",
            "currency": currency.upper(),
            "lifetime": max(3, int(lifetime_min)),
            "qr_image_template": self.qr_template,
        }
        body["hash"] = self._hash("".join(str(body.get(f, "")) for f in QR_HASH_FIELDS))

        data = await self._post("/api/payment-gateway/v1/payments/generate-qr", body)
        status = data.get("status", {})
        if str(status.get("code")) != "0":
            raise PayWayError(f"generate-qr failed: code={status.get('code')} {status.get('message')}")

        image = data.get("qrImage", "")
        image_bytes = base64.b64decode(image.split(",", 1)[1]) if "," in image else None
        return {"qr_string": data.get("qrString"), "qr_image": image_bytes,
                "deeplink": data.get("abapay_deeplink")}

    async def check_transaction(self, tran_id: str) -> dict:
        """ត្រឡប់ {'paid': bool, 'status': str, 'amount': float|None, 'currency': str|None}"""
        req_time = self._req_time()
        body = {"req_time": req_time, "merchant_id": self.merchant_id, "tran_id": tran_id,
                "hash": self._hash(req_time + self.merchant_id + tran_id)}
        data = await self._post("/api/payment-gateway/v1/payments/check-transaction-2", body)

        info = data.get("data") or {}
        status = data.get("status") or info.get("status") or {}
        code = str(status.get("code", ""))
        if code == "6":  # រកមិនឃើញ — អតិថិជនមិនទាន់ scan
            return {"paid": False, "status": "NOT_FOUND", "amount": None, "currency": None}
        if code not in ("0", "00"):
            raise PayWayError(f"check-transaction failed: code={code} {status.get('message')}")

        return {
            "paid": info.get("payment_status_code") == 0 or info.get("payment_status") == "APPROVED",
            "status": info.get("payment_status", ""),
            "amount": info.get("payment_amount", info.get("total_amount")),
            "currency": info.get("payment_currency"),
        }
