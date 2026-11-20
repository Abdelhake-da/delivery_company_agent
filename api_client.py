import os
from dataclasses import dataclass
from typing import Any

import httpx

class ShippingAPIError(Exception):
    """Raised when the shipping api request failes."""

@dataclass
class ShippingAPIClient:
    base_url: str
    api_key: str
    timeout: float = 10.0
  
    @classmethod
    def from_env(cls) -> "ShippingAPIClient":
        return cls(
            base_url=os.getenv("SHIPPING_API_URL", "http://127.0.0.1:8000"),
            api_key=os.getenv("SHIPPING_API_KEY", "demo-shipping-key"),
            timeout=float(os.getenv("SHIPPING_API_TIMEOUT", "10.0")),
        )

    def _headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}
    
    def _request(self, method: str, path: str, params: dict[str, Any] | None = None , json_data: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        try: 
            response = httpx.request(
                method = method,
                url = url,
                headers= self._headers(),
                params = params,
                json = json_data,
                timeout = self.timeout
            )

            response.raise_for_status()

            return response.json()

        except httpx.TimeoutException as e:
            raise ShippingAPIError(f"Request timeout: {e}")
        except httpx.HTTPStatusError as e:
            raise ShippingAPIError(f"API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise ShippingAPIError(f"Unexpected error: {e}")

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("GET", path, params=params)
    
    def _post(self, path: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("POST", path, json_data=json_data)
    
    def _patch(self, path: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("PATCH", path, json_data=json_data)

    # --------------------------------------------------
    # system
    # --------------------------------------------------

    def health_check(self) -> dict[str, Any]:
        return self._get("/health")

    # ---------------------------------------------------
    # Shipments - Read
    # ---------------------------------------------------
    def get_shipments(self , status:str | None = None, branch_name:str | None = None) -> dict:
        params = {}
        if status:
            params["status"] = status
        if branch_name :
            params["branch_name"] = branch_name
        
        return self._get("/shipments", params=params)
        
    def get_delayed_shipments(self) -> dict:
        return self._get("/shipments/delayed")
    
    def get_returned_shipments(self) -> dict:
        return self._get("/shipments/returned")
    
    def get_shipment_by_id(self, shipment_id: str) -> dict:
        return self._get(f"/shipments/{shipment_id}")


    # ---------------------------------------------------
    # Shipments - Write
    # ---------------------------------------------------
    
    def create_shipment(self, shipment_data: dict[str, Any]) -> dict[str, Any]:
        return self._post("/shipments", json_data=shipment_data)

    def update_shipment(self, shipment_id: str, shipment_data: dict[str, Any]) -> dict[str, Any]:
        return self._patch(f"/shipments/{shipment_id}", json_data=shipment_data)
    
    def change_shipment_status(self, shipment_id: str, status: str) -> dict[str, Any]:
        return self._patch(f"/shipments/{shipment_id}/status", {"status": status})
    
    def reschedule_shipment(self, shipment_id: str, expected_delivery: str) -> dict[str, Any]:
        return self._patch(f"/shipments/{shipment_id}/schedule", {"expected_delivery": expected_delivery})
    
    def cancel_shipment(self, shipment_id: str , reason: str | None = None) -> dict[str, Any]:
        return self._patch(f"/shipments/{shipment_id}/cancel", {"reason": reason})

    # ---------------------------------------------------
    # Returns
    # ---------------------------------------------------

    def get_returns(self) -> dict:
        return self._get("/returns")

    # ---------------------------------------------------
    # Payments
    # ---------------------------------------------------

    def get_payments_summary(self) -> dict:
        return self._get("/payments/summary")

    # ---------------------------------------------------
    # Branches
    # ---------------------------------------------------

    def get_branches_performance(self) -> dict:
        return self._get("/branches/performance")
    
    # ---------------------------------------------------
    # Management
    # ---------------------------------------------------

    def get_management_overview(self) -> dict:
        return self._get("/management/overview")
    