#include <format>
#include <chrono>

auto now = std::chrono::system_clock::now();

// Форматування дати й часу за специфікаторами strftime
std::string time_str = std::format("{:%Y-%m-%d %H:%M:%S}", now);
// Приклад: "2026-08-14 19:25:00"

// Днів тижня та місяців
std::string verbose_date = std::format("{:%A, %B %d, %Y}", now);
// Приклад: "Friday, August 14, 2026"
