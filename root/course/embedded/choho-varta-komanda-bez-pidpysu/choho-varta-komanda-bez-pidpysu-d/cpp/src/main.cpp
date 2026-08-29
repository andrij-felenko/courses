// Стенд: чого коштує звіряти тег автентичності через memcmp.
//
// Збірка:  c++ -O2 -std=c++23 -Iinclude src/*.cpp -o ctdemo
//
// Один і той самий нападник працює проти двох приймачів, які відрізняються
// РІВНО одним рядком — способом звіряння тегу.

#include <algorithm>
#include <cstdlib>
#include <format>
#include <iostream>
#include <ranges>
#include <string>
#include <string_view>

#include "constant_time.hpp"
#include "tag_attack.hpp"
#include "timing_oracle.hpp"

namespace {

/// Нібито тег HMAC-SHA256 законної команди «CMD_DISARM».
constexpr ct::Tag kSecretTag{
    0x9f, 0x1c, 0x40, 0xa7, 0x33, 0xd8, 0x0b, 0x62,
    0x5e, 0xf4, 0x21, 0x8c, 0x77, 0x09, 0xba, 0xd3,
    0x46, 0xe1, 0x58, 0x2a, 0xc9, 0x70, 0x3f, 0x84,
    0x1d, 0xb6, 0x05, 0xef, 0x92, 0x6b, 0xa8, 0x37};

struct CaseResult {
    bool accepted{false};
    ct::Tag tag{};
    std::uint64_t queries{0};
};

[[nodiscard]] std::string to_hex(const ct::Tag& tag)
{
    std::string out;
    out.reserve(tag.size() * 2);
    for (const std::uint8_t byte : tag) {
        out += std::format("{:02x}", byte);
    }
    return out;
}

[[nodiscard]] std::size_t matching_bytes(const ct::Tag& a, const ct::Tag& b)
{
    return static_cast<std::size_t>(
        std::ranges::count_if(std::views::zip(a, b), [](const auto& pair) {
            const auto& [left, right] = pair;
            return left == right;
        }));
}

CaseResult run_case(std::string_view title, ct::CompareMode mode)
{
    // Той самий засів джитеру в обох дослідах: різницю дає спосіб
    // звіряння, а не випадковість стенда.
    ct::TimingOracle oracle{kSecretTag, mode, 0x00c0ffeeU};

    CaseResult result;
    if (const auto outcome = ct::recover_tag(oracle); outcome.has_value()) {
        result = CaseResult{true, outcome->tag, outcome->queries};
    } else {
        result = CaseResult{false, outcome.error().best_guess, outcome.error().queries};
    }

    std::cout << std::format("--- {} ---\n", title);
    std::cout << std::format("  кадрів надіслано:      {}\n", result.queries);
    std::cout << std::format("  байтів тегу вгадано:   {} з {}\n",
                             matching_bytes(result.tag, kSecretTag), ct::kTagLen);
    std::cout << std::format("  приймач прийняв кадр:  {}\n", result.accepted ? "ТАК" : "ні");
    std::cout << std::format("  зібраний тег:          {}\n\n", to_hex(result.tag));
    return result;
}

}  // namespace

int main()
{
    std::cout << std::format("Секрет приймача (нападнику невідомий): {}\n", to_hex(kSecretTag));
    std::cout << "Повний перебір 32-байтного тегу коштував би 2^256 спроб.\n";
    std::cout << "Побайтовий підбір — 32 * 256 = 8192 різних кадри;\n";
    std::cout << "на живому стенді кожен доводиться повторити, щоб усереднити шум.\n\n";

    const CaseResult naive = run_case("Приймач звіряє тег через memcmp", ct::CompareMode::Naive);
    const CaseResult constant =
        run_case("Приймач звіряє тег через ct::verify", ct::CompareMode::ConstantTime);

    if (!naive.accepted) {
        std::cerr << "стенд зламано: наївний приймач мав віддати тег\n";
        return EXIT_FAILURE;
    }
    if (constant.accepted) {
        std::cerr << "стенд зламано: звіряння за сталий час не мало піддатися\n";
        return EXIT_FAILURE;
    }

    std::cout << "Різниця в коді — один виклик. Різниця в наслідках — уся система.\n";
    return EXIT_SUCCESS;
}
