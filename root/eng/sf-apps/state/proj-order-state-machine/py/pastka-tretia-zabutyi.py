# Додали стан OnHold, але забули клітину (OnHold, cancel) —
# бо з утримання теж мусить бути можна скасувати замовлення.
class OnHoldState(OrderState):
    name = "OnHold"
    def pay(self, order: "Order") -> None:
        order.transition_to(States.PAID)     # платіж підтвердили
    # cancel — ЗАБУЛИ описати

o = Order("B-002")
# ... замовлення потрапило в OnHold ...
o.cancel()
# → IllegalTransition: "не можна скасувати: замовлення у стані «OnHold»"
# Перший же тест, що торкнеться цієї клітини, ГУЧНО падає. Дірку видно одразу.
