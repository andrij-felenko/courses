# збірка застосунку: підписки в одному місці
bus.subscribe("OrderPlaced", lambda e: send_confirmation_email(e))
bus.subscribe("OrderPlaced", lambda e: award_loyalty_points(e))
bus.subscribe("OrderPlaced", lambda e: notify_shipping(e))

# сам видавець нічого про них не знає
def place_order(cart: Cart) -> None:
    order = save_order(cart)
    reserve_stock(order)
    bus.publish("OrderPlaced", {"order_id": order.id, "user_id": cart.user_id})
