#include "PogoPinContactMonitor.hpp"

#include <iostream>

int main() {
    std::cout << "=== Система аналізу надійності пружинних контактів Pogo Pin (C++) ===\n";

    PogoPinContactMonitor::Config cfg;
    cfg.min_glitch_duration = std::chrono::microseconds(10);
    cfg.noise_filter_threshold = std::chrono::microseconds(2);

    PogoPinContactMonitor monitor(cfg);

    auto base_time = PogoPinContactMonitor::Clock::now();
    auto current_time = base_time;

    // Стан початкового нормального притиску
    monitor.registerEdge(true, current_time);

    // Імітація вібраційного циклу:
    // 1. Короткий відскок плунжера через 50 мс, тривалість 35 мкс
    current_time += std::chrono::milliseconds(50);
    monitor.registerEdge(false, current_time);
    current_time += std::chrono::microseconds(35);
    monitor.registerEdge(true, current_time);

    // 2. Дрібний шум на 4 мкс через 100 мс (менше за поріг 10 мкс, ігнорується)
    current_time += std::chrono::milliseconds(100);
    monitor.registerEdge(false, current_time);
    current_time += std::chrono::microseconds(4);
    monitor.registerEdge(true, current_time);

    // 3. Відчутне розмикання через резонанс на 120 мкс через 200 мс
    current_time += std::chrono::milliseconds(200);
    monitor.registerEdge(false, current_time);
    current_time += std::chrono::microseconds(120);
    monitor.registerEdge(true, current_time);

    // Загальна тривалість тестової сесії 1 секунда (1000 мс)
    auto total_duration = std::chrono::milliseconds(1000);
    auto report = monitor.finalizeReport(std::chrono::duration_cast<std::chrono::microseconds>(total_duration));

    monitor.printReport(report);

    return 0;
}
