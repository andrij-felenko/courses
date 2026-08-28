// YUYV (packed 4:2:2): дістати Y,Cb,Cr для пікселя (x,y)
uint8_t *row = base + y * stride;          // stride байтів на рядок
uint8_t *pair = row + (x & ~1) * 2;        // початок пари: (x/2)*4 байти
uint8_t Y  = (x & 1) ? pair[2] : pair[0];  // парний → pair[0], непарний → pair[2]
uint8_t Cb = pair[1];                      // спільні на пару
uint8_t Cr = pair[3];

// NV12 (planar 4:2:0): дві площини в одному буфері
uint8_t *Yp  = base;                        // площина Y: W*H байтів
uint8_t *UVp = base + stride * height;      // напівплощина UV одразу за Y
uint8_t Y  = Yp[y * stride + x];
// один відлік U/V на блок 2×2 → ділимо координати навпіл
uint8_t *uv = UVp + (y >> 1) * stride + (x & ~1);
uint8_t Cb = uv[0];
uint8_t Cr = uv[1];
