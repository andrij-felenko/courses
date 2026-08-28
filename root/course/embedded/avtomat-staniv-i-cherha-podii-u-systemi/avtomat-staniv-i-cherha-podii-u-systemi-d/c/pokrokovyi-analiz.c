int main(void) {
    iot_node_t node;
    hsm_init((hsm_t *)&node, state_root);

    printf("\n--- Подія 1: Спрацював таймер пробудження ---\n");
    event_t e_wake = { SIG_TIMER_TICK, 0 };
    hsm_dispatch((hsm_t *)&node, &e_wake);

    printf("\n--- Подія 2: АЦП завершив вимірювання ---\n");
    event_t e_adc = { SIG_DATA_READY, 16 };
    hsm_dispatch((hsm_t *)&node, &e_adc);

    printf("\n--- Подія 3: Аварійне падіння напруги під час зв'язку ---\n");
    event_t e_batt = { SIG_LOW_BATTERY, 2800 };
    hsm_dispatch((hsm_t *)&node, &e_batt);

    return 0;
}
