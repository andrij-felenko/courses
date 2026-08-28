#include <stdio.h>

// Дописати один рядок вироку в журнал (CSV). Ключ — серійний номер плати.
void jig_log(const char *serial, const verdict_t *v) {
    FILE *f = fopen("jig_log.csv", "a");   // на контролері — це файл на SD чи в flash
    if (!f) return;                        // журнал не критичний для самого вироку
    fprintf(f, "%s,%s,%s,%lu\r\n",
            serial,
            v->passed ? "PASS" : "FAIL",
            v->passed ? "-" : v->reason,
            (unsigned long)jig_epoch_seconds());
    fclose(f);
}
