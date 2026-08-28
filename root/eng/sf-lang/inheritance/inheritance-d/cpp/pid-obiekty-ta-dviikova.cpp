#include <iostream>
#include <cstddef>

class Base {
public:
    int id{42};
    int flags{0x01};
};

class Derived : public Base {
public:
    double score{99.5};
    int extra{7};
};

void print_base(const Base* b) {
    std::cout << "Base id: " << b->id << ", flags: 0x" << std::hex << b->flags << std::dec << "\n";
}

int main() {
    Derived d;

    // Upcast: компілятор не генерує жодної машинної інструкції зміщення
    const Base* b_ptr = &d;
    print_base(b_ptr);

    std::cout << "Адреса Derived: " << static_cast<const void*>(&d) << "\n";
    std::cout << "Адреса Base:    " << static_cast<const void*>(b_ptr) << "\n";
    std::cout << "Різниця адрес:  " << reinterpret_cast<uintptr_t>(b_ptr) - reinterpret_cast<uintptr_t>(&d) << " B\n";
    return 0;
}
