struct PrearmResult {
    bool        pass;         // умова виконана?
    const char *reason;       // якщо ні — що саме сказати оператору
};

// Кожна перевірка звіряє ОДНЕ припущення, яким політ потім довіриться.
PrearmResult check_compass() {
    if (!compass_calibrated())  return { false, "компас не скалібровано" };
    if (!compass_healthy())     return { false, "компас не відповідає" };
    if (compass_disagree_deg() > 45.0f)                 // два компаси — згода?
        return { false, "компаси не згодні між собою" };
    return { true, nullptr };
}

PrearmResult check_gps() {
    if (gps_fix_type() < GPS_FIX_3D)
        return { false, "немає 3D-фіксації GPS" };
    if (gps_hdop() > 2.0f)                               // точність позиції
        return { false, "низька точність GPS" };
    return { true, nullptr };
}

PrearmResult check_battery() {
    if (battery_voltage() < FS_BATT_VOLTAGE)            // поріг failsafe
        return { false, "низька напруга батареї" };
    return { true, nullptr };
}
