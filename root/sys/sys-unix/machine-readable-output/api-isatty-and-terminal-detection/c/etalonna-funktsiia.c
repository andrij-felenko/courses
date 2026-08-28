#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int should_enable_color(int fd) {
    /* 1. Стандарт NO_COLOR: найвищий пріоритет */
    const char *no_color = getenv("NO_COLOR");
    if (no_color != NULL && no_color[0] != '\0') {
        return 0;
    }

    /* 2. Примусове увімкнення кольорів для CI/CD логів */
    const char *clicolor_force = getenv("CLICOLOR_FORCE");
    if (clicolor_force != NULL && strcmp(clicolor_force, "0") != 0) {
        return 1;
    }

    /* 3. Перевірка примітивного термінала dumb */
    const char *term = getenv("TERM");
    if (term != NULL && strcmp(term, "dumb") == 0) {
        return 0;
    }

    /* 4. Заборона через CLICOLOR=0 */
    const char *clicolor = getenv("CLICOLOR");
    if (clicolor != NULL && strcmp(clicolor, "0") == 0) {
        return 0;
    }

    /* 5. Автоматичне визначення TTY */
    return isatty(fd);
}
