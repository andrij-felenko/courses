#include <math.h>

const float RHO   = 1.225f;    // густина повітря, кг/м^3
const float G     = 9.81f;     // прискорення вільного падіння
const float R_M   = 0.127f;    // радіус гвинта 10", м
const int   NP    = 4;         // гвинтів
const float FOM   = 0.65f;     // добротність гвинта
const float ETA_M = 0.83f;     // ККД мотора
const float ETA_E = 0.96f;     // ККД регулятора
const float M0_KG = 0.6f;      // фіксована («суха») маса, кг
const float E_WHKG = 180.0f;   // придатна питома енергія LiPo, Вт·год/кг

float endurance_ceiling_min(float e_whkg) {
    float A     = NP * (float)M_PI * R_M * R_M;         // сумарна площа дисків, м^2
    float eta   = FOM * ETA_M * ETA_E;                   // повний ККД тракту висіння
    // стала рами c: P_вис = c · m^1.5,  c = g^1.5 / (sqrt(2ρA)·η)
    float c     = powf(G, 1.5f) / (sqrtf(2.0f * RHO * A) * eta);
    // критична маса й критичний множник kільця
    float mstar = 3.0f * M0_KG;                          // універсальна межа: m* = 3·m0
    float k     = 1.0f / (1.5f * sqrtf(mstar));          // нахил рівно 1
    float e_J   = e_whkg * 3600.0f;                      // Вт·год/кг → Дж/кг
    float t_s   = k * e_J / c;                            // критичний час, с
    return t_s / 60.0f;                                  // → хвилини
}
