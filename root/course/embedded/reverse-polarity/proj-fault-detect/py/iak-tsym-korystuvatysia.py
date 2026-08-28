# Пороги під 5-вольтову шину (усе в мВ). Один конфіг = одна плата.
CFG_5V = PmConfig(
    div_num=3, div_den=1,          # дільник 3:1 → 5 В на нозі стає ~1.67 В
    vref_mv=3300, adc_full=4095,

    v_nominal_mv=5000,             # очікуємо 5.0 В
    v_dead_mv=500,                 # < 0.5 В — мертва шина
    v_sag_trip_mv=4500,            # < 4.5 В — оголосити просад
    v_sag_heal_mv=4750,            # > 4.75 В — просад знято (зазор 250 мВ)
    diode_drop_mv=600,             # body-діод ~0.6 В
    diode_tol_mv=200,              # вікно ±0.2 В навколо 5.0−0.6 = 4.4 В

    confirm_dead=3,                # мертву/body-діод — за 3 відліки
    confirm_sag=10,                # просад терпимо довше (кидки струму — норма)
    confirm_ok=30,                 # назад у норму — за 30 добрих поспіль
)

vin_mon = pm_init(CFG_5V)

# Платформний шматок: прочитати канал АЦП шини (сирий код).
# Вибірку тримаємо ПОВІЛЬНОЮ: дільник високоомний, швидкий відлік занизить.
def read_vin_adc() -> int:
    return adc_read_raw_slow(ADC_CH_VIN)     # довгий SamplingTime

# Реакції плати.
def save_critical() -> None:      fram_store_context()      # швидкий запис
def switch_load(on: bool) -> None: gpio_write(LOAD_EN, on)  # ключ навантаження
def report_class(c: PmClass) -> None:
    if c == PmClass.OK:
        led_set(LED_GREEN);   log_line("power OK")
    elif c == PmClass.SAG:
        led_blink(LED_AMBER); log_line("power SAG")
    elif c == PmClass.DEAD:
        led_set(LED_RED);     log_line("power DEAD (fuse?)")
    elif c == PmClass.BODYDIODE:
        led_blink(LED_RED);   log_line("REVERSE? FET body-diode")

ACT = PmActions(
    save_state=save_critical,
    set_load=switch_load,
    on_class=report_class,
)

def power_mon_loop() -> None:
    pm_poll(vin_mon, read_vin_adc, ACT)      # раз на 1–5 мс (таймер/головний цикл)
    # ... решта роботи пристрою ...
