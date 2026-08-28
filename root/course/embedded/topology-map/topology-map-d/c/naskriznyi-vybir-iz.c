// Перевірка мінімального часу увімкнення для buck — робимо на етапі ТЗ.
// Якщо t_on виходить менший за даташитний t_on(min) — топологія/частота
// не реалізовні: буде пропуск імпульсів і втрата регулювання.
#include <stdio.h>

int buck_min_on_ok(float vin_max, float vout, float f_hz, float t_on_min_ns) {
    float D    = vout / vin_max;          // найменший D — на найбільшому вході
    float t_on = D / f_hz * 1e9f;         // час увімкнення, нс
    printf("D=%.3f  t_on=%.1f нс  (межа %.0f нс)\n", D, t_on, t_on_min_ns);
    return t_on >= t_on_min_ns;           // 1 = реалізовно, 0 = ні
}

int main(void) {
    // 24-В шина, що інколи стрибає до 30 В; ціль 3.3 В; 2 МГц; контролер 60 нс
    if (!buck_min_on_ok(30.0f, 3.3f, 2.0e6f, 60.0f))
        printf("-> 2 МГц не тягне: опусти частоту або зміни контролер\n");
    // те саме на 1 МГц
    buck_min_on_ok(30.0f, 3.3f, 1.0e6f, 60.0f);
    return 0;
}
