/* Інференс квантованої INT8-мережі DS-CNN над матрицею мел-ознак.
 *
 * Мережа має вигляд, звичний для keyword spotting на мікроконтролері:
 *
 *   вхід 40×32×1  → conv 3×3, крок 2, 4 канали, ReLU   → 20×16×4
 *                 → depthwise 3×3, крок 2, ReLU        → 10×8×4
 *                 → pointwise 1×1, 4→8, ReLU           → 10×8×8
 *                 → depthwise 3×3, крок 1, ReLU        → 10×8×8
 *                 → pointwise 1×1, 8→8, ReLU           → 10×8×8
 *                 → global average pool                → 8
 *                 → fully connected 8→4                → 4 логіти
 *
 * Роздільна згортка (depthwise + pointwise) робить те саме, що звичайна
 * 3×3, але множень у неї в 9 разів менше при тій самій кількості каналів —
 * саме тому вона й дожила до мікроконтролерів.
 */
#ifndef DSCNN_H
#define DSCNN_H

#include <stdint.h>

#include "acoustic_detector.h"

/* Параметри переквантування шару: множник у Q31 і правий зсув.
 * Разом вони кодують дробовий масштаб M = multiplier · 2^-31 · 2^-shift,
 * на який множиться int32-акумулятор, щоб повернутися в int8. */
typedef struct {
    int32_t multiplier;
    uint8_t shift;
} dscnn_requant_t;

/* Проганяє матрицю ознак крізь мережу й повертає розквантовані логіти. */
void dscnn_run(const int8_t features[AED_NUM_FRAMES][AED_MEL_BINS],
               float logits[AED_NUM_CLASSES]);

#endif /* DSCNN_H */
