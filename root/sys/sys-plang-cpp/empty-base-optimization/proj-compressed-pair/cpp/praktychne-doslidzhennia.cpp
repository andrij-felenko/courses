#include <iostream>
#include <iomanip>

struct EmptyPolicyA {};
struct EmptyPolicyB {};

void inspect_memory_layout() {
    modern::compressed_pair<int*, EmptyPolicyA> compressed_ptr(nullptr, {});

    const void* base_addr = static_cast<const void*>(&compressed_ptr);
    const void* first_addr = static_cast<const void*>(std::addressof(compressed_ptr.first()));
    const void* second_addr = static_cast<const void*>(std::addressof(compressed_ptr.second()));

    std::cout << "Базова адреса пари:   " << base_addr << '\n';
    std::cout << "Адреса першого поля:  " << first_addr << '\n';
    std::cout << "Адреса другого поля:  " << second_addr << '\n';
}
