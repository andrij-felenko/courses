#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define FLASH_ECC_WORD_SIZE 32 /* 256 бітів для Cortex-M7/M33 */

size_t pad_segment_for_flash_ecc(const uint8_t* in_data, size_t in_size, 
                                 uint8_t* out_padded_buffer, size_t max_out_buf) {
    if (!in_data || in_size == 0 || !out_padded_buffer) return 0;

    size_t remainder = in_size % FLASH_ECC_WORD_SIZE;
    size_t padding = (remainder == 0) ? 0 : (FLASH_ECC_WORD_SIZE - remainder);
    size_t total_padded_size = in_size + padding;

    if (total_padded_size > max_out_buf) return 0;

    /* Копіювання корисних даних */
    memcpy(out_padded_buffer, in_data, in_size);

    /* Заповнення залишку ECC-слова байтами 0xFF */
    if (padding > 0) {
        memset(out_padded_buffer + in_size, 0xFF, padding);
    }

    return total_padded_size;
}
