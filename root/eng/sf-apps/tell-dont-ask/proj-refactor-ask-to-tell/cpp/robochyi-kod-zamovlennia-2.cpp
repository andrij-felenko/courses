Order o("A-1");
o.pay();      // new -> paid
o.ship();     // paid -> shipped
// o.cancel(); // кине OrderError: "скасувати вже не можна (зараз shipped)"

// склад більше НЕ МОЖЕ відвантажити неоплачене — навіть якби забув перевірку:
Order bad("A-2");
try {
    bad.ship();          // OrderError: "відвантажити можна лише оплачене (зараз new)"
} catch (const OrderError& e) {
    // помилку видно ТУТ, а не через тиждень у зіпсованих даних
}
