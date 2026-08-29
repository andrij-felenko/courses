// main.cpp — головний цикл: черга подій і автомат.
//
// Прошивка складається з двох частин, які майже не знають одна про одну.
// Переривання лише кладуть сигнали в чергу і негайно завершуються;
// головний цикл забирає події по одній і віддає автоматові, який обробляє
// кожну до кінця (run-to-completion). Ніде немає жодного очікування.
//
// На хості справжніх переривань немає, тому їх роль грає simTick():
// на кожному такті вона вирішує, що «сталося» в залізі.
#include "device/host_board.hpp"
#include "device/menu_ui.hpp"
#include "hsm/event_queue.hpp"
#include "hsm/hsm.hpp"

#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>

namespace {

constexpr std::uint32_t kTickMs = 10;    // один такт системного таймера
constexpr std::uint32_t kIdleTicks = 50; // бездіяльність до згасання екрана
constexpr std::uint32_t kSimTicks = 130;

using Queue = hsm::EventQueue<16>;

Queue g_queue;                  // пишуть переривання, читає головний цикл
std::uint32_t g_ticksIdle = 0;  // тактів від останнього натискання

// Сценарій натискань: такт -> сигнал. Замінює зчитувач клавіатури.
struct SimInput {
    std::uint32_t tick;
    hsm::Signal sig;
};

constexpr std::array kScript{
    SimInput{5, device::kBtnEnter},      // ScreenSaver -> Active -> MainMenu
    SimInput{10, device::kBtnDown},      // виділяємо «Налаштування»
    SimInput{15, device::kBtnEnter},     // MainMenu -> Settings
    SimInput{20, device::kBtnUp},        // яскравіше
    SimInput{25, device::kSensorFault},  // аварію ловить Active, а не Settings
    SimInput{30, device::kBtnEnter},     // Settings -> Calibration
    SimInput{35, device::kBtnEnter},     // результат прийнято, назад у Settings
    SimInput{40, device::kBtnEnter},     // знову в Calibration — і більше ні звуку
    // такт 90: спрацює таймаут бездіяльності й розкрутить усю гілку
    SimInput{100, device::kBtnBack}      // прокидаємось удруге
};

// Переривання клавіатури: кладе подію і скидає лічильник бездіяльності.
void isrKeypad(hsm::Signal sig) {
    g_ticksIdle = 0;
    if (!g_queue.push(hsm::Event{sig})) {
        std::cout << "  [ISR ] чергу переповнено, натискання втрачено\n";
    }
}

// Переривання давача: аварія приходить асинхронно і бездіяльності не скасовує.
void isrSensorFault() {
    if (!g_queue.push(hsm::Event{device::kSensorFault})) {
        std::cout << "  [ISR ] чергу переповнено, аварію втрачено\n";
    }
}

// Переривання системного таймера: рахує бездіяльність і сам породжує подію.
void isrSysTick() {
    ++g_ticksIdle;
    if (g_ticksIdle >= kIdleTicks) {
        g_ticksIdle = 0;
        static_cast<void>(g_queue.push(hsm::Event{device::kTimeoutIdle}));
    }
}

void simTick(std::uint32_t tick) {
    for (const auto& input : kScript) {
        if (input.tick == tick) {
            if (input.sig == device::kSensorFault) {
                isrSensorFault();
            } else {
                isrKeypad(input.sig);
            }
        }
    }
    isrSysTick();
}

} // namespace

// Контракт рушія: порушення інваріанта зупиняє програму.
namespace hsm {
[[noreturn]] void onFault(Fault code, const char* where) {
    std::cerr << "ФАТАЛЬНО: порушено контракт HSM, код " << static_cast<int>(code)
              << ", місце " << where << '\n';
    // На платі тут був би запис причини в резервний регістр і апаратне
    // перезавантаження: працювати далі з невідомим станом небезпечніше,
    // ніж перезапуститися.
    std::abort();
}
} // namespace hsm

int main() {
    device::HostBoard board;
    device::MenuUi<device::HostBoard> ui{board};

    std::cout << "== початковий перехід ==\n";
    ui.init();

    std::uint32_t sleepTicks = 0;

    for (std::uint32_t tick = 0; tick < kSimTicks; ++tick) {
        simTick(tick);

        // Черга спорожняється повністю: кожна подія обробляється до кінця,
        // і лише потім береться наступна. Саме це й означає «неблокуючий
        // цикл» — жодного очікування всередині обробки.
        while (const auto e = g_queue.pop()) {
            std::cout << "== " << tick * kTickMs << " мс: сигнал "
                      << static_cast<int>(e->sig) << " ==\n";
            ui.dispatch(*e);
        }

        // Черга порожня. Прошивка на платі викликала б тут __WFI() і чекала
        // на наступне переривання; у заставці ядро ще й скидає частоту.
        if (ui.isAsleep()) {
            ++sleepTicks;
        }
    }

    std::cout << "\n== підсумок ==\n"
              << "втрачено подій: " << g_queue.dropped() << '\n'
              << "тактів у мікроспоживанні: " << sleepTicks << " з " << kSimTicks << '\n';
    return 0;
}
