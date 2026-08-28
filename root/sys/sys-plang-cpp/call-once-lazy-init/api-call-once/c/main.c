#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    double gains[3];
    char firmware_version[16];
} CalibrationProfileC;

static CalibrationProfileC* g_profile = NULL;
static pthread_once_t g_calib_flag = PTHREAD_ONCE_INIT;

static void load_profile_eeprom_c(void) {
    printf("Зчитування калібрувального профілю (POSIX C)...\n");
    g_profile = (CalibrationProfileC*)malloc(sizeof(CalibrationProfileC));
    if (g_profile) {
        g_profile->gains[0] = 1.024;
        g_profile->gains[1] = 0.998;
        g_profile->gains[2] = 1.005;
        strncpy(g_profile->firmware_version, "v2.4.1", 15);
    }
}

void read_sensor_c(int channel) {
    pthread_once(&g_calib_flag, load_profile_eeprom_c);
    if (g_profile) {
        printf("Канал %d з коефіцієнтом: %f\n", channel, g_profile->gains[channel % 3]);
    }
}
