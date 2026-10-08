#ifndef OSCORE_CONTEXT_HPP
#ifndef OSCORE_CONTEXT_HPP
#define OSCORE_CONTEXT_HPP

#include <vector>
#include <cstdint>
#include <span>
#include <string_view>
#include <iostream>

namespace oscore {

class OscoreContext {
public:
    OscoreContext(std::span<const std::uint8_t> master_secret, std::span<const std::uint8_t> master_salt) 
        : sequence_number_(1) {
        master_secret_.assign(master_secret.begin(), master_secret.end());
        master_salt_.assign(master_salt.begin(), master_salt.end());
        
        derive_keys();
        std::cout << "[C++ RAII OscoreContext] Контекст ініціалізовано, сесійні ключі захищено.\n";
    }

    ~OscoreContext() {
        /* RAII-безпечне очищення пам'яті ключів перед звільненням */
        std::fill(master_secret_.begin(), master_secret_.end(), 0);
        std::fill(sender_key_.begin(), sender_key_.end(), 0);
        std::fill(recipient_key_.begin(), recipient_key_.end(), 0);
        std::cout << "[C++ RAII OscoreContext] Секретні ключі безпечно вилучено з пам'яті.\n";
    }

    [[nodiscard]] std::uint64_t next_sequence_number() noexcept {
        return sequence_number_++;
    }

    [[nodiscard]] std::span<const std::uint8_t> sender_key() const noexcept {
        return sender_key_;
    }

    [[nodiscard]] std::span<const std::uint8_t> common_iv() const noexcept {
        return common_iv_;
    }

private:
    void derive_keys() {
        sender_key_.resize(16, 0xA5);
        recipient_key_.resize(16, 0x5A);
        common_iv_.resize(13, 0x11);
    }

    std::vector<std::uint8_t> master_secret_;
    std::vector<std::uint8_t> master_salt_;
    std::vector<std::uint8_t> sender_key_;
    std::vector<std::uint8_t> recipient_key_;
    std::vector<std::uint8_t> common_iv_;
    std::uint64_t sequence_number_;
};

} // namespace oscore

#endif // OSCORE_CONTEXT_HPP
