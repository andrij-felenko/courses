// НЕКОРЕКТНИЙ/ОБМЕЖЕНИЙ ПІДХІД: Програмна обробка квадратурного енкодера через переривання GPIO
#include "driver/gpio.h"
#include "esp_attr.h"

static volatile int32_t g_encoder_counter = 0;
static volatile uint8_t g_last_state = 0;

// Таблиця переходів фаз (0x0..0xF) для визначення напрямку рухомого вузла
static const int8_t ENC_STATES[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};

static void IRAM_ATTR gpio_encoder_isr_handler(void* arg) {
    uint32_t gpio_num = (uint32_t) arg;
    uint8_t a = gpio_get_level(GPIO_NUM_18);
    uint8_t b = gpio_get_level(GPIO_NUM_19);
    
    // Формуємо 4-бітне значення: [A_prev, B_prev, A_curr, B_curr]
    g_last_state = ((g_last_state << 2) | (a << 1) | b) & 0x0F;
    g_encoder_counter += ENC_STATES[g_last_state]; // Створює гігантське навантаження на CPU при високих RPM!
}

void init_software_gpio_encoder(void) {
    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_ANYEDGE,
        .mode = GPIO_MODE_INPUT,
        .pin_bit_mask = (1ULL << GPIO_NUM_18) | (1ULL << GPIO_NUM_19),
        .pull_up_en = GPIO_PULLUP_ENABLE
    };
    gpio_config(&io_conf);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(GPIO_NUM_18, gpio_encoder_isr_handler, (void*) 18);
    gpio_isr_handler_add(GPIO_NUM_19, gpio_encoder_isr_handler, (void*) 19);
}
