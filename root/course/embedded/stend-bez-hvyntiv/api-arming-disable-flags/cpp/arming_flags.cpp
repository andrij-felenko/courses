#include "arming_flags.hpp"

#include <format>

namespace bf {
namespace {

constexpr bool isSeparator(char c) noexcept
{
    return c == ' ' || c == '\t' || c == ',' || c == '\r' || c == '\n';
}

}  // namespace

std::vector<Flag> Mask::raised() const
{
    std::vector<Flag> out;
    out.reserve(static_cast<std::size_t>(count()));
    for (std::size_t i = 0; i < kFlagCount; ++i) {
        if (test(static_cast<Flag>(i))) {
            out.push_back(static_cast<Flag>(i));
        }
    }
    return out;
}

std::vector<unsigned> Mask::unknownBits() const
{
    std::vector<unsigned> out;
    for (unsigned bit = static_cast<unsigned>(kFlagCount); bit < 32; ++bit) {
        if (((bits_ >> bit) & 1u) != 0u) {
            out.push_back(bit);
        }
    }
    return out;
}

std::string_view describe(CliError error) noexcept
{
    switch (error) {
    case CliError::NoFlagsField:
        return "у виводі немає поля 'Arming disable flags:'";
    }
    return "невідома помилка";
}

std::expected<CliStatus, CliError> parseCliStatus(std::string_view line)
{
    constexpr std::string_view marker = "Arming disable flags:";

    const auto at = line.find(marker);
    if (at == std::string_view::npos) {
        return std::unexpected{CliError::NoFlagsField};
    }
    line.remove_prefix(at + marker.size());

    CliStatus status;
    std::size_t pos = 0;
    while (pos < line.size()) {
        while (pos < line.size() && isSeparator(line[pos])) {
            ++pos;
        }
        const std::size_t start = pos;
        while (pos < line.size() && !isSeparator(line[pos])) {
            ++pos;
        }
        const std::string_view token = line.substr(start, pos - start);
        if (token.empty() || token == "None") {   // None — це чистий стан
            continue;
        }
        if (const auto flag = flagByName(token)) {
            status.mask.set(*flag);
        } else {
            status.unknownNames.emplace_back(token);
        }
    }
    return status;
}

std::string explain(Mask mask)
{
    if (mask.armingAllowed()) {
        return "  маска чиста (0x00000000) — армінг дозволено\n";
    }

    std::string out;
    for (const Flag flag : mask.raised()) {
        const FlagInfo& item = info(flag);
        out += std::format("  біт {:2}  {:<18} {}\n           рецепт: {}\n",
                           static_cast<unsigned>(flag), item.name, item.cause, item.remedy);
    }
    for (const unsigned bit : mask.unknownBits()) {
        out += std::format("  біт {:2}  <прошивка новіша за довідник>\n", bit);
    }
    return out;
}

}  // namespace bf
