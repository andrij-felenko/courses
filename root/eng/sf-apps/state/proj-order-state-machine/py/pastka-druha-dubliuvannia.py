# ❌ Марнотратно: новий об'єкт стану на КОЖЕН перехід, хоч він порожній і спільний
class NewState(OrderState):
    def pay(self, order: "Order") -> None:
        order.transition_to(PaidState())     # ← новий об'єкт щоразу

class PaidState(OrderState):
    def ship(self, order: "Order") -> None:
        order.transition_to(ShippedState())  # ← і тут новий
# Мільйон замовлень пройшли через Paid → мільйон однакових PaidState,
# кожен живе до наступного переходу й одразу йде у смітник.
# Тиск на збирач сміття на порожньому місці.
