#include <math.h>
#define N 1024
float buf[N];        // відліки прискорення, вже зчитані з акселерометра

void prepare(float *buf) {
    // 1) прибрати постійну складову (середнє, зокрема проєкцію g)
    float mean = 0.0f;
    for (int i = 0; i < N; i++) mean += buf[i];
    mean /= N;
    for (int i = 0; i < N; i++) buf[i] -= mean;

    // 2) вікно Ганна: плавно притиснути краї до нуля
    for (int i = 0; i < N; i++) {
        float w = 0.5f * (1.0f - cosf(2.0f * 3.14159265f * i / (N - 1)));
        buf[i] *= w;
    }
}
