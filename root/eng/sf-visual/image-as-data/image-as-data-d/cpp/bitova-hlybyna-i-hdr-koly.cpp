// Побудувати LUT 10-біт → 8-біт із гамою (раз на старті)
// out = 255 · (in/1023)^(1/γ),  γ≈2.2 — типова гама дисплея
#include <math.h>
static uint8_t lut10to8[1024];

static void build_tonemap_lut(float gamma) {
    for (int i = 0; i < 1024; ++i) {
        float norm = i / 1023.0f;                 // 0..1
        float mapped = powf(norm, 1.0f / gamma);  // підняти тіні
        int v = (int)(mapped * 255.0f + 0.5f);    // у 0..255 з округленням
        lut10to8[i] = v > 255 ? 255 : (uint8_t)v;
    }
}
// у гарячому циклі — лише дешеве звертання до таблиці:
//   uint8_t shown = lut10to8[ raw10 & 0x3FF ];
