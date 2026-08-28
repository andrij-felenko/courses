#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <link.h>
#include <sys/stat.h>
#include <unistd.h>

static void check_directory(const char *path, const char *description) {
    struct stat st;
    if (stat(path, &st) == 0 && S_ISDIR(st.st_mode)) {
        printf("  [+] Знайдено каталог: %-32s -> %s\n", path, description);
    } else {
        printf("  [-] Відсутній каталог: %-31s -> %s\n", path, description);
    }
}

static void inspect_loaded_library(const char *lib_name) {
    /* Відкриваємо динамічну бібліотеку через динамічний завантажувач ld.so */
    void *handle = dlopen(lib_name, RTLD_LAZY);
    if (!handle) {
        printf("  [!] Помилка dlopen(%s): %s\n", lib_name, dlerror());
        return;
    }

    /* Отримуємо вказівник на внутрішню структуру link_map завантажувача */
    struct link_map *map = NULL;
    if (dlinfo(handle, RTLD_DI_LINKMAP, &map) == 0 && map && map->l_name) {
        printf("  [=>] %s (dlinfo link_map) -> %s\n", lib_name, 
               map->l_name[0] ? map->l_name : "[впроваджено в процес]");
    } else {
        printf("  [!] Не вдалося отримати link_map для %s\n", lib_name);
    }

    /* Додатково перевіряємо карти пам'яті процесу через procfs */
    FILE *maps = fopen("/proc/self/maps", "r");
    if (maps) {
        char line[512];
        int found_in_maps = 0;
        while (fgets(line, sizeof(line), maps)) {
            if (strstr(line, lib_name) && strstr(line, ".so")) {
                char *path = strchr(line, '/');
                if (path) {
                    char *newline = strchr(path, '\n');
                    if (newline) *newline = '\0';
                    printf("  [=>] %s (/proc/self/maps) -> %s\n", lib_name, path);
                    found_in_maps = 1;
                    break;
                }
            }
        }
        fclose(maps);
        if (!found_in_maps) {
            printf("  [?] %s не знайдено серед файлових мапінгів /proc/self/maps\n", lib_name);
        }
    }

    dlclose(handle);
}

int main(void) {
    printf("=========================================================\n");
    printf("   ДІАГНОСТИКА АРХІТЕКТУРНОЇ ІЄРАРХІЇ БІБЛІОТЕК (C)\n");
    printf("=========================================================\n\n");

    printf("Параметри поточного бінарного процесу:\n");
    printf("  • Модель пам'яті: %s\n", sizeof(void *) == 8 ? "LP64 (64-біт)" : "ILP32 (32-біт)");
    printf("  • Розмір вказівника: %lu байтів\n\n", (unsigned long)sizeof(void *));

    printf("1. Перевірка наявності каталогів Multilib (RPM-модель):\n");
    check_directory("/lib64", "64-бітні бібліотеки системи");
    check_directory("/usr/lib64", "64-бітні бібліотеки користувача");
    check_directory("/lib32", "32-бітні бібліотеки системи (альтернативні)");
    check_directory("/usr/lib32", "32-бітні бібліотеки користувача (альтернативні)");
    printf("\n");

    printf("2. Перевірка наявності каталогів Multiarch (Debian GNU Triplets):\n");
    check_directory("/usr/lib/x86_64-linux-gnu", "x86_64-linux-gnu (AMD64 / Intel 64)");
    check_directory("/usr/lib/i386-linux-gnu", "i386-linux-gnu (x86 32-bit)");
    check_directory("/usr/lib/aarch64-linux-gnu", "aarch64-linux-gnu (ARM64)");
    check_directory("/usr/lib/arm-linux-gnueabihf", "arm-linux-gnueabihf (ARMhf)");
    printf("\n");

    printf("3. Тестування реальних шляхів резолюції бібліотек системним ld.so:\n");
    inspect_loaded_library("libm.so.6");
    inspect_loaded_library("libc.so.6");
    printf("\n=========================================================\n");

    return 0;
}
