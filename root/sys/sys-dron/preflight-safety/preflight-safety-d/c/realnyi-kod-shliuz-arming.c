typedef struct {
    bool        pass;         // умова виконана?
    const char *reason;       // якщо ні — що саме сказати оператору
} prearm_result_t;

// Кожна перевірка звіряє ОДНЕ припущення, яким політ потім довіриться.
prearm_result_t check_compass(void) {
    if (!compass_calibrated())  return (prearm_result_t){ false, "компас не скалібровано" };
    if (!compass_healthy())     return (prearm_result_t){ false, "компас не відповідає" };
    if (compass_disagree_deg() > 45.0f)                 // два компаси — згода?
        return (prearm_result_t){ false, "компаси не згодні між собою" };
    return (prearm_result_t){ true, NULL };
}

prearm_result_t check_gps(void) {
    if (gps_fix_type() < GPS_FIX_3D)
        return (prearm_result_t){ false, "немає 3D-фіксації GPS" };
    if (gps_hdop() > 2.0f)                               // точність позиції
        return (prearm_result_t){ false, "низька точність GPS" };
    return (prearm_result_t){ true, NULL };
}

prearm_result_t check_battery(void) {
    if (battery_voltage() < FS_BATT_VOLTAGE)            // поріг failsafe
        return (prearm_result_t){ false, "низька напруга батареї" };
    return (prearm_result_t){ true, NULL };
}
