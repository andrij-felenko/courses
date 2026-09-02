#include "preflight.h"

#include <stdarg.h>
#include <string.h>

static const struct {
    uint32_t    flag;
    const char *name;
} BARRIERS[] = {
    { CHECK_GPS_FIX_OK,       "GNSS"     },
    { CHECK_EKF_HEALTHY,      "EKF"      },
    { CHECK_BATTERY_OK,       "Живлення" },
    { CHECK_GEOFENCE_ACTIVE,  "Геозона"  },
    { CHECK_RC_KILLSWITCH_OK, "RC/Kill"  },
    { CHECK_VIBRATION_OK,     "Вібрації" }
};

#define BARRIER_COUNT (sizeof BARRIERS / sizeof BARRIERS[0])

static void fail(PreflightReport *rep, const char *fmt, ...)
{
    rep->is_go = false;

    if (rep->failure_count >= PF_MAX_REASONS) {
        if (rep->dropped_count < UINT8_MAX) {
            rep->dropped_count++;
        }
        return;
    }

    va_list ap;
    va_start(ap, fmt);
    vsnprintf(rep->reasons[rep->failure_count], PF_REASON_LEN, fmt, ap);
    va_end(ap);
    rep->failure_count++;
}

/* Порівняння скрізь записані як !(значення <= поріг): NaN, що просочився
   повз парсер, тоді валить перевірку, а не проходить її мовчки. */

static bool check_gnss(const VehicleTelemetryState *t, PreflightReport *rep)
{
    bool ok = true;

    if (t->gps_fix_type < PF_GPS_MIN_FIX) {
        fail(rep, "GNSS: тип рішення %u, потрібен щонайменше 3D-Fix (%d)",
             (unsigned)t->gps_fix_type, PF_GPS_MIN_FIX);
        ok = false;
    }
    if (t->gps_satellites < PF_GPS_MIN_SATS) {
        fail(rep, "GNSS: у рішенні %u супутників, потрібно %d",
             (unsigned)t->gps_satellites, PF_GPS_MIN_SATS);
        ok = false;
    }
    if (!(t->gps_hdop <= PF_GPS_MAX_HDOP)) {
        fail(rep, "GNSS: HDOP %.2f перевищує допуск %.2f (похибка кілька метрів)",
             (double)t->gps_hdop, (double)PF_GPS_MAX_HDOP);
        ok = false;
    }
    return ok;
}

static bool check_ekf(const VehicleTelemetryState *t, PreflightReport *rep)
{
    static const char *const AXIS[] = { "позиції", "швидкості", "курсу" };
    const float innov[] = { t->ekf_pos_innov, t->ekf_vel_innov, t->ekf_yaw_innov };
    bool ok = true;

    for (size_t i = 0; i < sizeof innov / sizeof innov[0]; i++) {
        if (!(innov[i] < PF_EKF_MAX_INNOV)) {
            fail(rep, "EKF: інновація %s %.2f при порозі %.2f (дрейф оцінки стану)",
                 AXIS[i], (double)innov[i], (double)PF_EKF_MAX_INNOV);
            ok = false;
        }
    }
    return ok;
}

static bool check_battery(const VehicleTelemetryState *t, PreflightReport *rep)
{
    bool ok = true;

    if (!(t->battery_voltage >= PF_BAT_MIN_VOLTAGE)) {
        fail(rep, "Живлення: напруга шини %.2f В нижча за %.2f В",
             (double)t->battery_voltage, (double)PF_BAT_MIN_VOLTAGE);
        ok = false;
    }
    if (!(t->cell_delta_v <= PF_BAT_MAX_CELL_DELTA)) {
        fail(rep, "Живлення: перекіс осередків %.3f В понад %.3f В — акумулятор зняти",
             (double)t->cell_delta_v, (double)PF_BAT_MAX_CELL_DELTA);
        ok = false;
    }
    if (!(t->battery_temp_c >= PF_BAT_MIN_TEMP_C)) {
        fail(rep, "Живлення: акумулятор %.1f °C, нижче за %.1f °C електрохімія загальмована",
             (double)t->battery_temp_c, (double)PF_BAT_MIN_TEMP_C);
        ok = false;
    }
    if (!(t->battery_temp_c <= PF_BAT_MAX_TEMP_C)) {
        fail(rep, "Живлення: акумулятор перегрітий, %.1f °C понад %.1f °C",
             (double)t->battery_temp_c, (double)PF_BAT_MAX_TEMP_C);
        ok = false;
    }
    return ok;
}

