#include <cassert>
#include <iostream>

void run_test_suite_cpp() {
    navigation::FastLocalOccupancyGrid grid({0.0f, 0.0f});

    // Тест 1: Додавання фронтальної перешкоди на відстані 3.0 м
    for (float y = -2.0f; y <= 2.0f; y += 0.1f) {
        grid.update_ray({0.0f, 0.0f}, {3.0f, y}, true);
    }
    grid.inflate(0.4f);

    auto decision = grid.evaluate_vfh(4.0f, 0.0f, 0.0f, 4.0f);
    assert(decision.action != navigation::AvoidanceAction::Proceed);

    // Тест 2: Перевірка зміщення координат
    grid.shift_origin({5.0f, 0.0f});
    auto decision_after_shift = grid.evaluate_vfh(4.0f, 0.0f, 0.0f, 4.0f);
    // Після зсуву стара перешкода опинилася позаду, попереду чисто
    assert(decision_after_shift.action == navigation::AvoidanceAction::Proceed);
}
