#ifndef GRAY_CODE_H
#define GRAY_CODE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Перетворення 32-бітного коду Ґрея у двійковий формат (Binary)
 * @param gray Значення у коді Ґрея
 * @return Двійкове значення
 */
static inline uint32_t gray_to_binary32(uint32_t gray) {
    gray ^= (gray >> 1);
    gray ^= (gray >> 2);
    gray ^= (gray >> 4);
    gray ^= (gray >> 8);
    gray ^= (gray >> 16);
    return gray;
}

/**
 * @brief Перетворення 64-бітного коду Ґрея у двійковий формат (Binary)
 * @param gray Значення у коді Ґрея
 * @return Двійкове значення
 */
static inline uint64_t gray_to_binary64(uint64_t gray) {
    gray ^= (gray >> 1);
    gray ^= (gray >> 2);
    gray ^= (gray >> 4);
    gray ^= (gray >> 8);
    gray ^= (gray >> 16);
    gray ^= (gray >> 32);
    return gray;
}

/**
 * @brief Перетворення 32-бітного двійкового числа у код Ґрея
 * @param binary Двійкове значення
 * @return Значення у коді Ґрея
 */
static inline uint32_t binary_to_gray32(uint32_t binary) {
    return binary ^ (binary >> 1);
}

#ifdef __cplusplus
}
#endif

#endif /* GRAY_CODE_H */
