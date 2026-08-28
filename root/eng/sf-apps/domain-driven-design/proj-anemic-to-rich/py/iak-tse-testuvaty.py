import pytest

# ── Щасливий шлях: законні переходи ведуть куди слід ──
def test_draft_activates_then_enters_grace():
    p = Policy("P-1", None, Money.of(12000, "UAH"))
    p.activate()
    assert p.status is PolicyStatus.ACTIVE
    p.enter_grace_period()
    assert p.status is PolicyStatus.GRACE

def test_payment_within_premium_is_accepted():
    p = Policy("P-2", None, Money.of(10000, "UAH"))
    p.activate()
    p.add_payment(Money.of(4000, "UAH"), None)
    assert p.paid_total().cents == 4000

# ── Охорона інваріантів: заборонене кидає, стан НЕ псується ──
def test_cannot_enter_grace_from_draft():
    p = Policy("P-3", None, Money.of(10000, "UAH"))
    with pytest.raises(DomainError):
        p.enter_grace_period()
    assert p.status is PolicyStatus.DRAFT           # стан лишився недоторканим

def test_payment_over_premium_is_rejected():
    p = Policy("P-4", None, Money.of(10000, "UAH"))
    p.activate()
    p.add_payment(Money.of(8000, "UAH"), None)
    with pytest.raises(DomainError):
        p.add_payment(Money.of(3000, "UAH"), None)
    assert p.paid_total().cents == 8000             # невдалий платіж не додався

def test_payment_in_wrong_currency_is_rejected_by_money():
    p = Policy("P-5", None, Money.of(10000, "UAH"))
    p.activate()
    with pytest.raises(DomainError):
        p.add_payment(Money.of(1000, "USD"), None)
