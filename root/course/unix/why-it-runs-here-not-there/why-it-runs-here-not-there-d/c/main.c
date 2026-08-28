#include <stdio.h>
#include <stdlib.h>
#include <locale.h>

int init_runtime_locale(void) {
    /* Спроба ініціалізувати локаль із середовища */
    if (setlocale(LC_ALL, "") == NULL) {
        /* Fallback на безпечну UTF-8 локаль за замовчуванням */
        if (setlocale(LC_ALL, "C.UTF-8") == NULL) {
            setlocale(LC_ALL, "C");
        }
    }
    /* Примусова фіксація крапки як десяткового роздільника для парсингу даних */
    setlocale(LC_NUMERIC, "C");
    return 0;
}
