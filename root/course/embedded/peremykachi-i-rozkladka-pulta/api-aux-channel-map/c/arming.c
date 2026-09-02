#include "arming.h"

#include <stdio.h>
#include <string.h>

typedef struct {
    uint16_t bit;
    const char *name;
    const char *reason;
} arm_flag_desc_t;

static const arm_flag_desc_t k_flags[] = {
    { ARM_BLOCK_THROTTLE_NOT_ZERO,  "ARM_BLOCK_THROTTLE_NOT_ZERO",
      "Throttle above minimum" },
    { ARM_BLOCK_FAILSAFE_ACTIVE,    "ARM_BLOCK_FAILSAFE_ACTIVE",
      "Failsafe active or RC link lost" },
    { ARM_BLOCK_PREARM_NOT_ENGAGED, "ARM_BLOCK_PREARM_NOT_ENGAGED",
      "Pre-Arm not engaged" },
    { ARM_BLOCK_SWITCH_ACTIVE_BOOT, "ARM_BLOCK_SWITCH_ACTIVE_BOOT",
      "Arm switch was on at boot" },
    { ARM_BLOCK_CALIBRATING,        "ARM_BLOCK_CALIBRATING",
      "Gyro or baro calibration in progress" },
    { ARM_BLOCK_TILT_ANGLE,         "ARM_BLOCK_TILT_ANGLE",
      "Tilt angle above limit" },
    { ARM_BLOCK_NO_COMPASS_LOCK,    "ARM_BLOCK_NO_COMPASS_LOCK",
      "Compass not consistent" },
    { ARM_BLOCK_NO_GNSS_FIX,        "ARM_BLOCK_NO_GNSS_FIX",
      "Need 3D fix for this mode" },
};

#define ARM_FLAG_COUNT (sizeof(k_flags) / sizeof(k_flags[0]))

void arming_init(arming_state_t *st, bool arm_switch_at_boot)
{
    if (st == NULL) {
        return;
    }
    /* Тумблер, увімкнений до подачі живлення, ставить засувку: доки пілот
       не переведе його в Disarm, запуск заборонено. */
    st->boot_latch = arm_switch_at_boot;
    st->armed      = false;
}

uint16_t arming_evaluate(arming_state_t *st, const arming_inputs_t *in)
{
    if (st == NULL || in == NULL) {
        return 0xFFFFU;
    }

    /* Засувка знімається лише повним поверненням тумблера в Disarm */
    if (st->boot_latch && !in->arm_switch) {
        st->boot_latch = false;
    }

    uint16_t blocks = 0U;

    if (in->throttle_us > ARM_THROTTLE_MIN_US) {
        blocks |= ARM_BLOCK_THROTTLE_NOT_ZERO;
    }
    if (in->failsafe_active) {
        blocks |= ARM_BLOCK_FAILSAFE_ACTIVE;
    }
    if (!in->prearm_engaged) {
        blocks |= ARM_BLOCK_PREARM_NOT_ENGAGED;
    }
    if (st->boot_latch) {
        blocks |= ARM_BLOCK_SWITCH_ACTIVE_BOOT;
    }
    if (in->calibrating) {
        blocks |= ARM_BLOCK_CALIBRATING;
    }
    if (in->tilt_deg > ARM_MAX_TILT_DEG || in->tilt_deg < -ARM_MAX_TILT_DEG) {
        blocks |= ARM_BLOCK_TILT_ANGLE;
    }
    if (!in->compass_healthy) {
        blocks |= ARM_BLOCK_NO_COMPASS_LOCK;
    }
    if (flight_mode_requires_gnss(in->mode) && (!in->gnss_fix_3d || in->hdop >= ARM_MAX_HDOP)) {
        blocks |= ARM_BLOCK_NO_GNSS_FIX;
    }

    return blocks;
}

bool arming_update(arming_state_t *st, const arming_inputs_t *in, uint16_t *blocks_out)
{
    if (st == NULL || in == NULL) {
        return false;
    }

    uint16_t blocks = arming_evaluate(st, in);
    if (blocks_out != NULL) {
        *blocks_out = blocks;
    }

    if (!in->arm_switch) {
        /* Disarm діє завжди й негайно, без жодних перевірок */
        st->armed = false;
        return false;
    }
    if (st->armed) {
        /* Уже в повітрі: причини запуску не перевіряємо повторно, інакше
           перший же стрибок HDOP глушив би мотори в польоті. */
        return true;
    }
    st->armed = (blocks == 0U);
    return st->armed;
}

const char *arming_flag_name(uint16_t single_bit)
{
    for (size_t i = 0; i < ARM_FLAG_COUNT; ++i) {
        if (k_flags[i].bit == single_bit) {
            return k_flags[i].name;
        }
    }
    return "ARM_BLOCK_UNKNOWN";
}

const char *arming_flag_reason(uint16_t single_bit)
{
    for (size_t i = 0; i < ARM_FLAG_COUNT; ++i) {
        if (k_flags[i].bit == single_bit) {
            return k_flags[i].reason;
        }
    }
    return "unknown";
}

size_t arming_format_reasons(uint16_t mask, char *buf, size_t size)
{
    if (buf == NULL || size == 0U) {
        return 0U;
    }
    buf[0] = '\0';

    size_t count  = 0U;
    size_t offset = 0U;

    for (size_t i = 0; i < ARM_FLAG_COUNT; ++i) {
        if ((mask & k_flags[i].bit) == 0U) {
            continue;
        }
        int written = snprintf(buf + offset, size - offset, "%sPreArm: %s",
                               (count == 0U) ? "" : "; ", k_flags[i].reason);
        count++;
        if (written < 0 || (size_t)written >= size - offset) {
            /* Буфер скінчився — рядок уже обрізано, далі писати нікуди */
            return count;
        }
        offset += (size_t)written;
    }
    return count;
}
