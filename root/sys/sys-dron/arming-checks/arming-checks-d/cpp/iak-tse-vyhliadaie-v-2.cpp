typedef struct {
    const char *name;
    bool (*check)(char *reason, size_t n);   // true = ОК; інакше пише причину
    bool mandatory;                          // чи можна вимкнути
} PreArmCheck;

static bool chk_gps(char *reason, size_t n) {
    if (gps_fix_type() < GPS_FIX_3D || gps_num_sats() < 6) {
        snprintf(reason, n, "GPS: 3D fix required");
        return false;
    }
    return true;
}

static bool chk_battery(char *reason, size_t n) {
    if (battery_voltage() < arm_min_voltage()) {
        snprintf(reason, n, "Battery below arming voltage");
        return false;
    }
    return true;
}
// ... chk_gyro_calibrated, chk_ekf_ready, chk_rc_alive, chk_safety_switch ...

static const PreArmCheck CHECKS[] = {
    { "GYRO",   chk_gyro_calibrated, true  },
    { "EKF",    chk_ekf_ready,       true  },
    { "GPS",    chk_gps,             false },   // можна вимкнути для польоту без GPS
    { "RC",     chk_rc_alive,        true  },
    { "BATT",   chk_battery,         true  },
    { "SAFETY", chk_safety_switch,   true  },
};
