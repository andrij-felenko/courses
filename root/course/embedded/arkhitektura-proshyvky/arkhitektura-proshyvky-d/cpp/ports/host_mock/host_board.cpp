// ports/host_mock/host_board.cpp — плата на комп'ютері розробника.
// Час тут віртуальний: hal::cpu_sleep() не спить, а переводить годинник
// уперед до наступного тіку й кладе подію в чергу. Прошивка від цього не
// змінюється жодним рядком, зате доба роботи проходить за мить.
#include "app/config.hpp"
#include "board.hpp"
#include "hal/clock.hpp"
#include "hal/critical_section.hpp"
#include "ports/host_mock/host_mocks.hpp"

#include <cstdio>

namespace {

constexpr std::uint8_t kLedPin = 0;

std::uint32_t    g_virtual_ms = 0;
std::uint32_t    g_next_tick_ms = static_cast<std::uint32_t>(config::kTickPeriod.count());
app::IEventSink* g_sink = nullptr;

port::MockBme280            g_environment;
port::MockAdxl345           g_accelerometer;
port::MockI2cBus            g_bus{g_environment, g_accelerometer};
port::MockGpioPort          g_gpio;
port::ConsoleTelemetrySink  g_telemetry;

} // namespace

// --- hal/clock.hpp ---

namespace hal {

Millis now() noexcept
{
    return Millis{g_virtual_ms};
}

void delay(Millis duration) noexcept
{
    g_virtual_ms += static_cast<std::uint32_t>(duration.count());
}

void cpu_sleep() noexcept
{
    // Стрибаємо просто до моменту наступного тіку — рівно так, як ядро
    // прокидається з WFI від переривання таймера.
    if (static_cast<std::int32_t>(g_next_tick_ms - g_virtual_ms) > 0) {
        g_virtual_ms = g_next_tick_ms;
    }
    g_next_tick_ms = g_virtual_ms + static_cast<std::uint32_t>(config::kTickPeriod.count());

    if (g_sink != nullptr) {
        static_cast<void>(g_sink->post(app::SystemEvent{
            .id = app::EventId::Tick,
            .timestamp = Millis{g_virtual_ms},
        }));
    }
}

std::uint32_t critical_enter() noexcept
{
    // Справжніх переривань на хості немає, тож секція порожня. Функції
    // лишаються на місці навмисно: код черги подій має бути той самий,
    // інакше тест перевіряв би не ту прошивку, що поїде на плату.
    return 0;
}

void critical_exit(std::uint32_t /*saved_state*/) noexcept
{
}

} // namespace hal

namespace port {

void ConsoleTelemetrySink::publish(const app::TelemetryRecord& record)
{
    ++count_;
    std::printf("[%8ld ms] T=%.2f C (%.2f…%.2f) H=%.1f%% P=%.2f hPa "
                "VIB rms=%.3f g peak=%.3f g N=%u ERR=%u\n",
                static_cast<long>(record.window_end.count()),
                static_cast<double>(record.temp_avg_c),
                static_cast<double>(record.temp_min_c),
                static_cast<double>(record.temp_max_c),
                static_cast<double>(record.humidity_avg_rh),
                static_cast<double>(record.pressure_avg_hpa),
                static_cast<double>(record.vibration_rms_g),
                static_cast<double>(record.vibration_peak_g),
                record.sample_count,
                record.fault_count);
}

void mock_button_click()
{
    if (g_sink == nullptr) {
        return;
    }
    static_cast<void>(g_sink->post(app::SystemEvent{
        .id = app::EventId::ButtonClick,
        .timestamp = hal::Millis{g_virtual_ms},
        .payload = app::ButtonPayload{.pin = 0},
    }));
}

} // namespace port

// --- board.hpp ---

namespace board {

void bind_event_sink(app::IEventSink* sink)
{
    g_sink = sink;
}

app::IEventSink* event_sink() noexcept
{
    return g_sink;
}

Board* init()
{
    g_virtual_ms   = 0;
    g_next_tick_ms = static_cast<std::uint32_t>(config::kTickPeriod.count());

    static Board board{
        .env_bus    = g_bus,
        .accel_bus  = g_bus,
        .status_led = hal::OutputPin{g_gpio, kLedPin, false},
        .telemetry  = g_telemetry,
    };
    return &board;
}

} // namespace board
