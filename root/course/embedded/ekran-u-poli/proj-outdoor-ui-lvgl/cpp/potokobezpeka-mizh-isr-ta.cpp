#include "lvgl.h"
#include <span>
#include <cstdint>

namespace field_ui {

class HardwareEncoderDriver {
public:
    using DiffReader = int16_t(*)();
    using ButtonReader = bool(*)();

    static HardwareEncoderDriver& instance() {
        static HardwareEncoderDriver driver;
        return driver;
    }

    void initialize(DiffReader diff_fn, ButtonReader btn_fn) {
        diff_reader_ = diff_fn;
        btn_reader_  = btn_fn;

        group_ = lv_group_create();
        lv_group_set_default(group_);

        indev_ = lv_indev_create();
        lv_indev_set_type(indev_, LV_INDEV_TYPE_ENCODER);
        lv_indev_set_read_cb(indev_, &HardwareEncoderDriver::readCallbackThunk);
        lv_indev_set_group(indev_, group_);
        lv_indev_set_user_data(indev_, this);
    }

    void registerWidget(lv_obj_t* obj) {
        if (group_ && obj) {
            lv_group_add_obj(group_, obj);
        }
    }

    void registerWidgets(std::span<lv_obj_t*> widgets) {
        for (auto* obj : widgets) {
            registerWidget(obj);
        }
    }

    [[nodiscard]] lv_group_t* group() const noexcept { return group_; }

private:
    HardwareEncoderDriver() = default;

    static void readCallbackThunk(lv_indev_t* indev, lv_indev_data_t* data) {
        auto* self = static_cast<HardwareEncoderDriver*>(lv_indev_get_user_data(indev));
        if (self) {
            self->handleRead(data);
        }
    }

    void handleRead(lv_indev_data_t* data) {
        data->enc_diff = diff_reader_ ? diff_reader_() : 0;
        data->state    = (btn_reader_ && btn_reader_()) 
                         ? LV_INDEV_STATE_PRESSED 
                         : LV_INDEV_STATE_RELEASED;
    }

    DiffReader diff_reader_{nullptr};
    ButtonReader btn_reader_{nullptr};
    lv_indev_t* indev_{nullptr};
    lv_group_t* group_{nullptr};
};

} // namespace field_ui
