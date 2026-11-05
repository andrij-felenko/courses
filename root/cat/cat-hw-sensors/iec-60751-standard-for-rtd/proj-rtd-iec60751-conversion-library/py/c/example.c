#include "iec60751.h"
#include <stdio.h>

int main() {
    IEC60751 sensor;
    iec60751_init(&sensor, 100.0); // Pt100

    double t = 25.0;
    double r = iec60751_temp_to_res(&sensor, t);
    printf("Температура: %.2f C -> Опір: %.2f Ом\n", t, r);

    double t_calc = iec60751_res_to_temp(&sensor, r);
    printf("Опір: %.2f Ом -> Температура: %.2f C\n", r, t_calc);

    LookupTable lut;
    lut_init(&lut, &sensor, -100.0, 200.0, 1.0);

    double t_lut = lut_lookup_temp(&lut, r);
    printf("Опір через LUT: %.2f Ом -> Температура: %.2f C\n", r, t_lut);

    lut_free(&lut);
    return 0;
}
