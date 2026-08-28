// Конфіг — у const (лягає в ПЗП). Пороги під виріб на 5 В / до 3 А.
static const pwr_cfg_t CFG_5V = {
    .vbus_nominal_mv   = 5000,
    .vbus_sag_mv       = 4400,   // нижче — просадка (кабель/блок)
    .vbus_dead_mv      = 3000,   // нижче — живлення практично нема
    .i_expect_ma       = 1500,   // скільки домовились тягти
    .i_load_min_ma     = 100,    // менше — холостий хід, не класифікуємо
    .brownout_trip_mv  = 4000,   // нижче — стишуємось
    .brownout_clear_mv = 4300,   // вище — вертаємось (запас 300 мВ)
    .adc_avg_log2      = 5,      // 2^5 = 32 відліки на вимір
    .debounce_cycles   = 4,      // діагноз має вистояти 4 цикли поспіль
};

static pwr_diag_ctx_t g_pwr;

void power_init(void) {
    pwr_diag_init(&g_pwr, &CFG_5V);
}

// Викликається періодично — напр. раз на 100 мс із циклу нагляду.
void power_supervise_tick(void) {
    pwr_diag_step(&g_pwr);

    // 1) Дія: стишити чи ні (гістерезис усередині).
    if (pwr_low_power(&g_pwr))
        reduce_load();     // прибрати некритичне: підсвітку, радіо, тактову
    else
        restore_load();

    // 2) Слово: показати лише коли текст ЗМІНИВСЯ, щоб UI не смикався.
    static const char *shown = 0;
    const char *msg = pwr_diag_message(&g_pwr);
    if (msg != shown) {    // порівняння вказівників: рядки статичні
        ui_show_power_status(msg);
        shown = msg;
    }

    // 3) Лог: діагноз + сирі цифри для підтримки.
    log_power(g_pwr.diag, g_pwr.vbus_mv, g_pwr.i_charge_ma);
}
