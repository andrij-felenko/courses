#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Головного циклу як такого нема — його роль грає задача FreeRTOS.
// Створюють її з app_main(): xTaskCreate(appTask, "app", 4096, NULL, 5, NULL);
static void appTask(void *arg) {
    for (;;) {
        // Тут головна програма вільна: читати кнопки, давачі, рахувати.
        // Розгортка живе окремо, у перериванні таймера. Щоб змінити картинку —
        // просто перепиши frame[]; наступні оберти покажуть уже нове.
        vTaskDelay(pdMS_TO_TICKS(20));   // віддати процесор іншим задачам
    }
}
