#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_VARS 16
#define MAX_TERMS 512

typedef struct {
    unsigned bits;   // значення незмінних бітів
    unsigned mask;   // 1 на позиціях прочерків '-'
    int      used;   // прапорець: чи склеївся терм у більший куб
} Term;

// Підрахунок одиничних бітів (вага Геммінга)
static int popcount(unsigned x) {
    int c = 0;
    while (x) {
        c += (x & 1);
        x >>= 1;
    }
    return c;
}

// Перевірка, чи різняться терми рівно в одному незмінному біті
static int can_merge(Term a, Term b, unsigned *diff_bit) {
    if (a.mask != b.mask) return 0;
    unsigned d = (a.bits ^ b.bits) & ~a.mask;
    if (d && (d & (d - 1)) == 0) {
        *diff_bit = d;
        return 1;
    }
    return 0;
}

// Перевірка чи терм накриває конкретний числовий мінтерм
static int covers(Term pi, unsigned minterm) {
    return ((minterm & ~pi.mask) == (pi.bits & ~pi.mask));
}

// Друк імпліканта символами '0', '1', '-'
static void print_term(Term t, int nvars) {
    for (int i = nvars - 1; i >= 0; --i) {
        if (t.mask & (1U << i)) {
            putchar('-');
        } else if (t.bits & (1U << i)) {
            putchar('1');
        } else {
            putchar('0');
        }
    }
}

// Головна функція мінімізації
void quine_mccluskey(int nvars, const int *minterms, int n_min, const int *dontcares, int n_dc) {
    Term current[MAX_TERMS];
    int n_curr = 0;

    // Завантажуємо мінтерми та don't-care стани
    for (int i = 0; i < n_min; ++i) {
        current[n_curr++] = (Term){ .bits = (unsigned)minterms[i], .mask = 0, .used = 0 };
    }
    for (int i = 0; i < n_dc; ++i) {
        current[n_curr++] = (Term){ .bits = (unsigned)dontcares[i], .mask = 0, .used = 0 };
    }

    Term primes[MAX_TERMS];
    int n_primes = 0;

    // Фаза 1: Ітеративне каскадне склеювання
    while (n_curr > 0) {
        Term next_gen[MAX_TERMS];
        int n_next = 0;

        for (int i = 0; i < n_curr; ++i) {
            for (int j = i + 1; j < n_curr; ++j) {
                unsigned diff = 0;
                if (can_merge(current[i], current[j], &diff)) {
                    current[i].used = 1;
                    current[j].used = 1;

                    Term merged = {
                        .bits = current[i].bits & ~diff,
                        .mask = current[i].mask | diff,
                        .used = 0
                    };

                    // Усуваємо дублікати в новому поколінні
                    int exists = 0;
                    for (int k = 0; k < n_next; ++k) {
                        if (next_gen[k].bits == merged.bits && next_gen[k].mask == merged.mask) {
                            exists = 1;
                            break;
                        }
                    }
                    if (!exists && n_next < MAX_TERMS) {
                        next_gen[n_next++] = merged;
                    }
                }
            }
        }

        // Усі несклеєні терми поточного раунду є простими імплікантами
        for (int i = 0; i < n_curr; ++i) {
            if (!current[i].used) {
                int exists = 0;
                for (int k = 0; k < n_primes; ++k) {
                    if (primes[k].bits == current[i].bits && primes[k].mask == current[i].mask) {
                        exists = 1;
                        break;
                    }
                }
                if (!exists && n_primes < MAX_TERMS) {
                    primes[n_primes++] = current[i];
                }
            }
        }

        memcpy(current, next_gen, sizeof(Term) * n_next);
        n_curr = n_next;
    }

    // Фаза 2: Таблиця покриття
    int chart[MAX_TERMS][MAX_TERMS] = {0};
    for (int p = 0; p < n_primes; ++p) {
        for (int m = 0; m < n_min; ++m) {
            if (covers(primes[p], (unsigned)minterms[m])) {
                chart[p][m] = 1;
            }
        }
    }

    int covered_minterms[MAX_TERMS] = {0};
    int chosen_primes[MAX_TERMS] = {0};

    // Знаходження істотних простих імплікантів (EPI)
    for (int m = 0; m < n_min; ++m) {
        int count = 0;
        int last_p = -1;
        for (int p = 0; p < n_primes; ++p) {
            if (chart[p][m]) {
                count++;
                last_p = p;
            }
        }
        if (count == 1 && last_p != -1 && !chosen_primes[last_p]) {
            chosen_primes[last_p] = 1;
            for (int j = 0; j < n_min; ++j) {
                if (chart[last_p][j]) {
                    covered_minterms[j] = 1;
                }
            }
        }
    }

    // Жадібне докриття залишкових мінтермів
    while (1) {
        int all_done = 1;
        for (int m = 0; m < n_min; ++m) {
            if (!covered_minterms[m]) {
                all_done = 0;
                break;
            }
        }
        if (all_done) break;

        int best_p = -1;
        int max_new_cover = -1;
        for (int p = 0; p < n_primes; ++p) {
            if (chosen_primes[p]) continue;
            int new_cov = 0;
            for (int m = 0; m < n_min; ++m) {
                if (!covered_minterms[m] && chart[p][m]) {
                    new_cov++;
                }
            }
            if (new_cov > max_new_cover) {
                max_new_cover = new_cov;
                best_p = p;
            }
        }

        if (best_p == -1 || max_new_cover == 0) break;
        chosen_primes[best_p] = 1;
        for (int m = 0; m < n_min; ++m) {
            if (chart[best_p][m]) covered_minterms[m] = 1;
        }
    }

    // Друк підсумкової мінімальної ДНФ
    printf("Minimal SOP terms:\n");
    int first = 1;
    for (int p = 0; p < n_primes; ++p) {
        if (chosen_primes[p]) {
            if (!first) printf(" + ");
            print_term(primes[p], nvars);
            first = 0;
        }
    }
    printf("\n");
}

int main(void) {
    // Приклад F(A,B,C,D) = Σ m(0, 1, 2, 5, 6, 7, 8, 9, 10, 14)
    int minterms[] = {0, 1, 2, 5, 6, 7, 8, 9, 10, 14};
    int n_min = sizeof(minterms) / sizeof(minterms[0]);
    quine_mccluskey(4, minterms, n_min, NULL, 0);
    return 0;
}
