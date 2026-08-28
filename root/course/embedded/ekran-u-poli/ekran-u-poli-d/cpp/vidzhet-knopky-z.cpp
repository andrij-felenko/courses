#include "lvgl.h"
#include <functional>
#include <memory>

namespace field_ui {

class TacticalHoldButton {
public:
    using ConfirmCallback = std::function<void()>;

    TacticalHoldButton(lv_obj_t* parent, const char* label, uint32_t hold_time_ms, ConfirmCallback cb)
        : hold_time_ms_(hold_time_ms), callback_(std::move(cb)) {
        
        btn_ = lv_btn_create(parent);
        ThemeEngine::instance().styleButton(btn_);

        label_ = lv_label_create(btn_);
        lv_label_set_text(label_, label);
        lv_obj_center(label_);

        // Круговий індикатор заповнення по контуру кнопки
        arc_ = lv_arc_create(btn_);
        lv_obj_set_size(arc_, Metrics::MinTargetWidth - 10, Metrics::MinTargetHeight - 10);
        lv_arc_set_rotation(arc_, 270);
        lv_arc_set_bg_angles(arc_, 0, 360);
        lv_arc_set_angles(arc_, 0, 0);
        lv_arc_set_range(arc_, 0, 100);
        lv_obj_set_style_arc_color(arc_, Palette::Accent, LV_PART_INDICATOR);
        lv_obj_set_style_arc_width(arc_, 4, LV_PART_INDICATOR);
        lv_obj_remove_style(arc_, nullptr, LV_PART_KNOB); // Прибираємо ручку
        lv_obj_clear_flag(arc_, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_center(arc_);

        timer_ = lv_timer_create(timerCallbackThunk, 50, this);
        lv_timer_pause(timer_);

        lv_obj_add_event_cb(btn_, eventCallbackThunk, LV_EVENT_ALL, this);
    }

    ~TacticalHoldButton() {
        if (timer_) {
            lv_timer_delete(timer_);
        }
    }

    TacticalHoldButton(const TacticalHoldButton&) = delete;
    TacticalHoldButton& operator=(const TacticalHoldButton&) = delete;

private:
    static void timerCallbackThunk(lv_timer_t* t) {
        auto* self = static_cast<TacticalHoldButton*>(lv_timer_get_user_data(t));
        self->onTick();
    }

    static void eventCallbackThunk(lv_event_t* e) {
        auto* self = static_cast<TacticalHoldButton*>(lv_event_get_user_data(e));
        self->onEvent(lv_event_get_code(e));
    }

    void onTick() {
        elapsed_ms_ += 50;
        int32_t progress = static_cast<int32_t>((elapsed_ms_ * 100) / hold_time_ms_);
        if (progress > 100) progress = 100;
        lv_arc_set_value(arc_, progress);

        if (elapsed_ms_ >= hold_time_ms_) {
            lv_timer_pause(timer_);
            elapsed_ms_ = 0;
            lv_arc_set_value(arc_, 0);
            if (callback_) {
                callback_();
            }
        }
    }

    void onEvent(lv_event_code_t code) {
        if (code == LV_EVENT_PRESSED) {
            elapsed_ms_ = 0;
            lv_arc_set_value(arc_, 0);
            lv_timer_resume(timer_);
        } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
            lv_timer_pause(timer_);
            elapsed_ms_ = 0;
            lv_arc_set_value(arc_, 0);
        }
    }

    uint32_t hold_time_ms_{1500};
    uint32_t elapsed_ms_{0};
    ConfirmCallback callback_;
    lv_obj_t* btn_{nullptr};
    lv_obj_t* label_{nullptr};
    lv_obj_t* arc_{nullptr};
    lv_timer_t* timer_{nullptr};
};

} // namespace field_ui
