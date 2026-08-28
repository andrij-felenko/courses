#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    long long p;           // Порядок базового поля 𝔽_p
    long long a;           // Слід Фробеніуса a = p + 1 - N1
    long long N1;          // Кількість точок над 𝔽_p
    double re_alpha;       // Дійсна частина власних чисел α1, α2
    double im_alpha;       // Уявна частина власних чисел α1, α2
    bool hasse_valid;      // Прапорець виконання межі Хассе
} ZetaResult;

// Символ Лежандра (a / p) через піднесення до степеня (p - 1) / 2
static int legendre_symbol(long long a, long long p) {
    a = (a % p + p) % p;
    if (a == 0) return 0;
    
    long long res = 1;
    long long base = a;
    long long exp = (p - 1) / 2;
    
    while (exp > 0) {
        if (exp % 2 == 1) {
            res = (__int128)res * base % p;
        }
        base = (__int128)base * base % p;
        exp /= 2;
    }
    
    return (res == 1) ? 1 : -1;
}

// Підрахунок точок N1 на кривій y^2 = x^3 + A*x + B mod p
ZetaResult compute_local_zeta(long long A, long long B, long long p) {
    ZetaResult res;
    res.p = p;
    
    long long affine_points = 0;
    for (long long x = 0; x < p; x++) {
        long long rhs = ((__int128)x * x % p * x + A * x + B) % p;
        rhs = (rhs + p) % p;
        int leg = legendre_symbol(rhs, p);
        affine_points += (1 + leg);
    }
    
    res.N1 = affine_points + 1; // + 1 нескінченна точка O
    res.a = p + 1 - res.N1;
    
    // Перевірка обмеження Хассе |a| <= 2 * sqrt(p)
    double bound = 2.0 * sqrt((double)p);
    res.hasse_valid = (labs(res.a) <= (long long)floor(bound));
    
    // Власні значення α1, α2
    res.re_alpha = (double)res.a / 2.0;
    double disc = 4.0 * (double)p - (double)(res.a * res.a);
    res.im_alpha = (disc >= 0) ? sqrt(disc) / 2.0 : 0.0;
    
    return res;
}

// Обчислення N_n над 𝔽_{p^n} за допомогою рекурентності
long long compute_N_n(const ZetaResult* zeta, int n) {
    if (n == 1) return zeta->N1;
    
    long long s_prev2 = 2;              // S_0 = 2
    long long s_prev1 = zeta->a;        // S_1 = a
    long long s_curr = s_prev1;
    
    for (int i = 2; i <= n; i++) {
        s_curr = zeta->a * s_prev1 - zeta->p * s_prev2;
        s_prev2 = s_prev1;
        s_prev1 = s_curr;
    }
    
    // p^n
    long long p_pow = 1;
    for (int i = 0; i < n; i++) {
        p_pow *= zeta->p;
    }
    
    return p_pow + 1 - s_curr;
}

int main(void) {
    long long p = 5;
    long long A = 1;
    long long B = 1; // y^2 = x^3 + x + 1 mod 5
    
    ZetaResult zeta = compute_local_zeta(A, B, p);
    
    printf("Крива: y^2 = x^3 + %lld x + %lld над F_%lld\n", A, B, p);
    printf("Кількість точок N1 = %lld\n", zeta.N1);
    printf("Слід Фробеніуса a = %lld\n", zeta.a);
    printf("Межа Хассе складена: %s (|a| <= %.2f)\n", 
           zeta.hasse_valid ? "ТАК" : "НІ", 2.0 * sqrt((double)p));
    printf("Чисельник P(t) = 1 - (%lld)*t + %lld*t^2\n", zeta.a, p);
    printf("Власні значення α1, α2 = %.3f ± %.3fi (Модуль |α| = %.3f, sqrt(p) = %.3f)\n\n",
           zeta.re_alpha, zeta.im_alpha, 
           sqrt(zeta.re_alpha * zeta.re_alpha + zeta.im_alpha * zeta.im_alpha),
           sqrt((double)p));
    
    printf("Послідовність кількостей точок N_n над розширеннями F_{p^n}:\n");
    for (int n = 1; n <= 6; n++) {
        long long N_n = compute_N_n(&zeta, n);
        long long p_pow = (long long)pow((double)p, n);
        double bound = 2.0 * sqrt((double)p_pow);
        long long diff = labs(N_n - (p_pow + 1));
        
        printf("  n = %d (F_%-5lld): N_%d = %-6lld |N_n - (p^n+1)| = %-4lld <= %.1f\n",
               n, p_pow, n, N_n, diff, bound);
    }
    
    return 0;
}
