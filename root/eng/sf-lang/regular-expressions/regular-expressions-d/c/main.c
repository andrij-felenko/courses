#include <stdio.h>
#include <stdlib.h>
#include <regex.h>

#define MAX_MATCHES 3

int validate_identifier(const char *text) {
    regex_t regex;
    regmatch_t matches[MAX_MATCHES];
    char err_buf[128];

    /* Компіляція виразу ERE з ігноруванням регістру */
    int ret = regcomp(&regex, "^([a-zA-Z_][a-zA-Z0-9_]*)=([0-9]+)$", REG_EXTENDED | REG_ICASE);
    if (ret != 0) {
        regerror(ret, &regex, err_buf, sizeof(err_buf));
        fprintf(stderr, "Помилка компіляції: %s\n", err_buf);
        return -1;
    }

    /* Зіставлення з рядком */
    ret = regexec(&regex, text, MAX_MATCHES, matches, 0);
    if (ret == 0) {
        printf("Збіг успішний для \"%s\":\n", text);
        for (int i = 0; i < MAX_MATCHES; i++) {
            if (matches[i].rm_so == -1) continue;
            int len = matches[i].rm_eo - matches[i].rm_so;
            printf("  Група %d: %.*s\n", i, len, text + matches[i].rm_so);
        }
    } else if (ret == REG_NOMATCH) {
        printf("Рядок \"%s\" не відповідає формату.\n", text);
    }

    /* Обов'язкове вивільнення ресурсів */
    regfree(&regex);
    return ret == 0;
}

int main(void) {
    validate_identifier("timeout_ms=5000");
    validate_identifier("123_bad_name=10");
    return 0;
}
