#include <stdint.h>
#include <stdbool.h>

#define T_POLL_MS   1000        // застосовувати правило раз на 1 с

static uint32_t t_last_poll = 0;

// Викликається на КОЖНІЙ ітерації loop(), але тіло спрацьовує раз на T_POLL_MS.
static void control_step(uint32_t now) {
    if (now - t_last_poll < T_POLL_MS) return;   // ще не час — виходимо миттєво
    t_last_poll = now;

    float t = sensor_read_celsius();
    // ... тут буде правило регулювання ...
}
