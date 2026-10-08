#include <cstdio>
#include <cstdint>
#include <vector>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s_std.h"

class I2SMemsMicrophone {
public:
    I2SMemsMicrophone(gpio_num_t bclk, gpio_num_t ws, gpio_num_t din, uint32_t sample_rate = 44100)
        : m_bclk(bclk), m_ws(ws), m_din(din), m_sampleRate(sample_rate), m_rxHandle(nullptr),
          m_prevX(0), m_prevY(0.0f), m_alpha(0.995f) {}

    bool begin() {
        i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
        chan_cfg.dma_desc_num = 6;
        chan_cfg.dma_frame_num = 512;

        if (i2s_new_channel(&chan_cfg, nullptr, &m_rxHandle) != ESP_OK) {
            return false;
        }

        i2s_std_config_t std_cfg = {
            .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(m_sampleRate),
            .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
            .gpio_cfg = {
                .mclk = I2S_GPIO_UNUSED,
                .bclk = m_bclk,
                .ws = m_ws,
                .dout = I2S_GPIO_UNUSED,
                .din = m_din,
                .invert_flags = {
                    .mclk_inv = false,
                    .bclk_inv = false,
                    .ws_inv = false,
                },
            },
        };
        std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;

        if (i2s_channel_init_std_mode(m_rxHandle, &std_cfg) != ESP_OK) {
            return false;
        }

        return (i2s_channel_enable(m_rxHandle) == ESP_OK);
    }

    size_t readAndFilter(std::vector<int32_t>& outputBuffer, TickType_t waitTicks = portMAX_DELAY) {
        int32_t rawBuffer[512];
        size_t bytesRead = 0;

        if (i2s_channel_read(m_rxHandle, rawBuffer, sizeof(rawBuffer), &bytesRead, waitTicks) == ESP_OK) {
            size_t count = bytesRead / sizeof(int32_t);
            outputBuffer.resize(count);

            for (size_t i = 0; i < count; ++i) {
                int32_t aligned = rawBuffer[i] >> 8;
                float currentX = static_cast<float>(aligned);
                float filteredY = currentX - static_cast<float>(m_prevX) + m_alpha * m_prevY;
                m_prevX = static_cast<int32_t>(currentX);
                m_prevY = filteredY;

                outputBuffer[i] = static_cast<int32_t>(filteredY);
            }
            return count;
        }
        return 0;
    }

private:
    gpio_num_t m_bclk;
    gpio_num_t m_ws;
    gpio_num_t m_din;
    uint32_t m_sampleRate;
    i2s_chan_handle_t m_rxHandle;
    int32_t m_prevX;
    float m_prevY;
    float m_alpha;
};
