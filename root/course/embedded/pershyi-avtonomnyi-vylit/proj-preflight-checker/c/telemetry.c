#include "telemetry.h"

#include <ctype.h>
#include <errno.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    FLD_U8,
    FLD_U16,
    FLD_I16,
    FLD_F32,
    FLD_BOOL
} FieldKind;

typedef struct {
    const char *name;
    FieldKind   kind;
    size_t      offset;
} FieldDef;

/* Таблиця полів зліпка: ім'я в дампі -> тип і зсув у структурі.
   Одна таблиця замість п'ятнадцяти гілок if — і парсер, і перелік
   обов'язкових полів беруться звідси. */
static const FieldDef FIELDS[] = {
    { "gps_fix_type",     FLD_U8,   offsetof(VehicleTelemetryState, gps_fix_type)     },
    { "gps_satellites",   FLD_U8,   offsetof(VehicleTelemetryState, gps_satellites)   },
    { "gps_hdop",         FLD_F32,  offsetof(VehicleTelemetryState, gps_hdop)         },
    { "ekf_pos_innov",    FLD_F32,  offsetof(VehicleTelemetryState, ekf_pos_innov)    },
    { "ekf_vel_innov",    FLD_F32,  offsetof(VehicleTelemetryState, ekf_vel_innov)    },
    { "ekf_yaw_innov",    FLD_F32,  offsetof(VehicleTelemetryState, ekf_yaw_innov)    },
    { "battery_voltage",  FLD_F32,  offsetof(VehicleTelemetryState, battery_voltage)  },
    { "cell_delta_v",     FLD_F32,  offsetof(VehicleTelemetryState, cell_delta_v)     },
    { "battery_temp_c",   FLD_F32,  offsetof(VehicleTelemetryState, battery_temp_c)   },
    { "geofence_enabled", FLD_BOOL, offsetof(VehicleTelemetryState, geofence_enabled) },
    { "geofence_points",  FLD_U16,  offsetof(VehicleTelemetryState, geofence_points)  },
    { "geofence_action",  FLD_U8,   offsetof(VehicleTelemetryState, geofence_action)  },
    { "rc_rssi_dbm",      FLD_I16,  offsetof(VehicleTelemetryState, rc_rssi_dbm)      },
    { "rc_kill_channel",  FLD_U16,  offsetof(VehicleTelemetryState, rc_kill_channel)  },
    { "acc_vibe_floor",   FLD_F32,  offsetof(VehicleTelemetryState, acc_vibe_floor)   }
};

#define FIELD_COUNT (sizeof FIELDS / sizeof FIELDS[0])

/* Побачені поля тримаємо бітовою маскою — тому полів не більше за 32. */
_Static_assert(FIELD_COUNT <= 32, "маска побачених полів вміщає щонайбільше 32 поля");

static char *trim(char *s)
{
    while (*s != '\0' && isspace((unsigned char)*s)) {
        s++;
    }
    char *end = s + strlen(s);
    while (end > s && isspace((unsigned char)end[-1])) {
        *--end = '\0';
    }
    return s;
}

static bool ieq(const char *a, const char *b)
{
    while (*a != '\0' && *b != '\0') {
        if (tolower((unsigned char)*a) != tolower((unsigned char)*b)) {
            return false;
        }
        a++;
        b++;
    }
    return *a == '\0' && *b == '\0';
}

static int find_field(const char *key)
{
    for (size_t i = 0; i < FIELD_COUNT; i++) {
        if (strcmp(FIELDS[i].name, key) == 0) {
            return (int)i;
        }
    }
    return -1;
}

/* Число мусить бути скінченним: "nan" і "inf" strtod ковтає радо,
   а в передпольотній перевірці саме вони й проходять будь-який поріг. */
static bool parse_number(const char *text, double *out)
{
    errno = 0;
    char *end = NULL;
    double value = strtod(text, &end);
    if (end == text || *end != '\0') {
        return false;
    }
    if (errno == ERANGE || !isfinite(value)) {
        return false;
    }
    *out = value;
    return true;
}

static bool parse_bool(const char *text, bool *out)
{
    static const char *const YES[] = { "true", "1", "yes", "on" };
    static const char *const NO[]  = { "false", "0", "no", "off" };

    for (size_t i = 0; i < sizeof YES / sizeof YES[0]; i++) {
        if (ieq(text, YES[i])) {
            *out = true;
            return true;
        }
    }
    for (size_t i = 0; i < sizeof NO / sizeof NO[0]; i++) {
        if (ieq(text, NO[i])) {
            *out = false;
            return true;
        }
    }
    return false;
}

static bool range_err(char *err, size_t err_len, const FieldDef *f,
                      const char *text, const char *range)
{
    snprintf(err, err_len, "поле '%s': значення '%s' поза діапазоном (%s)",
             f->name, text, range);
    return false;
}

