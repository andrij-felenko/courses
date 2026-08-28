#include "vad.h"

// Дві прикмети кадру за один прохід: сума квадратів (енергія) і нуль-перетини.
// Гарячий цикл — строго в цілих, без жодного float.
typedef struct { uint64_t sumsq; uint16_t zcr; } frame_feat_t;

static frame_feat_t frame_features(const int16_t *x, uint16_t n)
{
    uint64_t sumsq = 0;
    uint16_t zcr   = 0;
    bool prev_nonneg = (x[0] >= 0);          // знак першого відліку

    for (uint16_t i = 0; i < n; i++) {
        int32_t s = x[i];                    // РОЗШИРЮЄМО до множення — інакше
        sumsq += (uint64_t)(s * s);          // int16·int16 переповниться в int16

        if (i > 0) {                         // зміна знаку ⟺ перетин нуля
            bool nonneg = (x[i] >= 0);
            if (nonneg != prev_nonneg) zcr++;
            prev_nonneg = nonneg;
        }
    }
    frame_feat_t f = { sumsq, zcr };
    return f;
}
