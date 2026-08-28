// RGB565: дістати канали з 16-бітного слова
uint16_t px = ((uint16_t*)(base + y*stride))[x];
uint8_t r = (px >> 11) & 0x1F;   // 5 біт  → 0..31
uint8_t g = (px >>  5) & 0x3F;   // 6 біт  → 0..63
uint8_t b =  px        & 0x1F;   // 5 біт  → 0..31

// BGR888: три байти, увага на порядок
uint8_t *p = base + y*stride + x*3;
uint8_t b = p[0], g = p[1], r = p[2];   // ← B перший!

// ARGB8888: чотири байти
uint8_t *p = base + y*stride + (x << 2);
uint8_t a = p[0], r = p[1], g = p[2], b = p[3];
