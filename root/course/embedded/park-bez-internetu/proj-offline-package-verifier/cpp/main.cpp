// Хостовий прогін верифікатора: пакет лежить звичайним файлом, Slot B
// емульовано другим файлом із поведінкою NOR (стирання в 0xFF, запис
// лише гасить біти), Ed25519 дає Monocypher 4.x. На платі замість цього
// файла стоять порти до FatFS, драйвера Flash і ROM-криптографії.
//
//   c++ -std=c++23 -O2 main.cpp installer.cpp sha256.cpp -lmonocypher -o upkgtool
//   ./upkgtool firmware.upkg slotb.bin [--resume]

#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <print>
#include <span>
#include <string>
#include <string_view>
#include <vector>

#include <monocypher.h>

#include "installer.hpp"

namespace {

using namespace upkg;

// Відкритий ключ випуску. На пристрої лежить у eFuse і не змінюється
// ніколи — саме тому підробити заголовок у полі неможливо.
constexpr PublicKey kRootPublicKey{
    0x3d, 0x40, 0x17, 0xc3, 0xe8, 0x43, 0x89, 0x5a,
    0x92, 0xb7, 0x0a, 0xa7, 0x4d, 0x1b, 0x7e, 0xbc,
    0x54, 0x94, 0xc9, 0x78, 0xc1, 0x67, 0x3b, 0xa5,
    0xa1, 0xc1, 0xc1, 0xd7, 0x93, 0xb1, 0x60, 0x1e};

// Ключ самого пристрою для підпису квитанції. У полі — захищений
// елемент або OTP-область, звідки байти не вичитуються назовні.
constexpr std::array<std::uint8_t, 32> kDeviceSecret{
    0x9d, 0x61, 0xb1, 0x9d, 0xef, 0xfd, 0x5a, 0x60,
    0xba, 0x84, 0x4a, 0xf4, 0x92, 0xec, 0x2c, 0xc4,
    0x44, 0x49, 0xc5, 0x69, 0x7b, 0x32, 0x69, 0x19,
    0x70, 0x3b, 0xac, 0x03, 0x1c, 0xae, 0x7f, 0x60};

// Файл, відкритий на читання й запис; закривається сам.
class FileDevice {
public:
    explicit FileDevice(const std::filesystem::path& path, bool create) {
        namespace fs = std::filesystem;
        auto flags = std::ios::binary | std::ios::in | std::ios::out;
        if (create && !fs::exists(path)) {
            std::ofstream{path, std::ios::binary};  // заводимо порожній
        }
        stream_.open(path, flags);
    }

    [[nodiscard]] bool ok() const { return stream_.is_open(); }

    [[nodiscard]] bool readAt(std::uint32_t offset, std::span<std::uint8_t> dst) {
        stream_.clear();
        stream_.seekg(offset);
        stream_.read(reinterpret_cast<char*>(dst.data()),
                     static_cast<std::streamsize>(dst.size()));
        return stream_.good() &&
               stream_.gcount() == static_cast<std::streamsize>(dst.size());
    }

    [[nodiscard]] bool writeAt(std::uint32_t offset,
                               std::span<const std::uint8_t> src) {
        stream_.clear();
        stream_.seekp(offset);
        stream_.write(reinterpret_cast<const char*>(src.data()),
                      static_cast<std::streamsize>(src.size()));
        stream_.flush();
        return stream_.good();
    }

private:
    std::fstream stream_;
};

class FilePackageMedia final : public PackageMedia {
public:
    explicit FilePackageMedia(FileDevice& dev) : dev_(dev) {}

    bool read(std::uint32_t offset, std::span<std::uint8_t> dst) override {
        return dev_.readAt(offset, dst);
    }
    bool write(std::uint32_t offset, std::span<const std::uint8_t> src) override {
        return dev_.writeAt(offset, src);
    }

private:
    FileDevice& dev_;
};

class FileFlashSlot final : public FlashSlot {
public:
    explicit FileFlashSlot(FileDevice& dev) : dev_(dev) {}

