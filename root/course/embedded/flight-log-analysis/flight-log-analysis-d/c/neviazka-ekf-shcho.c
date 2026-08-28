#include <stdint.h>

// Значення тест-відношень з одного запису NKF4/XKF4 (уже видобуті парсером).
typedef struct { double sp, sv, sm, sh; } EkfRatios;   // поз., швид., компас, висота

typedef struct {
    int bad_streak;      // скільки поспіль зразків хоч одне відношення > 1
    int worst_multi;     // найдовша смуга, де >1 було на ≥2 давачах разом
} EkfVerdict;

// Прогін по зразках EKF за відрізок: шукаємо не сплеск, а ТРИВАЛІСТЬ і збіг.
static EkfVerdict ekf_scan(const EkfRatios *r, int n) {
    EkfVerdict v = {0, 0};
    int streak = 0, multi = 0;
    for (int i = 0; i < n; i++) {
        int over = (r[i].sp > 1) + (r[i].sv > 1) + (r[i].sm > 1) + (r[i].sh > 1);
        if (over >= 1) { streak++; if (streak > v.bad_streak) v.bad_streak = streak; }
        else            streak = 0;
        if (over >= 2) { multi++;  if (multi  > v.worst_multi) v.worst_multi = multi; }
        else            multi = 0;
    }
    return v;
}
