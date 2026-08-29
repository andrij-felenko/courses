// main.cpp — бюджети затримки конкретних комплексів.
//
// Усі конфігурації зі configs.hpp пораховані ще компілятором; тут лишається
// зіставити їх між собою і показати, що затримка робить із контуром оператора.
//
// Збірка: c++ -std=c++20 -O2 -Wall -Wextra -Iinclude src/main.cpp src/report.cpp -o latency
#include <array>
#include <exception>
#include <format>
#include <iostream>

#include "latency/configs.hpp"
#include "latency/report.hpp"

namespace {

using namespace latency;
using namespace std::chrono_literals;

constexpr double kControlHz = 2.5;   // смуга ручного маневрування оператора
constexpr double kSpeedMps  = 25.0;  // 90 км/год

// Контур оператора замикається двічі: команда летить туди, картинка
// повертається назад. Фазу накопичує сума обох трактів — саме її
// порівнюють зі 100–150 мс, а не окремий Stick-to-Motor.
void closed_loop(std::string_view label, const Track& command, const Track& video) {
    report::print_dynamics(label, command.summary() + video.summary(),
                           kControlHz, kSpeedMps);
}

// Ті самі constexpr-конструктори працюють і в рантаймі — коли параметри
// приходять із заміру, а не з коду. Різниця лише в тому, що хибне число
// стає винятком, а не помилкою збірки.
void budget_from_measurement(double fps, Ms jitter_buffer) {
    try {
        const auto measured = configs::video_ip(fps, jitter_buffer);
        std::cout << std::format(" Замір: {:.0f} кадр/с, буфер {:.0f} мс -> Glass-to-Glass {:.1f} мс\n",
                                 fps, jitter_buffer.count(),
                                 measured.track().summary().typ.count());
    } catch (const std::exception& e) {
        std::cout << std::format(" Замір ({:.0f} кадр/с, буфер {:.0f} мс) відкинуто: {}\n",
                                 fps, jitter_buffer.count(), e.what());
    }
}

}  // namespace

int main() {
    // 1. Два контури керування в подробицях.
    report::print_track(configs::kStickLocked.track());
    report::print_dynamics(configs::kStickLocked.title(),
                           configs::kStickLocked.track().summary(),
                           kControlHz, kSpeedMps);

    report::print_track(configs::kStickAnalog.track());
    report::print_dynamics(configs::kStickAnalog.title(),
                           configs::kStickAnalog.track().summary(),
                           kControlHz, kSpeedMps);

    // 2. Ціна зведення фаз: та сама залізяка, зведена й не зведена.
    //    Різниця лише в одній ланці — і вона вилазить у джитер.
    constexpr std::array sticks{configs::kStickLocked.track(),
                                configs::kStickFree.track(),
                                configs::kStickAnalog.track()};
    report::print_comparison("КОНТУР КЕРУВАННЯ: Stick-to-Motor", sticks);

    // 3. Три відеотракти. Аналог виграє не роздільною здатністю, а
    //    відсутністю буферів; IP програє не радіо, а чергами ОС.
    report::print_track(configs::kVideoDigital.track());
    constexpr std::array videos{configs::kVideoAnalog.track(),
                                configs::kVideoDigital.track(),
                                configs::kVideoIp.track()};
    report::print_comparison("ВІДЕОТРАКТ: Glass-to-Glass", videos);

    // 4. Замкнений контур оператора: команда плюс картинка.
    closed_loop("Цифра + аналогове відео", configs::kStickLocked.track(),
                configs::kVideoAnalog.track());
    closed_loop("Цифра + цифрове HD", configs::kStickLocked.track(),
                configs::kVideoDigital.track());
    closed_loop("Аналог + LTE-стрім", configs::kStickAnalog.track(),
                configs::kVideoIp.track());

    // 5. Параметри із заміру, а не з коду — включно з негодящим.
    std::cout << " ПЕРЕРАХУНОК ЗА ЗАМІРОМ\n";
    budget_from_measurement(30.0, 60.0ms);
    budget_from_measurement(60.0, 25.0ms);
    budget_from_measurement(0.0, 60.0ms);  // камера не віддала кадрову частоту
    std::cout << '\n';

    return 0;
}
