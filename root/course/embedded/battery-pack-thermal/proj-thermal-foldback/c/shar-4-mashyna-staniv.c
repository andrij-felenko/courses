// ── Пороги (десяті °C). Кожен має пару: спрацювання / відпускання (гістерезис). ──
#define T_COLD_ENTER     0      //  0.0 °C: нижче — заряд заборонено (вхід у COLD)
#define T_COLD_EXIT     20      //  2.0 °C: вийти з COLD лише коли потеплішало (гіст.)
#define T_FOLD_ENTER   350      // 35.0 °C: вище — починаємо зрізати струм
#define T_FOLD_EXIT    330      // 33.0 °C: повертаємось до повного струму (гіст.)
#define T_STOP_ENTER   450      // 45.0 °C: вище — повна заборона
#define T_STOP_EXIT    420      // 42.0 °C: відновлюємо зрізаний заряд (гіст.)

#define I_CHARGE_MAX  4000      // повний струм заряду, мА

typedef enum { ST_COLD_WAIT, ST_CHARGE, ST_FOLDBACK, ST_STOP, ST_FAULT } therm_state_t;

// Контекст регулятора живе між викликами (пам'ять машини станів).
typedef struct {
    therm_state_t state;
    int32_t       charge_ma;   // поточний дозволений струм заряду
    bool          heater_on;   // чи увімкнено нагрівач (якщо він є)
} regulator_t;

#define HAS_HEATER  1          // 0, якщо нагрівача в пакеті немає

// Лінійне зрізання у вікні FOLD..STOP (та сама ідея, що charge_limit_ma у темі).
static int32_t foldback_ma(int16_t t_c10) {
    if (t_c10 <= T_FOLD_ENTER) return I_CHARGE_MAX;
    if (t_c10 >= T_STOP_ENTER) return 0;
    int32_t span  = T_STOP_ENTER - T_FOLD_ENTER;   // 100 десятих = 10 °C
    int32_t above = t_c10 - T_FOLD_ENTER;
    return (int32_t)I_CHARGE_MAX * (span - above) / span;
}

// Один крок машини: викликати періодично (напр. раз на 100 мс) зі свіжими кодами АЦП.
void regulator_step(regulator_t *reg, const uint16_t *adc_codes) {
    pack_temp_t pt = pack_temperature(adc_codes);

    // ── Найвищий пріоритет: жоден давач не живий → сліпі → FAULT. ──
    if (pt.n_valid == 0) {
        reg->state     = ST_FAULT;
        reg->charge_ma = 0;
        reg->heater_on = false;          // наосліп не гріємо й не заряджаємо
        return;
    }

    int16_t t = pt.t_max_c10;            // керуємо за найгарячішою живою коміркою

    switch (reg->state) {

    case ST_FAULT:
        // давачі повернулись — перезаходимо в логіку через безпечний STOP
        reg->state = ST_STOP;
        reg->charge_ma = 0;
        break;

    case ST_COLD_WAIT:
        reg->charge_ma = 0;                          // на морозі заряд заборонено
        reg->heater_on = HAS_HEATER ? true : false;  // гріємо, якщо вміємо
        if (t >= T_COLD_EXIT) {                       // потеплішало понад гіст-поріг
            reg->state     = ST_CHARGE;
            reg->heater_on = false;
        }
        break;

    case ST_CHARGE:
        reg->charge_ma = I_CHARGE_MAX;
        if (t < T_COLD_ENTER)       reg->state = ST_COLD_WAIT;   // похолодало
        else if (t >= T_FOLD_ENTER) reg->state = ST_FOLDBACK;    // нагрілося
        break;

    case ST_FOLDBACK:
        reg->charge_ma = foldback_ma(t);
        if (t >= T_STOP_ENTER)      reg->state = ST_STOP;        // перегрів
        else if (t < T_FOLD_EXIT)   reg->state = ST_CHARGE;      // охолов (гіст.)
        break;

    case ST_STOP:
        reg->charge_ma = 0;
        if (t < T_COLD_ENTER)       reg->state = ST_COLD_WAIT;   // впав у мороз
        else if (t < T_STOP_EXIT)   reg->state = ST_FOLDBACK;    // охолов (гіст.)
        break;
    }
}