static bool store(VehicleTelemetryState *st, const FieldDef *f, const char *text,
                  char *err, size_t err_len)
{
    unsigned char *base = (unsigned char *)st;

    if (f->kind == FLD_BOOL) {
        bool flag;
        if (!parse_bool(text, &flag)) {
            snprintf(err, err_len, "поле '%s': очікується true/false, отримано '%s'",
                     f->name, text);
            return false;
        }
        *(bool *)(base + f->offset) = flag;
        return true;
    }

    double value;
    if (!parse_number(text, &value)) {
        snprintf(err, err_len, "поле '%s': '%s' не є скінченним числом", f->name, text);
        return false;
    }
    if (f->kind != FLD_F32 && value != floor(value)) {
        snprintf(err, err_len, "поле '%s': очікується ціле число, отримано '%s'",
                 f->name, text);
        return false;
    }

    switch (f->kind) {
    case FLD_U8:
        if (value < 0.0 || value > 255.0) {
            return range_err(err, err_len, f, text, "0..255");
        }
        *(uint8_t *)(base + f->offset) = (uint8_t)value;
        break;
    case FLD_U16:
        if (value < 0.0 || value > 65535.0) {
            return range_err(err, err_len, f, text, "0..65535");
        }
        *(uint16_t *)(base + f->offset) = (uint16_t)value;
        break;
    case FLD_I16:
        if (value < -32768.0 || value > 32767.0) {
            return range_err(err, err_len, f, text, "-32768..32767");
        }
        *(int16_t *)(base + f->offset) = (int16_t)value;
        break;
    case FLD_F32:
        /* Звуження до float не має дати нескінченність */
        if (value < -3.0e38 || value > 3.0e38) {
            return range_err(err, err_len, f, text, "модуль до 3e38");
        }
        *(float *)(base + f->offset) = (float)value;
        break;
    case FLD_BOOL:
        break; /* оброблено вище */
    }
    return true;
}

static void report_missing(uint32_t seen, char *err, size_t err_len)
{
    char list[192];
    size_t missing = 0;

    list[0] = '\0';
    for (size_t i = 0; i < FIELD_COUNT; i++) {
        if ((seen & (1u << i)) != 0u) {
            continue;
        }
        missing++;
        if (missing <= 5) {
            size_t used = strlen(list);
            snprintf(list + used, sizeof list - used, "%s%s",
                     used > 0 ? ", " : "", FIELDS[i].name);
        }
    }
    snprintf(err, err_len, "у зліпку бракує %zu полів: %s%s",
             missing, list, missing > 5 ? ", …" : "");
}

int telemetry_parse(FILE *in, VehicleTelemetryState *out, char *err, size_t err_len)
{
    char line[256];
    uint32_t seen = 0;
    unsigned lineno = 0;

    memset(out, 0, sizeof *out);

    while (fgets(line, sizeof line, in) != NULL) {
        lineno++;

        size_t len = strlen(line);
        if (len + 1 == sizeof line && line[len - 1] != '\n') {
            snprintf(err, err_len, "рядок %u: задовгий (понад %zu символів)",
                     lineno, sizeof line - 2);
            return -1;
        }

        char *hash = strchr(line, '#');
        if (hash != NULL) {
            *hash = '\0';
        }
        char *text = trim(line);
        if (*text == '\0') {
            continue;
        }

        char *eq = strchr(text, '=');
        if (eq == NULL) {
            snprintf(err, err_len, "рядок %u: очікується 'ключ=значення', маємо '%s'",
                     lineno, text);
            return -1;
        }
        *eq = '\0';
        char *key = trim(text);
        char *value = trim(eq + 1);

        int idx = find_field(key);
        if (idx < 0) {
            snprintf(err, err_len, "рядок %u: невідоме поле '%s'", lineno, key);
            return -1;
        }
        if ((seen & (1u << idx)) != 0u) {
            /* Двічі задане поле — ознака склеєних дампів із різних бортів */
            snprintf(err, err_len, "рядок %u: поле '%s' задано двічі", lineno, key);
            return -1;
        }

        char why[160];
        if (!store(out, &FIELDS[idx], value, why, sizeof why)) {
            snprintf(err, err_len, "рядок %u: %s", lineno, why);
            return -1;
        }
        seen |= 1u << idx;
    }

    if (ferror(in)) {
        snprintf(err, err_len, "помилка читання потоку зі зліпком");
        return -1;
    }

    uint32_t full = (FIELD_COUNT == 32) ? 0xFFFFFFFFu : ((1u << FIELD_COUNT) - 1u);
    if (seen != full) {
        report_missing(seen, err, err_len);
        return -1;
    }
    return 0;
}
