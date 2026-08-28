/* Вибір рівня потужності PA телеметрійного тракту.
   Значення в регістр PA — умовні кроки підсилення (0..MAX_STEP);
   реальне відображення «крок → дБм» бере калібрувальна таблиця чипа.
   spi_write_reg / current_temp_c — платформні обгортки. */
#include <stdint.h>

#define REG_PA_LEVEL   0x1D
#define PA_STEP_MAX     20      /* верхня межа кроків підсилення PA        */
#define PA_LIMIT_LEGAL  17      /* стеля, дозволена регуляторами діапазону */
#define PA_TEMP_TRIP    85      /* °C: понад це — тепловий захист          */

/* Перевести бажану потужність (dBm) у крок регістра з урахуванням
   калібрування, законної стелі й теплового захисту. */
static uint8_t pa_step_for_dbm(int want_dbm) {
    /* груба лінійна калібровка «dBm → крок»; у житті — таблиця з даташита */
    int step = (want_dbm - (-1)) / 2;      /* напр. -1 dBm → 0, +19 → 10   */
    if (step < 0)            step = 0;
    if (step > PA_STEP_MAX)  step = PA_STEP_MAX;   /* вище фізичної межі не піднімеш */
    if (step > PA_LIMIT_LEGAL) step = PA_LIMIT_LEGAL; /* не порушуй норму діапазону */
    return (uint8_t)step;
}

int pa_set_power(int want_dbm) {
    if (current_temp_c() >= PA_TEMP_TRIP)
        want_dbm = -1;                     /* перегрів → притисни до мінімуму */

    uint8_t step = pa_step_for_dbm(want_dbm);
    spi_write_reg(REG_PA_LEVEL, step);
    return step;                           /* фактично встановлений крок      */
}
