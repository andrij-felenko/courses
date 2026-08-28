#include <math.h>
#include <stdint.h>

typedef struct { float u, v; float mag; } FlowN;  // нормальний потік у точці

// градієнт і часова похідна в пікселі (x,y); нормальна складова потоку
static FlowN normal_flow(const uint8_t *prev, const uint8_t *curr,
                         int W, int x, int y)
{
    // центральні різниці по поточному кадру → просторовий градієнт
    float Ix = 0.5f * ((float)curr[y*W + x+1] - (float)curr[y*W + x-1]);
    float Iy = 0.5f * ((float)curr[(y+1)*W + x] - (float)curr[(y-1)*W + x]);
    // різниця між кадрами в тій самій точці → часова похідна
    float It = (float)curr[y*W + x] - (float)prev[y*W + x];

    float g2 = Ix*Ix + Iy*Iy;              // квадрат модуля градієнта
    FlowN f = { 0.0f, 0.0f, 0.0f };
    if (g2 < 1.0f) return f;               // немає градієнта — потік невизначений

    // в'язь Ix·u + Iy·v + It = 0 дає ЛИШЕ рух уздовж градієнта (нормальний):
    //   (u,v) = -It · (Ix,Iy) / |∇I|²
    f.u = -It * Ix / g2;
    f.v = -It * Iy / g2;
    f.mag = fabsf(It) / sqrtf(g2);         // довжина нормальної складової
    return f;
}
