// Клієнт первинного рукостискання: відкриває порт радіомодема й веде апарат
// через п'ять фаз до робочого стану.
//
// Збірка: g++ -std=c++20 -I<шлях-до-mavlink> *.cpp -o handshake
// Запуск:  ./handshake /dev/ttyUSB0 57600
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <string>
#include <thread>

#include "handshake.h"

namespace {
volatile std::sig_atomic_t g_stop = 0;
void onSignal(int) { g_stop = 1; }
}  // namespace

int main(int argc, char** argv) {
    const std::string device = argc > 1 ? argv[1] : "/dev/ttyUSB0";
    const unsigned baud = argc > 2 ? std::strtoul(argv[2], nullptr, 10) : 57600;

    std::signal(SIGINT, onSignal);

    try {
        SerialLink link(device, baud);
        HandshakeEngine engine(link);
        std::cout << "[gcs] слухаємо " << device << " на " << baud << " бод; ефір поки мовчимо\n";

        while (!g_stop) {
            // Неблокувальний цикл: жодна фаза не має права зупинити вичитку порту,
            // інакше апаратний буфер USART переповниться і кадри поб'ються.
            const auto now = Clock::now();
            for (const auto& msg : link.receive()) {
                engine.onMessage(msg, now);
            }
            engine.tick(now);
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }
        std::cout << "\n[gcs] зупинено оператором, стан " << stateName(engine.state()) << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "[fatal] " << e.what() << "\n";
        return 1;
    }
}
