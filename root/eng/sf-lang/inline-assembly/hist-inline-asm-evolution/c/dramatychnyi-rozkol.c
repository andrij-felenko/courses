/* Модель MSVC для 32-розрядної архітектури x86 */
int add_msvc(int a, int b) {
    int res;
    __asm {
        mov eax, a
        add eax, b
        mov res, eax
    }
    return res;
}
