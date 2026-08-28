#include <vector>
#include <functional>

std::vector<int> de_bruijn_fkm(int k, int n) {
    std::vector<int> a(n + 1, 0), seq;
    std::function<void(int, int)> gen = [&](int t, int p) {   // t: довжина; p: період
        if (t > n) {
            if (n % p == 0)                                   // період p ділить n
                seq.insert(seq.end(), a.begin() + 1, a.begin() + p + 1);
        } else {
            a[t] = a[t - p];                                  // менша гілка: тягнемо період
            gen(t + 1, p);
            for (int c = a[t - p] + 1; c < k; ++c) {          // більший символ — новий період
                a[t] = c;
                gen(t + 1, t);
            }
        }
    };
    gen(1, 1);
    return seq;
}
