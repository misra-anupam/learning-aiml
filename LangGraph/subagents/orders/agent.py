
class Orders:

    def __init__(self):
       
        """
        Load MCP for order management.
        """
        pass

    def load_recent_orders(self, state, input):

        """
        Load recent top 5 orders.
        """
        pass

    def save_order_reference(self, state, input):

        """
        Accept user selection and save order reference to state.
        """
        pass

    def track(self, state, input):

        """
        Track order status.
        """
        pass

    def cancel(self, state, input):

        """
        Check if order can be cancelled.
        If yes, cancel it, if no, mention the same.
        """
        pass

    def change_delivery_date(self, state, input):

        """
        Check if order has been delivered.
        If not delivered, can delivery date be changed?
        If yes, change delivery date.
        """
        pass

    def change_address(self, state, input):

        """
        Check if order has been delivered.
        If not delivered, can address be changed?
        If yes, change delivery address.        
        """
        pass

    def load_order_item(self, state, input):
        
        """
        Show expected items in order.
        """
        pass

    def save_missing_item(self, state, input):
        
        """
        Accept user selection and save missing item to state.
        """
        pass

    def save_wrong_item(self, state, input):
        
        """
        Accept user selection and save wrong item to state.
        """
        pass

    def save_defective_item(self, state, input):
        
        """
        Accept user selection and save defective item to state.
        """
        pass

    def load_options_reorder_or_refund(self, state, input):

        """
        Check policy if item can be refunded.
        Offer user options accordingly.
        
        """
        pass

    def save_missing_defective_wrong_item_input(self, state, input):
        
        """
        Accept user input and accordingly trigger action.
        """
        pass

    def raise_ticket(self, state, input):
        
        """
        HITL -> When not addressed by the above options
        """
        pass


    def redelivery_request(self, state, input):
        
        """
        Schedule delivery on today()+1 on /change_delivery_date
        """
        pass