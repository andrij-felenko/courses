static bool signing_whitelist_filter(const mavlink_status_t *status, uint32_t msgid) {
    (void)status;
    switch (msgid) {
        // Дозволена інформаційна телеметрія:
        case MAVLINK_MSG_ID_HEARTBEAT:            // Серцебиття системи (ID 0)
        case MAVLINK_MSG_ID_SYS_STATUS:           // Стан батареї та сенсорів (ID 1)
        case MAVLINK_MSG_ID_SYSTEM_TIME:          // Час системи (ID 2)
        case MAVLINK_MSG_ID_ATTITUDE:             // Просторова орієнтація (ID 30)
        case MAVLINK_MSG_ID_GLOBAL_POSITION_INT:  // Координати GPS (ID 33)
        case MAVLINK_MSG_ID_VFR_HUD:              // Приладова швидкість і висота (ID 74)
            return true;

        // Заборонено без підпису (усі критичні накази):
        case MAVLINK_MSG_ID_COMMAND_LONG:         // Керуючі команди (ID 76)
        case MAVLINK_MSG_ID_COMMAND_INT:          // Координатні команди (ID 75)
        case MAVLINK_MSG_ID_MISSION_ITEM_INT:     // Точки польотного завдання (ID 73)
        case MAVLINK_MSG_ID_PARAM_SET:            // Зміна параметрів конфігурації (ID 23)
        case MAVLINK_MSG_ID_SET_MODE:             // Зміна режиму польоту (ID 11)
        default:
            return false;
    }
}
