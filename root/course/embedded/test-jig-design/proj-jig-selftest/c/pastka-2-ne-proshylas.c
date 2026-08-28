typedef enum {
    OUTCOME_PASS,          // рапорт прийшов, усе в допуску
    OUTCOME_HW_DEFECT,     // рапорт прийшов, та якесь поле погане → лагодити/брак
    OUTCOME_NOT_FLASHED,   // рапорту нема взагалі → перепрошити й повторити
    OUTCOME_GARBLED        // щось прийшло, але не наш рапорт → шум або чужа прошивка
} outcome_t;

outcome_t jig_classify(void) {
    char line[LINE_MAX];

    if (!jig_read_line(line, sizeof(line), REPORT_TIMEOUT_MS)) {
        return OUTCOME_NOT_FLASHED;   // ТИША → найпевніш не прошилась
    }
    // щось прийшло. Це взагалі наш рапорт?
    if (line[0] != '$' || !strstr(line, "$RPT;")) {
        return OUTCOME_GARBLED;       // прийшло, але не те — шум чи чужий образ
    }
    verdict_t v = jig_judge(line);
    return v.passed ? OUTCOME_PASS : OUTCOME_HW_DEFECT;
}
