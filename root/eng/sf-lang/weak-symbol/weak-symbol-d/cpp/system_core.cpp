// system_core.cpp — ядро системи зі слабким посиланням на C++20
#include <iostream>
#include <memory>
#include <cstddef>

extern "C" {
    // Слабке посилання на необов'язковий C-інтерфейс аудиту
    [[gnu::weak]] void memory_audit_hook(const void* ptr, std::size_t size) noexcept;
}

namespace core::memory {

void* allocate_buffer(std::size_t size)
{
    void* ptr = std::malloc(size);
    if (!ptr) {
        return nullptr;
    }

    // Перевірка адреси слабкого посилання
    if (memory_audit_hook != nullptr) {
        memory_audit_hook(ptr, size);
    }

    return ptr;
}

} // namespace core::memory
