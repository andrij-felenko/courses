// Уся таблиця як дані: (стан, подія) → наступний стан або спеціальна мітка.
type Cell = { to: string } | "reject" | "ignore";

const TABLE: Record<string, Record<string, Cell>> = {
  New:       { pay: {to:"Paid"}, cancel: {to:"Cancelled"},
               ship: "reject",   refund: "reject" },
  Paid:      { ship: {to:"Shipped"}, cancel: {to:"Refunded"}, refund: {to:"Refunded"},
               pay: "reject" },
  Shipped:   { refund: {to:"Refunded"}, ship: "ignore",
               pay: "reject", cancel: "reject" },
  Cancelled: { cancel: "ignore", pay: "reject", ship: "reject", refund: "reject" },
  Refunded:  { refund: "ignore", pay: "reject", ship: "reject", cancel: "reject" },
};

class Order {
  state = "New";
  logbook: string[] = [];
  constructor(readonly id: string) {}

  fire(event: string) {                       // ОДИН рушій на всі події
    const cell = TABLE[this.state]?.[event];
    if (cell === undefined || cell === "reject")
      throw new Error(`не можна ${event}: стан «${this.state}»`);
    if (cell === "ignore") { this.logbook.push(`ігнор: ${event}`); return; }
    this.logbook.push(`${this.state} → ${cell.to}`);
    this.state = cell.to;                      // + тут же побічна дія події, якщо треба
  }
  pay()    { this.fire("pay"); }
  ship()   { this.fire("ship"); }
  cancel() { this.fire("cancel"); }
  refund() { this.fire("refund"); }
}
