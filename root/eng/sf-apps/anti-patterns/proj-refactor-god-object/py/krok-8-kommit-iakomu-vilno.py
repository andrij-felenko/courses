# Item.price (грн, float) → Item.price_cents (копійки, int) — частина цієї ж зміни
class Pricer:
    def total(self, cart, user):
        cents = sum(it.price_cents * it.qty for it in cart.items)   # цілі копійки
        if user.is_vip:
            cents = (cents * 9 + 5) // 10        # −10% з явним округленням до копійки
        return cents

def test_pricer_vip_discount():
    cart = Cart([Item("Кава", price_cents=1999, qty=1),
                 Item("Чашка", price_cents=450, qty=2)])
    assert Pricer().total(cart, User(42, "vip@x", is_vip=True)) == 2609   # 26.09 грн
