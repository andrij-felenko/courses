#include <math.h>

/* Коефіцієнти дискретної НЧ-ланки 1-го порядку:
   y[n] = b0*x[n] + b1*x[n-1] + a1*y[n-1]  (тут b0 == b1). */
typedef struct { float b0, b1, a1; } Lowpass1;

/* Дискретизувати ланку H(s) = 1/(1 + s/w0) за Тастіном із передвикривленням
   на fc. Підставляємо s = K*(z-1)/(z+1), K = w0/tan(w0*dt/2), і зводимо
   H(z) = w0*(z+1) / (K*(z-1) + w0*(z+1)) до рекурсії. Зріз лягає точно
   на fc, DC-підсилення = 1. */
Lowpass1 prewarped_lowpass(float fc_hz, float fs_hz)
{
    float dt = 1.0f / fs_hz;
    float w0 = 2.0f * (float)M_PI * fc_hz;
    /* передвикривлена «частота» K замість сирого 2/dt */
    float K  = w0 / tanf(w0 * dt * 0.5f);   /* прибиває зріз точно на fc */

    /* ділимо чисельник і знаменник H(z) на (K + w0): */
    Lowpass1 c;
    c.b0 = w0 / (K + w0);          /* = b1 */
    c.b1 = c.b0;
    c.a1 = (K - w0) / (K + w0);    /* полюс усередині кола: 0 < a1 < 1 */
    return c;
}
