#include <stdint.h>
#include <stdbool.h>

// Декодування усіченого коду Ґрея для довільної парної роздільності M
bool decode_truncated_gray(uint32_t gray_raw, uint32_t M, uint32_t n_bits, uint32_t *out_binary) {
    uint32_t K = ((1U << n_bits) - M) / 2;
    uint32_t b_shifted = gray_to_binary(gray_raw);
    
    // Перевірка цілісності діапазону
    if (b_shifted < K || b_shifted >= (K + M)) {
        return false; // Помилка: код поза межами робочої шкали
    }
    
    *out_binary = b_shifted - K;
    return true;
}