    // Стирання NOR: сектор повертається у всі одиниці.
    bool erase(std::uint32_t offset, std::uint32_t length) override {
        const std::vector<std::uint8_t> ones(length, 0xFF);
        return dev_.writeAt(offset, ones);
    }

    // Програмування NOR уміє лише гасити біти. Якщо сектор не стертий,
    // реальна плата мовчки видала б суміш старого й нового — тут ми на
    // цьому чесно падаємо, щоб помилку було видно одразу.
    bool program(std::uint32_t offset,
                 std::span<const std::uint8_t> src) override {
        std::vector<std::uint8_t> old(src.size(), 0xFF);
        if (dev_.readAt(offset, old)) {
            for (std::size_t i = 0; i < src.size(); ++i) {
                if ((old[i] & src[i]) != src[i]) {
                    std::println(stderr, "запис у нестертий байт 0x{:08x}",
                                 offset + static_cast<std::uint32_t>(i));
                    return false;
                }
            }
        }
        return dev_.writeAt(offset, src);
    }

    bool read(std::uint32_t offset, std::span<std::uint8_t> dst) override {
        return dev_.readAt(offset, dst);
    }

private:
    FileDevice& dev_;
};

class MonocypherEngine final : public CryptoEngine {
public:
    bool verify(std::span<const std::uint8_t> message,
                const Signature& signature,
                const PublicKey& key) const override {
        return crypto_eddsa_check(signature.data(), key.data(), message.data(),
                                  message.size()) == 0;
    }

    std::optional<Signature> signReceipt(
        std::span<const std::uint8_t> message) const override {
        Signature signature{};
        crypto_eddsa_sign(signature.data(), kDeviceSecret.data(),
                          message.data(), message.size());
        return signature;
    }
};

// NVS: на платі це окремий сектор конфігурації, тут — маленький файл.
class FileBootConfig final : public BootConfig {
public:
    explicit FileBootConfig(std::filesystem::path path)
        : path_(std::move(path)) {}

    bool store(const BootState& state) override {
        std::ofstream out{path_, std::ios::binary | std::ios::trunc};
        out.write(reinterpret_cast<const char*>(&state), sizeof(state));
        return out.good();
    }

private:
    std::filesystem::path path_;
};

std::string toHex(std::span<const std::uint8_t> data) {
    std::string text;
    text.reserve(data.size() * 2);
    for (std::uint8_t byte : data) {
        char pair[3];
        std::snprintf(pair, sizeof(pair), "%02x", byte);
        text += pair;
    }
    return text;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 3) {
        std::println(stderr, "вжиток: {} <пакет.upkg> <slotb.bin> [--resume]",
                     argv[0]);
        return 2;
    }
    const auto mode = (argc > 3 && std::string_view{argv[3]} == "--resume")
                          ? Installer::Mode::Resume
                          : Installer::Mode::Fresh;

    FileDevice package_file{argv[1], /*create=*/false};
    if (!package_file.ok()) {
        std::println(stderr, "пакет {} не відкривається", argv[1]);
        return 2;
    }
    FileDevice slot_file{argv[2], /*create=*/true};
    if (!slot_file.ok()) {
        std::println(stderr, "Slot B {} не відкривається", argv[2]);
        return 2;
    }

    FilePackageMedia media{package_file};
    FileFlashSlot flash{slot_file};
    MonocypherEngine crypto;
    FileBootConfig boot{"bootstate.bin"};

    const Policy policy{
        .hardware_id = 0x0217,        // код моделі з OTP
        .min_version = 13,            // поріг із монотонних запобіжників
        .device_serial = 0x00A31C07,
        .root_public_key = kRootPublicKey};

    Installer installer{policy, media, flash, crypto, boot};
    const auto result = installer.install(mode);

    if (!result) {
        std::println("результат: {} (код {})", describe(result.error()),
                     static_cast<int>(result.error()));
        return 1;
    }

    const Receipt& receipt = result.value();
    std::println("результат: гаразд");
    std::println("прошито версію {}, спроб завантаження {}",
                 receipt.body.version, receipt.body.boot_retries);
    std::println("хеш образу:       {}", toHex(receipt.body.image_sha256));
    std::println("підпис квитанції: {}", toHex(receipt.signature));
    return 0;
}
