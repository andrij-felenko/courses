#include <stdio.h>
#include <wchar.h>
#include <locale.h>

int main(void) {
    /* Без цього виклику wcwidth працюватиме лише з 7-бітним ASCII */
    setlocale(LC_CTYPE, "");

    wchar_t chars[] = { L'A', L'ф', L'語', 0x0301, L'🚀', 0 };

    for (int i = 0; chars[i] != 0; ++i) {
        int w = wcwidth(chars[i]);
        printf("Символ U+%04X -> ширина: %2d комірки\n", (unsigned int)chars[i], w);
    }
    return 0;
}
