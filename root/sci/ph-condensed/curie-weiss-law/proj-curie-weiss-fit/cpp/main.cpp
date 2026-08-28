#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <stdexcept>

struct FitResult {
    double C;
    double Tc;
    double mu_eff_B;
};

class CurieWeissSolver {
public:
    static double solveMagnetization(double T, double Tc, double tol = 1e-9, int maxIter = 500) {
        if (T >= Tc) return 0.0;
        
        double mCurr = 0.99;
        for (int i = 0; i < maxIter; ++i) {
            double mNext = std::tanh(mCurr * Tc / T);
            if (std::abs(mNext - mCurr) < tol) {
                return mNext;
            }
            mCurr = mNext;
        }
        return mCurr;
    }

    static FitResult fitData(const std::vector<double>& T, const std::vector<double>& chi) {
        size_t n = T.size();
        if (n != chi.size() || n < 2) {
            throw std::invalid_argument("Масиви повинні мати однакову довжину >= 2");
        }

        double sumX = 0.0, sumY = 0.0, sumXX = 0.0, sumXY = 0.0;
        for (size_t i = 0; i < n; ++i) {
            double x = T[i];
            double y = 1.0 / chi[i];
            sumX += x;
            sumY += y;
            sumXX += x * x;
            sumXY += x * y;
        }

        double denom = n * sumXX - sumX * sumX;
        if (std::abs(denom) < 1e-12) {
            throw std::runtime_error("Система регресії вироджена");
        }

        double a = (n * sumXY - sumX * sumY) / denom;
        double b = (sumY - a * sumX) / static_cast<double>(n);

        double C = 1.0 / a;
        double Tc = -b / a;

        constexpr double k_B = 1.380649e-23;
        constexpr double mu_0 = 4.0 * M_PI * 1e-7;
        constexpr double N_A = 6.02214076e23;
        constexpr double mu_B = 9.27401007e-24;

        double mu_eff_J = std::sqrt((3.0 * k_B * C) / (N_A * mu_0));
        double mu_eff_B = mu_eff_J / mu_B;

        return {C, Tc, mu_eff_B};
    }
};
