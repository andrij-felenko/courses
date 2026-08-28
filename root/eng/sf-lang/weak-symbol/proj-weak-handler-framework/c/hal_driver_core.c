// ============================================================================
// ФАЙЛ: hal_driver_core.c (C99)
// ============================================================================
#include "hal_driver_core.h"
#include <stdio.h>

static uint32_t g_system_tick_mock = 1000;

// Універсальна безпечна заглушка за замовчуванням
void hal_default_event_stub(const hal_event_t* evt)
{
    // Безпечна порожня обробка: не потребує дій, якщо подія не цікавить застосунок
    (void)evt;
}

// Універсальна аварійна пастка для невиправних помилок
void hal_default_error_trap(const hal_event_t* evt)
{
    printf("[HAL CORE FATAL] Необроблена апаратна помилка у периферії %d, тип: 0x%02X\n",
           evt->periph, evt->kind);
}

// Оголошення слабких псевдонімів, що вказують на безпечну заглушку
void hal_uart_rx_callback(const hal_event_t* evt)
    __attribute__((weak, alias("hal_default_event_stub")));

void hal_spi_transfer_callback(const hal_event_t* evt)
    __attribute__((weak, alias("hal_default_event_stub")));

void hal_gpio_edge_callback(const hal_event_t* evt)
    __attribute__((weak, alias("hal_default_event_stub")));

void hal_timer_period_callback(const hal_event_t* evt)
    __attribute__((weak, alias("hal_default_event_stub")));

void hal_error_trap_callback(const hal_event_t* evt)
    __attribute__((weak, alias("hal_default_error_trap")));

void hal_driver_init(void)
{
    printf("[HAL CORE] Ініціалізація драйверного ядра. Слабкі символи налаштовано.\n");
}

void hal_driver_dispatch_interrupt(hal_periph_id_t periph, hal_event_kind_t kind,
                                   const uint8_t* data, size_t len)
{
    hal_event_t evt;
    evt.periph = periph;
    evt.kind = kind;
    evt.timestamp_us = g_system_tick_mock++;
    evt.payload = data;
    evt.length = len;
    evt.flags = 0;

    // 1. Опціональна перевірка цілісності даних через слабке посилання
    if (hal_telemetry_crc_check_hook != NULL) {
        if (data != NULL && len > 0) {
            bool ok = hal_telemetry_crc_check_hook(data, len);
            if (!ok) {
                evt.kind = HAL_EVT_ERROR_HARDWARE;
                hal_error_trap_callback(&evt);
                return;
            }
        }
    }

    // 2. Диспетчеризація за типом периферійного пристрою (прямий виклик функції)
    switch (periph) {
    case HAL_PERIPH_UART1:
    case HAL_PERIPH_UART2:
        hal_uart_rx_callback(&evt);
        break;
    case HAL_PERIPH_SPI1:
        hal_spi_transfer_callback(&evt);
        break;
    case HAL_PERIPH_GPIO:
        hal_gpio_edge_callback(&evt);
        break;
    case HAL_PERIPH_TIMER:
        hal_timer_period_callback(&evt);
        break;
    default:
        hal_error_trap_callback(&evt);
        break;
    }

    // 3. Опціональне публікування телеметрії через слабке посилання
    if (hal_telemetry_publish_hook != NULL) {
        hal_telemetry_publish_hook(&evt);
    }
}
