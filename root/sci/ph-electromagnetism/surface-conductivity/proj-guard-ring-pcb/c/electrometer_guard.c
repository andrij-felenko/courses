/* electrometer_guard.c — C-версія модуля вимірювання надмалих струмів */
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define ADC_FULL_SCALE        65535.0f
#define V_REF                 2.5f
#define TIA_GAIN              1.0e9f     /* Коефіцієнт підсилення ТІА: 1 В/нА */
#define MAX_LEAKAGE_THRESHOLD 50.0e-12f  /* Максимально допустимий витік: 50 пА */
#define HUMIDITY_WARNING_RH   70.0f      /* Поріг ризику поверхневого витоку */

typedef struct {
    float offset_current_pA;
    float last_measured_pA;
    float humidity_rh;
    float temperature_C;
    bool  guard_alarm;
    bool  humidity_warning;
} ElectrometerDev;

void electrometer_init(ElectrometerDev *dev) {
    dev->offset_current_pA = 0.0f;
    dev->last_measured_pA = 0.0f;
    dev->humidity_rh = 45.0f;
    dev->temperature_C = 23.0f;
    dev->guard_alarm = false;
    dev->humidity_warning = false;
}

/* Оновлення метеоданих та перевірка ризику поверхневого витоку */
void electrometer_update_environment(ElectrometerDev *dev, float rh, float temp_C) {
    dev->humidity_rh = rh;
    dev->temperature_C = temp_C;
    dev->humidity_warning = (rh >= HUMIDITY_WARNING_RH);
}

/* Калібрування нульового зсуву при відключеному джерелі сигналу */
bool electrometer_calibrate_zero(ElectrometerDev *dev, unsigned short raw_adc) {
    float voltage = (float)raw_adc * (V_REF / ADC_FULL_SCALE);
    float measured_current_A = voltage / TIA_GAIN;
    
    dev->offset_current_pA = measured_current_A * 1.0e12f;
    
    /* Перевірка чи не перевищує струм витоку допустиму межу 50 пА */
    if (fabsf(dev->offset_current_pA) > (MAX_LEAKAGE_THRESHOLD * 1.0e12f)) {
        dev->guard_alarm = true; /* Своєчасно сигналізуємо про деградацію захисного кільця */
        return false;
    }
    
    dev->guard_alarm = false;
    return true;
}

/* Обчислення чистого струму з компенсацією каліброваного витоку */
float electrometer_read_current_pA(ElectrometerDev *dev, unsigned short raw_adc) {
    float voltage = (float)raw_adc * (V_REF / ADC_FULL_SCALE);
    float raw_current_pA = (voltage / TIA_GAIN) * 1.0e12f;
    
    dev->last_measured_pA = raw_current_pA - dev->offset_current_pA;
    return dev->last_measured_pA;
}
