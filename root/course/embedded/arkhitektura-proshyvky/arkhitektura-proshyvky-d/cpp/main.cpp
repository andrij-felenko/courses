// main.cpp — головний диспетчер прошивки.
// Файл не залежить від плати: board::init() підставляє або справжній
// STM32F401, або імітацію на комп'ютері розробника. Ніяких затримок і
// порожніх очікувань — коли черга спорожніла, ядро спить.
#include "app/config.hpp"
#include "app/coordinator.hpp"
#include "board.hpp"
#include "bsp/accelerometer.hpp"
#include "bsp/bme280.hpp"
#include "bsp/status_led.hpp"
#include "hal/clock.hpp"
#include "services/event_queue.hpp"

namespace {

[[noreturn]] void sleep_forever()
{
    for (;;) {
        hal::cpu_sleep();
    }
}

} // namespace

int main()
{
    board::Board* board = board::init();
    if (board == nullptr) {
        // Плата не піднялася. Крутити цикл нема сенсу: чекаємо на
        // сторожовий таймер, який перезапустить пристрій.
        sleep_forever();
    }

    // Уся пам'ять порахована на етапі компіляції: купи в прошивці немає,
    // тож немає й способу впасти через її фрагментацію на шостому місяці.
    static services::EventQueue<config::kEventQueueCapacity> queue;
    board::bind_event_sink(&queue);

    bsp::StatusLed led{board->status_led};

    auto environment = bsp::Bme280::create(
        hal::I2cDevice{board->env_bus, config::kBme280Address});
    if (!environment) {
        // Без давача мікроклімату логер не має що записувати. Світимо
        // рівно й чекаємо на обслугу: тихо працювати наполовину гірше,
        // ніж не працювати помітно.
        led.set_mode(bsp::LedMode::On);
        sleep_forever();
    }

    auto accelerometer = bsp::Adxl345::create(
        hal::I2cDevice{board->accel_bus, config::kAdxl345Address},
        bsp::AccelRange::G16);

    app::Coordinator coordinator{
        app::Coordinator::Config{
            .environment       = *environment,
            .accelerometer     = accelerometer ? &*accelerometer : nullptr,
            .led               = led,
            .events            = queue,
            .telemetry         = &board->telemetry,
            .temp_limit_c      = config::kTempLimitC,
            .temp_hysteresis_c = config::kTempHysteresisC,
            .vibration_limit_g = config::kVibrationLimitG,
            .telemetry_window  = config::kTelemetryWindow,
            .fault_limit       = config::kSensorFaultLimit,
        },
        hal::now()};

    for (;;) {
        // Вибираємо чергу до дна: обробка однієї події часто породжує
        // наступну (вимір → аварія), і засинати з непорожньою чергою
        // означало б відкласти тривогу до наступного тіку.
        while (auto event = queue.pop()) {
            coordinator.dispatch(*event);
        }
        hal::cpu_sleep();
    }
}
