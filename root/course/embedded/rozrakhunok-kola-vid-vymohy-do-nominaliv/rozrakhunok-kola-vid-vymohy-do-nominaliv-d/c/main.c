#include <stdio.h>
#include <stdint.h>

#include "calib_store.h"
#include "divider.h"

/* Паспортні дані з розрахунку: дільник 100к/200к під вхід АЦП, Vref = 3.3 В. */
static const divider_spec_t SPEC = {
    .r1_ohms      = 100000u,
    .r2_ohms      = 200000u,
    .vref_mv      = 3300u,
    .adc_max_code = 4095u
};

/* Модель конкретної плати на столі: резистори з допуску 1% розбіглися в різні
   боки, а вбудований стабілізатор дає не рівно 3.300 В. Саме ці відхилення
   заводське калібрування й вилучає. У прошивці цієї структури немає. */
typedef struct {
    double r1_ohms;
    double r2_ohms;
    double vref_mv;
} board_t;

static uint16_t board_sample(const board_t *b, double vin_mv, uint16_t adc_max)
{
    double v_pin = vin_mv * b->r2_ohms / (b->r1_ohms + b->r2_ohms);
    double code  = v_pin * (double)adc_max / b->vref_mv;

    if (code < 0.0) {
        code = 0.0;
    }
    if (code > (double)adc_max) {
        code = (double)adc_max;   /* вхід АЦП насичується, а не рахує далі */
    }
    return (uint16_t)(code + 0.5);
}

/* Емуляція сторінки EEPROM: у прошивці на її місці буде читання i2c-мікросхеми
   або сектора Flash, решта коду від цього не міняється. */
static uint8_t eeprom_page[CALIB_BLOB_SIZE];

static void print_row(const divider_cal_t *raw_cal, const divider_cal_t *cal,
                      const board_t *board, double vin_true_mv)
{
    uint16_t code = board_sample(board, vin_true_mv, SPEC.adc_max_code);
    int32_t  mv_raw = 0;
    int32_t  mv_cal = 0;
    div_status_t st;

    st = divider_raw_to_mv(&SPEC, raw_cal, code, &mv_raw);
    if (st != DIV_OK) {
        printf("  %6.0f | %5u | %s\n", vin_true_mv, code, divider_status_str(st));
        return;
    }
    st = divider_raw_to_mv(&SPEC, cal, code, &mv_cal);
    if (st != DIV_OK) {
        printf("  %6.0f | %5u | %s\n", vin_true_mv, code, divider_status_str(st));
        return;
    }

    printf("  %6.0f | %5u | %7d | %+6d | %7d | %+6d\n",
           vin_true_mv, code,
           mv_raw, mv_raw - (int32_t)vin_true_mv,
           mv_cal, mv_cal - (int32_t)vin_true_mv);
}

int main(void)
{
    const board_t board = { 98700.0, 201500.0, 3287.0 };
    const double  ref_lo_mv = 1000.0;
    const double  ref_hi_mv = 4000.0;
    const double  battery_points[] = { 3000.0, 3300.0, 3600.0, 3900.0, 4200.0 };

    divider_cal_t cal;
    divider_cal_t loaded;
    calib_status_t cst;
    div_status_t   dst;
    uint16_t raw_lo, raw_hi;
    int32_t  mv;
    size_t   i;

    dst = divider_check_spec(&SPEC);
    if (dst != DIV_OK) {
        fprintf(stderr, "паспорт каналу хибний: %s\n", divider_status_str(dst));
        return 1;
    }

    /* --- Заводський стенд: дві еталонні напруги з калібратора --- */
    raw_lo = board_sample(&board, ref_lo_mv, SPEC.adc_max_code);
    raw_hi = board_sample(&board, ref_hi_mv, SPEC.adc_max_code);
    printf("Еталонні точки: %.0f мВ -> код %u, %.0f мВ -> код %u\n",
           ref_lo_mv, raw_lo, ref_hi_mv, raw_hi);

    dst = divider_fit_two_point(&SPEC, raw_lo, (int32_t)ref_lo_mv,
                                raw_hi, (int32_t)ref_hi_mv, &cal);
    if (dst != DIV_OK) {
        fprintf(stderr, "калібрування не вдалося: %s\n", divider_status_str(dst));
        return 1;   /* плата не проходить заводський тест — далі по конвеєру не йде */
    }
    printf("Поправка: нахил %u ppm (%+.3f%%), зсув %+d мВ\n\n",
           cal.gain_ppm,
           ((double)cal.gain_ppm - 1000000.0) / 10000.0,
           cal.offset_mv);

    /* --- Запис у EEPROM і читання назад при завантаженні прошивки --- */
    cst = calib_pack(&cal, eeprom_page, sizeof eeprom_page);
    if (cst != CALIB_OK) {
        fprintf(stderr, "запис калібрування: %s\n", calib_status_str(cst));
        return 1;
    }
    cst = calib_unpack(eeprom_page, sizeof eeprom_page, &loaded);
    printf("Читання з EEPROM: %s (нахил %u ppm, зсув %+d мВ)\n",
           calib_status_str(cst), loaded.gain_ppm, loaded.offset_mv);
    if (cst != CALIB_OK) {
        loaded = DIV_CAL_IDENTITY;
    }

    /* --- Що буде, якщо сторінка побилася --- */
    {
        uint8_t damaged[CALIB_BLOB_SIZE];
        divider_cal_t fallback;

        for (i = 0; i < CALIB_BLOB_SIZE; ++i) {
            damaged[i] = eeprom_page[i];
        }
        damaged[9] ^= 0x08u;   /* один перекинутий біт у полі нахилу */

        cst = calib_unpack(damaged, sizeof damaged, &fallback);
        printf("Побитий запис: %s -> працюємо на паспортних номіналах\n\n",
               calib_status_str(cst));
        if (cst != CALIB_OK) {
            fallback = DIV_CAL_IDENTITY;
        }
        (void)fallback;
    }

    /* --- Робота в полі --- */
    printf("  Vбат | код | без кал. | похиб. | з кал. | похиб.\n");
    printf("  -----+-------+---------+--------+---------+-------\n");
    for (i = 0; i < sizeof battery_points / sizeof battery_points[0]; ++i) {
        print_row(&DIV_CAL_IDENTITY, &loaded, &board, battery_points[i]);
    }

    /* --- Незручний випадок: драйвер АЦП віддав код поза роздільністю --- */
    dst = divider_raw_to_mv(&SPEC, &loaded, 5000u, &mv);
    printf("\nКод 5000 при 12 бітах: %s\n", divider_status_str(dst));

    return 0;
}
