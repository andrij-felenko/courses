// Додали стан OnHold, але забули клітину (OnHold, cancel) —
// бо з утримання теж мусить бути можна скасувати замовлення.
class OnHoldState extends OrderState {
  readonly name = "OnHold";
  pay(order: Order) { order.transitionTo(States.Paid); }   // платіж підтвердили
  // cancel — ЗАБУЛИ описати
}

const o = new Order("B-002");
/* ... замовлення потрапило в OnHold ... */
o.cancel();
// → IllegalTransition: "не можна скасувати: замовлення у стані «OnHold»"
// Перший же тест, що торкнеться цієї клітини, ГУЧНО падає. Дірку видно одразу.
