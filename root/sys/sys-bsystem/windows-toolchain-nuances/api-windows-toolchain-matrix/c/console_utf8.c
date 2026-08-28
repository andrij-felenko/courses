/* console_utf8.c — налаштування консолі в C */
#include <windows.h>
#include <stdio.h>

int init_console_utf8(void) {
    /* Встановлюємо кодову сторінку виводу та вводу консолі в UTF-8 (CP 65001) */
    if (!SetConsoleOutputCP(CP_UTF8) || !SetConsoleCP(CP_UTF8)) {
        return 0;
    }
    return 1;
}

int main(void) {
    if (!init_console_utf8()) {
        fprintf(stderr, "Помилка конфігурації консолі UTF-8\n");
    }
    printf("Тестовий вивід Unicode: Привіт, світе! 🚀\n");
    return 0;
}
