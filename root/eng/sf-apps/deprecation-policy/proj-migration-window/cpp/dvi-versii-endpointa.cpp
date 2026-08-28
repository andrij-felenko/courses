#include <vector>

// Багата модель замовлення — те, що реально є в системі.
struct Money   { int64_t value; std::string currency; };   // {value, currency}
struct Order   { uint64_t id; Money amount; };

std::vector<Order> load_orders(const Request& req);         // спільне джерело даних

// Проста сериалізація в JSON (тут — псевдо-збирач рядка заради стислості;
// у реальному коді — нормальний JSON-письменник).
static std::string to_json_v2(const std::vector<Order>& os);
static std::string to_json_v1(const std::vector<Order>& os);

// ── НОВИЙ ШЛЯХ: повна реалізація, джерело правди ────────────────────────────
// GET /api/v2/orders  — формат v2: amount = {value, currency}
void handle_orders_v2(const Request& req, Response& res) {
    std::vector<Order> orders = load_orders(req);           // єдина логіка вибірки
    res.status = 200;
    res.body   = to_json_v2(orders);                        // багатий формат
}

// ── СТАРИЙ ШЛЯХ: тонка обгортка над новим ───────────────────────────────────
// GET /api/v1/orders — формат v1: amount = ціле (копійки), без валюти.
// Делегує в v2-логіку, ЗВУЖУЄ результат, чіпляє попередження й лічить себе.
DeprecationMeter g_orders_v1_meter;                         // телеметрія цього шляху

void handle_orders_v1(const Request& req, Response& res) {
    // 1. Спільна логіка — та сама, що в v2. Жодного дубля вибірки даних.
    std::vector<Order> orders = load_orders(req);

    // 2. ЗВУЖЕННЯ: багатий Order → бідний формат v1.
    //    Валюту відкидаємо (v1 її не має), лишаємо ціле value.
    //    Звузити повне до неповного — завжди можна; тут просто губимо currency.
    res.status = 200;
    res.body   = to_json_v1(orders);

    // 3. Попередження — відповідь валідна, але чесно каже «переходь».
    mark_deprecated(res,
        /*deprecated_since=*/ 1735689600,                   // 2025-01-01
        /*sunset_at=*/        1798761600,                   // 2027-01-01
        /*successor_uri=*/    "/api/v2/orders",
        /*docs_uri=*/         "https://api.example.com/deprecations/orders-v1");

    // 4. Телеметрія: хтось іще ходить старим шляхом — рахуємо й записуємо, хто.
    g_orders_v1_meter.record(identify_caller(req));
}
