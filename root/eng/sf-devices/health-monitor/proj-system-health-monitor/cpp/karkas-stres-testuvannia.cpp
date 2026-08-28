#include <iostream>
#include <cassert>

namespace Health::Tests {

void run_unit_tests() {
    Supervisor<8, 16> sup;

    uint16_t mock_power = 1000;
    uint16_t mock_stack = 1000;
    uint16_t mock_can   = 1000;

    sup.register_component("Power", [&]() { return mock_power; }, 40, true);
    sup.register_component("Stack", [&]() { return mock_stack; }, 30, false);
    sup.register_component("CAN",   [&]() { return mock_can; },   30, false);

    // Тест 1: Номінальний стан (з урахуванням Warm-up)
    for (int i = 0; i < 25; ++i) {
        sup.tick(i * 50);
    }
    assert(sup.state() == State::Nominal);
    assert(sup.system_score() > 950);

    // Тест 2: Деградація другорядного вузла
    mock_can = 200;
    for (int i = 0; i < 16; ++i) {
        sup.tick(1500 + i * 50);
    }
    assert(sup.state() == State::Degraded || sup.state() == State::Critical);
    assert(sup.system_score() < 900);

    // Тест 3: Аварія критичного вузла
    mock_power = 100;
    for (int i = 0; i < 16; ++i) {
        sup.tick(2500 + i * 50);
    }
    assert(sup.state() == State::Emergency);
    assert(sup.system_score() == 0);

    // Тест 4: Перевірка чорної скриньки
    const auto log = sup.blackbox();
    assert(log[0].magic == BlackboxMagic);
    assert(log[0].system_state == State::Emergency);

    std::cout << "Health Monitor C++20 Unit Tests: ALL PASSED (4/4)\n";
}

} // namespace Health::Tests
