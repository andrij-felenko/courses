import time

# Ядро: тільки бізнес-правило замовлення. Єдиний актор — власник домену.
class PlaceOrder:
    def __init__(self, repo):
        self.repo = repo

    def __call__(self, order):
        self.repo.save(order)
        return order.id

# Кожна наскрізна турбота — окремий декоратор, що ОБГОРТАЄ будь-який обробник.
def with_logging(handler):
    def wrapped(order):
        log.info("place order %s", order.id)
        result = handler(order)
        log.info("order placed: %s", result)
        return result
    return wrapped

def with_timing(handler):
    def wrapped(order):
        started = time.perf_counter()
        try:
            return handler(order)
        finally:
            metrics.observe("place_order", time.perf_counter() - started)
    return wrapped

# Збірка: ядро загорнуте в шари; саме воно про журнал і заміри не знає.
handler = with_logging(with_timing(PlaceOrder(repo)))
order_id = handler(order)
