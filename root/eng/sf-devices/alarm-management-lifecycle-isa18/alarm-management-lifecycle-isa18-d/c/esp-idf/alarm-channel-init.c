#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>

typedef enum {
    ALARM_STATE_NORMAL = 0,
    ALARM_STATE_UNACK = 1,
    ALARM_STATE_ACK = 2,
    ALARM_STATE_RTN_UNACK = 3,
    ALARM_STATE_SHELVED = 4,
    ALARM_STATE_SUPPRESSED = 5,
    ALARM_STATE_OOS = 6
} alarm_state_t;

typedef enum {
    ALARM_PRIO_LOW = 0,
    ALARM_PRIO_MEDIUM = 1,
    ALARM_PRIO_HIGH = 2,
    ALARM_PRIO_EMERGENCY = 3
} alarm_priority_t;

typedef struct {
    float threshold_high;
    float deadband;
    uint16_t on_delay_samples;
    uint16_t off_delay_samples;
    alarm_priority_t priority;
    
    /* Рантайм-стан каналу */
    alarm_state_t state;
    uint16_t on_counter;
    uint16_t off_counter;
    uint64_t trip_timestamp_us;
    _Atomic uint32_t status_flags; /* Атомарний бітмаск для обміну з ISR */
} alarm_channel_t;

#define ALARM_FLAG_ACTIVE     (1U << 0)
#define ALARM_FLAG_FIRST_OUT  (1U << 1)

void alarm_channel_init(alarm_channel_t *ch, float threshold, float deadband, 
                        uint16_t on_delay, uint16_t off_delay, alarm_priority_t prio) {
    ch->threshold_high = threshold;
    ch->deadband = deadband;
    ch->on_delay_samples = on_delay;
    ch->off_delay_samples = off_delay;
    ch->priority = prio;
    ch->state = ALARM_STATE_NORMAL;
    ch->on_counter = 0;
    ch->off_counter = 0;
    ch->trip_timestamp_us = 0;
    atomic_store(&ch->status_flags, 0);
}

void alarm_channel_process_sample(alarm_channel_t *ch, float raw_val, uint64_t now_us) {
    if (ch->state == ALARM_STATE_OOS || ch->state == ALARM_STATE_SUPPRESSED) {
        return;
    }

    bool physical_exceeded = (raw_val >= ch->threshold_high);
    bool physical_cleared = (raw_val < (ch->threshold_high - ch->deadband));

    /* Обробка часових затримок дебаунсу */
    if (physical_exceeded) {
        ch->off_counter = 0;
        if (ch->on_counter < ch->on_delay_samples) {
            ch->on_counter++;
        }
    } else if (physical_cleared) {
        ch->on_counter = 0;
        if (ch->off_counter < ch->off_delay_samples) {
            ch->off_counter++;
        }
    }

    bool condition_active = (ch->on_counter >= ch->on_delay_samples);
    bool condition_normal = (ch->off_counter >= ch->off_delay_samples);

    /* Переходи скінченного автомата ISA-18.2 */
    switch (ch->state) {
        case ALARM_STATE_NORMAL:
            if (condition_active) {
                ch->state = ALARM_STATE_UNACK;
                ch->trip_timestamp_us = now_us;
                atomic_fetch_or(&ch->status_flags, ALARM_FLAG_ACTIVE);
            }
            break;

        case ALARM_STATE_UNACK:
            if (condition_normal) {
                ch->state = ALARM_STATE_RTN_UNACK;
                atomic_fetch_and(&ch->status_flags, ~ALARM_FLAG_ACTIVE);
            }
            break;

        case ALARM_STATE_ACK:
            if (condition_normal) {
                ch->state = ALARM_STATE_NORMAL;
                atomic_fetch_and(&ch->status_flags, ~ALARM_FLAG_ACTIVE);
            }
            break;

        case ALARM_STATE_RTN_UNACK:
            if (condition_active) {
                ch->state = ALARM_STATE_UNACK;
                atomic_fetch_or(&ch->status_flags, ALARM_FLAG_ACTIVE);
            }
            break;

        default:
            break;
    }
}

void alarm_channel_acknowledge(alarm_channel_t *ch) {
    if (ch->state == ALARM_STATE_UNACK) {
        ch->state = ALARM_STATE_ACK;
    } else if (ch->state == ALARM_STATE_RTN_UNACK) {
        ch->state = ALARM_STATE_NORMAL;
    }
}
