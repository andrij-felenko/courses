#include "lvgl_port.h"
#include <inttypes.h>
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

static const char *TAG = "LVGL_PORT";

/**
 * @brief Контекст порту LVGL
 */
struct lvgl_port_context_t {
    frame_buffer_descriptor_t *fb_desc;
    lv_disp_draw_buf_t disp_buf;
    lv_disp_drv_t disp_drv;
    lv_disp_t *disp_handle;
    esp_timer_handle_t tick_timer;
    TaskHandle_t task_handle;
    bool is_running;
};

static struct lvgl_port_context_t s_port_ctx;

/**
 * @brief Зворотний виклик періодичного таймера для сповіщення LVGL про перебіг часу
 */
static void lvgl_port_tick_callback(void *arg)
{
    uint32_t period_ms = (uint32_t)(uintptr_t)arg;
    lv_tick_inc(period_ms);
}

esp_err_t lvgl_port_init_tick(uint32_t period_ms)
{
    ESP_LOGI(TAG, "Налаштування таймера esp_timer для lv_tick_inc (період: %" PRIu32 " мс)...", period_ms);

    const esp_timer_create_args_t timer_args = {
        .callback = &lvgl_port_tick_callback,
        .arg = (void *)(uintptr_t)period_ms,
        .name = "lvgl_tick_timer"
    };

    esp_err_t err = esp_timer_create(&timer_args, &s_port_ctx.tick_timer);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка створення таймера LVGL tick: %s", esp_err_to_name(err));
        return err;
    }

    err = esp_timer_start_periodic(s_port_ctx.tick_timer, period_ms * 1000);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запуску таймера LVGL tick: %s", esp_err_to_name(err));
        return err;
    }

    return ESP_OK;
}

void lvgl_port_flush_callback(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p)
{
    frame_buffer_descriptor_t *fb = (frame_buffer_descriptor_t *)drv->user_data;
    if (fb == NULL) {
        lv_disp_flush_ready(drv);
        return;
    }

    uint32_t w = (area->x2 - area->x1 + 1);
    uint32_t h = (area->y2 - area->y1 + 1);

    /* Вибір цільового активного буфера в PSRAM */
    uint8_t *target_fb = (fb->active_index == 0) ? fb->buffer_1 : fb->buffer_2;

    /* Зміщення до області оновлення у цільовому буфері */
    size_t offset = ((size_t)area->y1 * fb->width + area->x1) * DISPLAY_COLOR_DEPTH_BYTES;
    void *dst_ptr = (void *)(target_fb + offset);

    /* Прискорене передавання блоку пікселів через периферійний модуль PPA */
    esp_err_t err = mipi_dsi_ppa_blit((const void *)color_p, dst_ptr, w, h, w, h);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Помилка блітингу PPA у flush_cb: %d", err);
    }

    /* Якщо оновлено весь кадр, виконуємо подвійне перемикання буферів та синхронізацію DSI */
    if (lv_disp_flush_is_last(drv)) {
        mipi_dsi_ppa_swap_and_display(fb);
    }

    /* Повідомляємо LVGL про завершення передачі порції даних */
    lv_disp_flush_ready(drv);
}

void lvgl_port_task(void *arg)
{
    ESP_LOGI(TAG, "Запуск фонової задачі обробника LVGL (lv_timer_handler)...");
    s_port_ctx.is_running = true;

    while (s_port_ctx.is_running) {
        uint32_t time_till_next = lv_timer_handler();
        if (time_till_next < 1) {
            time_till_next = 1;
        } else if (time_till_next > 10) {
            time_till_next = 10;
        }
        vTaskDelay(pdMS_TO_TICKS(time_till_next));
    }

    vTaskDelete(NULL);
}

esp_err_t lvgl_port_init(const lvgl_port_config_t *cfg, lvgl_port_handle_t *handle)
{
    if (cfg == NULL || cfg->fb_descriptor == NULL || handle == NULL) {
        ESP_LOGE(TAG, "Недійсні параметри конфігурації LVGL порту");
        return ESP_ERR_INVALID_ARG;
    }

    ESP_LOGI(TAG, "Ініціалізація ядра LVGL...");
    lv_init();

    s_port_ctx.fb_desc = cfg->fb_descriptor;

    /* Налаштування подвійного буфера вимальовування в PSRAM */
    lv_disp_draw_buf_init(&s_port_ctx.disp_buf,
                          cfg->fb_descriptor->buffer_1,
                          cfg->fb_descriptor->buffer_2,
                          cfg->fb_descriptor->width * cfg->fb_descriptor->height);

    /* Налаштування дисплейного драйвера LVGL */
    lv_disp_drv_init(&s_port_ctx.disp_drv);
    s_port_ctx.disp_drv.hor_res = cfg->hor_res;
    s_port_ctx.disp_drv.ver_res = cfg->ver_res;
    s_port_ctx.disp_drv.flush_cb = lvgl_port_flush_callback;
    s_port_ctx.disp_drv.draw_buf = &s_port_ctx.disp_buf;
    s_port_ctx.disp_drv.user_data = cfg->fb_descriptor;
    s_port_ctx.disp_drv.full_refresh = 1; /* Оновлення повними кадрами для запобігання розривам */

    s_port_ctx.disp_handle = lv_disp_drv_register(&s_port_ctx.disp_drv);
    if (s_port_ctx.disp_handle == NULL) {
        ESP_LOGE(TAG, "Не вдалося зареєструвати дисплейний драйвер LVGL!");
        return ESP_FAIL;
    }

    /* Запуск таймера генерації системних тиків */
    esp_err_t err = lvgl_port_init_tick(cfg->tick_period_ms);
    if (err != ESP_OK) {
        return err;
    }

    *handle = &s_port_ctx;
    ESP_LOGI(TAG, "Порт LVGL успішно ініціалізовано.");
    return ESP_OK;
}

esp_err_t lvgl_port_deinit(lvgl_port_handle_t handle)
{
    if (handle == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ESP_LOGI(TAG, "Деініціалізація порту LVGL...");
    s_port_ctx.is_running = false;

    if (s_port_ctx.tick_timer != NULL) {
        esp_timer_stop(s_port_ctx.tick_timer);
        esp_timer_delete(s_port_ctx.tick_timer);
        s_port_ctx.tick_timer = NULL;
    }

    return ESP_OK;
}
