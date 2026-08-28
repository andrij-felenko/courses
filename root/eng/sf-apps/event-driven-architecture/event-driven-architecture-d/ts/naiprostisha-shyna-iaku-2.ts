// збірка застосунку: підписки в одному місці
bus.subscribe("OrderPlaced", (e) => sendConfirmationEmail(e));
bus.subscribe("OrderPlaced", (e) => awardLoyaltyPoints(e));
bus.subscribe("OrderPlaced", (e) => notifyShipping(e));

// сам видавець нічого про них не знає
function placeOrder(cart: Cart): void {
  const order = saveOrder(cart);
  reserveStock(order);
  bus.publish("OrderPlaced", { orderId: order.id, userId: cart.userId });
}
