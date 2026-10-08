#include "dma_spi_hardware.hpp"
#include <utility>

namespace embedded {

DmaSpiHardware::DmaSpiHardware(const SpiDmaConfig& config)
    : config_(config), state_(HardwareState::Uninitialized) {
}

DmaSpiHardware::~DmaSpiHardware() {
    deinit();
}

DmaSpiHardware::DmaSpiHardware(DmaSpiHardware&& other) noexcept
    : config_(other.config_),
      state_(other.state_.load()),
      is_initialized_(other.is_initialized_),
      current_tx_buffer_(other.current_tx_buffer_),
      current_tx_length_(other.current_tx_length_) {
    other.state_ = HardwareState::Uninitialized;
    other.is_initialized_ = false;
    other.current_tx_buffer_ = nullptr;
    other.current_tx_length_ = 0;
}

DmaSpiHardware& DmaSpiHardware::operator=(DmaSpiHardware&& other) noexcept {
    if (this != &other) {
        deinit();
        config_ = other.config_;
        state_ = other.state_.load();
        is_initialized_ = other.is_initialized_;
        current_tx_buffer_ = other.current_tx_buffer_;
        current_tx_length_ = other.current_tx_length_;

        other.state_ = HardwareState::Uninitialized;
        other.is_initialized_ = false;
        other.current_tx_buffer_ = nullptr;
        other.current_tx_length_ = 0;
    }
    return *this;
}

bool DmaSpiHardware::init() {
    if (is_initialized_) {
        return true;
    }

    if (config_.spi_peripheral_addr == 0) {
        state_ = HardwareState::Error;
        return false;
    }

    is_initialized_ = true;
    state_ = HardwareState::Ready;
    return true;
}

void DmaSpiHardware::deinit() {
    if (!is_initialized_) {
        return;
    }

    if (state_ == HardwareState::Transmitting) {
        current_tx_buffer_ = nullptr;
        current_tx_length_ = 0;
    }

    is_initialized_ = false;
    state_ = HardwareState::Uninitialized;
}

bool DmaSpiHardware::startTransmitDma(const uint8_t* data, std::size_t length) {
    if (!is_initialized_ || data == nullptr || length == 0) {
        return false;
    }

    HardwareState expected = HardwareState::Ready;
    if (!state_.compare_exchange_strong(expected, HardwareState::Transmitting)) {
        return false;
    }

    current_tx_buffer_ = data;
    current_tx_length_ = length;

    return true;
}

bool DmaSpiHardware::isBusy() const {
    return state_.load() == HardwareState::Transmitting;
}

HardwareState DmaSpiHardware::getState() const {
    return state_.load();
}

void DmaSpiHardware::handleTransferCompleteIsr() {
    if (state_.load() == HardwareState::Transmitting) {
        current_tx_buffer_ = nullptr;
        current_tx_length_ = 0;
        state_.store(HardwareState::Ready);
    }
}

void DmaSpiHardware::handleTransferErrorIsr() {
    current_tx_buffer_ = nullptr;
    current_tx_length_ = 0;
    state_.store(HardwareState::Error);
}

} // namespace embedded
