#include <stdio.h>
#include "lvgl.h"

// Дескриптори віджетів дашборду
static lv_obj_t *s_arc_temp;
static lv_obj_t *s_arc_hum;
static lv_obj_t *s_lbl_temp_val;
static lv_obj_t *s_lbl_hum_val;
static lv_obj_t *s_lbl_batt;
static lv_obj_t *s_chart_press;
static lv_chart_series_t *s_ser_press;

// Колірна палітра інтерфейсу (темна тема для контрасту на IPS)
#define COLOR_BG            lv_color_hex(0x0e1117) // Глибокий чорно-синій фон
#define COLOR_PANEL         lv_color_hex(0x161b22) // Тло графіка
#define COLOR_COLD          lv_color_hex(0x38bdf8) // Холод (< 18 °C)
#define COLOR_COMFORT       lv_color_hex(0x22c55e) // Комфорт (18..24.5 °C)
#define COLOR_WARNING       lv_color_hex(0xf59e0b) // Увага (24.6..28 °C)
#define COLOR_DANGER        lv_color_hex(0xef4444) // Небезпека (> 28 °C)
#define COLOR_HUMIDITY      lv_color_hex(0x06b6d4) // Циановий для вологості
#define COLOR_TEXT_MUTED    lv_color_hex(0x8b949e) // Сірий для службових написів

// Вибір кольору дуги температури відповідно до зон комфорту
static lv_color_t get_temp_comfort_color(int16_t temp_x10) {
    if (temp_x10 < 180) {
        return COLOR_COLD;
    } else if (temp_x10 <= 245) {
        return COLOR_COMFORT;
    } else if (temp_x10 <= 280) {
        return COLOR_WARNING;
    } else {
        return COLOR_DANGER;
    }
}

