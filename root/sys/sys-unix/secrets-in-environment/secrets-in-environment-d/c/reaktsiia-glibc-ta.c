/* Використання secure_getenv у системному програмуванні на C */
#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>

void read_configuration(void) {
    /* secure_getenv повертає NULL, якщо процес виконується в захищеному режимі (AT_SECURE = 1) */
    const char *custom_path = secure_getenv("APP_PLUGIN_DIR");
    if (custom_path == NULL) {
        /* Безпечне значення за замовчуванням */
        custom_path = "/usr/lib/app/plugins";
    }
    printf("Шлях до плагінів: %s\n", custom_path);
}
