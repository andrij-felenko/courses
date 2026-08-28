// Приклад використання профілювальника на C++20
#include "task_profiler.hpp"
#include "gpio_profiling.hpp"

namespace {
    RealTime::TaskProfiler<4> g_profiler(168'000'000U);
    constexpr uint8_t kMotorTaskId = 0;
}

void run_motor_control_loop() noexcept {
    // Автоматичний старт і стоп профілювання за ідіомою RAII
    auto timer_scope = g_profiler.make_scope(kMotorTaskId);
    Hardware::GpioProfiler::ScopedPin pin_scope(PROF_PIN_TASK1);

    // Корисна робота алгоритму
    read_adc_currents();
    clarke_park_transform();
    run_pi_regulators();
    update_pwm_duty();
}
