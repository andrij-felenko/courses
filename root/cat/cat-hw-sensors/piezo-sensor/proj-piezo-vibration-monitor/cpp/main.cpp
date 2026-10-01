#include <iostream>
#include <iomanip>
#include "vibration_monitor.hpp"

// Конвертація стану автомата в текстовий рядок для виводу
static const char* relayStateToString(RelayState state) {
    switch (state) {
        case RelayState::NORMAL:         return "NORMAL (Норма)";
        case RelayState::TRIP_DELAY:     return "TRIP_DELAY (Затримка тривоги)";
        case RelayState::ALARM:          return "ALARM (Аварія / Реле УВІМК)";
        case RelayState::RECOVERY_DELAY: return "RECOVERY_DELAY (Відновлення)";
        default:                         return "НЕВІДОМО";
    }
}

// Функція симуляції вхідного сигналу від п'єзодатчика на АЦП
static uint16_t simulateAdcStream(uint32_t time_ms) {
    // 0..800 мс: Спокійний стан, фоновий шум (АЦП 20..80)
    if (time_ms < 800) {
        return static_cast<uint16_t>(30 + (time_ms % 50));
    }
    // 800..900 мс: Короткочасний завадовий імпульс (АЦП 750), < trip_delay (200 мс)
    else if (time_ms >= 800 && time_ms < 900) {
        return 750;
    }
    // 900..1800 мс: Повернення до норми
    else if (time_ms >= 900 && time_ms < 1800) {
        return static_cast<uint16_t>(40 + (time_ms % 30));
    }
    // 1800..3200 мс: Тривалий вібраційний удар (АЦП 1200..1400), тривалість 1400 мс > 200 мс
    else if (time_ms >= 1800 && time_ms < 3200) {
        return static_cast<uint16_t>(1200 + (time_ms % 200));
    }
    // 3200..5000 мс: Поступове згасання вібрації
    else {
        return 20;
    }
}

int main() {
    // Конфігурація фільтрації огинаючої сплесків
    PeakFilterConfig filter_cfg;
    filter_cfg.decay_factor = 0.95f;   // Коефіцієнт згасання (0.95 = ~5% згасання на крок)
    filter_cfg.noise_floor = 50;       // Відсікання фонового шуму АЦП

    // Конфігурація порогів та затримок реле
    RelayProtectionConfig relay_cfg;
    relay_cfg.alarm_threshold = 500;    // Поріг спрацьовування тривоги
    relay_cfg.recovery_threshold = 200; // Поріг гістерезису для зняття тривоги
    relay_cfg.trip_delay_ms = 200;      // Затримка тривоги (200 мс) для відсікання завад
    relay_cfg.recovery_delay_ms = 500;  // Затримка відновлення (500 мс) для захисту реле від дребезгу

    // Ініціалізація об'єкта монітора вібрації
    VibrationMonitor monitor(filter_cfg, relay_cfg);

    std::cout << "=== Система моніторингу вібраційного навантаження ===" << std::endl;
    std::cout << "Параметри: Alarm Threshold=" << relay_cfg.alarm_threshold
              << ", Recovery Threshold=" << relay_cfg.recovery_threshold
              << ", Trip Delay=" << relay_cfg.trip_delay_ms << "ms"
              << ", Recovery Delay=" << relay_cfg.recovery_delay_ms << "ms\n" << std::endl;

    std::cout << std::setw(10) << "Час (мс)"
              << std::setw(12) << "АЦП raw"
              << std::setw(15) << "Огинаюча"
              << std::setw(30) << "Стан автомата" << std::endl;
    std::cout << "------------------------------------------------------------------" << std::endl;

    RelayState prev_state = monitor.getRelayState();

    // Симуляція неблокуючого суперциклу (loop) з кроком вибірки 50 мс
    uint32_t current_time_ms = 0;
    const uint32_t step_ms = 50;
    const uint32_t total_simulation_time_ms = 5000;

    while (current_time_ms <= total_simulation_time_ms) {
        uint16_t raw_adc = simulateAdcStream(current_time_ms);

        // Періодичний виклик методів монітора в суперциклі
        monitor.update(raw_adc, current_time_ms);

        RelayState current_state = monitor.getRelayState();

        // Логування стану при зміні автомата або періодично кожні 200 мс
        if (current_state != prev_state || (current_time_ms % 200 == 0)) {
            std::cout << std::setw(10) << current_time_ms
                      << std::setw(12) << raw_adc
                      << std::setw(15) << std::fixed << std::setprecision(1) << monitor.getPeakEnvelope()
                      << std::setw(30) << relayStateToString(current_state);

            if (current_state != prev_state) {
                std::cout << "  <-- ЗМІНА СТАНУ!";
                prev_state = current_state;
            }
            std::cout << std::endl;
        }

        current_time_ms += step_ms;
    }

    std::cout << "------------------------------------------------------------------" << std::endl;
    std::cout << "Симуляцію завершено." << std::endl;

    return 0;
}
