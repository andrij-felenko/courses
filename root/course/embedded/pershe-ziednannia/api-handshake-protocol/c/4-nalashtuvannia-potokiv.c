typedef struct __mavlink_command_long_t {
    float    param1;          // Target Message ID (наприклад, 30 для ATTITUDE)
    float    param2;          // Інтервал у мікросекундах (1 000 000 / частота в Гц). -1 = вимкнути, 0 = дефолт
    float    param3;          // Резерв (0.0f)
    float    param4;          // Резерв (0.0f)
    float    param5;          // Резерв (0.0f)
    float    param6;          // Резерв (0.0f)
    float    param7;          // Response Target (0 = транслювати на поточний порт)
    uint16_t command;         // MAV_CMD_SET_MESSAGE_INTERVAL (511)
    uint8_t  target_system;    // SysID автопілота
    uint8_t  target_component; // CompID автопілота
    uint8_t  confirmation;     // Номер спроби (0 при першому надсиланні, 1..N при повторах)
} mavlink_command_long_t;
