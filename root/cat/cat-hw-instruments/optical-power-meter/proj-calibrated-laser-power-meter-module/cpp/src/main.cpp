#include <iostream>
#include <iomanip>
#include <vector>
#include "optical_power_meter.hpp"

int main() {
    std::cout << "=== Драйвер оптичного ватметра (C++ OOP) ===\n\n";

    // Калібрувальна таблиця спектральної чутливості кремнієвого фотодіода
    std::vector<opm::CalibPoint> calib_table = {
        {650, 0.42f},
        {780, 0.53f},
        {850, 0.58f},
        {980, 0.62f},
        {1064, 0.25f}
    };

    opm::HardwareConfig hw_config{
        .tia_gain_ohm = 100000.0f,    // 100 кОм
        .adc_vref_v = 3.3f,           // 3.3 В
        .adc_max_count = 4095,        // 12-біт АЦП
        .lidt_max_power_w = 0.100f    // Порог LIDT = 100 мВт
    };

    opm::OpticalPowerMeter opm_driver(hw_config, calib_table);

    std::cout << "1. Калібрування темнового струму за відсутності світла...\n";
    std::vector<std::uint16_t> dark_samples = {11, 13, 12, 14, 12, 10, 13, 12};
    if (opm_driver.calibrateDarkOffset(dark_samples)) {
        std::cout << "   Зафіксований темновий зсув: " 
                  << std::fixed << std::setprecision(4)
                  << opm_driver.darkOffsetVoltage() * 1000.0f << " мВ\n\n";
    }

    std::cout << "2. Встановлення робочої довжини хвилі лазера λ = 850 нм...\n";
    if (opm_driver.setWavelength(850)) {
        std::cout << "   Інтерпольована чутливість R(850 нм) = "
                  << std::setprecision(3) << opm_driver.currentSensitivity() << " А/Вт\n\n";
    }

    std::cout << "3. Симуляція вимірювального циклу падаючого променя:\n";
    std::vector<std::uint16_t> adc_readings = {150, 450, 1200, 2500, 4050};

    for (const auto raw_adc : adc_readings) {
        auto result = opm_driver.processAdcSample(raw_adc);
        if (result.has_value()) {
            std::cout << "   [АЦП: " << std::setw(4) << raw_adc << "] -> "
                      << "Потужність: " << std::setw(8) << std::setprecision(3) 
                      << result->power_w * 1e6f << " мкВт | "
                      << std::setw(6) << std::setprecision(2) << result->power_dbm << " dBm";

            if (result->lidt_exceeded) {
                std::cout << "  [УВАГА: Перевищено поріг оптичного руйнування LIDT!]";
            }
            std::cout << '\n';
        }
    }

    return 0;
}
