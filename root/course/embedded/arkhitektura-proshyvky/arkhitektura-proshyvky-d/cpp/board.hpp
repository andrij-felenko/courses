// board.hpp — усе, що застосунок знає про плату.
// Порти (stm32f4, host_mock) дають різні реалізації board::init(), а
// main.cpp лишається байт-у-байт тим самим.
#pragma once

#include "app/events.hpp"
#include "app/telemetry.hpp"
#include "hal/gpio.hpp"
#include "hal/i2c_bus.hpp"

namespace board {

struct Board {
    hal::II2cBus&        env_bus;     // шина давача мікроклімату
    hal::II2cBus&        accel_bus;   // шина акселерометра (може збігатися)
    hal::OutputPin       status_led;
    app::ITelemetrySink& telemetry;
};

// Піднімає тактування, шини й таймер тіку. nullptr — залізо не піднялося,
// і запускати застосунок нема сенсу.
[[nodiscard]] Board* init();

// Прив'язує приймач подій до порту: саме звідси його беруть обробники
// переривань і генератор системного тіку.
void bind_event_sink(app::IEventSink* sink);

[[nodiscard]] app::IEventSink* event_sink() noexcept;

} // namespace board
