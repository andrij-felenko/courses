/* C приклад отримання кодування через nl_langinfo */
#include <stdio.h>
#include <locale.h>
#include <langinfo.h>

void print_current_codeset(void) {
    setlocale(LC_ALL, "");
    const char *cs = nl_langinfo(CODESET);
    printf("Активне кодування термінала: %s\n", cs);
}
