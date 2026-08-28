#include <stdint.h>
#include <string.h>

// Безпечне пакування аргументів події: uint8_t (сенсор) + float (відхилення)
void pack_event_args(uint8_t *dest_buf, uint8_t sensor_id, float deviation) {
    // Зсув 0: запис 1 байта
    dest_buf[0] = sensor_id;
    // Зсув 1: копіювання 4 байтів float у форматі little-endian
    memcpy(&dest_buf[1], &deviation, sizeof(float));
}

// Безпечне розпакування аргументів із сирого буфера
void unpack_event_args(const uint8_t *src_buf, uint8_t *out_sensor_id, float *out_deviation) {
    *out_sensor_id = src_buf[0];
    memcpy(out_deviation, &src_buf[1], sizeof(float));
}
