// --- ланка 1: медіана-3 проти одиночних викидів (нелінійна) ---
static int16_t m0, m1, m2;
static int16_t median3(int16_t x) {
    m0 = m1; m1 = m2; m2 = x;
    int16_t a = m0, b = m1, c = m2, t;
    if (a > b) { t = a; a = b; b = t; }          // невелике сортування трьох
    if (b > c) { t = b; b = c; c = t; }
    if (a > b) { t = a; a = b; b = t; }
    return b;                                     // середній із трьох
}

// --- ланка 2: БІХ-notch 50 Гц (пряма форма II, один біквад) ---
static float bz1, bz2;                            // стан біквада
static float notch50(float x, const float c[5]) { // c = {b0,b1,b2,a1,a2}
    float w = x - c[3]*bz1 - c[4]*bz2;            // зворотний зв'язок (полюси)
    float y = c[0]*w + c[1]*bz1 + c[2]*bz2;       // прямий шлях (нулі)
    bz2 = bz1; bz1 = w;
    return y;
}

// --- ланка 3: короткий симетричний КІХ-згладжувач (лінійна фаза) ---
#define K 15
static float ring[K]; static int rp;
static float fir_smooth(float x, const float h[K]) {
    ring[rp] = x; rp = (rp + 1) % K;
    float acc = 0.0f;
    for (int i = 0; i < K; i++)                   // лише входи — стійкість гарантована
        acc += h[i] * ring[(rp + i) % K];
    return acc;
}

// --- увесь тракт на один відлік ---
float process_sample(int16_t raw, const float notch_c[5], const float fir_h[K]) {
    float x = (float)median3(raw);               // 1) вибили викиди
    x = notch50(x, notch_c);                      // 2) зрізали 50 Гц гостро й дешево
    x = fir_smooth(x, fir_h);                     // 3) згладили, зберігши форму
    return x;
}
