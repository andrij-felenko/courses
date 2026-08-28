// Переривання EXTI0 у мові C
void EXTI0_IRQHandler(void) {
    if (EXTI->PR & (1 << 0)) {
        EXTI->PR = (1 << 0); // Скидання прапорця переривання
        sys_event_t evt = {
            .id = EVT_ID_BUTTON_CLICK,
            .timestamp_ms = sys_get_tick_ms(),
            .data.button_pin = 0
        };
        event_queue_post_from_isr(&g_main_queue, &evt);
    }
}
