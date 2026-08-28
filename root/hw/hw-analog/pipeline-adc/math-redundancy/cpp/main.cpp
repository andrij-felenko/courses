// 1.5-бітний щабель: два пороги ±Vref/4 (тут Vref=1, шкала −1..+1).
// Повертає цифру D∈{0,1,2}; через out_res віддає залишок для наступного щабля.
int stage_15bit(float vin, float thr_hi, float thr_lo, float *out_res) {
    int d;
    if      (vin >=  thr_hi) d = 2;      // вище верхнього порога
    else if (vin >=  thr_lo) d = 1;      // між порогами — коридор
    else                     d = 0;      // нижче нижнього порога
    *out_res = 2.0f * vin - (float)(d - 1);   // залишок = 2·Vвх − (D−1)·Vref, Vref=1
    return d;
}

// Зібрати код N щаблів зсувним додаванням: код = Σ Dᵢ·2^(N−1−i)
int assemble(const int *D, int n) {
    int code = 0;
    for (int i = 0; i < n; i++) code += D[i] << (n - 1 - i);  // зсув = вага щабля
    return code;
}

void demo(void) {
    const int N = 4;
    float vin = 0.30f;                 // вхід у частках Vref
    int   D[4];
    float r;

    // — чесні пороги: ±0.25 на всіх щаблях —
    r = vin;
    for (int i = 0; i < N; i++) D[i] = stage_15bit(r, +0.25f, -0.25f, &r);
    int code_ok = assemble(D, N);      // еталонний код

    // — той самий вхід, але верхній поріг ПЕРШОГО щабля зсунуто на +0.15 —
    r = vin;
    D[0] = stage_15bit(r, +0.25f + 0.15f, -0.25f, &r);   // поріг 0.40 замість 0.25
    for (int i = 1; i < N; i++) D[i] = stage_15bit(r, +0.25f, -0.25f, &r);
    int code_bad = assemble(D, N);     // код зі зсунутим компаратором

    // code_ok == code_bad — зсувне додавання скасувало похибку порога
}
