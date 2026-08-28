#include <stdio.h>
#include <math.h>

void check_nan_c(void) {
    float val = 0.0f / 0.0f;
    if (val != val) {
        printf("val є NaN через пряме порівняння\n");
    }
    if (isnan(val)) {
        printf("val є NaN через макрос isnan()\n");
    }
}
