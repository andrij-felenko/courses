#include "params.h"

void fm_params_default(fm_params_t *p)
{
    if (!p) {
        return;
    }

    p->gnss_min_sats            = 6;
    p->gnss_min_fix_type        = 3;
    p->gnss_max_hdop            = 1.5f;
    p->gnss_max_vdop            = 2.0f;

    p->ekf_max_innov_pos        = 0.3f;
    p->ekf_max_innov_vel        = 0.5f;
    p->ekf_glitch_innov         = 1.0f;
    p->compass_max_yaw_err_deg  = 15.0f;

    p->guided_timeout_ms        = 1000u;

    p->throttle_deadband        = 0.12f;
    p->throttle_slew_per_s      = 0.60f;

    p->land_speed               = 0.7f;
    p->land_vz_epsilon          = 0.2f;
    p->land_thr_min             = 0.18f;
    p->land_accel_var_max       = 0.35f;
    p->land_contact_ms          = 1000u;
    p->land_confirm_ms          = 1500u;
    p->land_idle_throttle       = 0.05f;

    p->in_air_alt_m             = 1.5f;
    p->in_air_motor_min         = 0.25f;
    p->in_air_accel_var_min     = 0.20f;

    p->rc_loss_ms               = 1500u;
    p->gcs_loss_ms              = 3000u;

    p->batt_low_cell_v          = 3.5f;
    p->batt_low_remaining       = 0.25f;
    p->batt_crit_cell_v         = 3.3f;
    p->batt_crit_remaining      = 0.10f;

    p->fence_radius_m           = 300.0f;
    p->fence_alt_m              = 120.0f;
    p->rtl_alt_m                = 30.0f;

    p->guard_stable_ms          = 2000u;
    p->pilot_override_stick     = 0.15f;
    p->mission_max_alt_m        = 120.0f;
}
