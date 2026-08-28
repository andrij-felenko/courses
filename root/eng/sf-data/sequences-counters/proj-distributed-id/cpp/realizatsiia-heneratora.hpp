#include <array>
#include <cstdint>
#include <chrono>
#include <random>
#include <span>
#include <cstring>

struct UuidV7 {
    std::array<uint8_t, 16> bytes{};

    static UuidV7 Generate() noexcept {
        UuidV7 id;
        using namespace std::chrono;
        const auto ms = static_cast<uint64_t>(
            duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count()
        );

        // 48-бітний Unix timestamp у форматі Big-Endian
        id.bytes[0] = static_cast<uint8_t>(ms >> 40);
        id.bytes[1] = static_cast<uint8_t>(ms >> 32);
        id.bytes[2] = static_cast<uint8_t>(ms >> 24);
        id.bytes[3] = static_cast<uint8_t>(ms >> 16);
        id.bytes[4] = static_cast<uint8_t>(ms >> 8);
        id.bytes[5] = static_cast<uint8_t>(ms);

        // Криптографічна випадковість для полів ентропії
        thread_local std::random_device rd;
        thread_local std::mt19937_64 gen(rd());
        const uint64_t r1 = gen();
        const uint64_t r2 = gen();

        std::memcpy(&id.bytes[6], &r1, 8);
        std::memcpy(&id.bytes[14], &r2, 2);

        // Встановлення бітів ver (0111) та var (10)
        id.bytes[6] = (id.bytes[6] & 0x0F) | 0x70;
        id.bytes[8] = (id.bytes[8] & 0x3F) | 0x80;

        return id;
    }
};
