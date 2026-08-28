#include <iostream>
#include <array>
#include <cstdint>
#include <cstring>
#include <format>
#include <algorithm>
#include <span>

template <size_t Capacity>
class GuardedBuffer {
private:
    static constexpr uint64_t HeadCanaryValue = 0xDEADBEEFCAFE0001ULL;
    static constexpr uint64_t TailCanaryValue = 0xDEADBEEFCAFE0002ULL;

    uint64_t head_canary_{HeadCanaryValue};
    std::array<char, Capacity> storage_{};
    uint64_t tail_canary_{TailCanaryValue};

public:
    GuardedBuffer() = default;

    [[nodiscard]] bool is_valid() const noexcept {
        return head_canary_ == HeadCanaryValue && tail_canary_ == TailCanaryValue;
    }

    [[nodiscard]] uint64_t tail_canary() const noexcept {
        return tail_canary_;
    }

    // Безпечний ідіоматичний запис через std::span
    bool write_safe(std::span<const char> src) noexcept {
        if (src.size() > Capacity) {
            return false;
        }
        std::copy(src.begin(), src.end(), storage_.begin());
        return true;
    }

    // Небезпечний запис для демонстрації роботи канарки
    void write_raw_unchecked(const char* src, size_t len) noexcept {
        std::memcpy(storage_.data(), src, len);
    }
};

int main() {
    GuardedBuffer<64> buffer;

    std::array<char, 80> attack_payload{};
    attack_payload.fill('A');

    std::cout << "[*] Запис 80 байтів у захищений буфер розміром 64 байти...\n";
    buffer.write_raw_unchecked(attack_payload.data(), attack_payload.size());

    if (!buffer.is_valid()) {
        std::cout << std::format("[АЛАРМ] Пошкодження пам'яті виявлено! Tail Canary = 0x{:X}\n",
                                 buffer.tail_canary());
    } else {
        std::cout << "[OK] Цілісність буфера збережено.\n";
    }
    return 0;
}
