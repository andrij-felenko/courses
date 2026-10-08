#include "esp_lcd_mipi_dsi.h"
#include "esp_log.h"

static const char *TAG = "mipi_dsi_init";

esp_err_t init_mipi_dsi_display(esp_lcd_panel_handle_t *out_panel) {
    // Конфігурація апаратної шини DSI Host
    esp_lcd_dsi_bus_config_t bus_config = {
        .bus_id = 0,
        .num_data_lanes = 2,
        .phy_clk_src = MIPI_DSI_PHY_CLK_SRC_DEFAULT,
        .lane_bit_rate_mbps = 1000,
    };
    esp_lcd_dsi_bus_handle_t dsi_bus = NULL;
    ESP_ERROR_CHECK(esp_lcd_new_dsi_bus(&bus_config, &dsi_bus));

    // Конфігурація таймінгів DPI-панелі (800x480)
    esp_lcd_dpi_panel_config_t dpi_config = {
        .virtual_channel = 0,
        .dpi_clk_src = MIPI_DSI_DPI_CLK_SRC_DEFAULT,
        .dpi_def_clk_hz = 30 * 1000 * 1000,
        .pixel_format = LCD_COLOR_PIXEL_FORMAT_RGB565,
        .video_timing = {
            .h_size = 800,
            .v_size = 480,
            .hsync_back_porch = 40,
            .hsync_front_porch = 40,
            .hsync_pulse_width = 48,
            .vsync_back_porch = 13,
            .vsync_front_porch = 1,
            .vsync_pulse_width = 3,
        },
        .num_fbs = 2,
    };

    ESP_ERROR_CHECK(esp_lcd_new_panel_dpi(dsi_bus, &dpi_config, out_panel));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(*out_panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(*out_panel));
    ESP_LOGI(TAG, "Шину MIPI-DSI та панель DPI успішно ініціалізовано");
    return ESP_OK;
}
