#include "lvgl.h"
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    lv_obj_t *btn;
    lv_obj_t *arc;
    lv_obj_t *label;
    lv_timer_t *timer;
    uint32_t hold_time_ms;
    uint32_t elapsed_ms;
    void (*on_confirm)(void *user_data);
    void *user_data;
} tactical_hold_btn_t;

static void hold_timer_cb(lv_timer_t *t) {
    tactical_hold_btn_t *hb = (tactical_hold_btn_t *)lv_timer_get_user_data(t);
    hb->elapsed_ms += 30;

    int32_t progress = (int32_t)((hb->elapsed_ms * 100) / hb->hold_time_ms);
    if (progress > 100) progress = 100;
    lv_arc_set_value(hb->arc, progress);

    if (hb->elapsed_ms >= hb->hold_time_ms) {
        lv_timer_pause(t);
        hb->elapsed_ms = 0;
        lv_arc_set_value(hb->arc, 0);
        if (hb->on_confirm) {
            hb->on_confirm(hb->user_data);
        }
    }
}

static void hold_event_cb(lv_event_t *e) {
    tactical_hold_btn_t *hb = (tactical_hold_btn_t *)lv_event_get_user_data(e);
    lv_event_code_t code = lv_event_get_code(e);

    if (code == LV_EVENT_PRESSED) {
        hb->elapsed_ms = 0;
        lv_arc_set_value(hb->arc, 0);
        lv_timer_resume(hb->timer);
    } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
        lv_timer_pause(hb->timer);
        hb->elapsed_ms = 0;
        lv_arc_set_value(hb->arc, 0);
    }
}

tactical_hold_btn_t* tactical_hold_btn_create(lv_obj_t *parent, const char *text, 
                                             uint32_t hold_ms, 
                                             void (*confirm_cb)(void *), void *user_data) {
    tactical_hold_btn_t *hb = (tactical_hold_btn_t *)lv_malloc(sizeof(tactical_hold_btn_t));
    if (!hb) return NULL;

    hb->hold_time_ms = hold_ms;
    hb->elapsed_ms   = 0;
    hb->on_confirm   = confirm_cb;
    hb->user_data    = user_data;

    hb->btn = lv_btn_create(parent);
    lv_obj_set_size(hb->btn, 110, 110);

    hb->label = lv_label_create(hb->btn);
    lv_label_set_text(hb->label, text);
    lv_obj_center(hb->label);

    hb->arc = lv_arc_create(hb->btn);
    lv_obj_set_size(hb->arc, 100, 100);
    lv_arc_set_rotation(hb->arc, 270);
    lv_arc_set_bg_angles(hb->arc, 0, 360);
    lv_arc_set_angles(hb->arc, 0, 0);
    lv_arc_set_range(hb->arc, 0, 100);
    lv_obj_set_style_arc_width(hb->arc, 5, LV_PART_INDICATOR);
    lv_obj_remove_style(hb->arc, NULL, LV_PART_KNOB);
    lv_obj_clear_flag(hb->arc, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_center(hb->arc);

    hb->timer = lv_timer_create(hold_timer_cb, 30, hb);
    lv_timer_pause(hb->timer);

    lv_obj_add_event_cb(hb->btn, hold_event_cb, LV_EVENT_ALL, hb);
    return hb;
}
