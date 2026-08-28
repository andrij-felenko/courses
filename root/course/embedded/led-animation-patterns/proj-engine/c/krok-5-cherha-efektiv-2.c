static void queueAdvance(AnimQueue *q) {
    if (q->cur >= q->count) return;              // черга вичерпана

    bool slotFree = (q->slot < 0) || (anims[q->slot].mode == ANIM_OFF);
    if (!slotFree) return;                        // поточний ще грає — чекаємо без блокування

    if (q->left == 0) {                           // повтори поточного кроку скінчились
        q->cur++;                                 // → наступний крок
        if (q->cur >= q->count) { q->slot = -1; return; }  // черга добігла
        q->left = q->steps[q->cur].repeats;
    }

    const AnimStep *s = &q->steps[q->cur];
    q->slot = animStart(q->pin, s->mode, s->shape, s->durationMs, q->invert);
    if (q->left > 0) q->left--;                    // зарахували один повтор
}

void queueTick(void) {
    for (int i = 0; i < 4; i++) queueAdvance(&queues[i]);
}

// запустити послідовність
void queueStart(int i, uint8_t pin, bool invert,
                const AnimStep *steps, uint8_t count) {
    queues[i] = (AnimQueue){ .pin = pin, .invert = invert, .steps = steps,
                             .count = count, .cur = 0,
                             .left = count ? steps[0].repeats : 0, .slot = -1 };
}
