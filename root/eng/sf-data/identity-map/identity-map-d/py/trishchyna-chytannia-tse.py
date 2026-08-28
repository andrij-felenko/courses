# гілка 1 — служба оплати
order = Order.objects.get(pk=42)            # SELECT * FROM orders WHERE id=42
order.status = "paid"

# гілка 2 — служба знижок, дістає те саме замовлення через клієнта
customer = Customer.objects.get(pk=7)
same = customer.orders.get(pk=42)           # ЩЕ ОДИН SELECT * FROM orders WHERE id=42

order is same                               # False — два об'єкти на один рядок
same.discount = 15

order.save()   # UPDATE orders SET status='paid', discount=0  WHERE id=42
same.save()    # UPDATE orders SET status='new',  discount=15 WHERE id=42
