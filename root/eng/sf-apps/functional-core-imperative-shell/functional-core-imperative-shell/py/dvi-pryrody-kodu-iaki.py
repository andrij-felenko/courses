async def checkout(cart_id: str) -> None:
    cart = await db.load_cart(cart_id)            # дія: читання
    rate = await config.tax_rate()                # дія: читання

    total = sum(it.price * it.qty for it in cart.items)   # ↓ рішення в дії
    total *= 1 + rate
    if total > 1000:                              # знижка за великий чек
        total *= 0.95

    await db.save_order(cart_id, total)           # дія: запис
    await mailer.send_receipt(cart.email, total)  # дія: запис
