#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include <math.h>

/* Коди повернення статусу парсера */
typedef enum {
    CAP_PARSE_OK = 0,
    CAP_ERR_EMPTY_STRING,
    CAP_ERR_INVALID_CAPACITANCE,
    CAP_ERR_INVALID_TOLERANCE,
    CAP_ERR_INVALID_VOLTAGE,
    CAP_ERR_INVALID_TEMP_CLASS
} CapParseStatus;

/* Фізичний тип діелектрика */
typedef enum {
    DIELECTRIC_UNKNOWN = 0,
    DIELECTRIC_CLASS_I,    /* C0G / NP0 (параелектрик) */
    DIELECTRIC_CLASS_II,   /* X7R, X5R (сегнетоелектрик BaTiO3) */
    DIELECTRIC_CLASS_III,  /* Y5V, Z5U (високопроникний сегнетоелектрик) */
    DIELECTRIC_ELECTROLYTIC
} DielectricType;

/* Структура повного опису конденсатора */
typedef struct {
    double capacitance_farads; /* Номінал у фарадах (Ф) */
    double capacitance_pf;     /* Номінал у пікофарадах (пФ) */
    char formatted_value[32];  /* Форматований рядок (напр., "100 nF") */
    
    bool is_absolute_tolerance;/* true = у пФ, false = у % */
    double tolerance_plus;     /* Границя допуску в плюс (+% або +пФ) */
    double tolerance_minus;    /* Границя допуску в мінус (-% або -пФ) */
    char tolerance_code;       /* Літерний код допуску (J, K, M, Z тощо) */
    
    double rated_voltage;      /* Номінальна напруга, В */
    char voltage_code[8];      /* Код напруги (напр., "1H", "16V") */
    
    DielectricType dielectric_type;
    char temp_code[8];         /* Код класу (напр., "C0G", "X7R", "Y5V") */
    int temp_min_celsius;      /* Нижня робоча температура, °C */
    int temp_max_celsius;      /* Верхня робоча температура, °C */
    double max_temp_drift_pct; /* Максимальний дрейф ємності ΔC/C, % */

    double nearest_e24_nominal;/* Найближчий номінал ряду E24 */
    double e24_error_pct;      /* Відхилення від ряду E24, % */
} CapacitorSpec;

/* Стандартні мантиси ряду E24 за IEC 60063 */
static const double E24_TABLE[] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};
static const size_t E24_SIZE = sizeof(E24_TABLE) / sizeof(E24_TABLE[0]);

/* Форматування значення ємності з інженерними префіксами */
static void format_capacitance(double pf, char *buf, size_t max_len) {
    if (pf >= 1e6) {
        snprintf(buf, max_len, "%.4g uF", pf / 1e6);
    } else if (pf >= 1e3) {
        snprintf(buf, max_len, "%.4g nF", pf / 1e3);
    } else {
        snprintf(buf, max_len, "%.4g pF", pf);
    }
}

/* Верифікація номіналу за рядом E24 */
static void validate_e_series(CapacitorSpec *spec) {
    if (spec->capacitance_pf <= 0.0) return;

    double exp_val = floor(log10(spec->capacitance_pf));
    double scale = pow(10.0, exp_val);
    double mantissa = spec->capacitance_pf / scale;

    double best_diff = 1e9;
    double best_nominal = E24_TABLE[0];

    for (size_t i = 0; i < E24_SIZE; i++) {
        double diff = fabs(mantissa - E24_TABLE[i]);
        if (diff < best_diff) {
            best_diff = diff;
            best_nominal = E24_TABLE[i];
        }
    }

    spec->nearest_e24_nominal = best_nominal * scale;
    spec->e24_error_pct = (fabs(spec->capacitance_pf - spec->nearest_e24_nominal) / spec->nearest_e24_nominal) * 100.0;
}

