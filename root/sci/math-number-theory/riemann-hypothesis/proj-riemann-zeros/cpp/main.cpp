#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

class RiemannZeroFinder {
public:
    static double riemannSiegelTheta(double t) noexcept {
        if (t < 0.1) return 0.0;
        const double t2pi = t / (2.0 * M_PI);
        return (t / 2.0) * std::log(t2pi) - (t / 2.0) - (M_PI / 8.0) + (1.0 / (48.0 * t));
    }

    static double hardyZ(double t) noexcept {
        const double theta = riemannSiegelTheta(t);
        int bound = static_cast<int>(std::sqrt(t / (2.0 * M_PI)));
        if (bound < 1) bound = 1;

        double sum = 0.0;
        for (int n = 1; n <= bound; ++n) {
            sum += (1.0 / std::sqrt(static_cast<double>(n))) * std::cos(theta - t * std::log(static_cast<double>(n)));
        }
        return 2.0 * sum;
    }

    static std::vector<double> findZeros(double tMin, double tMax, double step = 0.1, double tol = 1e-7) {
        std::vector<double> zeros;
        double tCurr = tMin;
        double zCurr = hardyZ(tCurr);

        while (tCurr < tMax) {
            const double tNext = tCurr + step;
            const double zNext = hardyZ(tNext);

            if (zCurr * zNext < 0.0) {
                double low = tCurr;
                double high = tNext;
                double mid = low;

                for (int iter = 0; iter < 50; ++iter) {
                    mid = (low + high) / 2.0;
                    const double zMid = hardyZ(mid);
                    if (std::abs(zMid) < tol || (high - low) / 2.0 < tol) {
                        break;
                    }
                    if (zCurr * zMid < 0.0) {
                        high = mid;
                    } else {
                        low = mid;
                        zCurr = zMid;
                    }
                }
                zeros.push_back(mid);
            }
            tCurr = tNext;
            zCurr = zNext;
        }
        return zeros;
    }
};

int main() {
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Пошук нулів Дзета-функції Рімана (C++ RAII/STL):\n";
    
    const auto zeros = RiemannZeroFinder::findZeros(10.0, 30.0, 0.1);
    for (size_t i = 0; i < zeros.size(); ++i) {
        std::cout << "Нуль #" << (i + 1) << ": t = " << zeros[i] 
                  << "  =>  s = 1/2 + i·" << zeros[i] << "\n";
    }
    return 0;
}
