#ifndef PREFLIGHT_H
#define PREFLIGHT_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "telemetry.h"

/* Пороги допуску — рівно ті, що описані в шести бар'єрах статті.
   Тримаємо їх в одному місці: польотна група має бачити цифру,
   а не шукати її по гілках коду. */
#define PF_GPS_MIN_FIX        3       /* 3D-Fix і вище */
#define PF_GPS_MIN_SATS       12
#define PF_GPS_MAX_HDOP       1.20f
#define PF_EKF_MAX_INNOV      0.30f
#define PF_BAT_MIN_VOLTAGE    14.8f   /* 4S LiPo під навантаженням */
#define PF_BAT_MAX_CELL_DELTA 0.05f
#define PF_BAT_MIN_TEMP_C     5.0f
#define PF_BAT_MAX_TEMP_C     50.0f
#define PF_FENCE_MIN_POINTS   4
#define PF_RC_MIN_RSSI_DBM    (-85)
#define PF_KILL_PWM_MIN       980     /* безпечне положення тумблера ≈ 1000 мкс */
#define PF_KILL_PWM_MAX       1050
#define PF_VIBE_MAX           0.40f

#define PF_MAX_REASONS  16
#define PF_REASON_LEN   128

/* Побітові прапорці пройдених бар'єрів безпеки */
typedef enum {
    CHECK_GPS_FIX_OK       = 1u << 0,
    CHECK_EKF_HEALTHY      = 1u << 1,
    CHECK_BATTERY_OK       = 1u << 2,
    CHECK_GEOFENCE_ACTIVE  = 1u << 3,
    CHECK_RC_KILLSWITCH_OK = 1u << 4,
    CHECK_VIBRATION_OK     = 1u << 5
} PreflightCheckMask;

#define PF_ALL_CHECKS (CHECK_GPS_FIX_OK | CHECK_EKF_HEALTHY | CHECK_BATTERY_OK | \
                       CHECK_GEOFENCE_ACTIVE | CHECK_RC_KILLSWITCH_OK | CHECK_VIBRATION_OK)

/* Результат передпольотної діагностики */
typedef struct {
    bool     is_go;              /* true = GO, false = NO-GO */
    uint32_t passed_mask;        /* Маска успішно пройдених бар'єрів */
    uint8_t  failure_count;      /* Скільки пояснень записано */
    uint8_t  dropped_count;      /* Скільки не вмістилося в буфер */
    char     reasons[PF_MAX_REASONS][PF_REASON_LEN];
} PreflightReport;

/* Проганяє зліпок крізь усі шість бар'єрів. Перша ж невдача НЕ спиняє
   перевірку: польотній групі потрібен повний перелік зауважень за один
   захід, а не по одному дефекту на запуск. */
PreflightReport run_preflight_validation(const VehicleTelemetryState *telemetry);

/* Друкує звіт: рядок стану, стовпчик бар'єрів, деталізацію відхилень */
void print_report(const PreflightReport *report, FILE *out);

#endif /* PREFLIGHT_H */
