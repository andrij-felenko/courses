typedef struct {
    lv_obj_t *btn;
    lv_obj_t *arc;
    lv_timer_t *timer;
    uint32_t hold_time_ms;
    uint32_t elapsed_ms;
    void (*on_confirm)(void *user_data);
    void *user_data;
} tactical_hold_btn_t;

static void hold_timer_cb(lv_timer_t *timer) {
    tactical_hold_btn_t *hbtn = (tactical_hold_btn_t *)lv_timer_get_user_data(timer);
    hbtn->elapsed_ms += 50;

    int32_t progress = (hbtn->elapsed_ms * 100) / hbtn->hold_time_ms;
    if (progress > 100) progress = 100;
    lv_arc_set_value(hbtn->arc, progress);

    if (hbtn->elapsed_ms >= hbtn->hold_time_ms) {
        lv_timer_pause(timer);
        hbtn->elapsed_ms = 0;
        lv_arc_set_value(hbtn->arc, 0);
        if (hbtn->on_confirm) {
            hbtn->on_confirm(hbtn->user_data);
        }
    }
}

static void hold_btn_event_cb(lv_event_t *e) {
    tactical_hold_btn_t *hbtn = (tactical_hold_btn_t *)lv_event_get_user_data(e);
    lv_event_code_t code = lv_event_get_code(e);

    if (code == LV_EVENT_PRESSED) {
        hbtn->elapsed_ms = 0;
        lv_arc_set_value(hbtn->arc, 0);
        lv_timer_resume(hbtn->timer);
    } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
        lv_timer_pause(hbtn->timer);
        hbtn->elapsed_ms = 0;
        lv_arc_set_value(hbtn->arc, 0);
    }
}
