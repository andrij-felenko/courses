def test_place_order_characterization():
    m = TestableOrderManager()
    cart = Cart([Item("Кава", 19.99, 1), Item("Чашка", 4.50, 2)])
    user = User(42, "vip@x", is_vip=True)

    total = m.place_order(cart, user)

    # ЗАФІКСОВАНО ЯК Є. Хвіст ...0999999999998 — майже напевно баг (тікет #123),
    # але ЗАРАЗ ми його не чіпаємо: тест стереже поведінку, а не правильність.
    assert total == 26.090999999999998
    assert m.conn.calls == [
        ("INSERT INTO orders(user_id, total) VALUES(?, ?)", (42, 26.090999999999998)),
    ]
    assert m.smtp.sent == [
        ("shop@x", "vip@x", "Замовлення на 26.090999999999998 прийнято"),
    ]
