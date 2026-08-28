// Обробник аварійних збоїв прошивки у режимі випробування на C++20
#include <cstdint>

extern "C" void HardFault_Handler() noexcept {
    // Вимикаємо переривання для запобігання каскадним збоям
    __disable_irq();

    // Збереження діагностичного дампу регістрів у безпечну область RAM
    extern void save_crash_dump() noexcept;
    save_crash_dump();

    // Негайне системне скидання мікроконтролера
    NVIC_SystemReset();

    while (true) {
        // Очікування спрацювання сигналу скидання
    }
}
