#ifndef DIVIDER_H
#define DIVIDER_H

#include <stddef.h>
#include <stdint.h>

/* Канал вимірювання напруги акумулятора: резистивний дільник R1/R2 на вході АЦП.
   Уся арифметика цілочислова — мікроконтролер без FPU не має чим множити double. */

/* Стан операції. Жодна функція не повертає «просто число»: калібрувальні
   коефіцієнти приходять з EEPROM, а туди могло записатися що завгодно. */
typedef enum {
    DIV_OK = 0,
    DIV_ERR_SPEC,        /* нульові номінали, Vref або роздільність АЦП */
    DIV_ERR_RAW_RANGE,   /* код більший за роздільність АЦП */
    DIV_ERR_CAL_GAIN,    /* нахил поза розумною смугою — плата зібрана не так */
    DIV_ERR_CAL_POINTS   /* еталонні точки збіглися або йдуть у зворотному порядку */
} div_status_t;

/* Паспортні дані вузла — те, що інженер порахував і поклав у специфікацію. */
typedef struct {
    uint32_t r1_ohms;       /* верхнє плече, наприклад 100000 */
    uint32_t r2_ohms;       /* нижнє плече, наприклад 200000 */
    uint16_t vref_mv;       /* опорна напруга АЦП у мВ, наприклад 3300 */
    uint16_t adc_max_code;  /* 4095 для 12 біт, 65535 для 16 біт */
} divider_spec_t;

/* Заводська поправка: mv = nominal * gain_ppm / 1e6 + offset_mv.
   Спершу нахил, потім зсув — рівно в тому порядку, у якому їх обчислює
   divider_fit_two_point(); інший порядок дав би інші коефіцієнти. */
typedef struct {
    uint32_t gain_ppm;   /* 1000000 == 1.000000 */
    int32_t  offset_mv;
} divider_cal_t;

#define DIV_GAIN_UNITY  1000000u
/* Смуга здорового глузду для нахилу. Допуск резисторів 1%, дрейф і старіння
   дають одиниці відсотків; нахил 0.8 чи 1.25 означає не похибку, а те, що
   на плату впаяли не той номінал або еталон подали не на той вивід. */
#define DIV_GAIN_MIN     800000u
#define DIV_GAIN_MAX    1250000u

/* Розведення еталонних точок: різницю напруг ставимо в знаменник нахилу,
   тож на близьких точках шум еталона множиться на порядки. */
#define DIV_CAL_MIN_SPAN_MV 500

/* Поправка «нічого не робити» — з нею вузол працює на самих паспортних номіналах. */
extern const divider_cal_t DIV_CAL_IDENTITY;

div_status_t divider_check_spec(const divider_spec_t *spec);
div_status_t divider_check_cal(const divider_cal_t *cal);

/* Код АЦП -> напруга на вході дільника (тобто на акумуляторі), у мВ. */
div_status_t divider_raw_to_mv(const divider_spec_t *spec, const divider_cal_t *cal,
                               uint16_t raw, int32_t *out_mv);

/* Заводське калібрування за двома еталонними точками: подали точну напругу,
   зчитали сирий код — і так двічі, на різних кінцях робочого діапазону. */
div_status_t divider_fit_two_point(const divider_spec_t *spec,
                                   uint16_t raw_lo, int32_t ref_lo_mv,
                                   uint16_t raw_hi, int32_t ref_hi_mv,
                                   divider_cal_t *out_cal);

const char *divider_status_str(div_status_t st);

#endif /* DIVIDER_H */
