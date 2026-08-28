# Підставні порти — усе в пам'яті, жодної бази й жодних грошей
from contextlib import contextmanager

class FakeRepo:
    def __init__(self, cart):
        self._cart = cart
        self.saved = []
    def load_cart(self, _cart_id): return self._cart
    def save(self, o): self.saved.append(o)

class FakeGateway:
    def __init__(self, fail=False):
        self.fail = fail
        self.charges = []
    def charge(self, amount, _card, key):
        if self.fail:
            raise RuntimeError("оплата відхилена")
        self.charges.append((amount, key))
        return "pay_1"

class FakeMailer:
    def __init__(self): self.sent = 0
    def send_confirmation(self, _order): self.sent += 1

class MemIdempotency:
    def __init__(self): self._map = {}
    def find(self, k): return self._map.get(k)
    def remember(self, k, r): self._map[k] = r

class PassThroughTx:                    # «прозора» транзакція: виняток проштовхує
    @contextmanager
    def begin(self):
        yield                           # роботу виконуємо; при винятку він летить далі


# ── Тести ──
def test_happy_path():
    repo = FakeRepo(cart_with(2, items_worth(500)))
    gw, mail = FakeGateway(), FakeMailer()
    svc = OrderService(repo, gw, mail, MemIdempotency(), PassThroughTx())

    dto = svc.place_order(PlaceOrderCommand("c1", "tok", "k-1"))

    assert len(repo.saved) == 1          # рівно одне замовлення
    assert len(gw.charges) == 1          # рівно одне списання
    assert mail.sent == 1                # один лист
    assert dto.total == 500

def test_double_click_is_idempotent():
    repo = FakeRepo(cart_with(1, items_worth(100)))
    gw = FakeGateway()
    svc = OrderService(repo, gw, FakeMailer(), MemIdempotency(), PassThroughTx())

    a = svc.place_order(PlaceOrderCommand("c1", "tok", "same"))
    b = svc.place_order(PlaceOrderCommand("c1", "tok", "same"))

    assert b == a                        # той самий результат
    assert len(repo.saved) == 1          # а НЕ два замовлення
    assert len(gw.charges) == 1          # і НЕ два списання

def test_payment_failure_rolls_back():
    repo = FakeRepo(cart_with(1, items_worth(100)))
    gw = FakeGateway(fail=True)
    svc = OrderService(repo, gw, FakeMailer(), MemIdempotency(), PassThroughTx())

    with pytest.raises(RuntimeError, match="оплата відхилена"):
        svc.place_order(PlaceOrderCommand("c1", "tok", "k-3"))
    assert len(repo.saved) == 0          # нічого не збережено
