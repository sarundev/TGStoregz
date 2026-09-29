"""RielPay (KHQR តាម ABA PayWay): បង្កើតការបង់ប្រាក់ និងពិនិត្យស្ថានភាព

ឯកសារ API: https://rielpays.com/docs
"""

import httpx

BASE_URL = "https://rielpays.com/v1"


class RielPayError(Exception):
    pass


class RielPay:
    def __init__(self, api_key: str):
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.request(method, BASE_URL + path, headers=self.headers, **kwargs)
        try:
            data = r.json()
        except ValueError:
            raise RielPayError(f"HTTP {r.status_code}: {r.text[:200]}")
        if r.status_code >= 400:
            err = data.get("error", {})
            raise RielPayError(f"HTTP {r.status_code} {err.get('code')}: {err.get('message')}")
        return data

    async def create_payment(self, order_id: str, amount: float, currency: str = "USD",
                             expires_min: int = 15, description: str = "") -> dict:
        """ត្រឡប់ payment object: id, status, qr_string, checkout_url, deeplink, expires_at …"""
        body = {
            "amount": round(amount, 2) if currency.upper() == "USD" else int(amount),
            "currency": currency.upper(),
            "description": description or f"Order {order_id}",
            "metadata": {"order_id": order_id},
            "expires_in_minutes": min(1440, max(3, int(expires_min))),
            "idempotency_key": order_id,  # ព្យាយាមម្តងទៀតក៏មិនបង្កើតការបង់ប្រាក់ស្ទួន
        }
        return await self._request("POST", "/payments", json=body)

    async def get_payment(self, payment_id: str) -> dict:
        """status: pending | paid | expired | failed"""
        return await self._request("GET", f"/payments/{payment_id}")
