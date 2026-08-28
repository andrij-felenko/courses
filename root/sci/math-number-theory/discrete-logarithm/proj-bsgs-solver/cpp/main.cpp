#include <iostream>
#include <unordered_map>
#include <cmath>

using namespace std;

// Функція для модульного піднесення до степеня: (base^exp) % mod
long long power(long long base, long long exp, long long mod) {
    long long res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

// Алгоритм Baby-step Giant-step
long long solve_discrete_log(long long g, long long y, long long p) {
    g %= p;
    y %= p;
    
    // Якщо y = 1, то g^0 = 1, отже x = 0.
    if (y == 1) return 0;

    long long m = (long long)ceil(sqrt(p));

    // Baby steps: обчислюємо g^j і зберігаємо в хеш-таблицю
    unordered_map<long long, long long> value_to_j;
    long long cur = 1;
    for (long long j = 0; j < m; ++j) {
        // Зберігаємо перше знайдене j (оскільки нам потрібне найменше x)
        if (value_to_j.find(cur) == value_to_j.end()) {
            value_to_j[cur] = j;
        }
        cur = (cur * g) % p;
    }

    // Обчислюємо g^(-m) = (g^m)^(-1)
    // За малою теоремою Ферма, a^(-1) = a^(p-2) (mod p)
    long long g_m = power(g, m, p);
    long long inv_g_m = power(g_m, p - 2, p);

    // Giant steps: шукаємо збіг
    cur = y;
    for (long long i = 0; i < m; ++i) {
        if (value_to_j.find(cur) != value_to_j.end()) {
            return i * m + value_to_j[cur];
        }
        cur = (cur * inv_g_m) % p;
    }

    return -1; // Рішення не знайдено
}

int main() {
    long long g = 2;
    long long p = 1000000007; // Просте число
    // Приклад: нехай секретний x = 1234567
    long long y = power(g, 1234567, p); // y = 143640243
    
    cout << "g = " << g << ", y = " << y << ", p = " << p << endl;
    long long x = solve_discrete_log(g, y, p);
    
    if (x != -1) {
        cout << "Знайдено x: " << x << endl;
    } else {
        cout << "Рішення не знайдено." << endl;
    }

    return 0;
}
