"""
Orders MCP server — exposes order-management tools over FastMCP.

Backs every MCP call referenced in the Orders LangGraph subgraph:
    /list : List orders for a user(already authenticated and filtered)
    /track : Track a given order
    /cancellation_eligibility : Check if the given order is cancellable 
    /cancel : Cancel eligible order
    /date_change_eligibility : Check if the given order's deliver date can be changed
    /change_delivery_date : Change eligible order's delivery date
    /order_status : Check order status
    /address_change_eligibility : Check if the given order's deliver address can be changed
    /change_delivery_address : Change eligible order's delivery address
    /view_order : Fetch items in order 
    /return_options : Check eligible return options for an item
    /process_return : Process eligible return method for order

Data layer is an in-memory mock store — swap `OrdersDB` for a real
repository (Postgres, order-management API client, etc.) when ready.
Run standalone with:  python orders_mcp_server.py
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Literal
import random
from fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("orders-server")


# --------------------------------------------------------------------------
# Domain models
# --------------------------------------------------------------------------

class OrderStatus(str, Enum):
    PLACED = "placed"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    key: str
    name: str
    price: float
    quantity: int = 1


class Order(BaseModel):
    key: str
    customer_id: str
    status: OrderStatus
    placed_at: datetime
    delivery_date: date
    delivery_address: str
    items: list[OrderItem]


ReturnMode = Literal["order-return-refund", "order-return-return", "order-return-reorder"]

# --------------------------------------------------------------------------
# Mock data store — replace with real persistence/order-system client
# --------------------------------------------------------------------------

class OrdersDB:
    def __init__(self):
        self._orders: dict[str, Order] = {}
        self._seed()

    def _random_items(self, n: int) -> list[OrderItem]:
        templates = [("Wireless Mouse", 799.0), ("Monitor", 17999.0), ("Chair", 6999.0), ("USB-C Cable", 299.0)]
        chosen = random.sample(templates, min(n, len(templates)))
        return [OrderItem(key=str(uuid.uuid4()), name=name, price=price) for name, price in chosen]

    def _seed(self):
        customer_id = "customer-001"
        seed = [
            (OrderStatus.PLACED, 5, 1),
            (OrderStatus.SHIPPED, 2, 2),
            (OrderStatus.PLACED, 3, 2),
            (OrderStatus.SHIPPED, 2, 2),
            (OrderStatus.OUT_FOR_DELIVERY, 1, 3),
            (OrderStatus.OUT_FOR_DELIVERY, 2, 1),
            (OrderStatus.DELIVERED, -3, 1),
            (OrderStatus.CANCELLED, -10, 2),
        ]


        for status, days_offset, num_items in seed:
            key = str(uuid.uuid4())
            self._orders[key] = Order(
                key=key,
                customer_id=customer_id,
                status=status,
                placed_at=datetime.utcnow() - timedelta(days=abs(days_offset) + 1),
                delivery_date=date.today() + timedelta(days=days_offset if days_offset > 0 else 0),
                delivery_address="Embassy Tech Village, Bengaluru, KA 560100",
                items=self._random_items(num_items)
            )

    def recent_for_customer(self, customer_id: str = "customer-001", limit: int = 5) -> list[Order]:
        orders = [o for o in self._orders.values() if o.customer_id == customer_id]
        orders.sort(key=lambda o: o.placed_at, reverse=True)
        return orders[:limit]

    def get(self, order_key: str) -> Order | None:
        return self._orders.get(order_key)

    def get_item(self, order_key: str, item_key: str) -> OrderItem | None:
        order = self.get(order_key)
        if not order:
            return None
        return next((i for i in order.items if i.key == item_key), None)

    def find_order_for_item(self, item_key: str) -> Order | None:
        for order in self._orders.values():
            if any(i.key == item_key for i in order.items):
                return order
        return None


db = OrdersDB()


# --------------------------------------------------------------------------
# Tools — one per endpoint referenced in the Orders subgraph
# --------------------------------------------------------------------------

@mcp.tool()
def list_orders(customer_id: str = "customer-001") -> list[dict]:
    """Return the customer's 5 most recent orders. Backs `/list`."""
    return [o.model_dump(mode="json") for o in db.recent_for_customer(customer_id)]


@mcp.tool()
def track_order(order_key: str) -> dict:
    """Return current status and delivery ETA for an order. Backs `/track`."""
    order = db.get(order_key)
    if not order:
        return {"error": "order_not_found"}
    return {
        "status": order.status.value,
        "delivery_date": order.delivery_date.isoformat(),
        "delivery_address": order.delivery_address,
    }


