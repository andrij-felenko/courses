#include <math.h>
#include <stdint.h>

typedef struct { float u, v; int ok; } Flow;   // ok=0 → точка ненадійна

// LK по вікну (2*R+1)×(2*R+1) навколо (x,y). tau — поріг на менше власне число.
static Flow lk_flow(const uint8_t *prev, const uint8_t *curr,
                    int W, int x, int y, int R, float tau)
{
    // елементи структурного тензора AᵀA і правого вектора Aᵀb
    float Axx = 0, Axy = 0, Ayy = 0;   // Σ Iₓ², Σ IₓIᵧ, Σ Iᵧ²
    float bx  = 0, by  = 0;            // Σ IₓIₜ, Σ IᵧIₜ

    for (int dy = -R; dy <= R; dy++) {
        for (int dx = -R; dx <= R; dx++) {
            int px = x + dx, py = y + dy;
            // просторовий градієнт — центральні різниці по поточному кадру
            float Ix = 0.5f * ((float)curr[py*W + px+1] - (float)curr[py*W + px-1]);
            float Iy = 0.5f * ((float)curr[(py+1)*W + px] - (float)curr[(py-1)*W + px]);
            // часова похідна — різниця між кадрами в тій самій точці
            float It = (float)curr[py*W + px] - (float)prev[py*W + px];

            Axx += Ix*Ix;   Axy += Ix*Iy;   Ayy += Iy*Iy;
            bx  += Ix*It;   by  += Iy*It;
        }
    }

    Flow f = { 0.0f, 0.0f, 0 };

    // надійність: визначник і слід тензора → менше власне число λ₂
    float det   = Axx*Ayy - Axy*Axy;
    float trace = Axx + Ayy;
    // λ₂ = (trace − √(trace² − 4·det)) / 2  — менший з двох власних чисел
    float disc  = trace*trace - 4.0f*det;
    if (disc < 0.0f) disc = 0.0f;
    float lambda_min = 0.5f * (trace - sqrtf(disc));
    if (lambda_min < tau || det < 1e-6f) return f;   // майже вироджена → відкинути

    // розв'язок 2×2:  AᵀA · w = −Aᵀb  →  w = −(AᵀA)⁻¹ · Aᵀb
    f.u = -( Ayy*bx - Axy*by) / det;
    f.v = -(-Axy*bx + Axx*by) / det;
    f.ok = 1;
    return f;
}
