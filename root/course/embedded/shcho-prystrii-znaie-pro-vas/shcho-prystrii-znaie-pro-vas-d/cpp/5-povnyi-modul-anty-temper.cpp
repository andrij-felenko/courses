#include <cstdint>
#include <cstddef>
#include <span>
#include <atomic>
#include <concepts>
#include <utility>

namespace security {

enum class VaultStatus : uint8_t {
    Safe = 0,
    Triggered,
    Zeroized
};

template <size_t KeySize>
class alignas(uint32_t) ScopedSecureBuffer {
public:
    constexpr ScopedSecureBuffer() noexcept {
        zeroize();
    }

    explicit ScopedSecureBuffer(std::span<const uint8_t, KeySize> src) noexcept {
        load(src);
    }

    ~ScopedSecureBuffer() noexcept {
        zeroize();
    }

    ScopedSecureBuffer(const ScopedSecureBuffer&) = delete;
    ScopedSecureBuffer& operator=(const ScopedSecureBuffer&) = delete;

    ScopedSecureBuffer(ScopedSecureBuffer&& other) noexcept {
        load(std::span<const uint8_t, KeySize>(other.storage_, KeySize));
        other.zeroize();
    }

    ScopedSecureBuffer& operator=(ScopedSecureBuffer&& other) noexcept {
        if (this != &other) {
            zeroize();
            load(std::span<const uint8_t, KeySize>(other.storage_, KeySize));
            other.zeroize();
        }
        return *this;
    }

    void load(std::span<const uint8_t, KeySize> src) noexcept {
        zeroize();
        for (size_t i = 0; i < KeySize; ++i) {
            storage_[i] = src[i];
        }
    }

    void zeroize() noexcept {
        volatile uint8_t* ptr = storage_;
        for (size_t i = 0; i < KeySize; ++i) {
            ptr[i] = 0x00U;
        }
        std::atomic_signal_fence(std::memory_order_seq_cst);
    }

    [[nodiscard]] std::span<const uint8_t, KeySize> span() const noexcept {
        return std::span<const uint8_t, KeySize>(storage_, KeySize);
    }

private:
    uint8_t storage_[KeySize]{};
};

template <typename PlatformHw>
class AntiTamperController {
public:
    static constexpr size_t KeyLength = 32;

    explicit AntiTamperController(PlatformHw& hw) noexcept
        : hw_(hw), status_(VaultStatus::Safe), breached_(false) {}

    ~AntiTamperController() noexcept {
        triggerEmergencyZeroize();
    }

    [[nodiscard]] bool setMasterKey(std::span<const uint8_t, KeyLength> key) noexcept {
        if (breached_.load(std::memory_order_relaxed) || status_ != VaultStatus::Safe) {
            return false;
        }
        keyBuffer_.load(key);
        return true;
    }

    void onTamperInterrupt() noexcept {
        breached_.store(true, std::memory_order_seq_cst);
        triggerEmergencyZeroize();
    }

    void triggerEmergencyZeroize() noexcept {
        // 1. Апаратне скидання регістрів
        hw_.wipeBackupRegisters();

        // 2. Гарантоване затирання RAM за принципом RAII
        keyBuffer_.zeroize();
        status_ = VaultStatus::Zeroized;

        // 3. Затирання Flash
        hw_.eraseSensitiveFlashSectors();

        // 4. Фіксація eFuse та скидання
        hw_.burnPermanentSecurityLock();
        hw_.hardReset();
    }

    [[nodiscard]] VaultStatus getStatus() const noexcept { return status_; }

private:
    PlatformHw& hw_;
    ScopedSecureBuffer<KeyLength> keyBuffer_{};
    VaultStatus status_;
    std::atomic<bool> breached_{false};
};

} // namespace security
