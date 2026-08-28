#include <cstdint>

// Вартість одного місяця для заданого розміру пачки.
// batch=1 означає «кожну подію окремим викликом».
double monthly_cost_usd(std::uint64_t users, std::uint32_t events_per_day,
                        std::uint32_t batch, double price_per_call) {
    std::uint64_t events_month = users * events_per_day * 30ULL;  // подій за місяць
    // Скільки викликів: пачка на 50 подій — це 1 виклик замість 50.
    std::uint64_t calls_month  = (events_month + batch - 1) / batch;
    return static_cast<double>(calls_month) * price_per_call;    // рахунок за місяць
}
