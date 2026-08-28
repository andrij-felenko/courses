// Порівняння float32 vs int8 одного детектора на одноплатнику з прискорювачем.
// Міряємо РЕАЛЬНИЙ настінний час інференсу через <chrono>.
#include <chrono>
#include <cstdint>

double bench(Model& m, const uint8_t* frame) {
    auto t0 = std::chrono::steady_clock::now();
    m.infer(frame);             // один прогін детектора
    auto t1 = std::chrono::steady_clock::now();
    return std::chrono::duration<double, std::milli>(t1 - t0).count();  // мс на кадр
}

// очікувані порядки для легкого детектора:
//   float32: розмір ~ 7 МБ, інференс ~ 60 мс/кадр (~16 fps), mAP = базова
//   int8   : розмір ~ 1.8 МБ, інференс ~ 12 мс/кадр (~80 fps), mAP −1..2%
