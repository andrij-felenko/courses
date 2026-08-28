const o = new Order("A-001");
o.pay();      // New → Paid
o.ship();     // Paid → Shipped
o.ship();     // ігнор: повторне відправлення (стан «Shipped») — стан не змінився
o.refund();   // Shipped → Refunded
console.log(o.stateName);         // "Refunded"

try { o.cancel(); }               // у Refunded cancel не описаний → заборона з бази
catch (e) { console.log((e as Error).message); }
// "не можна скасувати: замовлення у стані «Refunded»"

console.log(o.logbook);
// [ "New → Paid", "Paid → Shipped",
//   "ігнор: повторне відправлення (стан «Shipped»)",
//   "Shipped → Refunded" ]
