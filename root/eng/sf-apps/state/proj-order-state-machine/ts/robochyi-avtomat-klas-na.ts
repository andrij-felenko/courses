// ── Спільний інтерфейс стану ──────────────────────────────────────────────
// Кожен стан мусить уміти відповісти на кожну з чотирьох подій.
// База дає безпечні типові відповіді, а конкретні стани перекривають лише те,
// що для них має сенс — так «забута клітина» стає явним рішенням, а не дірою.
abstract class OrderState {
  abstract readonly name: string;

  // Типова відповідь на дозволену-в-таблиці подію, яку стан не описав, — заборона.
  pay(order: Order):    void { this.reject("оплатити"); }
  ship(order: Order):   void { this.reject("відправити"); }
  cancel(order: Order): void { this.reject("скасувати"); }
  refund(order: Order): void { this.reject("повернути гроші"); }

  protected reject(action: string): never {
    throw new IllegalTransition(
      `не можна ${action}: замовлення у стані «${this.name}»`);
  }
  // Тихий ігнор — окремий, СВІДОМИЙ вихід, а не мовчазне «нічого не сталось».
  protected ignore(order: Order, note: string): void {
    order.log(`ігнор: ${note} (стан «${this.name}»)`);
  }
}

class IllegalTransition extends Error {}

// ── Контекст: тримає поточний стан і делегує йому все ──────────────────────
class Order {
  private state: OrderState = States.New;   // спільний екземпляр, див. нижче
  readonly logbook: string[] = [];

  constructor(readonly id: string) {}

  // Публічний API — жодного if за станом, самі делегації:
  pay()    { this.state.pay(this); }
  ship()   { this.state.ship(this); }
  cancel() { this.state.cancel(this); }
  refund() { this.state.refund(this); }

  // Перехід — єдина точка, де стан змінюється; звідси зручно логувати весь маршрут.
  transitionTo(next: OrderState) {
    this.log(`${this.state.name} → ${next.name}`);
    this.state = next;
  }
  get stateName() { return this.state.name; }
  log(msg: string) { this.logbook.push(msg); }
}

// ── Конкретні стани: кожен — один рядок таблиці ───────────────────────────
class NewState extends OrderState {
  readonly name = "New";
  pay(order: Order)    { /* провести оплату */ order.transitionTo(States.Paid); }
  cancel(order: Order) { order.transitionTo(States.Cancelled); }
  // ship, refund — не описані → база кине заборону. Це клітини (New,ship)/(New,refund).
}

class PaidState extends OrderState {
  readonly name = "Paid";
  ship(order: Order)   { /* відвантажити */ order.transitionTo(States.Shipped); }
  cancel(order: Order) { /* скасування після оплати = повернення грошей */
                         order.transitionTo(States.Refunded); }
  refund(order: Order) { order.transitionTo(States.Refunded); }
}

class ShippedState extends OrderState {
  readonly name = "Shipped";
  ship(order: Order)   { this.ignore(order, "повторне відправлення"); } // (Shipped,ship)=ігнор
  refund(order: Order) { order.transitionTo(States.Refunded); }
  // pay, cancel — база кине заборону: платити й скасовувати відправлене вже пізно.
}

// Кінцеві стани: будь-яка «дія» або заборонена, або ігнорується — далі шляху немає.
class CancelledState extends OrderState {
  readonly name = "Cancelled";
  cancel(order: Order) { this.ignore(order, "повторне скасування"); } // (Cancelled,cancel)=ігнор
}

class RefundedState extends OrderState {
  readonly name = "Refunded";
  refund(order: Order) { this.ignore(order, "повторне повернення"); } // (Refunded,refund)=ігнор
}

// ── Пул спільних екземплярів: по ОДНОМУ на стан на всю програму ───────────
const States = {
  New:       new NewState(),
  Paid:      new PaidState(),
  Shipped:   new ShippedState(),
  Cancelled: new CancelledState(),
  Refunded:  new RefundedState(),
} as const;
