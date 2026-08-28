#include <stdint.h>
#include <stdbool.h>

/* Перелік бітових позицій Betaflight armingDisableFlags */
typedef enum {
    ARMING_DISABLE_NO_GYRO          = (1 << 0),
    ARMING_DISABLE_FAILSAFE         = (1 << 1),
    ARMING_DISABLE_RX_FAILSAFE      = (1 << 2),
    ARMING_DISABLE_BAD_RX_RECOVERY  = (1 << 3),
    ARMING_DISABLE_BOXFAILSAFE      = (1 << 4),
    ARMING_DISABLE_THROTTLE         = (1 << 5),
    ARMING_DISABLE_CLI              = (1 << 6),
    ARMING_DISABLE_CMS_MENU         = (1 << 7),
    ARMING_DISABLE_OSD_MENU         = (1 << 8),
    ARMING_DISABLE_ROLLPITCH_CLIPPED= (1 << 9),
    ARMING_DISABLE_SERVO_INIT       = (1 << 10),
    ARMING_DISABLE_MOTOR_PROTOCOL   = (1 << 11),
    ARMING_DISABLE_ACC_CAL          = (1 << 12),
    ARMING_DISABLE_MOTOR_TEST       = (1 << 13),
    ARMING_DISABLE_ARM_SWITCH       = (1 << 14),
    ARMING_DISABLE_MSP              = (1 << 15),
    ARMING_DISABLE_PARALYZE         = (1 << 16),
    ARMING_DISABLE_GPS              = (1 << 17),
    ARMING_DISABLE_RESC             = (1 << 18),
    ARMING_DISABLE_RPMFILTER        = (1 << 19),
    ARMING_DISABLE_REBOOT_REQUIRED  = (1 << 20),
    ARMING_DISABLE_NOPREARM         = (1 << 21),
    ARMING_DISABLE_LOAD             = (1 << 22),
    ARMING_DISABLE_CALIBRATING      = (1 << 23)
} betaflight_arming_flags_e;

/* Перевірка можливості запуску */
bool is_ready_to_arm(uint32_t flags) {
    return (flags == 0);
}
