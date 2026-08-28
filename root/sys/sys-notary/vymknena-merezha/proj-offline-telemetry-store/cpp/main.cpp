#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <concepts>
#include <algorithm>

namespace telemetry {

inline constexpr uint32_t kFlashSectorSize = 4096;
inline constexpr uint32_t kFlashSectorHeaderSize = 16;
inline constexpr uint32_t kSectorMagic = 0x53464C53; // 'SFLS'
inline constexpr uint16_t kRecordMagic = 0xAA55;

enum class State : uint8_t {
    Erased = 0xFF,
    Allocated = 0xFE,
    Committed = 0xFC,
    Dispatched = 0x00
};

enum class BufferError : uint8_t {
    HalError,
    BufferFull,
    InvalidRecord,
    CrcMismatch,
    Unmounted
};

struct SectorHeader {
    uint32_t magic{kSectorMagic};
    uint32_t sequence_num{0};
    uint32_t erase_count{0};
    State state{State::Erased};
    uint8_t reserved{0xFF};
    uint16_t header_crc{0};
};

struct Sample {
    uint32_t timestamp{0};
    int32_t temperature_c_x100{0};
    uint32_t pressure_pa{0};
    uint16_t battery_mv{0};
    uint32_t pulse_count{0};
};

/* Концепт апаратного Flash-драйвера */
template <typename T>
concept FlashDriver = requires(T driver, uint32_t addr, std::span<const std::byte> wbuf, std::span<std::byte> rbuf) {
    { driver.read(addr, rbuf) } -> std::same_as<bool>;
    { driver.write(addr, wbuf) } -> std::same_as<bool>;
    { driver.erase_sector(addr) } -> std::same_as<bool>;
};

/* Утилітарний клас контрольних сум */
class Checksum {
public:
    static constexpr uint32_t crc32(std::span<const std::byte> data, uint32_t crc = 0xFFFFFFFF) noexcept {
        crc = ~crc;
        for (auto b : data) {
            crc ^= static_cast<uint8_t>(b);
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
            }
        }
        return ~crc;
    }

    static constexpr uint16_t crc16(std::span<const std::byte> data, uint16_t crc = 0xFFFF) noexcept {
        for (auto b : data) {
            crc ^= static_cast<uint16_t>(b) << 8;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc & 0x8000U) ? ((crc << 1) ^ 0x1021U) : (crc << 1);
            }
        }
        return crc;
    }
};

/* Кодек Varint та ZigZag */
class VarintCodec {
public:
    static constexpr uint32_t zigzag_encode(int32_t val) noexcept {
        return static_cast<uint32_t>((val << 1) ^ (val >> 31));
    }

    static constexpr int32_t zigzag_decode(uint32_t val) noexcept {
        return static_cast<int32_t>((val >> 1) ^ (-(val & 1U)));
    }

    static size_t encode(uint32_t val, std::span<std::byte> out) noexcept {
        size_t len = 0;
        while (val >= 0x80U && len < out.size()) {
            out[len++] = static_cast<std::byte>((val & 0x7FU) | 0x80U);
            val >>= 7;
        }
        if (len < out.size()) {
            out[len++] = static_cast<std::byte>(val & 0x7FU);
            return len;
        }
        return 0;
    }
};

/* Шаблонний клас енергонезалежного кільцевого буфера */
template <FlashDriver DriverType>
class RingBuffer {
public:
    explicit constexpr RingBuffer(DriverType& driver, uint32_t base_addr, uint32_t total_sectors) noexcept
        : driver_{driver}, base_addr_{base_addr}, total_sectors_{total_sectors} {}

