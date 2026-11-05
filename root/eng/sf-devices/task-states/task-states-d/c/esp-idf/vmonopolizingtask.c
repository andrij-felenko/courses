#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

// Поганий підхід: монополізація процесора в активному циклі
void vMonopolizingTask(void *pvParameters) {
    while (1) {
        // Активне очікування нажаття кнопки (busy waiting)
        while (gpio_get_level(GPIO_NUM_0) == 1) {
            // Процесор завантажений на 100%, інші задачі не отримують квантів часу
        }
        // Обробка події
        vProcessButtonPress();
    }
}

// Ефективний підхід: виклик затримки та передача управління RTOS
void vNonBlockingTask(void *pvParameters) {
    while (1) {
        if (gpio_get_level(GPIO_NUM_0) == 0) {
            vProcessButtonPress();
        }
        // Передача управління планивальнику RTOS на 10 системних тіків
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
