#include <cstdint>
#include <cstdlib>   // llabs

struct Frac { long long p, q; };

// floor(a / b) для b > 0 (цілочисельне ділення в C++ округляє до нуля,
// тож для від'ємного діленого потрібна поправка):
static long long floordiv(long long a, long long b) {
    long long t = a / b;
    return (a % b < 0) ? t - 1 : t;
}

// Найближчий до a/b дріб p/q зі знаменником 1 ≤ q ≤ Q.
// Вхід ТОЧНИЙ: a, b цілі, b ≠ 0, Q ≥ 1. Повертає нескоротний {p, q}.
// Припущення: значення комфортно вкладаються в int64 (до ~1e9).
Frac best_rational(long long a, long long b, long long Q) {
    if (b < 0) { a = -a; b = -b; }          // тримаємо знаменник додатним
    long long num = a, den = b;
    long long p = 1, pp = 0;                 // чисельники підхідних «−1» і «−2»
    long long q = 0, qq = 1;                 // знаменники «−1» і «−2»

    while (den != 0) {                       // кроки Евкліда для (a, b)
        long long ai = floordiv(num, den);   // чергова неповна частка
        long long qn = ai * q + qq;          // знаменник наступного підхідного

        if (qn > Q) {                        // стеля пробита — шукаємо напівпідхідний
            long long t = (Q - qq) / q;      // найвищий щабель, що влазить
            if (t > 0) {
                long long sp = pp + t * p, sq = qq + t * q;
                // порівняти │a/b − p/q│ і │a/b − sp/sq│ без дробів:
                //   │a·q − b·p│·sq   vs   │a·sq − b·sp│·q   (спільний множник b скорочено).
                // Множимо в __int128 — потрійний добуток легко перебиває int64:
                __int128 e1 = (__int128)a * q  - (__int128)b * p;   if (e1 < 0) e1 = -e1;
                __int128 e2 = (__int128)a * sq - (__int128)b * sp;  if (e2 < 0) e2 = -e2;
                if (e2 * q < e1 * sq) return { sp, sq };            // напівпідхідний ближчий
            }
            return { p, q };                 // інакше лишається сам підхідний
        }

        long long pn = ai * p + pp;          // чисельник наступного підхідного
        pp = p; qq = q; p = pn; q = qn;      // зсув вікна рекуренти
        long long rem = num - ai * den;      // остача Евкліда, 0 ≤ rem < den
        num = den; den = rem;
    }
    return { p, q };                         // ланцюг обірвався: a/b влазить точно
}
