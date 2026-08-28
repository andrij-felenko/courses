#include <math.h>
#include <stddef.h>

// дБ → рази (за потужністю)
static float db2lin(float db) { return powf(10.0f, db / 10.0f); }
// рази → дБ
static float lin2db(float x)  { return 10.0f * log10f(x); }

// Повний коефіцієнт шуму ланцюга за формулою Фрііса.
// nf_db[i], gain_db[i] — коефіцієнт шуму й підсилення i-ї ланки В ДЕЦИБЕЛАХ.
// n — число ланок. Повертає повний NF тракту в дБ.
float cascade_nf_db(const float *nf_db, const float *gain_db, size_t n)
{
    if (n == 0) return 0.0f;

    float F_total    = db2lin(nf_db[0]);   // перша ланка входить ЦІЛОЮ, без поділу
    float gain_accum = db2lin(gain_db[0]); // добуток підсилень УСІХ ланок перед наступною

    for (size_t i = 1; i < n; ++i) {
        float Fi = db2lin(nf_db[i]);
        // надлишок (Fᵢ − 1), поділений на добуток підсилень усіх попередніх
        F_total   += (Fi - 1.0f) / gain_accum;
        gain_accum *= db2lin(gain_db[i]);   // долучаємо підсилення цієї ланки до добутку
    }
    return lin2db(F_total);
}