    std::expected<void, BufferError> mount() noexcept {
        uint32_t max_seq = 0;
        uint32_t min_seq = 0xFFFFFFFF;
        bool found = false;

        for (uint32_t i = 0; i < total_sectors_; ++i) {
            SectorHeader hdr;
            auto raw_span = std::as_writable_bytes(std::span{&hdr, 1});
            if (!driver_.read(base_addr_ + i * kFlashSectorSize, raw_span)) {
                return std::unexpected(BufferError::HalError);
            }

            const auto crc = Checksum::crc16(raw_span.first(14));
            if (hdr.magic == kSectorMagic && hdr.header_crc == crc) {
                found = true;
                if (hdr.sequence_num >= max_seq) {
                    max_seq = hdr.sequence_num;
                    head_sector_idx_ = i;
                }
                if (hdr.state != State::Dispatched && hdr.sequence_num <= min_seq) {
                    min_seq = hdr.sequence_num;
                    tail_sector_idx_ = i;
                }
            }
        }

        if (!found) {
            return format_initial_sector();
        }

        mounted_ = true;
        return scan_head_offset();
    }

    std::expected<void, BufferError> push(const Sample& sample) noexcept {
        if (!mounted_) return std::unexpected(BufferError::Unmounted);

        std::array<std::byte, 64> payload_buf{};
        const auto payload_len = compress_sample(sample, payload_buf);
        if (payload_len == 0) return std::unexpected(BufferError::InvalidRecord);

        const uint32_t total_rec_size = 2 + 1 + 2 + 4 + static_cast<uint32_t>(payload_len) + 4;

        if (head_write_offset_ + total_rec_size > kFlashSectorSize) {
            auto res = rotate_to_next_sector();
            if (!res) return res;
        }

        const uint32_t write_addr = base_addr_ + (head_sector_idx_ * kFlashSectorSize) + head_write_offset_;

        // 1. Запис заголовка кадру (State = Allocated)
        const uint16_t magic = kRecordMagic;
        const auto state_alloc = State::Allocated;
        const auto p_len = static_cast<uint16_t>(payload_len);
        const uint32_t seq_id = global_seq_id_;

        driver_.write(write_addr, std::as_bytes(std::span{&magic, 1}));
        driver_.write(write_addr + 2, std::as_bytes(std::span{&state_alloc, 1}));
        driver_.write(write_addr + 3, std::as_bytes(std::span{&p_len, 1}));
        driver_.write(write_addr + 5, std::as_bytes(std::span{&seq_id, 1}));

        // 2. Запис корисного навантаження
        driver_.write(write_addr + 9, std::span{payload_buf.data(), payload_len});

        // 3. Обчислення та запис контрольної суми CRC-32
        uint32_t crc = Checksum::crc32(std::as_bytes(std::span{&seq_id, 1}));
        crc = Checksum::crc32(std::span{payload_buf.data(), payload_len}, crc);
        driver_.write(write_addr + 9 + payload_len, std::as_bytes(std::span{&crc, 1}));

        // 4. Фінальний атомарний коміт
        const auto state_committed = State::Committed;
        driver_.write(write_addr + 2, std::as_bytes(std::span{&state_committed, 1}));

        head_write_offset_ += total_rec_size;
        last_sample_ = sample;
        return {};
    }

    std::expected<void, BufferError> acknowledge(uint32_t sector_idx, uint32_t record_offset) noexcept {
        if (!mounted_) return std::unexpected(BufferError::Unmounted);

        const uint32_t target_addr = base_addr_ + (sector_idx * kFlashSectorSize) + record_offset + 2;
        const auto ack_state = State::Dispatched;

        if (!driver_.write(target_addr, std::as_bytes(std::span{&ack_state, 1}))) {
            return std::unexpected(BufferError::HalError);
        }

        return {};
    }

private:
    std::expected<void, BufferError> format_initial_sector() noexcept {
        head_sector_idx_ = 0;
        tail_sector_idx_ = 0;
        global_seq_id_ = 1;

        if (!driver_.erase_sector(base_addr_)) {
            return std::unexpected(BufferError::HalError);
        }

        SectorHeader new_hdr{
            .magic = kSectorMagic,
            .sequence_num = 1,
            .erase_count = 1,
            .state = State::Allocated,
            .reserved = 0xFF,
            .header_crc = 0
        };
        auto raw = std::as_writable_bytes(std::span{&new_hdr, 1});
        new_hdr.header_crc = Checksum::crc16(raw.first(14));

        if (!driver_.write(base_addr_, raw)) {
            return std::unexpected(BufferError::HalError);
        }

        head_write_offset_ = kFlashSectorHeaderSize;
        mounted_ = true;
        return {};
    }

