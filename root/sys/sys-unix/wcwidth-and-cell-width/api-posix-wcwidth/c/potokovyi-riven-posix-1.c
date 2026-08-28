#include <stdio.h>
#include <locale.h>
#include <wchar.h>

/* Безпечний багатопотоковий розрахунок ширини символу */
int thread_safe_wcwidth(wchar_t wc) {
    /* Створюємо або перевикористовуємо об'єкт локалі UTF-8 */
    locale_t utf8_loc = newlocale(LC_CTYPE_MASK, "C.UTF-8", (locale_t)0);
    if (!utf8_loc) {
        /* Запасний варіант: пробуємо загальну локаль за замовчуванням */
        utf8_loc = newlocale(LC_CTYPE_MASK, "", (locale_t)0);
    }

    if (!utf8_loc) {
        return wcwidth(wc);
    }

    /* Прив'язуємо локаль виключно до поточного потоку */
    locale_t old_loc = uselocale(utf8_loc);

    int width = wcwidth(wc);

    /* Відновлюємо попередню локаль потоку та вивільняємо ресурс */
    uselocale(old_loc);
    freelocale(utf8_loc);

    return width;
}
