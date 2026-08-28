typedef enum { ANIM_ONCE, ANIM_LOOP, ANIM_PINGPONG } AnimMode;

typedef struct {
    uint8_t  pin;
    unsigned long start;     // millis() на момент запуску
    uint32_t duration;       // тривалість фази, мс
    AnimMode mode;           // що робити на кінці
    float  (*shape)(float);  // функція форми: фаза → яскравість
} Anim;

Anim anims[8];   // до восьми незалежних ефектів

void animTick(unsigned long now) {
    for (int i = 0; i < 8; i++) {
        Anim *a = &anims[i];
        if (a->duration == 0) continue;            // порожній слот
        float phase = (now - a->start) / (float)a->duration;
        if (phase >= 1.0f) {
            if (a->mode == ANIM_LOOP)      { a->start = now; phase = 0.0f; }
            else if (a->mode == ANIM_PINGPONG) { /* розворот — нижче */ phase = 1.0f; }
            else { phase = 1.0f; a->duration = 0; } // ONCE: завершити й звільнити слот
        }
        float bright = a->shape(phase);            // форма руху
        uint8_t level = (uint8_t)(bright * 255.0f);
        ledcWrite(a->pin, gammaLUT[level]);        // гамма + вивід
    }
}
