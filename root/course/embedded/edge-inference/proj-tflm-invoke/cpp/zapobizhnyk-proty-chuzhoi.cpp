#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_log.h"        // MicroPrintf
#include "tensorflow/lite/schema/schema_generated.h" // TFLITE_SCHEMA_VERSION
#include "model_data.h"   // g_model[] — наш .tflite, вшитий у Flash

const tflite::Model* model = tflite::GetModel(g_model);
if (model->version() != TFLITE_SCHEMA_VERSION) {
    MicroPrintf("Model schema %d != supported %d",
                model->version(), TFLITE_SCHEMA_VERSION);
    return false;                                   // ← стоп ТУТ, не далі
}
