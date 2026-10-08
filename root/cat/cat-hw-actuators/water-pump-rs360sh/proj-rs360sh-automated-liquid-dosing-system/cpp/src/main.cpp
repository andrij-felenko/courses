#include "mosfet_pwm_hal.hpp"
#include "rs360sh_pump_driver.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "=== Демонстрація системи керування водяною помпою RS-360SH ===\n\n";

    MosfetPwmHal pwm_hal(9, 5000);

    PumpConfig config;
    config.max_flow_rate_ml_per_sec = 15.0f;
    config.ramp_up_duration_ms = 400;
    config.ramp_down_duration_ms = 400;
    config.min_operating_duty = 0.2f;
    config.max_operating_duty = 1.0f;
    config.dry_run_timeout_ms = 800;

    RS360SHPumpDriver pump(pwm_hal, config);
    pump.init();

    pump.setFlowRateCalibration(14.8f);

    std::cout << "[ТЕСТ 1] Нормальне точне дозування 60 мл рідини з використанням RAII Guard\n";
    {
        DosingGuard guard(pump);

        if (pump.startDosingVolume(60.0f, 1.0f)) {
            std::cout << "-> Запуск дозування 60 мл успішно прийнято.\n";

            std::uint32_t simulated_time_ms = 0;
            const std::uint32_t step_ms = 50;

            while (pump.getState() != PumpState::Idle && pump.getState() != PumpState::FaultDryRun) {
                FlowSensorData flow_data{false, 0.0f, 0};
                DryRunSensorData dry_data{true, simulated_time_ms};

                pump.update(simulated_time_ms, flow_data, dry_data);

                std::cout << "Час: " << std::setw(5) << simulated_time_ms << " мс | "
                          << "ШІМ: " << std::setw(5) << std::fixed << std::setprecision(1) << (pwm_hal.getDutyCycle() * 100.0f) << "% | "
                          << "Дозовано: " << std::setw(5) << std::setprecision(2) << pump.getDosedVolumeMl() << " мл\n";

                simulated_time_ms += step_ms;
            }

            if (pump.getState() == PumpState::Idle) {
                std::cout << "-> Дозування 60 мл успішно завершено! Підсумковий об'єм: "
                          << pump.getDosedVolumeMl() << " мл.\n";
                guard.dismiss();
            }
        }
    }

    std::cout << "\n[ТЕСТ 2] Симуляція виникнення аварії сухого ходу (Dry Run)\n";
    if (pump.startDosingVolume(100.0f, 1.0f)) {
        std::cout << "-> Запуск дозування 100 мл прийнято.\n";

        std::uint32_t simulated_time_ms = 5000;
        const std::uint32_t step_ms = 50;

        while (pump.getState() != PumpState::Idle && pump.getState() != PumpState::FaultDryRun) {
            bool fluid_present = (simulated_time_ms < 5500);

            FlowSensorData flow_data{true, fluid_present ? 14.8f : 0.0f, 0};
            DryRunSensorData dry_data{fluid_present, simulated_time_ms};

            pump.update(simulated_time_ms, flow_data, dry_data);

            std::cout << "Час: " << std::setw(5) << simulated_time_ms << " мс | "
                      << "ШІМ: " << std::setw(5) << std::fixed << std::setprecision(1) << (pwm_hal.getDutyCycle() * 100.0f) << "% | "
                      << "Рідина в магістралі: " << (fluid_present ? "ТАК" : "НІ ") << " | "
                      << "Стан: " << static_cast<int>(pump.getState()) << "\n";

            simulated_time_ms += step_ms;
        }

        if (pump.isDryRunDetected()) {
            std::cout << "-> АВАРІЯ: Захист сухого ходу успішно спрацював! Двигун зупинено, ШІМ знеструмлено.\n";
        }
    }

    std::cout << "\n[ТЕСТ 3] Скидання аварії (clearFault)\n";
    pump.clearFault();
    std::cout << "-> Стан після скидання аварії: " << static_cast<int>(pump.getState())
              << " (0 = Idle), Сухий хід: " << (pump.isDryRunDetected() ? "ТАК" : "НІ") << "\n";

    return 0;
}
