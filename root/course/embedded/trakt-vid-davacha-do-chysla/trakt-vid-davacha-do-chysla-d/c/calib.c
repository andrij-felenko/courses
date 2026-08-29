#include "calib.h"

#include "filters.h" /* div_round */

#include <stdlib.h>

bool calib_init(calib_t *cal,
                int32_t raw_p1, int32_t phys_p1_grams,
                int32_t raw_p2, int32_t phys_p2_grams)
{
    int32_t raw_span = raw_p2 - raw_p1;
    if (labs((long)raw_span) < CALIB_MIN_SPAN) {
        return false;
    }
    if (phys_p1_grams == phys_p2_grams) {
        return false; /* дві точки з однаковою вагою нахилу не задають */
    }

    cal->raw_p1 = raw_p1;
    cal->raw_p2 = raw_p2;
    cal->phys_p1 = phys_p1_grams;
    cal->phys_p2 = phys_p2_grams;
    return true;
}

int32_t calib_to_grams(const calib_t *cal, int32_t raw)
{
    /* Проміжок рахуємо в int64: код і вага окремо влазять у 32 біти,
       а їхній добуток — уже ні (2000 кодів * 10000 грамів = 2e7 це ще нічого,
       але на 24-бітному АЦП той самий вираз дає 1e11). */
    int64_t numerator = (int64_t)(raw - cal->raw_p1) * (cal->phys_p2 - cal->phys_p1);
    int64_t denominator = (int64_t)cal->raw_p2 - cal->raw_p1;

    return cal->phys_p1 + div_round(numerator, denominator);
}

double calib_counts_per_kg(const calib_t *cal)
{
    double raw_span = (double)cal->raw_p2 - (double)cal->raw_p1;
    double kg_span = ((double)cal->phys_p2 - (double)cal->phys_p1) / 1000.0;
    return raw_span / kg_span;
}
