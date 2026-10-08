#include <Arduino.h>

constexpr int TEMP_POINTS = 5;
constexpr int HUM_POINTS = 3;

const float temp_grid[TEMP_POINTS] = {-10.0f, 0.0f, 10.0f, 20.0f, 40.0f};
const float hum_grid[HUM_POINTS]   = {33.0f, 65.0f, 85.0f};

const float k_table[TEMP_POINTS][HUM_POINTS] = {
    {1.50f, 1.40f, 1.30f},
    {1.30f, 1.20f, 1.10f},
    {1.15f, 1.05f, 0.98f},
    {1.08f, 1.00f, 0.92f},
    {0.95f, 0.85f, 0.78f}
};

float getCorrectionFactor(float temp, float hum) {
    temp = constrain(temp, temp_grid[0], temp_grid[TEMP_POINTS - 1]);
    hum  = constrain(hum, hum_grid[0], hum_grid[HUM_POINTS - 1]);

    int t_idx = 0;
    while (t_idx < TEMP_POINTS - 2 && temp_grid[t_idx + 1] < temp) {
        t_idx++;
    }

    int h_idx = 0;
    while (h_idx < HUM_POINTS - 2 && hum_grid[h_idx + 1] < hum) {
        h_idx++;
    }

    float t1 = temp_grid[t_idx], t2 = temp_grid[t_idx + 1];
    float h1 = hum_grid[h_idx], h2 = hum_grid[h_idx + 1];

    float k11 = k_table[t_idx][h_idx];
    float k12 = k_table[t_idx][h_idx + 1];
    float k21 = k_table[t_idx + 1][h_idx];
    float k22 = k_table[t_idx + 1][h_idx + 1];

    float k_t1 = k11 + (hum - h1) * (k12 - k11) / (h2 - h1);
    float k_t2 = k21 + (hum - h1) * (k22 - k21) / (h2 - h1);

    return k_t1 + (temp - t1) * (k_t2 - k_t1) / (t2 - t1);
}
