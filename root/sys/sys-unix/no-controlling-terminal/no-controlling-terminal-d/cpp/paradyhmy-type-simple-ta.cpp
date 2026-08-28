#include <systemd/sd-daemon.h>
#include <chrono>
#include <iostream>
#include <thread>

int main() {
    std::setvbuf(stdout, nullptr, _IOLBF, 0);

    std::cout << "Ініціалізація компонентів C++...\n";
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Сповіщаємо супервізор про готовність
    ::sd_notify(0, "READY=1\nSTATUS=Обробка клієнтських запитів (C++20)");

    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(10));
    }
    return 0;
}
