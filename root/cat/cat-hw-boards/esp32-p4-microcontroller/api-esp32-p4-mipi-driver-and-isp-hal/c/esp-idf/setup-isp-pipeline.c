#include "esp_isp.h"
#include "esp_log.h"

static const char *TAG = "isp_pipeline";

esp_err_t setup_isp_pipeline(esp_isp_processor_handle_t *out_isp) {
    // Конфігурація головного процесора ISP
    esp_isp_processor_cfg_t isp_config = {
        .clk_src = ISP_CLK_SRC_DEFAULT,
        .input_data_source = ISP_INPUT_DATA_SOURCE_CSI,
        .input_data_color_type = ISP_COLOR_RAW8,
        .output_data_color_type = ISP_COLOR_RGB888,
        .has_h_size = 1280,
        .has_v_size = 720,
    };

    ESP_ERROR_CHECK(esp_isp_new_processor(&isp_config, out_isp));

    // Налаштування суб-контролера автоматичного балансу білого (AWB)
    esp_isp_awb_config_t awb_config = {
        .sample_point = ISP_AWB_SAMPLE_POINT_AFTER_CCM,
    };
    esp_isp_awb_ctlr_handle_t awb_handle = NULL;
    ESP_ERROR_CHECK(esp_isp_new_awb_controller(*out_isp, &awb_config, &awb_handle));
    ESP_ERROR_CHECK(esp_isp_awb_controller_enable(awb_handle));

    // Активація та запуск конвеєра ISP
    ESP_ERROR_CHECK(esp_isp_enable(*out_isp));
    ESP_ERROR_CHECK(esp_isp_start(*out_isp));

    ESP_LOGI(TAG, "Апаратний конвеєр ISP успішно запущено");
    return ESP_OK;
}
