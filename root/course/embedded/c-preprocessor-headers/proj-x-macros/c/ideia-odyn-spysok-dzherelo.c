// cmd_table.h — ЄДИНЕ джерело істини про команди протоколу.
// Кожен рядок: X(код, ідентифікатор, назва-рядок, обробник).
// Макрос X тут НАВМИСНО не визначений — його задає той, хто розгортає список.

#define CMD_TABLE(X)                                   \
    X(0x01, PING,    "PING",    handle_ping)           \
    X(0x02, ARM,     "ARM",     handle_arm)            \
    X(0x03, DISARM,  "DISARM",  handle_disarm)         \
    X(0x04, SET_PWM, "SET_PWM", handle_set_pwm)        \
    X(0x05, REBOOT,  "REBOOT",  handle_reboot)
