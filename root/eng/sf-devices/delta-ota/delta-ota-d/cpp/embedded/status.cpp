#include <cstdint>
#include <cstddef>
#include <array>

namespace embedded::ota {

inline constexpr uint32_t kDeltaMagic = 0x44454C54U;
inline constexpr std::size_t kPageSize = 256;
inline constexpr std::size_t kSectorSize = 4096;

enum class Status : uint8_t {
    Success = 0,
    InvalidMagic,
    FlashError,
    SizeMismatch,
    CorruptedPayload
};

struct Header {
    uint32_t magic;
    uint8_t  version;
    uint8_t  compression_type;
    uint16_t sector_size;
    uint32_t source_size;
    uint32_t target_size;
    uint32_t patch_size;
    uint8_t  sha256_source[32];
    uint8_t  sha256_target[32];
    uint32_t crc32_header;
};

/* Апаратний інтерфейс драйвера Flash-пам'яті без динамічного поліморфізму */
class IFlashDriver {
public:
    virtual bool read(uint32_t address, uint8_t* dst, std::size_t length) noexcept = 0;
    virtual bool write(uint32_t address, const uint8_t* src, std::size_t length) noexcept = 0;
    virtual bool erase_sector(uint32_t sector_address) noexcept = 0;
    virtual ~IFlashDriver() = default;
};

/* Детермінований клас потокового дельта-реконструктора */
class DeltaPatcher {
public:
    DeltaPatcher(IFlashDriver& flash, uint32_t src_base, uint32_t dst_base) noexcept
        : flash_(flash),
          src_base_(src_base),
          dst_base_(dst_base),
          old_offset_(0),
          new_offset_(0),
          page_idx_(0),
          running_crc_(0xFFFFFFFFU),
          header_{} {}

    Status initialize(const Header& header) noexcept {
        if (header.magic != kDeltaMagic) {
            return Status::InvalidMagic;
        }
        header_ = header;
        old_offset_ = 0;
        new_offset_ = 0;
        page_idx_ = 0;
        running_crc_ = 0xFFFFFFFFU;
        return Status::Success;
    }

    Status process_add(const uint8_t* diff, std::size_t len) noexcept {
        uint8_t old_byte = 0;
        for (std::size_t i = 0; i < len; ++i) {
            if (!flash_.read(src_base_ + old_offset_, &old_byte, 1)) {
                return Status::FlashError;
            }

            const uint8_t target_byte = static_cast<uint8_t>(old_byte + diff[i]);
            page_buffer_[page_idx_++] = target_byte;
            update_crc(target_byte);
            ++old_offset_;

            if (page_idx_ >= kPageSize) {
                Status res = flush();
                if (res != Status::Success) {
                    return res;
                }
            }
        }
        return Status::Success;
    }

    Status process_copy(const uint8_t* literal, std::size_t len) noexcept {
        for (std::size_t i = 0; i < len; ++i) {
            page_buffer_[page_idx_++] = literal[i];
            update_crc(literal[i]);

            if (page_idx_ >= kPageSize) {
                Status res = flush();
                if (res != Status::Success) {
                    return res;
                }
            }
        }
        return Status::Success;
    }

    void seek_old(int32_t offset) noexcept {
        old_offset_ = static_cast<uint32_t>(static_cast<int32_t>(old_offset_) + offset);
    }

    Status finalize() noexcept {
        Status res = flush();
        if (res != Status::Success) {
            return res;
        }
        if (new_offset_ != header_.target_size) {
            return Status::SizeMismatch;
        }
        return Status::Success;
    }

    [[nodiscard]] uint32_t get_crc32() const noexcept {
        return running_crc_ ^ 0xFFFFFFFFU;
    }

private:
    Status flush() noexcept {
        if (page_idx_ == 0) {
            return Status::Success;
        }

        const uint32_t target_addr = dst_base_ + new_offset_;
        if ((target_addr % kSectorSize) == 0) {
            if (!flash_.erase_sector(target_addr)) {
                return Status::FlashError;
            }
        }

        if (!flash_.write(target_addr, page_buffer_.data(), page_idx_)) {
            return Status::FlashError;
        }

        new_offset_ += static_cast<uint32_t>(page_idx_);
        page_idx_ = 0;
        return Status::Success;
    }

    void update_crc(uint8_t data) noexcept {
        running_crc_ ^= data;
        for (uint8_t b = 0; b < 8; ++b) {
            if (running_crc_ & 1U) {
                running_crc_ = (running_crc_ >> 1) ^ 0xEDB88320U;
            } else {
                running_crc_ = (running_crc_ >> 1);
            }
        }
    }

    IFlashDriver& flash_;
    uint32_t src_base_;
    uint32_t dst_base_;
    uint32_t old_offset_;
    uint32_t new_offset_;
    std::size_t page_idx_;
    uint32_t running_crc_;
    Header header_;
    std::array<uint8_t, kPageSize> page_buffer_{};
};

} // namespace embedded::ota
