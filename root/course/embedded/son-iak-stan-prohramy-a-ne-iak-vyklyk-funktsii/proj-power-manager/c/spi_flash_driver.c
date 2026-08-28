/* ============================================================================
 * spi_flash_driver.c — Драйвер Flash з інтеграцією в диспетчер живлення (C)
 * ============================================================================ */
#include "power_manager.h"
#include <stdbool.h>

static bool s_flash_busy = false;

static bool flash_pre_sleep_hook(pm_mode_t target_mode) {
    if (s_flash_busy) {
        /* Забороняємо глибокий сон під час запису секторів */
        return false;
    }

    if (target_mode == PM_MODE_STOP || target_mode == PM_MODE_STANDBY) {
        /* 1. Відправка апаратної команди Deep Power Down (0xB9) у мікросхему */
        /* spi_send_byte(0xB9); */

        /* 2. Переведення ліній шини SPI (SCK, MOSI, MISO) у режим Analog High-Z */
        /* gpio_set_mode_analog(SPI_PINS); */
    }
    return true;
}

static void flash_post_wakeup_hook(pm_mode_t from_mode) {
    if (from_mode == PM_MODE_STOP || from_mode == PM_MODE_STANDBY) {
        /* 1. Відновлення режимів альтернативної функції для пінів SPI */
        /* gpio_set_mode_af(SPI_PINS); */

        /* 2. Пробудження мікросхеми Flash сигналом Chip Select або командою 0xAB */
        /* spi_send_byte(0xAB); */
    }
}

static const pm_driver_client_t s_flash_client = {
    .name = "SPI_Flash",
    .pre_sleep = flash_pre_sleep_hook,
    .post_wakeup = flash_post_wakeup_hook
};

void spi_flash_init(void) {
    pm_register_client(&s_flash_client);
}

void spi_flash_write_sector_async(uint32_t address, const uint8_t *data, size_t len) {
    (void)address; (void)data; (void)len;

    /* Захоплюємо блокування: забороняємо системі переходити в режим STOP під час DMA */
    pm_lock_acquire(PM_LOCK_NO_STOP);
    s_flash_busy = true;

    /* Запуск асинхронної передачі через DMA... */
}

/* Обробник переривання завершення DMA передачі */
void DMA1_Channel3_IRQHandler(void) {
    /* Очищення прапорця завершення передачі */
    s_flash_busy = false;

    /* Звільняємо блокування — система знову має право заснути в глибокий режим STOP */
    pm_lock_release(PM_LOCK_NO_STOP);
}
