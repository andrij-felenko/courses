#include "lvgl.h"

static void on_arm_confirmed(void *user_data) {
    LV_UNUSED(user_data);
    /* Виклик протоколу MAVLink / команди на борт */
}

static void on_mode_toggle(lv_event_t *e) {
    if (lv_event_get_code(e) == LV_EVENT_CLICKED) {
        /* Перемикання польотного режиму */
    }
}

void build_field_ui_screen(lv_display_t *disp) {
    field_theme_init(disp, FIELD_MODE_DAY_HIGH_CONTRAST);
    field_input_init();

    lv_obj_t *scr = lv_screen_active();
    lv_obj_set_flex_flow(scr, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(scr, LV_FLEX_ALIGN_SPACE_BETWEEN, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

    /* 1. Верхня зона (Hard-to-Reach): статичні показники */
    lv_obj_t *top_bar = lv_obj_create(scr);
    lv_obj_set_size(top_bar, LV_PCT(100), 40);
    lv_obj_set_style_bg_color(top_bar, lv_color_hex(0x000000), 0);
    lv_obj_set_style_border_width(top_bar, 0, 0);

    lv_obj_t *telemetry_lbl = lv_label_create(top_bar);
    lv_label_set_text(telemetry_lbl, "BAT: 24.8V | GPS: 18 FIX | ALT: 120m | RSSI: -68dBm");
    lv_obj_center(telemetry_lbl);

    /* 2. Середня зона (Stretch Zone): карта / журнал */
    lv_obj_t *mid_panel = lv_obj_create(scr);
    lv_obj_set_size(mid_panel, LV_PCT(100), 260);

    /* 3. Нижня зона великого пальця (Natural Thumb Zone): кнопки 17 мм із зазором 25 px */
    lv_obj_t *bottom_bar = lv_obj_create(scr);
    lv_obj_set_size(bottom_bar, LV_PCT(100), 140);
    lv_obj_set_flex_flow(bottom_bar, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(bottom_bar, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_set_style_pad_gap(bottom_bar, 25, 0);

    /* Звичайна тактильна кнопка зміни режиму */
    lv_obj_t *btn_mode = lv_btn_create(bottom_bar);
    lv_obj_set_size(btn_mode, 110, 110);
    lv_obj_t *lbl_mode = lv_label_create(btn_mode);
    lv_label_set_text(lbl_mode, "MODE\nAUTO");
    lv_obj_center(lbl_mode);
    lv_obj_add_event_cb(btn_mode, on_mode_toggle, LV_EVENT_CLICKED, NULL);
    field_input_add_widget(btn_mode);

    /* Критична кнопка активації з утриманням 1.5 с */
    tactical_hold_btn_t *arm_btn = tactical_hold_btn_create(bottom_bar, "ARM\nHOLD 1.5s", 1500, on_arm_confirmed, NULL);
    field_input_add_widget(arm_btn->btn);
}
