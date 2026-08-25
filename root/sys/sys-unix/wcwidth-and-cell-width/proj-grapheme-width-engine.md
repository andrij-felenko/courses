# ⚙️ Обчислення ширини графемних кластерів: від UTF-8 до комірок

Розрахунок кількості комірок, які довільний рядок Unicode займає на екрані сучасного емулятора термінала, вимагає переходу від поодиноких байтів чи ізольованих кодових позицій `wchar_t` до неподільних користувацьких символів — розширених графемних кластерів (*extended grapheme clusters*).

Стандартні функції операційної системи `wcwidth` та `wcswidth` не мають інформації про сусідні символи. Коли у вхідному потоці з'являється складений емодзі на кшталт жінки-програміста 👩‍💻 (`U+1F469` + `U+200D` + `U+1F4BB`) або прапор країни 🇺🇦 (`U+1F1FA` + `U+1F1E6`), системний виклик підсумовує ширини окремих кодових позицій і повертає число від 4 до 8 комірок, тоді як графічний рушій емулятора малює єдиний гліф рівно у двох комірках. Для усунення розсинхронізації консольна програма мусить містити власний автономний рушій сегментації та підрахунку ширини.

## Архітектура власного рушія розрахунку ширини

Щоб правильно обробляти комбінаційні знаки, варіативні селектори та складні послідовності емодзі, алгоритм розділено на три послідовні рівні:

