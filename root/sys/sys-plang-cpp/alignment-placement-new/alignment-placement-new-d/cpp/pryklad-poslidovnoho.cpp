#include <memory>
#include <cstddef>
#include <iostream>

int main() {
    alignas(std::max_align_t) std::byte arena[1024];
    
    void* current_ptr = arena;
    std::size_t space_left = sizeof(arena);

    // 1. Виділяємо місце під int16_t (alignof = 2, sizeof = 2)
    void* p1 = std::align(alignof(int16_t), sizeof(int16_t), current_ptr, space_left);
    int16_t* val1 = ::new (p1) int16_t(100);
    // Зсуваємо вказівник за зайнятий об'єкт
    current_ptr = static_cast<std::byte*>(p1) + sizeof(int16_t);
    space_left -= sizeof(int16_t);

    // 2. Виділяємо місце під double (alignof = 8, sizeof = 8)
    void* p2 = std::align(alignof(double), sizeof(double), current_ptr, space_left);
    double* val2 = ::new (p2) double(3.14159);
    current_ptr = static_cast<std::byte*>(p2) + sizeof(double);
    space_left -= sizeof(double);

    std::cout << "int16_t розміщено за адресою: " << val1 << "\n";
    std::cout << "double  розміщено за адресою: " << val2 << "\n";
    std::cout << "Відступ між об'єктами: " 
              << (reinterpret_cast<std::byte*>(val2) - reinterpret_cast<std::byte*>(val1)) 
              << " байтів\n";

    // Ручне звільнення
    val2->~double();
    val1->~int16_t();
}
