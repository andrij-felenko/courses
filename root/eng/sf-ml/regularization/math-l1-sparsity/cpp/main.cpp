#include <cmath>

// Один L2-крок: кожну вагу ділимо на (1 + 2ηλ) — чисте масштабування.
// Нуль недосяжний, поки z != 0: множення ненульового ніколи не дає 0.
void l2_prox_step(float *w, int n, float eta, float lambda) {
    float scale = 1.0f / (1.0f + 2.0f * eta * lambda);   // < 1
    for (int i = 0; i < n; i++)
        w[i] *= scale;
}

// Один L1-крок: м'яке порогування S(z; ηλ) = sign(z)·max(|z|−ηλ, 0).
// Вага, менша за поріг ηλ, стає ТОЧНО нулем — ознака вимикається.
void l1_prox_step(float *w, int n, float eta, float lambda) {
    float thr = eta * lambda;                    // поріг ηλ — однаковий для всіх
    for (int i = 0; i < n; i++) {
        float z = w[i];
        if (z > thr)        w[i] = z - thr;      // додатну зсунули вниз
        else if (z < -thr)  w[i] = z + thr;      // від'ємну — вгору
        else                w[i] = 0.0f;         // |z| ≤ ηλ → рівний нуль
    }
}
