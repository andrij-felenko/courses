// Оцінка RMS-шуму на серії відліків сталого входу.
float mean = 0.0f;
for (int i = 0; i < N; i++) mean += x[i];
mean /= N;

float var = 0.0f;                       // дисперсія = середній квадрат відхилення
for (int i = 0; i < N; i++) {
    float d = x[i] - mean;
    var += d * d;
}
var /= N;
float sigma = sqrtf(var);               // RMS-шум, σ

float A      = 1000.0f;                 // робочий розмах сигналу, одиниці АЦП
float snr_db = 20.0f * log10f(A / sigma);
