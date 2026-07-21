from langgraph import StateGraph, END, START


class Orders:

    def __init__(self):
       
        """
        Load MCP for order management.
        """
        pass

    def load_recent_orders(self, state, input):

        """
        Load recent top 5 orders.
        Call MCP on /list
        """
        pass

    def save_order_reference(self, state, input):

        """
        Accept user selection and save order reference to state with key order=Order(key=...).
        """
        pass

    def intent(self, state, input):

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
        """
    
    def track(self, state, input):

        """
        Track order status.
        Call MCP on /track with order
        """
        pass

    def cancel(self, state, input):

        """
        Check if order can be cancelled.
        Call MCP on /cancellation_eligibility with order
        If yes, cancel it, if no, mention the same.
        If successful, /cancel with order
        """
        pass

    def change_delivery_date(self, state, input):

        """
        Check if order has been delivered.
        If not delivered, can delivery date be changed?
        Call MCP on /date_change_eligibility with order
        If yes, change delivery date.
        If successful, /change_delivery_date with order and delivery date
        """
        pass

    def change_delivery_address(self, state, input):

        """
        Check if order has been delivered.
        Call MCP on /order_status
        If not delivered, can address be changed?
        Call MCP on /address_change_eligibility with order
        If yes, change delivery address.        
        If successful, /change_delivery_address with order and delivery address
        """
        pass

    def load_order_items(self, state, input):
        
        """
        Show expected items in order.
        Call MCP on /view_order with order
        """
        pass

    def identify_order_items_issue(self, state, input):

        """
        Understand what is the issue
        - defective
        - missing
        - wrong
        Write to state with key order_item_issue=OrderItemIssue(issue=...)
        """
        pass

    def save_issue_item(self, state, input):
        
        """
        Accept user selection and save issue item to state with key item=Item(key=...).
        """
        pass

    def load_options_reorder_or_return_or_refund(self, state, input):

        """
        Check policy if item can be refunded.
        Offer user options accordingly.
        Call MCP on /return_options with item and save response to state with key return_options
        """
        pass

    def save_missing_defective_wrong_item_input(self, state, input):
        
        """
        Accept user input and accordingly trigger action. Save response to state with key return_mode
        """
        pass

    def process_item_return(self, state, input):

        """
        Refund/reorder/return the order.
        """
        pass

    def talk_to_human(self, state, input):
        
        """
        HITL -> When not addressed by the above options
        Give option to user to raise a ticket to handle the same
        """
        pass

    def redelivery_request(self, state, input):
        
        """
        Schedule delivery on today()+1 on /change_delivery_date
        Call MCP on /change_delivery_date with tomorrow's date
        """
        pass

    def build_graph(self, state, input):

        graph = StateGraph()

        graph.add_node("load_recent_orders", self.load_recent_orders)
        graph.add_node("save_order_reference", self.save_order_reference)
        graph.add_node("intent", self.intent)
        graph.add_node("track", self.track)
        graph.add_node("cancel", self.cancel)
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
            {
                state["action"] == "order-track": "track",
                state["action"] == "order-cancel": "cancel",
                state["action"] == "order-change delivery address": "change_delivery_address",
                state["action"] == "order-change delivery date": "change_delivery_date",
                state["action"] == "order-complaint regarding order items": "load_order_items",
                state["action"] == "order-talk to human": "talk_to_human",
                state["action"] == "order-redelivery request": "redelivery_request"
            },
            {
                "track": "track",
                "cancel": "cancel",
                "change_delivery_address": "change_delivery_address",
                "change_delivery_date": "change_delivery_date",
                "load_order_items": "load_order_items",
                "talk_to_human": "talk_to_human",
                "redelivery_request":"redelivery_request"
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

