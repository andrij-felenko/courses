// main.c — Головний диспетчер у C
int main(void) {
    board_hardware_init();
    event_queue_init(&g_main_queue);
    app_coordinator_init();

    while (1) {
        sys_event_t evt;
        if (event_queue_pop(&g_main_queue, &evt, TIMEOUT_MAX)) {
            app_coordinator_dispatch(&evt);
        } else {
            // Якщо подій немає, переходимо в режим збереження енергії до наступного переривання
            __WFI(); // Wait For Interrupt
        }
    }
}
