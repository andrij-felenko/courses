#include "dual_encoder_driver.hpp"
#include <iostream>
#include <iomanip>
#include <memory>

using namespace controls::encoders;

void print_report_line(const DiagnosticReport& rep) {
    std::cout << std::fixed << std::setprecision(2)
              << "[ДІАГНОСТИКА] Оптичний: " << std::setw(6) << rep.optical_angle_deg << " deg | "
              << "RVDT: " << std::setw(6) << rep.rvdt_angle_deg << " deg | "
              << "Зведений: " << std::setw(6) << rep.fused_angle_deg << " deg | "
              << "Розбіжність: " << std::setw(5) << rep.current_discrepancy_deg << " deg | "
              << "Дійсний: " << (rep.system_valid ? "ТАК" : "НІ ") << " | "
              << rep.status_message << "
";
}

int main() {
    std::cout << "======================================================================
";
    std::cout << " ДРАЙВЕР ПОДВІЙНОГО ОПТИЧНОГО ТА ІНДУКТИВНОГО (RVDT) ДАВАЧА ПОЛОЖЕННЯ 
";
    std::cout << "======================================================================

";

    auto opt_sensor = std::make_unique<OpticalEncoderSensor>(4096);
    auto rvdt_sensor = std::make_unique<InductiveRvdtSensor>(5.0, 50.0);

    OpticalEncoderSensor* opt_ptr = opt_sensor.get();
    InductiveRvdtSensor* rvdt_ptr = rvdt_sensor.get();

    DriverConfig config;
    config.max_allowed_discrepancy_deg = 3.0;
    config.warning_discrepancy_deg = 1.5;
    config.calibration_samples_count = 10;
    config.discrepancy_timeout_ms = 30;

    DualEncoderDriver driver(std::move(opt_sensor), std::move(rvdt_sensor), config);

    driver.register_discrepancy_callback([](const DiagnosticReport& report) {
        std::cout << "
>>> [ПОДІЯ РОЗБІЖНОСТІ (DISCREPANCY EVENT)] <<<
"
                  << ">>> Статус: " << static_cast<int>(report.status) << "
"
                  << ">>> Повідомлення: " << report.status_message << "

";
    });

    std::cout << "--- КРОК 1: Синхронний рух штурвала (Нормальний режим) ---
";
    for (int i = 0; i < 5; ++i) {
        opt_ptr->simulate_pulse_input(114);
        rvdt_ptr->simulate_adc_voltage(2.5 + (i + 1) * 0.5);
        
        DiagnosticReport rep = driver.update();
        print_report_line(rep);
    }

    std::cout << "
--- КРОК 2: Виконання автокалібрування нульової точки ---
";
    driver.start_auto_zero_calibration();
    for (int i = 0; i < 10; ++i) {
        opt_ptr->simulate_pulse_input(0);
        rvdt_ptr->simulate_adc_voltage(2.5 + (i % 2 == 0 ? 0.01 : -0.01));
        
        DiagnosticReport rep = driver.update();
        print_report_line(rep);
    }
    std::cout << "Калібрування завершено. Новий зсув нуля оптичного енкодера: " 
              << opt_ptr->get_zero_offset() << " deg, RVDT: " << rvdt_ptr->get_zero_offset() << " deg
";

    std::cout << "
--- КРОК 3: Симуляція механічного проковзування (Помилка розбіжності) ---
";
    opt_ptr->simulate_pulse_input(100);

    for (int i = 0; i < 4; ++i) {
        DiagnosticReport rep = driver.update();
        print_report_line(rep);
    }

    std::cout << "
--- КРОК 4: Апаратний збій (Обрив лінії оптичного енкодера) ---
";
    opt_ptr->set_hardware_fault(true);
    DiagnosticReport fault_rep = driver.update();
    print_report_line(fault_rep);

    std::cout << "
======================================================================
";
    std::cout << " ДЕМОНСТРАЦІЮ УСПІШНО ЗАВЕРШЕНО 
";
    std::cout << "======================================================================
";

    return 0;
}
