class FakeConn:
    def __init__(self): self.calls = []
    def execute(self, sql, *args): self.calls.append((sql, args))

class FakeSmtp:
    def __init__(self): self.sent = []
    def sendmail(self, frm, to, body): self.sent.append((frm, to, body))

class TestableOrderManager(OrderManager):        # підклас ЛИШЕ для тесту
    def __init__(self):
        self.conn, self.smtp = FakeConn(), FakeSmtp()
    def _open_db(self):   return self.conn        # шов спрацював
    def _open_smtp(self): return self.smtp
