#include <stdio.h>
#include <math.h>

double kadane_kahan_float(const double* arr, int n) {
    if (arr == NULL || n <= 0) {
        return 0.0;
    }

    double current_sum = arr[0];
    double max_sum = arr[0];
    double compensation = 0.0;

    for (int i = 1; i < n; ++i) {
        if (current_sum < 0.0) {
            current_sum = arr[i];
            compensation = 0.0;
        } else {
            /* Додавання за схемою Кехена з компенсацією похибки */
            double y = arr[i] - compensation;
            double t = current_sum + y;
            compensation = (t - current_sum) - y;
            current_sum = t;
        }

        if (current_sum > max_sum) {
            max_sum = current_sum;
        }
    }

    return max_sum;
}
