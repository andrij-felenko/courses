#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"

#define PIN_NUM_MISO 19
#define PIN_NUM_MOSI 23
#define PIN_NUM_CLK  18
#define PIN_NUM_CS   5
#define PIN_NUM_BUSY 26
#define PIN_NUM_DIO1 25

static spi_device_handle_t spi_handle;
static SemaphoreHandle_t dio1_semaphore = NULL;

// Обробник апаратного переривання від лінії DIO1
static void IRAM_ATTR dio1_isr_handler(void* arg) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(dio1_semaphore, &xHigherPriorityTaskWoken);
    if (xHigherPriorityTaskWoken) {
        portYIELD_FROM_ISR();
    }
}

// Очікування падіння лінії BUSY у логічний нуль
static void sx1262_wait_busy(void) {
    while (gpio_get_level(PIN_NUM_BUSY) == 1) {
        esp_rom_delay_us(5);
    }
}

// Передача команди по шині SPI із дотриманням таймінгів BUSY
esp_err_t sx1262_write_command(uint8_t opcode, const uint8_t *params, size_t param_len) {
    sx1262_wait_busy();

    gpio_set_level(PIN_NUM_CS, 0);

    spi_transaction_t t_cmd = {
        .length = 8,
        .tx_buffer = &opcode,
    };
    esp_err_t ret = spi_device_polling_transmit(spi_handle, &t_cmd);
    if (ret != ESP_OK) {
        gpio_set_level(PIN_NUM_CS, 1);
        return ret;
    }

    if (param_len > 0 && params != NULL) {
        spi_transaction_t t_data = {
            .length = param_len * 8,
            .tx_buffer = params,
        };
        ret = spi_device_polling_transmit(spi_handle, &t_data);
    }

    gpio_set_level(PIN_NUM_CS, 1);
    
    // Затримка на вихід лінії BUSY у стан HIGH після підняття CS
    sx1262_wait_busy();
    return ret;
}

// Фонова задача обробки подій трансивера
void sx1262_event_task(void *pvParameters) {
    uint8_t clear_irq_cmd[2] = {0x07, 0xFF}; // Маска скидання всіх подій
    for (;;) {
        if (xSemaphoreTake(dio1_semaphore, portMAX_DELAY) == pdTRUE) {
            printf("Отримано сигнал DIO1: обробка події радіомодуля\n");
            // Скидання прапорців переривань (Opcode 0x02)
            sx1262_write_command(0x02, clear_irq_cmd, 2);
        }
    }
}
