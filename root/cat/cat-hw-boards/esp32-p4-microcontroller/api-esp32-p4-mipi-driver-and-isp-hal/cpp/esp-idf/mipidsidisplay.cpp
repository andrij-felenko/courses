#include "esp_lcd_mipi_dsi.h"
#include "esp_log.h"

static const char *TAG = "mipi_dsi_cpp";

class MipiDsiDisplay {
public:
    esp_err_t init(esp_lcd_panel_handle_t &panel_handle) {
        esp_lcd_dsi_bus_config_t bus_config = {};
        bus_config.bus_id = 0;
        bus_config.num_data_lanes = 2;
        bus_config.phy_clk_src = MIPI_DSI_PHY_CLK_SRC_DEFAULT;
        bus_config.lane_bit_rate_mbps = 1000;

        esp_lcd_dsi_bus_handle_t dsi_bus = nullptr;
        esp_err_t ret = esp_lcd_new_dsi_bus(&bus_config, &dsi_bus);
        if (ret != ESP_OK) return ret;

        esp_lcd_dpi_panel_config_t dpi_config = {};
        dpi_config.virtual_channel = 0;
        dpi_config.dpi_clk_src = MIPI_DSI_DPI_CLK_SRC_DEFAULT;
        dpi_config.dpi_def_clk_hz = 30 * 1000 * 1000;
        dpi_config.pixel_format = LCD_COLOR_PIXEL_FORMAT_RGB565;
        dpi_config.video_timing.h_size = 800;
        dpi_config.video_timing.v_size = 480;
        dpi_config.video_timing.hsync_back_porch = 40;
        dpi_config.video_timing.hsync_front_porch = 40;
        dpi_config.video_timing.hsync_pulse_width = 48;
        dpi_config.video_timing.vsync_back_porch = 13;
        dpi_config.video_timing.vsync_front_porch = 1;
        dpi_config.video_timing.vsync_pulse_width = 3;
        dpi_config.num_fbs = 2;

        ret = esp_lcd_new_panel_dpi(dsi_bus, &dpi_config, &panel_handle);
        if (ret != ESP_OK) return ret;

        esp_lcd_panel_reset(panel_handle);
        return esp_lcd_panel_init(panel_handle);
    }
};
