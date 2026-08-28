typedef enum { CHK_RANGE, CHK_EXACT, CHK_FLAG_OK } check_kind_t;

typedef struct {
    const char   *field;      // ім'я поля в рапорті
    check_kind_t  kind;
    long          lo, hi;      // для CHK_RANGE — коридор; для CHK_EXACT — очікуване в lo
} spec_t;

// Специфікація доброї плати — «паспорт» тесту. Тут живуть усі допуски.
static const spec_t spec[] = {
    { "V33",  CHK_RANGE, 3200, 3400 },   // 3.3 В ±0.1 В
    { "V5",   CHK_RANGE, 4750, 5250 },   // 5 В ±5 %
    { "VREF", CHK_RANGE, 1180, 1220 },   // сама опорна теж має бути в нормі
    { "IMU",  CHK_EXACT, 0x71, 0    },   // підпис давача руху
    { "BARO", CHK_EXACT, 0x60, 0    },   // підпис барометра
    { "TEMP", CHK_RANGE, 150,  650  },   // 15…65 °C: не перегрів, але й не «мертво холодна»
};
#define N_SPEC (sizeof(spec) / sizeof(spec[0]))

typedef struct {
    bool passed;
    char reason[64];        // якщо БРАК — що саме й наскільки не так
} verdict_t;

verdict_t jig_judge(const char *line) {
    verdict_t v = { .passed = true, .reason = "" };

    // 0) ціле й неспотворене?
    if (!report_checksum_ok(line)) {
        v.passed = false;
        snprintf(v.reason, sizeof(v.reason), "checksum/format");
        return v;
    }

    // окремий випадок: плата сама зізналась у переповненні рапорту
    if (strstr(line, "ERR=")) {
        v.passed = false;
        snprintf(v.reason, sizeof(v.reason), "board reported error");
        return v;
    }

    // 1) прапорець GPIO — окремо, бо він рядковий
    char gpio[8];
    if (!field_str(line, "GPIO", gpio, sizeof(gpio)) || strcmp(gpio, "OK") != 0) {
        v.passed = false;
        snprintf(v.reason, sizeof(v.reason), "GPIO loop failed");
        return v;
    }

    // 2) числові поля — по таблиці допусків
    for (unsigned i = 0; i < N_SPEC; i++) {
        long val;
        if (!field_int(line, spec[i].field, &val)) {
            v.passed = false;
            snprintf(v.reason, sizeof(v.reason), "%s: missing", spec[i].field);
            return v;
        }
        bool field_ok;
        switch (spec[i].kind) {
            case CHK_RANGE: field_ok = (val >= spec[i].lo && val <= spec[i].hi); break;
            case CHK_EXACT: field_ok = (val == spec[i].lo);                      break;
            default:        field_ok = true;                                     break;
        }
        if (!field_ok) {
            v.passed = false;
            snprintf(v.reason, sizeof(v.reason),
                     "%s=%ld out of [%ld..%ld]",
                     spec[i].field, val, spec[i].lo, spec[i].hi);
            return v;   // перша ж хиба — вирок БРАК, далі не потрібно
        }
    }

    return v;   // усі поля в нормі → ПРОЙШЛА
}