/* Синтаксичний аналіз ємності */
static bool parse_cap_value(const char *token, double *out_pf, char *out_tol_char) {
    size_t len = strlen(token);
    if (len == 0) return false;
    *out_tol_char = '\0';

    /* Перевірка суфіксної літери допуску в кінці токена */
    char last = (char)toupper((unsigned char)token[len - 1]);
    size_t num_len = len;
    if (isalpha((unsigned char)last) && last != 'R' && last != 'P' && last != 'N' && last != 'U') {
        *out_tol_char = last;
        num_len = len - 1;
    }

    char num_str[32];
    if (num_len >= sizeof(num_str)) return false;
    strncpy(num_str, token, num_len);
    num_str[num_len] = '\0';

    /* 1. Перевірка на IEC-префікси (4n7, 2u2, 33p, n47, R47, 2R2) */
    char *prefix_pos = NULL;
    char p_char = '\0';
    for (size_t i = 0; i < num_len; i++) {
        char c = (char)tolower((unsigned char)num_str[i]);
        if (c == 'r' || c == 'p' || c == 'n' || c == 'u' || c == 'm') {
            prefix_pos = &num_str[i];
            p_char = c;
            break;
        }
    }

    if (prefix_pos != NULL) {
        double mult_to_pf = 1.0;
        if (p_char == 'r' || p_char == 'p') mult_to_pf = 1.0;
        else if (p_char == 'n') mult_to_pf = 1000.0;
        else if (p_char == 'u') mult_to_pf = 1000000.0;
        else if (p_char == 'm') mult_to_pf = 1000000000.0;

        char before[16] = {0}, after[16] = {0};
        size_t idx = (size_t)(prefix_pos - num_str);
        if (idx > 0) strncpy(before, num_str, idx);
        if (idx + 1 < num_len) strcpy(after, prefix_pos + 1);

        double v_before = (strlen(before) > 0) ? atof(before) : 0.0;
        double v_after = (strlen(after) > 0) ? atof(after) : 0.0;
        
        double fractional = 0.0;
        if (strlen(after) > 0) {
            fractional = v_after / pow(10.0, (double)strlen(after));
        }
        *out_pf = (v_before + fractional) * mult_to_pf;
        return true;
    }

    /* 2. Перевірка на тризначний та чотиризначний цифровий код EIA */
    bool all_digits = true;
    for (size_t i = 0; i < num_len; i++) {
        if (!isdigit((unsigned char)num_str[i])) { all_digits = false; break; }
    }

    if (all_digits) {
        if (num_len == 3) {
            int d1 = num_str[0] - '0';
            int d2 = num_str[1] - '0';
            int d3 = num_str[2] - '0';
            int mantissa = d1 * 10 + d2;
            
            if (d3 <= 6) {
                *out_pf = (double)mantissa * pow(10.0, (double)d3);
            } else if (d3 == 8) {
                *out_pf = (double)mantissa * 0.01;
            } else if (d3 == 9) {
                *out_pf = (double)mantissa * 0.1;
            } else {
                return false;
            }
            return true;
        } else if (num_len == 4) {
            int mantissa = (num_str[0] - '0') * 100 + (num_str[1] - '0') * 10 + (num_str[2] - '0');
            int exp = num_str[3] - '0';
            *out_pf = (double)mantissa * pow(10.0, (double)exp);
            return true;
        } else if (num_len == 1 || num_len == 2) {
            *out_pf = atof(num_str);
            return true;
        }
    }

    return false;
}

/* Декодування літерного допуску IEC 60062 */
static bool apply_tolerance(CapacitorSpec *spec, char code) {
    if (code == '\0') return true;
    spec->tolerance_code = (char)toupper((unsigned char)code);

    if (spec->capacitance_pf < 10.0) {
        spec->is_absolute_tolerance = true;
        switch (spec->tolerance_code) {
            case 'B': spec->tolerance_plus = 0.10; spec->tolerance_minus = 0.10; return true;
            case 'C': spec->tolerance_plus = 0.25; spec->tolerance_minus = 0.25; return true;
            case 'D': spec->tolerance_plus = 0.50; spec->tolerance_minus = 0.50; return true;
            default: break;
        }
    }

    spec->is_absolute_tolerance = false;
    switch (spec->tolerance_code) {
        case 'B': spec->tolerance_plus = 0.1;  spec->tolerance_minus = 0.1;  return true;
        case 'C': spec->tolerance_plus = 0.25; spec->tolerance_minus = 0.25; return true;
        case 'D': spec->tolerance_plus = 0.5;  spec->tolerance_minus = 0.5;  return true;
        case 'F': spec->tolerance_plus = 1.0;  spec->tolerance_minus = 1.0;  return true;
        case 'G': spec->tolerance_plus = 2.0;  spec->tolerance_minus = 2.0;  return true;
        case 'J': spec->tolerance_plus = 5.0;  spec->tolerance_minus = 5.0;  return true;
        case 'K': spec->tolerance_plus = 10.0; spec->tolerance_minus = 10.0; return true;
        case 'M': spec->tolerance_plus = 20.0; spec->tolerance_minus = 20.0; return true;
        case 'Z': spec->tolerance_plus = 80.0; spec->tolerance_minus = 20.0; return true;
        case 'P': spec->tolerance_plus = 100.0;spec->tolerance_minus = 0.0;  return true;
        default: return false;
    }
}

