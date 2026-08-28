constexpr int kArenaSize = 24 * 1024;
alignas(16) static uint8_t tensor_arena[kArenaSize];

static tflite::MicroInterpreter* interp = nullptr;
static TfLiteTensor* input  = nullptr;
static TfLiteTensor* output = nullptr;

bool model_init() {                                    // ← ОДИН РАЗ при старті
    const tflite::Model* model = tflite::GetModel(g_model);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        MicroPrintf("schema %d != %d", model->version(), TFLITE_SCHEMA_VERSION);
        return false;
    }

    static tflite::MicroMutableOpResolver<4> resolver;
    resolver.AddConv2D();
    resolver.AddDepthwiseConv2D();
    resolver.AddFullyConnected();
    resolver.AddSoftmax();

    static tflite::MicroInterpreter static_interp(
        model, resolver, tensor_arena, kArenaSize);
    interp = &static_interp;

    if (interp->AllocateTensors() != kTfLiteOk) {      // розкладка арени
        MicroPrintf("AllocateTensors failed: arena %d B too small", kArenaSize);
        return false;                                  // ← арени не вистачило
    }

    // ВАРТА: скільки арени модель з'їла НАСПРАВДІ.
    size_t used = interp->arena_used_bytes();
    MicroPrintf("arena: used %u of %d B (%u free)",
                (unsigned)used, kArenaSize, (unsigned)(kArenaSize - used));
    if (kArenaSize - used < kArenaSize / 10) {         // запасу < 10%
        MicroPrintf("WARNING: arena margin under 10%% — raise kArenaSize");
        // не валимо запуск, але голосно попереджаємо
    }

    input  = interp->input(0);
    output = interp->output(0);
    return true;
}
