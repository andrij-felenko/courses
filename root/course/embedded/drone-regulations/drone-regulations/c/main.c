#include <stdint.h>
#include <string.h>

// Спрощений кадр дистанційної ідентифікації, що йде в ефір.
typedef struct {
    uint8_t  msg_type;      // тип повідомлення (тут: базова ідентифікація)
    char     uas_id[20];    // реєстраційний рядок оператора (наноситься й мовиться)
    int32_t  lat_1e7;       // широта апарата, градуси × 1e7 (цілочисельно)
    int32_t  lon_1e7;       // довгота апарата
    int16_t  alt_m;         // висота над рівнем моря, метри
    int32_t  pilot_lat_1e7; // широта пілота (звідки керують)
    int32_t  pilot_lon_1e7; // довгота пілота
} rid_frame_t;

// Складання кадру з поточних даних навігації.
// pos — свіжі координати апарата, home — місце пілота (точка зльоту).
void rid_fill(rid_frame_t *f, const char *operator_id,
              const gps_fix_t *pos, const gps_fix_t *home) {
    f->msg_type = 0x00;                       // 0x00 — базова ідентифікація
    memset(f->uas_id, 0, sizeof(f->uas_id));  // очистити «хвіст» рядка
    strncpy(f->uas_id, operator_id, sizeof(f->uas_id) - 1);  // -1: лишити місце під '\0'

    f->lat_1e7 = (int32_t)(pos->lat_deg  * 1e7);   // градуси → цілі, щоб не тягти float в ефір
    f->lon_1e7 = (int32_t)(pos->lon_deg  * 1e7);
    f->alt_m   = (int16_t)(pos->alt_m + 0.5f);     // округлення до метра

    f->pilot_lat_1e7 = (int32_t)(home->lat_deg * 1e7);
    f->pilot_lon_1e7 = (int32_t)(home->lon_deg * 1e7);
}