// Ініціалізація та просторове компонування дашборду на екрані 240x240
void dashboard_create(void) {
    lv_obj_t *scr = lv_scr_act();
    lv_obj_set_style_bg_color(scr, COLOR_BG, 0);
    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);
    lv_obj_clear_flag(scr, LV_OBJ_FLAG_SCROLLABLE);

    // -------------------------------------------------------------------------
    // 1. Верхній рядок стану (Status Bar, y: 0..24)
    // -------------------------------------------------------------------------
    lv_obj_t *status_bar = lv_obj_create(scr);
    lv_obj_set_pos(status_bar, 0, 0);
    lv_obj_set_size(status_bar, 240, 24);
    lv_obj_set_style_bg_opa(status_bar, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(status_bar, 0, 0);
    lv_obj_set_style_pad_all(status_bar, 4, 0);
    lv_obj_clear_flag(status_bar, LV_OBJ_FLAG_SCROLLABLE);

    // Ідентифікатор приладу
    lv_obj_t *lbl_title = lv_label_create(status_bar);
    lv_label_set_text(lbl_title, LV_SYMBOL_SETTINGS " КЛІМАТ");
    lv_obj_set_style_text_color(lbl_title, COLOR_TEXT_MUTED, 0);
    lv_obj_set_style_text_font(lbl_title, &lv_font_montserrat_10, 0);
    lv_obj_align(lbl_title, LV_ALIGN_LEFT_MID, 4, 0);

    // Індикатор заряду акумулятора
    s_lbl_batt = lv_label_create(status_bar);
    lv_label_set_text(s_lbl_batt, "100% " LV_SYMBOL_BATTERY_FULL);
    lv_obj_set_style_text_color(s_lbl_batt, COLOR_COMFORT, 0);
    lv_obj_set_style_text_font(s_lbl_batt, &lv_font_montserrat_10, 0);
    lv_obj_align(s_lbl_batt, LV_ALIGN_RIGHT_MID, -4, 0);

    // -------------------------------------------------------------------------
    // 2. Центрально-радіальний сектор дугових шкал (y: 26..154)
    // -------------------------------------------------------------------------
    // Зовнішня дуга: Температура (-10.0 .. +50.0 °C, кут 240 градусів)
    s_arc_temp = lv_arc_create(scr);
    lv_obj_set_size(s_arc_temp, 136, 136);
    lv_obj_align(s_arc_temp, LV_ALIGN_TOP_MID, 0, 24);
    lv_arc_set_rotation(s_arc_temp, 150);
    lv_arc_set_bg_angles(s_arc_temp, 0, 240);
    lv_arc_set_range(s_arc_temp, -100, 500); // Дискретність 0.1 °C
    lv_arc_set_value(s_arc_temp, 225);

    // Налаштування стилів шкали: товщина 8 пікселів, скруглені краї
    lv_obj_set_style_arc_width(s_arc_temp, 8, LV_PART_MAIN);
    lv_obj_set_style_arc_color(s_arc_temp, lv_color_hex(0x21262d), LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_arc_temp, 8, LV_PART_INDICATOR);
    lv_obj_set_style_arc_color(s_arc_temp, COLOR_COMFORT, LV_PART_INDICATOR);
    lv_obj_set_style_arc_rounded(s_arc_temp, true, LV_PART_INDICATOR);
    lv_obj_remove_style(s_arc_temp, NULL, LV_PART_KNOB); // Прибираємо ручку
    lv_obj_clear_flag(s_arc_temp, LV_OBJ_FLAG_CLICKABLE);

    // Внутрішня дуга: Відносна вологість (0 .. 100%)
    s_arc_hum = lv_arc_create(scr);
    lv_obj_set_size(s_arc_hum, 112, 112);
    lv_obj_align(s_arc_hum, LV_ALIGN_TOP_MID, 0, 36);
    lv_arc_set_rotation(s_arc_hum, 150);
    lv_arc_set_bg_angles(s_arc_hum, 0, 240);
    lv_arc_set_range(s_arc_hum, 0, 100);
    lv_arc_set_value(s_arc_hum, 50);

    lv_obj_set_style_arc_width(s_arc_hum, 5, LV_PART_MAIN);
    lv_obj_set_style_arc_color(s_arc_hum, lv_color_hex(0x1a212d), LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_arc_hum, 5, LV_PART_INDICATOR);
    lv_obj_set_style_arc_color(s_arc_hum, COLOR_HUMIDITY, LV_PART_INDICATOR);
    lv_obj_set_style_arc_rounded(s_arc_hum, true, LV_PART_INDICATOR);
    lv_obj_remove_style(s_arc_hum, NULL, LV_PART_KNOB);
    lv_obj_clear_flag(s_arc_hum, LV_OBJ_FLAG_CLICKABLE);

    // Великий цифровий індикатор температури по центру
    s_lbl_temp_val = lv_label_create(scr);
    lv_obj_set_style_text_font(s_lbl_temp_val, &lv_font_montserrat_22, 0);
    lv_obj_set_style_text_color(s_lbl_temp_val, lv_color_white(), 0);
    lv_label_set_text(s_lbl_temp_val, "22.5°C");
    lv_obj_align(s_lbl_temp_val, LV_ALIGN_TOP_MID, 0, 64);

    // Менший числовий індикатор вологості під температурою
    s_lbl_hum_val = lv_label_create(scr);
    lv_obj_set_style_text_font(s_lbl_hum_val, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_color(s_lbl_hum_val, COLOR_HUMIDITY, 0);
    lv_label_set_text(s_lbl_hum_val, "50% RH");
    lv_obj_align(s_lbl_hum_val, LV_ALIGN_TOP_MID, 0, 92);

    // -------------------------------------------------------------------------
    // 3. Нижній сектор: Спарклайн атмосферного тиску (y: 156..236)
    // -------------------------------------------------------------------------
    s_chart_press = lv_chart_create(scr);
    lv_obj_set_pos(s_chart_press, 10, 156);
    lv_obj_set_size(s_chart_press, 220, 76);
    lv_obj_set_style_bg_color(s_chart_press, COLOR_PANEL, 0);
    lv_obj_set_style_bg_opa(s_chart_press, LV_OPA_COVER, 0);
    lv_obj_set_style_border_color(s_chart_press, lv_color_hex(0x30363d), 0);
    lv_obj_set_style_border_width(s_chart_press, 1, 0);
    lv_obj_set_style_radius(s_chart_press, 6, 0);
    lv_obj_set_style_pad_all(s_chart_press, 4, 0);

    lv_chart_set_type(s_chart_press, LV_CHART_TYPE_LINE);
    lv_chart_set_point_count(s_chart_press, 20); // 20 послідовних вимірювань
    lv_chart_set_range(s_chart_press, LV_CHART_AXIS_PRIMARY_Y, 730, 770); // мм рт. ст.
    lv_chart_set_update_mode(s_chart_press, LV_CHART_UPDATE_MODE_SHIFT);

    // Прибираємо масивну координатну сітку
    lv_obj_set_style_line_width(s_chart_press, 1, LV_PART_MAIN);
    lv_obj_set_style_line_color(s_chart_press, lv_color_hex(0x21262d), LV_PART_MAIN);

    // Серія даних тиску
    s_ser_press = lv_chart_add_series(s_chart_press, lv_color_hex(0xa855f7),
                                      LV_CHART_AXIS_PRIMARY_Y);
    lv_obj_set_style_size(s_chart_press, 0, LV_PART_INDICATOR); // Ховаємо точки з'єднання
    lv_obj_set_style_line_width(s_chart_press, 2, LV_PART_ITEMS);

    for (int i = 0; i < 20; i++) {
        lv_chart_set_next_value(s_chart_press, s_ser_press, 750);
    }
}

// Оновлення стану віджетів під час отримання нових даних сенсорів
void dashboard_update_data(float temp_c, float hum_pct, float press_mmhg, uint8_t batt_pct) {
    char buf[24];

    // 1. Оновлення цифрових показників температури та вологості
    snprintf(buf, sizeof(buf), "%.1f°C", temp_c);
    lv_label_set_text(s_lbl_temp_val, buf);

    snprintf(buf, sizeof(buf), "%.0f%% RH", hum_pct);
    lv_label_set_text(s_lbl_hum_val, buf);

    // 2. Оновлення дуги температури та її динамічного кольору
    int16_t temp_x10 = (int16_t)(temp_c * 10.0f);
    lv_arc_set_value(s_arc_temp, temp_x10);
    lv_color_t color = get_temp_comfort_color(temp_x10);
    lv_obj_set_style_arc_color(s_arc_temp, color, LV_PART_INDICATOR);

    // 3. Оновлення внутрішньої дуги вологості
    lv_arc_set_value(s_arc_hum, (int16_t)hum_pct);

    // 4. Додавання нової точки тиску до спарклайну
    lv_chart_set_next_value(s_chart_press, s_ser_press, (lv_coord_t)press_mmhg);

    // 5. Оновлення статусу та іконки заряду батареї
    const char *icon = (batt_pct > 80) ? LV_SYMBOL_BATTERY_FULL :
                       (batt_pct > 40) ? LV_SYMBOL_BATTERY_3 :
                       (batt_pct > 15) ? LV_SYMBOL_BATTERY_1 : LV_SYMBOL_BATTERY_EMPTY;
    snprintf(buf, sizeof(buf), "%d%% %s", batt_pct, icon);
    lv_label_set_text(s_lbl_batt, buf);
    lv_obj_set_style_text_color(s_lbl_batt, (batt_pct <= 15) ? COLOR_DANGER : COLOR_COMFORT, 0);
}
