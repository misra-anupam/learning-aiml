from state import OrderState

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
    
def entry_router(state: OrderState) -> str:
    return "has_order" if state.get("order") else "no_order"