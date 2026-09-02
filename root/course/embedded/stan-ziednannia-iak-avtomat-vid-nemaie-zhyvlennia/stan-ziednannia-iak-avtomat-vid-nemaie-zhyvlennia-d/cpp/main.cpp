#include "at_link.hpp"
#include "blackbox.hpp"
#include "conn_fsm.hpp"
#include "modem_hal.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <span>

using namespace std::chrono_literals;

/* Давач рівня — те, заради чого вузол узагалі виходить в ефір. */
std::uint16_t sensorReadLevelMm();

namespace {

constexpr auto kTick = 20ms;
constexpr auto kSession = 24h; /* сеанс раз на добу */

AtLink* g_link = nullptr;

std::span<const std::byte> buildTelemetry(std::span<std::byte> out, ModemHal& hal,
                                          const AtLink& link)
{
    const auto uptime = std::chrono::duration_cast<std::chrono::seconds>(
                            hal.now().time_since_epoch())
                            .count();

    const auto put16 = [&out](std::size_t at, std::uint16_t value) {
        out[at] = std::byte{static_cast<std::uint8_t>(value & 0xFF)};
        out[at + 1] = std::byte{static_cast<std::uint8_t>(value >> 8)};
    };

    put16(0, static_cast<std::uint16_t>(uptime & 0xFFFF));
    put16(2, static_cast<std::uint16_t>((uptime >> 16) & 0xFFFF));
    put16(4, sensorReadLevelMm());
    put16(6, hal.vbatMv());
    put16(8, static_cast<std::uint16_t>(link.overflows()));
    return out.first(10);
}

} // namespace

/* Міст із вектора переривання UART плати. */
extern "C" void app_uart_rx_isr(std::uint8_t byte)
{
    if (g_link != nullptr) {
        g_link->rxFromIsr(std::byte{byte});
    }
}

int main()
{
    ModemHal& hal = boardModemHal();

    AtLink link{hal};
    g_link = &link;

    BlackBox log{hal};
    ConnectionFsm fsm{hal, link, log};

    auto nextTick = hal.now();
    auto nextSession = hal.now();
    bool sessionOpen = false;

    for (;;) {
        /* Автомат неблокуючий, тож сторожа гладимо щотакту, а не «коли встигнемо». */
        hal.kickWatchdog();

        const auto now = hal.now();

        if (now >= nextSession) {
            std::array<std::byte, 16> frame{};
            nextSession += kSession;
            fsm.connect();
            (void)fsm.submit(buildTelemetry(frame, hal, link));
            sessionOpen = true;
        }

        if (now >= nextTick) {
            nextTick += kTick;
            fsm.tick();
        }

        /* Дані підтверджено брокером — згортаємо сеанс і йдемо спати.
           Якщо автомат зупинився фатально, сюди він просто не доходить,
           і наступний добовий сеанс почне все з нуля. */
        if (sessionOpen && fsm.idle()) {
            fsm.disconnect();
            sessionOpen = false;
        }
    }
}
