/* telemetry_throttler.h / .c — Регулятор частот MAVLink на базі автомата станів */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAVLINK_MSG_ID_HEARTBEAT           0
#define MAVLINK_MSG_ID_SYS_STATUS          1
#define MAVLINK_MSG_ID_GPS_RAW_INT         24
#define MAVLINK_MSG_ID_ATTITUDE            30
#define MAVLINK_MSG_ID_GLOBAL_POSITION_INT 33
#define MAVLINK_MSG_ID_VFR_HUD             74
#define MAVLINK_MSG_ID_RADIO_STATUS        109

#define MAV_CMD_SET_MESSAGE_INTERVAL       511

typedef enum {
    THROTTLE_STATE_NORMAL = 0,
    THROTTLE_STATE_DEGRADED,
    THROTTLE_STATE_CRITICAL
} TelemetryState;

typedef struct {
    uint32_t msg_id;
    int32_t  interval_us; /* -1 = вимкнено, >0 = період у мкс */
} StreamConfig;

typedef struct {
    TelemetryState current_state;
    uint32_t       last_state_change_ms;
    uint32_t       recovery_timer_ms;
    uint8_t        txbuf_smooth;
    uint8_t        packet_loss_pct;
    bool           pending_apply;
} TelemetryThrottler;

/* Профілі частот для трьох станів */
static const StreamConfig PROFILE_NORMAL[] = {
    {MAVLINK_MSG_ID_ATTITUDE,            20000},   /* 50 Гц */
    {MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 100000},  /* 10 Гц */
    {MAVLINK_MSG_ID_VFR_HUD,             100000},  /* 10 Гц */
    {MAVLINK_MSG_ID_GPS_RAW_INT,         200000},  /* 5 Гц  */
    {MAVLINK_MSG_ID_SYS_STATUS,          500000},  /* 2 Гц  */
    {MAVLINK_MSG_ID_HEARTBEAT,           1000000}  /* 1 Гц  */
};

static const StreamConfig PROFILE_DEGRADED[] = {
    {MAVLINK_MSG_ID_ATTITUDE,            66666},   /* 15 Гц */
    {MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 250000},  /* 4 Гц  */
    {MAVLINK_MSG_ID_VFR_HUD,             500000},  /* 2 Гц  */
    {MAVLINK_MSG_ID_GPS_RAW_INT,         500000},  /* 2 Гц  */
    {MAVLINK_MSG_ID_SYS_STATUS,          1000000}, /* 1 Гц  */
    {MAVLINK_MSG_ID_HEARTBEAT,           1000000}  /* 1 Гц  */
};

static const StreamConfig PROFILE_CRITICAL[] = {
    {MAVLINK_MSG_ID_ATTITUDE,            200000},  /* 5 Гц  */
    {MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 1000000}, /* 1 Гц  */
    {MAVLINK_MSG_ID_VFR_HUD,             -1},      /* Вимкнено */
    {MAVLINK_MSG_ID_GPS_RAW_INT,         1000000}, /* 1 Гц  */
    {MAVLINK_MSG_ID_SYS_STATUS,          1000000}, /* 1 Гц  */
    {MAVLINK_MSG_ID_HEARTBEAT,           1000000}  /* 1 Гц  */
};

#define STREAMS_COUNT (sizeof(PROFILE_NORMAL) / sizeof(PROFILE_NORMAL[0]))

void telemetry_throttler_init(TelemetryThrottler *th, uint32_t now_ms) {
    th->current_state = THROTTLE_STATE_NORMAL;
    th->last_state_change_ms = now_ms;
    th->recovery_timer_ms = 0;
    th->txbuf_smooth = 0;
    th->packet_loss_pct = 0;
    th->pending_apply = true;
}

/* Зовнішній виклик: відправка MAVLink-команди SET_MESSAGE_INTERVAL */
extern void mavlink_send_set_interval(uint32_t msg_id, int32_t interval_us);

static void apply_profile(const StreamConfig *profile, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        mavlink_send_set_interval(profile[i].msg_id, profile[i].interval_us);
    }
}

void telemetry_throttler_on_radio_status(TelemetryThrottler *th, uint8_t txbuf_pct,
                                        uint8_t rxerrors, uint32_t now_ms) {
    /* Фільтр експоненційного згладжування (EMA) для заповнення буфера */
    th->txbuf_smooth = (uint8_t)((th->txbuf_smooth * 7 + txbuf_pct * 3) / 10);
    th->packet_loss_pct = rxerrors;
}

void telemetry_throttler_update(TelemetryThrottler *th, uint32_t now_ms) {
    TelemetryState next_state = th->current_state;

    /* 1. Перевірка умов негайної деградації (DOWNGRADE) */
    if (th->txbuf_smooth > 85 || th->packet_loss_pct > 35) {
        next_state = THROTTLE_STATE_CRITICAL;
        th->recovery_timer_ms = 0;
    } else if (th->txbuf_smooth > 60 || th->packet_loss_pct > 15) {
        if (th->current_state == THROTTLE_STATE_NORMAL) {
            next_state = THROTTLE_STATE_DEGRADED;
            th->recovery_timer_ms = 0;
        }
    }

    /* 2. Перевірка умов повільного відновлення з гістерезисом (UPGRADE) */
    if (next_state == th->current_state) {
        if (th->current_state == THROTTLE_STATE_CRITICAL) {
            if (th->txbuf_smooth < 50 && th->packet_loss_pct < 10) {
                if (th->recovery_timer_ms == 0) th->recovery_timer_ms = now_ms;
                if (now_ms - th->recovery_timer_ms >= 5000) {
                    next_state = THROTTLE_STATE_DEGRADED;
                    th->recovery_timer_ms = 0;
                }
            } else {
                th->recovery_timer_ms = 0;
            }
        } else if (th->current_state == THROTTLE_STATE_DEGRADED) {
            if (th->txbuf_smooth < 30 && th->packet_loss_pct < 5) {
                if (th->recovery_timer_ms == 0) th->recovery_timer_ms = now_ms;
                if (now_ms - th->recovery_timer_ms >= 5000) {
                    next_state = THROTTLE_STATE_NORMAL;
                    th->recovery_timer_ms = 0;
                }
            } else {
                th->recovery_timer_ms = 0;
            }
        }
    }

    /* 3. Зміна стану та застосування нових частот */
    if (next_state != th->current_state || th->pending_apply) {
        th->current_state = next_state;
        th->last_state_change_ms = now_ms;
        th->pending_apply = false;

        switch (th->current_state) {
            case THROTTLE_STATE_NORMAL:
                apply_profile(PROFILE_NORMAL, STREAMS_COUNT);
                break;
            case THROTTLE_STATE_DEGRADED:
                apply_profile(PROFILE_DEGRADED, STREAMS_COUNT);
                break;
            case THROTTLE_STATE_CRITICAL:
                apply_profile(PROFILE_CRITICAL, STREAMS_COUNT);
                break;
        }
    }
}