/* Декодування напруги EIA / JIS */
static bool parse_voltage_code(const char *token, double *out_volts) {
    size_t len = strlen(token);
    if (len == 0) return false;

    if (toupper((unsigned char)token[len - 1]) == 'V') {
        char val_str[16];
        if (len - 1 >= sizeof(val_str)) return false;
        strncpy(val_str, token, len - 1);
        val_str[len - 1] = '\0';
        *out_volts = atof(val_str);
        return (*out_volts > 0.0);
    }

    if (len == 2 && isdigit((unsigned char)token[0])) {
        int exp = token[0] - '0';
        char base_code = (char)toupper((unsigned char)token[1]);
        double base_val = 0.0;
        
        switch (base_code) {
            case 'A': base_val = 1.0; break;
            case 'C': base_val = 1.6; break;
            case 'D': base_val = 2.0; break;
            case 'E': base_val = 2.5; break;
            case 'G': base_val = 4.0; break;
            case 'J': base_val = 6.3; break;
            case 'V': base_val = 3.5; break;
            case 'H': base_val = 5.0; break;
            default: return false;
        }
        *out_volts = base_val * pow(10.0, (double)exp);
        return true;
    }

    if (len == 1) {
        char c = token[0];
        switch (c) {
            case 'e': *out_volts = 2.5; return true;
            case 'G': *out_volts = 4.0; return true;
            case 'J': *out_volts = 6.3; return true;
            case 'A': *out_volts = 10.0; return true;
            case 'C': *out_volts = 16.0; return true;
            case 'D': *out_volts = 20.0; return true;
            case 'E': *out_volts = 25.0; return true;
            case 'V': *out_volts = 35.0; return true;
            case 'H': *out_volts = 50.0; return true;
            default: return false;
        }
    }

    return false;
}

/* Декодування температурного класу EIA RS-198 */
static bool parse_temp_class(const char *token, CapacitorSpec *spec) {
    size_t len = strlen(token);
    if (len == 0) return false;

    char up[16];
    if (len >= sizeof(up)) return false;
    for (size_t i = 0; i < len; i++) up[i] = (char)toupper((unsigned char)token[i]);
    up[len] = '\0';

    if (strcmp(up, "C0G") == 0 || strcmp(up, "NP0") == 0) {
        spec->dielectric_type = DIELECTRIC_CLASS_I;
        strcpy(spec->temp_code, "C0G/NP0");
        spec->temp_min_celsius = -55;
        spec->temp_max_celsius = 125;
        spec->max_temp_drift_pct = 0.54;
        return true;
    }

    if (len == 3) {
        char c1 = up[0], c2 = up[1], c3 = up[2];
        int t_min = 0, t_max = 0;
        double drift = 0.0;

        if (c1 == 'X') t_min = -55;
        else if (c1 == 'Y') t_min = -30;
        else if (c1 == 'Z') t_min = 10;
        else return false;

        if (c2 == '4') t_max = 65;
        else if (c2 == '5') t_max = 85;
        else if (c2 == '6') t_max = 105;
        else if (c2 == '7') t_max = 125;
        else if (c2 == '8') t_max = 150;
        else if (c2 == '9') t_max = 200;
        else return false;

        if (c3 == 'P') drift = 10.0;
        else if (c3 == 'R') drift = 15.0;
        else if (c3 == 'S') drift = 22.0;
        else if (c3 == 'U') drift = 56.0;
        else if (c3 == 'V') drift = 82.0;
        else return false;

        spec->dielectric_type = (drift > 22.0) ? DIELECTRIC_CLASS_III : DIELECTRIC_CLASS_II;
        strcpy(spec->temp_code, up);
        spec->temp_min_celsius = t_min;
        spec->temp_max_celsius = t_max;
        spec->max_temp_drift_pct = drift;
        return true;
    }

    return false;
}

