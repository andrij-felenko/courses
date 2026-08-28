#include <functional>

// Тепер годинник і "база" — це ЯВНІ входи (типажі-функції).
// Клас-обгортка для стану, щоб не тягнути глобалі всередину.
struct InvoiceCtx {
    double discountRate;       // було g_discountRate
    bool   forceSeasonal;      // було g_isBlackFriday
    std::function<std::tm()>              clock;    // шов #1: годинник
    std::function<double(const std::string&)> vat;  // шов #2: "база"
};

// "Чиста" версія: поведінка ТА САМА, але всі входи явні й керовані.
double computeInvoiceTotal(double net, const std::string& country,
                           int qty, const InvoiceCtx& ctx) {
    double subtotal = net * qty;

    if (ctx.discountRate > 0.0)
        subtotal *= (1.0 - ctx.discountRate);

    std::tm lt = ctx.clock();                       // замість std::time+localtime
    if (ctx.forceSeasonal || (lt.tm_mon == 10 && lt.tm_mday == 29))
        subtotal *= 0.90;

    double vat = ctx.vat(country);                  // замість lookupVatRate
    double total = subtotal * (1.0 + vat);

    long cents = (long)(total * 100.0);             // те саме усічення
    return cents / 100.0;
}

// Стара сигнатура жива — просто збирає контекст із глобалів і делегує.
// Жоден наявний виклик не зламано; поведінка байт-у-байт та сама.
extern double lookupVatRate(const std::string& country);
double computeInvoiceTotal(double net, const std::string& country, int qty) {
    InvoiceCtx ctx;
    ctx.discountRate  = g_discountRate;
    ctx.forceSeasonal = g_isBlackFriday;
    ctx.clock = []{ std::time_t t = std::time(nullptr);
                    return *std::localtime(&t); };
    ctx.vat   = [](const std::string& c){ return lookupVatRate(c); };
    return computeInvoiceTotal(net, country, qty, ctx);
}
