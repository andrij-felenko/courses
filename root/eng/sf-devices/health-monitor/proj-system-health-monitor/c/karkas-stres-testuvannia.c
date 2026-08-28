#include <stdio.h>
#include <assert.h>

static uint16_t s_mock_power_val = 1000;
static uint16_t s_mock_stack_val = 1000;
static uint16_t s_mock_can_val   = 1000;

static uint16_t test_collect_power(void *ctx) { (void)ctx; return s_mock_power_val; }
static uint16_t test_collect_stack(void *ctx) { (void)ctx; return s_mock_stack_val; }
static uint16_t test_collect_can(void *ctx)   { (void)ctx; return s_mock_can_val; }

void health_run_unit_tests(void) {
    health_supervisor_t sup;
    health_supervisor_init(&sup);

    health_supervisor_register(&sup, "Power", test_collect_power, NULL, 40, true);
    health_supervisor_register(&sup, "Stack", test_collect_stack, NULL, 30, false);
    health_supervisor_register(&sup, "CAN",   test_collect_can,   NULL, 30, false);

    // Тест 1: Початковий стан ідеальний (проходження періоду Warm-up)
    for (int i = 0; i < 25; ++i) {
        health_supervisor_tick(&sup, i * 50);
    }
    assert(sup.current_state == HEALTH_STATE_NOMINAL);
    assert(sup.system_score > 950);

    // Тест 2: Деградація некритичного вузла (CAN)
    s_mock_can_val = 200;
    for (int i = 0; i < 16; ++i) {
        health_supervisor_tick(&sup, 1500 + i * 50);
    }
    assert(sup.current_state == HEALTH_STATE_DEGRADED || sup.current_state == HEALTH_STATE_CRITICAL);
    assert(sup.system_score < 900);

    // Тест 3: Фатальний збій критичного вузла (Power) -> Миттєвий EMERGENCY
    s_mock_power_val = 100;
    for (int i = 0; i < 16; ++i) {
        health_supervisor_tick(&sup, 2500 + i * 50);
    }
    assert(sup.current_state == HEALTH_STATE_EMERGENCY);
    assert(sup.system_score == 0); // Мультиплікативний штраф обнулив бал

    // Тест 4: Перевірка запису в чорну скриньку
    assert(sup.blackbox_seq > 0);
    const health_blackbox_entry_t *last_log = &sup.blackbox_ring[0];
    assert(last_log->magic == HEALTH_BLACKBOX_MAGIC);
    assert(last_log->system_state == HEALTH_STATE_EMERGENCY);

    printf("Health Monitor Unit Tests: ALL PASSED (4/4)\n");
}
