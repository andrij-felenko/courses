// Стенд перевірки образу: той самий код, що в завантажувачі, зібраний під
// хост. На пристрої буфер — це слот завантаження у Flash, а ключ береться
// з захищеного сектора, не з файла.
//
//   ./verify firmware-revB-v2.4.0.signed.bin root-pubkey.bin [лічильник]
#include <charconv>
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <optional>
#include <print>
#include <string_view>
#include <vector>

#include "release/verifier.hpp"

namespace {

constexpr std::uint32_t kSlotCapacity = 512u * 1024u;

std::optional<std::vector<std::uint8_t>> readFile(const std::filesystem::path& path,
                                                  std::size_t limit)
{
    std::error_code ec;
    const auto size = std::filesystem::file_size(path, ec);
    if (ec) {
        std::println(stderr, "не відкривається {}: {}", path.string(), ec.message());
        return std::nullopt;
    }
    if (size == 0 || size > limit) {
        std::println(stderr, "{}: {} Б поза межами слота (1..{} Б)",
                     path.string(), size, limit);
        return std::nullopt;
    }

    std::vector<std::uint8_t> data(static_cast<std::size_t>(size));
    std::ifstream in{path, std::ios::binary};
    if (!in.read(reinterpret_cast<char*>(data.data()),
                 static_cast<std::streamsize>(data.size()))) {
        std::println(stderr, "{}: читання обірвалося", path.string());
        return std::nullopt;
    }
    return data;
}

std::optional<std::uint32_t> parseCounter(std::string_view text)
{
    std::uint32_t value{};
    const auto* end = text.data() + text.size();
    const auto [ptr, ec] = std::from_chars(text.data(), end, value);
    if (ec != std::errc{} || ptr != end) {
        return std::nullopt;
    }
    return value;
}

}  // namespace

int main(int argc, char** argv)
{
    if (argc < 3 || argc > 4) {
        std::println(stderr,
                     "вжиток: {} <образ.signed.bin> <root-pubkey.bin> [лічильник]",
                     argv[0]);
        return 2;
    }

    std::uint32_t activeCounter = 0;
    if (argc == 4) {
        const auto parsed = parseCounter(argv[3]);
        if (!parsed) {
            std::println(stderr, "лічильник '{}' не є числом", argv[3]);
            return 2;
        }
        activeCounter = *parsed;
    }

    const auto image = readFile(argv[1], release::kHeaderSize + kSlotCapacity);
    if (!image) {
        return 1;
    }

    const auto key = readFile(argv[2], release::kPublicKeySize);
    if (!key || key->size() != release::kPublicKeySize || key->front() != 0x04) {
        std::println(stderr, "{} не є непакованою точкою P-256 (65 Б, 0x04)", argv[2]);
        return 1;
    }

    std::uint64_t kicks = 0;
    // На пристрої тут стоїть HAL_IWDG_Refresh(&hiwdg).
    release::Verifier verifier{*key, [&kicks] { ++kicks; }};

    const release::Policy policy{
        .activeSecurityCounter = activeCounter,
        .maxPayloadSize = kSlotCapacity,
    };

    const auto verdict = verifier.verify(*image, policy);
    if (!verdict) {
        std::println(stderr, "ОБРАЗ ВІДХИЛЕНО: {}", release::describe(verdict.error()));
        return 1;
    }

    const auto version = release::unpackVersion(verdict->header.versionPacked);
    std::println("образ прийнято: v{}.{}.{}, тіло {} Б, лічильник {}, маска {:#06x}",
                 version.major, version.minor, version.patch,
                 verdict->header.payloadSize, verdict->header.securityCounter,
                 verdict->header.hwMask);
    std::println("сторожовий таймер поглажено {} разів", kicks);
    return 0;
}
