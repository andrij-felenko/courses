#include "lvgl.h"

/* Палітра денного висококонтрастного режиму */
#define FIELD_COLOR_BG       lv_color_hex(0x000000) // Глибокий чорний фон
#define FIELD_COLOR_FG       lv_color_hex(0xFFFFFF) // Чистий білий текст
#define FIELD_COLOR_ACCENT   lv_color_hex(0xFFD700) // Сигнальний золотаво-жовтий
#define FIELD_COLOR_ALERT    lv_color_hex(0xFF0000) // Насичений червоний тривоги
#define FIELD_COLOR_SAFE     lv_color_hex(0x00FF00) // Яскраво-зелений зв'язку

/* Метрики польових віджетів (розрахунок під екран 160 DPI: 1 мм ≈ 6.3 px) */
#define FIELD_TARGET_MIN_W   95  // ~15 мм мінімальна ширина кнопки
#define FIELD_TARGET_MIN_H   95  // ~15 мм мінімальна висота кнопки
#define FIELD_PAD_GAP        25  // ~4 мм захисний зазор між кнопками

static lv_style_t style_field_btn;
static lv_style_t style_field_btn_focused;
static lv_style_t style_field_btn_pressed;

void field_theme_init(void) {
    /* Базовий стиль тактильної польової кнопки */
    lv_style_init(&style_field_btn);
    lv_style_set_min_width(&style_field_btn, FIELD_TARGET_MIN_W);
    lv_style_set_min_height(&style_field_btn, FIELD_TARGET_MIN_H);
    lv_style_set_bg_color(&style_field_btn, lv_color_hex(0x1A1A1A));
    lv_style_set_bg_opa(&style_field_btn, LV_OPA_COVER);
    lv_style_set_border_color(&style_field_btn, FIELD_COLOR_FG);
    lv_style_set_border_width(&style_field_btn, 3);
    lv_style_set_radius(&style_field_btn, 8);
    lv_style_set_text_color(&style_field_btn, FIELD_COLOR_FG);
    lv_style_set_pad_all(&style_field_btn, 12);

    /* Стиль фокусу від фізичного енкодера / D-Pad */
    lv_style_init(&style_field_btn_focused);
    lv_style_set_border_color(&style_field_btn_focused, FIELD_COLOR_ACCENT);
    lv_style_set_border_width(&style_field_btn_focused, 5);

    /* Стиль натиснутого стану */
    lv_style_init(&style_field_btn_pressed);
    lv_style_set_bg_color(&style_field_btn_pressed, FIELD_COLOR_ACCENT);
    lv_style_set_text_color(&style_field_btn_pressed, FIELD_COLOR_BG);
}

void apply_field_btn_style(lv_obj_t *btn) {
    lv_obj_add_style(btn, &style_field_btn, LV_STATE_DEFAULT);
    lv_obj_add_style(btn, &style_field_btn_focused, LV_STATE_FOCUSED);
    lv_obj_add_style(btn, &style_field_btn_pressed, LV_STATE_PRESSED);
}
