#include <stdint.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int width;
    int height;
    double *sum;    // S(x, y) = Σ I
    double *sqsum;  // S2(x, y) = Σ I^2
} IntegralImage;

IntegralImage* integral_image_create(int width, int height) {
    IntegralImage *ii = (IntegralImage*)malloc(sizeof(IntegralImage));
    if (!ii) return NULL;
    ii->width = width;
    ii->height = height;
    ii->sum = (double*)calloc((size_t)(width + 1) * (size_t)(height + 1), sizeof(double));
    ii->sqsum = (double*)calloc((size_t)(width + 1) * (size_t)(height + 1), sizeof(double));
    if (!ii->sum || !ii->sqsum) {
        free(ii->sum);
        free(ii->sqsum);
        free(ii);
        return NULL;
    }
    return ii;
}

void integral_image_destroy(IntegralImage *ii) {
    if (ii) {
        free(ii->sum);
        free(ii->sqsum);
        free(ii);
    }
}

void integral_image_compute(IntegralImage *ii, const uint8_t *image, int stride) {
    const int w = ii->width;
    const int h = ii->height;
    const int stride_ii = w + 1;

    for (int y = 0; y < h; ++y) {
        double row_sum = 0.0;
        double row_sqsum = 0.0;
        const uint8_t *img_row = image + y * stride;
        double *sum_row = ii->sum + (y + 1) * stride_ii + 1;
        double *sum_prev = ii->sum + y * stride_ii + 1;
        double *sqsum_row = ii->sqsum + (y + 1) * stride_ii + 1;
        double *sqsum_prev = ii->sqsum + y * stride_ii + 1;

        for (int x = 0; x < w; ++x) {
            const double val = (double)img_row[x];
            row_sum += val;
            row_sqsum += val * val;
            sum_row[x] = sum_prev[x] + row_sum;
            sqsum_row[x] = sqsum_prev[x] + row_sqsum;
        }
    }
}

// Сума та сума квадратів у вікні [x, y, x + w - 1, y + h - 1] за O(1)
void integral_image_query(const IntegralImage *ii, int x, int y, int w, int h,
                          double *out_sum, double *out_sqsum) {
    const int stride = ii->width + 1;
    const int x0 = x, y0 = y;
    const int x1 = x + w, y1 = y + h;

    const double s_d = ii->sum[y1 * stride + x1];
    const double s_b = ii->sum[y0 * stride + x1];
    const double s_c = ii->sum[y1 * stride + x0];
    const double s_a = ii->sum[y0 * stride + x0];
    *out_sum = s_d - s_b - s_c + s_a;

    const double sq_d = ii->sqsum[y1 * stride + x1];
    const double sq_b = ii->sqsum[y0 * stride + x1];
    const double sq_c = ii->sqsum[y1 * stride + x0];
    const double sq_a = ii->sqsum[y0 * stride + x0];
    *out_sqsum = sq_d - sq_b - sq_c + sq_a;
}
