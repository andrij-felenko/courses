// Єдиний список полів ТЗ. Додав рядок сюди — поле з'явиться І в структурі,
// І в таблиці, І в перевірці повноти. Забути в одному з місць НЕ МОЖНА.
#define POWER_SPEC_FIELDS(X) \
    X(vin_min_mv,           "Вхід min",          "мВ") \
    X(vin_max_mv,           "Вхід max",          "мВ") \
    X(vin_absmax_mv,        "Вхід abs.max",      "мВ") \
    X(vin_droop_mv,         "Просідання входу",  "мВ") \
    X(vout_mv,              "Вихід номінал",     "мВ") \
    X(vout_tol_pct,         "Допуск виходу",     "%") \
    X(vout_ripple_mvpp,     "Пульсація",         "мВ pp") \
    X(vout_noise_mvrms,     "Шум",               "мВ rms") \
    X(iout_typ_ma,          "Струм середній",    "мА") \
    X(iout_peak_ma,         "Струм пік",         "мА") \
    X(iout_transient_ma,    "Стрибок",           "мА") \
    X(transient_slew_ma_us, "Швидкість стрибка", "мА/мкс") \
    X(ta_min_c,             "Темп. min",         "°C") \
    X(ta_max_c,             "Темп. max",         "°C") \
    X(ta_derate_c,          "Злам дератингу",    "°C") \
    X(life_hours_kh,        "Термін служби",     "тис.год")
