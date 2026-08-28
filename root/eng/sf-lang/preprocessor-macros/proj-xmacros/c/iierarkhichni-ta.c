#include <stdio.h>

#define POWER_COMMANDS(X) \
    X(PWR_SLEEP, 0x10, "sleep") \
    X(PWR_WAKE,  0x11, "wake")

#define SENSOR_COMMANDS(X) \
    X(SNS_READ_TEMP, 0x20, "read_temp") \
    X(SNS_READ_HUM,  0x21, "read_hum")

#define ALL_SYSTEM_COMMANDS(X) \
    POWER_COMMANDS(X) \
    SENSOR_COMMANDS(X)

typedef enum {
#define X(name, code, str) name = code,
    ALL_SYSTEM_COMMANDS(X)
#undef X
} SystemCmd;

int main(void) {
    printf("Код команди PWR_SLEEP: 0x%02X\n", PWR_SLEEP);
    printf("Код команди SNS_READ_TEMP: 0x%02X\n", SNS_READ_TEMP);
    return 0;
}
