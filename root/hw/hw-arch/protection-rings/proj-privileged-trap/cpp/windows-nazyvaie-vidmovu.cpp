// MSVC, x64 C++: структурна обробка виключень (SEH) у C++ коді
#include <iostream>
#include <windows.h>

extern "C" void do_hlt();

void test_privileged_seh() {
    __try {
        do_hlt();
    }
    __except (GetExceptionCode() == EXCEPTION_PRIV_INSTRUCTION
                  ? EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH) {
        std::cout << "процесор відмовив: привілейована команда (EXCEPTION_PRIV_INSTRUCTION)\n";
    }
}
