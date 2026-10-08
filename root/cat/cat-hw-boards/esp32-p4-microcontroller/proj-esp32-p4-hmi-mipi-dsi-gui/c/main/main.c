#include <stdio.h>
#include <inttypes.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "mipi_dsi_ppa_driver.h"
#include "lvgl_port.h"
#include "lvgl.h"

static const char *TAG = "MAIN_APP";

/* Глобальний дескриптор подвійного буфера кадру в PSRAM */
static frame_buffer_descriptor_t s_display_fb_desc;
static lvgl_port_handle_t s_lvgl_handle = NULL;

/**
 * @brief Обробник події натискання інтерактивної кнопки LVGL
 */
static void btn_event_cb(lv_event_t *e)
{
    lv_event_code_t code = lv_event_get_code(e);
    lv_obj_t *btn = lv_event_get_target(e);

    if (code == LV_EVENT_CLICKED) {
        static uint32_t click_count = 0;
        click_count++;
        ESP_LOGI(TAG, "Кнопку натиснуто! Лічильник: %" PRIu32, click_count);

        lv_obj_t *label = lv_obj_get_child(btn, 0);
        if (label != NULL) {
            char buf[32];
            snprintf(buf, sizeof(buf), "Натиснуто: %" PRIu32, click_count);
            lv_label_set_text(label, buf);
        }
    }
}

/**
 * @brief Створення демонстраційного графічного інтерфейсу LVGL
 */
static void create_demo_ui(void)
{
    ESP_LOGI(TAG, "Створення віджетів користувацького інтерфейсу LVGL...");

    /* Активний екран */
    lv_obj_t *scr = lv_scr_act();
    lv_obj_set_style_bg_color(scr, lv_palette_main(LV_PALETTE_GREY), LV_PART_MAIN);

    /* Заголовок проекту */
    lv_obj_t *title_label = lv_label_create(scr);
    lv_label_set_text(title_label, "ESP32-P4: MIPI-DSI + PPA + LVGL");
    lv_obj_align(title_label, LV_ALIGN_TOP_MID, 0, 30);
    lv_obj_set_style_text_font(title_label, &lv_font_montserrat_14, 0);

    /* Інформаційна картка */
    lv_obj_t *card = lv_obj_create(scr);
    lv_obj_set_size(card, 400, 200);
    lv_obj_align(card, LV_ALIGN_CENTER, 0, -20);
    lv_obj_set_style_radius(card, 12, 0);

    lv_obj_t *info_label = lv_label_create(card);
    lv_label_set_text(info_label,
        "Прискорення PPA: Активне\n"
        "Інтерфейс: MIPI-DSI DPHY\n"
        "Буферизація: Double PSRAM\n"
        "Запобігання Tearing: Включено");
    lv_obj_align(info_label, LV_ALIGN_CENTER, 0, 0);

    /* Інтерактивна кнопка */
    lv_obj_t *btn = lv_btn_create(scr);
    lv_obj_set_size(btn, 200, 50);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -40);
    lv_obj_add_event_cb(btn, btn_event_cb, LV_EVENT_CLICKED, NULL);

    lv_obj_t *btn_label = lv_label_create(btn);
    lv_label_set_text(btn_label, "Натисни мене");
    lv_obj_center(btn_label);
}

void app_main(void)
{
    ESP_LOGI(TAG, "=== Старт програми графічної підсистеми ESP32-P4 ===");

    /* Перевірка доступності зовнішньої оперативної пам'яті PSRAM */
    size_t psram_size = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "Доступний обсяг зовнішньої пам'яті PSRAM: %zu байт (%.2f МБ)",
             psram_size, (double)psram_size / (1024 * 1024));

    if (psram_size < (DISPLAY_HORIZONTAL_RESOLUTION * DISPLAY_VERTICAL_RESOLUTION * DISPLAY_COLOR_DEPTH_BYTES * 2)) {
        ESP_LOGE(TAG, "Критична помилка: Недостатньо пам'яті PSRAM для подвійного фреймбуфера!");
        return;
    }

    /* 1. Виділення двох кадрових буферів у PSRAM з 64-байтним кеш-вирівнюванням */
    esp_err_t err = mipi_dsi_ppa_init_psram_buffers(&s_display_fb_desc,
                                                     DISPLAY_HORIZONTAL_RESOLUTION,
                                                     DISPLAY_VERTICAL_RESOLUTION,
                                                     DISPLAY_COLOR_DEPTH_BYTES);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати буфери у PSRAM");
        return;
    }

    /* 2. Конфігурація та ініціалізація шини MIPI-DSI */
    mipi_dsi_timing_config_t dsi_timing = {
        .clock_lane_freq_mhz = 500,
        .num_data_lanes = 2,
        .hsync_pulse_width = 40,
        .hsync_back_porch = 40,
        .hsync_front_porch = 48,
        .vsync_pulse_width = 4,
        .vsync_back_porch = 8,
        .vsync_front_porch = 12,
    };
    err = mipi_dsi_ppa_init_dsi(&dsi_timing);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати шину MIPI-DSI");
        return;
    }

    /* 3. Конфігурація апаратного прискорювача пікселів PPA */
    ppa_config_t ppa_cfg = {
        .input_color_mode = PPA_COLOR_MODE_RGB565,
        .output_color_mode = PPA_COLOR_MODE_RGB565,
        .enable_scaling = true,
        .enable_blending = false,
        .scale_factor_x = 1.0f,
        .scale_factor_y = 1.0f
    };
    err = mipi_dsi_ppa_init_ppa(&ppa_cfg);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати прискорювач PPA");
        return;
    }

    /* 4. Налаштування порту LVGL */
    lvgl_port_config_t lvgl_cfg = {
        .fb_descriptor = &s_display_fb_desc,
        .hor_res = DISPLAY_HORIZONTAL_RESOLUTION,
        .ver_res = DISPLAY_VERTICAL_RESOLUTION,
        .tick_period_ms = 2,
        .task_priority = 5,
        .task_stack_size = 4096
    };
    err = lvgl_port_init(&lvgl_cfg, &s_lvgl_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати порт LVGL");
        return;
    }

    /* 5. Побудова демонстраційного UI */
    create_demo_ui();

    /* 6. Запуск фонової задачі FreeRTOS для постійної обробки графіки LVGL */
    xTaskCreatePinnedToCore(lvgl_port_task,
                           "lvgl_gui_task",
                           lvgl_cfg.task_stack_size,
                           NULL,
                           lvgl_cfg.task_priority,
                           NULL,
                           1);

    ESP_LOGI(TAG, "Графічну підсистему ESP32-P4 успішно запущено.");
}
