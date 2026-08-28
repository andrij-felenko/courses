#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>

class VacancyKMC {
private:
    int size;
    double T;
    double Em;
    double nu0;
    double a;
    double kB;
    int vx, vy;
    std::mt19937 rng;

public:
    VacancyKMC(int lSize = 100, double temp = 900.0, double energyM = 0.75, 
               double freq = 1e13, double latticeA = 2.86e-10)
        : size(lSize), T(temp), Em(energyM), nu0(freq), a(latticeA),
          kB(8.61733e-5), rng(1337) {
        vx = size / 2;
        vy = size / 2;
    }

    void runSimulation(size_t totalJumps = 100000) {
        double singleRate = nu0 * std::exp(-Em / (kB * T));
        double gammaTotal = 4.0 * singleRate;

        std::uniform_real_distribution<double> dist(0.0, 1.0);

        double currentTime = 0.0;
        double unwrappedX = (size / 2) * a;
        double unwrappedY = (size / 2) * a;
        double startX = unwrappedX;
        double startY = unwrappedY;

        const int dx[4] = {1, -1, 0, 0};
        const int dy[4] = {0, 0, 1, -1};

        for (size_t step = 0; step < totalJumps; ++step) {
            double u1 = dist(rng);
            while (u1 == 0.0) u1 = dist(rng);

            double dt = -std::log(u1) / gammaTotal;
            currentTime += dt;

            int moveIdx = static_cast<int>(dist(rng) * 4.0);
            if (moveIdx >= 4) moveIdx = 3;

            vx = (vx + dx[moveIdx] + size) % size;
            vy = (vy + dy[moveIdx] + size) % size;

            unwrappedX += dx[moveIdx] * a;
            unwrappedY += dy[moveIdx] * a;
        }

        double r2 = (unwrappedX - startX) * (unwrappedX - startX) + 
                    (unwrappedY - startY) * (unwrappedY - startY);
        double Dsim = r2 / (4.0 * currentTime);
        double Dtheo = (a * a / 4.0) * gammaTotal;

        std::cout << "=== Симуляція KMC (C++) ===\n"
                  << "Температура T              = " << T << " K\n"
                  << "Фізичний час              = " << std::scientific << currentTime << " с\n"
                  << "Кількість перескоків        = " << totalJumps << "\n"
                  << "Розрахований D (симуляція) = " << Dsim << " м²/с\n"
                  << "Теоретичний D (аналітичний) = " << Dtheo << " м²/с\n";
    }
};

int main() {
    VacancyKMC kmc(100, 900.0, 0.75);
    kmc.runSimulation(100000);
    return 0;
}
