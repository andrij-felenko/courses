#include <iostream>
#include <iomanip>
#include <array>
#include <span>
#include <string_view>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

namespace wifi::security {

constexpr size_t PmkSize = 32;
constexpr size_t PtkSize = 64;
constexpr size_t MacSize = 6;
constexpr size_t NonceSize = 32;
constexpr size_t MicSize = 16;
constexpr size_t EapolMicOffset = 81;

struct PtkKeys {
    std::array<uint8_t, 16> kck{}; // Key Confirmation Key (перевірка MIC)
    std::array<uint8_t, 16> kek{}; // Key Encryption Key (доставка GTK)
    std::array<uint8_t, 16> tk{};  // Temporal Key (шифрування CCMP)

    ~PtkKeys() noexcept {
        OPENSSL_cleanse(kck.data(), kck.size());
        OPENSSL_cleanse(kek.data(), kek.size());
        OPENSSL_cleanse(tk.data(), tk.size());
    }
};

// RAII обгортка для безпечного очищення чутливих буферів
template <size_t N>
struct SecureBuffer : public std::array<uint8_t, N> {
    ~SecureBuffer() noexcept {
        OPENSSL_cleanse(this->data(), this->size());
    }
};

// Генерація PMK через PBKDF2
[[nodiscard]] SecureBuffer<PmkSize> derivePmk(std::string_view passphrase, std::string_view ssid) {
    SecureBuffer<PmkSize> pmk{};
    int res = PKCS5_PBKDF2_HMAC(passphrase.data(), static_cast<int>(passphrase.size()),
                                reinterpret_cast<const uint8_t*>(ssid.data()), static_cast<int>(ssid.size()),
                                4096, EVP_sha1(), static_cast<int>(pmk.size()), pmk.data());
    if (res != 1) {
        throw std::runtime_error("Помилка генерації PMK через PBKDF2");
    }
    return pmk;
}

// Генерація PTK за алгоритмом PRF-512
[[nodiscard]] PtkKeys derivePtk(std::span<const uint8_t, PmkSize> pmk,
                                std::span<const uint8_t, MacSize> apMac,
                                std::span<const uint8_t, MacSize> staMac,
                                std::span<const uint8_t, NonceSize> aNonce,
                                std::span<const uint8_t, NonceSize> sNonce) {
    constexpr std::string_view label = "Pairwise key expansion";

    // 1. Канонічне впорядкування MAC-адрес
    std::array<uint8_t, MacSize * 2> macBlock{};
    if (std::lexicographical_compare(apMac.begin(), apMac.end(), staMac.begin(), staMac.end())) {
        std::copy(apMac.begin(), apMac.end(), macBlock.begin());
        std::copy(staMac.begin(), staMac.end(), macBlock.begin() + MacSize);
    } else {
        std::copy(staMac.begin(), staMac.end(), macBlock.begin());
        std::copy(apMac.begin(), apMac.end(), macBlock.begin() + MacSize);
    }

    // 2. Канонічне впорядкування Nonce
    std::array<uint8_t, NonceSize * 2> nonceBlock{};
    if (std::lexicographical_compare(aNonce.begin(), aNonce.end(), sNonce.begin(), sNonce.end())) {
        std::copy(aNonce.begin(), aNonce.end(), nonceBlock.begin());
        std::copy(sNonce.begin(), sNonce.end(), nonceBlock.begin() + NonceSize);
    } else {
        std::copy(sNonce.begin(), sNonce.end(), nonceBlock.begin());
        std::copy(aNonce.begin(), aNonce.end(), nonceBlock.begin() + NonceSize);
    }

    // 3. Формування вхідного буфера: Label || 0x00 || MACs || Nonces || Counter
    std::vector<uint8_t> dataPrefix;
    dataPrefix.reserve(label.size() + 1 + macBlock.size() + nonceBlock.size() + 1);
    dataPrefix.insert(dataPrefix.end(), label.begin(), label.end());
    dataPrefix.push_back(0x00);
    dataPrefix.insert(dataPrefix.end(), macBlock.begin(), macBlock.end());
    dataPrefix.insert(dataPrefix.end(), nonceBlock.begin(), nonceBlock.end());
    dataPrefix.push_back(0x00); // Позиція для лічильника ітерацій

    // 4. Ітеративне розширення PRF-512 (4 блоки по 20 байтів)
    SecureBuffer<80> ptkRaw{};
    for (uint8_t counter = 0; counter < 4; ++counter) {
        dataPrefix.back() = counter;
        unsigned int mdLen = 20;
        HMAC(EVP_sha1(), pmk.data(), static_cast<int>(pmk.size()),
             dataPrefix.data(), dataPrefix.size(),
             ptkRaw.data() + (counter * 20), &mdLen);
    }

    PtkKeys ptk;
    std::copy_n(ptkRaw.begin(), 16, ptk.kck.begin());
    std::copy_n(ptkRaw.begin() + 16, 16, ptk.kek.begin());
    std::copy_n(ptkRaw.begin() + 32, 16, ptk.tk.begin());

    OPENSSL_cleanse(dataPrefix.data(), dataPrefix.size());
    return ptk;
}

// Верифікація EAPOL MIC у константному часі
[[nodiscard]] bool verifyEapolMic(std::span<const uint8_t, 16> kck,
                                  std::span<const uint8_t> eapolFrame) noexcept {
    if (eapolFrame.size() < EAPOL_MICOffset + MicSize) {
        return false;
    }

    // 1. Копіювання отриманого MIC
    std::array<uint8_t, MicSize> originalMic{};
    std::copy_n(eapolFrame.begin() + EapolMicOffset, MicSize, originalMic.begin());

    // 2. Створення робочої копії кадру з обнуленим MIC
    std::vector<uint8_t> frameCopy(eapolFrame.begin(), eapolFrame.end());
    std::fill_n(frameCopy.begin() + EapolMicOffset, MicSize, 0x00);

    // 3. Обчислення HMAC-SHA1 над кадром
    std::array<uint8_t, 20> digest{};
    unsigned int digestLen = static_cast<unsigned int>(digest.size());
    HMAC(EVP_sha1(), kck.data(), static_cast<int>(kck.size()),
         frameCopy.data(), frameCopy.size(), digest.data(), &digestLen);

    // 4. Порівняння в константному часі
    int cmp = CRYPTO_memcmp(originalMic.data(), digest.data(), MicSize);

    OPENSSL_cleanse(frameCopy.data(), frameCopy.size());
    OPENSSL_cleanse(digest.data(), digest.size());
    return (cmp == 0);
}

} // namespace wifi::security

