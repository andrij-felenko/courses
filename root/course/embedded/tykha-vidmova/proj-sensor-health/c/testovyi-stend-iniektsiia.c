#include <stdio.h>
#include <stdlib.h>

static float pseudo_gaussian_noise(void) {
    /* Проста апроксимація гаусового шуму через суму рівномірних величин */
    float sum = 0.0f;
    for (int i = 0; i < 12; ++i) {
        sum += (float)rand() / (float)RAND_MAX;
    }
    return (sum - 6.0f) * 0.05f; /* Середнє 0, розмах ~0.15 */
}

int main(void) {
    sensor_guard_config_t cfg = {
        .min_plausible    = -20.0f,
        .max_plausible    = 85.0f,
        .max_slew_rate    = 5.0f,    /* Максимум 5 °C за секунду */
        .min_variance     = 0.0001f, /* Мінімальний рівень природного шуму */
        .min_samples_var  = 20
    };

    sensor_guard_t guard;
    sensor_guard_init(&guard, &cfg);

    printf("=== 1. Здоровий сенсор із природним шумом ===\n");
    uint32_t time_ms = 0;
    for (int i = 0; i < 25; ++i) {
        float sample = 25.0f + pseudo_gaussian_noise();
        uint8_t flags = sensor_guard_update(&guard, sample, time_ms);
        time_ms += 100;
        if (i == 24) {
            printf("Відлік #%d: T=%.3f C, дисперсія=%.6f, прапорці=0x%02X (OK)\n",
                   i, sample, guard.m2 / (float)(guard.sample_count - 1), flags);
        }
    }

    printf("\n=== 2. Зависання цифрового виходу (Stuck Value) ===\n");
    for (int i = 0; i < 30; ++i) {
        float sample = 25.000f; /* Абсолютно плоске значення */
        uint8_t flags = sensor_guard_update(&guard, sample, time_ms);
        time_ms += 100;
        if (flags & SENSOR_FAULT_ZERO_VARIANCE) {
            printf("Зафіксовано тиху відмову на кроці #%d! Прапорці=0x%02X (Zero Variance)\n", i, flags);
            break;
        }
    }

    printf("\n=== 3. Мажоритарний кворум 2oo3 при дрейфі одного давача ===\n");
    float t1 = 25.1f, t2 = 25.3f, t3_drifted = 33.8f;
    quorum_result_t qr = sensor_guard_vote_2oo3(t1, t2, t3_drifted, 1.0f);
    printf("Входи: S1=%.1f, S2=%.1f, S3=%.1f\n", t1, t2, t3_drifted);
    printf("Результат кворуму: валідний=%s, результуюча T=%.2f C, маска помилки=0x%02X\n",
           qr.quorum_valid ? "ТАК" : "НІ", qr.voted_value, qr.faulty_sensor_mask);

    return 0;
}
