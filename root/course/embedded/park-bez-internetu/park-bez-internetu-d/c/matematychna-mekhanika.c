/* Порівняння бітових масок для генерації запиту відсутніх чанків */
int find_first_missing_chunk(const uint8_t *local_mask, const uint8_t *remote_mask, int mask_len_bytes) {
    for (int byte_idx = 0; byte_idx < mask_len_bytes; byte_idx++) {
        uint8_t needed = remote_mask[byte_idx] & (~local_mask[byte_idx]);
        if (needed != 0) {
            for (int bit_idx = 0; bit_idx < 8; bit_idx++) {
                if (needed & (1 << bit_idx)) {
                    return (byte_idx * 8) + bit_idx;
                }
            }
        }
    }
    return -1; /* Нічого завантажувати не потрібно */
}
