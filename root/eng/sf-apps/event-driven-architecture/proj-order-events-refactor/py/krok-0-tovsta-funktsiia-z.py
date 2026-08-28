async def place_order(cart: Cart) -> Order:
    order = await save_order(cart)             # головна дія
    await reserve_stock(order)                 # головна дія

    # …а далі наросли наслідки, кожен — прямий виклик чужого модуля
    await send_confirmation_email(order)       # пошта
    await award_loyalty_points(order)          # бонуси
    await notify_shipping(order)               # доставка
    await track_sale_analytics(order)          # аналітика

    return order
