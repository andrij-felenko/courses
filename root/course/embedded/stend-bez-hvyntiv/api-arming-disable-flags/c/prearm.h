#ifndef PREARM_H
#define PREARM_H

#include "bf_flags.h"

/* Пороги — типові значення прошивки за замовчуванням. */
#define BF_MIN_CHECK_US        1050u  /* вище цього газ уже не «в нулі» */
#define BF_RC_MIN_US           1000u
#define BF_RC_MAX_US           2000u
#define BF_FAILSAFE_DELAY_MS    400u  /* failsafe_delay = 4 (десяті секунди) */
#define BF_RX_RECOVERY_MS      1000u  /* захисна секунда чистого лінка */
#define BF_CPU_LOAD_LIMIT_PCT    75u
#define BF_GPS_MIN_SATS           6u

/* Зріз того, що модулі апарата повідомляють диспетчеру в одному такті
 * TASK_SYSTEM. Часу тут немає: час приходить окремим аргументом, бо
 * таймери веде автомат, а не джерела сигналів. */
typedef struct {
    /* сенсори */
    bool gyro_present;
    bool acc_calibrated;
    bool gyro_calibrating;
    /* радіолінк */
    bool rx_frame_valid;     /* у цьому такті приймач віддав валідний кадр */
    bool rx_failsafe_flag;   /* приймач сам підняв свій failsafe */
    bool box_failsafe;       /* тумблер аварійного Failsafe на пульті */
    uint16_t throttle_us;
    uint16_t roll_us;
    uint16_t pitch_us;
    bool arm_switch_high;
    bool prearm_required;    /* у конфігурації є перемикач Prearm */
    bool prearm_engaged;
    /* інтерфейси конфігурації */
    bool cli_open;
    bool msp_client_active;
    bool motor_test_active;
    bool cms_menu_open;
    bool osd_menu_open;
    /* мотори й приводи */
    bool servos_settling;
    bool motor_protocol_ok;
    bool rpm_filter_enabled;
    bool esc_telemetry_ok;
    /* решта */
    bool paralyze;
    bool rescue_switch;
    bool reboot_required;
    bool gps_required;
    uint8_t gps_sats;
    uint8_t cpu_load_pct;
} bf_inputs_t;

/* Те, що прошивка пам'ятає МІЖ тактами: два таймери радіолінка
 * і засувка тумблера армінгу. */
typedef struct {
    bool link_ok;
    uint32_t link_ok_since_ms;
    uint32_t link_lost_since_ms;
    bool failsafe;
    bool arm_switch_latched;
} bf_state_t;

void bf_state_init(bf_state_t *st, const bf_inputs_t *at_boot, uint32_t now_ms);

/* Один такт диспетчера: повертає свіже значення armingDisableFlags. */
uint32_t bf_update(bf_state_t *st, const bf_inputs_t *in, uint32_t now_ms);

#endif /* PREARM_H */
