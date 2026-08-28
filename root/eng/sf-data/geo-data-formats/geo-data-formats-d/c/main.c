#include <stdio.h>
#include <math.h>

int main(void) {
    const double MET_PER_DEG = 111100.0;   /* 1° широти ≈ 111.1 км */

    float  lat32  = 50.4501f;
    double step32 = (double)nextafterf(lat32, INFINITY) - (double)lat32;

    double lat64  = 50.4501;
    double step64 = nextafter(lat64, INFINITY) - lat64;

    printf("float : крок %.3e° = %.3f м\n",  step32, step32 * MET_PER_DEG);
    printf("double: крок %.3e° = %.3e м\n",  step64, step64 * MET_PER_DEG);
    return 0;
}
