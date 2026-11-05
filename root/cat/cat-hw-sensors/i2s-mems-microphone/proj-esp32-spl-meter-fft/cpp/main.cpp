#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <algorithm>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s.h"
#include "esp_log.h"

namespace audio {

class HannWindow {
public:
    explicit HannWindow(size_t size) : window_(size) {
        for (size_t i = 0; i < size; ++i) {
            window_[i] = 0.5f * (1.0f - std::cos(2.0f * static_cast<float>(M_PI) * static_cast<float>(i) / static_cast<float>(size - 1)));
        }
    }

    void apply(const float* input, float* output, size_t size) const noexcept {
        for (size_t i = 0; i < size; ++i) {
            output[i] = input[i] * window_[i];
        }
    }

private:
    std::vector<float> window_;
};

class FftProcessor {
public:
    explicit FftProcessor(size_t n) : size_(n) {}

    void compute(std::vector<float>& real, std::vector<float>& imag) {
        int n = static_cast<int>(size_);
        int j = 0;
        for (int i = 0; i < n - 1; ++i) {
            if (i < j) {
                std::swap(real[j], real[i]);
                std::swap(imag[j], imag[i]);
            }
            int k = n >> 1;
            while (k <= j) {
                j -= k;
                k >>= 1;
            }
            j += k;
        }

        for (int len = 2; len <= n; len <<= 1) {
            float angle = -2.0f * static_cast<float>(M_PI) / static_cast<float>(len);
            float wlen_r = std::cos(angle);
            float wlen_i = std::sin(angle);
            for (int i = 0; i < n; i += len) {
                float w_r = 1.0f;
                float w_i = 0.0f;
                for (int k = 0; k < len / 2; ++k) {
                    float u_r = real[i + k];
                    float u_i = imag[i + k];
                    float v_r = real[i + k + len / 2] * w_r - imag[i + k + len / 2] * w_i;
                    float v_i = real[i + k + len / 2] * w_i + imag[i + k + len / 2] * w_r;
                    real[i + k] = u_r + v_r;
                    imag[i + k] = u_i + v_i;
                    real[i + k + len / 2] = u_r - v_r;
                    imag[i + k + len / 2] = u_i - v_i;
                    float next_w_r = w_r * wlen_r - w_i * wlen_i;
                    w_i = w_r * wlen_i + w_i * wlen_r;
                    w_r = next_w_r;
                }
            }
        }
    }

private:
    size_t size_;
};

class SoundLevelMeter {
public:
    static constexpr float kRefSensitivityOffset = 120.0f; // dB SPL при повному розмаху шкали

    static float calculateSplDb(const float* samples, size_t n) noexcept {
        float sum_sq = 0.0f;
        for (size_t i = 0; i < n; ++i) {
            sum_sq += samples[i] * samples[i];
        }
        float rms = std::sqrt(sum_sq / static_cast<float>(n));
        if (rms < 1e-6f) rms = 1e-6f;
        float spl = kRefSensitivityOffset + 20.0f * std::log10(rms);
        return std::max(30.0f, spl);
    }
};

class I2SMemsReader {
public:
    I2SMemsReader(i2s_port_t port, int sample_rate, size_t block_size)
        : port_(port), sample_rate_(sample_rate), block_size_(block_size) {}

    bool begin(gpio_num_t sck, gpio_num_t ws, gpio_num_t sd) {
        i2s_config_t config = {
            .mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_RX),
            .sample_rate = static_cast<uint32_t>(sample_rate_),
            .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
            .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
            .communication_format = I2S_COMM_FORMAT_STAND_I2S,
            .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
            .dma_buf_count = 4,
            .dma_buf_len = static_cast<int>(block_size_),
            .use_apll = false,
            .tx_desc_auto_clear = false,
            .fixed_mclk = 0
        };

        i2s_pin_config_t pin_config = {
            .bck_io_num = sck,
            .ws_io_num = ws,
            .data_out_num = I2S_PIN_NO_CHANGE,
            .data_in_num = sd
        };

        if (i2s_driver_install(port_, &config, 0, nullptr) != ESP_OK) return false;
        if (i2s_set_pin(port_, &pin_config) != ESP_OK) return false;
        return (i2s_zero_dma_buffer(port_) == ESP_OK);
    }

    bool readBlock(std::vector<int32_t>& raw_buffer) {
        size_t bytes_read = 0;
        esp_err_t err = i2s_read(port_, raw_buffer.data(), raw_buffer.size() * sizeof(int32_t),
                                 &bytes_read, portMAX_DELAY);
        return (err == ESP_OK && bytes_read == raw_buffer.size() * sizeof(int32_t));
    }

private:
    i2s_port_t port_;
    int sample_rate_;
    size_t block_size_;
};

} // namespace audio

extern "C" void app_main()
{
    ESP_LOGI("APP", "Запуск C++ ООП спектроаналізатора та SPL-метра");

    constexpr size_t kFftSize = 512;
    constexpr int kSampleRate = 16000;

    audio::I2SMemsReader mic(I2S_NUM_0, kSampleRate, kFftSize);
    if (!mic.begin(GPIO_NUM_14, GPIO_NUM_15, GPIO_NUM_32)) {
        ESP_LOGE("APP", "Не вдалося ініціалізувати I2S мікрофон");
        return;
    }

    audio::HannWindow hann(kFftSize);
    audio::FftProcessor fft(kFftSize);

    std::vector<int32_t> raw_i2s(kFftSize);
    std::vector<float> unwindowed(kFftSize);
    std::vector<float> real(kFftSize);
    std::vector<float> imag(kFftSize);

    while (true) {
        if (!mic.readBlock(raw_i2s)) {
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }

        // Масштабування відліків
        for (size_t i = 0; i < kFftSize; ++i) {
            int32_t val24 = raw_i2s[i] >> 8;
            unwindowed[i] = static_cast<float>(val24) / 8388608.0f;
            imag[i] = 0.0f;
        }

        float spl_db = audio::SoundLevelMeter::calculateSplDb(unwindowed.data(), kFftSize);
        hann.apply(unwindowed.data(), real.data(), kFftSize);
        fft.compute(real, imag);

        // Обчислення домінуючої гармоніки
        float max_mag = 0.0f;
        size_t peak_bin = 0;
        for (size_t k = 1; k < kFftSize / 2; ++k) {
            float mag = std::sqrt(real[k] * real[k] + imag[k] * imag[k]);
            if (mag > max_mag) {
                max_mag = mag;
                peak_bin = k;
            }
        }

        float peak_freq = static_cast<float>(peak_bin) * static_cast<float>(kSampleRate) / static_cast<float>(kFftSize);
        ESP_LOGI("APP", "SPL: %5.1f дБ | Пік: %6.1f Гц (Ампл: %6.3f)", spl_db, peak_freq, max_mag);

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
