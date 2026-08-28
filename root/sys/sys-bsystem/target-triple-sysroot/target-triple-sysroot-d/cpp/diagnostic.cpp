// diagnostic.cpp - перевірка цільової архітектури та розмірів типів
#include <iostream>
#include <string_view>
#include <cstdint>
#include <sys/types.h>

namespace target_info {
    constexpr std::string_view get_arch_name() noexcept {
#if defined(__x86_64__) || defined(_M_X64)
        return "x86_64 (64-bit AMD/Intel)";
#elif defined(__aarch64__)
        return "AArch64 (64-bit ARMv8-A)";
#elif defined(__arm__)
        return "ARM (32-bit)";
#elif defined(__riscv)
        return "RISC-V";
#else
        return "Невідома цільова архітектура";
#endif
    }

    constexpr std::string_view get_endianness() noexcept {
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
        return "Little-Endian";
#elif defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
        return "Big-Endian";
#else
        return "Невідомий порядок байтів";
#endif
    }
}

int main() {
    std::cout << "=== ДІАГНОСТИКА ЦІЛЬОВОЇ ПЛАТФОРМИ ===\n";
    std::cout << "Архітектура CPU: " << target_info::get_arch_name() << "\n";
    std::cout << "Порядок байтів:  " << target_info::get_endianness() << "\n";
    std::cout << "Розмір void*:    " << sizeof(void*) << " байтів\n";
    std::cout << "Розмір long:     " << sizeof(long) << " байтів\n";
    std::cout << "Розмір time_t:   " << sizeof(time_t) << " байтів\n";
    std::cout << "Розмір off_t:    " << sizeof(off_t) << " байтів\n";

    return 0;
}
