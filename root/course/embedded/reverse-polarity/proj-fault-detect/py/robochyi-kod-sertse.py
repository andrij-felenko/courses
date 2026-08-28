# Класифікатор БЕЗ пам'яті: за однією напругою шини — який це почерк.
# Гістерезис і підтвердження застосовує ВИЩЕ, машина станів.
def _classify(c: PmConfig, bus_mv: int, cur: PmClass) -> PmClass:
    # 1. Мертва шина: майже нуль. Найгрубіший і найдешевший діагноз.
    if bus_mv < c.v_dead_mv:
        return PmClass.DEAD

    # 2. Почерк body-діода: шина тримається біля «номінал − діод-падіння».
    #    Це вужче вікно, і воно має перевагу над «просто просадом»,
    #    бо каже про КОНКРЕТНУ несправність захисту, а не про слабке живлення.
    bd_center = c.v_nominal_mv - c.diode_drop_mv if c.v_nominal_mv > c.diode_drop_mv else 0
    if bd_center - c.diode_tol_mv < bus_mv < bd_center + c.diode_tol_mv:
        return PmClass.BODYDIODE

    # 3. Просад — з гістерезисом: пороги спрацювання й відпускання різні.
    #    Якщо ЗАРАЗ уже просад — тримаємось у ньому, поки не піднялись вище heal.
    if cur == PmClass.SAG:
        return PmClass.OK if bus_mv >= c.v_sag_heal_mv else PmClass.SAG
    # Якщо ЗАРАЗ норма — оголошуємо просад лише впавши нижче trip (нижчий поріг).
    return PmClass.SAG if bus_mv < c.v_sag_trip_mv else PmClass.OK
