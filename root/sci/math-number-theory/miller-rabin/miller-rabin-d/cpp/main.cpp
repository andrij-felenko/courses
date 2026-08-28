using u64  = uint64_t;
using u128 = __uint128_t;

u64 mulmod(u64 a, u64 b, u64 m) { return (u128)a * b % m; }   // без переповнення

u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1 % m;  a %= m;
    while (e) { if (e & 1) r = mulmod(r, a, m); a = mulmod(a, a, m); e >>= 1; }
    return r;
}

// чи є a свідком складеності n, де n − 1 = 2^s · d, d непарне
bool is_witness(u64 a, u64 d, int s, u64 n) {
    u64 x = powmod(a, d, n);
    if (x == 1 || x == n - 1) return false;      // основа мовчить
    for (int r = 1; r < s; ++r) {
        x = mulmod(x, x, n);
        if (x == n - 1) return false;            // дійшли до −1 — мовчить
    }
    return true;                                  // −1 так і не з'явилось — свідок
}
