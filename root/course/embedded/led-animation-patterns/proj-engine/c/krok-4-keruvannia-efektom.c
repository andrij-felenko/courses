// повертає індекс слота або -1, якщо всі зайняті
int animStart(uint8_t pin, AnimMode mode, ShapeFn shape,
              uint32_t durationMs, bool invert) {
    for (int i = 0; i < ANIM_SLOTS; i++) {
        if (anims[i].mode == ANIM_OFF) {
            anims[i] = (Anim){ .pin = pin, .mode = mode, .shape = shape,
                               .start = millis(), .duration = durationMs,
                               .pausedAt = 0, .invert = invert };
            return i;
        }
    }
    return -1;   // слотів немає — ефект не запущено (а не «тихо проковтнуто»)
}
