// Квадратичний закон у насиченні: Id = 0.5 * k * (Vgs - Vth)^2
#include <cstdio>

float id_sat(float vgs, float vth, float k) {
    float vov = vgs - vth;          // перевищення порогу
    if (vov <= 0.0f) return 0.0f;   // нижче порога — канал закрито
    return 0.5f * k * vov * vov;    // квадрат перевищення
}

int main() {
    const float vth = 1.0f, k = 0.5f;
    float vgs[] = { 1.5f, 2.0f, 3.0f };
    for (float v : vgs) {
        float vov = v - vth;
        std::printf("Vgs=%.1f V  Vov=%.1f V  Id=%.3f A\n",
                    v, vov, id_sat(v, vth, k));
    }
    return 0;
}
