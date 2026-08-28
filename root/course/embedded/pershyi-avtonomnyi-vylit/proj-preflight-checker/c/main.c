#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_REASONS 8
#define REASON_BUF_LEN 96

/* Побітові прапорці критичних підсистем безпеки */
typedef enum {
    CHECK_GPS_FIX_OK       = (1 << 0),
    CHECK_EKF_HEALTHY      = (1 << 1),
    CHECK_BATTERY_OK       = (1 << 2),
    CHECK_GEOFENCE_ACTIVE  = (1 << 3),
    CHECK_RC_KILLSWITCH_OK = (1 << 4),
    CHECK_VIBRATION_OK     = (1 << 5)
} PreflightCheckMask;

/* Телеметричні параметри, зчитані з борту перед армінгом */
typedef struct {
    uint8_t  gps_fix_type;      /* 3 = 3D Fix, 4 = DGPS, 5 = RTK Float, 6 = RTK Fixed */
    uint8_t  gps_satellites;    /* Кількість захоплених супутників */
    float    gps_hdop;          /* Horizontal Dilution of Precision */
    
    float    ekf_pos_innov;     /* Нормована похибка інновації позиції EKF (0.0 .. 1.0) */
    float    ekf_vel_innov;     /* Нормована похибка інновації швидкості EKF */
    float    ekf_yaw_innov;     /* Нормована похибка інновації курсу EKF */
    
    float    battery_voltage;   /* Загальна напруга силового акумулятора (В) */
    float    cell_delta_v;      /* Максимальна різниця напруг між осередками (В) */
    float    battery_temp_c;    /* Температура акумулятора (°C) */
    
    bool     geofence_enabled;  /* Чи активована жорстка геозона в параметрах */
    uint16_t geofence_points;   /* Кількість завантажених точок межі полігону */
    uint8_t  geofence_action;   /* 1 = RTL, 2 = Land, 3 = Terminate */
    
    int16_t  rc_rssi_dbm;       /* Рівень сигналу пульта керування (дБм) */
    uint16_t rc_kill_channel;   /* Значення ШІМ аварійного каналу (1000..2000 мкс) */
    
    float    acc_vibe_floor;    /* Фонова амплітуда шуму акселерометра в спокої (м/с²) */
} VehicleTelemetryState;

/* Результат передпольотної діагностики */
typedef struct {
    bool     is_go;             /* Загальний дозвіл на виліт (true = GO, false = NO-GO) */
    uint32_t passed_mask;       /* Маска успішно пройдених перевірок */
    uint8_t  failure_count;     /* Кількість виявлених дефектів */
    char     reasons[MAX_REASONS][REASON_BUF_LEN]; /* Текстові пояснення відхилень */
} PreflightReport;

static void add_failure(PreflightReport *rep, const char *msg) {
    if (rep->failure_count < MAX_REASONS) {
        strncpy(rep->reasons[rep->failure_count], msg, REASON_BUF_LEN - 1);
        rep->reasons[rep->failure_count][REASON_BUF_LEN - 1] = '\0';
        rep->failure_count++;
    }
    rep->is_go = false;
}

PreflightReport run_preflight_validation(const VehicleTelemetryState *telemetry) {
    PreflightReport report;
    memset(&report, 0, sizeof(PreflightReport));
    report.is_go = true;

    /* 1. Перевірка навігаційної підсистеми GNSS */
    if (telemetry->gps_fix_type >= 3 && telemetry->gps_satellites >= 12 && telemetry->gps_hdop <= 1.20f) {
        report.passed_mask |= CHECK_GPS_FIX_OK;
    } else {
        add_failure(&report, "GNSS: Недостатня точність (вимагається 3D-Fix, sats >= 12, HDOP <= 1.20)");
    }

    /* 2. Перевірка здоров'я розширеного фільтра Калмана */
    if (telemetry->ekf_pos_innov < 0.30f && telemetry->ekf_vel_innov < 0.30f && telemetry->ekf_yaw_innov < 0.30f) {
        report.passed_mask |= CHECK_EKF_HEALTHY;
    } else {
        add_failure(&report, "EKF: Розходження інновацій перевищує поріг 0.30 (дрейф оцінки стану)");
    }

    /* 3. Перевірка живлення */
    if (telemetry->battery_voltage >= 14.8f && telemetry->cell_delta_v <= 0.05f &&
        telemetry->battery_temp_c >= 5.0f && telemetry->battery_temp_c <= 50.0f) {
        report.passed_mask |= CHECK_BATTERY_OK;
    } else {
        add_failure(&report, "BATTERY: Небезпечний рівень напруги, перекіс осередків > 0.05 В або мороз");
    }

    /* 4. Перевірка жорсткої геозони */
    if (telemetry->geofence_enabled && telemetry->geofence_points >= 4 && telemetry->geofence_action >= 1) {
        report.passed_mask |= CHECK_GEOFENCE_ACTIVE;
    } else {
        add_failure(&report, "GEOFENCE: Геозона не активована або містить менше 4 опорних точок");
    }

    /* 5. Перевірка каналу аварійного відключення (Kill Switch) */
    if (telemetry->rc_rssi_dbm >= -85 && telemetry->rc_kill_channel >= 980 && telemetry->rc_kill_channel <= 1050) {
        report.passed_mask |= CHECK_RC_KILLSWITCH_OK;
    } else {
        add_failure(&report, "SAFETY: Тумблер Kill Switch активований або зв'язок пульта слабкий (< -85 дБм)");
    }

    /* 6. Перевірка статичного шуму акселерометра */
    if (telemetry->acc_vibe_floor <= 0.40f) {
        report.passed_mask |= CHECK_VIBRATION_OK;
    } else {
        add_failure(&report, "IMU: Підвищений рівень фонових вібрацій (перевірити демпфери автопілота)");
    }

    return report;
}

void print_report(const PreflightReport *report) {
    if (report->is_go) {
        printf("==========================================\n");
        printf(">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ GO ] <<<\n");
        printf("Усі 6 систем безпеки валідовано. Дозвіл на ARM надано.\n");
        printf("==========================================\n");
    } else {
        printf("==========================================\n");
        printf(">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ NO-GO ] <<<\n");
        printf("Виявлено критичні блокування (%u відхилень):\n", report->failure_count);
        for (uint8_t i = 0; i < report->failure_count; i++) {
            printf("  [!] %s\n", report->reasons[i]);
        }
        printf("Старт категорично заборонено до усунення зауважень!\n");
        printf("==========================================\n");
    }
}
