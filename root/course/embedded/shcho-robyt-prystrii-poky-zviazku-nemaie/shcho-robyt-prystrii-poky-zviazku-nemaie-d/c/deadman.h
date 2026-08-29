#ifndef DEADMAN_H
#define DEADMAN_H

#include <stdbool.h>
#include <stdint.h>

// Таймер мертвої руки. На відміну від системного сторожа, його скидає
// ВИКЛЮЧНО успішно декодований і автентифікований кадр, а не справний
// головний цикл. Поки дозвіл дійсний, service() тактує апаратний interlock;
// щойно дедлайн минув — імпульси припиняються, і залізо гасить каскад саме.
typedef struct {
    uint32_t timeout_ms;
    uint32_t heartbeat_ms;
    uint32_t deadline_ms;
    uint32_t last_pulse_ms;
    uint32_t trips;          // скільки разів дозвіл протухав
    bool     tripped;
} deadman_t;

void deadman_init(deadman_t *d, uint32_t timeout_ms, uint32_t heartbeat_ms, uint32_t now);
void deadman_feed(deadman_t *d, uint32_t now);
bool deadman_expired(const deadman_t *d, uint32_t now);
uint32_t deadman_remaining_ms(const deadman_t *d, uint32_t now);
void deadman_service(deadman_t *d, uint32_t now);

#endif /* DEADMAN_H */
