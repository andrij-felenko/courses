#include <iostream>

#if defined(__has_cpp_attribute)
    #if __has_cpp_attribute(nodiscard) >= 201907L
        #define SAFE_CHECK [[nodiscard("Ігнорування результату неприпустиме")]]
    #elif __has_cpp_attribute(nodiscard)
        #define SAFE_CHECK [[nodiscard]]
    #else
        #define SAFE_CHECK
    #endif
#else
    #define SAFE_CHECK
#endif

SAFE_CHECK int compute_status() {
    return 1;
}

int main() {
    std::cout << "Статус обчислення: " << compute_status() << "\n";
    return 0;
}
