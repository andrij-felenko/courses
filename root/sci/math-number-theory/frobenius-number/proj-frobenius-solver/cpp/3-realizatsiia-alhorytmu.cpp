#include <iostream>
#include <vector>
#include <queue>
#include <numeric>
#include <algorithm>
#include <stdexcept>

// Функція для обчислення НСД кількох чисел
long long get_gcd(const std::vector<long long>& coins) {
    long long res = coins[0];
    for (size_t i = 1; i < coins.size(); ++i) {
        res = std::gcd(res, coins[i]);
    }
    return res;
}

// Головна функція
long long frobenius_number(std::vector<long long> coins) {
    if (coins.empty()) throw std::invalid_argument("Масив не може бути порожнім");
    
    // Відкидаємо нулі та сортуємо
    coins.erase(std::remove(coins.begin(), coins.end(), 0), coins.end());
    if (coins.empty()) throw std::invalid_argument("Повинні бути ненульові базових елементів");
    
    std::sort(coins.begin(), coins.end());
    
    if (get_gcd(coins) != 1) {
        throw std::invalid_argument("Найбільший спільний дільник має бути 1");
    }
    
    long long a1 = coins[0];
    if (a1 == 1) return -1; // Усі натуральні числа досяжні
    
    // Відстані (найменші суми для кожної остачі)
    const long long INF = 1e18;
    std::vector<long long> M(a1, INF);
    M[0] = 0;
    
    // Пріоритетна черга для Дейкстри: пара {відстань, вершина}
    using pii = std::pair<long long, int>;
    std::priority_queue<pii, std::vector<pii>, std::greater<pii>> pq;
    pq.push({0, 0});
    
    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        
        if (d > M[u]) continue;
        
        for (size_t i = 1; i < coins.size(); ++i) {
            long long weight = coins[i];
            int v = (u + weight) % a1;
            
            if (M[u] + weight < M[v]) {
                M[v] = M[u] + weight;
                pq.push({M[v], v});
            }
        }
    }
    
    long long max_M = 0;
    for (int i = 1; i < a1; ++i) {
        if (M[i] > max_M) {
            max_M = M[i];
        }
    }
    
    return max_M - a1;
}
