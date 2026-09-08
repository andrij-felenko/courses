// Обробник замовлення без синхронного звернення до зовнішнього API
async function createOrder(cmd: CreateOrderCommand, db: Transaction): Promise<OrderId> {
  const order = new Order(cmd.items, cmd.userId);
  await db.orders.insert(order);

  // Фіксація наміру виконати інтеграцію локально в тій самій транзакції
  await db.outbox.insert({
    type: "PAYMENT_REQUESTED",
    orderId: order.id,
    amount: order.totalAmount,
    status: "PENDING"
  });

  return order.id; // Клієнт отримує відповідь за кілька мілісекунд
}
