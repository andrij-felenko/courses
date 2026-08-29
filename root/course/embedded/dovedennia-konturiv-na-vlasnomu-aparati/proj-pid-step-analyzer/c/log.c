#include "log.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LINE_CAP    256
#define MIN_SAMPLES 32

static int is_number_start(char c)
{
    return (c >= '0' && c <= '9') || c == '-' || c == '+' || c == '.';
}

static int log_push(FlightLog *log, const LogSample *s)
{
    if (log->count == log->cap) {
        size_t cap = log->cap ? log->cap * 2u : 1024u;
        LogSample *grown = realloc(log->s, cap * sizeof *grown);
        if (!grown) {
            return -1;
        }
        log->s = grown;
        log->cap = cap;
    }
    log->s[log->count++] = *s;
    return 0;
}

void flightlog_free(FlightLog *log)
{
    free(log->s);
    log->s = NULL;
    log->count = 0;
    log->cap = 0;
}

int flightlog_load(const char *path, FlightLog *log, char *err, size_t err_size)
{
    static const char *names[4] = { "setpoint", "gyro", "d_term", "vbat" };
    const char *seps = ",;\t\r\n";
    char line[LINE_CAP];
    unsigned long lineno = 0;
    FILE *f;

    memset(log, 0, sizeof *log);

    f = fopen(path, "r");
    if (!f) {
        snprintf(err, err_size, "не вдалося відкрити «%s»: %s", path, strerror(errno));
        return -1;
    }

    while (fgets(line, (int)sizeof line, f)) {
        LogSample s;
        double *fields[4];
        char *tok;
        char *endp;
        char *p = line;
        size_t len = strlen(line);
        int k;

        lineno++;
        if (len + 1 == sizeof line && line[len - 1] != '\n') {
            snprintf(err, err_size, "рядок %lu довший за %d байтів — це не схоже на наш лог",
                     lineno, LINE_CAP - 1);
            goto fail;
        }

        while (*p == ' ' || *p == '\t') {
            p++;
        }
        if (*p == '\0' || *p == '\n' || *p == '\r' || *p == '#') {
            continue;                       /* порожній рядок або коментар */
        }
        if (!is_number_start(*p)) {
            if (log->count == 0) {
                continue;                   /* шапка CSV, а не дані */
            }
            snprintf(err, err_size, "рядок %lu: перше поле не схоже на час", lineno);
            goto fail;
        }

        tok = strtok(p, seps);
        if (!tok) {
            continue;
        }
        errno = 0;
        s.t_us = (uint64_t)strtoull(tok, &endp, 10);
        if (errno != 0 || endp == tok || *endp != '\0') {
            snprintf(err, err_size, "рядок %lu: час «%s» не читається", lineno, tok);
            goto fail;
        }

        fields[0] = &s.setpoint;
        fields[1] = &s.gyro;
        fields[2] = &s.d_term;
        fields[3] = &s.vbat;
        for (k = 0; k < 4; ++k) {
            tok = strtok(NULL, seps);
            if (!tok) {
                snprintf(err, err_size, "рядок %lu: бракує поля %s (чекали п'ять стовпчиків)",
                         lineno, names[k]);
                goto fail;
            }
            errno = 0;
            *fields[k] = strtod(tok, &endp);
            if (endp == tok || errno == ERANGE) {
                snprintf(err, err_size, "рядок %lu: поле %s = «%s» не число", lineno, names[k], tok);
                goto fail;
            }
        }

        /* Час мусить зростати строго: інакше лог склеєно з двох сесій, і всі
           інтервали між сходинками поїдуть. Краще впасти тут, ніж видати
           «затримку» в мінус десять мілісекунд. */
        if (log->count > 0 && s.t_us <= log->s[log->count - 1].t_us) {
            snprintf(err, err_size, "рядок %lu: час %llu не більший за попередній %llu",
                     lineno, (unsigned long long)s.t_us,
                     (unsigned long long)log->s[log->count - 1].t_us);
            goto fail;
        }
        if (log_push(log, &s) != 0) {
            snprintf(err, err_size, "бракує пам'яті на %zu-й відлік", log->count + 1);
            goto fail;
        }
    }

    if (ferror(f)) {
        snprintf(err, err_size, "помилка читання «%s»: %s", path, strerror(errno));
        goto fail;
    }
    if (log->count < MIN_SAMPLES) {
        snprintf(err, err_size, "у лозі лише %zu відліків, потрібно щонайменше %d",
                 log->count, MIN_SAMPLES);
        goto fail;
    }

    fclose(f);
    return 0;

fail:
    fclose(f);
    flightlog_free(log);
    return -1;
}

double flightlog_mean_dt_us(const FlightLog *log)
{
    if (log->count < 2) {
        return 0.0;
    }
    return (double)(log->s[log->count - 1].t_us - log->s[0].t_us) / (double)(log->count - 1);
}
