#include <stdint.h>
#include <stddef.h>

// Формування пакету запису в регістр Debug Port (DP) для CMSIS-DAP
size_t build_dp_write_request(uint8_t *buffer, uint8_t reg_addr, uint32_t data) {
    buffer[0] = 0x05; // ID команди DAP_Transfer
    buffer[1] = 0x00; // Індекс DAP-пристрою
    buffer[2] = 0x01; // Кількість операцій у пакеті = 1
    
    // Бітова маска: Direction=0 (Write), Port=0 (DP), Address A[2:3]
    buffer[3] = (uint8_t)(reg_addr & 0x0C);
    
    // Запис 32-бітного слова у форматі Little-Endian
    buffer[4] = (uint8_t)(data & 0xFF);
    buffer[5] = (uint8_t)((data >> 8) & 0xFF);
    buffer[6] = (uint8_t)((data >> 16) & 0xFF);
    buffer[7] = (uint8_t)((data >> 24) & 0xFF);
    
    return 8; // Розмір сформованого пакета в байтах
}
