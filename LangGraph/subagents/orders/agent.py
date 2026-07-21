from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from state import OrderState, Order, Item, OrderAction, OrderSelection, OrderItemIssue, ItemSelection, ReturnOption
from routers import route_by_intent, delivery_date_check_router, delivery_address_check_router, entry_router
from chain import _chain
from mcp_client import OrdersMCPClient
from pathlib import Path

SERVER_SCRIPT = str(Path(__file__).parent / "mcp" / "mcp_server.py")

class OrdersAgent:

    def __init__(self, mcp_client: OrdersMCPClient):
        """
        mcp_client: async client exposing .call(endpoint: str, payload: dict) -> dict
        Injected so it can be shared/pooled across subgraphs and mocked in tests.
        """
        self.checkpointer = InMemorySaver()
        self.mcp = mcp_client

    @classmethod
    async def init_mcp(cls) -> "OrdersAgent":
        mcp_client = OrdersMCPClient(server_script="mcp/mcp_server.py")
        await mcp_client.connect()
        return cls(mcp_client=mcp_client)

    async def load_recent_orders(self, state: OrderState, config: RunnableConfig):

        """
        Assuming the user is authenticated & the filtering of orders by user has been done.
        Load recent top 5 orders.
        Call MCP on /list and save to state with key recent_orders = List[Order]
        Ideally we would want to get all orders within 30 days
        [Assuming orders can be actioned upon upto 30 days]
        """
        orders = await self.mcp.call("/list", {})
        recent = [Order(key=o["key"]) for o in orders]
        summary = "\n".join(f"{i+1}. Order {o['key']} - {o.get('status', '')} - {',' .join(item["name"] for item in o["items"])}" for i, o in enumerate(orders))
        return {
            "recent_orders": recent,
            "messages": [AIMessage(content=f"Here are your recent orders:\n{summary}\nWhich order are you interested in?\n\nPlease enter the order ID")],
            # Resetting state vars from previous conversations, if the order ID has changed
            "action" : "",
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": "",
            "order_items": [],
            "delivery_address_change_eligibility": "",
            "delivery_date_change_eligibility": ""
        }

    async def save_order_reference(self, state: OrderState, config: RunnableConfig):

        """
        Accept user selection and save order reference to state with key order=Order(key=...).
        """
        user_reply = interrupt({
            "type": "input_request",
            "message": f"Which order is this about? \n{state['recent_orders']}",
        })
        order_selection_chain = _chain("order_selection", OrderSelection, state["recent_orders"])
        selection = await order_selection_chain.ainvoke({"query": user_reply})
        return {
            "order": Order(key=selection.key),
            "action": "",
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": "",
            "order_items": [],
            "delivery_address_change_eligibility": "",
            "delivery_date_change_eligibility": ""
            }

    async def intent(self, state: OrderState, config: RunnableConfig):

        """
        Determine user action for the identified order
        Allowed outputs
            - track
            - cancel
            - change delivery address
            - change delivery date
            - complaint regarding order items
            - talk to a human
            - redelivery

        Save it to OrderActionType
        """
        user_reply = interrupt({
            "type": "input_request",
            "message": "Describe your issue in a few words",
        })
        intent_chain = _chain("intent_classification", OrderAction)
        result = await intent_chain.ainvoke({"query": user_reply})
        return {
            "action": result.action,
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": "",
            "order_items": [],
            "delivery_address_change_eligibility": "",
            "delivery_date_change_eligibility": ""
            }
    
    async def track(self, state: OrderState, config: RunnableConfig):

        """
        Track order status.
        Call MCP on /track with order
        """
        status = await self.mcp.call("/track", {"order": state["order"]["key"]})
        return {
            "messages": [AIMessage(content=f"Your order status: {status}")],
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": "",
            "order_items": [],
            "delivery_address_change_eligibility": "",
            "delivery_date_change_eligibility": ""
            }

    async def cancel(self, state: OrderState, config: RunnableConfig):

        """
        Check if order can be cancelled.
        Call MCP on /cancellation_eligibility with order
        If yes, cancel it, if no, mention the same.
        If successful, /cancel with order
        """
        eligible = await self.mcp.call("/cancellation_eligibility", {"order": state["order"]["key"]})
        if not eligible.get("eligible"):
            return {"messages": [AIMessage(content="Sorry, this order is no longer eligible for cancellation.")]}
        await self.mcp.call("/cancel", {"order": state["order"]["key"]})
        return {
            "messages": [AIMessage(content="Your order has been cancelled.")],
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": "",
            "order_items": [],
            "delivery_address_change_eligibility": "",
            "delivery_date_change_eligibility": ""
            }

    async def check_if_delivery_date_can_be_changed(self, state: OrderState, config: RunnableConfig):

        """
        Check if order has been delivered.
        If not delivered, can delivery date be changed?
        Call MCP on /date_change_eligibility with order
        Update state with key delivery_date_change_eligibility to True or False
        If False, notify the user of the same
        """
        result = await self.mcp.call("/date_change_eligibility", {"order": state["order"]["key"]})
        eligible = bool(result.get("eligible"))
        if not eligible:
            return {"messages": [AIMessage(content="This order has already shipped, so the delivery date can't be changed.")]}
        
        else:
            return {
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": "",
            "order_items": [],
            "delivery_date_change_eligibility": eligible,
            "delivery_address_change_eligibility": ""
            }

    async def change_delivery_date(self, state: OrderState, config: RunnableConfig):

        """
        Accept from user the new delivery date
        Call MCP on /change_delivery_date with order and new delivery date
        """
        new_date = interrupt({
            "type": "input_request",
            "message": "What delivery date would you like instead?",
        })
        await self.mcp.call("/change_delivery_date", {"order": state["order"]["key"], "date": new_date})
        return {
            "messages": [AIMessage(content=f"Your delivery date has been updated to {new_date}.")],
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": "",
            "order_items": []
            }

    async def check_if_delivery_address_can_be_changed(self, state: OrderState, config: RunnableConfig):

        """
        Check if order has been delivered.
        Call MCP on /order_status
        If not delivered, can address be changed?
        Call MCP on /address_change_eligibility with order
        Update state with key delivery_address_change_eligibility to True or False
        If False, notify the user of the same
        """
        status = await self.mcp.call("/order_status", {"order": state["order"]["key"]})
        if status.get("delivered"):
            return {
                "delivery_address_change_eligibility": False,
                "messages": [AIMessage(content="This order has already been delivered, so the address can't be changed.")],
                "order_item_issue": "",
                "issue_item": "",
                "return_options": [],
                "return_mode": "",
                "order_items": [],
                "delivery_date_change_eligibility": ""
            }
        result = await self.mcp.call("/address_change_eligibility", {"order": state["order"]["key"]})
        eligible = bool(result.get("eligible"))

        if not eligible:
            return {"messages": [AIMessage(content="This order can't have its address changed — it's already been dispatched.")]}
        else:
            return {
                "order_item_issue": "",
                "issue_item": "",
                "return_options": [],
                "return_mode": "",
                "order_items": [],
                "delivery_date_change_eligibility": "",
                "delivery_address_change_eligibility": eligible
            }

    async def change_delivery_address(self, state: OrderState, config: RunnableConfig):

        """
        Accept from user the new delivery address
        Call MCP on /change_delivery_address with order and new delivery address
        """
        new_address = interrupt({
        "type": "input_request",
        "message": "What's the new delivery address?",
        })
        await self.mcp.call("/change_delivery_address", {"order": state["order"]["key"], "address": new_address})
        return {
            "messages": [AIMessage(content="Your delivery address has been updated.")],
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": "",
            "order_items": []
            }

    async def load_order_items(self, state: OrderState, config: RunnableConfig):
        
        """
        Show expected items in order.
        Call MCP on /view_order with order and save to state with key=List[Item]
        """
        items = await self.mcp.call("/view_order", {"order": state["order"]["key"]})
        order_items = [Item(key=i["key"]) for i in items]
        summary = "\n".join(f"{i+1}. {it.get('name', '')}" for i, it in enumerate(items))
        return {
            "order_items": order_items,
            "messages": [AIMessage(content=f"Here are the items in this order:\n{summary}\nWhich item, and what's the issue?")],
            "order_item_issue": "",
            "issue_item": "",
            "return_options": [],
            "return_mode": ""
        }

    async def identify_order_items_issue(self, state: OrderState, config: RunnableConfig):

        """
        Understand what is the issue
        - defective
        - missing
        - wrong
        Write to state with key order_item_issue=IssueType
        """
        order_issue = interrupt({
        "type": "input_request",
        "message": "What's the issue with your order?",
        })
        item_issue_chain = _chain("item_issue_classification", OrderItemIssue)
        result = await item_issue_chain.ainvoke({"query": order_issue})
        return {
            "order_item_issue": result.issue,
            "issue_item": "",
            "return_options": [],
            "return_mode": ""
            }

    async def save_issue_item(self, state: OrderState, config: RunnableConfig):
        
        """
        Accept user selection and save issue item to state with key issue_item=Item(key=...).
        """
        item_issue = interrupt({
        "type": "input_request",
        "message": f"Which item was {state['order_item_issue']}?",
        })
        issue_item_selection_chain = _chain("issue_item_selection", ItemSelection)
        selection = await issue_item_selection_chain.ainvoke({"query": item_issue})
        return {
            "issue_item": Item(key=selection.key),
            "order_item_issue": "",
            "return_options": [],
            "return_mode": ""
            }


    async def load_options_reorder_or_return_or_refund(self, state: OrderState, config: RunnableConfig):

        """
        Check policy if item can be refunded.
        Offer user options accordingly.
        Call MCP on /return_options with item and save response to state with key return_options
        """
        options = await self.mcp.call("/return_options", {"item": state["issue_item"]["key"]})
        return {
            "return_options": options,
            "messages": [AIMessage(content=f"Here's what we can do: {', '.join(options)}. Which would you like?")],
        }

    async def save_missing_defective_wrong_item_input(self, state: OrderState, config: RunnableConfig):
        
        """
        Accept user input and accordingly trigger action. Save response to state with key return_mode
        """
        return_option = interrupt({
            "type": "input_request",
            "message": f"Which action to take among {state['return_options']}?",
        })
        return_mode_chain = _chain("return_mode_selection", ReturnOption)
        result = await return_mode_chain.ainvoke({"query": return_option})
        return {"return_mode": result.option}

    async def process_item_return(self, state: OrderState, config: RunnableConfig):

        """
        Refund/reorder/return the order.
        """
        await self.mcp.call("/process_return", {"item": state["issue_item"]["key"], "mode": state["return_mode"]})
        return {"messages": [AIMessage(content=f"Done — we've processed a {state['return_mode']} for this item.")]}


    async def talk_to_human(self, state: OrderState, config: RunnableConfig):
        
        """
        HITL -> When not addressed by the above options
        Give option to user to raise a ticket to handle the same
        """
        thread_id = config["configurable"]["thread_id"]

        ticket_id = "241234"
        # ticket_id = await self.ticket_store.create_ticket(
        #     thread_id=thread_id,
        #     order=state.get("order"),
        #     conversation=state["messages"],
        #     priority="normal",  # could derive from sentiment in state if you're tracking it
        # )

        # self.notify_queue.delay(ticket_id)  # Celery task -> pushes to agent queue / alerting

        human_response = interrupt({
            "type": "human_handoff",
            "ticket_id": ticket_id,
            "message": "I've raised a ticket and a support agent will follow up shortly.",
        })

        # human_response is whatever the agent's tool sends on resume — see below
        return {"messages": [AIMessage(content=human_response["reply"])]}

    async def redelivery_request(self, state: OrderState, config: RunnableConfig):
        
        """
        Schedule delivery on today()+1 on /change_delivery_date
        Call MCP on /change_delivery_date with tomorrow's date
        """
        await self.mcp.call("/change_delivery_date", {"order": state["order"]["key"], "date": "tomorrow"})
        return {"messages": [AIMessage(content="We've scheduled redelivery for tomorrow.")]}


    def build_graph(self):

        graph = StateGraph(OrderState)

        graph.add_node("load_recent_orders", self.load_recent_orders)
        graph.add_node("save_order_reference", self.save_order_reference)
        graph.add_node("intent", self.intent)
        graph.add_node("track", self.track)
        graph.add_node("cancel", self.cancel)
        graph.add_node("check_if_delivery_address_can_be_changed", self.check_if_delivery_address_can_be_changed)
        graph.add_node("check_if_delivery_date_can_be_changed", self.check_if_delivery_date_can_be_changed)
        graph.add_node("change_delivery_date", self.change_delivery_date)
        graph.add_node("change_delivery_address", self.change_delivery_address)
        graph.add_node("load_order_items", self.load_order_items)
        graph.add_node("identify_order_items_issue", self.identify_order_items_issue)
        graph.add_node("save_issue_item", self.save_issue_item)
        graph.add_node("load_options_reorder_or_return_or_refund", self.load_options_reorder_or_return_or_refund)
        graph.add_node("save_missing_defective_wrong_item_input", self.save_missing_defective_wrong_item_input)
        graph.add_node("process_item_return", self.process_item_return)
        graph.add_node("talk_to_human", self.talk_to_human)
        graph.add_node("redelivery_request", self.redelivery_request)

        graph.add_conditional_edges(
            START,
            entry_router,
            {
                "has_order": "intent",
                "no_order": "load_recent_orders",
            },
        )       
        graph.add_edge("load_recent_orders", "save_order_reference")
        graph.add_edge("save_order_reference", "intent")

        graph.add_conditional_edges(
            "intent",
            route_by_intent,
            {
                "order-track": "track",
                "order-cancel": "cancel",
                "order-change-delivery-address": "check_if_delivery_address_can_be_changed",
                "order-change-delivery-date": "check_if_delivery_date_can_be_changed",
                "order-complaint-regarding-order-items": "load_order_items",
                "order-talk-to-human": "talk_to_human",
                "order-redelivery-request": "redelivery_request"
            }
        )

        graph.add_conditional_edges(
            "check_if_delivery_address_can_be_changed",
            delivery_address_check_router,
            {
                "yes":"change_delivery_address",
                "no":END
            }
        )
        graph.add_conditional_edges(
            "check_if_delivery_date_can_be_changed",
            delivery_date_check_router,
            {
                "yes":"change_delivery_date",
                "no":END
            }
        )

        graph.add_edge("load_order_items", "identify_order_items_issue")
        graph.add_edge("identify_order_items_issue", "save_issue_item")
        graph.add_edge("save_issue_item", "load_options_reorder_or_return_or_refund")
        graph.add_edge("load_options_reorder_or_return_or_refund", "save_missing_defective_wrong_item_input")
        graph.add_edge("save_missing_defective_wrong_item_input", "process_item_return")

        for item in [
            "track",
            "cancel",
            "change_delivery_address",
            "change_delivery_date",
            "process_item_return",
            "redelivery_request",
            "talk_to_human"
        ]:
            graph.add_edge(item, END)

        return graph.compile(checkpointer=self.checkpointer)

