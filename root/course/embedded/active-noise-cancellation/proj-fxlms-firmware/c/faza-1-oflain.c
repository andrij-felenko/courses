#include <stdint.h>

#define M  32                     // довжина моделі вторинного шляху Ŝ (відводів)

static float s_hat[M] = {0};      // оцінка вторинного шляху — її ми вчимо
static float u_buf[M] = {0};      // вікно тестового сигналу u[n] (для згортки Ŝ)

// --- дешевий «білий» шум: 16-бітний LFSR з відводами 16,14,13,11 ---
static uint16_t lfsr = 0xACE1u;   // будь-який ненульовий стан

static inline float white_noise(void)
{
    uint16_t bit = ((lfsr >> 0) ^ (lfsr >> 2) ^ (lfsr >> 3) ^ (lfsr >> 5)) & 1u;
    lfsr = (lfsr >> 1) | (bit << 15);
    return (lfsr & 1u) ? 0.25f : -0.25f;   // ±чверть шкали: тихий тест, щоб не глушити вухо
}

// один такт ідентифікації: подали u в динамік, прочитали відгук d з мікрофона
// повертає поточну похибку моделі (щоб бачити збіжність)
static float ident_step(float u, float d)
{
    // зсув вікна u — поки наївно; у фазі 2 покажемо кільцевий буфер
    for (int i = M - 1; i > 0; --i) u_buf[i] = u_buf[i-1];
    u_buf[0] = u;

    // оцінка відгуку: ŷ = Ŝ ⊛ u
    float y_hat = 0.0f;
    for (int i = 0; i < M; ++i) y_hat += s_hat[i] * u_buf[i];

    float eps = d - y_hat;                  // наскільки Ŝ ще не схожий на S

    // звичайний LMS — женемо eps у нуль (без filtered-x: міряємо шлях напряму)
    const float mu_id = 0.01f;
    for (int i = 0; i < M; ++i)
        s_hat[i] += mu_id * eps * u_buf[i];

    return eps;
}
