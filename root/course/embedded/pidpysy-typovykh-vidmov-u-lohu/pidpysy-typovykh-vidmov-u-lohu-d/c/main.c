#include <math.h>
#include <stdbool.h>
#include <stdint.h>

#define WINDOW_SIZE 64

typedef enum {
    FAULT_NONE = 0,
    FAULT_MOTOR_DESYNC,
    FAULT_SENSOR_CLIPPING,
    FAULT_TOILET_BOWL,
    FAULT_MIXER_SATURATION
} FaultType;

typedef struct {
    double time_s;
    double gyro_roll;
    double setpoint_roll;
    double acc_z;
    double motor_cmd[4];    // 0.0 .. 1.0
    double motor_erpm[4];   // оберти/хв
    double roll_deg;
    double pitch_deg;
    int    clip_count;
} LogSample;

// Аналіз відрізка польоту на наявність характерних сигнатур відмов
static FaultType detect_flight_fault(const LogSample *samples, int n) {
    if (n < WINDOW_SIZE) return FAULT_NONE;

    int desync_votes = 0;
    int clip_votes = 0;
    int sat_votes = 0;

    for (int i = 0; i < n; i++) {
        // 1. Детекція кліпінгу: переповнення лічильника або вихід на межу +-15.8g
        if (samples[i].clip_count > 0 || fabs(samples[i].acc_z) > 15.8 * 9.81) {
            clip_votes++;
        }

        // 2. Детекція десинхрону: команда 100% при падінні eRPM до 0 і великій помилці гіроскопа
        for (int m = 0; m < 4; m++) {
            if (samples[i].motor_cmd[m] > 0.98 && samples[i].motor_erpm[m] < 100.0) {
                double tracking_err = fabs(samples[i].gyro_roll - samples[i].setpoint_roll);
                if (tracking_err > 300.0) { // кутова швидкість розбіглася > 300 deg/s
                    desync_votes++;
                }
            }
        }

        // 3. Детекція тривалого насичення мікшера (плато 100%)
        int max_motors = 0;
        for (int m = 0; m < 4; m++) {
            if (samples[i].motor_cmd[m] > 0.98) max_motors++;
        }
        if (max_motors >= 2) sat_votes++;
    }

    if (desync_votes >= 3) return FAULT_MOTOR_DESYNC;
    if (clip_votes >= 5)   return FAULT_SENSOR_CLIPPING;

    // 4. Детекція «унітазу»: взаємна кореляція Roll та Pitch зі зсувом 90 градусів
    double sum_roll_sq = 0.0, sum_pitch_sq = 0.0;
    for (int i = 0; i < n; i++) {
        sum_roll_sq  += samples[i].roll_deg * samples[i].roll_deg;
        sum_pitch_sq += samples[i].pitch_deg * samples[i].pitch_deg;
    }
    double rms_roll  = sqrt(sum_roll_sq / n);
    double rms_pitch = sqrt(sum_pitch_sq / n);

    // Якщо обидві осі коливаються з великою амплітудою (> 10 deg) у навігаційному режимі
    if (rms_roll > 10.0 && rms_pitch > 10.0) {
        int phase_shifted_matches = 0;
        int quarter_period = 16; // зсув на 90 градусів при вікні 64 семпли
        for (int i = 0; i < n - quarter_period; i++) {
            // Перевірка ортогональності знаків: Roll(t) та Pitch(t + T/4) мають однаковий напрям
            if ((samples[i].roll_deg * samples[i + quarter_period].pitch_deg) > 0.0) {
                phase_shifted_matches++;
            }
        }
        if (phase_shifted_matches > (n - quarter_period) * 0.75) {
            return FAULT_TOILET_BOWL;
        }
    }

    if (sat_votes > n / 2) return FAULT_MIXER_SATURATION;

    return FAULT_NONE;
}
