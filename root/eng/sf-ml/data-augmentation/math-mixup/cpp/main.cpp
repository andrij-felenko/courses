#include <cstdint>
#include <cstddef>

constexpr int NCLASS = 3;   // напр. кіт / пес / птах

// Змішати два сірі кадри й ДВА ЇХНІ ЯРЛИКИ одним коефіцієнтом lam.
// a, b   — вхідні кадри w*h байтів (рядок за рядком);
// out    — куди покласти змішаний кадр (w*h байтів);
// ya, yb — вхідні ярлики (по NCLASS ймовірностей, сума = 1);
// yout   — куди покласти змішаний ярлик (NCLASS ймовірностей).
void mixup(const uint8_t *a, const uint8_t *b, uint8_t *out,
           const float *ya, const float *yb, float *yout,
           int w, int h, float lam)
{
    // 1) ПІКСЕЛІ: out = lam*a + (1-lam)*b, з округленням і в межах 0…255.
    for (std::size_t i = 0; i < static_cast<std::size_t>(w) * h; ++i) {
        // static_cast<float> важливо: без нього lam*a[i] порахується неточно
        float v = lam * static_cast<float>(a[i]) + (1.0f - lam) * static_cast<float>(b[i]);
        int   p = static_cast<int>(v + 0.5f);   // округлити до найближчого
        if (p < 0)   p = 0;                      // clamp — на випадок похибки float
        if (p > 255) p = 255;
        out[i] = static_cast<uint8_t>(p);
    }

    // 2) ЯРЛИК: yout = lam*ya + (1-lam)*yb — ТА САМА формула, той самий lam.
    for (int c = 0; c < NCLASS; ++c)
        yout[c] = lam * ya[c] + (1.0f - lam) * yb[c];
}
