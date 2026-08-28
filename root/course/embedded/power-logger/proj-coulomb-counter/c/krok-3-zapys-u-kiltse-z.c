#include <string.h>
#include "esp_partition.h"

// Один запис журналу — 12 байтів. Пакуємо щільно, бо розмір прямо диктує знос.
typedef struct __attribute__((packed)) {
    uint32_t seq;        // монотонний лічильник записів: 0,1,2,... — для пошуку голови
    uint32_t epoch_s;    // мітка часу: секунди від старту місії
    uint32_t charge_mC;  // заряд за вікно, мілікулони
} log_rec_t;             // sizeof == 12

_Static_assert(sizeof(log_rec_t) == 12, "запис має бути рівно 12 байтів");
