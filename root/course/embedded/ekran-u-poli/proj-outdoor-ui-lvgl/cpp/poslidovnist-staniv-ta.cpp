#include "lvgl.h"
#include <functional>
#include <memory>
#include <string_view>

namespace field_ui {

class TacticalHoldButton {
public:
    using Callback = std::function<void()>;

    TacticalHoldButton(lv_obj_t* parent, std::string_view label, uint32_t hold_time_ms, Callback cb)
        : hold_time_ms_(hold_time_ms), callback_(std::move(cb)) {

        btn_ = lv_btn_create(parent);
        lv_obj_set_size(btn_, 110, 110);

        label_ = lv_label_create(btn_);
        lv_label_set_text(label_, label.data());
        lv_obj_center(label_);

        arc_ = lv_arc_create(btn_);
        lv_obj_set_size(arc_, 100, 100);
        lv_arc_set_rotation(arc_, 270);
        lv_arc_set_bg_angles(arc_, 0, 360);
        lv_arc_set_angles(arc_, 0, 0);
        lv_arc_set_range(arc_, 0, 100);
        lv_obj_set_style_arc_width(arc_, 5, LV_PART_INDICATOR);
        lv_obj_remove_style(arc_, nullptr, LV_PART_KNOB);
        lv_obj_clear_flag(arc_, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_center(arc_);

        timer_ = lv_timer_create(&TacticalHoldButton::onTimerThunk, 30, this);
        lv_timer_pause(timer_);

        lv_obj_add_event_cb(btn_, &TacticalHoldButton::onEventThunk, LV_EVENT_ALL, this);
    }

    ~TacticalHoldButton() {
        if (timer_) {
            lv_timer_delete(timer_);
            timer_ = nullptr;
        }
    }

    TacticalHoldButton(const TacticalHoldButton&) = delete;
    TacticalHoldButton& operator=(const TacticalHoldButton&) = delete;

    [[nodiscard]] lv_obj_t* handle() const noexcept { return btn_; }

private:
    static void onTimerThunk(lv_timer_t* t) {
        auto* self = static_cast<TacticalHoldButton*>(lv_timer_get_user_data(t));
        self->handleTick();
    }

    static void onEventThunk(lv_event_t* e) {
        auto* self = static_cast<TacticalHoldButton*>(lv_event_get_user_data(e));
        self->handleEvent(lv_event_get_code(e));
    }

    void handleTick() {
        elapsed_ms_ += 30;
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

    void handleEvent(lv_event_code_t code) {
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
    Callback callback_;
    lv_obj_t* btn_{nullptr};
    lv_obj_t* label_{nullptr};
    lv_obj_t* arc_{nullptr};
    lv_timer_t* timer_{nullptr};
};

} // namespace field_ui
