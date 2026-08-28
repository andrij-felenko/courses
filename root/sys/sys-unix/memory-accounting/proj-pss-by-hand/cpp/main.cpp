#include <algorithm>
#include <charconv>
#include <cstdint>
#include <string>
#include <string_view>
#include <unordered_map>

struct Region {
    std::uint64_t size{}, rss{}, pss{},
                  privClean{}, privDirty{}, swap{}, swapPss{};
};

using Counter = std::uint64_t Region::*;

/* Ключ порівнюється ЦІЛКОМ — про це дбає сам unordered_map. */
static const std::unordered_map<std::string_view, Counter> kFields{
    { "Size",          &Region::size      },
    { "Rss",           &Region::rss       },
    { "Pss",           &Region::pss       },
    { "Private_Clean", &Region::privClean },
    { "Private_Dirty", &Region::privDirty },
    { "Swap",          &Region::swap      },
    { "SwapPss",       &Region::swapPss   },
};

static std::string_view vmaName(std::string_view head)
{
    for (int field = 0; field < 5; ++field) {
        const auto sp = head.find(' ');
        if (sp == std::string_view::npos)
            return "[anon]";
        head.remove_prefix(sp);
        head.remove_prefix(std::min(head.find_first_not_of(' '), head.size()));
    }
    return head.empty() ? std::string_view{"[anon]"} : head;
}

void parseSmaps(std::string_view text,
                std::unordered_map<std::string, Region> &byName)
{
    Region *cur = nullptr;

    while (!text.empty()) {
        const auto nl   = text.find('\n');
        const auto line = text.substr(0, nl);
        text = (nl == std::string_view::npos) ? std::string_view{}
                                              : text.substr(nl + 1);
        if (line.empty())
            continue;

        // Адреси — малими літерами, назви полів — з великої.
        if (line.front() < 'A' || line.front() > 'Z') {
            cur = &byName[std::string(vmaName(line))];
            continue;
        }
        if (!cur)
            continue;

        const auto colon = line.find(':');
        if (colon == std::string_view::npos)
            continue;

        const auto it = kFields.find(line.substr(0, colon));
        if (it == kFields.end())
            continue;

        auto tail = line.substr(colon + 1);
        tail.remove_prefix(std::min(tail.find_first_not_of(' '), tail.size()));

        std::uint64_t value{};
        std::from_chars(tail.data(), tail.data() + tail.size(), value);
        cur->*(it->second) += value;
    }
}
