#include <cstdio>
#include "esp_ppa.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

static const char *TAG = "ppa_cpp";

class PpaProcessor {
private:
    ppa_client_handle_t ppa_client_ = nullptr;
    SemaphoreHandle_t done_sem_ = nullptr;

    static bool IRAM_ATTR on_trans_done(ppa_client_handle_t client, const ppa_event_data_t *event_data, void *user_ctx) {
        auto *self = static_cast<PpaProcessor *>(user_ctx);
        BaseType_t high_task_awoken = pdFALSE;
        xSemaphoreGiveFromISR(self->done_sem_, &high_task_awoken);
        return high_task_awoken == pdTRUE;
    }

public:
    esp_err_t init() {
        ppa_client_config_t config = {};
        config.oper_type = PPA_OPERATION_SRM;
        esp_err_t ret = esp_ppa_register_client(&config, &ppa_client_);
        if (ret != ESP_OK) return ret;

        done_sem_ = xSemaphoreCreateBinary();
        ppa_event_callbacks_t cbs = {};
        cbs.on_trans_done = PpaProcessor::on_trans_done;
        return esp_ppa_register_event_callbacks(ppa_client_, &cbs, this);
    }

    esp_err_t scale_frame(void *src_yuv, void *dst_rgb, uint32_t in_w, uint32_t in_h, uint32_t out_w, uint32_t out_h) {
        ppa_srm_oper_config_t srm = {};
        srm.in.buffer = src_yuv;
        srm.in.pic_w = in_w;
        srm.in.pic_h = in_h;
        srm.in.block_w = in_w;
        srm.in.block_h = in_h;
        srm.in.srm_cm = PPA_SRM_COLOR_MODE_YUV420P;

        srm.out.buffer = dst_rgb;
        srm.out.buffer_size = out_w * out_h * 2;
        srm.out.pic_w = out_w;
        srm.out.pic_h = out_h;
        srm.out.srm_cm = PPA_SRM_COLOR_MODE_RGB565;

        srm.scale_x = static_cast<float>(out_w) / in_w;
        srm.scale_y = static_cast<float>(out_h) / in_h;
        srm.mode = PPA_TRANS_MODE_NON_BLOCKING;

        return esp_ppa_do_srm(ppa_client_, &srm);
    }

    bool wait_completion(TickType_t timeout_ticks) {
        return xSemaphoreTake(done_sem_, timeout_ticks) == pdTRUE;
    }
};
