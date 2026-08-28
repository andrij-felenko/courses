#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

std::vector<int> generate_primes(int max_limit) {
    std::vector<bool> is_prime(max_limit + 1, true);
    is_prime[0] = is_prime[1] = false;
    for (int p = 2; p * p <= max_limit; ++p) {
        if (is_prime[p]) {
            for (int i = p * p; i <= max_limit; i += p)
                is_prime[i] = false;
        }
    }
    std::vector<int> primes;
    for (int i = 2; i <= max_limit; ++i) {
        if (is_prime[i]) primes.push_back(i);
    }
    return primes;
}

double compute_zeta_sum(double s, int terms) {
    double sum = 0.0;
    for (int k = 1; k <= terms; ++k) {
        sum += 1.0 / std::pow(k, s);
    }
    return sum;
}

double compute_euler_product(double s, const std::vector<int>& primes) {
    double product = 1.0;
    for (int p : primes) {
        product *= 1.0 / (1.0 - 1.0 / std::pow(p, s));
    }
    return product;
}

int main() {
    double s = 2.0; // Zeta(2) = Pi^2 / 6 ≈ 1.6449340668
    int prime_limit = 100000;
    int sum_terms = 100000;

    auto primes = generate_primes(prime_limit);
    double sum_val = compute_zeta_sum(s, sum_terms);
    double prod_val = compute_euler_product(s, primes);
    double exact_zeta2 = M_PI * M_PI / 6.0;

    std::cout << std::fixed << std::setprecision(10);
    std::cout << "Точне значення Zeta(2) = Pi^2 / 6: " << exact_zeta2 << "\n";
    std::cout << "Часткова сума ряду (100,000 елементів): " << sum_val << "\n";
    std::cout << "Частковий добуток Ейлера (9,592 простих): " << prod_val << "\n";
    std::cout << "Похибка ряду: " << std::abs(exact_zeta2 - sum_val) << "\n";
    std::cout << "Похибка добутку: " << std::abs(exact_zeta2 - prod_val) << "\n";

    return 0;
}
