// adev.cpp — перекривна девіація Аллана з журналу відносної частоти.
// Збірка:  g++ -O2 -std=c++17 -o adev adev.cpp
// Виклик:  ./adev 1.0 < y.txt      // 1.0 — крок вимірювання τ₀, секунди
// Рядок журналу: число y (відносне відхилення частоти) або «*» — пропуск.
#include <cmath>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

constexpr size_t MIN_SPANS = 10;   // менш як стільки незалежних відрізків τ у записі — не рахуємо

int main(int argc, char* argv[])
{
    double tau0 = (argc > 1) ? std::stod(argv[1]) : 1.0;

    // 1. Прочитати журнал. Усе, що не парситься у скінченне число, — пропуск.
    std::vector<double> y;
    std::vector<bool> miss;
    std::string line;

    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        try {
            size_t idx = 0;
            double v = std::stod(line, &idx);
            bool ok = (idx > 0) && std::isfinite(v);
            y.push_back(ok ? v : 0.0);
            miss.push_back(!ok);
        } catch (const std::exception&) {
            y.push_back(0.0);
            miss.push_back(true);
        }
    }
    if (y.size() < 4) {
        std::cerr << "замало даних\n";
        return 1;
    }

    const size_t M = y.size();

    // 2. Зняти середню частоту: девіація Аллана від сталого зсуву не залежить,
    //    а великий зсув під час інтегрування з'їдає значущі цифри.
    double sum = 0.0;
    size_t nv = 0;
    for (size_t i = 0; i < M; ++i) {
        if (!miss[i]) {
            sum += y[i];
            ++nv;
        }
    }
    double mean = nv ? sum / nv : 0.0;

    // 3. Один прохід: фаза x (секунди) і наростальний лічильник пропусків.
    //    Фазових точок на одну більше, ніж вимірів.
    const size_t N = M + 1;
    std::vector<double> x(N, 0.0);
    std::vector<unsigned> ng(N, 0);

    for (size_t i = 0; i < M; ++i) {
        x[i + 1]  = x[i] + (miss[i] ? 0.0 : y[i] - mean) * tau0;
        ng[i + 1] = ng[i] + (miss[i] ? 1u : 0u);
    }

    // 4. Драбина τ октавами: m = 1, 2, 4, 8, …
    std::cout << "#   tau, s      sigma_y(tau)   доданків   відрізків\n";
    for (size_t m = 1; 2 * m < N && N / m >= MIN_SPANS; m *= 2) {
        double acc = 0.0;
        size_t k = 0;
        for (size_t i = 0; i + 2 * m < N; ++i) {
            if (ng[i + 2 * m] != ng[i]) continue;   // трійка накрила пропуск
            double d = x[i + 2 * m] - 2.0 * x[i + m] + x[i];
            acc += d * d;
            ++k;
        }
        if (k < 2) continue;
        double tau = static_cast<double>(m) * tau0;
        double avar = acc / (2.0 * tau * tau * static_cast<double>(k));
        std::cout << std::setw(9) << std::setprecision(4) << tau << "  "
                  << std::setw(14) << std::scientific << std::setprecision(4) << std::sqrt(avar) << "  "
                  << std::setw(9) << std::defaultfloat << k << "  "
                  << std::setw(9) << N / m << "\n";
    }

    return 0;
}
