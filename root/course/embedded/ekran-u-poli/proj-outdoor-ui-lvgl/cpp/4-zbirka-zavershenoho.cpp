#include "lvgl.h"
#include <memory>
#include <vector>

namespace field_ui {

class FieldDashboard {
public:
    explicit FieldDashboard(lv_display_t* disp) {
        FieldTheme::instance().setup(disp, ColorMode::DayHighContrast);

        auto* scr = lv_screen_active();
        lv_obj_set_flex_flow(scr, LV_FLEX_FLOW_COLUMN);
        lv_obj_set_flex_align(scr, LV_FLEX_ALIGN_SPACE_BETWEEN, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);

        // 1. Верхня статична зона
        top_bar_ = lv_obj_create(scr);
        lv_obj_set_size(top_bar_, LV_PCT(100), 40);
        lv_obj_set_style_bg_color(top_bar_, lv_color_hex(0x000000), 0);
        lv_obj_set_style_border_width(top_bar_, 0, 0);

        telemetry_label_ = lv_label_create(top_bar_);
        lv_label_set_text(telemetry_label_, "BAT: 24.8V | GPS: 18 FIX | ALT: 120m | RSSI: -68dBm");
        lv_obj_center(telemetry_label_);

        // 2. Середня зона
        middle_view_ = lv_obj_create(scr);
        lv_obj_set_size(middle_view_, LV_PCT(100), 260);

        // 3. Нижня зона великого пальця
        bottom_bar_ = lv_obj_create(scr);
        lv_obj_set_size(bottom_bar_, LV_PCT(100), 140);
        lv_obj_set_flex_flow(bottom_bar_, LV_FLEX_FLOW_ROW);
        lv_obj_set_flex_align(bottom_bar_, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
        lv_obj_set_style_pad_gap(bottom_bar_, 25, 0);

        // Кнопка режиму
        mode_btn_ = lv_btn_create(bottom_bar_);
        lv_obj_set_size(mode_btn_, 110, 110);
        auto* mode_lbl = lv_label_create(mode_btn_);
        lv_label_set_text(mode_lbl, "MODE\nAUTO");
        lv_obj_center(mode_lbl);
        HardwareEncoderDriver::instance().registerWidget(mode_btn_);

        // Кнопка Arm з утриманням 1.5 с
        arm_button_ = std::make_unique<TacticalHoldButton>(
            bottom_bar_,
            "ARM\nHOLD 1.5s",
            1500,
            [this]() { onArmTriggered(); }
        );
        HardwareEncoderDriver::instance().registerWidget(arm_button_->handle());
    }

private:
    void onArmTriggered() {
        // Відправка критичної команди на виконавчий механізм
    }

    lv_obj_t* top_bar_{nullptr};
    lv_obj_t* telemetry_label_{nullptr};
    lv_obj_t* middle_view_{nullptr};
    lv_obj_t* bottom_bar_{nullptr};
    lv_obj_t* mode_btn_{nullptr};
    std::unique_ptr<TacticalHoldButton> arm_button_;
};

} // namespace field_ui
