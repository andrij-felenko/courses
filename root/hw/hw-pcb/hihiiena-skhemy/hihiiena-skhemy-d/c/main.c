#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

// Структура валідації атрибутів компонента
typedef struct {
    char refdes[16];
    char value_raw[32];
    double value_numeric;
    double voltage_rating;
    bool has_voltage;
    bool is_dnp;
    bool valid_format;
} ComponentAttr;

// Парсинг інженерного формату IEC 60062 (наприклад: "4k7", "0R22", "100n", "2u2")
bool parse_engineering_value(const char *raw, double *out_val) {
    if (!raw || *raw == '\0') return false;
    
    char clean[32];
    size_t len = 0;
    char unit_char = '\0';
    int unit_idx = -1;

    for (size_t i = 0; raw[i] != '\0' && len < sizeof(clean) - 1; ++i) {
        char c = raw[i];
        if (isdigit((unsigned char)c) || c == '.') {
            clean[len++] = c;
        } else if (strchr("RKMGTpnumk", c) && unit_char == '\0') {
            unit_char = c;
            unit_idx = (int)len;
            clean[len++] = '.'; // Замінюємо літеру на крапку
        }
    }
    clean[len] = '\0';

    if (len == 0) return false;

    // Множники
    double multiplier = 1.0;
    switch (unit_char) {
        case 'p': multiplier = 1e-12; break;
        case 'n': multiplier = 1e-9;  break;
        case 'u': multiplier = 1e-6;  break;
        case 'm': multiplier = 1e-3;  break;
        case 'R': multiplier = 1.0;   break;
        case 'k':
        case 'K': multiplier = 1e3;   break;
        case 'M': multiplier = 1e6;   break;
        case 'G': multiplier = 1e9;   break;
        default:  multiplier = 1.0;   break;
    }

    // Якщо множник був на початку (наприклад: "R22" або "u1")
    char *endptr = NULL;
    double base = strtod(clean, &endptr);
    if (endptr == clean && unit_idx == 0) {
        base = strtod(clean + 1, &endptr);
    }

    *out_val = base * multiplier;
    return true;
}

// Перевірка гігієни компонента
bool validate_component(ComponentAttr *comp) {
    comp->valid_format = parse_engineering_value(comp->value_raw, &comp->value_numeric);
    
    // Перевірка 1: Конденсатор повинен мати робочу напругу
    if (comp->refdes[0] == 'C' && !comp->is_dnp) {
        if (!comp->has_voltage || comp->voltage_rating <= 0.0) {
            printf("[ПОПЕРЕДЖЕННЯ] %s: Конденсатор %s не має робочої напруги!\n",
                   comp->refdes, comp->value_raw);
            return false;
        }
    }
    
    // Перевірка 2: Наявність небезпечної крапки в Value (наприклад "4.7k" замість "4k7")
    if (strchr(comp->value_raw, '.') != NULL) {
        printf("[ЗАСТЕРЕЖЕННЯ] %s: Номінал '%s' містить крапку. Рекомендовано IEC-формат.\n",
               comp->refdes, comp->value_raw);
    }

    return comp->valid_format;
}
