#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr double PI = 3.14159265358979323846;
constexpr double L  = 100e-6;                  // Гн
constexpr double C  = 100e-12;                 // Ф
const double w0 = 1.0 / std::sqrt(L * C);      // власна частота, рад/с
const double T  = 2 * PI / w0;                 // період, с
const double q0 = C * 5.0;                     // заряд при 5 В

struct State { double q, I; };

double energy(State s) { return s.q * s.q / (2 * C) + L * s.I * s.I / 2; }

State forward(State s, double dt) {            // обидва — зі СТАРОГО стану
    return { s.q - dt * s.I, s.I + dt * s.q / (L * C) };
}
State symplectic(State s, double dt) {         // струм зі старого q, заряд — з НОВОГО I
    const double I_new = s.I + dt * s.q / (L * C);
    return { s.q - dt * I_new, I_new };
}
State verlet(State s, double dt) {             // пів кроку струму · крок заряду · пів кроку
    const double Ih = s.I + (dt / 2) * s.q / (L * C);
    const double q  = s.q - dt * Ih;
    return { q, Ih + (dt / 2) * q / (L * C) };
}

template <class Step>
void ring(const char* name, Step step, int periods = 10, int per_period = 200) {
    const double dt = T / per_period;
    State s { q0, 0.0 };
    const double E0 = energy(s);
    double lo = 1.0, hi = 1.0;
    for (int n = 0; n < periods * per_period; ++n) {
        s = step(s, dt);
        const double e = energy(s) / E0;
        lo = std::min(lo, e);
        hi = std::max(hi, e);
    }
    std::printf("%s E: від %.4f до %.4f, наприкінці %.4f\n",
                name, lo, hi, energy(s) / E0);
}

int main() {                                   // назви вирівняні вручну:
    ring("явний Ейлер   ", forward);           // ширина в printf рахує байти,
    ring("симплектичний ", symplectic);        // а не літери кирилиці
    ring("Верле         ", verlet);
}
