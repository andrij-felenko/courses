# 📋 Інтерфейс POSIX wcwidth, wcswidth та класифікація широких символів

Стандарт POSIX.1-2001 (IEEE Std 1003.1-2001) разом зі стандартом мови C (ISO/IEC 9899:1999) визначає базовий програмний інтерфейс для розрахунку екранної ширини окремих широких символів та багатосимвольних рядків у сітці моноширинного термінала.

Цей програмний інтерфейс є мостом між числовим представленням кодової позиції в пам'яті процесу та геометрією екранного буфера. Будь-яка бібліотека взаємодії з терміналом — від низькорівневих системних оболонок до повноекранних рушіїв керування вікнами — спирається на цей контракт для визначення того, на скільки стовпчиків пересунеться фізичний або віртуальний курсор після запису символу.

## Сигнатури та базовий контракт функцій

Інтерфейс оголошено в системному заголовному файлі `<wchar.h>` (або `<cwchar>` у мові C++):

:::tabs
```c
#include <wchar.h>

int wcwidth(wchar_t wc);
int wcswidth(const wchar_t *pwcs, size_t n);
```
```cpp
#include <cwchar>

// Стандартні оголошення POSIX у глобальному просторі імен та просторі std
int wcwidth(wchar_t wc);
int wcswidth(const wchar_t *pwcs, std::size_t n);
```
:::

### Поведінка та семантика повернення функції `wcwidth`

Функція `wcwidth` приймає один широкий символ `wc` і повертає ціле число:

1. **Повернення `0` (знаки нульової ширини):**
   - Нульовий байт завершення рядка `L'\0'` (`U+0000`);
   - Комбінаційні діакритичні знаки (Unicode General Category `Mn` — Nonspacing Mark та `Me` — Enclosing Mark), такі як наголоси, титли, умлаути (`U+0300`..`U+036F`);
   - Символи форматування та керування напрямком тексту (категорія `Cf`), включаючи маркери BiDi (`U+200E`, `U+200F`), м'який перенос (`U+00AD`) та з'єднувачі (`U+200D` ZWJ, `U+200C` ZWNJ);
   - Варіативні селектори формату (`U+FE00`..`U+FE0F`).

2. **Повернення `1` (одинарна ширина):**
   - Друковані символи базового набору ASCII (`0x20`..`0x7E`);
   - Символи європейських абеток (кирилиця, грецька, латиниця з діакритикою);
   - Символи категорії East Asian Narrow (`Na`), Halfwidth (`H`) та Neutral (`N`), якщо вони є друкованими;
   - Символи категорії East Asian Ambiguous (`A`) у західноєвропейських, американських та слов'янських локалях.

3. **Повернення `2` (подвійна ширина):**
   - Ієрогліфи східноазійських писемностей (CJK Unified Ideographs, `U+4E00`..`U+9FFF`);
   - Символи японських абеток хірагана та катакана;
   - Склади корейського письма хангиль (`U+AC00`..`U+D7A3`);
   - Символи сумісності повної ширини (`Fullwidth`, `U+FF01`..`U+FF60`);
   - Базові унітарні піктограми та емодзі стандарту Unicode, для яких визначено графічне представлення повної ширини;
   - Символи категорії Ambiguous (`A`), якщо поточною активною локаллю процесу є східноазійська локаль (наприклад, японська або китайська).

4. **Повернення `-1` (недрукований або недопустимий символ):**
   - Усі керуючі символи C0 та C1 (`\n`, `\r`, `\t`, `\b`, `\a`, `ESC`);
   - Кодові позиції, які не є друкованими згідно з предикатом `iswprint(wc)`;
   - Будь-які символи з кодом понад `0x7F`, якщо програма виконується в початковій локалі `"C"` або `"POSIX"`;
   - Невизначені або недійсні кодові позиції Unicode, відсутні в таблицях поточної системної бібліотеки.

### Поведінка та контракт функції `wcswidth`

Функція `wcswidth` перевіряє широкі символи в масиві, на який вказує покажчик `pwcs`, обробляючи щонайбільше `n` елементів:
- Підсумовування зупиняється на першому зустрінутому нульовому термінаторі `L'\0'` або після вичерпання ліміту `n`.
- Якщо під час обходу хоча б один широкий символ повертає значення `-1` (тобто символ не є друкованим), функція `wcswidth` **негайно перериває обчислення** і повертає **`-1`**.
- Якщо всі перевірені символи є коректними й друкованими, функція повертає точну суму ширин: `∑ wcwidth(pwcs[i])`.

