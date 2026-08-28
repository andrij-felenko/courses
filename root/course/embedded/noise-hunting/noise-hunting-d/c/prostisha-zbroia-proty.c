#include <math.h>

// Загороджувальний біквадрат: глушить рівно f0, лишає решту спектра.
// f0 — частота гулу (50 Гц), fs — частота дискретизації, Q — гострота
// вирізу (більше Q → вужчий, глибший провал саме на 50 Гц).
typedef struct { float b0,b1,b2,a1,a2, x1,x2,y1,y2; } notch_t;

void notch_init(notch_t *f, float f0, float fs, float Q) {
    float w0 = 2.0f * (float)M_PI * f0 / fs;
    float c  = cosf(w0), s = sinf(w0);
    float alpha = s / (2.0f * Q);
    float a0 = 1.0f + alpha;          // нормувальник
    f->b0 =  1.0f      / a0;          // коефіцієнти вирізу:
    f->b1 = -2.0f * c  / a0;          // чисельник має нулі точно на f0,
    f->b2 =  1.0f      / a0;          // тому саме ця частота гаситься в нуль
    f->a1 = -2.0f * c  / a0;
    f->a2 = (1.0f - alpha) / a0;
    f->x1 = f->x2 = f->y1 = f->y2 = 0.0f;
}

// Пряма форма II transposed — по одному відліку за виклик.
float notch_step(notch_t *f, float x) {
    float y = f->b0*x + f->b1*f->x1 + f->b2*f->x2
                       - f->a1*f->y1 - f->a2*f->y2;
    f->x2 = f->x1; f->x1 = x;
    f->y2 = f->y1; f->y1 = y;
    return y;
}
