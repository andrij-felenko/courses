async function placeOrder(cart: Cart): Promise<Order> {
  const order = await saveOrder(cart);        // головна дія
  await reserveStock(order);                   // головна дія

  // …а далі наросли наслідки, кожен — прямий виклик чужого модуля
  await sendConfirmationEmail(order);          // пошта
  await awardLoyaltyPoints(order);             // бонуси
  await notifyShipping(order);                  // доставка
  await trackSaleAnalytics(order);             // аналітика

  return order;
}
