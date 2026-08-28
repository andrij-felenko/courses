class OrderRepository {
  constructor(private connect: () => Conn) {}
  save(user: User, total: number): void {
    this.connect().execute(
      "INSERT INTO orders(user_id, total) VALUES(?, ?)", user.id, total);
  }
}

class EmailNotifier {
  constructor(private openSmtp: () => Smtp) {}
  orderPlaced(user: User, total: number): void {
    this.openSmtp().send(
      "shop@x", user.email, `Замовлення на ${total} прийнято`);
  }
}

test("Repository — пише очікуваний рядок", () => {
  const conn = new FakeConn();
  new OrderRepository(() => conn).save({ id: 42, email: "vip@x", isVip: true }, 26.09);
  assert.deepEqual(conn.calls, [
    ["INSERT INTO orders(user_id, total) VALUES(?, ?)", [42, 26.09]],
  ]);
});

test("Notifier — шле очікуваний лист", () => {
  const smtp = new FakeSmtp();
  new EmailNotifier(() => smtp).orderPlaced({ id: 42, email: "vip@x", isVip: true }, 26.09);
  assert.deepEqual(smtp.sent, [["shop@x", "vip@x", "Замовлення на 26.09 прийнято"]]);
});
