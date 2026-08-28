#include <stdio.h>

// Функція-резолвер: викликається динамічним лінкером ld.so один раз під час старту
static vec_sum_fn resolve_vec_sum(void) {
    CpuCapabilities caps = detect_cpu_features();
    if (caps.has_avx2 && caps.has_fma) {
        return vec_sum_avx2;
    }
    return vec_sum_scalar;
}

// Оголошення публічної функції з атрибутом ifunc
float vec_sum(const float* data, size_t count)
    __attribute__((ifunc("resolve_vec_sum")));

int main(void) {
    float numbers[16] = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f,
                         9.0f, 10.0f, 11.0f, 12.0f, 13.0f, 14.0f, 15.0f, 16.0f};

    // Прямий виклик: динамічний лінкер уже спрямував точку входу на потрібне ядро
    float result = vec_sum(numbers, 16);
    printf("Обчислена сума: %f\n", result);
    return (result > 0.0f) ? 0 : 1;
}
