// Деквантування int8-виходу в звичайне число тим самим афінним містком.
static float dequant(const TfLiteTensor* t, int i) {
    if (t->type == kTfLiteFloat32) return t->data.f[i];        // вже float
    const float s  = t->params.scale;
    const int   zp = t->params.zero_point;
    return s * (t->data.int8[i] - zp);                          // int8 → float
}

// Прогнати ОДИН кадр і записати kNumOutputs виходів у out[].
bool LiteModel::run(const Frame& frame, float* out) {
    if (input->type == kTfLiteFloat32) {
        // Вхід моделі float — кладемо як є.
        for (size_t i = 0; i < frame.size(); ++i) input->data.f[i] = frame[i];
    } else {
        // Вхід моделі int8 — КВАНТУЄМО за параметрами САМОЇ моделі.
        const float s  = input->params.scale;
        const int   zp = input->params.zero_point;
        for (size_t i = 0; i < frame.size(); ++i) {
            int32_t q = (int32_t)lroundf(frame[i] / s) + zp;   // фізичне → int8
            q = std::max(-128, std::min(127, q));              // обов'язковий clamp
            input->data.int8[i] = (int8_t)q;
        }
    }

    if (interp->Invoke() != kTfLiteOk) { printf("Invoke fail\n"); return false; }

    for (int i = 0; i < kNumOutputs; ++i) out[i] = dequant(output, i);
    return true;
}
