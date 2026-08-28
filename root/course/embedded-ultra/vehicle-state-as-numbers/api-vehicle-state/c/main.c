#include <stdint.h>
#include <stdbool.h>

typedef struct {
    volatile uint32_t sequence;
    vehicle_state_t   state;
} seqlock_vehicle_state_t;

// Читання стану у фоновому потоці телеметрії
bool vehicle_state_read_atomic(const seqlock_vehicle_state_t *seq, vehicle_state_t *out) {
    uint32_t s1, s2;
    uint32_t retries = 0;
    do {
        s1 = seq->sequence;
        if (s1 & 1) { // Запис у процесі (непарне число)
            continue;
        }
        *out = seq->state;
        s2 = seq->sequence;
        retries++;
        if (retries > 10) return false;
    } while (s1 != s2 || (s1 & 1));
    return true;
}
