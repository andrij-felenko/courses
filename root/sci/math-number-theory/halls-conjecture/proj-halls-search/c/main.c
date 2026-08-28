#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Структура для збереження знайденої кандидатури пар Холла
typedef struct {
    uint64_t x;
    uint64_t y;
    int64_t diff;
    double ratio;
} HallCandidate;

// Допоміжна функція для виведення 128-бітного цілого числа у стандартний потік
void print_int128(__int128 n) {
    if (n < 0) {
        putchar('-');
        n = -n;
    }
    if (n == 0) {
        putchar('0');
        return;
    }
    char buf[40];
    int i = 0;
    while (n > 0) {
        buf[i++] = (char)('0' + (n % 10));
        n /= 10;
    }
    while (i > 0) {
        putchar(buf[--i]);
    }
}

// Пошук кандидатури з найменшим ratio для заданого x
bool evaluate_x(uint64_t x, double threshold, HallCandidate *best_out) {
    double x_dbl = (double)x;
    double sqrt_x = sqrt(x_dbl);
    double y_ideal = x_dbl * sqrt_x;
    
    uint64_t y_base = (uint64_t)floor(y_ideal);
    bool found = false;
    double min_ratio = 1e18;
    HallCandidate best_cand = {0};

    // Перевіряємо два сусідні цілі значення: floor(y_ideal) та floor(y_ideal) + 1
    for (uint64_t dy = 0; dy <= 1; ++dy) {
        uint64_t y = y_base + dy;
        if (y == 0) continue;

        __int128 x128 = (__int128)x;
        __int128 y128 = (__int128)y;
        
        __int128 x_cube = x128 * x128 * x128;
        __int128 y_sq = y128 * y128;
        
        __int128 diff128 = y_sq - x_cube;
        if (diff128 == 0) continue; // Ігноруємо тривіальну рівність y^2 = x^3

        double abs_diff = (double)(diff128 < 0 ? -diff128 : diff128);
        double ratio = abs_diff / sqrt_x;

        if (ratio < threshold && ratio < min_ratio) {
            min_ratio = ratio;
            best_cand.x = x;
            best_cand.y = y;
            best_cand.diff = (int64_t)diff128;
            best_cand.ratio = ratio;
            found = true;
        }
    }

    if (found && best_out) {
        *best_out = best_cand;
    }
    return found;
}

int main(void) {
    uint64_t x_max = 10000000ULL; // Межа пошуку x = 10^7
    double threshold = 0.5;      // Шукаємо відношення |y^2 - x^3| / sqrt(x) < 0.5

    printf("Пошук пар Холла для x <= %llu з порогом ratio < %.2f...\n",
           (unsigned long long)x_max, threshold);

    uint64_t count = 0;
    for (uint64_t x = 2; x <= x_max; ++x) {
        HallCandidate cand;
        if (evaluate_x(x, threshold, &cand)) {
            printf("Знайдено пару #%llu: x = %llu, y = %llu, diff = %lld, ratio = %.6f\n",
                   (unsigned long long)++count,
                   (unsigned long long)cand.x,
                   (unsigned long long)cand.y,
                   (long long)cand.diff,
                   cand.ratio);
        }
    }

    printf("Пошук завершено. Знайдено аномальних пар: %llu\n", (unsigned long long)count);
    return 0;
}
