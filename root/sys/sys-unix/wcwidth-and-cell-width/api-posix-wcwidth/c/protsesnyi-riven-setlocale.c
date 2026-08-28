#include <stdio.h>
#include <locale.h>
#include <wchar.h>

int main(void) {
    /* 1. Ініціалізація локалі процесу зі змінних оточення (LC_ALL / LC_CTYPE / LANG) */
    char *current_locale = setlocale(LC_CTYPE, "");
    if (!current_locale) {
        fprintf(stderr, "Попередження: не вдалося завантажити системну локаль\n");
    }

    /* 2. Тепер wcwidth коректно розпізнає символи UTF-8 */
    wchar_t cjk_char = L'語';
    printf("Ширина символу: %d комірки\n", wcwidth(cjk_char));

    return 0;
}
