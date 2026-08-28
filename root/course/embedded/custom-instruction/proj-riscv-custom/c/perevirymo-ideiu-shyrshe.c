// CRC-крок: rs1 = байт даних, rs2 = поточний CRC -> rd = новий CRC.
static inline uint8_t crc8_step_ci(uint8_t data, uint8_t crc) {
    uint32_t r;
    asm volatile (
        ".insn r 0x0B, 1, 0, %0, %1, %2"  // funct3=1 -> ІНША команда блоку!
        : "=r" (r)
        : "r" ((uint32_t)data), "r" ((uint32_t)crc)
    );
    return (uint8_t)r;
}
