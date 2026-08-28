extern uint16_t gammaLUT[256];     // готова таблиця гамми з конвеєра яскравості

void animTick(uint32_t now) {
    for (int i = 0; i < ANIM_SLOTS; i++) {
        Anim *a = &anims[i];
        if (a->mode == ANIM_OFF) continue;       // вільний слот — пропустити
        if (a->pausedAt != 0) continue;          // на паузі — нічого не рухаємо

        uint32_t raw = phaseRaw(a, now);         // 0..4096
        uint16_t phase;                          // підсумкова фаза 0..4095

        if (raw <= 4095) {
            phase = (uint16_t)raw;               // прохід ще триває
        } else {
            // прохід дійшов до кінця — розгалуження за режимом
            switch (a->mode) {
                case ANIM_ONCE:
                    phase = 4095;                // зафіксувати кінець…
                    a->mode = ANIM_OFF;          // …і звільнити слот
                    break;
                case ANIM_LOOP:
                    a->start = now;              // новий прохід від нуля
                    phase = 0;
                    break;
                case ANIM_PINGPONG: {
                    // два проходи на період: парний — вперед, непарний — назад
                    uint32_t cycle = (elapsed(a, now)) / a->duration;   // 0,1,2,…
                    uint32_t pos   = (elapsed(a, now)) % a->duration;   // у межах проходу
                    uint32_t fwd   = (pos << 12) / a->duration;         // 0..4095
                    phase = (cycle & 1) ? (uint16_t)(4095 - fwd)        // назад: дзеркало
                                        : (uint16_t)fwd;               // вперед
                    break;
                }
                default:
                    phase = 0;
            }
        }

        uint16_t bright = a->shape(phase);       // форма руху: 0..4095
        uint8_t  idx    = (uint8_t)(bright >> 4);// 0..4095 → 0..255 для гамми
        uint16_t duty   = gammaLUT[idx];         // корекція ока
        if (a->invert) duty = 4095 - duty;       // активно-низьке підключення
        ledcWrite(a->pin, duty);
    }
}
