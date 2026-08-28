#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>

/* Структура для збереження зрізів знайдених полів без копіювання байтів */
typedef struct {
    const char *ts_val;
    size_t ts_len;
    const char *path_val;
    size_t path_len;
    long status_code;
    double latency_val;
    bool has_status;
    bool has_latency;
} log_record_t;

/* Простий і швидкий пошук поля JSON першого рівня в рядку */
static bool parse_log_line(char *line, size_t len, log_record_t *rec) {
    memset(rec, 0, sizeof(*rec));
    char *p = line;
    char *end = line + len;

    while (p < end) {
        /* Шукаємо початок ключа */
        if (*p != '"') { p++; continue; }
        p++;
        char *key_start = p;
        while (p < end && *p != '"') p++;
        if (p >= end) break;
        size_t key_len = p - key_start;
        p++; /* Пропускаємо закриваючу лапку ключа */

        /* Шукаємо двокрапку */
        while (p < end && (*p == ' ' || *p == '\t' || *p == ':')) {
            if (*p == ':') { p++; break; }
            p++;
        }
        while (p < end && (*p == ' ' || *p == '\t')) p++;
        if (p >= end) break;

        /* Розбираємо значення залежно від ключа */
        if (key_len == 9 && strncmp(key_start, "timestamp", 9) == 0) {
            if (*p == '"') {
                p++;
                rec->ts_val = p;
                while (p < end && *p != '"') p++;
                rec->ts_len = p - rec->ts_val;
                if (p < end) p++;
            }
        } else if (key_len == 4 && strncmp(key_start, "path", 4) == 0) {
            if (*p == '"') {
                p++;
                rec->path_val = p;
                while (p < end && *p != '"') p++;
                rec->path_len = p - rec->path_val;
                if (p < end) p++;
            }
        } else if (key_len == 6 && strncmp(key_start, "status", 6) == 0) {
            char *val_end;
            rec->status_code = strtol(p, &val_end, 10);
            rec->has_status = (val_end > p);
            p = val_end;
        } else if (key_len == 10 && strncmp(key_start, "latency_ms", 10) == 0) {
            char *val_end;
            rec->latency_val = strtod(p, &val_end);
            rec->has_latency = (val_end > p);
            p = val_end;
        } else {
            /* Пропускаємо невідоме значення */
            if (*p == '"') {
                p++;
                while (p < end && *p != '"') {
                    if (*p == '\\' && p + 1 < end) p++;
                    p++;
                }
                if (p < end) p++;
            } else {
                while (p < end && *p != ',' && *p != '}' && *p != '\n') p++;
            }
        }
    }

    return (rec->ts_val && rec->path_val && rec->has_status && rec->has_latency);
}

int main(void) {
    char *line_buf = NULL;
    size_t line_cap = 0;
    ssize_t nread;
    log_record_t rec;

    /* Вимикаємо блокову буферизацію для швидкої реакції в конвеєрі */
    setvbuf(stdout, NULL, _IOLBF, 0);

    while ((nread = getline(&line_buf, &line_cap, stdin)) != -1) {
        /* Відкидаємо завершальний символ переходу рядка */
        if (nread > 0 && line_buf[nread - 1] == '\n') {
            line_buf[nread - 1] = '\0';
            nread--;
        }
        if (nread == 0) continue;

        if (!parse_log_line(line_buf, (size_t)nread, &rec)) {
            fprintf(stderr, "[WARN] Некоректний запис ndjson: %s\n", line_buf);
            continue;
        }

        /* Критерій фільтрації: серверна помилка або висока затримка */
        if (rec.status_code >= 500 || rec.latency_val > 1000.0) {
            int ret = printf("{\"ts\":\"%.*s\",\"endpoint\":\"%.*s\",\"err\":%ld,\"dur\":%.2f}\n",
                             (int)rec.ts_len, rec.ts_val,
                             (int)rec.path_len, rec.path_val,
                             rec.status_code, rec.latency_val);
            if (ret < 0) {
                if (errno == EPIPE) {
                    /* Наступна ланка конвеєра закрила дескриптор читання */
                    break;
                }
            }
        }
    }

    free(line_buf);
    return 0;
}
