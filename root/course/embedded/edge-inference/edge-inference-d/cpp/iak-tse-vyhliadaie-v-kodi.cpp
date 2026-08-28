#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "model_data.h"   // масив g_model[] — наш .tflite, вшитий у Flash

// Арену задаємо РУКАМИ. Замала — AllocateTensors() впаде; зависока — крадемо RAM.
// alignas(16): бібліотека хоче вирівняний буфер.
constexpr int kArenaSize = 24 * 1024;
alignas(16) static uint8_t tensor_arena[kArenaSize];

static tflite::MicroInterpreter* interp = nullptr;
static TfLiteTensor* input  = nullptr;
static TfLiteTensor* output = nullptr;

bool model_setup() {                                   // ← ОДИН РАЗ при старті
    const tflite::Model* model = tflite::GetModel(g_model);

    // Перелічуємо ЛИШЕ ті операції, що є в моделі (кожна важить пам'ять).
    static tflite::MicroMutableOpResolver<4> resolver;
    resolver.AddConv2D();
    resolver.AddDepthwiseConv2D();
    resolver.AddFullyConnected();
    resolver.AddSoftmax();

    static tflite::MicroInterpreter static_interp(
        model, resolver, tensor_arena, kArenaSize);
    interp = &static_interp;

    if (interp->AllocateTensors() != kTfLiteOk)        // розкладка арени
        return false;                                  // ← арени не вистачило

    input  = interp->input(0);
    output = interp->output(0);
    return true;
}
