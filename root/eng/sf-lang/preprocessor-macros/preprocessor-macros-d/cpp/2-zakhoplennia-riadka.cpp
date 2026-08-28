#include <iostream>
#include <cstdlib>

#define CUSTOM_ASSERT(expr) \
    do { \
        if (!(expr)) { \
            std::cerr << "ASSERT FAILED: (" #expr ") at " \
                      << __FILE__ << ":" << __LINE__ << " in " \
                      << __func__ << "()\n"; \
            std::abort(); \
        } \
    } while (0)

int main() {
    int valid_handle = 1;
    CUSTOM_ASSERT(valid_handle != 0);
    std::cout << "Перевірку інваріанта C++ пройдено успішно.\n";
    return 0;
}
