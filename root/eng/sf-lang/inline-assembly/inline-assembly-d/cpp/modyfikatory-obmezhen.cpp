/* C++ версія безпечного комбінування операндів */
uint32_t safe_combine(uint32_t a, uint32_t b) noexcept {
    uint32_t result = 0;
    asm (
        "movl %1, %0\n\t"
        "addl %2, %0"
        : "=&r" (result)
        : "r" (a), "r" (b)
    );
    return result;
}
