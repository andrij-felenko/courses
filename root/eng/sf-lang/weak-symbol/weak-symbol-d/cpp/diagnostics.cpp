// diagnostics.cpp — необов'язковий модуль на C++20
#include <iostream>
#include <cstddef>

extern "C" {

void memory_audit_hook(const void* ptr, std::size_t size) noexcept
{
    std::cout << "[AUDIT] Виділено " << size << " байтів за адресою " << ptr << '\n';
}

} // extern "C"
