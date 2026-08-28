# Конфіг — незмінний (frozen). Пороги під виріб на 5 В / до 3 А.
CFG_5V = PwrCfg(
    vbus_nominal_mv   = 5000,
    vbus_sag_mv       = 4400,   # нижче — просадка (кабель/блок)
    vbus_dead_mv      = 3000,   # нижче — живлення практично нема
    i_expect_ma       = 1500,   # скільки домовились тягти
    i_load_min_ma     = 100,    # менше — холостий хід, не класифікуємо
    brownout_trip_mv  = 4000,   # нижче — стишуємось
    brownout_clear_mv = 4300,   # вище — вертаємось (запас 300 мВ)
    adc_avg_log2      = 5,      # 2^5 = 32 відліки на вимір
    debounce_cycles   = 4,      # діагноз має вистояти 4 цикли поспіль
)

g_pwr = PwrDiagCtx(CFG_5V)

def power_init() -> None:
    global g_pwr
    g_pwr = PwrDiagCtx(CFG_5V)

# Стан «останнє показане» тримаємо між викликами (замість C-static).
_shown = None

# Викликається періодично — напр. раз на 100 мс із циклу нагляду.
def power_supervise_tick() -> None:
    global _shown
    g_pwr.step()

    # 1) Дія: стишити чи ні (гістерезис усередині).
    if g_pwr.pwr_low_power():
        reduce_load()      # прибрати некритичне: підсвітку, радіо, тактову
    else:
        restore_load()

    # 2) Слово: показати лише коли текст ЗМІНИВСЯ, щоб UI не смикався.
    msg = g_pwr.message()
    if msg != _shown:      # порівняння за значенням рядка
        ui_show_power_status(msg)
        _shown = msg

    # 3) Лог: діагноз + сирі цифри для підтримки.
    log_power(g_pwr.diag, g_pwr.vbus_mv, g_pwr.i_charge_ma)
