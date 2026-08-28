#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_LINE_LEN 2048
#define MAX_FIELDS 32
#define MAX_DESIGNATORS 2048
#define MAX_STR_LEN 128

typedef struct {
    char name[MAX_STR_LEN];
    int line_num;
} RefDesEntry;

typedef struct {
    RefDesEntry entries[MAX_DESIGNATORS];
    size_t count;
} RefDesTable;

// Розбір одного рядка CSV з урахуванням лапок
static int parse_csv_line(char *line, char *fields[], int max_f) {
    int count = 0;
    char *p = line;
    bool in_quotes = false;
    char *field_start = p;

    while (*p && count < max_f) {
        if (*p == '"') {
            in_quotes = !in_quotes;
        } else if (*p == ',' && !in_quotes) {
            *p = '\0';
            fields[count++] = field_start;
            field_start = p + 1;
        }
        p++;
    }
    if (count < max_f) {
        // Обрізаємо перенесення рядка
        char *end = p - 1;
        while (end >= field_start && (*end == '\r' || *end == '\n')) {
            *end = '\0';
            end--;
        }
        fields[count++] = field_start;
    }
    return count;
}

// Очищення пробілів і лапок на краях рядка
static void trim(char *s) {
    char *p = s;
    while (isspace((unsigned char)*p) || *p == '"') p++;
    if (p != s) memmove(s, p, strlen(p) + 1);

    size_t len = strlen(s);
    while (len > 0 && (isspace((unsigned char)s[len - 1]) || s[len - 1] == '"')) {
        s[--len] = '\0';
    }
}

// Перевірка синтаксису RefDes: 1-3 великі літери + цифри + опціональна секція
static bool is_valid_refdes(const char *s) {
    if (!s || !*s) return false;
    int letters = 0;
    while (isalpha((unsigned char)*s)) {
        if (!isupper((unsigned char)*s)) return false;
        letters++;
        s++;
    }
    if (letters < 1 || letters > 3) return false;
    if (!isdigit((unsigned char)*s)) return false;
    while (isdigit((unsigned char)*s)) s++;
    // Допускаємо букву секції для багатосекційних ІС (U1A, U1B)
    if (isalpha((unsigned char)*s) && isupper((unsigned char)*s)) s++;
    return *s == '\0';
}

// Перевірка на заборонені заглушки в артикулах
static bool is_dummy_value(const char *s) {
    if (!s || strlen(s) == 0) return true;
    if (strcmp(s, "TBD") == 0 || strcmp(s, "N/A") == 0 ||
        strcmp(s, "TODO") == 0 || strcmp(s, "?") == 0 ||
        strcmp(s, "DNI") == 0 || strcmp(s, "DNP") == 0) {
        return true;
    }
    return false;
}

