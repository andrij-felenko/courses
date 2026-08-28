/* main.c — C-реалізація динамічного завантаження плагіна */
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

/* Тип вказівника на функцію плагіна */
typedef void (*plugin_func_t)(const char *);

int main(int argc, char *argv[]) {
    const char *plugin_path = "./libplugin.so";
    if (argc > 1) {
        plugin_path = argv[1];
    }

    /* 1. Динамічне відкриття бібліотеки */
    void *handle = dlopen(plugin_path, RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        fprintf(stderr, "Помилка завантаження %s: %s\n", plugin_path, dlerror());
        return EXIT_FAILURE;
    }

    /* Скидаємо попередній стан помилок */
    dlerror();

    /* 2. Пошук адреси символу */
    plugin_func_t process_func = (plugin_func_t)dlsym(handle, "plugin_process");
    const char *dlsym_err = dlerror();
    if (dlsym_err != NULL) {
        fprintf(stderr, "Символ plugin_process не знайдено: %s\n", dlsym_err);
        dlclose(handle);
        return EXIT_FAILURE;
    }

    /* 3. Виклик функції плагіна */
    process_func("Тестовий пакет даних C");

    /* 4. Закриття дескриптора */
    dlclose(handle);
    return EXIT_SUCCESS;
}
