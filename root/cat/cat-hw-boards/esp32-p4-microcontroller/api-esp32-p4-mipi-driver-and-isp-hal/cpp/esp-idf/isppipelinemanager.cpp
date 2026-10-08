#include "esp_isp.h"
#include "esp_log.h"

static const char *TAG = "isp_cpp";

class IspPipelineManager {
public:
    esp_err_t init(esp_isp_processor_handle_t &isp_handle) {
        esp_isp_processor_cfg_t isp_config = {};
        isp_config.clk_src = ISP_CLK_SRC_DEFAULT;
        isp_config.input_data_source = ISP_INPUT_DATA_SOURCE_CSI;
        isp_config.input_data_color_type = ISP_COLOR_RAW8;
        isp_config.output_data_color_type = ISP_COLOR_RGB888;
        isp_config.has_h_size = 1280;
        isp_config.has_v_size = 720;

        esp_err_t ret = esp_isp_new_processor(&isp_config, &isp_handle);
        if (ret != ESP_OK) return ret;

        esp_isp_awb_config_t awb_config = {};
        awb_config.sample_point = ISP_AWB_SAMPLE_POINT_AFTER_CCM;

        esp_isp_awb_ctlr_handle_t awb_handle = nullptr;
        ret = esp_isp_new_awb_controller(isp_handle, &awb_config, &awb_handle);
        if (ret != ESP_OK) return ret;

        esp_isp_awb_controller_enable(awb_handle);

        ret = esp_isp_enable(isp_handle);
        if (ret != ESP_OK) return ret;

        return esp_isp_start(isp_handle);
    }
};
