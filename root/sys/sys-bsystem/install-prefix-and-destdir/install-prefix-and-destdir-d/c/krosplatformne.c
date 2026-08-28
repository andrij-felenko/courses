#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libgen.h>

int get_app_datadir(char* buffer, size_t max_len) {
    char exe_path[1024];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len == -1) {
        /* Fallback до скомпільованого префікса за замовчуванням */
        snprintf(buffer, max_len, "/usr/local/share/myapp");
        return 0;
    }
    exe_path[len] = '\0';

    /* Отримуємо каталог бінарника (наприклад /opt/myapp/bin) */
    char* dir = dirname(exe_path);
    /* Формуємо відносний шлях до ресурсів /opt/myapp/share/myapp */
    snprintf(buffer, max_len, "%s/../share/myapp", dir);
    return 1;
}
