// Ефект як ДАНІ: не робимо його, а описуємо значенням
type Effect =
  | { kind: "saveTotal"; id: number; total: number }
  | { kind: "notify";    to: string; text: string };

// ЧИСТЕ ядро: приймає замовлення й політику, ПОВЕРТАЄ план ефектів
function decide(order: Order, p: Pricing): Effect[] {
  const total = totalPrice(order.items, p.taxRate);
  return [
    { kind: "saveTotal", id: order.id, total },
    { kind: "notify", to: order.email, text: `Разом: ${total}` },
  ];
}
