#include <stdio.h>
#include <stdlib.h>
#include <regex.h>
#include <string.h>

int match_line_posix(const char *pattern, const char *text) {
    regex_t regex;
    int ret;

    /* Компіляція розширеного регулярного виразу (ERE) */
    ret = regcomp(&regex, pattern, REG_EXTENDED | REG_NOSUB);
    if (ret != 0) {
        char err_buf[256];
        regerror(ret, &regex, err_buf, sizeof(err_buf));
        fprintf(stderr, "Помилка компіляції виразу: %s\n", err_buf);
        return -1;
    }

    /* Зіставлення тексту */
    ret = regexec(&regex, text, 0, NULL, 0);
    regfree(&regex);

    return (ret == 0) ? 1 : 0;
}

int main(void) {
    const char *pattern = "^[0-9]{4}-[0-9]{2}-[0-9]{2}";
    const char *line = "2026-08-25 [INFO] Сервіс запущено";

    int res = match_line_posix(pattern, line);
    if (res == 1) {
        printf("Знайдено дату на початку рядка\n");
    }
    return 0;
}
