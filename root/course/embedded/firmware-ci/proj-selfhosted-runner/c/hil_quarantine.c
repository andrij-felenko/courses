// hil_quarantine.c — простий карантин стенда файлом-прапорцем.
// Ідея: мертвий стенд (код 2) виводимо з обігу, поки людина не зніме карантин
// вручну (видаливши файл). Так один битий чіп не червонить КОЖЕН коміт.

#include <stdio.h>
#include <unistd.h>

#define QFILE "/var/lib/hil/quarantine.flag"

// Перед прогоном: якщо стенд на карантині — не чіпати плату взагалі.
int hil_check_quarantine(void) {
    if (access(QFILE, F_OK) == 0) {
        fprintf(stderr,
            "HIL: стенд НА КАРАНТИНІ (%s). Прогін пропущено.\n"
            "     Огляньте плату; знявши проблему, видаліть файл вручну.\n",
            QFILE);
        return 1;   // на карантині → крок падає одразу, плати не торкаючись
    }
    return 0;
}

// Після невдалого рукостискання (код 2): поставити стенд на карантин.
void hil_set_quarantine(const char *reason) {
    FILE *f = fopen(QFILE, "w");
    if (f) { fprintf(f, "%s\n", reason); fclose(f); }
    fprintf(stderr, "HIL: стенд ПОСТАВЛЕНО НА КАРАНТИН: %s\n", reason);
}

// Крихітний main: просто перевірити карантин перед прогоном (крок YAML).
// Ненуль (на карантині) валить крок одразу, плати не торкаючись.
int main(void) {
    return hil_check_quarantine();
}
