#include <stdint.h>
#include <string.h>
#include <math.h>

#define ODID_MSG_SIZE   25       // повідомлення завжди рівно 25 байтів
#define ODID_ID_LEN     20       // максимум символів ідентифікатора
#define ODID_PACK_MAX    9       // максимум повідомлень в одному пакеті

// Типи повідомлень (старший півбайт першого байта повідомлення).
enum {
    MSG_BASIC_ID = 0x0,
    MSG_LOCATION = 0x1,
    MSG_OPERATOR = 0x5,
    MSG_PACK     = 0xF,
};

// Свіжий фікс від навігації — те, що дає GPS-парсер.
// Прапорець valid каже, чи можна вірити координатам ЦІЄЇ миті.
typedef struct {
    int      valid;       // 0 — фіксу нема (координатам не вірити)
    double   lat_deg;     // широта, градуси
    double   lon_deg;     // довгота, градуси
    float    alt_m;       // висота над рівнем моря, метри
    uint32_t fix_age_ms;  // вік фіксу НА МИТЬ парсингу; парсер його зафіксував і не рухає
} gps_fix_t;

// --- Кодувальники окремих полів (уся хитрість стандарту — тут) ---

// Градуси → ціле int32 (градуси × 10⁷). Один множник, жодного float в ефір.
static int32_t enc_deg(double deg) {
    return (int32_t)lround(deg * 1e7);   // lround — чесне округлення, не зріз
}

// Висота → uint16 за формулою стандарту: (h + 1000) / 0.5, з обрізанням меж.
static uint16_t enc_alt(float alt_m) {
    float raw = (alt_m + 1000.0f) / 0.5f;
    if (raw < 0)       raw = 0;          // нижче -1000 м — у нуль (позначка «дуже низько»)
    if (raw > 65535.0f) raw = 65535.0f;  // не даємо переповнити uint16
    return (uint16_t)(raw + 0.5f);       // +0.5 — округлення до найближчого
}
