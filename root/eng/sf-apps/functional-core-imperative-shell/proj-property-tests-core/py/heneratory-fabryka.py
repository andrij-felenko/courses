from hypothesis import strategies as st

# товар: ціна — невід'ємне ціле (копійки), кількість — 0..100
item = st.builds(Item,
    price=st.integers(min_value=0, max_value=100_000),
    qty=st.integers(min_value=0, max_value=100))

# заморожений рахунок: усе випадкове, але frozen ЗАВЖДИ True
frozen_acc = st.builds(Account,
    id=st.text(), user_id=st.text(),
    balance=st.integers(min_value=0, max_value=1_000_000),
    frozen=st.just(True))
