#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Структура для повернення результату розв'язку рівняння Пелля
typedef struct {
    uint64_t x;
    uint64_t y;
    bool found;
    bool overflow;
} PellSolutionC;

// Функція безпечного множення з перевіркою 64-бітного переповнення
static inline bool check_mul_overflow_u64(uint64_t a, uint64_t b, uint64_t *res) {
    if (a == 0 || b == 0) {
        *res = 0;
        return false;
    }
    if (a > UINT64_MAX / b) {
        return true; // Переповнення
    }
    *res = a * b;
    return false;
}

// Пошук фундаментального розв'язку x^2 - d*y^2 = 1 мовою C
PellSolutionC solve_pell_c(uint64_t d) {
    PellSolutionC sol = {0, 0, false, false};

    uint64_t a0 = (uint64_t)sqrt((double)d);
    if (a0 * a0 == d) {
        // d є точним квадратом — нетривіальних розв'язків не існує
        return sol;
    }

    uint64_t m = 0;
    uint64_t d_val = 1;
    uint64_t a = a0;

    uint64_t p_prev1 = 1;
    uint64_t p_curr = a0;

    uint64_t q_prev1 = 0;
    uint64_t q_curr = 1;

    while (true) {
        // Перевірка, чи є поточний підхідний дріб розв'язком: p^2 - d*q^2 == 1
        uint64_t p2, dq2, q2;
        bool ov1 = check_mul_overflow_u64(p_curr, p_curr, &p2);
        bool ov2 = check_mul_overflow_u64(q_curr, q_curr, &q2);
        bool ov3 = check_mul_overflow_u64(d, q2, &dq2);

        if (!ov1 && !ov2 && !ov3 && (p2 == 1 + dq2)) {
            sol.x = p_curr;
            sol.y = q_curr;
            sol.found = true;
            return sol;
        }

        // Обчислення наступних коефіцієнтів ланцюгового дробу
        m = d_val * a - m;
        d_val = (d - m * m) / d_val;
        a = (a0 + m) / d_val;

        // Перевірка переповнення при обчисленні p_next = a * p_curr + p_prev1
        uint64_t a_p, a_q;
        if (check_mul_overflow_u64(a, p_curr, &a_p) || check_mul_overflow_u64(a, q_curr, &a_q)) {
            sol.overflow = true;
            return sol;
        }

        if (UINT64_MAX - a_p < p_prev1 || UINT64_MAX - a_q < q_prev1) {
            sol.overflow = true;
            return sol;
        }

        uint64_t p_next = a_p + p_prev1;
        uint64_t q_next = a_q + q_prev1;

        p_prev1 = p_curr;
        p_curr = p_next;

        q_prev1 = q_curr;
        q_curr = q_next;
    }
}

int main(void) {
    uint64_t test_d[] = {2, 3, 5, 7, 13, 61, 67, 109};
    size_t count = sizeof(test_d) / sizeof(test_d[0]);

    for (size_t i = 0; i < count; ++i) {
        uint64_t d = test_d[i];
        PellSolutionC res = solve_pell_c(d);
        if (res.found) {
            printf("d = %3llu: x = %16llu, y = %16llu\n",
                   (unsigned long long)d,
                   (unsigned long long)res.x,
                   (unsigned long long)res.y);
        } else if (res.overflow) {
            printf("d = %3llu: розв'язок перевищує 64-бітне ціле (переповнення)\n",
                   (unsigned long long)d);
        } else {
            printf("d = %3llu: розв'язок відсутній (d є точним квадратом)\n",
                   (unsigned long long)d);
        }
    }
    return 0;
}
