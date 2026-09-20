#include <iostream>
#include <vector>
#include <iomanip>
#include "esc_control.hpp"

// Симулятор зчитування значення АЦП для заданої напруги BEC
static uint16_t simulateAdc(float target_voltage) {
    const float v_pin = std::min(target_voltage / esc::EscController::kDividerRatio,
                                esc::EscController::kVrefVolts);
    return static_cast<uint16_t>((v_pin * esc::EscController::kAdcMaxVal) / esc::EscController::kVrefVolts);
}

struct TestStep {
    float voltage;
    uint16_t requested_pulse;
    std::string_view note;
};

int main() {
    std::cout << "====================================================\n";
    std::cout << " C++ Драйвер ESC BLHeli 30A з моніторингом BEC\n";
    std::cout << "====================================================\n\n";

    esc::EscController controller;
    controller.init();

    std::cout << "Армовано: " << (controller.isArmed() ? "ТАК" : "НІ") << "\n";
    std::cout << "ШІМ при армуванні: " << controller.getPulseWidthUs() << " мкс\n\n";

    const std::vector<TestStep> steps = {
        {5.00f, 1150, "Старт двигуна, низькі оберти (1150 мкс)"},
        {4.90f, 1550, "Крейсерські оберти 55% (1550 мкс)"},
        {4.76f, 1950, "Максимальна потужність (1950 мкс)"},
        {4.60f, 1950, "Просідання напруги BEC до 4.60В (Попередження)"},
        {4.30f, 1800, "Критичне просідання 4.30В (Аварійне вимкнення)"},
        {5.00f, 1500, "Живлення відновилося, перевірка автоблокування"}
    };

    std::cout << std::fixed << std::setprecision(2);

    for (size_t i = 0; i < steps.size(); ++i) {
        const auto& step = steps[i];
        uint16_t raw_adc = simulateAdc(step.voltage);

        controller.process(raw_adc, step.requested_pulse);

        std::cout << "Крок " << (i + 1) << ": " << step.note << "\n";
        std::cout << "  АЦП сире: " << raw_adc
                  << " | BEC: " << controller.getBecVoltage() << " В"
                  << " | Стан: " << esc::EscController::statusToString(controller.getStatus()) << "\n";
        std::cout << "  Запит: " << step.requested_pulse << " мкс"
                  << " -> Фактичний ШІМ: " << controller.getPulseWidthUs() << " мкс\n";
        std::cout << "  Аварійне блокування: "
                  << (controller.isEmergencyStop() ? "АКТИВНЕ (Газ 0%)" : "НЕМАЄ") << "\n\n";
    }

    return 0;
}
