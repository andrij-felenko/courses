#include <stdint.h>
#include <math.h>
#define R 2                       /* радіус вікна: 5x5 */
/* білатеральний фільтр одного каналу uint8; ss — просторова сигма, sr — яскравісна */
void bilateral(const uint8_t *src, uint8_t *dst, int w, int h,
               float ss, float sr){
    float gs[2*R+1][2*R+1];                       /* просторові ваги наперед */
    for (int dy = -R; dy <= R; ++dy)
        for (int dx = -R; dx <= R; ++dx)
            gs[dy+R][dx+R] = expf(-(dx*dx + dy*dy) / (2.0f*ss*ss));
    for (int y = 0; y < h; ++y)
        for (int x = 0; x < w; ++x){
            float wsum = 0.0f, acc = 0.0f;
            int   c = src[(size_t)y*w + x];        /* яскравість центру */
            for (int dy = -R; dy <= R; ++dy)
                for (int dx = -R; dx <= R; ++dx){
                    int yi = y+dy, xi = x+dx;
                    if (yi < 0 || yi >= h || xi < 0 || xi >= w) continue;
                    int   p  = src[(size_t)yi*w + xi];
                    int   d  = p - c;                          /* різниця яскравості */
                    float gr = expf(-(float)(d*d) / (2.0f*sr*sr));  /* яскравісна вага */
                    float ww = gs[dy+R][dx+R] * gr;            /* добуток двох ваг */
                    acc  += ww * p;
                    wsum += ww;
                }
            dst[(size_t)y*w + x] = (uint8_t)(acc / wsum + 0.5f);
        }
}
