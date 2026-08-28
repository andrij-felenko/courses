#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <numeric>
#include <iomanip>

using Complex = std::complex<double>;
constexpr double PI = 3.14159265358979323846;

// Моделювання біть двох хвиль та обчислення фазової й групової швидкості
void simulateBeats() {
    const double dx = 0.01;
    const double x_max = 50.0;
    const size_t n = static_cast<size_t>(x_max / dx);

    const double w0 = 5.0, dw = 0.5;
    const double k0 = 3.0, dk = 0.8;

    const double w1 = w0 + dw, w2 = w0 - dw;
    const double k1 = k0 + dk, k2 = k0 - dk;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "[C++] Теоретична v_p = " << (w0 / k0) << "\n";
    std::cout << "[C++] Теоретична v_g = " << (dw / dk) << "\n";

    for (double t : {0.0, 10.0}) {
        double max_env = -1.0;
        double x_peak = 0.0;

        for (size_t i = 0; i < n; ++i) {
            double x = i * dx;
            if (x < 10.0 || x > 40.0) continue;

            double env = std::abs(2.0 * std::cos(dw * t - dk * x));
            if (env > max_env) {
                max_env = env;
                x_peak = x;
            }
        }
        std::cout << "Час t = " << std::setw(4) << t 
                  << " c | Пік огинаючої: x_peak = " << x_peak << " м\n";
    }
}

// Просте Кулі-Тьюкі ДПФ (FFT) для комплексної послідовності
void fft(std::vector<Complex>& x, bool invert) {
    size_t n = x.size();
    if (n <= 1) return;

    std::vector<Complex> even(n / 2), odd(n / 2);
    for (size_t i = 0; i < n / 2; ++i) {
        even[i] = x[2 * i];
        odd[i]  = x[2 * i + 1];
    }

    fft(even, invert);
    fft(odd, invert);

    double angle = 2 * PI / n * (invert ? -1.0 : 1.0);
    Complex w(1.0), wlen(std::cos(angle), std::sin(angle));

    for (size_t i = 0; i < n / 2; ++i) {
        Complex u = even[i];
        Complex v = w * odd[i];
        x[i]         = u + v;
        x[i + n / 2] = u - v;
        if (invert) {
            x[i]         /= 2.0;
            x[i + n / 2] /= 2.0;
        }
        w *= wlen;
    }
}

// Симуляція GVD розпливання імпульсу у C++
void simulateGvdPulse() {
    const size_t n = 512; // Степінь 2 для FFT
    const double dt = 0.2;
    const double tau0 = 3.0;
    const double beta2 = 2.5;
    const double z = 100.0;

    std::vector<Complex> u(n);
    std::vector<double> t(n);

    for (size_t i = 0; i < n; ++i) {
        t[i] = (static_cast<double>(i) - n / 2.0) * dt;
        double g = std::exp(- (t[i] * t[i]) / (2.0 * tau0 * tau0));
        u[i] = Complex(g, 0.0);
    }

    fft(u, false);

    const double df = 2.0 * PI / (n * dt);
    for (size_t i = 0; i < n; ++i) {
        double w = (i < n / 2) ? i * df : (static_cast<double>(i) - n) * df;
        double phase = -0.5 * beta2 * w * w * z;
        u[i] *= Complex(std::cos(phase), std::sin(phase));
    }

    fft(u, true);

    double sum_i = 0.0, sum_t2 = 0.0;
    for (size_t i = 0; i < n; ++i) {
        double I = std::norm(u[i]);
        sum_i += I;
        sum_t2 += t[i] * t[i] * I;
    }
    double w_out = std::sqrt(sum_t2 / sum_i);
    std::cout << "[C++] Уширений імпульс: RMS ширина = " << w_out << "\n";
}

// Симуляція солітонного поширення SSFM у C++
void simulateSolitonSsfm() {
    const size_t n = 512;
    const double dt = 0.2;
    const double z_total = 5.0;
    const size_t steps = 100;
    const double dz = z_total / steps;
    const double beta2 = -1.0;
    const double gamma = 1.0;

    std::vector<Complex> A(n);
    for (size_t i = 0; i < n; ++i) {
        double t = (static_cast<double>(i) - n / 2.0) * dt;
        A[i] = Complex(1.0 / std::cosh(t), 0.0);
    }

    const double df = 2.0 * PI / (n * dt);

    for (size_t step = 0; step < steps; ++step) {
        // 1. Півкроку дисперсії
        fft(A, false);
        for (size_t i = 0; i < n; ++i) {
            double w = (i < n / 2) ? i * df : (static_cast<double>(i) - n) * df;
            double phase = -0.5 * beta2 * w * w * (dz / 2.0);
            A[i] *= Complex(std::cos(phase), std::sin(phase));
        }
        fft(A, true);

        // 2. Повний крок нелінійності
        for (size_t i = 0; i < n; ++i) {
            double phase = gamma * std::norm(A[i]) * dz;
            A[i] *= Complex(std::cos(phase), std::sin(phase));
        }

        // 3. Півкроку дисперсії
        fft(A, false);
        for (size_t i = 0; i < n; ++i) {
            double w = (i < n / 2) ? i * df : (static_cast<double>(i) - n) * df;
            double phase = -0.5 * beta2 * w * w * (dz / 2.0);
            A[i] *= Complex(std::cos(phase), std::sin(phase));
        }
        fft(A, true);
    }

    double max_val = 0.0;
    for (size_t i = 0; i < n; ++i) {
        max_val = std::max(max_val, std::abs(A[i]));
    }
    std::cout << "[C++] SSFM солітон: підсумковий пік амплітуди = " << max_val << "\n";
}

int main() {
    simulateBeats();
    simulateGvdPulse();
    simulateSolitonSsfm();
    return 0;
}
