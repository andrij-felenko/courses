// ── Мемоізована обгортка над ЧИСТИМ ядром ────────────────────────
#include <unordered_map>
#include <sstream>

// ключ кеша = усе, від чого залежить результат (весь вхід ядра).
static std::string cacheKey(const Order& o, const Pricing& p) {
    std::ostringstream k;
    k << o.customerTier << '|'
      << p.taxRate << '|' << p.freeShipFrom << '|' << p.shipCost;
    for (const Item& it : o.items) k << '|' << it.price << 'x' << it.qty;
    return k.str();
}

Totals computeTotalsMemo(const Order& order, const Pricing& p) {
    static std::unordered_map<std::string, Totals> cache;

    std::string key = cacheKey(order, p);
    auto found = cache.find(key);
    if (found != cache.end())
        return found->second;                 // ← влучили: віддаємо збережене

    Totals t = computeTotals(order, p);        // промах: рахуємо ядром
    cache.emplace(key, t);                     // і запам'ятовуємо
    return t;
}
