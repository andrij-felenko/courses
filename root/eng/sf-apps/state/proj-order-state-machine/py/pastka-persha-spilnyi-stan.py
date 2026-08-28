# ❌ ОТРУЄНО: власне змінне поле в об'єкті, який СПІЛЬНИЙ для всіх замовлень
class PaidState(OrderState):
    name = "Paid"
    paid_at = None                     # ← здається невинним

    def ship(self, order: "Order") -> None:
        self.paid_at = datetime.now()  # ← пише у СПІЛЬНИЙ об'єкт States.PAID
        order.transition_to(States.SHIPPED)
# Наслідок: States.PAID один на всі замовлення. Замовлення B оплатилось —
# перезаписало paid_at, поставлене замовленням A хвилину тому. Дані течуть
# між НЕ пов'язаними замовленнями. Баг плаваючий, відтворюється лише під
# навантаженням, коли два замовлення в Paid одночасно.
