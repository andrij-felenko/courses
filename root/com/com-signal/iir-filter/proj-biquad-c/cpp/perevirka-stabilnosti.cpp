void reset(BiquadChain &c) {
    for (auto &s : c.stage) {
        s.x1 = s.x2 = 0.0f;
        s.y1 = s.y2 = 0.0f;
    }
}

// Повертає true, якщо хвіст згас (фільтр стабільний), інакше false.
bool is_stable(BiquadChain &c) {
    reset(c);
    float out = c.step(1.0f);                     // імпульс
    float peak = std::abs(out);
    for (int n = 1; n < 1000; ++n) {
        out = c.step(0.0f);                      // далі — нулі
        peak = std::max(peak, std::abs(out));
        if (std::abs(out) > 1e6f) { reset(c); return false; }  // вибухає
    }
    reset(c);
    return std::abs(out) < 1e-3f;                 // хвіст справді згас
}
