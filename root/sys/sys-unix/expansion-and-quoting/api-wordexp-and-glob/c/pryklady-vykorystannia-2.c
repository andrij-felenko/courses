#include <stdio.h>
#include <stdlib.h>
#include <glob.h>

void list_log_files(const char *pattern) {
    glob_t gstruct;
    int flags = GLOB_MARK | GLOB_TILDE;

    int res = glob(pattern, flags, NULL, &gstruct);
    if (res == 0) {
        printf("Знайдено файлів: %zu\n", gstruct.gl_pathc);
        for (size_t i = 0; i < gstruct.gl_pathc; i++) {
            printf("  [%zu] %s\n", i, gstruct.gl_pathv[i]);
        }
        globfree(&gstruct);
    } else if (res == GLOB_NOMATCH) {
        printf("Файлів за маскою '%s' не знайдено.\n", pattern);
    } else {
        fprintf(stderr, "Помилка глобінгу: %d\n", res);
    }
}

int main(void) {
    list_log_files("/var/log/*.log");
    return 0;
}