static bool check_geofence(const VehicleTelemetryState *t, PreflightReport *rep)
{
    bool ok = true;

    if (!t->geofence_enabled) {
        fail(rep, "Геозона: полігон завантажено, але примусовий контроль меж вимкнено");
        ok = false;
    }
    if (t->geofence_points < PF_FENCE_MIN_POINTS) {
        fail(rep, "Геозона: %u вершин, замкнений контур вимагає щонайменше %d",
             (unsigned)t->geofence_points, PF_FENCE_MIN_POINTS);
        ok = false;
    }
    if (t->geofence_action < 1) {
        fail(rep, "Геозона: дію при порушенні межі не задано (потрібно RTL або посадку)");
        ok = false;
    }
    return ok;
}

static bool check_safety(const VehicleTelemetryState *t, PreflightReport *rep)
{
    bool ok = true;

    if (t->rc_rssi_dbm < PF_RC_MIN_RSSI_DBM) {
        fail(rep, "RC: рівень сигналу %d дБм на стоянці нижчий за %d дБм",
             (int)t->rc_rssi_dbm, PF_RC_MIN_RSSI_DBM);
        ok = false;
    }
    if (t->rc_kill_channel < PF_KILL_PWM_MIN || t->rc_kill_channel > PF_KILL_PWM_MAX) {
        fail(rep, "Kill: аварійний канал %u мкс поза вікном готовності %d..%d мкс",
             (unsigned)t->rc_kill_channel, PF_KILL_PWM_MIN, PF_KILL_PWM_MAX);
        ok = false;
    }
    return ok;
}

static bool check_vibration(const VehicleTelemetryState *t, PreflightReport *rep)
{
    if (!(t->acc_vibe_floor <= PF_VIBE_MAX)) {
        fail(rep, "IMU: фоновий шум %.2f м/с² при нерухомих гвинтах, поріг %.2f",
             (double)t->acc_vibe_floor, (double)PF_VIBE_MAX);
        return false;
    }
    return true;
}

PreflightReport run_preflight_validation(const VehicleTelemetryState *telemetry)
{
    PreflightReport report;
    memset(&report, 0, sizeof report);
    report.is_go = true;

    if (check_gnss(telemetry, &report))      report.passed_mask |= CHECK_GPS_FIX_OK;
    if (check_ekf(telemetry, &report))       report.passed_mask |= CHECK_EKF_HEALTHY;
    if (check_battery(telemetry, &report))   report.passed_mask |= CHECK_BATTERY_OK;
    if (check_geofence(telemetry, &report))  report.passed_mask |= CHECK_GEOFENCE_ACTIVE;
    if (check_safety(telemetry, &report))    report.passed_mask |= CHECK_RC_KILLSWITCH_OK;
    if (check_vibration(telemetry, &report)) report.passed_mask |= CHECK_VIBRATION_OK;

    return report;
}

void print_report(const PreflightReport *report, FILE *out)
{
    static const char *const RULE = "==========================================";

    fprintf(out, "%s\n", RULE);
    fprintf(out, ">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ %s ] <<<\n",
            report->is_go ? "GO" : "NO-GO");

    for (size_t i = 0; i < BARRIER_COUNT; i++) {
        bool passed = (report->passed_mask & BARRIERS[i].flag) != 0u;
        fprintf(out, "  [%s] %s\n", passed ? " OK " : "FAIL", BARRIERS[i].name);
    }

    if (report->is_go) {
        fprintf(out, "Усі шість бар'єрів пройдено. Дозвіл на ARM надано.\n");
    } else {
        fprintf(out, "Виявлено критичні блокування (%u):\n", (unsigned)report->failure_count);
        for (uint8_t i = 0; i < report->failure_count; i++) {
            fprintf(out, "  [!] %s\n", report->reasons[i]);
        }
        if (report->dropped_count > 0) {
            fprintf(out, "  [!] ще %u відхилень не вмістилося у звіт\n",
                    (unsigned)report->dropped_count);
        }
        fprintf(out, "Старт заборонено до усунення зауважень!\n");
    }
    fprintf(out, "%s\n", RULE);
}
