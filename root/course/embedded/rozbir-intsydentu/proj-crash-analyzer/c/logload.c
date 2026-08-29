#include "crashlog.h"

#include <errno.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LINE_BUF 4096
#define MAX_COLS 128

/* Порядок полів у таблиці колонок. */
enum {
    F_TS = 0, F_ROLL_DES, F_ROLL, F_YAW_DES, F_YAW,
    F_M0, F_M1, F_M2, F_M3,
    F_VOLT, F_CURR, F_MAG, F_GYRO, F_STATUS,
    F_COUNT
};

typedef struct {
    const char *name;
    bool required;
} ColumnSpec;

static const ColumnSpec kColumns[F_COUNT] = {
    { "timestamp_us", true },
    { "roll_des",     true },
    { "roll",         true },
    { "yaw_des",      true },
    { "yaw",          true },
    { "mot0",         true },
    { "mot1",         true },
    { "mot2",         true },
    { "mot3",         true },
    { "bat_v",        true },
    { "bat_a",        true },
    { "mag_innov",    true },
    { "gyro_x",       true },
    /* Маски здоров'я в старих записах DataFlash немає — вважаємо IMU справним. */
    { "imu_status",   false }
};

static LoadStatus status_ok(void)
{
    LoadStatus s;
    s.ok = true;
    s.line = 0;
    s.message[0] = '\0';
    return s;
}

static LoadStatus status_fail(size_t line, const char *fmt, ...)
{
    LoadStatus s;
    va_list ap;
    s.ok = false;
    s.line = line;
    va_start(ap, fmt);
    vsnprintf(s.message, sizeof s.message, fmt, ap);
    va_end(ap);
    return s;
}

static char *trim(char *s)
{
    while (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n') {
        s++;
    }
    char *end = s + strlen(s);
    while (end > s && (end[-1] == ' ' || end[-1] == '\t' ||
                       end[-1] == '\r' || end[-1] == '\n')) {
        *--end = '\0';
    }
    return s;
}

/* Ріже рядок на місці: після виклику tok[i] — окремі нуль-термінальні рядки. */
static size_t split_line(char *line, char *tok[], size_t max)
{
    size_t n = 0;
    char *p = line;
    while (n < max) {
        tok[n++] = p;
        char *comma = strchr(p, ',');
        if (comma == NULL) {
            break;
        }
        *comma = '\0';
        p = comma + 1;
    }
    for (size_t i = 0; i < n; i++) {
        tok[i] = trim(tok[i]);
    }
    return n;
}

static bool parse_float(const char *tok, float *out)
{
    if (*tok == '\0') {
        *out = NAN; /* порожня клітинка — кадр просто не судитимемо */
        return true;
    }
    char *end = NULL;
    errno = 0;
    float v = strtof(tok, &end);
    if (end == tok || *end != '\0' || errno == ERANGE) {
        return false;
    }
    *out = v;
    return true;
}

static bool parse_u64(const char *tok, uint64_t *out)
{
    if (*tok == '\0') {
        return false;
    }
    char *end = NULL;
    errno = 0;
    unsigned long long v = strtoull(tok, &end, 10);
    if (end == tok || *end != '\0' || errno == ERANGE) {
        return false;
    }
    *out = (uint64_t)v;
    return true;
}

static bool log_reserve(FrameLog *log)
{
    if (log->count < log->capacity) {
        return true;
    }
    size_t cap = log->capacity ? log->capacity * 2 : 1024;
    TelemetryFrame *p = realloc(log->frames, cap * sizeof *p);
    if (p == NULL) {
        return false;
    }
    log->frames = p;
    log->capacity = cap;
    return true;
}

