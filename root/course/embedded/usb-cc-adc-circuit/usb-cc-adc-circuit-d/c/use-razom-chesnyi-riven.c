// Періодичний крок: виміряти CC, відфільтрувати, продебаунсити, виставити бюджет.
void cc_task(void) {
    int mv = cc_read_mv_avg(PIN_CC_ACTIVE);   // RC на нозі + усереднення N відліків
    cc_level_t lvl = cc_update(mv);           // гістерезис + дебаунс → сталий рівень

    static cc_level_t applied = CC_NONE;
    if (lvl == applied) return;               // нічого не змінилось — виходимо
    applied = lvl;

    switch (lvl) {
        case CC_NONE:    set_input_current_limit(0);    break;  // джерела нема
        case CC_DEFAULT: set_input_current_limit(500);  break;  // звичайний USB
        case CC_1A5:     set_input_current_limit(1500); break;  // 1.5 А
        case CC_3A0:     set_input_current_limit(3000); break;  // повні 3 А, 15 Вт
    }
}
