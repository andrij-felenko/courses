#include <stdint.h>
#include <stddef.h>

/* Прототип внутрішнього генератора мутацій LibFuzzer */
size_t LLVMFuzzerMutate(uint8_t *data, size_t size, size_t max_size);

/* Кастомний мутатор зі збереженням коректності заголовка та CRC */
size_t LLVMFuzzerCustomMutator(uint8_t *data, size_t size, size_t max_size, unsigned int seed) {
    /* 1. Застосовуємо стандартні мутації LibFuzzer */
    size_t mutated_size = LLVMFuzzerMutate(data, size, max_size);
    if (mutated_size < (HEADER_SIZE + CRC_SIZE)) {
        return mutated_size;
    }

    /* 2. Якщо знайдено маркер кадру, коригуємо заголовок та перераховуємо CRC */
    if (data[0] == FRAME_MAGIC_BYTE) {
        uint8_t payload_len = data[2];
        if (payload_len <= MAX_PAYLOAD_SIZE && (HEADER_SIZE + (size_t)payload_len + CRC_SIZE) <= mutated_size) {
            uint16_t crc = crc16_ccitt(&data[1], (HEADER_SIZE - 1) + payload_len);
            size_t crc_pos = HEADER_SIZE + payload_len;
            data[crc_pos] = (uint8_t)(crc & 0xFF);
            data[crc_pos + 1] = (uint8_t)((crc >> 8) & 0xFF);
        }
    }

    return mutated_size;
}