/* Кладе значення колонки field у відповідне поле кадру. */
static void assign_field(TelemetryFrame *f, int field, float v)
{
    switch (field) {
    case F_ROLL_DES: f->roll_des_deg = v; break;
    case F_ROLL:     f->roll_act_deg = v; break;
    case F_YAW_DES:  f->yaw_des_deg = v; break;
    case F_YAW:      f->yaw_act_deg = v; break;
    case F_M0:       f->motor_out[0] = v; break;
    case F_M1:       f->motor_out[1] = v; break;
    case F_M2:       f->motor_out[2] = v; break;
    case F_M3:       f->motor_out[3] = v; break;
    case F_VOLT:     f->bat_voltage_v = v; break;
    case F_CURR:     f->bat_current_a = v; break;
    case F_MAG:      f->ekf_mag_innov = v; break;
    case F_GYRO:     f->gyro_x_rads = v; break;
    /* Порожня клітинка маски дає NaN — тоді лишаємо усталене «IMU справний». */
    case F_STATUS:   f->sensor_status_mask = isfinite(v) ? (uint32_t)v : 0x01u; break;
    default:         break;
    }
}

LoadStatus log_load_csv(const char *path, FrameLog *out)
{
    memset(out, 0, sizeof *out);

    FILE *fp = fopen(path, "r");
    if (fp == NULL) {
        return status_fail(0, "не вдалося відкрити '%s': %s", path, strerror(errno));
    }

    char line[LINE_BUF];
    char *tok[MAX_COLS];
    int map[MAX_COLS];       /* колонка CSV -> індекс поля, -1 якщо чужа */
    size_t ncols = 0;
    bool header_done = false;
    size_t lineno = 0;

    while (fgets(line, sizeof line, fp) != NULL) {
        lineno++;
        if (strchr(line, '\n') == NULL && !feof(fp)) {
            fclose(fp);
            log_free(out);
            return status_fail(lineno, "рядок довший за %d байтів", LINE_BUF - 1);
        }

        char *body = trim(line);
        if (*body == '\0' || *body == '#') {
            continue;
        }

        if (!header_done) {
            ncols = split_line(body, tok, MAX_COLS);
            bool seen[F_COUNT] = { false };
            for (size_t c = 0; c < ncols; c++) {
                map[c] = -1;
                for (int fidx = 0; fidx < F_COUNT; fidx++) {
                    if (strcmp(tok[c], kColumns[fidx].name) == 0) {
                        map[c] = fidx;
                        seen[fidx] = true;
                        break;
                    }
                }
            }
            for (int fidx = 0; fidx < F_COUNT; fidx++) {
                if (kColumns[fidx].required && !seen[fidx]) {
                    fclose(fp);
                    return status_fail(lineno, "у шапці немає обов'язкової колонки '%s'",
                                       kColumns[fidx].name);
                }
            }
            header_done = true;
            continue;
        }

        size_t got = split_line(body, tok, MAX_COLS);
        if (got != ncols) {
            fclose(fp);
            log_free(out);
            return status_fail(lineno, "колонок %zu, а в шапці %zu", got, ncols);
        }

        if (!log_reserve(out)) {
            fclose(fp);
            log_free(out);
            return status_fail(lineno, "бракує пам'яті на %zu-й кадр", out->count + 1);
        }

        TelemetryFrame *f = &out->frames[out->count];
        memset(f, 0, sizeof *f);
        f->sensor_status_mask = 0x01u; /* немає колонки — вважаємо IMU справним */

        for (size_t c = 0; c < ncols; c++) {
            int fidx = map[c];
            if (fidx < 0) {
                continue;
            }
            if (fidx == F_TS) {
                if (!parse_u64(tok[c], &f->timestamp_us)) {
                    fclose(fp);
                    log_free(out);
                    return status_fail(lineno, "нечитабельна мітка часу '%s'", tok[c]);
                }
            } else {
                float v = 0.0f;
                if (!parse_float(tok[c], &v)) {
                    fclose(fp);
                    log_free(out);
                    return status_fail(lineno, "нечитабельне число '%s' у колонці '%s'",
                                       tok[c], kColumns[fidx].name);
                }
                assign_field(f, fidx, v);
            }
        }
        out->count++;
    }

    if (ferror(fp)) {
        fclose(fp);
        log_free(out);
        return status_fail(lineno, "помилка читання: %s", strerror(errno));
    }
    fclose(fp);

    if (!header_done) {
        return status_fail(0, "файл порожній: немає навіть шапки з іменами колонок");
    }
    return status_ok();
}

void log_free(FrameLog *log)
{
    free(log->frames);
    log->frames = NULL;
    log->count = 0;
    log->capacity = 0;
}