namespace {
void printHex(std::string_view label, std::span<const uint8_t> data) {
    std::cout << std::left << std::setw(28) << label << ": ";
    for (uint8_t b : data) {
        std::cout << std::hex << std::uppercase << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    std::cout << std::dec << "\n";
}
}

int main() {
    using namespace wifi::security;

    const std::string_view ssid = "Office_Secure_WiFi";
    const std::string_view passphrase = "CorrectHorseBatteryStaple99";

    const std::array<uint8_t, 6> apMac  = {0x00, 0x14, 0x6C, 0x7E, 0x40, 0x80};
    const std::array<uint8_t, 6> staMac = {0x00, 0x25, 0xD3, 0x11, 0x22, 0x33};

    const std::array<uint8_t, 32> aNonce = {
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27,
        0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F
    };

    const std::array<uint8_t, 32> sNonce = {
        0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7,
        0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF,
        0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7,
        0xB8, 0xB9, 0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF
    };

    try {
        auto pmk = derivePmk(passphrase, ssid);
        auto ptk = derivePtk(pmk, apMac, staMac, aNonce, sNonce);

        std::cout << "=== WPA2 C++ РОЗРАХУНОК КЛЮЧІВ ===\n";
        std::cout << "SSID:       " << ssid << "\n";
        std::cout << "Passphrase: " << passphrase << "\n";
        printHex("KCK (Key Confirmation)", ptk.kck);
        printHex("KEK (Key Encryption)",   ptk.kek);
        printHex("TK  (Temporal CCMP Key)", ptk.tk);
        std::cout << "\n";

        // Синтез валідного EAPOL кадру для тестування
        std::vector<uint8_t> eapolFrame(121, 0x00);
        eapolFrame[0] = 0x02; // Version
        eapolFrame[1] = 0x03; // Type Key
        eapolFrame[4] = 0x02; // RSN Descriptor
        eapolFrame[6] = 0x01; // Key Info
        eapolFrame[7] = 0x0A;

        // Генерація еталонного підпису
        unsigned int len = 20;
        std::array<uint8_t, 20> digest{};
        HMAC(EVP_sha1(), ptk.kck.data(), static_cast<int>(ptk.kck.size()),
             eapolFrame.data(), eapolFrame.size(), digest.data(), &len);
        std::copy_n(digest.begin(), 16, eapolFrame.begin() + EapolMicOffset);

        bool isValid = verifyEapolMic(ptk.kck, eapolFrame);
        std::cout << "Результат верифікації: " << (isValid ? "ПРАВИЛЬНИЙ (УСПІХ)" : "ПОМИЛКА") << "\n";

    } catch (const std::exception &ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
