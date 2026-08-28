#include <stdio.h>
#include <assert.h>

void run_clock_manager_tests_c(void) {
    // 1. Ініціалізація
    clock_manager_init();
    assert(!clock_manager_is_enabled(PERIPH_USART1));
    assert(!clock_manager_is_enabled(PERIPH_GPIOA));
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_APB2) == 0);
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_AHB1) == 0);

    // 2. Захоплення USART1 (має автоматично ввімкнути GPIOA)
    clock_status_t status = clock_manager_acquire(PERIPH_USART1);
    assert(status == CLOCK_STATUS_OK);
    assert(clock_manager_is_enabled(PERIPH_USART1));
    assert(clock_manager_is_enabled(PERIPH_GPIOA));
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_APB2) == 1);
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_AHB1) == 1);

    // 3. Другий клієнт захоплює GPIOA напряму
    status = clock_manager_acquire(PERIPH_GPIOA);
    assert(status == CLOCK_STATUS_OK);

    // 4. Перший клієнт звільняє USART1 (GPIOA повинен залишитися активним!)
    status = clock_manager_release(PERIPH_USART1);
    assert(status == CLOCK_STATUS_OK);
    assert(!clock_manager_is_enabled(PERIPH_USART1));
    assert(clock_manager_is_enabled(PERIPH_GPIOA)); // GPIOA все ще потрібен другому клієнту
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_APB2) == 0); // Домен APB2 заснув!
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_AHB1) == 1);

    // 5. Другий клієнт звільняє GPIOA (усе вимикається)
    status = clock_manager_release(PERIPH_GPIOA);
    assert(status == CLOCK_STATUS_OK);
    assert(!clock_manager_is_enabled(PERIPH_GPIOA));
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_AHB1) == 0); // Домен AHB1 заснув!

    // 6. Складна залежність: SPI1 (тягне GPIOA та DMA2)
    status = clock_manager_acquire(PERIPH_SPI1);
    assert(status == CLOCK_STATUS_OK);
    assert(clock_manager_is_enabled(PERIPH_SPI1));
    assert(clock_manager_is_enabled(PERIPH_GPIOA));
    assert(clock_manager_is_enabled(PERIPH_DMA2));
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_APB2) == 1);
    assert(clock_manager_get_bus_activity(BUS_DOMAIN_AHB1) == 2); // GPIOA + DMA2

    // Звільнення SPI1
    status = clock_manager_release(PERIPH_SPI1);
    assert(status == CLOCK_STATUS_OK);
    assert(!clock_manager_is_enabled(PERIPH_SPI1));
    assert(!clock_manager_is_enabled(PERIPH_GPIOA));
    assert(!clock_manager_is_enabled(PERIPH_DMA2));
}
