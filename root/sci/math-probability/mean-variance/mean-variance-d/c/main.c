#include <math.h>

/* Середнє та стандартне відхилення блоку з n відліків.
   Результати кладе за вказівниками out_mean і out_sd; n > 0. */
void block_stats(const float x[], int n, float *out_mean, float *out_sd)
{
    double sum    = 0.0;        /* сума значень      */
    double sum_sq = 0.0;        /* сума їх квадратів  */
    for (int i = 0; i < n; i++) {
        sum    += x[i];
        sum_sq += (double)x[i] * x[i];      /* квадрат у широкому типі */
    }
    double mean = sum / n;                   /* середнє */
    double var  = sum_sq / n - mean * mean;  /* середнє кв. − кв. середнього */
    if (var < 0.0) var = 0.0;                /* захист від похибки округлення */

    *out_mean = (float)mean;
    *out_sd   = (float)sqrt(var);            /* корінь повертає одиниці */
}
