typedef enum { FS_NONE, FS_LINK_LOST, FS_GPS_LOST, FS_LOW_BATTERY } fs_reason_t;

void enter_failsafe(fs_reason_t reason) {
    // Найнебезпечніше — найвищий пріоритет. Батарея переважує все:
    // немає сенсу летіти додому, якщо двигуни заглухнуть на півдорозі.
    if (battery_critical()) {
        set_mode(MODE_LAND);             // сідай ТУТ І ЗАРАЗ
        return;
    }
    switch (reason) {
        case FS_LINK_LOST:
            set_mode(MODE_RTL);          // зв'язку немає → вертайся додому
            break;
        case FS_GPS_LOST:
            set_mode(MODE_ALT_HOLD);     // позиції немає → тримай лише висоту
            break;
        case FS_LOW_BATTERY:
            set_mode(MODE_LAND);         // енергія тане → керована посадка
            break;
        default:
            set_mode(MODE_LAND);         // невідомий збій → найобережніше
            break;
    }
}
