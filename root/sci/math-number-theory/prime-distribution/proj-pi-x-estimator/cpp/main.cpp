#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

// 1. Апроксимація інтегрального логарифма Li(x)
// Використовуємо наближення через ряд Ейлера для експоненціального інтеграла Ei(x)
// Li(x) = Ei(ln(x)), де Ei(u) = gamma + ln(u) + sum(u^k / (k * k!))
double Li(double x) {
    if (x <= 1.0) return 0.0;
    
    double u = std::log(x);
    double gamma = 0.57721566490153286; // Стала Ейлера-Маскероні
    double sum = gamma + std::log(u);
    
    double term = u;
    double factorial = 1.0;
    
    // Обчислюємо 50 членів ряду для високої точності
    for (int k = 1; k < 50; ++k) {
        sum += term / (k * factorial);
        term *= u;
        factorial *= (k + 1);
        
        if (term / (k * factorial) < 1e-9) break; // Зупинка, якщо член ряду дуже малий
    }
    
    return sum;
}

// 2. Функція підрахунку кількості простих чисел π(x) через Решето Ератосфена
long long count_primes(long long limit) {
    if (limit < 2) return 0;
    
    // Вектор булевих значень (std::vector<bool> оптимізований по пам'яті)
    std::vector<bool> is_prime(limit + 1, true);
    is_prime[0] = is_prime[1] = false;
    
    long long count = 0;
    
    for (long long p = 2; p * p <= limit; p++) {
        if (is_prime[p]) {
            // Відмічаємо всі кратні p як складені
            for (long long i = p * p; i <= limit; i += p) {
                is_prime[i] = false;
            }
        }
    }
    
    // Підрахунок прапорців, що залишилися true
    for (long long p = 2; p <= limit; p++) {
        if (is_prime[p]) {
            count++;
        }
    }
    
    return count;
}

// 3. Функція для форматованого виводу порівняння
void print_comparison(long long x) {
    long long pi_val = count_primes(x);
    double li_val = Li(x);
    double x_lnx_val = x / std::log(x);
    
    long long error_li = std::abs(pi_val - (long long)li_val);
    long long error_x_lnx = std::abs(pi_val - (long long)x_lnx_val);
    
    std::cout << "x = 10^" << (long long)std::log10(x) << " (" << x << ")\n";
    std::cout << "π(x):      " << pi_val << "\n";
    std::cout << "x/ln(x):   " << (long long)x_lnx_val << " (похибка: " << error_x_lnx << ")\n";
    std::cout << "Li(x):     " << (long long)li_val << " (похибка: " << error_li << ")\n";
    std::cout << "------------------------------------------\n";
}

int main() {
    std::cout << "Порівняння π(x) з аналітичними наближеннями\n";
    std::cout << "==========================================\n";
    
    // 4. Перевіряємо різні порядки величин
    long long powers_of_10[] = {10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000};
    
    for (long long x : powers_of_10) {
        print_comparison(x);
    }
    
    return 0;
}
