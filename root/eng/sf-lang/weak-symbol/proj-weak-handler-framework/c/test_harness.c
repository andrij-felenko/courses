// ============================================================================
// ФАЙЛ: test_harness.c (C99) — демонстраційний тестовий сценарій
// ============================================================================
#include "hal_driver_core.h"
#include <stdio.h>

int main(void)
{
    printf("=== СТАРТ ТЕСТУВАННЯ ФРЕЙМВОРКУ СЛАБКИХ СИМВОЛІВ (C99) ===\n\n");

    hal_driver_init();

    // Тест 1. Подія UART RX -> Має викликати сильний користувацький обробник
    printf("\n--- ТЕСТ 1: Перевірка перекритого UART обробника ---\n");
    const uint8_t test_msg[] = { 'H', 'E', 'L', 'L', 'O' };
    hal_driver_dispatch_interrupt(HAL_PERIPH_UART1, HAL_EVT_RX_READY, test_msg, sizeof(test_msg));

    // Тест 2. Подія GPIO Edge -> Має викликати сильний користувацький обробник
    printf("\n--- ТЕСТ 2: Перевірка перекритого GPIO обробника ---\n");
    hal_driver_dispatch_interrupt(HAL_PERIPH_GPIO, HAL_EVT_PIN_EDGE, NULL, 0);

    // Тест 3. Подія SPI Transfer -> Не перекрита! Має тихо викликати hal_default_event_stub
    printf("\n--- ТЕСТ 3: Перевірка неперекритого SPI обробника (Default Stub) ---\n");
    const uint8_t spi_data[] = { 0xAA, 0xBB };
    hal_driver_dispatch_interrupt(HAL_PERIPH_SPI1, HAL_EVT_TRANSFER_DONE, spi_data, sizeof(spi_data));
    printf("SPI обробка завершилася безпечно без краху програми.\n");

    // Тест 4. Подія Timer Period -> Не перекрита! Спрацьовує заглушка
    printf("\n--- ТЕСТ 4: Перевірка неперекритого Таймера (Default Stub) ---\n");
    hal_driver_dispatch_interrupt(HAL_PERIPH_TIMER, HAL_EVT_PERIOD_ELAPSED, NULL, 0);
    printf("Таймер завершив роботу без збоїв.\n");

    printf("\n=== ТЕСТУВАННЯ ЗАВЕРШЕНО УСПІШНО ===\n");
    return 0;
}
