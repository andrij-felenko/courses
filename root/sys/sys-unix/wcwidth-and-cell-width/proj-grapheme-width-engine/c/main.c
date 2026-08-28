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
