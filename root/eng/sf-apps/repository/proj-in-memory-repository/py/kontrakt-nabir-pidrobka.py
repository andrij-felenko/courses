import pytest


@pytest.fixture(params=["in-memory", "postgres"])
def repo(request):
    if request.param == "in-memory":
        yield InMemoryOrderRepository()
    else:
        db = open_test_db()
        db.execute("TRUNCATE orders")
        yield SqlOrderRepository(db, mapper)
        db.close()


def test_saved_comes_back_equal(repo):
    o = paid_order("o-1", "c-19", 600, 1)
    repo.save(o)
    got = repo.by_id("o-1")
    assert got is not None
    assert got.total == 600
    assert got.is_paid() is True
    assert got.created_at == o.created_at


def test_mutation_after_save_is_invisible(repo):
    o = Order("o-1", "c-19", 600, day(1))          # «new»
    repo.save(o)
    o.mark_paid()                                  # ← без save
    assert repo.by_id("o-1").is_paid() is False


def test_recent_paid_orders_newest_first(repo):
    repo.save(paid_order("o-1", "c-19", 100, 1))
    repo.save(paid_order("o-3", "c-19", 300, 3))
    repo.save(paid_order("o-2", "c-19", 200, 2))   # навмисно не по черзі
    assert [o.id for o in repo.recent_paid_orders("c-19", 2)] == ["o-3", "o-2"]


def test_recent_paid_orders_breaks_tie_by_id(repo):
    repo.save(paid_order("o-1", "c-19", 100, 5))
    repo.save(paid_order("o-9", "c-19", 200, 5))   # той самий час
    assert [o.id for o in repo.recent_paid_orders("c-19", 1)] == ["o-9"]


def test_recent_paid_orders_skips_others_and_unpaid(repo):
    repo.save(paid_order("x-1", "c-77", 100, 1))
    repo.save(Order("o-2", "c-19", 200, day(2)))
    assert repo.recent_paid_orders("c-19", 10) == []


def test_by_id_is_none_after_remove(repo):
    o = paid_order("o-1", "c-19", 600, 1)
    repo.save(o)
    repo.remove(o)
    assert repo.by_id("o-1") is None
