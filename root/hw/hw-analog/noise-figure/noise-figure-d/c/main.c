#include <math.h>

// дБ → рази
static float db2lin(float db) { return powf(10.0f, db / 10.0f); }
// рази → дБ
static float lin2db(float x)  { return 10.0f * log10f(x); }

float F1 = db2lin(1.0f);    // NF LNA: 1 дБ  → F₁ ≈ 1.259
float G1 = db2lin(20.0f);   // підсилення LNA: 20 дБ → G₁ = 100
float F2 = db2lin(10.0f);   // NF змішувача: 10 дБ → F₂ = 10

// формула Фрііса для двох каскадів
float F  = F1 + (F2 - 1.0f) / G1;   // 1.259 + 9/100 = 1.349
float NF = lin2db(F);               // 10·log₁₀(1.349) ≈ 1.30 дБ
