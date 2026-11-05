#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s.h"
#include "driver/i2c.h"
#include "esp_log.h"

static const char *TAG = "SPL_METER";

#define I2S_PORT            I2S_NUM_0
#define I2S_SAMPLE_RATE     16000
#define I2S_SCK_IO          GPIO_NUM_14
#define I2S_WS_IO           GPIO_NUM_15
#define I2S_SD_IO           GPIO_NUM_32

#define I2C_MASTER_NUM      I2C_NUM_0
#define I2C_MASTER_SDA_IO   GPIO_NUM_21
#define I2C_MASTER_SCL_IO   GPIO_NUM_22
#define I2C_MASTER_FREQ_HZ  400000
#define SSD1306_I2C_ADDR    0x3C

#define FFT_N               512
#define NUM_SPECTRUM_BARS   8

// Чутливість INMP441: -26 dBFS при 94 дБ SPL (1 Па)
// Опорна константа: SPL_dB = 94.0f + 20.0f * log10f(rms) + 26.0f = 120.0f + 20.0f * log10f(rms)
#define MIC_SENSITIVITY_OFFSET 120.0f

static float s_hann_window[FFT_N];
static float s_real_buffer[FFT_N];
static float s_imag_buffer[FFT_N];
static float s_mag_buffer[FFT_N / 2];
static int32_t s_raw_i2s_buffer[FFT_N];

static void init_hann_window(void)
{
    for (int i = 0; i < FFT_N; ++i) {
        s_hann_window[i] = 0.5f * (1.0f - cosf(2.0f * M_PI * (float)i / (float)(FFT_N - 1)));
    }
}

static esp_err_t init_i2s_microphone(void)
{
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = I2S_SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = FFT_N,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK_IO,
        .ws_io_num = I2S_WS_IO,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_SD_IO
    };

    esp_err_t ret = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка встановлення драйвера I2S: %s", esp_err_to_name(ret));
        return ret;
    }

    ret = i2s_set_pin(I2S_PORT, &pin_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації пінів I2S: %s", esp_err_to_name(ret));
        return ret;
    }

    return i2s_zero_dma_buffer(I2S_PORT);
}

static esp_err_t init_i2c_master(void)
{
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ
    };
    esp_err_t ret = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (ret != ESP_OK) return ret;
    return i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
}

// Базовий Cooley-Tukey Radix-2 FFT на місці
static void compute_fft_radix2(float *real, float *imag, int n)
{
    int j = 0;
    for (int i = 0; i < n - 1; ++i) {
        if (i < j) {
            float tr = real[j]; real[j] = real[i]; real[i] = tr;
            float ti = imag[j]; imag[j] = imag[i]; imag[i] = ti;
        }
        int k = n >> 1;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }

    for (int len = 2; len <= n; len <<= 1) {
        float angle = -2.0f * M_PI / (float)len;
        float wlen_r = cosf(angle);
        float wlen_i = sinf(angle);
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

static float calculate_spl_dbspl(const float *samples, int n)
{
    float sum_sq = 0.0f;
    for (int i = 0; i < n; ++i) {
        sum_sq += samples[i] * samples[i];
    }
    float rms = sqrtf(sum_sq / (float)n);
    if (rms < 1e-6f) rms = 1e-6f;
    float spl_db = MIC_SENSITIVITY_OFFSET + 20.0f * log10f(rms);
    if (spl_db < 30.0f) spl_db = 30.0f; // Поріг тиші для приміщення
    return spl_db;
}

void app_main(void)
{
    ESP_LOGI(TAG, "Ініціалізація вимірювача звукового тиску та аналізатора спектра (SPL / FFT)");

    init_hann_window();

    if (init_i2c_master() != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати I2C для дисплея");
    }

    if (init_i2s_microphone() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка ініціалізації мікрофона I2S!");
        return;
    }

    ESP_LOGI(TAG, "Конвеєр вимірювання успішно запущено. Частота: %d Гц, Блоки: %d семплів", I2S_SAMPLE_RATE, FFT_N);

    while (1) {
        size_t bytes_read = 0;
        esp_err_t res = i2s_read(I2S_PORT, s_raw_i2s_buffer, sizeof(s_raw_i2s_buffer), &bytes_read, portMAX_DELAY);
        if (res != ESP_OK || bytes_read != sizeof(s_raw_i2s_buffer)) {
            ESP_LOGW(TAG, "Пропуск кадру або переривання потоку I2S");
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }

        // Перетворення 24-бітного PCM у 32-бітному слоті на нормалізоване число [-1.0 .. 1.0]
        float unwindowed[FFT_N];
        for (int i = 0; i < FFT_N; ++i) {
            int32_t sample24 = s_raw_i2s_buffer[i] >> 8; // Знакове розширення 24 біт
            float val = (float)sample24 / 8388608.0f;     // Ділення на 2^23
            unwindowed[i] = val;
            s_real_buffer[i] = val * s_hann_window[i];
            s_imag_buffer[i] = 0.0f;
        }

        // Обчислення фізичного звукового тиску
        float spl_dbspl = calculate_spl_dbspl(unwindowed, FFT_N);

        // Обчислення спектра Фур'є
        compute_fft_radix2(s_real_buffer, s_imag_buffer, FFT_N);

        for (int k = 0; k < FFT_N / 2; ++k) {
            float mag = sqrtf(s_real_buffer[k] * s_real_buffer[k] + s_imag_buffer[k] * s_imag_buffer[k]) / (float)(FFT_N / 2);
            s_mag_buffer[k] = mag;
        }

        // Групування спектра на 8 частотних смуг
        int bar_values[NUM_SPECTRUM_BARS] = {0};
        int bin_edges[NUM_SPECTRUM_BARS + 1] = {1, 3, 7, 15, 31, 63, 127, 200, 256};
        for (int b = 0; b < NUM_SPECTRUM_BARS; ++b) {
            float band_energy = 0.0f;
            int count = 0;
            for (int k = bin_edges[b]; k < bin_edges[b + 1]; ++k) {
                band_energy += s_mag_buffer[k];
                count++;
            }
            float avg_energy = (count > 0) ? (band_energy / (float)count) : 0.0f;
            int bar_height = (int)(avg_energy * 300.0f);
            if (bar_height > 60) bar_height = 60;
            bar_values[b] = bar_height;
        }

        ESP_LOGI(TAG, "SPL: %5.1f дБ | Спектр: [%2d %2d %2d %2d %2d %2d %2d %2d]",
                 spl_dbspl,
                 bar_values[0], bar_values[1], bar_values[2], bar_values[3],
                 bar_values[4], bar_values[5], bar_values[6], bar_values[7]);

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
