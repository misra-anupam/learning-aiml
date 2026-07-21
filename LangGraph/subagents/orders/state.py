from typing import TypedDict, List
from pydantic import Field, BaseModel, field_validator
from uuid import UUID

allowed_actions = [
    "order-track", "order-cancel", "order-change delivery address",
    "order-change delivery date", "order-complaint regarding order items",
    "order-talk to human", "order-redelivery request"
    ]

allowed_order_item_issues = [
    "order-item-missing", "order-item-defective", "order-item-wrong"
]

allowed_return_modes = [
    "order-return-refund", "order-return-return", "order-return-reorder"
]

class OrderAction(BaseModel):
    action: str

    @field_validator("action")
    @classmethod
    def validate_order_action(cls, value: str) -> str:

        if value not in allowed_actions:
            raise ValueError(f"action type must be one of {allowed_actions}")

        return value

class OrderItemIssue(BaseModel):
    issue: str
    
    @field_validator("issue")
    @classmethod
    def validate_order_item_issue(cls, value: str) -> str:

        if value not in allowed_order_item_issues:
            raise ValueError(f"Issue type must be one of {allowed_order_item_issues}")

        return value


class ReturnOptions(BaseModel):
    option: str
    
    @field_validator("option")
    @classmethod
    def validate_order_return_options(cls, value: str) -> str:

        if value not in allowed_return_modes:
            raise ValueError(f"Return mode must be one of {allowed_return_modes}")

        return value

class Order(TypedDict):
    key: UUID4

class Item(TypedDict):
    key: UUID4

class OrderState(TypedDict):

    action: OrderAction
    order: Order
    order_item_issue: OrderItemIssue
    issue_item: Item
    return_options: List[ReturnOptions]
    return_mode: str
