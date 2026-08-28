/* plugin.c — C-реалізація плагіна з конструктором та деструктором */
#include <stdio.h>

/* Функція ініціалізації: викликається при dlopen */
__attribute__((constructor))
static void plugin_init(void) {
    printf("[Plugin C] Ініціалізація модуля (constructor)...\n");
}

/* Функція фіналізації: викликається при dlclose */
__attribute__((destructor))
static void plugin_fini(void) {
    printf("[Plugin C] Завершення роботи модуля (destructor)...\n");
}

/* Експортована функція з C ABI */
void plugin_process(const char *input) {
    printf("[Plugin C] Обробка вхідних даних: %s\n", input);
}
