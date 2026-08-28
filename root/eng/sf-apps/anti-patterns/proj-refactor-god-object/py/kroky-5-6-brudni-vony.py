class OrderRepository:
    def __init__(self, connect):
        self._connect = connect
    def save(self, user, total):
        self._connect().execute(
            "INSERT INTO orders(user_id, total) VALUES(?, ?)", user.id, total)

class EmailNotifier:
    def __init__(self, open_smtp):
        self._open_smtp = open_smtp
    def order_placed(self, user, total):
        self._open_smtp().sendmail(
            "shop@x", user.email, "Замовлення на %s прийнято" % total)

def test_repository_writes_expected_row():
    conn = FakeConn()
    OrderRepository(lambda: conn).save(User(42, "vip@x", True), 26.09)
    assert conn.calls == [
        ("INSERT INTO orders(user_id, total) VALUES(?, ?)", (42, 26.09)),
    ]

def test_notifier_sends_expected_body():
    smtp = FakeSmtp()
    EmailNotifier(lambda: smtp).order_placed(User(42, "vip@x", True), 26.09)
    assert smtp.sent == [("shop@x", "vip@x", "Замовлення на 26.09 прийнято")]
