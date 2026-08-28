// inspect_integrity.cpp - Інспекція атрибутів IMA/EVM мовою C++ (C++20, RAII, std::span)
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span >
#include <iomanip>
#include <cstdint>
#include <system_error>
#include <byteswap.h>
#include <sys/xattr.h>

enum class ImaXattrType : uint8_t {
    DigestNg = 0x02,
    EvmSig = 0x04,
    AsymSig = 0x05
};

#pragma pack(push, 1)
struct SignatureV2Hdr {
    uint8_t type;
    uint8_t version;
    uint8_t hash_algo;
    uint32_t keyid;
    uint16_t sig_size;
};
#pragma pack(pop)

std::string_view algoToName(uint8_t algo) noexcept {
    switch (algo) {
        case 1: return "SHA-1";
        case 2: return "RIPEMD160";
        case 4: return "SHA-256";
        case 5: return "SHA-384";
        case 6: return "SHA-512";
        default: return "Невідомий";
    }
}

void inspectImaXattr(std::string_view path) {
    std::vector<uint8_t> buffer(1024);
    ssize_t res = ::getxattr(path.data(), "security.ima", buffer.data(), buffer.size());

    if (res < 0) {
        if (errno == ENODATA) {
            std::cout << "[IMA] Атрибут security.ima відсутній у файлі\n";
        } else {
            std::cout << "[IMA] Помилка getxattr: " << std::generic_category().message(errno) << "\n";
        }
        return;
    }

    std::span<const uint8_t> data(buffer.data(), static_cast<size_t>(res));
    if (data.empty()) {
        std::cout << "[IMA] Атрибут security.ima порожній\n";
        return;
    }

    const auto type = static_cast<ImaXattrType>(data[0]);
    std::cout << "[IMA] Зчитано " << data.size() << " байт. Тип: 0x"
              << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(data[0])
              << std::dec << "\n";

    if (type == ImaXattrType::DigestNg && data.size() >= 2) {
        const uint8_t algo = data[1];
        std::cout << "  -> Формат: DIGEST_NG (необроблений хеш)\n";
        std::cout << "  -> Алгоритм: " << algoToName(algo) << "\n";
        std::cout << "  -> Хеш вмісту (hex): ";
        for (size_t i = 2; i < data.size(); ++i) {
            std::cout << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(data[i]);
        }
        std::cout << std::dec << "\n";
    } else if ((type == ImaXattrType::EvmSig || type == ImaXattrType::AsymSig) &&
               data.size() >= sizeof(SignatureV2Hdr)) {
        const auto* hdr = reinterpret_cast<const SignatureV2Hdr*>(data.data());
        const uint32_t keyid = __builtin_bswap32(hdr->keyid);
        const uint16_t sigLen = __builtin_bswap16(hdr->sig_size);

        std::cout << "  -> Формат: Асиметричний цифровий підпис (v" << static_cast<int>(hdr->version) << ")\n";
        std::cout << "  -> Алгоритм хешування: " << algoToName(hdr->hash_algo);
        std::cout << "  -> Key ID у брелоку .ima: 0x" << std::hex << std::setfill('0') << std::setw(8) << keyid << std::dec << "\n";
        std::cout << "  -> Розмір цифрового підпису: " << sigLen << " байт\n";
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_файлу>\n";
        return EXIT_FAILURE;
    }

    std::cout << "=== Аналіз цілісності файлу (C++20): " << argv[1] << " ===\n";
    inspectImaXattr(argv[1]);
    return EXIT_SUCCESS;
}
