from typing import TypedDict, List, Literal, Annotated
from pydantic import Field, BaseModel, field_validator
from uuid import UUID
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

IssueType = Literal[
    "order-item-missing", "order-item-defective", "order-item-wrong"
]

ReturnMode = Literal[
    "order-return-refund", "order-return-return", "order-return-reorder"
]

OrderActionType = Literal[
    "order-track", "order-cancel", "order-change-delivery-address",
    "order-change-delivery-date", "order-complaint-regarding-order-items",
    "order-talk-to-human", "order-redelivery-request"
]

class OrderAction(BaseModel):
    action: OrderActionType

class OrderItemIssue(BaseModel):
    issue: IssueType

class ReturnOption(BaseModel):
    option: ReturnMode
class Order(TypedDict):
    key: UUID

class Item(TypedDict):
    key: UUID

class OrderSelection(BaseModel):
    key: UUID

class ItemSelection(BaseModel):
    key: UUID
    
class OrderState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]
    action: OrderActionType
    order: Order
    order_item_issue: IssueType
    issue_item: Item
    return_options: List[ReturnMode]
    return_mode: ReturnMode
    recent_orders: List[Order]
    order_items: List[Item]
    delivery_address_change_eligibility: bool
    delivery_date_change_eligibility: bool