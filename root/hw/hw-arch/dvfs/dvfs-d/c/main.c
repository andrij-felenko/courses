typedef struct {
    uint16_t mv;    // напруга ядра, мВ
    uint32_t hz;    // частота ядра, Гц
} opp_t;            // operating performance point — робоча точка

static const opp_t OPP_LOW  = {  900,  80000000u };
static const opp_t OPP_HIGH = { 1200, 240000000u };

// підняти напругу і ДОЧЕКАТИСЯ, поки регулятор її виведе
static void set_core_voltage(uint16_t mv) {
    pmic_set_core_mv(mv);          // задати нову напругу регулятору
    while (!pmic_voltage_settled(mv))  // опитувати, поки не встановиться
        ;                          // ~десятки-сотні мкс
}

void opp_switch(const opp_t *from, const opp_t *to) {
    if (to->hz > from->hz) {
        // РОЗГІН: спершу напруга (вища), потім частота
        set_core_voltage(to->mv);
        clock_set_cpu_hz(to->hz);
    } else {
        // ГАЛЬМУВАННЯ: спершу частота (нижча), потім напруга
        clock_set_cpu_hz(to->hz);
        set_core_voltage(to->mv);
    }
}
