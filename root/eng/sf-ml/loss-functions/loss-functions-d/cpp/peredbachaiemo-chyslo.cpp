// Середньоквадратична похибка для масиву прогнозів
float mse(const float *pred, const float *truth, int n) {
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        float e = pred[i] - truth[i];   // помилка (зі знаком)
        sum += e * e;                    // квадрат прибирає знак і роздуває великі
    }
    return sum / (float)n;
}

// pred = {7.6, 5.0, 8.7}, truth = {8.0, 3.0, 9.0}
// e      = {-0.4,  2.0, -0.3}
// e*e    = { 0.16, 4.00, 0.09}
// сума   = 4.25 → MSE = 4.25 / 3 ≈ 1.42
