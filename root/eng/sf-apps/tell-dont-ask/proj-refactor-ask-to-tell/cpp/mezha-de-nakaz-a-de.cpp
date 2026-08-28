// показ — читаємо стан, щоб намалювати
std::string line = "#" + order.id() + " — " + toString(order.status());

// сортування — читаємо стан як ключ; нічого не міняємо
std::sort(orders.begin(), orders.end(),
    [](const Order& a, const Order& b) { return a.status() < b.status(); });

// звіт — рахуємо, скільки замовлень оплачено; жодної зміни станів
long paid = std::count_if(orders.begin(), orders.end(),
    [](const Order& o) { return o.status() == Status::Paid; });
