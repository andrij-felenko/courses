#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Знайти у рядку значення JSON-ключа виду  "key": "value"  і скопіювати
// value у out (до out_sz-1 символів). Повертає true, якщо ключ знайдено.
// Свідомо вузька реалізація під ПЛАСКІ рядкові поля звіту DRC — не загальний
// парсер JSON (екранованих лапок усередині значень тут не буває).
static bool json_str_field(const char *line, const char *key,
                           char *out, size_t out_sz) {
    char pat[64];
    snprintf(pat, sizeof pat, "\"%s\"", key);   // шукаємо "key"
    const char *k = strstr(line, pat);
    if (!k) return false;
    const char *colon = strchr(k + strlen(pat), ':');
    if (!colon) return false;
    const char *q1 = strchr(colon, '"');        // відкривна лапка значення
    if (!q1) return false;
    const char *q2 = strchr(q1 + 1, '"');       // закривна лапка значення
    if (!q2) return false;
    size_t n = (size_t)(q2 - (q1 + 1));
    if (n >= out_sz) n = out_sz - 1;
    memcpy(out, q1 + 1, n);
    out[n] = '\0';
    return true;
}

// Підрахунок порушень: читаємо звіт построково, для кожного рядка з полем
// "severity" дивимось значення; "error" із потрібного правила — критично.
// Повертає кількість КРИТИЧНИХ порушень keep-out антени.
static int scan_report(FILE *f, const char *rule_name, int *out_all_errors) {
    char line[1024];
    char sev[32], desc[512];
    int ant_crit = 0, all_err = 0;
    while (fgets(line, sizeof line, f)) {
        if (json_str_field(line, "severity", sev, sizeof sev)) {
            if (strcmp(sev, "error") == 0) {
                all_err++;
                // опис порушення KiCad кладе поруч полем "description"
                if (json_str_field(line, "description", desc, sizeof desc)
                    && strstr(desc, rule_name) != NULL)
                    ant_crit++;
            }
        }
    }
    if (out_all_errors) *out_all_errors = all_err;
    return ant_crit;
}
