// Пресети драйвера D+/D− (bq25890H, REG01: DP_DAC[7:5], DM_DAC[4:2]).
enum dac { DAC_HIZ = 0, DAC_0V0 = 1, DAC_0V6 = 2, DAC_1V2 = 3,
           DAC_2V0 = 4, DAC_2V7 = 5, DAC_3V3 = 6 };

#define REG01 0x01

static void dp_dm_set(enum dac dp, enum dac dm) {
    uint8_t v = (uint8_t)((dp << 5) | (dm << 2));
    i2c_write_reg(CHG_ADDR, REG01, v);
}

// Вхід у безперервний режим: D+ = 0.6 В, D− = 3.3 В (рядок таблиці кодів).
static void qc3_enter_continuous(void) {
    dp_dm_set(DAC_0V6, DAC_3V3);
    delay_ms(100);              // фільтр зміни режиму 20–60 мс + запас
}

// Крок +200 мВ: короткий імпульс на D+ (0.6 → 3.3 → 0.6).
// Утримати треба довше за фільтр кроку, але НАБАГАТО коротше за фільтр режиму,
// інакше 3.3/3.3 прочитають як код 20 В.
static void qc3_step_up(void) {
    dp_dm_set(DAC_3V3, DAC_3V3);
    delay_us(300);              // фільтр кроку 100–200 мкс → беремо з запасом
    dp_dm_set(DAC_0V6, DAC_3V3);
    delay_ms(3);                // напруга встигає стати (≈2 мс)
}

// Абсолютного значення протокол не передає — лік ведемо самі.
static int vbus_mv = 5000;

void qc3_goto_peak(void) {
    qc3_enter_continuous();
    while (vbus_mv < 6400) {    // (6400 − 5000) / 200 = 7 кроків
        qc3_step_up();
        vbus_mv += 200;
    }
}
