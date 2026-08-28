#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <link.h>
#include <sys/auxv.h>
#include <stdbool.h>

/* Ітератор завантажених розділюваних об'єктів у адресному просторі */
static int module_callback(struct dl_phdr_info *info, size_t size, void *data) {
    (void)size;
    (void)data;
    const char *name = (info->dlpi_name && info->dlpi_name[0] != '\0') 
                       ? info->dlpi_name 
                       : "[Main Executable]";
    printf("  - Базова адреса: 0x%012lx | Модуль: %s\n", 
           (unsigned long)info->dlpi_addr, name);
    return 0;
}

/* Отримання та вивід шляхів пошуку ld.so */
static bool print_search_paths(void *handle) {
    Dl_serinfo size_info;
    Dl_serinfo *info = NULL;

    /* Крок 1: Запит необхідного розміру пам'яті */
    if (dlinfo(handle, RTLD_DI_SERINFOSIZE, &size_info) != 0) {
        fprintf(stderr, "Помилка dlinfo(RTLD_DI_SERINFOSIZE): %s\n", dlerror());
        return false;
    }

    info = (Dl_serinfo *)malloc(size_info.dls_size);
    if (!info) {
        perror("Помилка виділення пам'яті під Dl_serinfo");
        return false;
    }

    /* Ініціалізація полів структури перед повторним викликом */
    info->dls_size = size_info.dls_size;
    info->dls_cnt = size_info.dls_cnt;

    /* Крок 2: Отримання детальної інформації про шляхи */
    if (dlinfo(handle, RTLD_DI_SERINFO, info) != 0) {
        fprintf(stderr, "Помилка dlinfo(RTLD_DI_SERINFO): %s\n", dlerror());
        free(info);
        return false;
    }

    printf("\nАктивні шляхи пошуку ld.so (усього: %u):\n", info->dls_cnt);
    for (unsigned int i = 0; i < info->dls_cnt; ++i) {
        printf("  [%u] %s\n", i + 1, info->dls_serpath[i].dls_name);
    }

    free(info);
    return true;
}

int main(void) {
    unsigned long secure = getauxval(AT_SECURE);
    printf("=== Інспектор динамічного завантажувача (C) ===\n");
    printf("Режим безпеки AT_SECURE: %lu (%s)\n\n", 
           secure, secure ? "АКТИВНИЙ — LD_LIBRARY_PATH ігнорується" : "Ззвичайний");

    printf("Завантажені ELF-модулі в адресному просторі:\n");
    dl_iterate_phdr(module_callback, NULL);

    void *handle = dlopen(NULL, RTLD_NOW);
    if (!handle) {
        fprintf(stderr, "Помилка dlopen(NULL): %s\n", dlerror());
        return EXIT_FAILURE;
    }

    if (!print_search_paths(handle)) {
        dlclose(handle);
        return EXIT_FAILURE;
    }

    dlclose(handle);
    return EXIT_SUCCESS;
}
