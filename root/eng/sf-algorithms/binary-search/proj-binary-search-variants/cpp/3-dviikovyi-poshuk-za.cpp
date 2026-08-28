#include <iostream>

long long integer_sqrt(long long n) {
    if (n < 0) return -1;
    if (n == 0) return 0;

    long long low = 1;
    long long high = n;
    long long ans = 1;

    while (low <= high) {
        long long mid = low + (high - low) / 2;

        // Щоб уникнути переповнення mid * mid, порівнюємо mid з n / mid
        if (mid <= n / mid) {
            ans = mid;     // mid є можливим кандидатів, шукаємо більше значення
            low = mid + 1;
        } else {
            high = mid - 1; // mid * mid > n, звужуємо зверху
        }
    }
    return ans;
}

int main() {
    long long number = 50;
    std::cout << "integer_sqrt(" << number << ") = " << integer_sqrt(number) << "\n"; // Поверне 7
    return 0;
}
