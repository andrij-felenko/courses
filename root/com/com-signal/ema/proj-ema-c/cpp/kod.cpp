struct Ema {
    float alpha;                 // коефіцієнт згладжування, 0..1
    float y     = 0.0f;          // поточна згладжена оцінка
    bool  primed = false;        // чи ініціалізовано першим відліком

    explicit Ema(float a) : alpha(a) {}   // y задамо першим же відліком

    float step(float x) {
        if (!primed) {           // старт біля істини, не від нуля
            y = x;
            primed = true;
        } else {
            y += alpha * (x - y);   // одне множення, одне додавання
        }
        return y;
    }
};
