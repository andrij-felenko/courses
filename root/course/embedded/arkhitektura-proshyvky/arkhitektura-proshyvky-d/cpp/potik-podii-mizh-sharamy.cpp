// Переривання EXTI0 з викликом черги C++
extern "C" void EXTI0_IRQHandler() {
    if (EXTI->PR & (1 << 0)) {
        EXTI->PR = (1 << 0); // Скидання прапорця переривання
        events::SystemEvent evt{
            .id = events::EventId::ButtonClick,
            .timestamp_ms = board::get_tick_ms(),
            .payload = static_cast<uint8_t>(0)
        };
        board::get_main_queue().push_from_isr(evt);
    }
}
