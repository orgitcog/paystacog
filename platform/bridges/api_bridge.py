#!/usr/bin/env python3
"""
API Bridge - Unified Interface for Paystack API

This bridge provides:
- Unified API client
- Request/response handling
- Rate limiting
- Error handling
- Webhook management
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import hashlib
import hmac
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)


class APIEndpoint(Enum):
    """Paystack API endpoints."""
    # Transactions
    TRANSACTION_INITIALIZE = "/transaction/initialize"
    TRANSACTION_VERIFY = "/transaction/verify/{reference}"
    TRANSACTION_LIST = "/transaction"
    TRANSACTION_FETCH = "/transaction/{id}"
    TRANSACTION_CHARGE_AUTHORIZATION = "/transaction/charge_authorization"
    TRANSACTION_TIMELINE = "/transaction/timeline/{id_or_reference}"
    TRANSACTION_TOTALS = "/transaction/totals"
    TRANSACTION_EXPORT = "/transaction/export"
    
    # Customers
    CUSTOMER_CREATE = "/customer"
    CUSTOMER_LIST = "/customer"
    CUSTOMER_FETCH = "/customer/{email_or_code}"
    CUSTOMER_UPDATE = "/customer/{code}"
    CUSTOMER_VALIDATE = "/customer/{code}/identification"
    
    # Plans
    PLAN_CREATE = "/plan"
    PLAN_LIST = "/plan"
    PLAN_FETCH = "/plan/{id_or_code}"
    PLAN_UPDATE = "/plan/{id_or_code}"
    
    # Subscriptions
    SUBSCRIPTION_CREATE = "/subscription"
    SUBSCRIPTION_LIST = "/subscription"
    SUBSCRIPTION_FETCH = "/subscription/{id_or_code}"
    SUBSCRIPTION_ENABLE = "/subscription/enable"
    SUBSCRIPTION_DISABLE = "/subscription/disable"
    
    # Transfers
    TRANSFER_INITIATE = "/transfer"
    TRANSFER_LIST = "/transfer"
    TRANSFER_FETCH = "/transfer/{id_or_code}"
    TRANSFER_VERIFY = "/transfer/verify/{reference}"
    
    # Refunds
    REFUND_CREATE = "/refund"
    REFUND_LIST = "/refund"
    REFUND_FETCH = "/refund/{reference}"
    
    # Verification
    RESOLVE_ACCOUNT = "/bank/resolve"
    RESOLVE_BVN = "/bank/resolve_bvn/{bvn}"
    RESOLVE_CARD_BIN = "/decision/bin/{bin}"


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class APIRequest:
    """Represents an API request."""
    endpoint: APIEndpoint
    method: HTTPMethod
    params: Dict[str, Any] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    
    def get_url(self, base_url: str) -> str:
        """Get the full URL for this request."""
        path = self.endpoint.value
        for key, value in self.path_params.items():
            path = path.replace(f"{{{key}}}", str(value))
        return f"{base_url}{path}"


@dataclass
class APIResponse:
    """Represents an API response."""
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str] = field(default_factory=dict)
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success(self) -> bool:
        return 200 <= self.status_code < 300 and self.data.get("status", False)
    
    @property
    def message(self) -> str:
        return self.data.get("message", "")


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_second: int = 10
    requests_per_minute: int = 100
    burst_limit: int = 20


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.burst_limit
        self.last_update = datetime.utcnow()
        self.request_counts: Dict[str, int] = defaultdict(int)
    
    async def acquire(self) -> bool:
        """Acquire a token for making a request."""
        now = datetime.utcnow()
        elapsed = (now - self.last_update).total_seconds()
        
        # Refill tokens
        self.tokens = min(
            self.config.burst_limit,
            self.tokens + elapsed * self.config.requests_per_second
        )
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        
        # Wait for token
        wait_time = (1 - self.tokens) / self.config.requests_per_second
        await asyncio.sleep(wait_time)
        self.tokens = 0
        return True
    
    def get_remaining(self) -> int:
        """Get remaining tokens."""
        return int(self.tokens)


class WebhookHandler:
    """Handles Paystack webhooks."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.handlers: Dict[str, List[Callable]] = defaultdict(list)
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        expected = hmac.new(
            self.secret_key.encode(),
            payload,
            hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for an event type."""
        self.handlers[event_type].append(handler)
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process a webhook payload."""
        event_type = payload.get("event")
        data = payload.get("data", {})
        
        results = []
        for handler in self.handlers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(data)
                else:
                    result = handler(data)
                results.append({"handler": handler.__name__, "success": True, "result": result})
            except Exception as e:
                results.append({"handler": handler.__name__, "success": False, "error": str(e)})
        
        return {
            "event": event_type,
            "processed": len(results),
            "results": results
        }


class APIBridge:
    """
    Bridge for unified Paystack API access.
    
    Provides:
    - Unified API client
    - Rate limiting
    - Error handling
    - Webhook management
    - Request/response logging
    """
    
    def __init__(self, secret_key: str = "", public_key: str = "",
                 base_url: str = "https://api.paystack.co"):
        self.secret_key = secret_key
        self.public_key = public_key
        self.base_url = base_url
        self.rate_limiter = RateLimiter(RateLimitConfig())
        self.webhook_handler = WebhookHandler(secret_key)
        self.request_log: List[Dict] = []
        self.error_log: List[Dict] = []
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def request(self, api_request: APIRequest) -> APIResponse:
        """Make an API request."""
        # Rate limiting
        await self.rate_limiter.acquire()
        
        # Build request
        url = api_request.get_url(self.base_url)
        headers = {**self._get_headers(), **api_request.headers}
        
        # Log request
        request_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": api_request.endpoint.value,
            "method": api_request.method.value,
            "url": url
        }
        
        # Simulate API call (in production, use aiohttp or httpx)
        try:
            # Simulated response
            response = APIResponse(
                status_code=200,
                data={
                    "status": True,
                    "message": "Request successful",
                    "data": {}
                },
                request_id=hashlib.md5(url.encode()).hexdigest()[:16]
            )
            
            request_log["status_code"] = response.status_code
            request_log["success"] = response.success
            self.request_log.append(request_log)
            
            return response
            
        except Exception as e:
            error_log = {
                **request_log,
                "error": str(e)
            }
            self.error_log.append(error_log)
            
            return APIResponse(
                status_code=500,
                data={"status": False, "message": str(e)}
            )
    
    # Transaction methods
    async def initialize_transaction(self, email: str, amount: int,
                                    **kwargs) -> APIResponse:
        """Initialize a transaction."""
        request = APIRequest(
            endpoint=APIEndpoint.TRANSACTION_INITIALIZE,
            method=HTTPMethod.POST,
            body={"email": email, "amount": amount, **kwargs}
        )
        return await self.request(request)
    
    async def verify_transaction(self, reference: str) -> APIResponse:
        """Verify a transaction."""
        request = APIRequest(
            endpoint=APIEndpoint.TRANSACTION_VERIFY,
            method=HTTPMethod.GET,
            path_params={"reference": reference}
        )
        return await self.request(request)
    
    async def list_transactions(self, **kwargs) -> APIResponse:
        """List transactions."""
        request = APIRequest(
            endpoint=APIEndpoint.TRANSACTION_LIST,
            method=HTTPMethod.GET,
            params=kwargs
        )
        return await self.request(request)
    
    async def charge_authorization(self, email: str, amount: int,
                                  authorization_code: str, **kwargs) -> APIResponse:
        """Charge an authorization."""
        request = APIRequest(
            endpoint=APIEndpoint.TRANSACTION_CHARGE_AUTHORIZATION,
            method=HTTPMethod.POST,
            body={
                "email": email,
                "amount": amount,
                "authorization_code": authorization_code,
                **kwargs
            }
        )
        return await self.request(request)
    
    # Customer methods
    async def create_customer(self, email: str, **kwargs) -> APIResponse:
        """Create a customer."""
        request = APIRequest(
            endpoint=APIEndpoint.CUSTOMER_CREATE,
            method=HTTPMethod.POST,
            body={"email": email, **kwargs}
        )
        return await self.request(request)
    
    async def list_customers(self, **kwargs) -> APIResponse:
        """List customers."""
        request = APIRequest(
            endpoint=APIEndpoint.CUSTOMER_LIST,
            method=HTTPMethod.GET,
            params=kwargs
        )
        return await self.request(request)
    
    async def fetch_customer(self, email_or_code: str) -> APIResponse:
        """Fetch a customer."""
        request = APIRequest(
            endpoint=APIEndpoint.CUSTOMER_FETCH,
            method=HTTPMethod.GET,
            path_params={"email_or_code": email_or_code}
        )
        return await self.request(request)
    
    # Plan methods
    async def create_plan(self, name: str, amount: int, interval: str,
                         **kwargs) -> APIResponse:
        """Create a plan."""
        request = APIRequest(
            endpoint=APIEndpoint.PLAN_CREATE,
            method=HTTPMethod.POST,
            body={"name": name, "amount": amount, "interval": interval, **kwargs}
        )
        return await self.request(request)
    
    async def list_plans(self, **kwargs) -> APIResponse:
        """List plans."""
        request = APIRequest(
            endpoint=APIEndpoint.PLAN_LIST,
            method=HTTPMethod.GET,
            params=kwargs
        )
        return await self.request(request)
    
    # Subscription methods
    async def create_subscription(self, customer: str, plan: str,
                                 **kwargs) -> APIResponse:
        """Create a subscription."""
        request = APIRequest(
            endpoint=APIEndpoint.SUBSCRIPTION_CREATE,
            method=HTTPMethod.POST,
            body={"customer": customer, "plan": plan, **kwargs}
        )
        return await self.request(request)
    
    async def list_subscriptions(self, **kwargs) -> APIResponse:
        """List subscriptions."""
        request = APIRequest(
            endpoint=APIEndpoint.SUBSCRIPTION_LIST,
            method=HTTPMethod.GET,
            params=kwargs
        )
        return await self.request(request)
    
    # Transfer methods
    async def initiate_transfer(self, amount: int, recipient: str,
                               **kwargs) -> APIResponse:
        """Initiate a transfer."""
        request = APIRequest(
            endpoint=APIEndpoint.TRANSFER_INITIATE,
            method=HTTPMethod.POST,
            body={"amount": amount, "recipient": recipient, **kwargs}
        )
        return await self.request(request)
    
    async def verify_transfer(self, reference: str) -> APIResponse:
        """Verify a transfer."""
        request = APIRequest(
            endpoint=APIEndpoint.TRANSFER_VERIFY,
            method=HTTPMethod.GET,
            path_params={"reference": reference}
        )
        return await self.request(request)
    
    # Refund methods
    async def create_refund(self, transaction: str, **kwargs) -> APIResponse:
        """Create a refund."""
        request = APIRequest(
            endpoint=APIEndpoint.REFUND_CREATE,
            method=HTTPMethod.POST,
            body={"transaction": transaction, **kwargs}
        )
        return await self.request(request)
    
    # Verification methods
    async def resolve_account(self, account_number: str,
                             bank_code: str) -> APIResponse:
        """Resolve a bank account."""
        request = APIRequest(
            endpoint=APIEndpoint.RESOLVE_ACCOUNT,
            method=HTTPMethod.GET,
            params={"account_number": account_number, "bank_code": bank_code}
        )
        return await self.request(request)
    
    # Webhook methods
    def register_webhook_handler(self, event_type: str, handler: Callable):
        """Register a webhook handler."""
        self.webhook_handler.register_handler(event_type, handler)
    
    async def process_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Process an incoming webhook."""
        if not self.webhook_handler.verify_signature(payload, signature):
            return {"error": "Invalid signature"}
        
        data = json.loads(payload)
        return await self.webhook_handler.process_webhook(data)
    
    # Utility methods
    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return {
            "total_requests": len(self.request_log),
            "total_errors": len(self.error_log),
            "success_rate": (len(self.request_log) - len(self.error_log)) / max(1, len(self.request_log)),
            "rate_limit_remaining": self.rate_limiter.get_remaining(),
            "recent_requests": self.request_log[-10:],
            "recent_errors": self.error_log[-5:]
        }
    
    def get_available_endpoints(self) -> List[Dict[str, str]]:
        """Get list of available API endpoints."""
        return [
            {"endpoint": e.value, "name": e.name}
            for e in APIEndpoint
        ]


if __name__ == "__main__":
    # Test the API bridge
    async def test():
        bridge = APIBridge(secret_key="sk_test_xxx", public_key="pk_test_xxx")
        
        # Test transaction initialization
        response = await bridge.initialize_transaction(
            email="test@example.com",
            amount=10000
        )
        print("Initialize Transaction Response:")
        print(json.dumps(response.data, indent=2))
        
        # Test customer creation
        response = await bridge.create_customer(
            email="customer@example.com",
            first_name="John",
            last_name="Doe"
        )
        print("\nCreate Customer Response:")
        print(json.dumps(response.data, indent=2))
        
        # Get statistics
        print("\nAPI Statistics:")
        print(json.dumps(bridge.get_statistics(), indent=2))
        
        # List endpoints
        print("\nAvailable Endpoints:")
        for ep in bridge.get_available_endpoints()[:5]:
            print(f"  {ep['name']}: {ep['endpoint']}")
    
    asyncio.run(test())
