#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>

// Функція для знаходження НСД вектора чисел
int find_gcd(const std::vector<int>& coins) {
    int res = coins[0];
    for (size_t i = 1; i < coins.size(); ++i) {
        res = std::gcd(res, coins[i]);
    }
    return res;
}

int frobenius_number(const std::vector<int>& coins) {
    if (find_gcd(coins) != 1) {
        return -1; // Числа Фробеніуса не існує, НСД > 1
    }

    // Для n=2 та n=3 верхня межа рідко перевищує 100000 для невеликих номіналів
    const int MAX_LIMIT = 100000;
    std::vector<bool> dp(MAX_LIMIT + 1, false);
    dp[0] = true;

    int last_unreachable = -1;

    for (int i = 0; i <= MAX_LIMIT; ++i) {
        if (!dp[i]) {
            last_unreachable = i;
        } else {
            for (int c : coins) {
                if (i + c <= MAX_LIMIT) {
                    dp[i + c] = true;
                }
            }
        }
    }

    return last_unreachable;
}

int main() {
    std::vector<int> coins_2 = {3, 5};
    std::vector<int> coins_3 = {6, 9, 20}; // g(6,9,20) = 43

    std::cout << "Frobenius number for (3, 5): " << frobenius_number(coins_2) << "\n";
    std::cout << "Expected: " << 3*5 - 3 - 5 << "\n";
    
    std::cout << "Frobenius number for (6, 9, 20): " << frobenius_number(coins_3) << "\n";
    
    return 0;
}
