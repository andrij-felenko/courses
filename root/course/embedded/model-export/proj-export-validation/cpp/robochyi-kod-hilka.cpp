#include "tensorflow/lite/interpreter.h"
#include "tensorflow/lite/kernels/register.h"
#include "tensorflow/lite/model.h"

#include <vector>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <algorithm>

// Скільки виходів у моделі (число класів, або 1 для регресії).
constexpr int kNumOutputs = 4;

// Один кадр — вектор float у ФІЗИЧНИХ одиницях (як з давача/датасету).
using Frame = std::vector<float>;

// Гілка ПРИСТРОЮ на хості: проганяє кадр крізь .tflite тим самим рушієм,
// що й на чипі, і повертає kNumOutputs float-значень (деквантований вихід).
struct LiteModel {
    std::unique_ptr<tflite::FlatBufferModel> model;
    std::unique_ptr<tflite::Interpreter>     interp;
    TfLiteTensor* input  = nullptr;
    TfLiteTensor* output = nullptr;

    bool load(const char* path) {
        model = tflite::FlatBufferModel::BuildFromFile(path);   // читаємо .tflite
        if (!model) { printf("не відкрив %s\n", path); return false; }

        tflite::ops::builtin::BuiltinOpResolver resolver;       // на хості — повний набір
        tflite::InterpreterBuilder(*model, resolver)(&interp);
        if (!interp || interp->AllocateTensors() != kTfLiteOk) {
            printf("AllocateTensors не вдався\n"); return false;
        }
        input  = interp->input_tensor(0);
        output = interp->output_tensor(0);
        return true;
    }
    // ...прогін кадра — нижче
};
