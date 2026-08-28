// ==================== C++: SecureChannel.cpp ====================
#include "SecureChannel.hpp"
#include <vector>
#include <array>
#include <iostream>

// Повне визначення Impl у .cpp:
struct SecureChannel::Impl {
    std::array<std::uint8_t, 32> session_key_;
    std::uint64_t sequence_number_{0};
    std::uint64_t total_bytes_{0};
    std::uint16_t port_{0};
    bool is_connected_{false};

    Impl(std::string_view peer, std::uint16_t port) : port_(port), is_connected_(true) {
        session_key_.fill(0xAA); // Ініціалізація криптографічного стану
    }

    bool transmit(std::span<const std::byte> data) {
        if (!is_connected_) return false;
        total_bytes_ += data.size();
        ++sequence_number_;
        return true;
    }
};

SecureChannel::SecureChannel(std::string_view peer_address, std::uint16_t port)
    : pImpl_(peer_address, port) {}

// Визначення деструктора у .cpp гарантує наявність повного типу Impl
SecureChannel::~SecureChannel() = default;
SecureChannel::SecureChannel(SecureChannel&&) noexcept = default;
SecureChannel& SecureChannel::operator=(SecureChannel&&) noexcept = default;

bool SecureChannel::send_payload(std::span<const std::byte> data) {
    return pImpl_->transmit(data);
}

std::uint64_t SecureChannel::bytes_sent() const noexcept {
    return pImpl_->total_bytes_;
}
