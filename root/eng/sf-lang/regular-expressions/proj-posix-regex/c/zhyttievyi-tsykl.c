#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>

#define MAX_GROUPS 4

void parse_log_line(const char *pattern, const char *line) {
    regex_t regex;
    regmatch_t matches[MAX_GROUPS];
    char err_buf[256];

    /* Компіляція розширеного регулярного виразу (ERE) */
    int ret = regcomp(&regex, pattern, REG_EXTENDED);
    if (ret != 0) {
        regerror(ret, &regex, err_buf, sizeof(err_buf));
        fprintf(stderr, "Помилка компіляції виразу: %s\n", err_buf);
        return;
    }

    /* Виконання зіставлення з вхідним рядком */
    ret = regexec(&regex, line, MAX_GROUPS, matches, 0);
    if (ret == 0) {
        printf("Збіг знайдено для рядка: %s\n", line);
        for (int i = 0; i < MAX_GROUPS; i++) {
            if (matches[i].rm_so == -1) {
                printf("  Група %d: [не брала участі у збігу]\n", i);
                continue;
            }
            int len = matches[i].rm_eo - matches[i].rm_so;
            printf("  Група %d: %.*s (байти %d..%d)\n",
                   i, len, line + matches[i].rm_so,
                   (int)matches[i].rm_so, (int)matches[i].rm_eo);
        }
    } else if (ret == REG_NOMATCH) {
        printf("Збігу немає для рядка: %s\n", line);
    } else {
        regerror(ret, &regex, err_buf, sizeof(err_buf));
        fprintf(stderr, "Помилка виконання regexec: %s\n", err_buf);
    }

    /* Обов'язкове звільнення внутрішніх таблиць автомата */
    regfree(&regex);
}

int main(void) {
    const char *pattern = "^([A-Z]+) \\[([0-9]{4}-[0-9]{2}-[0-9]{2})\\] (.+)$";
    const char *log1 = "ERROR [2026-08-26] Disk array degraded on node-04";
    const char *log2 = "invalid line format";

    parse_log_line(pattern, log1);
    parse_log_line(pattern, log2);
    return 0;
}
