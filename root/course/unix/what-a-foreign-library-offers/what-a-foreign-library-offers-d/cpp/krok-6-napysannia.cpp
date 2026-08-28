#include <iostream>
#include <iomanip>
#include <string_view>
#include <array>
#include <span>
#include <openssl/evp.h>

int main() {
    constexpr std::string_view message = "Unix library contract verification";
    std::array<uint8_t, EVP_MAX_MD_SIZE> digest{};
    size_t digest_len = 0;

    int const ok = EVP_Q_digest(
        nullptr,
        "SHA256",
        nullptr,
        message.data(),
        message.size(),
        digest.data(),
        &digest_len
    );

    if (!ok) {
        std::cerr << "Помилка обчислення хешу SHA-256\n";
        return 1;
    }

    std::cout << "SHA-256: ";
    for (uint8_t byte : std::span(digest.data(), digest_len)) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    std::cout << '\n';
    return 0;
}
