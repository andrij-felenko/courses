#include <stdio.h>
#include <assert.h>

void run_escape_simulation_test(void) {
    LocalMinimaEscapeModule mod;
    local_minima_init(&mod, 0.02f); /* 50 Гц */

    Vec3 goal = {20.0f, 0.0f, 0.0f};
    Vec3 pos = {0.0f, 0.0f, 0.0f};
    Vec3 vel = {2.0f, 0.0f, 0.0f};
    Vec3 setpoint;
    bool replan_req = false;

    printf("[TEST] 1. Рух вперед до входу у пастку...\n");
    for (int step = 0; step < 150; ++step) {
        pos.x += vel.x * 0.02f;
        local_minima_step(&mod, &pos, &vel, &goal, true, 10.0f, NULL, 0, &setpoint, &replan_req);
    }
    assert(mod.crumbs.count > 5);
    printf("       Успішно записано %d крихт у буфер.\n", mod.crumbs.count);

    printf("[TEST] 2. Вхід у зону рівноваги сил (швидкість падає до 0)...\n");
    vel.x = 0.0f;
    vel.y = 0.0f;
    for (int step = 0; step < 160; ++step) {
        local_minima_step(&mod, &pos, &vel, &goal, true, 1.0f, NULL, 0, &setpoint, &replan_req);
    }

    assert(mod.state == ESCAPE_STATE_BACKTRACK);
    printf("       Зависання виявлено! Стан перемкнуто на ESCAPE_STATE_BACKTRACK.\n");

    printf("[TEST] 3. Виконання відкату по записаних крихтах...\n");
    while (mod.state == ESCAPE_STATE_BACKTRACK) {
        pos.x = setpoint.x;
        pos.y = setpoint.y;
        local_minima_step(&mod, &pos, &vel, &goal, true, 1.0f, NULL, 0, &setpoint, &replan_req);
    }

    assert(replan_req == true);
    printf("       Відкат завершено на відстань %.2f м! Прапорець replan = TRUE.\n", mod.backtrack_accum_dist);
    printf("[TEST] ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО.\n");
}
