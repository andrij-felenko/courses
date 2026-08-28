#include <iostream>
#include <cassert>

void run_escape_simulation_test_cpp() {
    LocalMinimaEscapeModule mod{LocalMinimaEscapeModule::Config{.loop_dt = 0.02F}};

    const Vec3 goal{20.0F, 0.0F, 0.0F};
    Vec3 pos{0.0F, 0.0F, 0.0F};
    Vec3 vel{2.0F, 0.0F, 0.0F};

    std::cout << "[TEST CPP] 1. Рух вперед до входу у пастку...\n";
    for (int step = 0; step < 150; ++step) {
        pos.x += vel.x * 0.02F;
        mod.update(pos, vel, goal, true, 10.0F, {});
    }

    std::cout << "[TEST CPP] 2. Зависання всередині кишені...\n";
    vel = {0.0F, 0.0F, 0.0F};
    LocalMinimaEscapeModule::StepResult res{};
    for (int step = 0; step < 160; ++step) {
        res = mod.update(pos, vel, goal, true, 1.0F, {});
    }

    assert(mod.state() == EscapeFsmState::Backtrack);
    std::cout << "           Пастку виявлено! Активовано Backtrack.\n";

    std::cout << "[TEST CPP] 3. Відкат назад...\n";
    while (mod.state() == EscapeFsmState::Backtrack) {
        pos = res.setpoint;
        res = mod.update(pos, vel, goal, true, 1.0F, {});
    }

    assert(res.request_global_replan == true);
    std::cout << "           Відкат успішний! Запит глобального перепланування.\n";
    std::cout << "[TEST CPP] ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО.\n";
}
