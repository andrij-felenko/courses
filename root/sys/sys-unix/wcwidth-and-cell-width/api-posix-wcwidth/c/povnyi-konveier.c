#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <locale.h>

/* Обчислення сумарної ширини рядка UTF-8 з обробкою багатобайтних послідовностей */
int calculate_utf8_display_width(const char *utf8_text) {
    if (!utf8_text) return 0;

    mbstate_t state;
    memset(&state, 0, sizeof(state));

    const char *current = utf8_text;
    size_t remaining = strlen(utf8_text);
    int total_width = 0;

    while (remaining > 0) {
        wchar_t wc;
        size_t consumed = mbrtowc(&wc, current, remaining, &state);

        if (consumed == 0) {
            break; /* Зустріли кінцевий нуль-термінатор */
        }
        if (consumed == (size_t)-1) {
            /* Помилка EILSEQ: неприпустима байтова послідовність UTF-8 */
            return -1;
        }
        if (consumed == (size_t)-2) {
            /* Неповна багатобайтова послідовність на кінці буфера */
            return -1;
        }

        int w = wcwidth(wc);
        if (w < 0) {
            /* Зустріли недрукований або керівний символ */
            return -1;
        }

        total_width += w;
        current += consumed;
        remaining -= consumed;
    }

    return total_width;
}

int main(void) {
    setlocale(LC_CTYPE, "");

    const char *test_lines[] = {
        "Команда: status",
        "Статус: [OK]",
        "Символи CJK: 言語",
        "Діакритика: е\u0301кран",
        NULL
    };

    for (int i = 0; test_lines[i] != NULL; ++i) {
        int w = calculate_utf8_display_width(test_lines[i]);
        printf("Текст: %-24s -> Ширина: %d комірок\n", test_lines[i], w);
    }
    return 0;
}
