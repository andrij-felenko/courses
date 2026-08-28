#include <cmath>

struct Biquad {
    float b0, b1, b2, a1, a2;
    float s1 = 0.f, s2 = 0.f;               // стан: Direct Form II транспонована

    // Режектор RBJ: центр f0, частота дискретизації fs, гострота Q
    static Biquad notch(float f0, float fs, float Q) {
        constexpr float PI = 3.14159265f;
        const float w0    = 2.f * PI * f0 / fs;
        const float cw    = std::cos(w0);
        const float alpha = std::sin(w0) / (2.f * Q);
        const float a0    = 1.f + alpha;
        return { 1.f/a0, -2.f*cw/a0, 1.f/a0, -2.f*cw/a0, (1.f-alpha)/a0 };
    }

    // Гарячий шлях: один семпл гіро → відфільтрований
    float process(float x) {
        const float y = b0 * x + s1;
        s1 = b1 * x - a1 * y + s2;
        s2 = b2 * x - a2 * y;
        return y;
    }
};

// --- використання ---
Biquad notchRoll = Biquad::notch(63.7f, 8000.f, 6.f);   // по одному на вісь
// ...8000 разів на секунду:
float gyroClean = notchRoll.process(gyroRaw);
