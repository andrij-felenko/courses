/* diagnostic.c - перевірка цільової архітектури та розмірів типів */
#include <stdio.h>
#include <stdint.h>
#include <sys/types.h>

int main(void) {
    printf("=== ДІАГНОСТИКА ЦІЛЬОВОЇ ПЛАТФОРМИ ===\n");

#if defined(__x86_64__) || defined(_M_X64)
    printf("Архітектура CPU: x86_64 (64-bit AMD/Intel)\n");
#elif defined(__aarch64__)
    printf("Архітектура CPU: AArch64 (64-bit ARMv8-A)\n");
#elif defined(__arm__)
    printf("Архітектура CPU: ARM (32-bit)\n");
#elif defined(__riscv)
    printf("Архітектура CPU: RISC-V (%d-bit)\n", __riscv_xlen);
#else
    printf("Архітектура CPU: Невідома цільова архітектура\n");
#endif

#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    printf("Порядок байтів: Little-Endian\n");
#elif defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    printf("Порядок байтів: Big-Endian\n");
#endif

    printf("Розмір void*:   %zu байтів\n", sizeof(void*));
    printf("Розмір long:    %zu байтів\n", sizeof(long));
    printf("Розмір time_t:  %zu байтів\n", sizeof(time_t));
    printf("Розмір off_t:   %zu байтів\n", sizeof(off_t));

    return 0;
}
