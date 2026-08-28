/* Еквівалент MSVC у C++ */
int add_msvc(int a, int b) noexcept {
    int res = 0;
    __asm {
        mov eax, a
        add eax, b
        mov res, eax
    }
    return res;
}
