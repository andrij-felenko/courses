/* gnss_rf_controller.c - С-версія модуля керування генератором та атенюатором */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define GPS_L1_FREQ_HZ   1575420000.0
#define SPEED_OF_LIGHT   299792458.0
#define SAMPLE_RATE_SPS  2600000.0
#define NUM_SATELLITES   8

typedef struct {
    double x, y, z;       /* Координати ECEF у метрах */
    double vx, vy, vz;    /* Швидкість у м/с */
} ecef_state_t;

typedef struct {
    int sat_prn;
    ecef_state_t pos;
    double doppler_hz;
    double pseudorange_m;
    double carrier_phase_rad;
    double snr_dbhz;
} satellite_channel_t;

typedef struct {
    int serial_fd;
    double current_attenuation_db;
} rf_attenuator_t;

/* Розрахунок доплерівського зсуву частоти */
double calculate_doppler(const ecef_state_t *user, const ecef_state_t *sat) {
    double dx = sat->x - user->x;
    double dy = sat->y - user->y;
    double dz = sat->z - user->z;
    double range = sqrt(dx*dx + dy*dy + dz*dz);
    if (range < 1.0) return 0.0;

    /* Одиничний вектор прямої видимості */
    double ex = dx / range;
    double ey = dy / range;
    double ez = dz / range;

    /* Вектор відносної швидкості */
    double dvx = sat->vx - user->vx;
    double dvy = sat->vy - user->vy;
    double dvz = sat->vz - user->vz;

    double v_relative = dvx * ex + dvy * ey + dvz * ez;
    return -GPS_L1_FREQ_HZ * (v_relative / SPEED_OF_LIGHT);
}

/* Формування SCPI команди для зміни загасання крокового атенюатора */
bool attenuator_set_db(rf_attenuator_t *att, double db) {
    if (db < 0.0) db = 0.0;
    if (db > 95.0) db = 95.0;

    char cmd_buffer[64];
    int len = snprintf(cmd_buffer, sizeof(cmd_buffer), ":ATT:VAL %.2f\n", db);
    if (len <= 0) return false;

    /* Надсилання команди в послідовний порт керування */
    printf("[SCPI TX] %s", cmd_buffer);
    att->current_attenuation_db = db;
    return true;
}

/* Генерація одного блоку 16-бітних I/Q вибірок для передавача SDR */
void generate_iq_block(satellite_channel_t *sats, int num_sats,
                       int16_t *iq_buffer, size_t num_samples) {
    const double dt = 1.0 / SAMPLE_RATE_SPS;

    for (size_t n = 0; n < num_samples; ++n) {
        double total_i = 0.0;
        double total_q = 0.0;

        for (int s = 0; s < num_sats; ++s) {
            satellite_channel_t *ch = &sats[s];
            
            /* Інтегрування фази з урахуванням доплера */
            ch->carrier_phase_rad += 2.0 * M_PI * ch->doppler_hz * dt;
            if (ch->carrier_phase_rad > 2.0 * M_PI) {
                ch->carrier_phase_rad -= 2.0 * M_PI;
            }

            /* Квадратурна модуляторна сума */
            total_i += cos(ch->carrier_phase_rad);
            total_q += sin(ch->carrier_phase_rad);
        }

        /* Масштабування до діапазону ЦАП SDR (-32768..+32767) */
        iq_buffer[2 * n]     = (int16_t)(total_i * 1000.0);
        iq_buffer[2 * n + 1] = (int16_t)(total_q * 1000.0);
    }
}
