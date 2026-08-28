// popcount через .insn: ми диктуємо ТІЛЬКИ опкод/funct,
// а які саме регістри — обирає компілятор через обмеження.
static inline uint32_t popcount_ci(uint32_t x) {
    uint32_t r;
    asm volatile (
        ".insn r 0x0B, 0, 0, %0, %1, x0"   // opcode=0x0B funct3=0 funct7=0
        : "=r" (r)        // %0 -> rd : будь-який регістр, СЮДИ запишеться
        : "r"  (x)        // %1 -> rs1: будь-який регістр зі значенням x
    );                    // rs2 не потрібен -> x0 (нульовий регістр)
    return r;
}
