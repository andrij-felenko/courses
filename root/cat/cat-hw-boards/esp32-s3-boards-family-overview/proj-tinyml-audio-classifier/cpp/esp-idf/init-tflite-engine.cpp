#include <cstddef>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

static const char *TAG = "TFLITE_CPP";
constexpr size_t kTensorArenaSize = 64 * 1024;

void init_tflite_engine(const uint8_t *model_flatbuffer) {
    // Виділяємо 16-байтово вирівняну арену у внутрішній SRAM
    uint8_t *tensor_arena = static_cast<uint8_t*>(
        heap_caps_aligned_alloc(16, kTensorArenaSize, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)
    );

    const tflite::Model *model = tflite::GetModel(model_flatbuffer);
    
    // Реєструємо лише необхідні оператори для класифікатора аудіоподій
    static tflite::MicroMutableOpResolver<5> micro_resolver;
    micro_resolver.AddConv2D();
    micro_resolver.AddDepthwiseConv2D();
    micro_resolver.AddReshape();
    micro_resolver.AddFullyConnected();
    micro_resolver.AddSoftmax();

    static tflite::MicroInterpreter interpreter(
        model, micro_resolver, tensor_arena, kTensorArenaSize
    );

    if (interpreter.AllocateTensors() != kTfLiteOk) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті для тензорів в арені!");
        return;
    }

    ESP_LOGI(TAG, "Інтерпретатор TFLite Micro успішно готовий до інференсу.");
}
