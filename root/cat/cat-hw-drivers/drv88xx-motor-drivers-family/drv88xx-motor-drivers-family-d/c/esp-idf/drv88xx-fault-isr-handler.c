#include "driver/gpio.h"
#include "esp_log.h"

#define GPIO_NFAULT_PIN    GPIO_NUM_19
#define GPIO_ENABLE_PIN    GPIO_NUM_18
static const char *TAG = "DRV88XX_GUARD";

static void IRAM_ATTR drv88xx_fault_isr_handler(void* arg) {
    // Негайно вимикаємо драйвер шляхом скидання лінії ENABLE
    gpio_set_level(GPIO_ENABLE_PIN, 0);
}

void init_drv88xx_protection(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_NFAULT_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE, // Підтяжка для відкритого стоку
        .intr_type = GPIO_INTR_NEGEDGE   // Переривання за спадаючим фронтом
    };
    gpio_config(&io_conf);

    gpio_config_t out_conf = {
        .pin_bit_mask = (1ULL << GPIO_ENABLE_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_DISABLE
    };
    gpio_config(&out_conf);
    gpio_set_level(GPIO_ENABLE_PIN, 1); // Активація драйвера

    gpio_install_isr_service(0);
    gpio_isr_handler_add(GPIO_NFAULT_PIN, drv88xx_fault_isr_handler, NULL);
}
