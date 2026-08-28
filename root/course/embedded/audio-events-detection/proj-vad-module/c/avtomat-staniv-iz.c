static void noise_update(vad_t *v, uint64_t e);     // визначення — нижче

bool vad_feed(vad_t *v, const int16_t *frame)
{
    frame_feat_t f = frame_features(frame, v->cfg.frame_len);
    uint64_t e = f.sumsq;                        // енергія цього кадру

    // Пороги над фоном, у цілих: множник Qm.4 → множимо й зсуваємо на 4.
    uint64_t thr_up   = ((uint64_t)v->noise * v->cfg.k_up)   >> 4;
    uint64_t thr_down = ((uint64_t)v->noise * v->cfg.k_down) >> 4;

    if (!v->active) {                            // ЗАРАЗ ТИША
        // Основне рішення — за енергією; ZCR підстраховує глухий початок:
        // якщо енергія трохи не дотягла, але ZCR підозріло висока — впускаємо.
        bool loud    = (e > thr_up);
        bool hissy   = (f.zcr >= v->cfg.zcr_high) && (e > thr_down);
        if (loud || hissy) {
            v->active = true;
            v->hang   = v->cfg.hang_frames;      // зарядили хвіст
        } else {
            // ІНВАРІАНТА: фон повзе ТІЛЬКИ тут, у тиші.
            noise_update(v, e);
        }
    } else {                                     // ЗАРАЗ ПОДІЯ
        if (e > thr_down) {
            v->hang = v->cfg.hang_frames;        // ще гучно — перезарядили хвіст
        } else if (v->hang > 0 && --v->hang == 0) {
            v->active = false;                   // тихо й хвіст вичерпано — кінець
        }
    }
    return v->active;
}

bool vad_poll(const vad_t *v) { return v->active; }
