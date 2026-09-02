#include <atomic>
#include <chrono>
#include <cmath>
#include <csignal>
#include <cstring>
#include <format>
#include <iostream>
#include <stop_token>
#include <thread>

#include <sys/mman.h>

#include "offboard_streamer.hpp"

namespace {

constexpr const char* kUartPort = "/dev/ttyAMA0";
constexpr speed_t kUartBaud = B921600;
constexpr std::uint8_t kOurSysId = 240;   // окремий ID супутнього комп'ютера
constexpr std::uint8_t kOurCompId = 191;  // MAV_COMP_ID_ONBOARD_COMPUTER
constexpr int kPlannerHz = 10;

volatile std::sig_atomic_t g_stop = 0;

void on_signal(int) {
    g_stop = 1;
}

// Повільний контур планування. Тут була б обробка кадру нейромережею,
// оновлення воксельної карти й побудова сплайна — усе зі змінною
// тривалістю. Для генератора важливо лише те, що цілі приходять рідко
// (10 Гц) і нерівномірно, а їхній штамп часу може будь-коли застаріти.
void planner_loop(std::stop_token stop, OffboardStreamer& streamer) {
    using namespace std::chrono_literals;
    constexpr float kSpeed = 2.0f;   // м/с
    constexpr float kRadius = 5.0f;  // м
    constexpr float kOmega = kSpeed / kRadius;
    const auto period = std::chrono::milliseconds(1000 / kPlannerHz);

    auto next = std::chrono::steady_clock::now();
    float t = 0.0f;

    while (!stop.stop_requested() && g_stop == 0) {
        // Обліт кола: вектор швидкості в горизонті, ніс за напрямком руху.
        const float vx = kSpeed * std::cos(kOmega * t);
        const float vy = kSpeed * std::sin(kOmega * t);
        streamer.set_target(VelocityCommand{vx, vy, 0.0f, std::atan2(vy, vx)});

        t += 1.0f / static_cast<float>(kPlannerHz);
        next += period;
        std::this_thread::sleep_until(next);  // планувальник не в реальному часі
    }
}

}  // namespace

int main() {
    // Закріплюємо сторінки в RAM: жодного page fault усередині такту
    // 20 Гц, навіть коли зір з'їдає всю вільну пам'ять.
    if (::mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        std::cerr << std::format("[main] mlockall: {} — сторінки можуть піти в підкачку\n",
                                 std::strerror(errno));
    }

    std::signal(SIGINT, on_signal);
    std::signal(SIGTERM, on_signal);

    try {
        OffboardStreamer streamer(kUartPort, kUartBaud, kOurSysId, kOurCompId);

        std::jthread rt_thread([&streamer](std::stop_token stop) { streamer.run(stop); });
        std::jthread planner([&streamer](std::stop_token stop) {
            planner_loop(stop, streamer);
        });

        // Даємо планувальнику видати першу ціль — і аж тоді просимо режим.
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
        streamer.begin_mission();

        while (g_stop == 0 && streamer.running()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
        }

        std::cerr << "[main] зупинка: гальмуємо й віддаємо керування автопілоту\n";
        streamer.request_shutdown();
        rt_thread.join();
        planner.request_stop();
    } catch (const std::system_error& e) {
        std::cerr << std::format("[main] фатально: {}\n", e.what());
        return 1;
    }
    return 0;
}
