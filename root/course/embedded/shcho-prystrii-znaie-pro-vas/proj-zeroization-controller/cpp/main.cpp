#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <atomic>
#include <utility>

namespace security {

enum class State : uint8_t {
    Locked = 0,
    Unlocked,
    Tampered,
    Zeroized
};

template <size_t KeySize>
class alignas(uint32_t) SecureKeyBuffer {
public:
    constexpr SecureKeyBuffer() noexcept {
        clear();
    }

    explicit SecureKeyBuffer(std::span<const uint8_t, KeySize> source) noexcept {
        assign(source);
    }

    ~SecureKeyBuffer() noexcept {
        clear();
    }

    // Забороняємо неявне копіювання, щоб уникнути витоку дублікатів у стек
    SecureKeyBuffer(const SecureKeyBuffer&) = delete;
    SecureKeyBuffer& operator=(const SecureKeyBuffer&) = delete;

    SecureKeyBuffer(SecureKeyBuffer&& other) noexcept {
        assign(std::span<const uint8_t, KeySize>(other.data_, KeySize));
        other.clear();
    }

    SecureKeyBuffer& operator=(SecureKeyBuffer&& other) noexcept {
        if (this != &other) {
            clear();
            assign(std::span<const uint8_t, KeySize>(other.data_, KeySize));
            other.clear();
        }
        return *this;
    }

    void assign(std::span<const uint8_t, KeySize> source) noexcept {
        clear();
        for (size_t i = 0; i < KeySize; ++i) {
            data_[i] = source[i];
        }
    }

    void clear() noexcept {
        volatile uint8_t* p = data_;
        for (size_t i = 0; i < KeySize; ++i) {
            p[i] = 0x00U;
        }
        std::atomic_signal_fence(std::memory_order_seq_cst);
    }

    [[nodiscard]] std::span<const uint8_t, KeySize> view() const noexcept {
        return std::span<const uint8_t, KeySize>(data_, KeySize);
    }

private:
    uint8_t data_[KeySize]{};
};

template <typename HardwareInterface>
class TamperGuard {
public:
    static constexpr size_t MasterKeyBytes = 32;

    explicit TamperGuard(HardwareInterface& hw) noexcept
        : hw_(hw), state_(State::Locked), tamperActive_(false) {}

    ~TamperGuard() noexcept {
        emergencyZeroize();
    }

    [[nodiscard]] bool loadMasterKey(std::span<const uint8_t, MasterKeyBytes> key) noexcept {
        if (tamperActive_.load(std::memory_order_relaxed) || state_ == State::Tampered) {
            return false;
        }
        keyBuffer_.assign(key);
        state_ = State::Unlocked;
        return true;
    }

    void handleTamperInterrupt() noexcept {
        tamperActive_.store(true, std::memory_order_seq_cst);
        emergencyZeroize();
    }

    void emergencyZeroize() noexcept {
        // 1. Аварійна зупинка передач DMA
        hw_.abortDmaTransfers();

        // 2. Миттєве скидання апаратного сховища Backup SRAM
        hw_.wipeBackupSram();

        // 3. Гарантоване затирання оперативної пам'яті через RAII-буфер
        keyBuffer_.clear();
        state_ = State::Zeroized;

        // 4. Повне стирання Flash-пам'яті
        hw_.eraseAllFlashPartitions();

        // 5. Перепалювання eFuse захисту та перезавантаження
        hw_.burnPermanentSecurityLock();
        hw_.systemReset();
    }

    [[nodiscard]] State getState() const noexcept { return state_; }

private:
    HardwareInterface& hw_;
    SecureKeyBuffer<MasterKeyBytes> keyBuffer_{};
    State state_;
    std::atomic<bool> tamperActive_{false};
};

} // namespace security
