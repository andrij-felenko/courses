// Класифікатор БЕЗ пам'яті: за однією напругою шини — який це почерк.
// Гістерезис і підтвердження застосовує ВИЩЕ, машина станів.
static pm_class_t classify(const pm_config_t *c, uint16_t bus_mv, pm_class_t cur) {
    // 1. Мертва шина: майже нуль. Найгрубіший і найдешевший діагноз.
    if (bus_mv < c->v_dead_mv) return PM_DEAD;

    // 2. Почерк body-діода: шина тримається біля «номінал − діод-падіння».
    //    Це вужче вікно, і воно має перевагу над «просто просадом»,
    //    бо каже про КОНКРЕТНУ несправність захисту, а не про слабке живлення.
    uint16_t bd_center = (c->v_nominal_mv > c->diode_drop_mv)
                       ? (c->v_nominal_mv - c->diode_drop_mv) : 0u;
    if (bus_mv > bd_center - c->diode_tol_mv &&
        bus_mv < bd_center + c->diode_tol_mv) return PM_BODYDIODE;

    // 3. Просад — з гістерезисом: пороги спрацювання й відпускання різні.
    //    Якщо ЗАРАЗ уже просад — тримаємось у ньому, поки не піднялись вище heal.
    if (cur == PM_SAG) {
        return (bus_mv >= c->v_sag_heal_mv) ? PM_OK : PM_SAG;
    }
    // Якщо ЗАРАЗ норма — оголошуємо просад лише впавши нижче trip (нижчий поріг).
    return (bus_mv < c->v_sag_trip_mv) ? PM_SAG : PM_OK;
}