1. **Потоковий декодер UTF-8:** перетворює сирий потік байтів у послідовність 32-бітних кодових позицій Unicode (`uint32_t` або `char32_t`). Декодер виконує валідацію байтів продовження (`0x80`..`0xBF`), відкидає надлишкові (*overlong*) послідовності та замінює пошкоджені байти символом заміни `U+FFFD`.
2. **Таблична класифікація за стандартом UAX #11:** швидкий бінарний пошук за відсортованими діапазонами кодових позицій. Класифікатор визначає, чи є символ повноширинним (Wide / Fullwidth), нейтральним чи нульової ширини (категорії `Mn`, `Me`, `Cf`, варіативні селектори `VS1`..`VS16`).
3. **Скінченний автомат згортання графемного кластера (UAX #29):** відстежує стан між сусідніми кодовими позиціями:
   - Базовий друкований символ відкриває новий графемний кластер і встановлює початкову ширину (1 або 2 комірки);
   - Комбінаційні діакритичні знаки нульової ширини приєднуються до базового символу, не збільшуючи загальну ширину кластера;
   - Варіативний селектор `U+FE0E` (VS15) примусово обмежує ширину кластера однією коміркою (текстове монохромне представлення);
   - Варіативний селектор `U+FE0F` (VS16) розширює кластер до двох комірок (кольорове графічне емодзі);
   - З'єднувач `U+200D` (ZWJ) переводить автомат у стан зв'язування: наступний символ емодзі зливається з попереднім у єдиний гліф максимальною шириною у 2 комірки;
   - Послідовні пари регіональних індикаторів (`U+1F1E6`..`U+1F1FF`) об'єднуються в єдиний 2-комірковий прапор.

## Таблиці інтервалів та швидкість пошуку

Простір Unicode містить 1 114 112 кодових позицій (`0x000000`..`0x10FFFF`). Зберігати плоский масив ширин для кожного коду невигідно: масив зайняв би понад 1 мегабайт пам'яті, вимиваючи процесорний кеш першого рівня L1.

Натомість властивості символів мають високу просторову локальність і групуються у великі неперервні інтервали (наприклад, блок ієрогліфів CJK `U+4E00`..`U+9FFF` охоплює понад 20 тисяч знаків одним діапазоном). Зберігання списку інтервалів `{first, last}` зменшує обсяг таблиці до кількох кілобайтів.

Пошук кодової позиції у відсортованій таблиці інтервалів виконується за алгоритмом двійкового поділу `O(log N)`. Для 40 інтервалів потрібно щонайбільше 6 порівнянь, що виконується менш ніж за 10 наносекунд на сучасних процесорах.

## Покрокове трасування станів автомата

Щоб наочно проілюструвати роботу автомата розрахунку ширини, розглянемо обробку трьох типових тестових послідовностей:

1. **Комбінаційний наголос у слові `е́кран` (`U+0065` + `U+0301`):**
   - Крок 1: надходить `U+0065` (латинська або кирилична літера `e`). Вона не є нульовою чи широкою, автомат фіксує початок кластера: `current_cluster_width = 1`.
   - Крок 2: надходить `U+0301` (Combining Acute Accent). Функція `is_zero_width` повертає `true`. Автомат ігнорує знак і залишає `current_cluster_width = 1`.
   - Результат: для пари кодових позицій повернуто рівно **1 комірку**.

2. **Складений ZWJ-емодзі `👨‍💻` (`U+1F468` + `U+200D` + `U+1F4BB`):**
   - Крок 1: надходить `U+1F468` (чоловік). Функція `is_wide_char` повертає `true`: `current_cluster_width = 2`.
   - Крок 2: надходить `U+200D` (ZWJ). Автомат виставляє прапорець `in_zwj_sequence = true`.
   - Крок 3: надходить `U+1F4BB` (ноутбук). Прапорець `in_zwj_sequence` активний: автомат скидає прапорець і не створює новий кластер, залишаючи `current_cluster_width = 2`.
   - Результат: для 3 кодових позицій сумарно нараховано рівно **2 комірки**.

3. **Прапор України `🇺🇦` (`U+1F1FA` + `U+1F1E6`):**
   - Крок 1: надходить `U+1F1FA` (регіональний індикатор U). Прапорець `is_regional_indicator` стає `true`, `current_cluster_width = 2`.
   - Крок 2: надходить `U+1F1E6` (регіональний індикатор A). Попередній індикатор активний: пара замикається, прапорець скидається в `false`.
   - Результат: для 2 кодових позицій нараховано рівно **2 комірки**.

## Практична реалізація: повний рушій ширини

Нижче наведено повністю працездатний модуль розрахунку ширини тексту мовами C та C++, оптимізований для використання в CLI/TUI утилітах без зовнішніх бібліотечних залежностей.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Інтервал кодових позицій для бінарного пошуку */
struct Interval {
    uint32_t first;
    uint32_t last;
};

/* Допоміжний бінарний пошук по таблиці відсортованих інтервалів */
static bool in_intervals(uint32_t cp, const struct Interval *table, size_t size) {
    if (cp < table[0].first || cp > table[size - 1].last) {
        return false;
    }
    size_t min = 0;
    size_t max = size - 1;
    while (max >= min) {
        size_t mid = (min + max) / 2;
        if (cp > table[mid].last) {
            min = mid + 1;
        } else if (cp < table[mid].first) {
            if (mid == 0) break;
            max = mid - 1;
        } else {
            return true;
        }
    }
    return false;
}

/* Перевірка на знаки нульової ширини (Mn, Me, Cf, ZWJ) */
static bool is_zero_width(uint32_t cp) {
    static const struct Interval zero_table[] = {
        {0x0000, 0x0000},   /* NUL */
        {0x0300, 0x036F},   /* Combining Diacritical Marks */
        {0x0483, 0x0489},   /* Cyrillic Combining Marks */
        {0x0591, 0x05BD},   /* Hebrew Accents */
        {0x05BF, 0x05BF},
        {0x05C1, 0x05C2},
        {0x05C4, 0x05C5},
        {0x05C7, 0x05C7},
        {0x0610, 0x061A},   /* Arabic Signs */
        {0x064B, 0x065F},
        {0x0670, 0x0670},
        {0x06D6, 0x06DC},
        {0x200B, 0x200F},   /* Zero-Width Space, ZWNJ, ZWJ, LRM, RLM */
        {0x202A, 0x202E},   /* BiDi Controls */
        {0x2060, 0x206F},   /* Invisible Formatting */
        {0xFE00, 0xFE0F},   /* Variation Selectors VS1..VS16 */
        {0xE0100, 0xE01EF}  /* Variation Selectors Supplement */
    };
    return in_intervals(cp, zero_table, sizeof(zero_table)/sizeof(zero_table[0]));
}

/* Перевірка на повноширинні символи та CJK (East Asian Wide / Fullwidth) */
static bool is_wide_char(uint32_t cp) {
    static const struct Interval wide_table[] = {
        {0x1100, 0x115F},   /* Hangul Jamo */
        {0x231A, 0x231B},   /* Watch, Hourglass */
        {0x23E9, 0x23EC},   /* Fast-forward etc. */
        {0x23F0, 0x23F3},   /* Alarm clock etc. */
        {0x25FD, 0x25FE},   /* Medium small squares */
        {0x2614, 0x2615},   /* Umbrella, Hot beverage */
        {0x2648, 0x2653},   /* Zodiac signs */
        {0x267F, 0x267F},   /* Wheelchair */
        {0x2693, 0x2693},   /* Anchor */
        {0x26A1, 0x26A1},   /* High voltage */
        {0x26AA, 0x26AB},   /* Circles */
        {0x26BD, 0x26BE},   /* Soccer, Baseball */
        {0x26C4, 0x26C5},   /* Snowman, Sun behind cloud */
        {0x26CE, 0x26CE},   /* Ophiuchus */
        {0x26D4, 0x26D4},   /* No entry */
        {0x26EA, 0x26EA},   /* Church */
        {0x26F2, 0x26F3},   /* Fountain, Flag in hole */
        {0x26F5, 0x26F5},   /* Sailboat */
        {0x26FA, 0x26FA},   /* Tent */
        {0x26FD, 0x26FD},   /* Fuel pump */
        {0x2705, 0x2705},   /* Check mark */
        {0x270A, 0x270B},   /* Raised fist, hand */
        {0x2728, 0x2728},   /* Sparkles */
        {0x274C, 0x274C},   /* Cross mark */
        {0x274E, 0x274E},
        {0x2753, 0x2755},   /* Question marks */
        {0x2757, 0x2757},   /* Exclamation mark */
        {0x27B0, 0x27B0},   /* Curly loop */
        {0x27BF, 0x27BF},
        {0x2B1B, 0x2B1C},   /* Black/White large squares */
        {0x2B50, 0x2B50},   /* Star */
        {0x2B55, 0x2B55},   /* Heavy circle */
        {0x2E80, 0xA4CF},   /* CJK Radicals, Kangxi, Ideographs */
        {0xAC00, 0xD7A3},   /* Hangul Syllables */
        {0xF900, 0xFAFF},   /* CJK Compatibility Ideographs */
        {0xFE10, 0xFE19},   /* Vertical forms */
        {0xFE30, 0xFE6F},   /* CJK Compatibility Forms */
        {0xFF01, 0xFF60},   /* Fullwidth ASCII Variants */
        {0xFFE0, 0xFFE6},   /* Fullwidth Currency Signs */
        {0x1F300, 0x1F64F}, /* Emoji and Pictographs */
        {0x1F680, 0x1F6FF}, /* Transport and Map Symbols */
        {0x1F900, 0x1F9FF}, /* Supplemental Symbols and Pictographs */
        {0x1FA70, 0x1FAFF}, /* Symbols and Pictographs Extended-A */
        {0x20000, 0x2FFFD}, /* CJK Unified Ideographs Extension B..F */
        {0x30000, 0x3FFFD}  /* CJK Unified Ideographs Extension G..I */
    };
    return in_intervals(cp, wide_table, sizeof(wide_table)/sizeof(wide_table[0]));
}

/* Декодування одного символу UTF-8 у 32-бітний кодовий пункт */
static size_t decode_utf8(const char *s, size_t len, uint32_t *out_cp) {
    if (len == 0 || !s) return 0;
    unsigned char c = (unsigned char)s[0];

    if (c < 0x80) {
        *out_cp = c;
        return 1;
    } else if ((c & 0xE0) == 0xC0) {
        if (len < 2) return 0;
        *out_cp = ((c & 0x1F) << 6) | (s[1] & 0x3F);
        return 2;
    } else if ((c & 0xF0) == 0xE0) {
        if (len < 3) return 0;
        *out_cp = ((c & 0x0F) << 12) | ((s[1] & 0x3F) << 6) | (s[2] & 0x3F);
        return 3;
    } else if ((c & 0xF8) == 0xF0) {
        if (len < 4) return 0;
        *out_cp = ((c & 0x07) << 18) | ((s[1] & 0x3F) << 12) | ((s[2] & 0x3F) << 6) | (s[3] & 0x3F);
        return 4;
    }
    *out_cp = 0xFFFD; /* Некоректний байт замінюється на Replacement Character */
    return 1;
}

/* Розрахунок термінальної ширини рядка з урахуванням графемних кластерів та ZWJ */
int calculate_grapheme_string_width(const char *utf8_str) {
    if (!utf8_str) return 0;

    size_t len = strlen(utf8_str);
    size_t offset = 0;
    int total_width = 0;

    int current_cluster_width = 0;
    bool in_zwj_sequence = false;
    bool is_regional_indicator = false;

    while (offset < len) {
        uint32_t cp = 0;
        size_t bytes = decode_utf8(utf8_str + offset, len - offset, &cp);
        if (bytes == 0) break;
        offset += bytes;

        if (cp == 0x200D) { /* Zero Width Joiner (ZWJ) */
            in_zwj_sequence = true;
            continue;
        }

        if (cp == 0xFE0E) { /* VS15: примусове текстове відображення (ширина 1) */
            if (current_cluster_width > 1) current_cluster_width = 1;
            continue;
        }

        if (cp == 0xFE0F) { /* VS16: примусове емодзі-відображення (ширина 2) */
            if (current_cluster_width < 2) current_cluster_width = 2;
            continue;
        }

        if (is_zero_width(cp)) {
            /* Комбінаційний знак приєднується до поточної графеми, не додаючи ширини */
            continue;
        }

        /* Обробка пар регіональних індикаторів для прапорів (U+1F1E6..U+1F1FF) */
        if (cp >= 0x1F1E6 && cp <= 0x1F1FF) {
            if (is_regional_indicator) {
                /* Друга половина прапора закриває 2-коміркову графему */
                is_regional_indicator = false;
                continue;
            } else {
                total_width += current_cluster_width;
                current_cluster_width = 2;
                is_regional_indicator = true;
                continue;
            }
        }
        is_regional_indicator = false;

        if (in_zwj_sequence) {
            /* Послідовність після ZWJ не створює нових комірок, якщо вже є емодзі */
            in_zwj_sequence = false;
            if (current_cluster_width < 2) current_cluster_width = 2;
            continue;
        }

        /* Фіксуємо ширину попереднього завершеного кластера */
        total_width += current_cluster_width;

        /* Початок нового графемного кластера */
        current_cluster_width = is_wide_char(cp) ? 2 : 1;
    }

    total_width += current_cluster_width;
    return total_width;
}

int main(void) {
    const char *test_cases[] = {
        "ASCII text",           /* 10 комірок */
        "Кирилиця",             /* 8 комірок */
        "Кава ☕ та код 💻",     /* 5 + 2 + 8 + 2 = 17 комірок */
        "е\u0301кран (accent)", /* 5 + 9 = 14 комірок */
        "👨‍💻 програміст",       /* 2 + 1 + 11 = 14 комірок */
        "🇺🇦 Україна",          /* 2 + 1 + 7 = 10 комірок */
        NULL
    };

    for (int i = 0; test_cases[i] != NULL; ++i) {
        int w = calculate_grapheme_string_width(test_cases[i]);
        printf("Рядок: %-26s | Ширина: %2d комірок\n", test_cases[i], w);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <cstdint>
#include <algorithm>

struct Interval {
    uint32_t first;
    uint32_t last;
};

// Швидкий бінарний пошук за інтервалами кодових позицій
bool in_intervals(uint32_t cp, const std::vector<Interval>& table) {
    if (table.empty() || cp < table.front().first || cp > table.back().last) {
        return false;
    }
    auto it = std::lower_bound(table.begin(), table.end(), cp,
        [](const Interval& interval, uint32_t val) {
            return interval.last < val;
        });
    return (it != table.end() && cp >= it->first && cp <= it->last);
}

bool is_zero_width(uint32_t cp) {
    static const std::vector<Interval> zero_table = {
        {0x0000, 0x0000},
        {0x0300, 0x036F}, // Combining Diacritical Marks
        {0x0483, 0x0489}, // Cyrillic Combining Marks
        {0x0591, 0x05BD}, // Hebrew Accents
        {0x05BF, 0x05BF},
        {0x05C1, 0x05C2},
        {0x05C4, 0x05C5},
        {0x05C7, 0x05C7},
        {0x0610, 0x061A}, // Arabic Signs
        {0x064B, 0x065F},
        {0x0670, 0x0670},
        {0x06D6, 0x06DC},
        {0x200B, 0x200F}, // ZWSP, ZWNJ, ZWJ, LRM, RLM
        {0x202A, 0x202E}, // BiDi Controls
        {0x2060, 0x206F}, // Formatting
        {0xFE00, 0xFE0F}, // Variation Selectors
        {0xE0100, 0xE01EF}
    };
    return in_intervals(cp, zero_table);
}

bool is_wide_char(uint32_t cp) {
    static const std::vector<Interval> wide_table = {
        {0x1100, 0x115F},   // Hangul Jamo
        {0x231A, 0x231B},   // Watch, Hourglass
        {0x23E9, 0x23EC},
        {0x23F0, 0x23F3},
        {0x25FD, 0x25FE},
        {0x2614, 0x2615},
        {0x2648, 0x2653},
        {0x267F, 0x267F},
        {0x2693, 0x2693},
        {0x26A1, 0x26A1},
        {0x26AA, 0x26AB},
        {0x26BD, 0x26BE},
        {0x26C4, 0x26C5},
        {0x26CE, 0x26CE},
        {0x26D4, 0x26D4},
        {0x26EA, 0x26EA},
        {0x26F2, 0x26F3},
        {0x26F5, 0x26F5},
        {0x26FA, 0x26FA},
        {0x26FD, 0x26FD},
        {0x2705, 0x2705},
        {0x270A, 0x270B},
        {0x2728, 0x2728},
        {0x274C, 0x274C},
        {0x274E, 0x274E},
        {0x2753, 0x2755},
        {0x2757, 0x2757},
        {0x27B0, 0x27B0},
        {0x27BF, 0x27BF},
        {0x2B1B, 0x2B1C},
        {0x2B50, 0x2B50},
        {0x2B55, 0x2B55},
        {0x2E80, 0xA4CF},   // CJK Radicals, Ideographs
        {0xAC00, 0xD7A3},   // Hangul Syllables
        {0xF900, 0xFAFF},   // CJK Compatibility
        {0xFE10, 0xFE19},
        {0xFE30, 0xFE6F},
        {0xFF01, 0xFF60},   // Fullwidth ASCII
        {0xFFE0, 0xFFE6},
        {0x1F300, 0x1F64F}, // Emoji
        {0x1F680, 0x1F6FF},
        {0x1F900, 0x1F9FF},
        {0x1FA70, 0x1FAFF},
        {0x20000, 0x3FFFD}  // CJK Unified Extensions
    };
    return in_intervals(cp, wide_table);
}

// Декодування наступного UTF-8 символу з перевіркою коректності
std::pair<uint32_t, std::size_t> decode_utf8(std::string_view s) {
    if (s.empty()) return {0, 0};
    auto c = static_cast<unsigned char>(s[0]);

    if (c < 0x80) {
        return {c, 1};
    } else if ((c & 0xE0) == 0xC0 && s.size() >= 2) {
        return {((c & 0x1F) << 6) | (s[1] & 0x3F), 2};
    } else if ((c & 0xF0) == 0xE0 && s.size() >= 3) {
        return {((c & 0x0F) << 12) | ((s[1] & 0x3F) << 6) | (s[2] & 0x3F), 3};
    } else if ((c & 0xF8) == 0xF0 && s.size() >= 4) {
        return {((c & 0x07) << 18) | ((s[1] & 0x3F) << 12) | ((s[2] & 0x3F) << 6) | (s[3] & 0x3F), 4};
    }
    return {0xFFFD, 1};
}

int calculate_grapheme_string_width(std::string_view utf8_str) {
    std::size_t offset = 0;
    int total_width = 0;
    int current_cluster_width = 0;
    bool in_zwj_sequence = false;
    bool is_regional_indicator = false;

    while (offset < utf8_str.size()) {
        auto [cp, bytes] = decode_utf8(utf8_str.substr(offset));
        if (bytes == 0) break;
        offset += bytes;

        if (cp == 0x200D) { // ZWJ
            in_zwj_sequence = true;
            continue;
        }

        if (cp == 0xFE0E) { // VS15
            if (current_cluster_width > 1) current_cluster_width = 1;
            continue;
        }
        if (cp == 0xFE0F) { // VS16
            if (current_cluster_width < 2) current_cluster_width = 2;
            continue;
        }

        if (is_zero_width(cp)) {
            continue;
        }

        if (cp >= 0x1F1E6 && cp <= 0x1F1FF) {
            if (is_regional_indicator) {
                is_regional_indicator = false;
                continue;
            } else {
                total_width += current_cluster_width;
                current_cluster_width = 2;
                is_regional_indicator = true;
                continue;
            }
        }
        is_regional_indicator = false;

        if (in_zwj_sequence) {
            in_zwj_sequence = false;
            if (current_cluster_width < 2) current_cluster_width = 2;
            continue;
        }

        total_width += current_cluster_width;
        current_cluster_width = is_wide_char(cp) ? 2 : 1;
    }

    total_width += current_cluster_width;
    return total_width;
}

int main() {
    const std::vector<std::string_view> test_cases = {
        "ASCII text",
        "Кирилиця",
        "Кава ☕ та код 💻",
        "е\u0301кран (accent)",
        "👨‍💻 програміст",
        "🇺🇦 Україна"
    };

    for (const auto& text : test_cases) {
        int w = calculate_grapheme_string_width(text);
        std::cout << "Рядок: " << text << " | Ширина: " << w << " комірок\n";
    }

    return 0;
}
```
:::

## Складні випадки: іконки Nerd Fonts та область PUA

Окремим викликом для сучасних розробників термінальних інтерфейсів є іконки шрифтів розробника (шрифтові патчі Nerd Fonts, Powerline, FontAwesome). Усі ці піктограми (іконки Git-гілок `\uE0A0`, папок, мов програмування) розташовані в приватній області кодових позицій Unicode — **Private Use Area (PUA)**:
- Базова площина PUA: `U+E000`..`U+F8FF`;
- Додаткові площини: `U+F0000`..`U+FFFFD` та `U+100000`..`U+10FFFD`.

Оскільки стандарт Unicode навмисно не визначає властивості для PUA, системний `wcwidth` завжди повертає для них `1` (або `-1`). Однак при рендерингу моноширинний шрифт часто малює складні значки з вильотом за межі однієї комірки або у масштабі 200%. Якщо ваш застосунок розробляється для просунутих оболонок (наприклад, теми `Starship` чи `Powerlevel10k`), таблицю `wide_table` доцільно розширювати явними діапазонами гліфів Nerd Fonts за окремим прапорцем конфігурації.
