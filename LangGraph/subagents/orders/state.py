from typing import TypedDict
from pydantic import Field
from uuid import UUID

class OrderAction(TypedDict):
    action: Field()

class Order(TypedDict):
    order_id: UUID4

class Item(TypedDict):
    item_id: UUID4

class OrderState(TypedDict):

    action: OrderAction
    order: Order
    wrong_item: Item
