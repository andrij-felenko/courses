/* Стендове випробування на одноплатнику: самоперевірка нагрівачем,
   далі відлік раз на дві секунди, доки не натиснуто Ctrl-C. */

#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <exception>
#include <format>
#include <iostream>
#include <thread>

#include "linux_i2c.hpp"
#include "sht3x.hpp"

namespace {

constexpr auto kBusPath    = "/dev/i2c-1";
constexpr auto kPollPeriod = std::chrono::seconds(2);

std::atomic_bool g_stop{false};

void on_signal(int) noexcept
{
    g_stop.store(true, std::memory_order_relaxed);
}

void print(std::string_view tag, const sht3x::Reading& r)
{
    std::cout << std::format("{:<12} T = {:7.3f} °C   RH = {:6.2f} %\n",
                             tag, r.celsius(), r.humidity());
}

// Нагрівач на дві секунди: справний сенсор мусить помітно нагрітися
// й одночасно показати провал вологості. Нема реакції — мембрана мертва.
template <sht3x::I2cBus Bus>
void heater_selftest(sht3x::Sensor<Bus>& sensor)
{
    const auto cold = sensor.measure_with_retry();
    if (!cold) {
        std::cerr << "самоперевірка: базовий відлік не знявся ("
                  << sht3x::to_string(cold.error()) << ")\n";
        return;
    }

    if (auto on = sensor.heater(true); !on) {
        std::cerr << "самоперевірка: нагрівач не увімкнувся\n";
        return;
    }
    std::this_thread::sleep_for(std::chrono::seconds(2));

    const auto hot = sensor.measure_with_retry();
    // Гасимо нагрівач у будь-якому разі, навіть якщо відлік провалився.
    if (auto off = sensor.heater(false); !off) {
        std::cerr << "УВАГА: нагрівач лишився ввімкненим\n";
    }

    if (!hot) {
        std::cerr << "самоперевірка: відлік під нагрівом не знявся\n";
        return;
    }

    print("холодний:", *cold);
    print("нагрітий:", *hot);

    const std::int32_t d_t  = hot->temperature_mc - cold->temperature_mc;
    const std::int32_t d_rh = static_cast<std::int32_t>(cold->humidity_cpm) -
                              static_cast<std::int32_t>(hot->humidity_cpm);

    if (d_t > 1000 && d_rh > 300) {
        std::cout << "самоперевірка: OK\n";
    } else {
        std::cout << std::format("самоперевірка: ПРОВАЛ (ΔT = {} м°C, ΔRH = {} сотих)\n",
                                 d_t, d_rh);
    }
}

}  // namespace

int main()
{
    std::signal(SIGINT, on_signal);
    std::signal(SIGTERM, on_signal);

    try {
        sht3x::LinuxI2c bus{kBusPath, sht3x::kAddrGnd};
        sht3x::Sensor sensor{bus};

        if (auto ready = sensor.init(); !ready) {
            std::cerr << "сенсор недоступний: " << sht3x::to_string(ready.error()) << '\n';
            return EXIT_FAILURE;
        }

        heater_selftest(sensor);

        while (!g_stop.load(std::memory_order_relaxed)) {
            if (const auto reading = sensor.measure_with_retry()) {
                print("відлік:", *reading);
            } else {
                std::cerr << std::format("збій: {} (шина {}, CRC {})\n",
                                         sht3x::to_string(reading.error()),
                                         sensor.bus_errors(), sensor.crc_errors());
            }

            // Дві секунди паузи — проти самопідігріву кристала: при
            // безперервному опитуванні він додає 1..1.8 °C і забирає
            // 5..6 %RH з показань вологості.
            std::this_thread::sleep_for(kPollPeriod);
        }

        std::cout << std::format("зупинено. Збоїв шини {}, CRC {}\n",
                                 sensor.bus_errors(), sensor.crc_errors());
        return EXIT_SUCCESS;
    } catch (const std::exception& e) {
        std::cerr << "шина недоступна: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
}
