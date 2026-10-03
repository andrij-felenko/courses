#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "esp_log.h"

static const char *TAG = "tflite_pie";

bool setup_tflite_pie_interpreter(const tflite::Model* model,
                                 uint8_t* tensor_arena,
                                 size_t arena_size) {
    // Налаштування розпізнавача операцій із підтримкою прискорення ESP-NN
    static tflite::MicroMutableOpResolver<4> micro_op_resolver;
    micro_op_resolver.AddConv2D();
    micro_op_resolver.AddDepthwiseConv2D();
    micro_op_resolver.AddReshape();
    micro_op_resolver.AddFullyConnected();

    static tflite::MicroInterpreter interpreter(
        model, micro_op_resolver, tensor_arena, arena_size);

    if (interpreter.AllocateTensors() != kTfLiteOk) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті в Tensor Arena");
        return false;
    }

    ESP_LOGI(TAG, "Інтерпретатор TFLite Micro з інструкціями PIE готовий");
    return true;
}
