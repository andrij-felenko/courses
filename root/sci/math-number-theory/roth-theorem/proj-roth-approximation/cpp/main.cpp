#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

struct Convergent {
    long long p;
    long long q;
    double alpha_val;
    double error;
    double mu;
    long long a_next;
};

// Обчислення підхідних дробів ланцюгового дробу для дійсного числа alpha
std::vector<Convergent> compute_convergents(double alpha, int max_terms) {
    std::vector<Convergent> result;
    double val = alpha;
    
    long long p0 = 0, p1 = 1;
    long long q0 = 1, q1 = 0;

    for (int i = 0; i < max_terms; ++i) {
        long long a = static_cast<long long>(std::floor(val));
        
        long long p2 = a * p1 + p0;
        long long q2 = a * q1 + q0;

        if (q2 <= 0 || q2 > 1e15) break; // Запобігання переповненню типів цілих чисел

        double approx = static_cast<double>(p2) / static_cast<double>(q2);
        double err = std::abs(alpha - approx);

        double mu = 0.0;
        if (err > 0.0 && q2 > 1) {
            mu = -std::log(err) / std::log(static_cast<double>(q2));
        }

        double diff = val - static_cast<double>(a);
        long long a_next = 0;
        if (std::abs(diff) > 1e-12) {
            a_next = static_cast<long long>(std::floor(1.0 / diff));
        }

        result.push_back({p2, q2, alpha, err, mu, a_next});

        p0 = p1; p1 = p2;
        q0 = q1; q1 = q2;

        if (std::abs(diff) < 1e-12) break;
        val = 1.0 / diff;
    }

    return result;
}

void print_table(const std::string& title, const std::vector<Convergent>& convs) {
    std::cout << "\n=== " << title << " ===\n";
    std::cout << std::setw(12) << "p" 
              << std::setw(12) << "q" 
              << std::setw(18) << "|alpha - p/q|" 
              << std::setw(14) << "Показник mu" 
              << std::setw(12) << "a_{n+1}" << "\n";
    std::cout << std::string(68, '-') << "\n";

    for (const auto& c : convs) {
        std::cout << std::setw(12) << c.p
                  << std::setw(12) << c.q
                  << std::setw(18) << std::scientific << std::setprecision(5) << c.error
                  << std::setw(14) << std::fixed << std::setprecision(4) << c.mu
                  << std::setw(12) << c.a_next << "\n";
    }
}

int main() {
    // 1. Квадратичне алгебраїчне число: sqrt(2) (корінь x² - 2 = 0)
    double sqrt2 = std::sqrt(2.0);
    auto conv_sqrt2 = compute_convergents(sqrt2, 10);
    print_table("Алгебраїчне число sqrt(2) (Теорема Рота: mu <= 2)", conv_sqrt2);

    // 2. Кубічне алгебраїчне число: cbrt(2) (корінь x³ - 2 = 0)
    double cbrt2 = std::cbrt(2.0);
    auto conv_cbrt2 = compute_convergents(cbrt2, 10);
    print_table("Алгебраїчне число cbrt(2) (Теорема Рота: mu <= 2)", conv_cbrt2);

    // 3. Золотий перетин phi = (1 + sqrt(5)) / 2 (найгірше наближуване ірраціональне число)
    double phi = (1.0 + std::sqrt(5.0)) / 2.0;
    auto conv_phi = compute_convergents(phi, 10);
    print_table("Золотий перетин phi (Теорема Рота: mu -> 2 знізу)", conv_phi);

    // 4. Число Ліувіля: L = sum 10^(-k!)
    double liouville = 0.0;
    long long fact = 1;
    for (int k = 1; k <= 6; ++k) {
        fact *= k;
        liouville += std::pow(10.0, -fact);
    }
    auto conv_liouville = compute_convergents(liouville, 6);
    print_table("Число Ліувіля L (Трансцендентне, mu -> inf)", conv_liouville);

    return 0;
}
