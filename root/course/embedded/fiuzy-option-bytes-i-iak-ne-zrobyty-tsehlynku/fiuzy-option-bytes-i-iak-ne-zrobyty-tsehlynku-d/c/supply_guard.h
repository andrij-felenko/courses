#ifndef SUPPLY_GUARD_H
#define SUPPLY_GUARD_H

/*
 * Перевірка напруги живлення перед записом службової Flash. Використовуємо
 * штатний детектор PVD: він порівнює VDD із внутрішнім опорним джерелом і
 * дає готову відповідь «вище / нижче», не потребуючи ані АЦП, ані калібрування.
 */

typedef enum {
    SUPPLY_PVD_2V0 = 0,
    SUPPLY_PVD_2V2 = 1,
    SUPPLY_PVD_2V4 = 2,
    SUPPLY_PVD_2V5 = 3,
    SUPPLY_PVD_2V6 = 4,
    SUPPLY_PVD_2V8 = 5,
    SUPPLY_PVD_2V9 = 6
} supply_threshold_t;

void supply_guard_enable(supply_threshold_t level);
void supply_guard_disable(void);

/* 1 — VDD не нижча за обраний поріг. */
int supply_guard_above_threshold(void);

#endif /* SUPPLY_GUARD_H */
