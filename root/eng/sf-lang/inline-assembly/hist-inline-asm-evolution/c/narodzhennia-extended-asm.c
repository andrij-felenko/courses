/* Контракт Extended Asm у GCC 2.0 (1992 рік) */
int add_extended(int a, int b) {
    int result;
    __asm__ __volatile__ (
        "addl %2, %0"
        : "=r" (result)        /* вихідний операнд */
        : "0" (a), "r" (b)     /* вхідні операнди */
        : "cc"                 /* зіпсовані прапорці */
    );
    return result;
}
