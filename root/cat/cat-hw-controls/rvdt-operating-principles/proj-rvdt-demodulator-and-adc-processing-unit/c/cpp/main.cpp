#include "RvdtDriver.hpp"
#include <iostream>
#include <vector>
#include <string>

int main() {
    using namespace hw_controls;

    std::cout << "=== C++ Драйвер розбору сигналів давача RVDT ===\n\n";

    RvdtConfig config{
        .max_angle_deg = 45.0f,
        .sensitivity_v_v_deg = 0.025f,
        .zero_offset_deg = 0.0f,
        .min_sum_voltage_v = 0.5f,
        .max_sum_voltage_v = 15.0f,
        .alpha_filter = 0.3f
    };

    RvdtDriver driver(config);

    struct SampleTest {
        float vs1;
        float vs2;
        std::string label;
    };

    const std::vector<SampleTest> test_cases = {
        {3.0f, 3.0f, "Центральне положення (0 град.)"},
        {4.2f, 1.8f, "Правий кут повороту (+20 град.)"},
        {1.8f, 4.2f, "Лівий кут повороту (-20 град.)"},
        {0.05f, 0.05f, "Помилка: обрив котушок RVDT"},
        {10.0f, 10.0f, "Помилка: коротке замикання"}
    };

    for (const auto& test : test_cases) {
        auto result = driver.processSample(test.vs1, test.vs2);

        std::cout << "Тест: " << test.label << "\n";
        std::cout << "  Вхід: V_S1=" << result.v_s1 << "V, V_S2=" << result.v_s2
                  << "V | Сума=" << result.sum_voltage << "V\n";

        if (result.error == RvdtError::Ok) {
            std::cout << "  Кут: сирий = " << result.raw_angle_deg
                      << " град., фільтрований = " << result.filtered_angle_deg << " град.\n";
        } else {
            std::cout << "  ВИЯВЛЕНО ПОМИЛКУ: ";
            if (result.error & RvdtError::OpenCircuit) std::cout << "[Обрив обмотки] ";
            if (result.error & RvdtError::ShortCircuit) std::cout << "[Коротке замикання] ";
            if (result.error & RvdtError::OutOfRange) std::cout << "[Вихід за робочий діапазон] ";
            std::cout << "\n";
        }
        std::cout << "\n";
    }

    std::cout << "--- Процедура калібрування нуля ---\n";
    driver.processSample(3.8f, 2.2f);
    std::cout << "Поточний кут до калібрування: " << driver.processSample(3.8f, 2.2f).raw_angle_deg << " град.\n";
    driver.calibrateZero();
    std::cout << "Нове значення нуля встановлено.\n";
    std::cout << "Кут після калібрування: " << driver.processSample(3.8f, 2.2f).raw_angle_deg << " град.\n";

    return 0;
}
