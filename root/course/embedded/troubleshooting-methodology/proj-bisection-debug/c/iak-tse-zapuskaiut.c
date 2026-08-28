// Діагностична точка входу: запустити бісекцію й показати результат.
void run_bisection_diagnostic(void) {
    JOURNAL_NOTE("--- діагностика: локалізація несправності бісекцією ---");

    int culprit = bisect_debug(SUS_COUNT, predicate_symptom_flag);

    if (culprit < 0) {
        report("бісекція: винуватця в списку не знайдено (розшир список або приборкай баг)");
    } else {
        report_fmt("бісекція: винуватець — вузол #%d (%s)", culprit, SUS_NAME[culprit]);
    }
    suspects_set_mask(0);                 // прибрати за собою: вимкнути всіх
}
