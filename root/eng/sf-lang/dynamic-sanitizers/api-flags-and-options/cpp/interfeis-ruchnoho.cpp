#include <sanitizer/asan_interface.h>
#include <array>
#include <cstddef>
#include <span>
#include <stdexcept>

class CustomStackArena {
public:
    static constexpr std::size_t Capacity = 2048;

    CustomStackArena() noexcept {
        // Отруюємо всю область пам'яті арени при створенні
        ASAN_POISON_MEMORY_REGION(m_storage.data(), m_storage.size());
    }

    ~CustomStackArena() noexcept {
        // Знімаємо отруєння перед знищенням об'єкта
        ASAN_UNPOISON_MEMORY_REGION(m_storage.data(), m_storage.size());
    }

    [[nodiscard]] auto allocate(std::size_t size) -> std::span<std::byte> {
        if (m_offset + size > Capacity) {
            throw std::bad_alloc();
        }
        auto* ptr = &m_storage[m_offset];
        m_offset += size;
        // Дозволяємо доступ лише до виділеного діапазону
        ASAN_UNPOISON_MEMORY_REGION(ptr, size);
        return {reinterpret_cast<std::byte*>(ptr), size};
    }

private:
    alignas(16) std::array<uint8_t, Capacity> m_storage{};
    std::size_t m_offset{0};
};
