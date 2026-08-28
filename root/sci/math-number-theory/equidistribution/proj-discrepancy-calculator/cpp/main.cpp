#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <complex>
#include <numbers>

// Точне обчислення зіркової дискрепантності D*N для std::vector<double>
double compute_star_discrepancy(const std::vector<double>& pts) {
    if (pts.empty()) return 0.0;
    
    std::vector<double> sorted(pts.size());
    for (size_t i = 0; i < pts.size(); ++i) {
        double val = std::fmod(pts[i], 1.0);
        if (val < 0.0) val += 1.0;
        sorted[i] = val;
    }
    
    // Ідіоматичне сортування C++
    std::sort(sorted.begin(), sorted.end());
    
    const size_t n = sorted.size();
    const double inv_n = 1.0 / static_cast<double>(n);
    double max_diff = 0.0;
    
    for (size_t i = 0; i < n; ++i) {
        double current_i = static_cast<double>(i + 1) * inv_n;
        double previous_i = static_cast<double>(i) * inv_n;
        
        double diff1 = std::abs(current_i - sorted[i]);
        double diff2 = std::abs(previous_i - sorted[i]);
        
        max_diff = std::max({max_diff, diff1, diff2});
    }
    
    return max_diff;
}

// Обчислення тригонометричної суми Вейля з використанням std::complex
double compute_weyl_sum(const std::vector<double>& pts, int h) {
    if (pts.empty()) return 0.0;
    
    std::complex<double> sum(0.0, 0.0);
    const double two_pi = 2.0 * std::numbers::pi;
    
    for (double x : pts) {
        double angle = two_pi * h * x;
        sum += std::complex<double>(std::cos(angle), std::sin(angle));
    }
    
    return std::abs(sum) / static_cast<double>(pts.size());
}

// Послідовність Ван дер Корпута
double van_der_corput(size_t n, size_t base) {
    double q = 0.0;
    double bk = 1.0 / static_cast<double>(base);
    while (n > 0) {
        q += static_cast<double>(n % base) * bk;
        n /= base;
        bk /= static_cast<double>(base);
    }
    return q;
}

int main() {
    const size_t N = 1000;
    const double phi = (std::sqrt(5.0) - 1.0) / 2.0;
    
    std::vector<double> golden_seq(N);
    std::vector<double> vdc_seq(N);
    
    for (size_t i = 0; i < N; ++i) {
        golden_seq[i] = std::fmod((i + 1) * phi, 1.0);
        vdc_seq[i] = van_der_corput(i + 1, 2);
    }
    
    std::cout << "Дискрепантність {n*phi} (N=" << N << "): "
              << compute_star_discrepancy(golden_seq) << '\n';
    std::cout << "Дискрепантність Ван дер Корпута (N=" << N << "): "
              << compute_star_discrepancy(vdc_seq) << '\n';
    std::cout << "Сума Вейля |S_N(1)|/N для {n*phi}: "
              << compute_weyl_sum(golden_seq, 1) << '\n';
              
    return 0;
}
