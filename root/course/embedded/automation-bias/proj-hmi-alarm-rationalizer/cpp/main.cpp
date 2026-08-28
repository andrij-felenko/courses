#include "alarm_rationalizer.hpp"
#include "plausibility_checker.hpp"
#include <iostream>
#include <iomanip>

int main() {
    using namespace isa18_2;
    using namespace std::chrono_literals;

    std::cout << "=== Диспетчер та раціоналізатор тривог ISA-18.2 (C++20) ===\n\n";

    AlarmRationalizer ar;

    /* 1. Реєстрація первинної тривоги: Втрата головної шини живлення 28V */
    ar.register_alarm({
        .id = 0,
        .tag = "PWR_MAIN_BUS_UV",
        .action_text = "Увімкнути резервний акумулятор, перевірити інвертор",
        .consequence = "Повна втрата живлення корисного навантаження та зв'язку",
        .priority = AlarmPriority::Critical,
        .category = AlarmCategory::Safety,
        .response_time_limit = 10000ms,
        .trip_threshold = 22.0f,
        .clear_threshold = 24.5f,
        .is_high_alarm = false,
        .on_delay = 100ms,
        .off_delay = 500ms,
        .chatter_limit = 3,
        .chatter_window = 5000ms,
        .suppression_mask = SystemStateMask::ColdBoot | SystemStateMask::Maintenance,
        .parent_alarm_id = std::nullopt
    });

    /* 2. Реєстрація вторинної тривоги: Втрата телеметрії лідара (Parent ID = 0) */
    ar.register_alarm({
        .id = 1,
        .tag = "LIDAR_COMM_LOST",
        .action_text = "Перевірити живлення та кабель RS-485 лідара",
        .consequence = "Неможливість побудови карти перешкод на малій висоті",
        .priority = AlarmPriority::Medium,
        .category = AlarmCategory::Communication,
        .response_time_limit = 60000ms,
        .trip_threshold = 0.5f,
        .clear_threshold = 0.5f,
        .is_high_alarm = false,
        .on_delay = 500ms,
        .off_delay = 1000ms,
        .chatter_limit = 4,
        .chatter_window = 10000ms,
        .suppression_mask = SystemStateMask::ColdBoot | SystemStateMask::Standby,
        .parent_alarm_id = 0
    });

    /* 3. Реєстрація діагностичної тривоги достовірності сенсорів */
    ar.register_alarm({
        .id = 2,
        .tag = "SENSOR_PLAUSIBILITY_WARN",
        .action_text = "Звірити первинні прилади, перейти на ручне керування",
        .consequence = "Сліпа довіра до здеградованого фільтра EKF спричинить зіткнення",
        .priority = AlarmPriority::High,
        .category = AlarmCategory::SensorHealth,
        .response_time_limit = 15000ms,
        .trip_threshold = 0.50f,
        .clear_threshold = 0.75f,
        .is_high_alarm = false,
        .on_delay = 200ms,
        .off_delay = 1000ms,
        .chatter_limit = 3,
        .chatter_window = 5000ms,
        .suppression_mask = SystemStateMask::ColdBoot,
        .parent_alarm_id = std::nullopt
    });

    PlausibilityChecker pc({
        .max_allowed_accel_jerk = 15.0f,
        .max_kinematic_residual = 3.5f,
        .max_power_residual_w = 45.0f,
        .min_confidence_alarm_threshold = 0.50f,
        .diagnostic_alarm_id = 2
    });

    std::cout << "[1] Перехід системи у робочий режим SYS_STATE_MISSION (now = 1000 ms)\n";
    ar.set_system_state(SystemStateMask::Mission, 1000ms);

    ar.update_value(0, 27.8f, 1000ms);
    ar.update_value(1, 1.0f, 1000ms);
    pc.check_battery_power(27.8f, 12.0f, 330.0f, 1000ms);
    pc.check_kinematics(0.2f, 15.0f, 1000ms);
    pc.sync_to_rationalizer(ar, 1000ms);
    ar.process(1000ms);

    std::cout << "   Активних тривог на HMI: " << ar.get_active_hmi_alarms().size() << "\n";

    /* Симуляція аварії живлення */
    std::cout << "\n[2] Аварія шини живлення 28V (падає до 19.5V, now = 2000 ms)\n";
    ar.update_value(0, 19.5f, 2000ms);
    ar.update_value(1, 0.0f, 2000ms);
    ar.process(2200ms);

    auto active = ar.get_active_hmi_alarms();
    std::cout << "   Активних тривог на HMI: " << active.size() << "\n";
    for (auto id : active) {
        const auto& cfg = ar.get_config(id);
        const auto& rt = ar.get_runtime(id);
        std::cout << "   -> [" << cfg.tag << "] Стан=" << static_cast<int>(rt.state)
                  << ", Пріоритет=" << static_cast<int>(cfg.priority)
                  << ", Дія=\"" << cfg.action_text << "\"\n";
    }

    std::cout << "   Стан вторинної тривоги LIDAR_COMM_LOST (ID 1): Стан="
              << static_cast<int>(ar.get_runtime(1).state)
              << " (SuppressedByParent=" << (ar.get_runtime(1).is_suppressed_by_parent ? "ТАК" : "НІ") << ")\n";

    /* Квитування оператором */
    std::cout << "\n[3] Оператор квитує PWR_MAIN_BUS_UV (now = 3000 ms)\n";
    ar.acknowledge(0, 3000ms);
    ar.process(3000ms);
    std::cout << "   Стан після ACK: " << static_cast<int>(ar.get_runtime(0).state) << " (AcknowledgedAlarm)\n";

    /* Симуляція спуфінгу GNSS */
    std::cout << "\n[4] Симуляція спуфінгу GNSS: розбіжність прискорення IMU та GNSS (now = 4000 ms)\n";
    pc.check_kinematics(0.1f, 35.0f, 4000ms);
    pc.sync_to_rationalizer(ar, 4000ms);
    ar.process(4500ms);

    const auto& nav_est = pc.nav_velocity_confidence();
    std::cout << "   Оцінка швидкості: " << std::fixed << std::setprecision(1) << nav_est.estimated_value
              << " м/с, Довірчий інтервал 95%: +/-" << std::setprecision(2) << nav_est.confidence_bound_95
              << " м/с, Достовірність=" << nav_est.confidence_score
              << " (Статус=" << static_cast<int>(nav_est.status) << ")\n";

    active = ar.get_active_hmi_alarms();
    std::cout << "   Активних тривог на HMI після збою достовірності: " << active.size() << "\n";
    for (auto id : active) {
        const auto& cfg = ar.get_config(id);
        const auto& rt = ar.get_runtime(id);
        std::cout << "   -> [" << cfg.tag << "] Стан=" << static_cast<int>(rt.state)
                  << ", Пріоритет=" << static_cast<int>(cfg.priority)
                  << ", Дія=\"" << cfg.action_text << "\"\n";
    }

    std::cout << "\nПідсумок: Раціоналізація ISA-18.2 та оцінка достовірності працюють узгоджено.\n";
    return 0;
}
