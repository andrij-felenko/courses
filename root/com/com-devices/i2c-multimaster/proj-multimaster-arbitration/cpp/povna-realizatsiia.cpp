#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <vector>
#include <functional>
#include <random>
#include <expected>

class MultiMasterI2C {
public:
    enum class Error : uint8_t {
        Busy,
        ArbitrationLost,
        Nack,
        Timeout,
        BufferOverflow,
        MaxRetriesExceeded
    };

    enum class State : uint8_t {
        Idle,
        MasterTx,
        MasterRx,
        SlaveTx,
        SlaveRx,
        ArbitrationLost
    };

    static constexpr size_t MaxBufferSize = 32;
    static constexpr uint8_t MaxRetries = 5;
    static constexpr uint32_t BaseBackoffUs = 100;

    using RxCallback = std::function<void(std::span<const uint8_t>)>;

    explicit MultiMasterI2C(uint8_t ownAddress, RxCallback rxCallback = nullptr)
        : ownAddress_{ownAddress},
          rxCallback_{std::move(rxCallback)},
          rng_{std::random_device{}()} {}

    [[nodiscard]] std::expected<void, Error> transmit(uint8_t targetAddress, std::span<const uint8_t> data) {
        if (data.size() > MaxBufferSize) {
            return std::unexpected(Error::BufferOverflow);
        }
        if (state_ != State::Idle) {
            return std::unexpected(Error::Busy);
        }

        activeTarget_ = targetAddress;
        txBuffer_.assign(data.begin(), data.end());
        transferredBytes_ = 0;
        retryCount_ = 0;

        state_ = State::MasterTx;
        hwGenerateStart();
        return {};
    }

    /* Апаратні обробники переривань контролера */
    void onEventInterrupt() noexcept {
        switch (state_) {
            case State::MasterTx:
                handleMasterTxStep();
                break;
            case State::SlaveRx:
                handleSlaveRxStep();
                break;
            default:
                break;
        }
    }

    void onAddressMatchInterrupt() noexcept {
        state_ = State::SlaveRx;
        slaveRxBuffer_.clear();
        hwEnableAck(true);
    }

    void onStopConditionInterrupt() noexcept {
        if (state_ == State::SlaveRx) {
            if (rxCallback_ && !slaveRxBuffer_.empty()) {
                rxCallback_(std::span<const uint8_t>{slaveRxBuffer_});
            }
            ++rxSuccessCount_;
            state_ = State::Idle;
        }
    }

    void onErrorInterrupt() noexcept {
        ++arbitrationLostCount_;
        hwClearArloFlag();
        hwDisableTxInterrupts();

        state_ = State::ArbitrationLost;
        hwEnableSlaveListening(ownAddress_);

        if (retryCount_ < MaxRetries) {
            ++retryCount_;
            uint32_t delayUs = calculateBackoffDelay(retryCount_);
            hwDelayUs(delayUs);

            transferredBytes_ = 0;
            state_ = State::MasterTx;
            hwGenerateStart();
        } else {
            state_ = State::Idle;
        }
    }

    [[nodiscard]] uint32_t getArbitrationLostCount() const noexcept { return arbitrationLostCount_; }
    [[nodiscard]] uint32_t getTxSuccessCount() const noexcept { return txSuccessCount_; }
    [[nodiscard]] uint32_t getRxSuccessCount() const noexcept { return rxSuccessCount_; }

private:
    uint8_t ownAddress_{0};
    RxCallback rxCallback_;
    State state_{State::Idle};

    uint8_t activeTarget_{0};
    std::vector<uint8_t> txBuffer_;
    size_t transferredBytes_{0};
    uint8_t retryCount_{0};

    std::vector<uint8_t> slaveRxBuffer_;
    std::mt19937 rng_;

    uint32_t arbitrationLostCount_{0};
    uint32_t txSuccessCount_{0};
    uint32_t rxSuccessCount_{0};

    void handleMasterTxStep() noexcept {
        if (transferredBytes_ == 0) {
            uint8_t addrByte = static_cast<uint8_t>((activeTarget_ << 1) | 0x00);
            hwWriteByte(addrByte);
            transferredBytes_ = 1;
        } else {
            size_t idx = transferredBytes_ - 1;
            if (idx < txBuffer_.size()) {
                hwWriteByte(txBuffer_[idx]);
                ++transferredBytes_;
            } else {
                hwGenerateStop();
                state_ = State::Idle;
                ++txSuccessCount_;
            }
        }
    }

    void handleSlaveRxStep() noexcept {
        if (slaveRxBuffer_.size() < MaxBufferSize) {
            slaveRxBuffer_.push_back(hwReadByte());
        }
    }

    [[nodiscard]] uint32_t calculateBackoffDelay(uint8_t retries) noexcept {
        uint32_t maxSlots = 1U << std::min<uint8_t>(retries, MaxRetries);
        std::uniform_int_distribution<uint32_t> dist(1, maxSlots);
        return dist(rng_) * BaseBackoffUs;
    }

    /* Апаратні виклики рівня драйвера */
    void hwGenerateStart() noexcept;
    void hwGenerateStop() noexcept;
    void hwWriteByte(uint8_t byte) noexcept;
    uint8_t hwReadByte() noexcept;
    void hwEnableAck(bool enable) noexcept;
    void hwClearArloFlag() noexcept;
    void hwDisableTxInterrupts() noexcept;
    void hwEnableSlaveListening(uint8_t addr) noexcept;
    void hwDelayUs(uint32_t us) noexcept;
};
