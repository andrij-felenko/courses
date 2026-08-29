#ifndef CRASHLOG_H
#define CRASHLOG_H

/* Аналізатор аварійних сигнатур польотного журналу.
 * Один публічний заголовок на всю утиліту: типи кадру й звіту,
 * розбір журналу (logload.c) і самі детектори (analyzer.c). */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define MAX_MOTORS 4

typedef enum {
    FAULT_NONE = 0,
    FAULT_MOTOR_ESC_LOSS,
    FAULT_MAGNETIC_INTERFERENCE,
    FAULT_BROWNOUT_VOLTAGE_SAG,
    FAULT_SENSOR_BUS_LOCKUP
} FaultType;

/* Один синхронізований кадр телеметрії: те, що лишається від ULog/DataFlash
 * після зведення потоків IMU, EKF, BAT і RCOU на спільну часову сітку. */
typedef struct {
    uint64_t timestamp_us;       /* мікросекунди від старту контролера */
    float roll_des_deg;          /* заданий крен (DesRoll) */
    float roll_act_deg;          /* фактичний крен (Roll) */
    float yaw_des_deg;           /* заданий курс (DesYaw) */
    float yaw_act_deg;           /* фактичний курс (Yaw) */
    float motor_out[MAX_MOTORS]; /* нормовані виходи на мотори [0.0 .. 1.0] */
    float bat_voltage_v;         /* напруга силової шини, В */
    float bat_current_a;         /* струм споживання, А */
    float ekf_mag_innov;         /* нормалізована нев'язка компаса в EKF */
    float gyro_x_rads;           /* кутова швидкість крену, рад/с */
    uint32_t sensor_status_mask; /* маска здоров'я давачів, біт 0 — IMU справний */
} TelemetryFrame;

/* Звіт про інцидент. Крім самої сигнатури тут лежать «контекстні мітки» —
 * події, які детектори свідомо ВІДКИНУЛИ як не-першопричину, але про які
 * інженерові треба знати: удар об перешкоду, зовнішня магнітна аномалія,
 * плавне вичерпання заряду. Нуль означає «такого не траплялося». */
typedef struct {
    FaultType fault;
    uint64_t timestamp_us;   /* мікросекундна мітка ПОЧАТКУ аномалії */
    float confidence;        /* коефіцієнт впевненості [0.0 .. 1.0] */
    const char *description;
    uint64_t impact_us;      /* різкий сплеск гіроскопа = зіткнення */
    uint64_t env_anomaly_us; /* магнітна аномалія середовища без власного струму */
    uint64_t depletion_us;   /* плавне просідання напруги наприкінці польоту */
    size_t frames_used;      /* кадрів прийнято до аналізу */
    size_t frames_skipped;   /* кадрів відкинуто: NaN, дубль або зсув часу назад */
} IncidentReport;

/* Головна функція: скан усього запису рухомим вікном. Повертає ПЕРШУ за часом
 * сигнатуру — саме вона й є першопричиною, решта вже наслідки падіння. */
IncidentReport analyze_incident(const TelemetryFrame *frames, size_t count);

const char *fault_name(FaultType fault);

/* Накопичувач кадрів, вичитаних із розпакованого журналу. */
typedef struct {
    TelemetryFrame *frames;
    size_t count;
    size_t capacity;
} FrameLog;

typedef struct {
    bool ok;
    size_t line;          /* рядок CSV, на якому спіткнулися (0 — файл цілком) */
    char message[160];
} LoadStatus;

/* Читає CSV, зведений із ULog/DataFlash утилітами розпакування
 * (pyulog, mavlogdump). Колонки шукаються ЗА ІМЕНЕМ у шапці, порядок довільний:
 * timestamp_us, roll_des, roll, yaw_des, yaw, mot0..mot3,
 * bat_v, bat_a, mag_innov, gyro_x і необов'язкова imu_status. */
LoadStatus log_load_csv(const char *path, FrameLog *out);
void log_free(FrameLog *log);

#endif /* CRASHLOG_H */
