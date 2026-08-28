#include "lvgl.h"
#include <stdbool.h>
#include <stdint.h>

/* Режими роботи польового інтерфейсу */
typedef enum {
    FIELD_MODE_DAY_HIGH_CONTRAST = 0,
    FIELD_MODE_NIGHT_RED
} field_color_mode_t;

typedef struct {
    lv_color_t bg;
    lv_color_t surface;
    lv_color_t text;
    lv_color_t border;
    lv_color_t accent;
    lv_color_t alert;
    lv_color_t safe;
} field_palette_t;

static const field_palette_t PALETTES[] = {
    [FIELD_MODE_DAY_HIGH_CONTRAST] = {
        .bg      = LV_COLOR_MAKE(0x00, 0x00, 0x00), // Чорний
        .surface = LV_COLOR_MAKE(0x1C, 0x1C, 0x1E), // Темно-сірий
        .text    = LV_COLOR_MAKE(0xFF, 0xFF, 0xFF), // Білий
        .border  = LV_COLOR_MAKE(0xFF, 0xFF, 0xFF), // Біла рамка
        .accent  = LV_COLOR_MAKE(0xFF, 0xD7, 0x00), // Золотаво-жовтий
        .alert   = LV_COLOR_MAKE(0xFF, 0x2D, 0x55), // Червоний
        .safe    = LV_COLOR_MAKE(0x34, 0xC7, 0x59)  // Зелений
    },
    [FIELD_MODE_NIGHT_RED] = {
        .bg      = LV_COLOR_MAKE(0x00, 0x00, 0x00), // Чорний
        .surface = LV_COLOR_MAKE(0x20, 0x00, 0x00), // Темно-червоний
        .text    = LV_COLOR_MAKE(0xFF, 0x3B, 0x30), // Насичений червоний
        .border  = LV_COLOR_MAKE(0x8B, 0x00, 0x00), // Бордовий
        .accent  = LV_COLOR_MAKE(0xFF, 0x45, 0x3A), // Світло-червоний
        .alert   = LV_COLOR_MAKE(0xFF, 0x00, 0x00), // Яскраво-червоний
        .safe    = LV_COLOR_MAKE(0x99, 0x1B, 0x1B)  // Приглушений червоний
    }
};

static field_color_mode_t current_mode = FIELD_MODE_DAY_HIGH_CONTRAST;
static lv_theme_t field_theme;
static lv_style_t style_btn_base;
static lv_style_t style_btn_focus;
static lv_style_t style_btn_press;
static lv_style_t style_scr;

static void field_theme_apply_cb(lv_theme_t *th, lv_obj_t *obj) {
    LV_UNUSED(th);
    if (lv_obj_check_type(obj, &lv_btn_class)) {
        lv_obj_add_style(obj, &style_btn_base, LV_STATE_DEFAULT);
        lv_obj_add_style(obj, &style_btn_focus, LV_STATE_FOCUSED);
        lv_obj_add_style(obj, &style_btn_press, LV_STATE_PRESSED);
    } else if (lv_obj_check_type(obj, &lv_screen_class) || lv_obj_get_parent(obj) == NULL) {
        lv_obj_add_style(obj, &style_scr, LV_STATE_DEFAULT);
    }
}

void field_theme_update_styles(field_color_mode_t mode) {
    current_mode = mode;
    const field_palette_t *p = &PALETTES[mode];

    /* Налаштування стилю головного екрана */
    lv_style_reset(&style_scr);
    lv_style_init(&style_scr);
    lv_style_set_bg_color(&style_scr, p->bg);
    lv_style_set_bg_opa(&style_scr, LV_OPA_COVER);

    /* Базовий стиль польової кнопки (15 мм) */
    lv_style_reset(&style_btn_base);
    lv_style_init(&style_btn_base);
    lv_style_set_min_width(&style_btn_base, 95);
    lv_style_set_min_height(&style_btn_base, 95);
    lv_style_set_bg_color(&style_btn_base, p->surface);
    lv_style_set_bg_opa(&style_btn_base, LV_OPA_COVER);
    lv_style_set_border_color(&style_btn_base, p->border);
    lv_style_set_border_width(&style_btn_base, 3);
    lv_style_set_radius(&style_btn_base, 8);
    lv_style_set_text_color(&style_btn_base, p->text);
    lv_style_set_pad_all(&style_btn_base, 14);

    /* Стиль фокусу енкодера / апаратних клавіш */
    lv_style_reset(&style_btn_focus);
    lv_style_init(&style_btn_focus);
    lv_style_set_border_color(&style_btn_focus, p->accent);
    lv_style_set_border_width(&style_btn_focus, 6);

    /* Стиль активного натискання */
    lv_style_reset(&style_btn_press);
    lv_style_init(&style_btn_press);
    lv_style_set_bg_color(&style_btn_press, p->accent);
    lv_style_set_text_color(&style_btn_press, p->bg);
}

void field_theme_init(lv_display_t *disp, field_color_mode_t initial_mode) {
    field_theme_update_styles(initial_mode);
    lv_theme_set_apply_cb(&field_theme, field_theme_apply_cb);
    lv_theme_set_display(&field_theme, disp);
    lv_display_set_theme(disp, &field_theme);
}
