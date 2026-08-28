// Список 1 — перелік команд.
typedef enum {
    CMD_PING    = 0x01,
    CMD_ARM     = 0x02,
    CMD_DISARM  = 0x03,
    CMD_SET_PWM = 0x04,
    CMD_REBOOT  = 0x05,
} cmd_id_t;

// Список 2 — назви для логу. Індекс мусить збігатися з кодом команди.
static const char *CMD_NAME[] = {
    [CMD_PING]    = "PING",
    [CMD_ARM]     = "ARM",
    [CMD_DISARM]  = "DISARM",
    [CMD_SET_PWM] = "SET_PWM",
    [CMD_REBOOT]  = "REBOOT",
};

// Список 3 — обробники. Знову той самий перелік, утретє.
static const cmd_handler_t CMD_HANDLER[] = {
    [CMD_PING]    = handle_ping,
    [CMD_ARM]     = handle_arm,
    [CMD_DISARM]  = handle_disarm,
    [CMD_SET_PWM] = handle_set_pwm,
    [CMD_REBOOT]  = handle_reboot,
};
