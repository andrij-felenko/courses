#include <math.h>
#include <stdint.h>
#include <stdbool.h>

// Втрати вільного простору, дБ.  d — метри (зручно для польових відстаней),
// f — мегагерци.  Усередині переводимо метри в кілометри під формулу.
static float fspl_db(float d_m, float f_mhz) {
    float d_km = d_m / 1000.0f;
    return 20.0f * log10f(d_km) + 20.0f * log10f(f_mhz) + 32.44f;
}
