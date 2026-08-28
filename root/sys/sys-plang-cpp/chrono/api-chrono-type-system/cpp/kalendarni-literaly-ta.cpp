using namespace std::chrono;

// Різні варіанти конструювання year_month_day через оператор /
constexpr year_month_day ymd1 = 2026y / August / 14d;
constexpr year_month_day ymd2 = 14d / August / 2026y;
constexpr year_month_day ymd3 = August / 14d / 2026y;

// Перевірка валідності дати
static_assert(ymd1.ok());

// Отримання останнього дня лютого 2024 року (високосний рік)
constexpr year_month_day_last ymld = 2024y / February / last; // 29 лютого 2024
