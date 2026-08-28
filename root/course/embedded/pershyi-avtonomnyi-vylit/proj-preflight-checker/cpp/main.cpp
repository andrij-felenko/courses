#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <cstdint>

enum class CheckFlag : uint32_t {
    GpsOk        = 1 << 0,
    EkfOk        = 1 << 1,
    BatteryOk    = 1 << 2,
    GeofenceOk   = 1 << 3,
    KillSwitchOk = 1 << 4,
    VibrationOk  = 1 << 5
};

struct TelemetrySnapshot {
    uint8_t     gps_fix_type{0};
    uint8_t     gps_satellites{0};
    float       gps_hdop{99.0f};

    float       ekf_pos_innov{1.0f};
    float       ekf_vel_innov{1.0f};
    float       ekf_yaw_innov{1.0f};

    float       battery_voltage{0.0f};
    float       cell_delta_v{0.0f};
    float       battery_temp_c{0.0f};

    bool        geofence_enabled{false};
    uint16_t    geofence_points{0};
    uint8_t     geofence_action{0};

    int16_t     rc_rssi_dbm{-120};
    uint16_t    rc_kill_channel{0};

    float       acc_vibe_floor{0.0f};
};

struct PreflightResult {
    bool                     is_go{true};
    uint32_t                 passed_mask{0};
    std::vector<std::string> failures;

    void add_failure(std::string_view reason) {
        failures.emplace_back(reason);
        is_go = false;
    }
};

class PreflightValidator {
public:
    static PreflightResult evaluate(const TelemetrySnapshot& state) {
        PreflightResult result;

        // 1. Валідація GNSS
        if (state.gps_fix_type >= 3 && state.gps_satellites >= 12 && state.gps_hdop <= 1.20f) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::GpsOk);
        } else {
            result.add_failure("GNSS: Недостатня точність (вимагається 3D-Fix, sats >= 12, HDOP <= 1.20)");
        }

        // 2. Валідація фільтра Калмана (EKF)
        if (state.ekf_pos_innov < 0.30f && state.ekf_vel_innov < 0.30f && state.ekf_yaw_innov < 0.30f) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::EkfOk);
        } else {
            result.add_failure("EKF: Розходження інновацій перевищує поріг 0.30 (дрейф оцінки стану)");
        }

        // 3. Валідація акумулятора
        if (state.battery_voltage >= 14.8f && state.cell_delta_v <= 0.05f &&
            state.battery_temp_c >= 5.0f && state.battery_temp_c <= 50.0f) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::BatteryOk);
        } else {
            result.add_failure("BATTERY: Небезпечний рівень напруги, перекіс осередків > 0.05 В або мороз");
        }

        // 4. Валідація жорсткої геозони
        if (state.geofence_enabled && state.geofence_points >= 4 && state.geofence_action >= 1) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::GeofenceOk);
        } else {
            result.add_failure("GEOFENCE: Геозона не активована або містить менше 4 опорних точок");
        }

        // 5. Валідація апаратного каналу перехоплення / Kill Switch
        if (state.rc_rssi_dbm >= -85 && state.rc_kill_channel >= 980 && state.rc_kill_channel <= 1050) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::KillSwitchOk);
        } else {
            result.add_failure("SAFETY: Тумблер Kill Switch активований або зв'язок пульта слабкий (< -85 дБм)");
        }

        // 6. Валідація фонового вібраційного шуму
        if (state.acc_vibe_floor <= 0.40f) {
            result.passed_mask |= static_cast<uint32_t>(CheckFlag::VibrationOk);
        } else {
            result.add_failure("IMU: Підвищений рівень фонових вібрацій (перевірити демпфери автопілота)");
        }

        return result;
    }
};

void print_diagnostic_report(const PreflightResult& report) {
    if (report.is_go) {
        std::cout << "==========================================\n"
                  << ">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ GO ] <<<\n"
                  << "Усі 6 систем безпеки валідовано. Дозвіл на ARM надано.\n"
                  << "==========================================\n";
    } else {
        std::cout << "==========================================\n"
                  << ">>> СТАТУС ПЕРЕДПОЛЬОТНОГО АУДИТУ: [ NO-GO ] <<<\n"
                  << "Виявлено критичні блокування (" << report.failures.size() << " відхилень):\n";
        for (const auto& reason : report.failures) {
            std::cout << "  [!] " << reason << "\n";
        }
        std::cout << "Старт категорично заборонено до усунення зауважень!\n"
                  << "==========================================\n";
    }
}
