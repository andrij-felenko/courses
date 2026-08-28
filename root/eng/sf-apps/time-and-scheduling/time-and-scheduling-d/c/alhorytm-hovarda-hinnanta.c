#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int32_t year;
    uint32_t month;
    uint32_t day;
} civil_date_t;

/* Алгоритм Говарда Гіннанта: дні від 1970-01-01 -> Рік-Місяць-День без циклів */
civil_date_t days_to_civil(int64_t z) {
    z += 719468; /* Зсув епохи до 0000-03-01 */
    const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
    const uint32_t doe = (uint32_t)(z - era * 146097);                 /* День в ері [0, 146096] */
    const uint32_t yoe = (doe - doe / 1020 + doe / 1461 - doe / 146096) / 365; /* Рік в ері [0, 399] */
    const int64_t y = (int64_t)yoe + era * 400;
    const uint32_t doy = doe - (365 * yoe + yoe / 4 - yoe / 100);      /* День у році [0, 365] */
    const uint32_t mp = (5 * doy + 2) / 153;                           /* [0, 11] */
    const uint32_t d = doy - (153 * mp + 2) / 5 + 1;                  /* [1, 31] */
    const uint32_t m = mp < 10 ? mp + 3 : mp - 9;                     /* [1, 12] */
    
    civil_date_t res;
    res.year = (int32_t)(y + (m <= 2 ? 1 : 0));
    res.month = m;
    res.day = d;
    return res;
}
