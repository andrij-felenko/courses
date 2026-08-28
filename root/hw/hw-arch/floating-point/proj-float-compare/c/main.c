#include <stdint.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

// біти float як 32-бітне ціле — переносно, через memcpy (не *(int*)&f: те UB)
static int32_t bitsAsInt(float f) {
    int32_t bits;
    memcpy(&bits, &f, sizeof bits);
    return bits;
}

bool nearEqualUlp(float a, float b, int maxUlps) {
    if (isnan(a) || isnan(b))          // NaN не рівний нічому, навіть собі
        return false;
    int32_t ia = bitsAsInt(a);         // біти float як 32-бітне ціле
    int32_t ib = bitsAsInt(b);
    if ((ia < 0) != (ib < 0))          // різні знаки (різні півпрямі):
        return a == b;                 //   єдиний «рівний» випадок тут — ±0
    int32_t ulps = ia - ib;            // та сама півпряма — рахуємо крок
    if (ulps < 0) ulps = -ulps;        // |ia − ib|
    return ulps <= maxUlps;
}
