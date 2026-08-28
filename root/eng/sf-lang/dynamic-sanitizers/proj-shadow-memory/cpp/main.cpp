#include <iostream>
#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>
#include <memory>
#include <array>
#include <stdexcept>

enum class ShadowTag : uint8_t {
    Valid = 0x00,
    Redzone = 0xFA,
    Freed = 0xFD
};

class ShadowMemoryTracker {
public:
    static constexpr std::size_t PoolSize = 1024;
    static constexpr std::size_t ShadowSize = PoolSize >> 3;
    static constexpr std::size_t RedzoneSize = 16;

    ShadowMemoryTracker() {
        m_shadow.fill(ShadowTag::Redzone);
    }

    [[nodiscard]] auto allocate(std::size_t payload_size) -> std::span<std::byte> {
        const std::size_t total_size = RedzoneSize + payload_size + RedzoneSize;
        if (m_pool_offset + total_size > PoolSize) {
            throw std::bad_alloc();
        }

        auto* base = &m_pool[m_pool_offset];
        auto* left_rz = base;
        auto* payload = base + RedzoneSize;
        auto* right_rz = payload + payload_size;

        poison_range(left_rz, RedzoneSize, ShadowTag::Redzone);
        unpoison_range(payload, payload_size);
        poison_range(right_rz, RedzoneSize, ShadowTag::Redzone);

        m_pool_offset += total_size;
        return {reinterpret_cast<std::byte*>(payload), payload_size};
    }

    void deallocate(std::span<std::byte> buffer) noexcept {
        if (buffer.empty()) return;
        auto* left_rz = reinterpret_cast<uint8_t*>(buffer.data()) - RedzoneSize;
        const std::size_t total_size = RedzoneSize + buffer.size() + RedzoneSize;
        poison_range(left_rz, total_size, ShadowTag::Freed);
    }

    [[nodiscard]] auto validate_access(const void* addr, std::size_t size = 1) const noexcept -> bool {
        const auto* byte_addr = reinterpret_cast<const uint8_t*>(addr);
        if (byte_addr < m_pool.data() || byte_addr + size > m_pool.data() + PoolSize) {
            std::cerr << "[ASAN-EMU] CRASH: Доступ за межами пам'яті!\n";
            return false;
        }

        const std::size_t s_idx = addr_to_shadow(byte_addr);
        const auto tag = m_shadow[s_idx];

        if (tag == ShadowTag::Valid) {
            return true;
        }
        if (tag == ShadowTag::Redzone) {
            std::cerr << "[ASAN-EMU] CRASH: Порушення межі Redzone (Buffer Overflow)!\n";
            return false;
        }
        if (tag == ShadowTag::Freed) {
            std::cerr << "[ASAN-EMU] CRASH: Доступ до звільненої пам'яті (Use-After-Free)!\n";
            return false;
        }
        return false;
    }

private:
    [[nodiscard]] auto addr_to_shadow(const uint8_t* addr) const noexcept -> std::size_t {
        const auto offset = static_cast<std::size_t>(addr - m_pool.data());
        return offset >> 3;
    }

    void poison_range(const uint8_t* addr, std::size_t size, ShadowTag tag) noexcept {
        const std::size_t start_shadow = addr_to_shadow(addr);
        const std::size_t shadow_bytes = (size + 7) >> 3;
        for (std::size_t i = 0; i < shadow_bytes && (start_shadow + i) < ShadowSize; ++i) {
            m_shadow[start_shadow + i] = tag;
        }
    }

    void unpoison_range(const uint8_t* addr, std::size_t size) noexcept {
        const std::size_t start_shadow = addr_to_shadow(addr);
        const std::size_t full_chunks = size >> 3;
        for (std::size_t i = 0; i < full_chunks; ++i) {
            m_shadow[start_shadow + i] = ShadowTag::Valid;
        }
        if (const std::size_t rem = size & 7; rem > 0) {
            m_shadow[start_shadow + full_chunks] = ShadowTag::Valid;
        }
    }

    alignas(16) std::array<uint8_t, PoolSize> m_pool{};
    std::array<ShadowTag, ShadowSize> m_shadow{};
    std::size_t m_pool_offset{0};
};

int main() {
    ShadowMemoryTracker tracker;
    std::cout << "=== Демонстрація переповнення буфера в C++ ===\n";

    auto buffer = tracker.allocate(10);
    auto* raw_ptr = reinterpret_cast<char*>(buffer.data());

    // Безпечний запис у межах діапазону
    for (std::size_t i = 0; i < buffer.size(); ++i) {
        if (tracker.validate_access(&raw_ptr[i])) {
            raw_ptr[i] = static_cast<char>('A' + i);
        }
    }
    std::cout << "Успішно записано 10 байтів.\n";

    // Спроба переповнення (вихід за межі)
    std::cout << "Спроба запису в raw_ptr[10]:\n";
    if (tracker.validate_access(&raw_ptr[10])) {
        raw_ptr[10] = '!';
    }

    std::cout << "\n=== Демонстрація Use-After-Free в C++ ===\n";
    tracker.deallocate(buffer);
    std::cout << "Буфер звільнено (deallocate).\n";

    std::cout << "Спроба читання з raw_ptr[0]:\n";
    if (tracker.validate_access(&raw_ptr[0])) {
        [[maybe_unused]] char ch = raw_ptr[0];
    }

    return 0;
}
