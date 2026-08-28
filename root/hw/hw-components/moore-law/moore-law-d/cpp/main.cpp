#include <cmath>

// У скільки разів зросте складність за `years` років
// при подвоєнні кожні `double_time` років (закон Мура: double_time = 2).
double moore_factor(double years, double double_time) {
    double doublings = years / double_time;   // скільки подвоєнь сталося
    return std::pow(2.0, doublings);          // кожне подвоєння — множник 2
}

// Приклад: транзистори на флагманському чипі.
// 1971: Intel 4004 — 2300 транзисторів.
// Скільки прогнозує закон Мура через 50 років (до 2021)?
double base   = 2300.0;
double factor = moore_factor(50.0, 2.0);      // 2^(50/2) = 2^25 ≈ 33.5 млн
double pred   = base * factor;                // ≈ 7.7×10¹⁰ — близько 77 мільярдів