## Внутрішня реалізація в glibc проти musl libc

Системні бібліотеки C у світі Unix реалізують таблиці `wcwidth` принципово різними шляхами, що безпосередньо впливає на швидкість, споживання пам'яті та актуальність даних:

### Реалізація в GNU C Library (glibc)

У складі `glibc` функція `wcwidth` спирається на скомпільовані бінарні файли локалей (`locale-archive` або окремі каталоги в `/usr/lib/locale/`). Під час збирання файлу локалі системною утилітою `localedef` генерується двійкова структура властивостей символів `LC_CTYPE`. У цій структурі для кожної кодової позиції зберігається бітова маска атрибутів (`_ISwprint`, `_ISwalnum`, `_ISwspace` тощо) та окрема таблиця екранних ширин (`WIDTH`).

Коли програма викликає `setlocale(LC_CTYPE, "")`, бібліотека `glibc` відкриває файл локалі та відображає його структури в адресний простір процесу за допомогою системного виклику `mmap(2)`. Розрахунок ширини виконується через трирівневу таблицю індексування (*three-level trie/lookup table*): старші біти кодової позиції слугують індексом першого рівня, середні — другого, а молодші визначають конкретний елемент у блоці. Якщо відповідна таблиця локалі не була згенерована або в системі активна базова локаль `"C"`, `glibc` використовує вбудовану мінімальну таблицю ASCII, де для всіх кодових позицій `wc > 127` безумовно повертається `-1`.

### Реалізація в musl libc

Бібліотека `musl` сповідує філософію максимальної компактності та повної незалежності від зовнішніх бінарних файлів локалей. Усі текстові потоки в `musl` вважаються закодованими в UTF-8. Функція `wcwidth` реалізована як компактна статична таблиця інтервалів безпосередньо в тілі бібліотеки (за оптимізованим двійковим деревом Маркуса Куна). Завдяки відсутності звернень до файлової системи та викликів `mmap`, виклик `wcwidth` у `musl` виконується з високою швидкістю, займаючи кілька сотень байтів машинного коду.

## Керування системною та потоковою локаллю

Оскільки контракт POSIX зобов'язує `wcwidth` враховувати активну локаль, будь-яка прикладна програма зобов'язана явно декларувати середовище виконання.

### Процесний рівень: `setlocale`

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <clocale>
#include <cwchar>

int main() {
    // Ініціалізація локалі процесу
    const char* current_locale = std::setlocale(LC_CTYPE, "");
    if (!current_locale) {
        std::cerr << "Попередження: не вдалося завантажити системну локаль\n";
    }

    wchar_t cjk_char = L'語';
    std::cout << "Ширина символу: " << wcwidth(cjk_char) << " комірки\n";

    return 0;
}
```
:::

### Потоковий рівень: POSIX.1-2008 `newlocale` та `uselocale`

Виклик `setlocale` не є безпечним для багатопотокових бібліотек, оскільки змінює глобальний стан усього процесу. Якщо бібліотека розрахунку термінальної ширини виконується у фоновому потоці або всередині плагіна, вона повинна використовувати об'єкти локалі `locale_t`:

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <clocale>
#include <cwchar>
#include <locale.h>

// RAII-обгортка для безпечного перемикання потокової локалі в C++
class ThreadLocaleGuard {
public:
    explicit ThreadLocaleGuard(const char* locale_name) {
        loc_ = newlocale(LC_CTYPE_MASK, locale_name, nullptr);
        if (loc_) {
            old_loc_ = uselocale(loc_);
        }
    }

    ~ThreadLocaleGuard() {
        if (loc_) {
            uselocale(old_loc_);
            freelocale(loc_);
        }
    }

    ThreadLocaleGuard(const ThreadLocaleGuard&) = delete;
    ThreadLocaleGuard& operator=(const ThreadLocaleGuard&) = delete;

private:
    locale_t loc_{nullptr};
    locale_t old_loc_{nullptr};
};

int calculate_width_safe(wchar_t wc) {
    ThreadLocaleGuard guard("C.UTF-8");
    return wcwidth(wc);
}
```
:::