// Головна процедура аудиту CSV файлу
int validate_bom(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) {
        fprintf(stderr, "Помилка відкриття файлу: %s\n", filename);
        return -1;
    }

    char line[MAX_LINE_LEN];
    char *fields[MAX_FIELDS];
    RefDesTable ref_table = { .count = 0 };
    int line_num = 0;
    int errors_count = 0;
    int warnings_count = 0;

    // Читаємо заголовок
    if (!fgets(line, sizeof(line), f)) {
        fclose(f);
        return -1;
    }
    line_num++;

    printf("=== Початок аудиту BOM: %s ===\n", filename);

    while (fgets(line, sizeof(line), f)) {
        line_num++;
        // Пропускаємо порожні рядки
        if (line[0] == '\r' || line[0] == '\n' || line[0] == '\0') continue;

        int num_fields = parse_csv_line(line, fields, MAX_FIELDS);
        if (num_fields < 5) {
            printf("[ПОМИЛКА] Рядок %d: недостатньо полів (%d)\n", line_num, num_fields);
            errors_count++;
            continue;
        }

        char *raw_designators = fields[0];
        char *raw_qty         = fields[1];
        char *raw_mpn         = fields[2];
        char *raw_mfg         = fields[3];
        char *raw_footprint   = fields[4];
        char *raw_status      = (num_fields > 5) ? fields[5] : "Populate";

        trim(raw_designators);
        trim(raw_qty);
        trim(raw_mpn);
        trim(raw_mfg);
        trim(raw_footprint);
        trim(raw_status);

        bool is_dnp = (strcasecmp(raw_status, "DNP") == 0 ||
                       strcasecmp(raw_status, "DNI") == 0 ||
                       strcasecmp(raw_status, "NF") == 0);

        int expected_qty = atoi(raw_qty);
        int parsed_qty = 0;

        // Розбираємо список позначень
        char des_copy[MAX_LINE_LEN];
        strncpy(des_copy, raw_designators, sizeof(des_copy) - 1);
        des_copy[sizeof(des_copy) - 1] = '\0';

        char *token = strtok(des_copy, ",; ");
        while (token) {
            trim(token);
            if (strlen(token) > 0) {
                parsed_qty++;

                // 1. Перевірка валідності формату позначення
                if (!is_valid_refdes(token)) {
                    printf("[ПОМИЛКА] Рядок %d: неприпустимий синтаксис позначення '%s'\n", line_num, token);
                    errors_count++;
                }

                // 2. Перевірка на глобальні дублікати
                for (size_t i = 0; i < ref_table.count; i++) {
                    if (strcmp(ref_table.entries[i].name, token) == 0) {
                        printf("[ПОМИЛКА] Рядок %d: дублікат позначення '%s' (раніше у рядку %d)\n",
                               line_num, token, ref_table.entries[i].line_num);
                        errors_count++;
                    }
                }

                // Додаємо в таблицю
                if (ref_table.count < MAX_DESIGNATORS) {
                    strncpy(ref_table.entries[ref_table.count].name, token, MAX_STR_LEN - 1);
                    ref_table.entries[ref_table.count].line_num = line_num;
                    ref_table.count++;
                }
            }
            token = strtok(NULL, ",; ");
        }

        // 3. Звірка Qty з фактичною кількістю
        if (parsed_qty != expected_qty) {
            printf("[ПОМИЛКА] Рядок %d: розбіжність Qty! Заявлено %d, перелічено %d (%s)\n",
                   line_num, expected_qty, parsed_qty, raw_designators);
            errors_count++;
        }

        // 4. Перевірка обов'язкових полів для монтованих позицій
        if (!is_dnp) {
            if (is_dummy_value(raw_mpn)) {
                printf("[ПОМИЛКА] Рядок %d: монтована деталь (%s) не має валідного MPN ('%s')\n",
                       line_num, raw_designators, raw_mpn);
                errors_count++;
            }
            if (is_dummy_value(raw_mfg)) {
                printf("[ПОМИЛКА] Рядок %d: монтована деталь (%s) не має виробника ('%s')\n",
                       line_num, raw_designators, raw_mfg);
                errors_count++;
            }
            if (is_dummy_value(raw_footprint)) {
                printf("[ПОМИЛКА] Рядок %d: відсутній посадковий футпрінт для (%s)\n",
                       line_num, raw_designators);
                errors_count++;
            }

            // 5. Евристика суфіксів Tape & Reel для мікросхем
            if (raw_designators[0] == 'U' && strlen(raw_mpn) > 5) {
                // Якщо це чіп, перевіряємо відсутність суфіксів стрічки
                const char *last_two = raw_mpn + strlen(raw_mpn) - 2;
                const char *last_one = raw_mpn + strlen(raw_mpn) - 1;
                if (strcasecmp(last_two, "TR") != 0 && strcasecmp(last_one, "R") != 0) {
                    printf("[ПОПЕРЕДЖЕННЯ] Рядок %d: чіп %s (%s) може не мати суфікса Tape&Reel\n",
                           line_num, raw_designators, raw_mpn);
                    warnings_count++;
                }
            }
        }
    }

    fclose(f);
    printf("=== Результат аудиту: помилок: %d, попереджень: %d ===\n", errors_count, warnings_count);
    return errors_count > 0 ? 1 : 0;
}
