/* Файл: analytics/report_builder.c */
/* Розробник скопіював значення вручну три місяці тому */
static const char* status_to_str(int st) {
    switch (st) {
        case 1: return "AUTH";
        case 2: return "CAPTURED";
        case 3: return "REFUNDED";
        default: return "UNKNOWN"; /* Новий статус 4 потрапить сюди і зламає звіт */
    }
}
