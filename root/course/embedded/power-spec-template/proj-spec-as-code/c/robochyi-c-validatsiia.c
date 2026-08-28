// Реально обрані деталі вузла (з даташитів конкретних компонентів).
typedef struct {
    uint16_t conv_vin_min_mv;   // нижній робочий вхід перетворювача
    uint16_t conv_vin_max_mv;   // верхній робочий вхід перетворювача
    uint16_t conv_iout_max_ma;  // макс. вихідний струм перетворювача
    uint16_t cout_ripple_mvpp;  // пульсація з ОБРАНИМ вих. конденсатором (за ESR)
    int16_t  derate_slope_ma_c; // скільки мА втрачаємо на кожен °C понад ta_derate
} power_parts_t;

static const power_parts_t parts_5v = {
    .conv_vin_min_mv = 6000,  .conv_vin_max_mv = 36000, // напр. buck 6..36 В
    .conv_iout_max_ma = 4000,                            // 4 А запас над 3 А піку
    .cout_ripple_mvpp = 35,                              // з обраним C + його ESR
    .derate_slope_ma_c = 50,   // -50 мА на кожен °C вище зламу
};

// Звірка деталей із ТЗ. Повертає кількість порушень (0 = усе покрито).
int validate_against_spec(const power_spec_t *s, const power_parts_t *p) {
    int viol = 0;

    // 1) Перетворювач мусить тримати ВЕСЬ діапазон входу ТЗ.
    if (p->conv_vin_min_mv > s->vin_min_mv) {
        printf("ПОРУШЕННЯ: перетворювач не бере низ входу %u<%u мВ\n",
               s->vin_min_mv, p->conv_vin_min_mv);
        viol++;
    }
    if (p->conv_vin_max_mv < s->vin_max_mv) {
        printf("ПОРУШЕННЯ: перетворювач не бере верх входу %u>%u мВ\n",
               s->vin_max_mv, p->conv_vin_max_mv);
        viol++;
    }
    // 2) Струм перетворювача мусить покривати пік ТЗ (із запасом — на рев'ю).
    if (p->conv_iout_max_ma < s->iout_peak_ma) {
        printf("ПОРУШЕННЯ: пік %u мА перевищує межу перетворювача %u мА\n",
               s->iout_peak_ma, p->conv_iout_max_ma);
        viol++;
    }
    // 3) Обраний вихідний конденсатор мусить тримати пульсацію в межах ТЗ.
    if (p->cout_ripple_mvpp > s->vout_ripple_mvpp) {
        printf("ПОРУШЕННЯ: пульсація з обраним C %u>%u мВ pp\n",
               p->cout_ripple_mvpp, s->vout_ripple_mvpp);
        viol++;
    }
    // 4) КЛЮЧОВЕ: дератинг при Ta_max не повинен з'їсти піковий струм.
    //    Доступний струм на верхній температурі = межа перетворювача
    //    мінус втрати дератингу за (ta_max - ta_derate) градусів.
    int dt = (int)s->ta_max_c - (int)s->ta_derate_c;
    if (dt > 0) {
        int avail = (int)p->conv_iout_max_ma - dt * (int)p->derate_slope_ma_c;
        if (avail < (int)s->iout_peak_ma) {
            printf("ПОРУШЕННЯ: при %d°C дератинг лишає %d мА < пік %u мА\n",
                   s->ta_max_c, avail, s->iout_peak_ma);
            viol++;
        }
    }
    return viol;
}
