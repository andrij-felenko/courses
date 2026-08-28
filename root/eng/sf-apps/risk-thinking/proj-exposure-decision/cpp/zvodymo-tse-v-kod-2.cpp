// Варіант архітектури: назва + список його ризиків.
struct Variant {
    const char* name;
    const Risk* risks;
    int         count;
};

// Сумарна експозиція варіанта — сума експозицій усіх ризиків (НАЇВНА версія).
static double total_exposure_naive(const Variant& v) {
    double sum = 0.0;
    for (int i = 0; i < v.count; ++i)
        sum += exposure(v.risks[i]);
    return sum;
}
