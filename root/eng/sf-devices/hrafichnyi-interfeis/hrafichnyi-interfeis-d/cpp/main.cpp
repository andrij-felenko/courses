#include "lvgl.h"
#include <span>
#include <memory>

namespace app::ui {

template <size_t HorRes, size_t VerRes, size_t Lines>
class GraphicsSystem {
public:
    static constexpr size_t kBufferSize = HorRes * Lines;

    GraphicsSystem() = default;

    void initialize(void (*flushCallback)(lv_disp_drv_t*, const lv_area_t*, lv_color_t*))
    {
        lv_init();

        lv_disp_draw_buf_init(&draw_buf_, buffer1_, buffer2_, kBufferSize);

        lv_disp_drv_init(&disp_drv_);
        disp_drv_.hor_res   = static_cast<lv_coord_t>(HorRes);
        disp_drv_.ver_res   = static_cast<lv_coord_t>(VerRes);
        disp_drv_.flush_cb  = flushCallback;
        disp_drv_.draw_buf  = &draw_buf_;
        disp_drv_.user_data = this;

        lv_disp_drv_register(&disp_drv_);

        buildUserInterface();
    }

    void process()
    {
        lv_timer_handler();
    }

private:
    alignas(32) lv_color_t buffer1_[kBufferSize]{};
    alignas(32) lv_color_t buffer2_[kBufferSize]{};

    lv_disp_draw_buf_t draw_buf_{};
    lv_disp_drv_t      disp_drv_{};

    void buildUserInterface()
    {
        lv_obj_t* btn = lv_btn_create(lv_scr_act());
        lv_obj_align(btn, LV_ALIGN_CENTER, 0, 0);

        lv_obj_t* label = lv_label_create(btn);
        lv_label_set_text(label, "Старт системи");
    }
};

} // namespace app::ui
