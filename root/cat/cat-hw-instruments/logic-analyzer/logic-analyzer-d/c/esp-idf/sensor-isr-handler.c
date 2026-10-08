#include "driver/gpio.h"
#include "esp_attr.h"

// Призначення діагностичного виводу GPIO4 та вхідного переривання GPIO5
#define DIAG_GPIO_PIN  GPIO_NUM_4
#define SENSOR_INT_PIN GPIO_NUM_5

// Обробник зовнішнього переривання, розміщений у швидкій пам'яті IRAM
void IRAM_ATTR sensor_isr_handler(void* arg) {
    // Атомарне встановлення високого рівня на виводі (1-2 такти процесора)
    GPIO.out_w1ts = (1u << DIAG_GPIO_PIN);

    // Виконання критичного алгоритму обробки даних датчика
    process_sensor_sample();

    // Атомарне скидання виводу в низький логічний рівень перед виходом
    GPIO.out_w1tc = (1u << DIAG_GPIO_PIN);
}
