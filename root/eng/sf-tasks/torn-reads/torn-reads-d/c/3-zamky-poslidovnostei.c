#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t sequence;
    uint64_t x;
    uint64_t y;
    uint64_t z;
} telemetry_record_t;

void read_telemetry(const volatile telemetry_record_t *src, telemetry_record_t *dst) {
    uint32_t seq;
    do {
        seq = src->sequence;
        while (seq & 1) { // Непарний лічильник — триває запис
            seq = src->sequence;
        }
        dst->x = src->x;
        dst->y = src->y;
        dst->z = src->z;
    } while (src->sequence != seq);
}
