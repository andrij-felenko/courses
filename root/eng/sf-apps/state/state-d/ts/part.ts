class Order {
  state: "new" | "paid" | "shipped" = "new";

  pay() {
    if (this.state === "new") { /* провести оплату */ this.state = "paid"; }
    else if (this.state === "paid") throw new Error("уже оплачено");
    else if (this.state === "shipped") throw new Error("надто пізно платити");
  }
  ship() {
    if (this.state === "new") throw new Error("спершу оплатіть");
    else if (this.state === "paid") { /* відвантажити */ this.state = "shipped"; }
    else if (this.state === "shipped") throw new Error("уже відправлено");
  }
  // те саме розгалуження ще й у cancel(), і в refund(), і в кожному новому методі…
}
