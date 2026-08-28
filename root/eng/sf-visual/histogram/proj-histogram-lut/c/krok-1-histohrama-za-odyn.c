#include <stdint.h>
#include <string.h>

// img    — буфер пікселів (8 біт на піксель, рядок за рядком)
// n      — кількість пікселів (width * height)
// hist   — вихід: 256 лічильників
void build_histogram(const uint8_t *img, uint32_t n, uint32_t hist[256])
{
    memset(hist, 0, 256 * sizeof(uint32_t));   // обнулити кошики
    for (uint32_t i = 0; i < n; ++i)
        hist[img[i]]++;                        // піксель сам каже, який кошик рахувати
}
