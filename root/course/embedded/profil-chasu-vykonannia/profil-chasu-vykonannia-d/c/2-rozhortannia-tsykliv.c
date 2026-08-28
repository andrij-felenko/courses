/* Розгортання циклу фільтрації на C */
#define VECTOR_SIZE 4

float dot_product_unrolled(const float *a, const float *b) {
    float sum = 0.0f;

    #pragma GCC unroll 4
    for (int i = 0; i < VECTOR_SIZE; ++i) {
        sum += a[i] * b[i];
    }
    return sum;
}
