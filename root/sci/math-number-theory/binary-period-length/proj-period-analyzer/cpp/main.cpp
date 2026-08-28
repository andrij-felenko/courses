#include <iostream>
#include <numeric>
#include <string>
#include <stdexcept>
#include <cstdint>

// 1. Типи та константи
using u64 = std::uint64_t;

// 2. Математичне ядро
u64 modular_pow(u64 base, u64 exp, u64 mod) {
    u64 res = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        exp = exp / 2;
        base = (base * base) % mod;
    }
    return res;
}

// Функція обчислення мультиплікативного порядку (найменше t: 2^t mod n == 1)
u64 get_multiplicative_order(u64 n) {
    if (n == 1) return 0;
    u64 t = 1;
    u64 current = 2 % n;
    while (current != 1) {
        current = (current * 2) % n;
        t++;
        // Захист від нескінченного циклу у разі переповнення
        if (t > n) return 0; 
    }
    return t;
}

// 3. Аналізатор знаменника та 4. Обчислювач періоду
struct FractionProperties {
    u64 preperiod_length;
    u64 period_length;
    u64 reduced_p;
    u64 reduced_q;
};

FractionProperties analyze_fraction(u64 p, u64 q) {
    if (q == 0) throw std::invalid_argument("Знаменник не може бути нулем");
    
    u64 gcd_val = std::gcd(p, q);
    u64 p_red = p / gcd_val;
    u64 q_red = q / gcd_val;
    
    u64 s = 0;
    u64 q_odd = q_red;
    
    while (q_odd > 0 && q_odd % 2 == 0) {
        q_odd /= 2;
        s++;
    }
    
    u64 t = get_multiplicative_order(q_odd);
    
    return {s, t, p_red, q_red};
}

// 5. Інтерфейс користувача
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Використання: " << argv[0] << " <чисельник> <знаменник>\n";
        return 1;
    }
    
    try {
        u64 p = std::stoull(argv[1]);
        u64 q = std::stoull(argv[2]);
        
        auto props = analyze_fraction(p, q);
        
        std::cout << "Оригінальний дріб: " << p << " / " << q << "\n";
        std::cout << "Скорочений дріб:   " << props.reduced_p << " / " << props.reduced_q << "\n";
        std::cout << "Довжина передперіоду: " << props.preperiod_length << " біт\n";
        std::cout << "Довжина періоду:      " << props.period_length << " біт\n";
        
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
