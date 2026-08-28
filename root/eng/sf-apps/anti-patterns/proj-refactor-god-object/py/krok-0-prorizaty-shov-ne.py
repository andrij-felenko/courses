class OrderManager:
    def place_order(self, cart, user):
        if not cart.items:
            raise ValueError("порожній кошик")
        for it in cart.items:
            if it.qty <= 0:
                raise ValueError("хибна кількість")

        total = sum(it.price * it.qty for it in cart.items)
        if user.is_vip:
            total *= 0.9

        conn = self._open_db()                    # ← було db.connect()
        conn.execute("INSERT INTO orders(user_id, total) VALUES(?, ?)", user.id, total)

        smtp = self._open_smtp()                  # ← було smtplib.SMTP("mail.local")
        smtp.sendmail("shop@x", user.email, "Замовлення на %s прийнято" % total)
        return total

    # два шви — і більше нічого нового
    def _open_db(self):
        return db.connect()

    def _open_smtp(self):
        return smtplib.SMTP("mail.local")
