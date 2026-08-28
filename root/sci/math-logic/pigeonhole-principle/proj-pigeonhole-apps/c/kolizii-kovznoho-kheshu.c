#include <stdio.h>
#include <string.h>

#define BASE 256
#define MOD 101 // Просте число для модуля

void rabin_karp_search(const char* pat, const char* txt) {
    size_t m = strlen(pat);
    size_t n = strlen(txt);
    if (m > n || m == 0) return;

    long long p_hash = 0;
    long long t_hash = 0;
    long long h = 1;

    for (size_t i = 0; i < m - 1; ++i) {
        h = (h * BASE) % MOD;
    }

    for (size_t i = 0; i < m; ++i) {
        p_hash = (BASE * p_hash + pat[i]) % MOD;
        t_hash = (BASE * t_hash + txt[i]) % MOD;
    }

    for (size_t i = 0; i <= n - m; ++i) {
        if (p_hash == t_hash) {
            // Перевірка на справжній збіг чи колізію Діріхле
            if (strncmp(txt + i, pat, m) == 0) {
                printf("Знайдено паттерн на індексі %zu\n", i);
            } else {
                printf("Хибна колізія Діріхле на індексі %zu!\n", i);
            }
        }
        if (i < n - m) {
            t_hash = (BASE * (t_hash - txt[i] * h) + txt[i + m]) % MOD;
            if (t_hash < 0) t_hash += MOD;
        }
    }
}

int main(void) {
    const char* text = "ABABDABACDABABCABAB";
    const char* pattern = "ABABC";
    rabin_karp_search(pattern, text);
    return 0;
}
