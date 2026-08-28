// Друк ТЗ як таблиці. Розгортається з того САМОГО списку POWER_SPEC_FIELDS,
// тож жодне поле структури не може випасти з документа й навпаки.
void print_spec_table(const power_spec_t *s) {
    printf("ТЗ на вузол живлення (єдине джерело — код)\n");
    printf("%-18s %10s %6s\n", "Параметр", "Значення", "Од.");
    printf("-------------------------------------------\n");
    #define X(field, label, unit) \
        printf("%-18s %10u %6s\n", label, (unsigned)s->field, unit);
    POWER_SPEC_FIELDS(X)
    #undef X
}
