float model_classify(const int8_t* features, int n) {  // ← НА КОЖЕН КАДР
    // 1. Дані вже у int8 (масштаб/нульова точка взяті з input->params).
    for (int i = 0; i < n; i++)
        input->data.int8[i] = features[i];

    // 2. Один прохід графа — детермінований, без алокацій.
    if (interp->Invoke() != kTfLiteOk)
        return -1.0f;

    // 3. Вихід — теж int8; повертаємо в звичне число тим самим містком.
    int8_t  raw   = output->data.int8[0];
    float   scale = output->params.scale;
    int     zp    = output->params.zero_point;
    return scale * (raw - zp);                          // ймовірність 0…1
}
