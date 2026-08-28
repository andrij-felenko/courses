#define CACHE_LINE  32u
#define ALIGN_UP(n, a)  (((n) + (a) - 1u) / (a) * (a))   /* округлення вгору */

size_t need  = 100;                       /* корисних байтів */
size_t alloc = ALIGN_UP(need, CACHE_LINE);
/* alloc = (100 + 31) / 32 * 32 = 131 / 32 * 32 = 4 * 32 = 128 байтів */

uint8_t *buf = heap_caps_aligned_alloc(   /* початок — на межі 32 Б */
                   CACHE_LINE, alloc,
                   MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA);
