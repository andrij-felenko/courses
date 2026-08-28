#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void app_main(void) {
    // Журнал тут окремо не піднімають: ESP_LOG* пише в UART від старту.

    if (!camera_start())  return;   // камера не піднялася — далі немає сенсу
    if (!sdcard_start())  return;   // картка не змонтувалася — так само

    // Ім'я файлу зі зростаючим лічильником, щоб не затирати попередні.
    static int n = 0;
    char path[40];
    snprintf(path, sizeof(path), "/sdcard/photo_%04d.jpg", n++);

    save_photo(path);

    // Замість порожнього loop() — задача просто спить: один знімок уже зроблено.
    while (true) vTaskDelay(pdMS_TO_TICKS(1000));
}
