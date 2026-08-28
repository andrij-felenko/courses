/* Класичний виклик setlocale у C */
#include <stdio.h>
#include <locale.h>
#include <string.h>

int main(void) {
    // Ініціалізація локалі із середовища користувача
    if (setlocale(LC_ALL, "") == NULL) {
        fprintf(stderr, "Помилка встановлення локалі з оточення\n");
    }

    const char *s1 = "апельсин";
    const char *s2 = "банан";

    // Порівняння з урахуванням LC_COLLATE
    int res = strcoll(s1, s2);
    if (res < 0) {
        printf("%s передує %s\n", s1, s2);
    }
    return 0;
}
