#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <string.h>
#include <locale.h>

int main(void) {
    const char *s1 = "abc-1";
    const char *s2 = "abc1";

    // 1. Стандартна UTF-8 локаль
    setlocale(LC_ALL, "en_US.UTF-8");
    printf("en_US.UTF-8 strcoll: %d\n", strcoll(s1, s2)); // Дефіс ігнорується на первинному рівні

    // 2. Стандартна C-локаль
    setlocale(LC_ALL, "C");
    printf("C locale strcmp:     %d\n", strcmp(s1, s2));  // Побайтове порівняння ASCII ('-' < '1')

    return 0;
}
