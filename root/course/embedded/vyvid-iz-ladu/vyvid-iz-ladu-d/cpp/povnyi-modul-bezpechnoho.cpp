#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <string_view>
#include <expected>
#include <algorithm>

namespace embedded::security {

enum class DecomError : uint8_t {
    InvalidParameter,
    FlashEraseFailed,
    FlashVerifyFailed,
    EfuseBlowFailed,
    SecureEnclaveError
};

struct PartitionTarget {
    uint32_t start_address;
    uint32_t size_bytes;
    std::string_view label;
};

/* RAII-обгортка для безпечного автоматичного затирання пам'яті */
template <size_t N>
class SecureBuffer {
public:
    SecureBuffer() noexcept { data_.fill(0); }
    explicit SecureBuffer(uint8_t fill_byte) noexcept { data_.fill(fill_byte); }

    ~SecureBuffer() noexcept {
        wipe();
    }

    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;
    SecureBuffer(SecureBuffer&&) noexcept = default;
    SecureBuffer& operator=(SecureBuffer&&) noexcept = default;

    [[nodiscard]] std::span<uint8_t, N> span() noexcept { return std::span<uint8_t, N>(data_); }
    [[nodiscard]] std::span<const uint8_t, N> span() const noexcept { return std::span<const uint8_t, N>(data_); }
    [[nodiscard]] uint8_t* data() noexcept { return data_.data(); }
    [[nodiscard]] const uint8_t* data() const noexcept { return data_.data(); }
    [[nodiscard]] constexpr size_t size() const noexcept { return N; }

    void wipe() noexcept {
        volatile uint8_t* p = data_.data();
        for (size_t i = 0; i < N; ++i) {
            p[i] = 0x00;
        }
        __asm__ __volatile__("" : : "r"(data_.data()) : "memory");
    }

private:
    std::array<uint8_t, N> data_;
};

class HardwareDecommissioner {
public:
    static constexpr size_t SectorSize = 4096;
    static constexpr size_t AuditHashSize = 32;

    using AuditReceipt = std::array<uint8_t, AuditHashSize>;

    /**
     * @brief Головний вхід у процедуру виведення з експлуатації.
     */
    static std::expected<AuditReceipt, DecomError> execute(
        std::span<const PartitionTarget> targets,
        bool permanent_lockdown) noexcept
    {
        if (targets.empty()) {
            return std::unexpected(DecomError::InvalidParameter);
        }

        /* 1. Затирання кожного розділу Flash */
        for (const auto& target : targets) {
            if (auto res = wipePartition(target); !res) {
                return std::unexpected(res.error());
            }
        }

        /* 2. Апаратне блокування eFuses */
        if (permanent_lockdown) {
            if (auto res = burnLockdownEfuses(); !res) {
                return std::unexpected(res.error());
            }
        }

        /* 3. Генерація аудиторської квитанції */
        return generateAuditReceipt(targets.size(), permanent_lockdown);
    }

private:
    static std::expected<void, DecomError> wipePartition(const PartitionTarget& part) noexcept {
        if (part.size_bytes == 0 || (part.size_bytes % SectorSize) != 0) {
            return std::unexpected(DecomError::InvalidParameter);
        }

        const uint32_t num_sectors = part.size_bytes / SectorSize;
        SecureBuffer<256> wipe_buf;

        for (uint32_t s = 0; s < num_sectors; ++s) {
            const uint32_t sector_addr = part.start_address + (s * SectorSize);

            /* Прохід 1: Запис нулями */
            std::fill(wipe_buf.span().begin(), wipe_buf.span().end(), 0x00);
            if (!writeSectorPass(sector_addr, wipe_buf.span())) {
                return std::unexpected(DecomError::FlashEraseFailed);
            }

            /* Прохід 2: Запис інвертованим шаблоном 0xAA */
            std::fill(wipe_buf.span().begin(), wipe_buf.span().end(), 0xAA);
            if (!writeSectorPass(sector_addr, wipe_buf.span())) {
                return std::unexpected(DecomError::FlashEraseFailed);
            }

            /* Прохід 3: Апаратне стирання сектора в 0xFF */
            if (hal_flash_erase_sector(sector_addr) != 0) {
                return std::unexpected(DecomError::FlashEraseFailed);
            }

            /* Прохід 4: Контрольне зчитування та перевірка 0xFF */
            if (!verifySectorClean(sector_addr)) {
                return std::unexpected(DecomError::FlashVerifyFailed);
            }
        }

        return {};
    }

    static bool writeSectorPass(uint32_t sector_addr, std::span<const uint8_t> block) noexcept {
        for (uint32_t off = 0; off < SectorSize; off += block.size()) {
            if (hal_flash_write(sector_addr + off, block.data(), block.size()) != 0) {
                return false;
            }
        }
        return true;
    }

    static bool verifySectorClean(uint32_t sector_addr) noexcept {
        SecureBuffer<256> read_buf;
        for (uint32_t off = 0; off < SectorSize; off += read_buf.size()) {
            if (hal_flash_read(sector_addr + off, read_buf.data(), read_buf.size()) != 0) {
                return false;
            }
            if (!std::all_of(read_buf.span().begin(), read_buf.span().end(), [](uint8_t b) { return b == 0xFF; })) {
                return false;
            }
        }
        return true;
    }

    static std::expected<void, DecomError> burnLockdownEfuses() noexcept {
        /* Блокування JTAG, UART завантажувача та переведення в стан Terminated */
        constexpr uint32_t SecurityBlock = 0;
        constexpr uint32_t JtagDisableBit = 3;
        constexpr uint32_t BootDisableBit = 4;
        constexpr uint32_t TerminatedBit = 7;

        if (hal_efuse_burn_bit(SecurityBlock, JtagDisableBit) != 0 ||
            hal_efuse_burn_bit(SecurityBlock, BootDisableBit) != 0 ||
            hal_efuse_burn_bit(SecurityBlock, TerminatedBit) != 0) {
            return std::unexpected(DecomError::EfuseBlowFailed);
        }

        if (!hal_efuse_read_bit(SecurityBlock, TerminatedBit)) {
            return std::unexpected(DecomError::EfuseBlowFailed);
        }

        return {};
    }

    static AuditReceipt generateAuditReceipt(size_t target_count, bool locked) noexcept {
        SecureBuffer<64> entropy(0xA5);
        entropy.data()[0] = locked ? 0x01 : 0x00;
        entropy.data()[1] = static_cast<uint8_t>(target_count);

        AuditReceipt receipt{};
        hal_sha256_calculate(entropy.data(), entropy.size(), receipt.data());
        return receipt;
    }
};

} // namespace embedded::security
