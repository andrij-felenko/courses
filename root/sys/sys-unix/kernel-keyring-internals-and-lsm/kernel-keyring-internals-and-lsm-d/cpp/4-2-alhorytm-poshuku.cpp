#include <iostream>
#include <vector>
#include <string>
#include <system_error>
#include <expected>
#include <cstddef>
#include <keyutils.h>

/* Безпечне зчитування ключа в C++ з поверненням вектору байтів */
std::expected<std::vector<std::byte>, std::error_code> fetch_user_key_bytes(
    const std::string& description
) {
    key_serial_t key_id = request_key("user", description.c_str(), nullptr, 0);
    if (key_id == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    long len = keyctl(KEYCTL_READ, key_id, nullptr, 0);
    if (len < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    std::vector<std::byte> buffer(static_cast<size_t>(len));
    long bytes_read = keyctl(KEYCTL_READ, key_id, buffer.data(), buffer.size());
    if (bytes_read < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    /* KEYCTL_READ повертає ПОВНУ довжину payload, навіть коли буфер менший:
       якщо ключ оновили між двома викликами, дані обрізано. */
    if (static_cast<size_t>(bytes_read) > buffer.size()) {
        return std::unexpected(std::make_error_code(std::errc::message_size));
    }

    buffer.resize(static_cast<size_t>(bytes_read));
    return buffer;
}
