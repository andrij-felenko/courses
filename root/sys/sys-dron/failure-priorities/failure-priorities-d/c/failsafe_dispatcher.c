/**
 * @file failsafe_dispatcher.c
 * @brief Диспетчер аварійного витіснення та деградації станів.
 */

#include <stdint.h>
#include <stdbool.h>

/* Сенсорні спроможності */
#define CAP_ATTITUDE_OK   (1u << 0)
#define CAP_ALTITUDE_OK   (1u << 1)
#define CAP_POSITION_OK   (1u << 2)
#define CAP_PROPULSION_OK (1u << 3)

typedef enum {
    ACT_NONE = 0,
    ACT_WARN,
    ACT_ALT_HOLD,
    ACT_RTL,
    ACT_LAND,
    ACT_TERMINATE
} DispatchAction_t;

typedef struct {
    uint8_t          rank;          /* 0 = найвищий пріоритет */
    uint8_t          req_caps;      /* Маска обов'язкових CAP_* */
    DispatchAction_t desired_act;
    DispatchAction_t fallback_act;
    bool             latch;
} FailureDescriptor_t;

/* Таблиця детермінованих пріоритетів аварій */
static const FailureDescriptor_t FAILURE_TABLE[] = {
    /* 0: Втрата просторового контролю */
    { .rank = 0, .req_caps = 0,                 .desired_act = ACT_TERMINATE, .fallback_act = ACT_TERMINATE, .latch = true },
    /* 1: Критичний розряд батареї */
    { .rank = 1, .req_caps = CAP_ATTITUDE_OK,   .desired_act = ACT_LAND,      .fallback_act = ACT_TERMINATE, .latch = true },
    /* 2: Низький заряд батареї */
    { .rank = 2, .req_caps = CAP_POSITION_OK | CAP_ALTITUDE_OK, .desired_act = ACT_RTL, .fallback_act = ACT_LAND, .latch = false },
    /* 3: Втрата зв'язку RC */
    { .rank = 3, .req_caps = CAP_POSITION_OK | CAP_ALTITUDE_OK, .desired_act = ACT_RTL, .fallback_act = ACT_LAND, .latch = false },
    /* 4: Сенсорна деградація GNSS */
    { .rank = 4, .req_caps = CAP_ALTITUDE_OK,   .desired_act = ACT_ALT_HOLD,  .fallback_act = ACT_LAND,      .latch = false }
};

#define NUM_FAILURES (sizeof(FAILURE_TABLE) / sizeof(FAILURE_TABLE[0]))

static bool s_latched_flags[NUM_FAILURES] = { false };
static DispatchAction_t s_current_action = ACT_NONE;
static uint8_t s_current_rank = 255;

/**
 * @brief Оцінити активні відмови та виконати атомарне витіснення.
 * @param active_failures_mask Бітова маска виявлених відмов.
 * @param current_caps_mask Бітова маска справних датчиків.
 * @return Результуюча активна дія.
 */
DispatchAction_t failsafe_dispatch_step(uint8_t active_failures_mask, uint8_t current_caps_mask) {
    uint8_t best_rank = 255;
    DispatchAction_t selected_action = ACT_NONE;

    for (uint8_t i = 0; i < NUM_FAILURES; ++i) {
        bool is_active = (active_failures_mask & (1u << i)) != 0;
        if (is_active || s_latched_flags[i]) {
            if (FAILURE_TABLE[i].latch) {
                s_latched_flags[i] = true;
            }

            if (FAILURE_TABLE[i].rank < best_rank) {
                bool caps_valid = (current_caps_mask & FAILURE_TABLE[i].req_caps) == FAILURE_TABLE[i].req_caps;
                DispatchAction_t act = caps_valid ? FAILURE_TABLE[i].desired_act : FAILURE_TABLE[i].fallback_act;

                best_rank = FAILURE_TABLE[i].rank;
                selected_action = act;
            }
        }
    }

    s_current_action = selected_action;
    s_current_rank = best_rank;
    return s_current_action;
}
