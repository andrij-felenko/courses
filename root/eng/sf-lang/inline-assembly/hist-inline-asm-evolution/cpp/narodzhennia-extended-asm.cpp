/* Еквівалент на C++ */
int add_extended(int a, int b) noexcept {
    int result = 0;
    asm volatile (
        "addl %2, %0"
        : "=r" (result)
        : "0" (a), "r" (b)
        : "cc"
    );
    return result;
}
