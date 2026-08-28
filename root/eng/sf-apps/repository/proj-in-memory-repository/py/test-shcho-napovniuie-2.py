import pytest


@pytest.fixture
def orders() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()          # ← свіжий на КОЖЕН тест


@pytest.fixture
def loyalty(orders) -> LoyaltyService:
    return LoyaltyService(orders)


def test_three_recent_paid_over_500(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    orders.save(paid_order("o-3", "c-19", 800, 3))
    assert loyalty.is_loyal("c-19") is True


def test_only_two_paid(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    assert loyalty.is_loyal("c-19") is False


def test_exactly_500_is_not_over_500(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 500, 2))    # ← межа
    orders.save(paid_order("o-3", "c-19", 700, 3))
    assert loyalty.is_loyal("c-19") is False


def test_old_cheap_order_is_out_of_the_window(orders, loyalty):
    orders.save(paid_order("o-0", "c-19", 10, 0))     # ← найстаріше й дешеве
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    orders.save(paid_order("o-3", "c-19", 800, 3))
    assert loyalty.is_loyal("c-19") is True


def test_unpaid_does_not_count(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    orders.save(Order("o-3", "c-19", 9000, day(3)))   # ← лишилось «new»
    assert loyalty.is_loyal("c-19") is False


def test_other_customers_orders_do_not_count(orders, loyalty):
    orders.save(paid_order("o-1", "c-19", 600, 1))
    orders.save(paid_order("o-2", "c-19", 700, 2))
    orders.save(paid_order("x-1", "c-77", 800, 3))    # ← інший клієнт
    assert loyalty.is_loyal("c-19") is False
