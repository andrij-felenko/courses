#include "esp_nn.h"
#include "esp_log.h"

static const char *TAG = "nn_vector";

void run_vector_conv2d(const int8_t *input_data, const int8_t *filter_data,
                       int32_t *output_data, int width, int height,
                       int in_channels, int out_channels) {
    // Векторне обчислення згортки за допомогою ESP-NN та Xtensa PIE
    esp_nn_conv_s8_data_t conv_params = {
        .in_dim = {width, height},
        .in_channel = in_channels,
        .out_channel = out_channels,
        .stride = {1, 1},
        .padding = {0, 0},
        .filter_dim = {3, 3}
    };

    // Виклик прискореного ядра ESP-NN з вирівняними буферами
    esp_nn_conv_s8(&conv_params, input_data, filter_data, output_data);
    ESP_LOGI(TAG, "Обчислення шару Conv2D через інструкції PIE успішно виконано");
}
