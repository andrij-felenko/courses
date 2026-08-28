#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <regex.h>
#include <stdbool.h>

static char *trim_whitespace(char *str) {
    while (isspace((unsigned char)*str)) str++;
    if (*str == 0) return str;
    char *end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return str;
}

static bool validate_ipv4(const char *ip_str) {
    int o1, o2, o3, o4;
    char extra;
    if (sscanf(ip_str, "%d.%d.%d.%d%c", &o1, &o2, &o3, &o4, &extra) != 4) {
        return false;
    }
    return (o1 >= 0 && o1 <= 255) &&
           (o2 >= 0 && o2 <= 255) &&
           (o3 >= 0 && o3 <= 255) &&
           (o4 >= 0 && o4 <= 255);
}

int main(int argc, char *argv[]) {
    const char *filepath = (argc > 1) ? argv[1] : "/dev/stdin";
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        perror("fopen");
        return 1;
    }

    regex_t name_regex;
    if (regcomp(&name_regex, "^[a-zA-Z0-9_-]+$", REG_EXTENDED | REG_NOSUB) != 0) {
        fprintf(stderr, "Помилка компіляції регулярного виразу\n");
        fclose(fp);
        return 1;
    }

    char *line = NULL;
    size_t len = 0;
    ssize_t nread;
    int total = 0, valid = 0, invalid = 0;

    /* getline автоматично виділяє пам'ять та зчитує рядок до \n або EOF */
    while ((nread = getline(&line, &len, fp)) != -1) {
        /* Видалення завершального переходу рядка */
        if (nread > 0 && line[nread - 1] == '\n') {
            line[nread - 1] = '\0';
        }

        char *trimmed = trim_whitespace(line);
        if (*trimmed == '\0' || *trimmed == '#') {
            continue;
        }

        total++;

        /* Розбиття на поля за двокрапкою за допомогою безпечної функції strtok_r */
        char *saveptr;
        char *name_token   = strtok_r(trimmed, ":", &saveptr);
        char *ip_token     = strtok_r(NULL, ":", &saveptr);
        char *port_token   = strtok_r(NULL, ":", &saveptr);
        char *status_token = strtok_r(NULL, ":", &saveptr);

        if (!name_token || !ip_token || !port_token || !status_token) {
            invalid++;
            fprintf(stderr, "[ПОМИЛКА] Неповний запис: '%s'\n", line);
            continue;
        }

        char *name   = trim_whitespace(name_token);
        char *ip     = trim_whitespace(ip_token);
        char *port_s = trim_whitespace(port_token);
        char *status = trim_whitespace(status_token);

        bool is_valid = true;

        /* Перевірка імені через POSIX regex */
        if (regexec(&name_regex, name, 0, NULL, 0) != 0) is_valid = false;

        /* Перевірка октетів IP-адреси */
        if (!validate_ipv4(ip)) is_valid = false;

        /* Перевірка діапазону порту */
        int port = atoi(port_s);
        if (port < 1 || port > 65535) is_valid = false;

        /* Перевірка дозволених статусів */
        if (strcmp(status, "ENABLED") != 0 &&
            strcmp(status, "DISABLED") != 0 &&
            strcmp(status, "MAINTENANCE") != 0) {
            is_valid = false;
        }

        if (is_valid) {
            valid++;
            printf("[OK] Сервіс: %-15s | Адреса: %-15s:%-5d | Стан: %s\n",
                   name, ip, port, status);
        } else {
            invalid++;
            fprintf(stderr, "[ПОМИЛКА] Невалідні дані: '%s'\n", line);
        }
    }

    free(line);
    regfree(&name_regex);
    fclose(fp);

    printf("\n=== Підсумок обробки ===\n");
    printf("Усього: %d, Валідних: %d, Невалідних: %d\n", total, valid, invalid);
    return 0;
}
