#include <iostream>
#include "sensor_driver.hpp"

template <driver::BusTransport Transport>
void application_task_step(driver::SensorDevice<Transport>& sensor) {
    switch (sensor.state()) {
        case driver::State::Idle:
            sensor.start_measurement();
            break;

        case driver::State::Converting: {
            auto result = sensor.poll();
            if (result.has_value()) {
                const auto& data = result.value();
                std::cout << "T = " << data.temperature_mdeg_c << " mC, P = " 
                          << data.pressure_pa << " Pa\n";
            } else if (result.error() == driver::Status::NotReady) {
                // Виконуємо інші фонові задачі
            } else {
                // Відновлення після помилки CRC або шини
                sensor.recover_bus();
                sensor.reset_fsm();
            }
            break;
        }

        case driver::State::DataReady:
            sensor.start_measurement();
            break;

        case driver::State::Error:
        default:
            sensor.recover_bus();
            sensor.reset_fsm();
            break;
    }
}
