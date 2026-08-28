#include <array>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <format>
#include <expected>
#include <cstring>
#include <cstdint>

struct Uuid {
    std::array<uint8_t, 16> bytes{};

    [[nodiscard]] std::string to_string() const {
        return std::format(
            "{:02x}{:02x}{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}",
            bytes[0], bytes[1], bytes[2], bytes[3],
            bytes[4], bytes[5],
            bytes[6], bytes[7],
            bytes[8], bytes[9],
            bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15]
        );
    }
};

/* Відповідник структури Microsoft GUID */
struct WindowsGuid {
    uint32_t data1;
    uint16_t data2;
    uint16_t data3;
    std::array<uint8_t, 8> data4;
};

class UuidV7Generator {
public:
    UuidV7Generator() : rng_(std::random_device{}()) {}

    [[nodiscard]] Uuid generate() {
        Uuid id{};
        fill_random(id.bytes);

        const auto now = std::chrono::system_clock::now();
        const auto ms_count = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()
        ).count();
        const auto ms = static_cast<uint64_t>(ms_count);

        if (ms == last_ms_) {
            seq_counter_ = (seq_counter_ + 1) & 0x0FFF;
        } else {
            last_ms_ = ms;
            seq_counter_ = (static_cast<uint16_t>(id.bytes[6] << 8) | id.bytes[7]) & 0x0FFF;
        }

        /* Запис 48-бітного Unix timestamp у порядку Big-Endian */
        id.bytes[0] = static_cast<uint8_t>(ms >> 40);
        id.bytes[1] = static_cast<uint8_t>(ms >> 32);
        id.bytes[2] = static_cast<uint8_t>(ms >> 24);
        id.bytes[3] = static_cast<uint8_t>(ms >> 16);
        id.bytes[4] = static_cast<uint8_t>(ms >> 8);
        id.bytes[5] = static_cast<uint8_t>(ms);

        /* Версія 0x7 + 12-бітний субмілісекундний лічильник */
        id.bytes[6] = 0x70 | static_cast<uint8_t>((seq_counter_ >> 8) & 0x0F);
        id.bytes[7] = static_cast<uint8_t>(seq_counter_ & 0xFF);

        /* Варіант RFC 9562: 0b10xxxxxx */
        id.bytes[8] = (id.bytes[8] & 0x3F) | 0x80;

        return id;
    }

    [[nodiscard]] static WindowsGuid to_windows_guid(const Uuid& u) noexcept {
        WindowsGuid g{};
        g.data1 = (static_cast<uint32_t>(u.bytes[0]) << 24) |
                  (static_cast<uint32_t>(u.bytes[1]) << 16) |
                  (static_cast<uint32_t>(u.bytes[2]) << 8)  |
                  (static_cast<uint32_t>(u.bytes[3]));
        g.data2 = (static_cast<uint16_t>(u.bytes[4]) << 8) | static_cast<uint16_t>(u.bytes[5]);
        g.data3 = (static_cast<uint16_t>(u.bytes[6]) << 8) | static_cast<uint16_t>(u.bytes[7]);
        std::memcpy(g.data4.data(), &u.bytes[8], 8);
        return g;
    }

private:
    std::mt19937_64 rng_;
    uint64_t last_ms_ = 0;
    uint16_t seq_counter_ = 0;

    void fill_random(std::array<uint8_t, 16>& arr) {
        auto* ptr = reinterpret_cast<uint64_t*>(arr.data());
        ptr[0] = rng_();
        ptr[1] = rng_();
    }
};
