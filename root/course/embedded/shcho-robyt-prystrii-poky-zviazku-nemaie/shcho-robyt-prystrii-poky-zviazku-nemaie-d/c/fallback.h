#ifndef FALLBACK_H
#define FALLBACK_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "deadman.h"
#include "link.h"
#include "logstore.h"
#include "timebase.h"

// Автомат автономної деградації. П'ять станів із статті — і вся їхня
// обв'язка: мертва рука, монотонний час, канал і чорна скринька.
typedef enum {
    FALLBACK_ONLINE = 0,
    FALLBACK_HOLD_PHASE1,
    FALLBACK_AUTONOMOUS_PHASE2,
    FALLBACK_SAFE_STATE_PHASE3,
    FALLBACK_RECONNECTING
} fallback_state_t;

#define FB_TICK_MS             20U
#define FB_DEADMAN_TIMEOUT_MS  250U     // дозвіл, що його поновлює лише свіжий кадр
#define FB_HEARTBEAT_MS        20U      // період імпульсів на лінію ENABLE
#define FB_PHASE1_MS           5000U
#define FB_PHASE2_MS           60000U
#define FB_RECONNECT_MS        1000U

#define FB_MAX_ACCEL           0.6f     // межа другої похідної (одиниць тяги/с)
#define FB_MAX_JERK            3.0f     // межа третьої похідної (одиниць тяги/с²)
#define FB_DECEL               0.5f     // безпечне сповільнення у фазі 2
#define FB_STEER_RATE          1.5f
#define FB_MAX_SPEED_MPS       2.0f

// Числення шляху у фазі 1: невизначеність росте тим швидше, чим швидше їдемо.
#define FB_DR_SIGMA_BASE       0.05f
#define FB_DR_SIGMA_GAIN       0.25f
#define FB_DR_SIGMA_LIMIT      1.0f     // радіус безпеки, метри

#define FB_BEACON_PERIOD_MS    3000U
#define FB_BEACON_FLASH_MS     100U

// Токен-бакет фонового зливу: ~20% смуги радіо, решта — свіжим пакетам.
#define FB_DRAIN_CREDIT_TICK   12U
#define FB_DRAIN_CREDIT_MAX    240U

#define FB_EV_LINK_LOST   0x01U
#define FB_EV_PHASE2      0x02U
#define FB_EV_SAFE_STATE  0x03U
#define FB_EV_DR_LIMIT    0x04U
#define FB_EV_RECONNECT   0xA1U
#define FB_EV_ONLINE      0xA2U

typedef struct {
    fallback_state_t state;
    uint32_t state_since_ms;
    uint32_t last_frame_ms;
    uint32_t offline_since_ms;

    link_command_t cached;      // остання довірена уставка
    float throttle;
    float throttle_rate;        // швидкість зміни уставки — її й обмежує ривок
    float steering;

    float dr_pos_m;             // числення шляху у фазі 1
    float dr_sigma_m;

    uint32_t beacon_phase_ms;
    size_t   drain_credit;
    uint32_t raw_now;

    deadman_t  dm;
    timebase_t tb;
    link_t     link;
    logstore_t log;
} fallback_t;

void fallback_init(fallback_t *fb, uint32_t raw_now, uint32_t key);
link_status_t fallback_on_frame(fallback_t *fb, const uint8_t *frame, size_t len, uint32_t raw_now);
void fallback_tick(fallback_t *fb, uint32_t raw_now, float sensor_value);
uint32_t fallback_offline_ms(const fallback_t *fb);
const char *fallback_state_name(fallback_state_t st);

#endif /* FALLBACK_H */
