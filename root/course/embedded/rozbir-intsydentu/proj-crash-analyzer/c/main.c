#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <math.h>

#define MAX_MOTORS 4
#define WINDOW_SIZE 30

typedef enum {
    FAULT_NONE = 0,
    FAULT_MOTOR_ESC_LOSS,
    FAULT_MAGNETIC_INTERFERENCE,
    FAULT_BROWNOUT_VOLTAGE_SAG,
    FAULT_SENSOR_BUS_LOCKUP
} FaultType;

typedef struct {
    uint64_t timestamp_us;       // мікросекунди від старту контролера
    float roll_des_deg;          // заданий крен (DesRoll)
    float roll_act_deg;          // фактичний крен (Roll)
    float yaw_des_deg;           // заданий курс (DesYaw)
    float yaw_act_deg;           // фактичний курс (Yaw)
    float motor_out[MAX_MOTORS]; // виходи на мотори [0.0 .. 1.0]
    float bat_voltage_v;         // напруга батареї, В
    float bat_current_a;         // струм споживання, А
    float ekf_mag_innov;         // нев'язка компаса в EKF
    float gyro_x_rads;           // кутова швидкість крену, рад/с
    uint32_t sensor_status_mask; // маска прапорців здоров'я (0x01 - IMU OK)
} TelemetryFrame;

typedef struct {
    FaultType fault;
    uint64_t timestamp_us;       // часова мітка першого прояву
    float confidence;            // коефіцієнт впевненості [0.0 .. 1.0]
    const char *description;
} IncidentReport;

static bool is_angle_diverging(float des, float act, float threshold_deg) {
    float err = fabsf(des - act);
    if (err > 180.0f) err = 360.0f - err; // корекція кільцевого переходу через 180°
    return err > threshold_deg;
}

IncidentReport analyze_incident(const TelemetryFrame *frames, size_t count) {
    IncidentReport report = {
        .fault = FAULT_NONE,
        .timestamp_us = 0,
        .confidence = 0.0f,
        .description = "Інцидентів не виявлено: параметри в межах норми"
    };

    if (count < WINDOW_SIZE) {
        report.description = "Замало даних для формування вікна аналізу";
        return report;
    }

    size_t motor_sat_count = 0;
    size_t mag_fault_count = 0;
    size_t sensor_freeze_count = 0;
    float prev_gyro = frames[0].gyro_x_rads;

    for (size_t i = 0; i < count; i++) {
        const TelemetryFrame *f = &frames[i];

        // 1. Провал напруги батареї (Brownout)
        if (f->bat_voltage_v < 13.2f && f->bat_current_a > 25.0f) {
            report.fault = FAULT_BROWNOUT_VOLTAGE_SAG;
            report.timestamp_us = f->timestamp_us;
            report.confidence = 0.95f;
            report.description = "Критичне просідання напруги батареї (Brownout) під струмовим навантаженням";
            return report;
        }

        // 2. Апаратне зависання шини або мікросхеми давача
        if ((f->sensor_status_mask & 0x01) == 0) {
            report.fault = FAULT_SENSOR_BUS_LOCKUP;
            report.timestamp_us = f->timestamp_us;
            report.confidence = 1.0f;
            report.description = "Апаратна відмова шини IMU (I2C/SPI timeout або втрата зв'язку)";
            return report;
        }

        if (i > 0 && fabsf(f->gyro_x_rads - prev_gyro) < 1e-6f) {
            sensor_freeze_count++;
            if (sensor_freeze_count > 25) {
                report.fault = FAULT_SENSOR_BUS_LOCKUP;
                report.timestamp_us = f->timestamp_us;
                report.confidence = 0.90f;
                report.description = "Застигання показів гіроскопа (Sensor freeze) на постійному значенні";
                return report;
            }
        } else {
            sensor_freeze_count = 0;
        }
        prev_gyro = f->gyro_x_rads;

        // 3. Відмова мотора / регулятора ESC
        bool motor_saturated = false;
        if ((f->motor_out[0] > 0.98f && f->motor_out[1] < 0.05f) ||
            (f->motor_out[1] > 0.98f && f->motor_out[0] < 0.05f)) {
            motor_saturated = true;
        }

        if (motor_saturated && is_angle_diverging(f->roll_des_deg, f->roll_act_deg, 20.0f)) {
            motor_sat_count++;
            if (motor_sat_count > 15) { // ~150 мс стійкого насичення при 100 Гц
                report.fault = FAULT_MOTOR_ESC_LOSS;
                report.timestamp_us = f->timestamp_us;
                report.confidence = 0.98f;
                report.description = "Відмова мотора або ESC: насичення виходу 100%/0% при зростаючій помилці крену";
                return report;
            }
        } else {
            motor_sat_count = (motor_sat_count > 0) ? motor_sat_count - 1 : 0;
        }

        // 4. Магнітна завада від струмових кіл
        if (f->ekf_mag_innov > 0.45f && f->bat_current_a > 30.0f) {
            if (is_angle_diverging(f->yaw_des_deg, f->yaw_act_deg, 15.0f)) {
                mag_fault_count++;
                if (mag_fault_count > 20) {
                    report.fault = FAULT_MAGNETIC_INTERFERENCE;
                    report.timestamp_us = f->timestamp_us;
                    report.confidence = 0.92f;
                    report.description = "Розходження курсу через магнітні наведення силового струму на компас";
                    return report;
                }
            }
        } else {
            mag_fault_count = (mag_fault_count > 0) ? mag_fault_count - 1 : 0;
        }
    }

    return report;
}
