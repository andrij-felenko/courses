// Періодичне надсилання сигналу активності у сторожовий таймер (C++20)
#include <fstream>
#include <thread>
#include <chrono>

using namespace std::chrono_literals;

int main() {
    std::ofstream watchdog("/dev/watchdog");
    if (!watchdog.is_open()) return 1;

    while (true) {
        watchdog.put('\0');
        watchdog.flush();
        std::this_thread::sleep_for(10s);
    }
    return 0;
}
