#include <math.h>
const float RHO   = 1.225f;    // густина повітря, кг/м^3
const float G     = 9.81f;
const float M_KG  = 1.200f;    // злітна маса
const int   NP    = 4;         // гвинтів
const float D_IN  = 10.0f;     // діаметр, дюйми
const float VBAT  = 14.8f;     // 4S
const float FOM   = 0.68f;     // добротність гвинта
const float ETA_M = 0.83f;     // ККД мотора
const float ETA_E = 0.96f;     // ККД ESC

float hover_current() {
    float R   = (D_IN * 0.0254f) / 2.0f;
    float A   = NP * (float)M_PI * R * R;        // сумарна площа дисків, м^2
    float T   = M_KG * G;                         // тяга висіння = вага, Н
    float vi  = sqrtf(T / (2.0f * RHO * A));     // індукована швидкість, м/с
    float Pid = T * vi;                           // ідеальна потужність, Вт (усі гвинти)
    float Pbat = Pid / (FOM * ETA_M * ETA_E);    // потужність із батареї
    float Ibat = Pbat / VBAT;                     // струм із батареї, А
    return Ibat;
}
