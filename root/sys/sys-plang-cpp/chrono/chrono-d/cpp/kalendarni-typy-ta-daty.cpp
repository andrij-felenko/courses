using namespace std::chrono;

// Створення дати: 14 серпня 2026 року
year_month_day date1 = 2026y / August / 14d;
year_month_day date2 = 14d / August / 2026y;

// Перевірка коректності дати (наприклад, 29 лютого)
if (date1.ok()) {
    // Дата є дійсною
}

// Перетворення дати у точку часу системного годинника за O(1)
sys_days tp = sys_days(date1); // time_point<system_clock, days>
