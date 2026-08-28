#include <stdint.h>
#include <math.h>

typedef struct { float x, y, z; } vec3;

typedef struct {
    vec3  accel_bias;     // зсув акселерометра в системі ТІЛА (м/с²)
    int   calibrated;     // 1, коли зсув визначено
} accel_cal_t;

// Калібрування зсуву на НЕРУХОМОМУ апараті: усереднити N відліків.
// Горизонтальні осі мають дати ~0, вертикальна — ~g; зсув беремо з горизонталі,
// а по вертикалі лишаємо тяжіння (віднімемо його пізніше у світовій системі).
// Повертає 1, якщо апарат був досить нерухомий (розкид малий), інакше 0.
int accel_calibrate(accel_cal_t *cal, const vec3 *samples, int N) {
    vec3 mean = {0, 0, 0};
    for (int i = 0; i < N; i++) {
        mean.x += samples[i].x;  mean.y += samples[i].y;  mean.z += samples[i].z;
    }
    mean.x /= N;  mean.y /= N;  mean.z /= N;

    // перевірка нерухомості: середньоквадратичний розкид навколо середнього
    float var = 0.0f;
    for (int i = 0; i < N; i++) {
        float dx = samples[i].x - mean.x;
        float dy = samples[i].y - mean.y;
        float dz = samples[i].z - mean.z;
        var += dx*dx + dy*dy + dz*dz;
    }
    var /= N;
    if (var > 0.25f) return 0;          // (0.5 м/с²)² — апарат ворушився, не калібруємо

    // зсув по горизонталі — прямо середнє; по вертикалі зсув поки не чіпаємо
    cal->accel_bias.x = mean.x;
    cal->accel_bias.y = mean.y;
    cal->accel_bias.z = 0.0f;           // вертикаль тримає g; зсув Z сховаємо в нуль висоти
    cal->calibrated = 1;
    return 1;
}
