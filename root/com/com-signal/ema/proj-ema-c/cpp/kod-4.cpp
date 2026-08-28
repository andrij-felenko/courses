struct Dema {
    float alpha, beta;           // α — для рівня, β — для тренду
    float level = 0.0f;          // оцінка рівня
    float trend = 0.0f;          // оцінка тренду
    bool  primed = false;

    Dema(float a, float b) : alpha(a), beta(b) {}

    float step(float x) {
        if (!primed) {
            level = x; trend = 0.0f; primed = true;
            return level;
        }
        float prev = level;
        level += alpha * (x - level) + trend;        // рівень + хід тренду
        trend += beta  * ((level - prev) - trend);   // оновлюємо сам тренд
        return level;
    }
};