@mcp.tool()
def check_cancellation_eligibility(order_key: str) -> dict:
    """Whether an order can still be cancelled. Backs `/cancellation_eligibility`."""
    order = db.get(order_key)
    if not order:
        return {"eligible": False, "reason": "order_not_found"}
    eligible = order.status in (OrderStatus.PLACED,)
    reason = None if eligible else f"order already {order.status.value}"
    return {"eligible": eligible, "reason": reason}


@mcp.tool()
def cancel_order(order_key: str) -> dict:
    """Cancel an order. Backs `/cancel`."""
    order = db.get(order_key)
    if not order:
        return {"success": False, "reason": "order_not_found"}
    if order.status != OrderStatus.PLACED:
        return {"success": False, "reason": f"order already {order.status.value}"}
    order.status = OrderStatus.CANCELLED
    return {"success": True}


@mcp.tool()
def check_date_change_eligibility(order_key: str) -> dict:
    """Whether the delivery date can still be changed. Backs `/date_change_eligibility`."""
    order = db.get(order_key)
    if not order:
        return {"eligible": False, "reason": "order_not_found"}
    eligible = order.status in (OrderStatus.PLACED, OrderStatus.SHIPPED)
    reason = None if eligible else f"order already {order.status.value}"
    return {"eligible": eligible, "reason": reason}


@mcp.tool()
def change_delivery_date(order_key: str, new_date: str) -> dict:
    """Update an order's delivery date (ISO format YYYY-MM-DD). Backs `/change_delivery_date`."""
    order = db.get(order_key)
    if not order:
        return {"success": False, "reason": "order_not_found"}
    try:
        parsed = date.fromisoformat(new_date)
    except ValueError:
        return {"success": False, "reason": "invalid_date_format"}
    order.delivery_date = parsed
    return {"success": True, "delivery_date": parsed.isoformat()}


@mcp.tool()
def get_order_status(order_key: str) -> dict:
    """Return delivery status, including whether the order has been delivered. Backs `/order_status`."""
    order = db.get(order_key)
    if not order:
        return {"error": "order_not_found"}
    return {"status": order.status.value, "delivered": order.status == OrderStatus.DELIVERED}


@mcp.tool()
def check_address_change_eligibility(order_key: str) -> dict:
    """Whether the delivery address can still be changed. Backs `/address_change_eligibility`."""
    order = db.get(order_key)
    if not order:
        return {"eligible": False, "reason": "order_not_found"}
    eligible = order.status in (OrderStatus.PLACED,)
    reason = None if eligible else f"order already {order.status.value}"
    return {"eligible": eligible, "reason": reason}


@mcp.tool()
def change_delivery_address(order_key: str, new_address: str) -> dict:
    """Update an order's delivery address. Backs `/change_delivery_address`."""
    order = db.get(order_key)
    if not order:
        return {"success": False, "reason": "order_not_found"}
    order.delivery_address = new_address
    return {"success": True, "delivery_address": new_address}


@mcp.tool()
def view_order(order_key: str) -> list[dict]:
    """Return the items in an order. Backs `/view_order`."""
    order = db.get(order_key)
    if not order:
        return []
    return [i.model_dump(mode="json") for i in order.items]


@mcp.tool()
def get_return_options(item_key: str) -> dict:
    """Return eligible return/refund/reorder options for an item. Backs `/return_options`."""
    order = db.find_order_for_item(item_key)
    if not order:
        return {"options": [], "reason": "item_not_found"}
    # Simple policy: delivered orders get all three options; anything else, none.
    if order.status != OrderStatus.DELIVERED:
        return {"options": [], "reason": "item not yet delivered"}
    return {"options": ["order-return-refund", "order-return-return", "order-return-reorder"]}


@mcp.tool()
def process_return(item_key: str, mode: ReturnMode) -> dict:
    """Execute a refund/return/reorder for an item. Backs `/process_return`.

    NOTE: idempotency — in a real backend, require an idempotency key
    (e.g. ticket_id) here so a graph retry never double-processes a refund.
    """
    order = db.find_order_for_item(item_key)
    if not order:
        return {"success": False, "reason": "item_not_found"}
    return {"success": True, "mode": mode, "order_key": order.key, "item_key": item_key}


if __name__ == "__main__":
    mcp.run(transport="stdio")  # default transport, explicit here for clarity