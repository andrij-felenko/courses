from typing import Protocol

# РИЗИК НАЗВАНО Й ЗМЕНШЕНО: таймаут + повтор + запасний хід, і все за швом
class PaymentGateway(Protocol):         # шов: логіка знає лише інтерфейс
    def charge(self, customer_id: int, amount: float) -> PayResult: ...

def charge_customer(gw: PaymentGateway, customer_id: int, amount: float) -> PayResult:
    for _attempt in range(3):                # зменшуємо ЙМОВІРНІСТЬ збою
        r = gw.charge(customer_id, amount)   # (таймаут — усередині адаптера)
        if r.ok:
            return r
    # запасний хід зменшує ВТРАТУ: не валимо все, а ставимо платіж у чергу
    return PayResult.queued_for_retry(customer_id, amount)
# Постачальник за швом → якщо цей сервіс виявиться поганим, міняємо адаптер,
# а charge_customer і виклики не чіпаємо. Це відповідь на «невідоме невідоме».
