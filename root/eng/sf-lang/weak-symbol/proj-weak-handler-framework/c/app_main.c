// ============================================================================
// ФАЙЛ: app_main.c (C99) — користувацький модуль із сильними перекриттями
// ============================================================================
#include "hal_driver_core.h"
#include <stdio.h>
#include <string.h>

#define RX_BUFFER_SIZE 128
static uint8_t g_rx_ring_buffer[RX_BUFFER_SIZE];
static size_t  g_rx_head = 0;
static uint32_t g_button_press_count = 0;

// СИЛЬНЕ ПЕРЕКРИТТЯ: обробка байтів UART
void hal_uart_rx_callback(const hal_event_t* evt)
{
    printf("[APP USER] Сильний обробник UART RX спрацював!\n");
    if (evt->payload && evt->length > 0) {
        for (size_t i = 0; i < evt->length; ++i) {
            g_rx_ring_buffer[g_rx_head] = evt->payload[i];
            g_rx_head = (g_rx_head + 1) % RX_BUFFER_SIZE;
        }
        printf("  -> Прийнято %zu байтів, поточна голова кільцевого буфера: %zu\n",
               evt->length, g_rx_head);
    }
}

// СИЛЬНЕ ПЕРЕКРИТТЯ: обробка натискання кнопки GPIO
void hal_gpio_edge_callback(const hal_event_t* evt)
{
    g_button_press_count++;
    printf("[APP USER] Сильний обробник GPIO спрацював! Натискань: %u\n",
           g_button_press_count);
}

// Зверніть увагу: hal_spi_transfer_callback та hal_timer_period_callback
// НЕ визначені у цьому файлі! Для них лінкер збереже hal_default_event_stub.
