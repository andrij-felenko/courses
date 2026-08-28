// ❌ Марнотратно: новий об'єкт стану на КОЖЕН перехід, хоч він порожній і спільний
class NewState extends OrderState {
  pay(order: Order) { order.transitionTo(new PaidState()); }  // ← new щоразу
}
class PaidState extends OrderState {
  ship(order: Order) { order.transitionTo(new ShippedState()); }  // ← і тут new
}
// Мільйон замовлень пройшли через Paid → мільйон однакових PaidState,
// кожен живе рівно до наступного переходу й одразу йде у смітник.
// Тиск на збирач сміття на порожньому місці.
