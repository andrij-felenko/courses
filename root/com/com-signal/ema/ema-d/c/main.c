#include <stdbool.h>

typedef struct {
    float y;          // поточна згладжена оцінка
    float alpha;      // коефіцієнт згладжування, 0..1
    bool  primed;     // чи вже ініціалізовано першим відліком
} ema_t;

void ema_init(ema_t *f, float alpha) {
    f->alpha  = alpha;
    f->primed = false;   // y задамо першим же відліком, не нулем
}

float ema_step(ema_t *f, float x) {
    if (!f->primed) {            // старт біля істини, а не від нуля
        f->y = x;
        f->primed = true;
    } else {
        f->y += f->alpha * (x - f->y);   // одне множення, одне додавання
    }
    return f->y;
}
