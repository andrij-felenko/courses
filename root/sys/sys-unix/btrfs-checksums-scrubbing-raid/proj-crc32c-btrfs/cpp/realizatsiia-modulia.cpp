#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <cstddef>
#include <iomanip>

#if defined(__x86_64__) || defined(_M_X64)
#include <nmmintrin.h>
#define HAS_SSE42_CPP 1
#else
#define HAS_SSE42_CPP 0
#endif

namespace btrfs {

class Crc32cCalculator {
public:
    static constexpr std::uint32_t InitialState = 0xFFFFFFFFU;
    static constexpr std::uint32_t XorMask = 0xFFFFFFFFU;

    // Типобезпечне обчислення хешу через std::span без виділення пам'яті
    [[nodiscard]] static std::uint32_t calculate(std::span<const std::byte> buffer, 
                                                std::uint32_t initial = InitialState) noexcept 
    {
        std::uint64_t crc = initial;
        const auto* ptr = reinterpret_cast<const std::uint8_t*>(buffer.data());
        std::size_t length = buffer.size();

#if HAS_SSE42_CPP
        // 1. Вирівнювання адреси буфера
        while (length > 0 && (reinterpret_cast<std::uintptr_t>(ptr) & 7)) {
            crc = _mm_crc32_u8(static_cast<std::uint32_t>(crc), *ptr++);
            --length;
        }

        // 2. Конвеєрне обчислення блоків по 8 байтів
        const auto* p64 = reinterpret_cast<const std::uint64_t*>(ptr);
        std::size_t blocks = length / sizeof(std::uint64_t);
        for (std::size_t i = 0; i < blocks; ++i) {
            crc = _mm_crc32_u64(crc, p64[i]);
        }

        // 3. Залишкові байти
        ptr = reinterpret_cast<const std::uint8_t*>(p64 + blocks);
        length %= sizeof(std::uint64_t);
        while (length > 0) {
            crc = _mm_crc32_u8(static_cast<std::uint32_t>(crc), *ptr++);
            --length;
        }
#else
        for (std::size_t i = 0; i < length; ++i) {
            crc ^= ptr[i];
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc & 1) ? ((crc >> 1) ^ 0x82F63B78U) : (crc >> 1);
            }
        }
#endif

        return static_cast<std::uint32_t>(crc) ^ XorMask;
    }
};

} // namespace btrfs

int main()
{
    // Створення тестового сектора 4 КіБ у RAII-контейнері
    std::vector<std::byte> sector(4096);
    for (std::size_t i = 0; i < sector.size(); ++i) {
        sector[i] = static_cast<std::byte>(i & 0xFF);
    }

    std::uint32_t checksum = btrfs::Crc32cCalculator::calculate(sector);

    std::cout << "Обчислено CRC32c (C++ RAII/std::span): 0x"
              << std::hex << std::uppercase << std::setw(8) << std::setfill('0')
              << checksum << std::endl;

    return 0;
}
