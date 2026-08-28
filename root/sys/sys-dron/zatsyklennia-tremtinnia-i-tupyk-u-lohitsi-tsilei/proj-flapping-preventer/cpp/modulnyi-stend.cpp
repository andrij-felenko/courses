#include <iostream>
#include <cmath>

void runVerificationCpp() {
    uint32_t nowUs = 0;
    drone::autonomy::FlappingPreventer filter(0.60f, 0.40f, 200'000, 1'000'000, 5.0f, 2.0f, nowUs);

    std::cout << "--- Тест 1: Зашумлений сигнал у смузі гістерезису ---\n";
    for (int step = 0; step < 100; ++step) {
        nowUs += 20'000; // 50 Гц
        const float noise = (static_cast<float>(step % 7) - 3.0f) * 0.03f;
        const float signal = 0.50f + noise;
        filter.process(signal, 1, 10.0f, 10.0f, 50.0f, nowUs, false);
    }
    std::cout << "Заблоковано брязкоту: " << filter.suppressedSwitches()
              << ", стан: " << (filter.state() ? "TRUE" : "FALSE") << "\n";

    std::cout << "--- Тест 2: 3-фазне просторове зациклення A->B->C->A ---\n";
    const uint16_t states[3] = {101, 102, 103};
    const float coords[3][3] = {
        {10.0f, 10.0f, 50.0f},
        {30.0f, 10.0f, 50.0f},
        {20.0f, 25.0f, 50.0f}
    };

    for (int cycle = 0; cycle < 4; ++cycle) {
        for (int phase = 0; phase < 3; ++phase) {
            nowUs += 500'000;
            filter.process(0.8f, states[phase], coords[phase][0], coords[phase][1], coords[phase][2], nowUs, false);
        }
    }
    std::cout << "Детектовано цикл: " << static_cast<int>(filter.detectedCycleLength())
              << ", Рівень ескалації: " << static_cast<int>(filter.escalation()) << "\n";
}
