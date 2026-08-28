// Шумове число каскаду (формула Фрііса), вхід і вихід — у dB
#include <math.h>

static float db2lin(float db) { return powf(10.0f, db / 10.0f); }
static float lin2db(float x)  { return 10.0f * log10f(x); }

float cascade_nf(float nf1_db, float g1_db, float nf2_db) {
    float F1 = db2lin(nf1_db);
    float G1 = db2lin(g1_db);
    float F2 = db2lin(nf2_db);
    float Ftot = F1 + (F2 - 1.0f) / G1;   // внесок 2-го ділиться на G1
    return lin2db(Ftot);
}
// cascade_nf(2.0f, 20.0f, 8.0f) ≈ 2.14 dB
