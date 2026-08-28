// ── ДО: одна функція робить усе ──────────────────────────────────
#include <string>
#include <vector>
#include <iostream>

struct Item { double price; int qty; };

struct Order {
    int              id;
    std::string      customerTier;   // "regular" | "silver" | "gold"
    std::vector<Item> items;
    double           computedTotal;  // ← сюди функція запише результат
};

// глобальний стан — прихований вхід, про який сигнатура мовчить
double g_taxRate      = 0.20;
double g_freeShipFrom = 500.0;
double g_shipCost     = 49.0;

Database db;   // глобальне з'єднання з базою
Logger   log;  // глобальний лог

double computeOrderTotal(Order& order) {          // Order& — не const!
    double subtotal = 0.0;
    for (Item& it : order.items)
        subtotal += it.price * it.qty;

    // знижка за обсяг
    double volumeDisc = 0.0;
    if      (subtotal > 1000.0) volumeDisc = 0.10;
    else if (subtotal >  300.0) volumeDisc = 0.05;

    // знижка за рівень клієнта
    double tierDisc = 0.0;
    if      (order.customerTier == "gold")   tierDisc = 0.08;
    else if (order.customerTier == "silver") tierDisc = 0.04;

    // каскад: спершу обсяг, тоді рівень (множаться, не додаються)
    double afterDisc = subtotal * (1.0 - volumeDisc) * (1.0 - tierDisc);

    // податок із глобального курсу
    double taxed = afterDisc * (1.0 + g_taxRate);

    // доставка
    double shipping = (afterDisc >= g_freeShipFrom) ? 0.0 : g_shipCost;
    double total    = taxed + shipping;

    // ── а тепер ефекти, розсипані по функції ──
    order.computedTotal = total;                       // мутація входу
    db.saveTotal(order.id, total);                     // запис у базу
    log.info("order " + std::to_string(order.id) +
             " total=" + std::to_string(total));       // вивід у лог
    std::cout << "DEBUG total=" << total << "\n";       // ще й у консоль

    return total;
}