## Повний конвеєр: перетворення UTF-8 у широкі символи з контролем стану

У реальних програмах вхідні дані надходять у вигляді байтового потоку кодування UTF-8. Перед викликом `wcwidth` рядок необхідно перетворити на послідовність широких символів за допомогою стандартизованої функції `mbrtowc` (Multi-Byte Reentrant to Wide Character), яка підтримує структуру зсуву стану `mbstate_t`.

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <cwchar>
#include <clocale>
#include <cstring>
#include <expected>

enum class StringWidthError {
    InvalidUtf8Sequence,
    IncompleteSequence,
    NonPrintableCharacter
};

// Розрахунок термінальної ширини рядка UTF-8 у стилі C++23 з std::expected
std::expected<int, StringWidthError> calculate_utf8_display_width(std::string_view utf8_text) {
    std::mbstate_t state{};
    const char* current = utf8_text.data();
    std::size_t remaining = utf8_text.size();
    int total_width = 0;

    while (remaining > 0) {
        wchar_t wc = 0;
        std::size_t consumed = std::mbrtowc(&wc, current, remaining, &state);

        if (consumed == 0) {
            break;
        }
        if (consumed == static_cast<std::size_t>(-1)) {
            return std::unexpected(StringWidthError::InvalidUtf8Sequence);
        }
        if (consumed == static_cast<std::size_t>(-2)) {
            return std::unexpected(StringWidthError::IncompleteSequence);
        }

        int w = wcwidth(wc);
        if (w < 0) {
            return std::unexpected(StringWidthError::NonPrintableCharacter);
        }

        total_width += w;
        current += consumed;
        remaining -= consumed;
    }

    return total_width;
}

int main() {
    std::setlocale(LC_CTYPE, "");

    const std::vector<std::string_view> test_lines = {
        "Команда: status",
        "Статус: [OK]",
        "Символи CJK: 言語",
        "Діакритика: е\u0301кран"
    };

    for (const auto& line : test_lines) {
        auto width_result = calculate_utf8_display_width(line);
        if (width_result.has_value()) {
            std::cout << "Текст: " << line << " -> Ширина: " << *width_result << " комірок\n";
        } else {
            std::cerr << "Помилка розрахунку ширини для рядка: " << line << "\n";
        }
    }
    return 0;
}
```
:::

## Зведена таблиця помилок та крайових випадків

Під час інтеграції функцій `wcwidth` та `wcswidth` у власні системні компоненти необхідно враховувати типові пастки поведінки стандартної бібліотеки:

| Сценарій / Вхідні дані | Поведінка `wcwidth` / `wcswidth` | Причина та наслідки | Коректне вирішення в коді |
| :--- | :--- | :--- | :--- |
| **Локаль `"C"` за замовчуванням** | Повертає `-1` для будь-яких символів з кодом `> 127` | Таблиці локалі не підключені | Викликати `setlocale(LC_CTYPE, "")` перед роботою з текстом |
| **Складені емодзі з ZWJ (`U+200D`)** | Повертає `2 + 0 + 2 = 4` для одного гліфа на 2 комірки | Посимвольна обробка без контексту графеми | Використовувати алгоритм сегментації графемних кластерів UAX #29 |
| **Символи PUA (Private Use Area)** | Повертає `-1` або `1` залежно від libc | Коди `U+E000`..`U+F8FF` не стандартизовані | Явна обробка іконок Nerd Fonts / Powerline у таблицях застосунку |
| **16-бітний `wchar_t` у Windows (MSVC)** | Сурогатні пари розбивають символ вищої площини на два `wchar_t` | `wcwidth` не стандартизований у Win32 CRT | Використовувати власні таблиці над 32-бітним типом `char32_t` / `uint32_t` |
| **Символ табуляції `\t` (`0x09`)** | Повертає `-1` | Табуляція не має фіксованої ширини, вона зсуває курсор до наступної позиції кратно 8 | Програма повинна самостійно розгортати табуляції в пробіли за формулою `8 - (col % 8)` |
| **Помилка кодування `EILSEQ`** | `mbrtowc` повертає `(size_t)-1` | Неприпустимий байт у потоці UTF-8 | Замінити пошкоджений байт символом `U+FFFD` і продовжити обробку з наступного байта |