/* Головна функція парсингу маркування */
CapParseStatus parse_capacitor_code(const char *input_str, CapacitorSpec *spec) {
    if (input_str == NULL || strlen(input_str) == 0) return CAP_ERR_EMPTY_STRING;
    memset(spec, 0, sizeof(CapacitorSpec));

    char buf[128];
    strncpy(buf, input_str, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';

    char *tokens[8];
    int token_count = 0;
    char *p = strtok(buf, " \t\r\n,");
    while (p != NULL && token_count < 8) {
        tokens[token_count++] = p;
        p = strtok(NULL, " \t\r\n,");
    }

    if (token_count == 0) return CAP_ERR_EMPTY_STRING;

    char tol_char = '\0';
    if (!parse_cap_value(tokens[0], &spec->capacitance_pf, &tol_char)) {
        return CAP_ERR_INVALID_CAPACITANCE;
    }
    spec->capacitance_farads = spec->capacitance_pf * 1e-12;
    format_capacitance(spec->capacitance_pf, spec->formatted_value, sizeof(spec->formatted_value));

    if (tol_char != '\0') {
        apply_tolerance(spec, tol_char);
    }

    for (int i = 1; i < token_count; i++) {
        const char *tok = tokens[i];
        
        if (strlen(tok) == 1 && spec->tolerance_code == '\0' && isalpha((unsigned char)tok[0])) {
            if (apply_tolerance(spec, tok[0])) continue;
        }

        if (spec->temp_code[0] == '\0') {
            if (parse_temp_class(tok, spec)) continue;
        }

        if (spec->rated_voltage == 0.0) {
            double volts = 0.0;
            if (parse_voltage_code(tok, &volts)) {
                spec->rated_voltage = volts;
                strncpy(spec->voltage_code, tok, sizeof(spec->voltage_code) - 1);
                continue;
            }
        }
    }

    validate_e_series(spec);
    return CAP_PARSE_OK;
}

int main(void) {
    const char *test_cases[] = {
        "104K 1H X7R",
        "2R2C 1H C0G",
        "475M 1C X5R",
        "4n7J 2A",
        "R47B 50V",
        "1002F 1E",
        "106 0J"
    };
    int n_tests = (int)(sizeof(test_cases) / sizeof(test_cases[0]));

    for (int i = 0; i < n_tests; i++) {
        CapacitorSpec spec;
        CapParseStatus status = parse_capacitor_code(test_cases[i], &spec);
        if (status == CAP_PARSE_OK) {
            printf("Маркування: %-14s -> Ємність: %-10s (%.2e F)\n",
                   test_cases[i], spec.formatted_value, spec.capacitance_farads);
            if (spec.is_absolute_tolerance) {
                printf("  Допуск: ±%.2f пФ (код %c)\n", spec.tolerance_plus, spec.tolerance_code);
            } else if (spec.tolerance_code != '\0') {
                printf("  Допуск: +%.1f%% / -%.1f%% (код %c)\n",
                       spec.tolerance_plus, spec.tolerance_minus, spec.tolerance_code);
            }
            if (spec.rated_voltage > 0) {
                printf("  Напруга: %.1f В (код %s)\n", spec.rated_voltage, spec.voltage_code);
            }
            if (spec.temp_code[0] != '\0') {
                printf("  Клас: %s (%d°C...+%d°C, max ΔC = ±%.1f%%)\n",
                       spec.temp_code, spec.temp_min_celsius, spec.temp_max_celsius, spec.max_temp_drift_pct);
            }
            printf("  E24-валідація: найближчий %.4g пФ (похибка %.2f%%)\n",
                   spec.nearest_e24_nominal, spec.e24_error_pct);
            printf("----------------------------------------------------------------\n");
        } else {
            printf("Помилка парсингу: %s (код %d)\n", test_cases[i], status);
        }
    }
    return 0;
}
