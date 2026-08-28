#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

#define I2C_MASTER_NUM       I2C_NUM_0
#define MCP23017_I2C_ADDR    0x20
#define INT_INPUT_PIN        GPIO_NUM_4

static QueueHandle_t gpio_evt_queue = NULL;

static void IRAM_ATTR gpio_isr_handler(void* arg) {
    uint32_t gpio_num = (uint32_t) arg;
    xQueueSendFromISR(gpio_evt_queue, &gpio_num, NULL);
}

static void expander_task(void* arg) {
    uint32_t io_num;
    while (1) {
        if (xQueueReceive(gpio_evt_queue, &io_num, portMAX_DELAY)) {
            /* Затримка дебаунсингу перед опитуванням I2C */
            vTaskDelay(pdMS_TO_TICKS(25));

            uint8_t intf_reg = 0x0E;
            uint8_t intf_data[2] = {0};
            uint8_t intcap_reg = 0x10;
            uint8_t intcap_data[2] = {0};

            /* Читання прапорців */
            i2c_master_write_read_device(I2C_MASTER_NUM, MCP23017_I2C_ADDR,
                                         &intf_reg, 1, intf_data, 2, pdMS_TO_TICKS(50));
            /* Читання знімка стану пінів */
            i2c_master_write_read_device(I2C_MASTER_NUM, MCP23017_I2C_ADDR,
                                         &intcap_reg, 1, intcap_data, 2, pdMS_TO_TICKS(50));

            uint16_t flags = (uint16_t)intf_data[0] | ((uint16_t)intf_data[1] << 8);
            uint16_t levels = (uint16_t)intcap_data[0] | ((uint16_t)intcap_data[1] << 8);

            /* Логіка обробки подій периферії */
        }
    }
}
