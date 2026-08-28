#include <string>
#include <ctime>
#include <cstdio>

// Глобальний мутабельний стан — його виставляє хтось десь-інде,
// а функція мовчки на нього спирається.
double g_discountRate = 0.0;          // "проведено" з іншого модуля
bool   g_isBlackFriday = false;

// Легасі-функція. Хвороби, які роблять її нетестовною:
//  1) читає глобальний стан (g_discountRate, g_isBlackFriday);
//  2) сама лізе до годинника (std::time) — результат залежить від дати;
//  3) сама лізе до "бази" через глобальну функцію lookupVatRate();
//  4) усе це вшито намертво, підмінити нічим.
extern double lookupVatRate(const std::string& country);  // "ходить у БД"

double computeInvoiceTotal(double net, const std::string& country, int qty) {
    double subtotal = net * qty;

    // знижка з глобального стану
    if (g_discountRate > 0.0)
        subtotal *= (1.0 - g_discountRate);

    // сезонна знижка — залежить від РЕАЛЬНОЇ дати (годинник!)
    std::time_t now = std::time(nullptr);
    std::tm* lt = std::localtime(&now);
    if (g_isBlackFriday || (lt->tm_mon == 10 && lt->tm_mday == 29))  // 29 листопада
        subtotal *= 0.90;

    // ПДВ — ставку тягне з "бази" (мережа / БД)
    double vat = lookupVatRate(country);        // напр., 0.19 для "DE"
    double total = subtotal * (1.0 + vat);

    // копійки округляємо донизу (як воно історично й робило)
    long cents = (long)(total * 100.0);         // усічення, не round!
    return cents / 100.0;
}
