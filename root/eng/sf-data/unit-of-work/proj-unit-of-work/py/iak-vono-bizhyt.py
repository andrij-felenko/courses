import sqlite3
conn = sqlite3.connect(":memory:")
conn.executescript('''
  CREATE TABLE customer("id" INTEGER PRIMARY KEY, name TEXT, points INT);
  CREATE TABLE "order"("id" INTEGER PRIMARY KEY, customer_id INT, total INT);
''')
mappers = [CustomerMapper(), OrderMapper()]

# ── операція 1: створити клієнта й замовлення ──
uow = UnitOfWork(conn, mappers)
alice = Customer("Аліса")
order = Order(alice); order.total = 250
uow.register_new(order)                # навмисне В НЕПРАВИЛЬНОМУ порядку:
uow.register_new(alice)                #   спершу замовлення, тоді клієнт
uow.commit()

print(alice.id)                        # → 1  — база призначила ключ клієнтові
print(conn.execute('SELECT customer_id FROM "order"').fetchone())   # → (1,)
