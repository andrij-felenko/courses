#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"

// Структура стану драйвера прихована від користувача API
typedef struct {
    gpio_num_t pin_clock;
    gpio_num_t pin_data;
    gpio_num_t pin_req;
    volatile uint64_t raw_buffer;
    volatile uint8_t bit_count;
    SemaphoreHandle_t data_ready_sem;
} digimatic_dev_t;

// Обробник переривання тактового сигналу
static void IRAM_ATTR digimatic_isr_handler(void* arg) {
    digimatic_dev_t* dev = (digimatic_dev_t*)arg;
    
    // Зчитуємо біт і додаємо в буфер
    uint8_t bit = gpio_get_level(dev->pin_data);
    dev->raw_buffer |= ((uint64_t)bit << dev->bit_count);
    dev->bit_count++;
    
    // Пакет протоколу має 52 біти (13 ніблів)
    if (dev->bit_count >= 52) {
        BaseType_t high_task_wakeup = pdFALSE;
        xSemaphoreGiveFromISR(dev->data_ready_sem, &high_task_wakeup);
        dev->bit_count = 0; // Підготовка до наступного пакета
        if (high_task_wakeup == pdTRUE) {
            portYIELD_FROM_ISR();
        }
    }
}
