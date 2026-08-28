#include <iostream>

#define MAKE_FN_NAME(prefix, name) prefix##_##name

void api_v1_init() {
    std::cout << "Ініціалізація API v1 C++\n";
}

int main() {
    auto* init_ptr = &MAKE_FN_NAME(api_v1, init);
    init_ptr();
    return 0;
}
