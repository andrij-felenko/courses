// Захисний рівень (HPL) приймач обчислює з даних цілісності SBAS —
// це гарантована верхня межа горизонтальної похибки, у метрах.
// Допуск (HAL) задає поточна задача: для цього заходу — 40 м.
struct Integrity { double hpl_m; double hal_m; };

bool position_trustworthy(const Integrity& ig) {
    return ig.hpl_m <= ig.hal_m;   // межа під допуском → довіряти можна
}

Integrity ig{ .hpl_m = 12.4, .hal_m = 40.0 };
bool ok = position_trustworthy(ig);   // 12.4 ≤ 40.0 → true: використовувати

// Якби похмура іоносфера роздула межу:
ig.hpl_m = 47.0;
ok = position_trustworthy(ig);        // 47.0 ≤ 40.0 → false: НЕ використовувати
