#include "prearm.h"

void bf_state_init(bf_state_t *st, const bf_inputs_t *at_boot, uint32_t now_ms)
{
    st->link_ok = at_boot->rx_frame_valid && !at_boot->rx_failsafe_flag;
    st->link_ok_since_ms = now_ms;
    st->link_lost_since_ms = now_ms;
    st->failsafe = !st->link_ok;
    /* Плату ввімкнено з піднятим тумблером — блокування-засувка, яку
     * знімає лише фізичне опускання тумблера, а не наступний такт. */
    st->arm_switch_latched = at_boot->arm_switch_high;
}

static void update_link(bf_state_t *st, const bf_inputs_t *in, uint32_t now_ms)
{
    const bool valid = in->rx_frame_valid && !in->rx_failsafe_flag;

    if (valid && !st->link_ok) {
        st->link_ok = true;
        st->link_ok_since_ms = now_ms;   /* відлік захисної секунди з нуля */
    } else if (!valid && st->link_ok) {
        st->link_ok = false;
        st->link_lost_since_ms = now_ms;
    }

    if (!st->link_ok && (uint32_t)(now_ms - st->link_lost_since_ms) >= BF_FAILSAFE_DELAY_MS) {
        st->failsafe = true;
    }
    /* Знімається тільки після цілої секунди БЕЗ жодного пропуску: кожен
     * втрачений кадр перезаписує link_ok_since_ms і відлік починається знову.
     * Саме тому пульт поруч із приймачем блокує армінг нескінченно. */
    if (st->failsafe && st->link_ok &&
        (uint32_t)(now_ms - st->link_ok_since_ms) >= BF_RX_RECOVERY_MS) {
        st->failsafe = false;
    }
}

uint32_t bf_update(bf_state_t *st, const bf_inputs_t *in, uint32_t now_ms)
{
    uint32_t mask = 0;

    update_link(st, in, now_ms);
    if (!in->arm_switch_high) {
        st->arm_switch_latched = false;
    }

    /* сенсори */
    if (!in->gyro_present)    { mask |= BF_BIT(BF_NO_GYRO); }
    if (in->gyro_calibrating) { mask |= BF_BIT(BF_CALIBRATING); }
    if (!in->acc_calibrated)  { mask |= BF_BIT(BF_ACC_CAL); }

    /* радіолінк */
    if (st->failsafe) {
        mask |= BF_BIT(BF_FAILSAFE);
        if (st->link_ok) {
            mask |= BF_BIT(BF_BAD_RX_RECOVERY);
        }
    }
    if (in->rx_failsafe_flag) { mask |= BF_BIT(BF_RX_FAILSAFE); }
    if (in->box_failsafe)     { mask |= BF_BIT(BF_BOXFAILSAFE); }

    /* органи керування */
    if (in->throttle_us > BF_MIN_CHECK_US) {
        mask |= BF_BIT(BF_THROTTLE);
    }
    if (in->roll_us < BF_RC_MIN_US || in->roll_us > BF_RC_MAX_US ||
        in->pitch_us < BF_RC_MIN_US || in->pitch_us > BF_RC_MAX_US) {
        mask |= BF_BIT(BF_ROLLPITCH_CLIPPED);
    }
    if (st->arm_switch_latched) {
        mask |= BF_BIT(BF_ARM_SWITCH);
    }
    if (in->prearm_required && !in->prearm_engaged) {
        mask |= BF_BIT(BF_NOPREARM);
    }

    /* інтерфейси конфігурації */
    if (in->cli_open)          { mask |= BF_BIT(BF_CLI); }
    if (in->msp_client_active) { mask |= BF_BIT(BF_MSP); }
    if (in->motor_test_active) { mask |= BF_BIT(BF_MOTOR_TEST); }
    if (in->cms_menu_open)     { mask |= BF_BIT(BF_CMS_MENU); }
    if (in->osd_menu_open)     { mask |= BF_BIT(BF_OSD_MENU); }

    /* мотори й приводи */
    if (in->servos_settling)   { mask |= BF_BIT(BF_SERVO_INIT); }
    if (!in->motor_protocol_ok) { mask |= BF_BIT(BF_MOTOR_PROTOCOL); }
    if (in->rpm_filter_enabled && !in->esc_telemetry_ok) {
        mask |= BF_BIT(BF_RPMFILTER);
    }

    /* решта */
    if (in->paralyze)        { mask |= BF_BIT(BF_PARALYZE); }
    if (in->rescue_switch)   { mask |= BF_BIT(BF_RESC); }
    if (in->reboot_required) { mask |= BF_BIT(BF_REBOOT_REQUIRED); }
    if (in->gps_required && in->gps_sats < BF_GPS_MIN_SATS) {
        mask |= BF_BIT(BF_GPS);
    }
    if (in->cpu_load_pct > BF_CPU_LOAD_LIMIT_PCT) {
        mask |= BF_BIT(BF_LOAD);
    }

    return mask;
}
