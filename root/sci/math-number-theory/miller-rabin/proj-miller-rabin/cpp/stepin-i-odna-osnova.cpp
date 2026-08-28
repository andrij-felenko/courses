// a^e mod m швидким піднесенням до квадрата
u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1 % m;     // саме 1 % m — коректно й для m == 1
    a %= m;
    while (e) {
        if (e & 1) r = mulmod(r, a, m);
        a = mulmod(a, a, m);
        e >>= 1;
    }
    return r;
}
