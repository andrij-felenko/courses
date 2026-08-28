#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <math.h>

#define MAX_MOTORS 4
#define AXIS_ROLL  0
#define AXIS_PITCH 1
#define AXIS_YAW   2

typedef struct {
    uint64_t timestamp_us;
    float setpoint_rate[3];         /* deg/s: Roll, Pitch, Yaw */
    float gyro_rate[3];             /* deg/s: Roll, Pitch, Yaw */
    float pid_p_term[3];            /* Пропорційна складова */
    float pid_i_term[3];            /* Інтегральна складова [-1000..1000] */
    float pid_d_term[3];            /* Диференційна складова */
    float motor_output[MAX_MOTORS]; /* Відносна тяга [0.0 .. 1.0] */
    float vbat_v;                   /* Напруга батареї у вольтах */
    float ibat_a;                   /* Струм споживання в амперах */
} blackbox_frame_t;

typedef enum {
    ANOMALY_NONE             = 0,
    ANOMALY_TRACKING_LOSS    = (1 << 0),
    ANOMALY_MIXER_SATURATION = (1 << 1),
    ANOMALY_MOTOR_DESYNC     = (1 << 2),
    ANOMALY_BROWNOUT         = (1 << 3)
} anomaly_flags_t;

typedef struct {
    float tracking_error_threshold_deg; /* Поріг кутової похибки (напр. 45.0 град/с) */
    float desync_motor_min_throttle;    /* Мінімальна тяга мотора для десинхрону (0.95) */
    uint32_t min_anomaly_duration_us;   /* Мінімальна тривалість події (20000 мкс) */
    float brownout_voltage_threshold_v; /* Поріг напруги BOD (напр. 6.0 В для 6S) */
} analyzer_config_t;

typedef struct {
    uint64_t start_time_us;
    uint64_t end_time_us;
    uint32_t flags;
    uint8_t failed_motor_index;
    float max_error_deg;
    float min_vbat_v;
} crash_incident_report_t;
