// ── Перевірки ВХОДУ ────────────────────────────────────────────────────
_Static_assert(logic_5v.vin_min_mv < logic_5v.vin_max_mv,
    "вхід: min мусить бути нижчим за max");
_Static_assert(logic_5v.vin_max_mv < logic_5v.vin_absmax_mv,
    "робочий max мусить лишати запас до absolute maximum");
// запас до absmax — не косметичний: комутаційні викиди легко докидають
// десятки %. Вимагаємо хоча б +25 % від робочого max до absmax.
_Static_assert(logic_5v.vin_absmax_mv >= (uint32_t)logic_5v.vin_max_mv * 5 / 4,
    "absolute maximum мусить лишати >=25% над робочим max (викиди!)");
_Static_assert(logic_5v.vin_droop_mv < logic_5v.vin_min_mv,
    "просідання не може бути більшим за саму мінімальну напругу входу");

// ── Перевірки ВИХОДУ ───────────────────────────────────────────────────
// Найтонший assert усього файлу: ВІКНО ДОПУСКУ мусить вміщати ПУЛЬСАЦІЮ.
// Якщо розмах ripple ширший за допуск, вихід вилітає з вікна сам собою,
// ще до будь-якого навантаження. Половина допуску (бо ripple — це ±) у мВ:
_Static_assert(logic_5v.vout_ripple_mvpp <=
                   (uint32_t)logic_5v.vout_mv * logic_5v.vout_tol_pct / 100u,
    "пульсація (розмах) не вміщається у вікно допуску — ТЗ суперечливе");
_Static_assert(logic_5v.vout_tol_pct > 0 && logic_5v.vout_tol_pct <= 10,
    "допуск виходу: 0 < tol <= 10% (інакше це не ТЗ, а побажання)");
_Static_assert(logic_5v.vout_mv > 0, "номінал виходу не може бути нулем");

// ── Перевірки НАВАНТАЖЕННЯ ─────────────────────────────────────────────
_Static_assert(logic_5v.iout_peak_ma >= logic_5v.iout_typ_ma,
    "пік не може бути меншим за середній струм");
_Static_assert(logic_5v.iout_transient_ma <= logic_5v.iout_peak_ma,
    "стрибок не може перевищувати заявлений пік");
_Static_assert(logic_5v.iout_transient_ma > 0,
    "стрибок=0 означає забуте поле: реальне навантаження завжди смикає");
_Static_assert(logic_5v.transient_slew_ma_us > 0,
    "швидкість стрибка=0 — забуте поле; вкажи мА/мкс");

// ── Перевірки СЕРЕДОВИЩА ───────────────────────────────────────────────
_Static_assert(logic_5v.ta_min_c < logic_5v.ta_max_c,
    "температура: min мусить бути нижчою за max");
// злам дератингу мусить лежати ВСЕРЕДИНІ робочого діапазону. Якщо він
// вище за ta_max, дератинг ніколи не настає (число-привид); якщо нижче
// за ta_min — вузол ВЖЕ в дератингу на найхолоднішому, що абсурд.
_Static_assert(logic_5v.ta_derate_c >  logic_5v.ta_min_c &&
               logic_5v.ta_derate_c <= logic_5v.ta_max_c,
    "температура зламу дератингу мусить бути всередині [ta_min..ta_max]");
_Static_assert(logic_5v.life_hours_kh > 0,
    "термін служби=0 — забуте поле; конденсатори сохнуть, це треба знати");
