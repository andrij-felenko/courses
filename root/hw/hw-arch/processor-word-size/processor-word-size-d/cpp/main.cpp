#include <iostream>
#include <cstdint>
#include <cstddef>

struct MemoryBlock {
    int id;              // 4 байти
    long tag;            // 4 байти в Windows LLP64, але 8 байтів у Linux LP64!
    void* payload;       // 8 байтів на обох 64-бітних системах
};

int main() {
    std::cout << "Розмір int:       " << sizeof(int) << " байтів\n";
    std::cout << "Розмір long:      " << sizeof(long) << " байтів\n";
    std::cout << "Розмір void*:     " << sizeof(void*) << " байтів\n";
    std::cout << "Розмір uintptr_t: " << sizeof(std::uintptr_t) << " байтів\n";
    std::cout << "Розмір структури: " << sizeof(MemoryBlock) << " байтів\n";
    std::cout << "Зміщення payload: " << offsetof(MemoryBlock, payload) << " байтів\n";

    // ПРАВИЛЬНО: статичний контроль розрядності покажчика
    static_assert(sizeof(std::uintptr_t) == sizeof(void*), "uintptr_t must match pointer size");

    void* ptr = reinterpret_cast<void*>(0x123456789ABCDEF0ULL);
    auto p_safe = reinterpret_cast<std::uintptr_t>(ptr);
    std::cout << "Безпечна адреса:  0x" << std::hex << p_safe << '\n';
    return 0;
}