    std::expected<void, BufferError> scan_head_offset() noexcept {
        const uint32_t s_addr = base_addr_ + (head_sector_idx_ * kFlashSectorSize);
        head_write_offset_ = kFlashSectorHeaderSize;

        while (head_write_offset_ + 12 < kFlashSectorSize) {
            uint16_t magic = 0;
            State rec_state = State::Erased;
            uint16_t p_len = 0;

            driver_.read(s_addr + head_write_offset_, std::as_writable_bytes(std::span{&magic, 1}));
            if (magic != kRecordMagic) break;

            driver_.read(s_addr + head_write_offset_ + 2, std::as_writable_bytes(std::span{&rec_state, 1}));
            driver_.read(s_addr + head_write_offset_ + 3, std::as_writable_bytes(std::span{&p_len, 1}));

            if (rec_state == State::Committed) {
                head_write_offset_ += 2 + 1 + 2 + 4 + p_len + 4;
            } else {
                break;
            }
        }
        return {};
    }

    std::expected<void, BufferError> rotate_to_next_sector() noexcept {
        const uint32_t cur_hdr_addr = base_addr_ + (head_sector_idx_ * kFlashSectorSize) + 12;
        const auto full_state = State::Committed;
        driver_.write(cur_hdr_addr, std::as_bytes(std::span{&full_state, 1}));

        const uint32_t next_sector = (head_sector_idx_ + 1) % total_sectors_;
        const uint32_t next_addr = base_addr_ + (next_sector * kFlashSectorSize);

        SectorHeader old_hdr{};
        driver_.read(next_addr, std::as_writable_bytes(std::span{&old_hdr, 1}));
        const uint32_t er_cnt = (old_hdr.magic == kSectorMagic) ? old_hdr.erase_count + 1 : 1;

        if (!driver_.erase_sector(next_addr)) {
            return std::unexpected(BufferError::HalError);
        }

        SectorHeader new_hdr{
            .magic = kSectorMagic,
            .sequence_num = ++global_seq_id_,
            .erase_count = er_cnt,
            .state = State::Allocated,
            .reserved = 0xFF,
            .header_crc = 0
        };
        auto raw = std::as_writable_bytes(std::span{&new_hdr, 1});
        new_hdr.header_crc = Checksum::crc16(raw.first(14));
        driver_.write(next_addr, raw);

        head_sector_idx_ = next_sector;
        head_write_offset_ = kFlashSectorHeaderSize;
        return {};
    }

    size_t compress_sample(const Sample& current, std::span<std::byte> out) noexcept {
        size_t off = 0;
        const uint32_t dt = current.timestamp - last_sample_.timestamp;
        const int32_t d_temp = current.temperature_c_x100 - last_sample_.temperature_c_x100;
        const int32_t d_press = static_cast<int32_t>(current.pressure_pa) - static_cast<int32_t>(last_sample_.pressure_pa);
        const int32_t d_volt = static_cast<int32_t>(current.battery_mv) - static_cast<int32_t>(last_sample_.battery_mv);
        const uint32_t d_pulse = current.pulse_count - last_sample_.pulse_count;

        off += VarintCodec::encode(dt, out.subspan(off));
        off += VarintCodec::encode(VarintCodec::zigzag_encode(d_temp), out.subspan(off));
        off += VarintCodec::encode(VarintCodec::zigzag_encode(d_press), out.subspan(off));
        off += VarintCodec::encode(VarintCodec::zigzag_encode(d_volt), out.subspan(off));
        off += VarintCodec::encode(d_pulse, out.subspan(off));

        return off;
    }

    DriverType& driver_;
    uint32_t base_addr_{0};
    uint32_t total_sectors_{0};
    uint32_t head_sector_idx_{0};
    uint32_t head_write_offset_{0};
    uint32_t tail_sector_idx_{0};
    uint32_t global_seq_id_{0};
    Sample last_sample_{};
    bool mounted_{false};
};

} // namespace telemetry
