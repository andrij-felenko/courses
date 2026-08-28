// БІХ 1-го порядку: y[n] = a*x[n] + (1-a)*y[n-1]
typedef struct { float a; float y; } ema_t;     // a = α, y = попередній вихід

void ema_init(ema_t *f, float alpha) {
    f->a = alpha;
    f->y = 0.0f;                                 // старт із нуля
}

float ema_step(ema_t *f, float x) {
    f->y += f->a * (x - f->y);                   // = a*x + (1-a)*y_prev, але без зайвого множення
    return f->y;                                 // зворотний зв'язок: y залежить від себе ж
}
