#include "adc_interface.hpp"
#include "lvdt_conditioner.hpp"
#include <iostream>
#include <iomanip>
#include <cstdlib>

/**
 * @brief Симульований драйвер АЦП для демонстрації роботи кондиціонера LVDT.
 * 
 * Імітує роботу аналогового демодулятора/кондиціонера LVDT із зміщенням нуля
 * та додає невеликий шум оцифрування.
 */
class SimulatedAdcDriver : public lvdt::IAdcDriver {
public:
    SimulatedAdcDriver() : core_position_mm_(0.0f), is_initialized_(false) {}

    bool init() override {
        is_initialized_ = true;
        std::cout << "[АЦП Драйвер] Периферію АЦП успішно ініціалізовано." << std::endl;
        return true;
    }

    /**
     * @brief Задати фізичне положення сердечника для моделювання аналогового сигналу.
     * @param displacement_mm Зсув у міліметрах.
     */
    void set_simulated_position(float displacement_mm) {
        core_position_mm_ = displacement_mm;
    }

    bool read_voltage(float& out_voltage_v) override {
        if (!is_initialized_) {
            return false;
        }

        // Параметри симуляції LVDT:
        // Null напруга V_null = 1.65 В (середина діапазону 0..3.3 В)
        // Чутливість = 0.1 В / мм
        constexpr float kNullVoltage = 1.65f;
        constexpr float kSensitivity = 0.1f;

        float ideal_voltage = kNullVoltage + (core_position_mm_ * kSensitivity);

        // Малий високочастотний шум (+-0.5 мВ)
        float noise = ((static_cast<float>(rand()) / RAND_MAX) - 0.5f) * 0.001f;

        out_voltage_v = ideal_voltage + noise;
        return true;
    }

private:
    float core_position_mm_;
    bool is_initialized_;
};

int main() {
    std::cout << "==================================================" << std::endl;
    std::cout << " Системи вимірювання лінійного зсуву LVDT (C++)  " << std::endl;
    std::cout << "==================================================" << std::endl;

    // 1. Ініціалізація симульованого АЦП та кондиціонера LVDT (робочий діапазон -10.0 мм .. +10.0 мм)
    SimulatedAdcDriver adc_driver;
    lvdt::LVDTConditioner lvdt_conditioner(adc_driver, -10.0f, 10.0f, 16);

    if (!lvdt_conditioner.init()) {
        std::cerr << "Помилка ініціалізації АЦП!" << std::endl;
        return 1;
    }

    // 2. Демонстрація поведінки до проведення калібрування
    std::cout << "\n[Крок 1] Перевірка статусу вимірювання до калібрування:" << std::endl;
    lvdt::DisplacementResult uncal_result = lvdt_conditioner.measure_displacement();
    if (uncal_result.status == lvdt::Status::Uncalibrated) {
        std::cout << " -> Повідомлення: Систему ще не відкалібровано (Status::Uncalibrated)." << std::endl;
    }

    // 3. Процедура двопоточкового калібрування LVDT
    std::cout << "\n[Крок 2] Запуск процедури двопоточкового калібрування..." << std::endl;

    // Точка 1: Нульове положення (0.0 мм)
    adc_driver.set_simulated_position(0.0f);
    std::cout << " -> Встановлення сердечника в нуль (0.0 мм)..." << std::endl;
    if (!lvdt_conditioner.calibrate_null_point(32)) {
        std::cerr << "Помилка фіксації нульової точки!" << std::endl;
        return 1;
    }
    std::cout << "    Нульову точку успішно зафіксовано." << std::endl;

    // Точка 2: Еталонне переміщення (+5.0 мм)
    constexpr float kRefDisplacementMm = 5.0f;
    adc_driver.set_simulated_position(kRefDisplacementMm);
    std::cout << " -> Встановлення еталонної плитки " << kRefDisplacementMm << " мм..." << std::endl;
    if (!lvdt_conditioner.calibrate_reference_point(kRefDisplacementMm, 32)) {
        std::cerr << "Помилка фіксації еталонної точки!" << std::endl;
        return 1;
    }
    std::cout << "    Еталонну точку успішно зафіксовано." << std::endl;

    // Виведення розрахованих параметрів
    lvdt::CalibrationData cal_data = lvdt_conditioner.get_calibration_data();
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "\n[Калібрувальні дані]:" << std::endl;
    std::cout << " - Нульова напруга (V_null): " << cal_data.null_voltage_v << " В" << std::endl;
    std::cout << " - Еталонна напруга (V_ref): " << cal_data.ref_voltage_v << " В" << std::endl;
    std::cout << " - Масштабний коефіцієнт (K): " << cal_data.scale_factor_k << " мм/В" << std::endl;

    // 4. Опитальний цикл вимірювань у робочому режимі
    std::cout << "\n[Крок 3] Періодичне опитування давача в циклі вимірювання:" << std::endl;
    const float test_positions_mm[] = { 0.0f, 2.5f, -4.0f, 8.0f, -12.0f }; // -12.0 мм вийшовши за хід -10 мм

    for (float target_pos : test_positions_mm) {
        adc_driver.set_simulated_position(target_pos);
        lvdt::DisplacementResult result = lvdt_conditioner.measure_displacement();

        std::cout << " Вхідний зсув: " << std::setw(6) << target_pos << " мм | ";
        std::cout << "Напруга: " << result.voltage_v << " В | ";

        switch (result.status) {
            case lvdt::Status::OK:
                std::cout << "Розраховано: " << std::setw(6) << result.displacement_mm << " мм [OK]" << std::endl;
                break;
            case lvdt::Status::OutOfRange:
                std::cout << "Розраховано: " << std::setw(6) << result.displacement_mm << " мм [ПОМИЛКА: OutOfRange!]" << std::endl;
                break;
            case lvdt::Status::Uncalibrated:
                std::cout << "[Uncalibrated]" << std::endl;
                break;
            case lvdt::Status::AdcError:
                std::cout << "[AdcError]" << std::endl;
                break;
        }
    }

    std::cout << "\nВимірювальну сесію завершено успішно." << std::endl;
    return 0;
}
