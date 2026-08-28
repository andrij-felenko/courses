# ДО: один метод валідує, рахує ціну, пише в базу й шле лист.
# Чотири причини змінюватись зрощені в одному місці.
class OrderManager:
    def place_order(self, cart, user):
        if not cart.items:                       # 1) перевірка
            raise ValueError("порожній кошик")
        for it in cart.items:
            if it.qty <= 0:
                raise ValueError("хибна кількість")

        total = sum(it.price * it.qty for it in cart.items)   # 2) ціна
        if user.is_vip:
            total *= 0.9

        conn = db.connect()                       # 3) запис у базу
        conn.execute("INSERT INTO orders(...) VALUES(...)", user.id, total)

        smtp = smtplib.SMTP("mail.local")         # 4) сповіщення
        smtp.sendmail("shop@x", user.email, f"Замовлення на {total} прийнято")
        return total
