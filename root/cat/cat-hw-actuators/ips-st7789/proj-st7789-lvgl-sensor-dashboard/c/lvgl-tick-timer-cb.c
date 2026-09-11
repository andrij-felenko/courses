#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_timer.h"
#include "lvgl.h"

// М'ютекс для взаємного виключення під час доступу до API бібліотеки
static SemaphoreHandle_t gui_mutex = NULL;

static lv_obj_t *arc_temperature = NULL;
static lv_obj_t *lbl_temp_value = NULL;

// Апаратний таймер: інкремент системного тікера щомілісекунди
static void lvgl_tick_timer_cb(void *arg)
{
    lv_tick_inc(1);
}

// Окрема нитка періодичного опитування кліматичних датчиків
static void sensor_worker_task(void *pvParameters)
{
    int16_t measured_temp = 20;

    for (;;) {
        // Зчитування шини I2C без впливу на рендеринг графіки
        measured_temp = (measured_temp >= 35) ? 17 : (measured_temp + 1);

        // Захищене оновлення стану віджетів через м'ютекс
        if (xSemaphoreTake(gui_mutex, pdMS_TO_TICKS(50)) == pdTRUE) {
            lv_arc_set_value(arc_temperature, measured_temp);
            lv_label_set_text_fmt(lbl_temp_value, "%d °C", measured_temp);
            xSemaphoreGive(gui_mutex);
        }

        // Переведення задачі в режим очікування на 1000 мс
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// Нитка диспетчеризації графічного інтерфейсу користувача
static void gui_render_task(void *pvParameters)
{
    for (;;) {
        // Виклик обробника задач у захищеній секції
        if (xSemaphoreTake(gui_mutex, pdMS_TO_TICKS(20)) == pdTRUE) {
            lv_timer_handler();
            xSemaphoreGive(gui_mutex);
        }

        // Квант очікування 10 мс забезпечує частоту рендерингу до 100 FPS
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void app_main(void)
{
    gui_mutex = xSemaphoreCreateMutex();
    lv_init();

    // Налаштування та запуск високоточного апаратного таймера для тікера
    const esp_timer_create_args_t periodic_timer_args = {
        .callback = &lvgl_tick_timer_cb,
        .name = "lvgl_tick"
    };
    esp_timer_handle_t periodic_timer;
    esp_timer_create(&periodic_timer_args, &periodic_timer);
    esp_timer_start_periodic(periodic_timer, 1000); // 1000 мкс = 1 мс

    // Побудова графічного інтерфейсу...
    arc_temperature = lv_arc_create(lv_scr_act());
    lbl_temp_value = lv_label_create(lv_scr_act());

    // Запуск паралельних потоків у диспетчері FreeRTOS
    xTaskCreatePinnedToCore(gui_render_task, "gui_task", 4096, NULL, 5, NULL, 1);
    xTaskCreatePinnedToCore(sensor_worker_task, "sensor_task", 2048, NULL, 2, NULL, 0);
}
