// ==================== C++: SecureChannel.hpp ====================
#ifndef SECURE_CHANNEL_HPP
#define SECURE_CHANNEL_HPP

#include "FastPimpl.hpp"
#include <string_view>
#include <span>
#include <cstdint>

class SecureChannel {
    struct Impl;
    // Резервуємо 128 байтів під структуру реалізації
    static constexpr std::size_t ImplSize = 128;
    static constexpr std::size_t ImplAlign = 8;

    FastPimpl<Impl, ImplSize, ImplAlign> pImpl_;

public:
    SecureChannel(std::string_view peer_address, std::uint16_t port);
    ~SecureChannel(); // Оголошений тут, визначений у .cpp!

    SecureChannel(SecureChannel&&) noexcept;
    SecureChannel& operator=(SecureChannel&&) noexcept;

    bool send_payload(std::span<const std::byte> data);
    std::uint64_t bytes_sent() const noexcept;
};

#endif // SECURE_CHANNEL_HPP
