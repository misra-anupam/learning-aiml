"""
Adapter so the Orders LangGraph nodes can keep calling
    await self.mcp.call("/track", {"order": order_key})
without rewriting them, while the actual transport is a FastMCP tool call.

Transport: stdio — the client spawns orders_mcp_server.py as a subprocess
and talks to it over stdin/stdout. No network/port setup needed locally.

Usage in Orders.__init__:
    self.mcp = OrdersMCPClient(server_script="orders_mcp_server.py")
    await self.mcp.connect()   # or manage as an async context manager:
    # async with OrdersMCPClient("orders_mcp_server.py") as mcp: ...
"""

from __future__ import annotations

from fastmcp import Client

# endpoint string (as used in agent.py docstrings/calls) -> FastMCP tool name
_ENDPOINT_TO_TOOL = {
    "/list": "list_orders",
    "/track": "track_order",
    "/cancellation_eligibility": "check_cancellation_eligibility",
    "/cancel": "cancel_order",
    "/date_change_eligibility": "check_date_change_eligibility",
    "/change_delivery_date": "change_delivery_date",
    "/order_status": "get_order_status",
    "/address_change_eligibility": "check_address_change_eligibility",
    "/change_delivery_address": "change_delivery_address",
    "/view_order": "view_order",
    "/return_options": "get_return_options",
    "/process_return": "process_return",
}

# payload key(s) each endpoint expects -> tool's actual argument name(s).
# Only needed where names differ from the payload key used in agent.py.
_PAYLOAD_KEY_MAP = {
    "/track": {"order": "order_key"},
    "/cancellation_eligibility": {"order": "order_key"},
    "/cancel": {"order": "order_key"},
    "/date_change_eligibility": {"order": "order_key"},
    "/change_delivery_date": {"order": "order_key", "date": "new_date"},
    "/order_status": {"order": "order_key"},
    "/address_change_eligibility": {"order": "order_key"},
    "/change_delivery_address": {"order": "order_key", "address": "new_address"},
    "/view_order": {"order": "order_key"},
    "/return_options": {"item": "item_key"},
    "/process_return": {"item": "item_key", "mode": "mode"},
}


class OrdersMCPClient:
    def __init__(self, server_script: str = "orders_mcp_server.py"):
        # Passing a .py path (rather than a URL) tells fastmcp's Client
        # to use stdio transport: it spawns `python orders_mcp_server.py`
        # as a subprocess and speaks MCP over its stdin/stdout.
        self._server_script = server_script
        self._client: Client | None = None

    async def connect(self):
        self._client = Client(self._server_script)
        await self._client.__aenter__()

    async def close(self):
        if self._client:
            await self._client.__aexit__(None, None, None)

    async def call(self, endpoint: str, payload: dict) -> dict:
        if endpoint not in _ENDPOINT_TO_TOOL:
            raise ValueError(f"Unknown MCP endpoint: {endpoint}")

        tool_name = _ENDPOINT_TO_TOOL[endpoint]
        key_map = _PAYLOAD_KEY_MAP.get(endpoint, {})
        args = {key_map.get(k, k): v for k, v in payload.items()}

        result = await self._client.call_tool(tool_name, args)
        return result.data if hasattr(result, "data") else result

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *exc):
        await self.close()