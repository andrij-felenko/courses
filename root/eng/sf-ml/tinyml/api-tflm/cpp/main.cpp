#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_log.h"          // MicroPrintf
#include "tensorflow/lite/schema/schema_generated.h"
#include "model_data.h"                                // g_model[], згенероване xxd
#include <math.h>                                      // lroundf

// Арена — єдиний робочий буфер в ОЗП. Розмір із запасом, потім звузити.
constexpr int kArenaSize = 24 * 1024;
alignas(16) static uint8_t tensor_arena[kArenaSize];

int run_once(const float sensor[], int n, int* out_class) {
  // Модель із байтів + звірка версії схеми.
  const tflite::Model* model = tflite::GetModel(g_model);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    MicroPrintf("версія схеми моделі не збігається");
    return -1;
  }

  // Резолвер: лише ядра, що є в моделі (N = їх кількість).
  tflite::MicroMutableOpResolver<3> resolver;
  resolver.AddConv2D();
  resolver.AddFullyConnected();
  resolver.AddSoftmax();

  // Рушій зшиває модель, ядра й арену.
  tflite::MicroInterpreter interpreter(model, resolver, tensor_arena, kArenaSize);

  // Розмітити арену — тут падає замала арена або брак ядра.
  if (interpreter.AllocateTensors() != kTfLiteOk) {
    MicroPrintf("AllocateTensors: збільш kArenaSize або додай операції");
    return -1;
  }
  MicroPrintf("арена: %d із %d Б", (int)interpreter.arena_used_bytes(), kArenaSize);

  // Вхід: перевести real → int8 через масштаб тензора.
  TfLiteTensor* input = interpreter.input(0);
  const float s = input->params.scale;
  const int   z = input->params.zero_point;
  for (int i = 0; i < n; ++i) {
    int q = (int)lroundf(sensor[i] / s) + z;
    if (q < -128) q = -128; else if (q > 127) q = 127;   // затиснути в int8
    input->data.int8[i] = (int8_t)q;
  }

  // Прогнати граф.
  if (interpreter.Invoke() != kTfLiteOk) {
    MicroPrintf("Invoke не вдалося");
    return -1;
  }

  // Вихід: int8 → real, знайти клас із найбільшою ймовірністю.
  TfLiteTensor* output = interpreter.output(0);
  const float os = output->params.scale;
  const int   oz = output->params.zero_point;
  const int   classes = output->dims->data[output->dims->size - 1];
  int best = 0; float best_p = -1.0f;
  for (int i = 0; i < classes; ++i) {
    float p = os * (output->data.int8[i] - oz);
    if (p > best_p) { best_p = p; best = i; }
  }
  *out_class = best;
  return 0;
}
