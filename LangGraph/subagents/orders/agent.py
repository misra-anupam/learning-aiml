from langgraph import StateGraph, END, START
from .state import OrderState

def route_by_intent(state: OrderState) -> str:
    return state["action"]

def delivery_address_check_router(state: OrderState) -> str:
    if state["delivery_address_change_eligibility"]:
        return "yes"
    else:
        return "no"

def delivery_date_check_router(state: OrderState) -> str:
    if state["delivery_date_change_eligibility"]:
        return "yes"
    else:
        return "no"

class Orders:

    def __init__(self):
       
        """
        Load MCP for order management.
        """
        pass

    def load_recent_orders(self, state):

        """
        Load recent top 5 orders.
        Call MCP on /list and save to state with key recent_orders = List[Order]
        """
        pass

    def save_order_reference(self, state):

        """
        Accept user selection and save order reference to state with key order=Order(key=...).
        """
        pass

    def intent(self, state):

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
    
    def track(self, state):

        """
        Track order status.
        Call MCP on /track with order
        """
        pass

    def cancel(self, state):

        """
        Check if order can be cancelled.
        Call MCP on /cancellation_eligibility with order
        If yes, cancel it, if no, mention the same.
        If successful, /cancel with order
        """
        pass

    def check_if_delivery_date_can_be_changed(self, state):

        """
        Check if order has been delivered.
        If not delivered, can delivery date be changed?
        Call MCP on /date_change_eligibility with order
        Update state with key delivery_date_change_eligibility to True or False
        """
        pass

    def change_delivery_date(self, state):

        """
        Accept from user the new delivery date
        Call MCP on /change_delivery_date with order and new delivery date
        """
        pass

    def check_if_delivery_address_can_be_changed(self, state):

        """
        Check if order has been delivered.
        Call MCP on /order_status
        If not delivered, can address be changed?
        Call MCP on /address_change_eligibility with order
        Update state with key delivery_address_change_eligibility to True or False
        """
        pass

    def change_delivery_address(self, state):

        """
        Accept from user the new delivery address
        Call MCP on /change_delivery_address with order and new delivery address
        """
        pass

    def load_order_items(self, state):
        
        """
        Show expected items in order.
        Call MCP on /view_order with order and save to state with key=List[Item]
        """
        pass

    def identify_order_items_issue(self, state):

        """
        Understand what is the issue
        - defective
        - missing
        - wrong
        Write to state with key order_item_issue=IssueType
        """
        pass

    def save_issue_item(self, state):
        
        """
        Accept user selection and save issue item to state with key issue_item=Item(key=...).
        """
        pass

    def load_options_reorder_or_return_or_refund(self, state):

        """
        Check policy if item can be refunded.
        Offer user options accordingly.
        Call MCP on /return_options with item and save response to state with key return_options
        """
        pass

    def save_missing_defective_wrong_item_input(self, state):
        
        """
        Accept user input and accordingly trigger action. Save response to state with key return_mode
        """
        pass

    def process_item_return(self, state):

        """
        Refund/reorder/return the order.
        """
        pass

    def talk_to_human(self, state):
        
        """
        HITL -> When not addressed by the above options
        Give option to user to raise a ticket to handle the same
        """
        pass

    def redelivery_request(self, state):
        
        """
        Schedule delivery on today()+1 on /change_delivery_date
        Call MCP on /change_delivery_date with tomorrow's date
        """
        pass

    def build_graph(self):

        graph = StateGraph()

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

        graph.add_edge(START, "load_recent_orders")
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

        graph.add_conditional_edge(
            "check_if_delivery_address_can_be_changed",
            delivery_address_check_router,
            {
                "yes":"change_delivery_address",
                "no":END
            }
        )
        graph.add_conditional_edge(
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

        return graph.compile()

