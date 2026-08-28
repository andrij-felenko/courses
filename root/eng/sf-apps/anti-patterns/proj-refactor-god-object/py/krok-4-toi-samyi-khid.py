class OrderValidator:
    def check(self, cart):
        if not cart.items:
            raise ValueError("порожній кошик")
        for it in cart.items:
            if it.qty <= 0:
                raise ValueError("хибна кількість")

def test_validator_rejects_empty_cart():
    try:
        OrderValidator().check(Cart([]))
        assert False, "мало впасти"
    except ValueError as e:
        assert str(e) == "порожній кошик"

def test_validator_rejects_zero_qty():
    try:
        OrderValidator().check(Cart([Item("Кава", 19.99, 0)]))
        assert False, "мало впасти"
    except ValueError as e:
        assert str(e) == "хибна кількість"
