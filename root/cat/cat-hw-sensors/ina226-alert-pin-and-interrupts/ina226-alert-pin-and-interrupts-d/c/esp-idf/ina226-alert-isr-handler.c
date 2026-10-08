#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

#define INA226_ALERT_PIN       GPIO_NUM_4
#define POWER_MOSFET_PIN       GPIO_NUM_5
#define INA226_I2C_ADDR        0x40
#define INA226_REG_MASK_ENABLE 0x06

static QueueHandle_t alert_evt_queue = NULL;

// Неблокувальний апаратний обробник переривань (ISR)
static void IRAM_ATTR ina226_alert_isr_handler(void* arg) {
    // Негайна апаратна дія захисту без затримок і шини I2C
    gpio_set_level(POWER_MOSFET_PIN, 0); // Відключаємо силовий MOSFET
    
    uint32_t gpio_num = (uint32_t) arg;
    xQueueSendFromISR(alert_evt_queue, &gpio_num, NULL);
}

// Фонова задача обробки тривог та скидання засувки по I2C
static void ina226_alert_task(void* arg) {
    uint32_t io_num;
    uint8_t reg_addr = INA226_REG_MASK_ENABLE;
    uint8_t data[2];

    for (;;) {
        if (xQueueReceive(alert_evt_queue, &io_num, portMAX_DELAY)) {
            // Зчитати регістр Mask/Enable (0x06) для скидання засувки LEN та з'ясування причини
            i2c_master_write_read_device(I2C_NUM_0, INA226_I2C_ADDR, 
                                         &reg_addr, 1, 
                                         data, 2, 
                                         100 / portTICK_PERIOD_MS);
            
            uint16_t mask_enable = (data[0] << 8) | data[1];
            printf("ALERT triggered on GPIO %lu! Mask/Enable register: 0x%04X\n", io_num, mask_enable);
        }
    }
}

void app_main(void) {
    // Налаштування GPIO для відключення силового ключа
    gpio_config_t io_conf_out = {
        .pin_bit_mask = (1ULL << POWER_MOSFET_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf_out);
    gpio_set_level(POWER_MOSFET_PIN, 1); // Вмикаємо живлення

    // Налаштування GPIO для виводу ALERT (вхід з перериванням по спаду)
    gpio_config_t io_conf_in = {
        .pin_bit_mask = (1ULL << INA226_ALERT_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_NEGEDGE
    };
    gpio_config(&io_conf_in);

    alert_evt_queue = xQueueCreate(10, sizeof(uint32_t));
    xTaskCreate(ina226_alert_task, "ina226_alert_task", 2048, NULL, 10, NULL);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(INA226_ALERT_PIN, ina226_alert_isr_handler, (void*) INA226_ALERT_PIN);
}
