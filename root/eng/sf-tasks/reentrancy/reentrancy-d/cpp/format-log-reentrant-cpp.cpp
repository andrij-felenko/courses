#include <iostream>
#include <string>
#include <string_view>
#include <ctime>
#include <array>

// НЕРЕЕНТЕРАБЕЛЬНИЙ ВАРІАНТ (C++): прихований static буфер створює неявний стан.
std::string_view format_log_unsafe_cpp(std::string_view level, std::string_view message) {
    static std::array<char, 256> buffer; // Спільний статичний стан
    std::time_t now = std::time(nullptr);
    std::tm tm_info;
    gmtime_r(&now, &tm_info);

    int written = snprintf(buffer.data(), buffer.size(), "[%02d:%02d:%02d] [%.*s] %.*s",
                           tm_info.tm_hour, tm_info.tm_min, tm_info.tm_sec,
                           static_cast<int>(level.size()), level.data(),
                           static_cast<int>(message.size()), message.data());

    return std::string_view(buffer.data(), written > 0 ? written : 0);
}

// РЕЕНТЕРАБЕЛЬНИЙ ВАРІАНТ (C++): передача локального буфера викликачем.
// Локальна автоматична пам'ять на стекі гарантує повну ізоляцію кожного виклику.
bool format_log_reentrant_cpp(char* out_buf, std::size_t out_size,
                              std::string_view level, std::string_view message) {
    if (!out_buf || out_size == 0) {
        return false;
    }

    std::time_t now = std::time(nullptr);
    std::tm tm_info;
    if (gmtime_r(&now, &tm_info) == nullptr) {
        return false;
    }

    int written = snprintf(out_buf, out_size, "[%02d:%02d:%02d] [%.*s] %.*s",
                           tm_info.tm_hour, tm_info.tm_min, tm_info.tm_sec,
                           static_cast<int>(level.size()), level.data(),
                           static_cast<int>(message.size()), message.data());

    return written >= 0 && static_cast<std::size_t>(written) < out_size;
}
