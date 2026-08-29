#include "cohort.hpp"

#include "sha256.hpp"

#include <algorithm>

namespace fleet {
namespace {

constexpr double kChiSquareCritical = 134.64;   // df = 99, p = 0.01

std::uint8_t bucket_sha256(const DeviceId& id, std::span<const std::byte> salt) noexcept
{
    const auto digest = Sha256::of(id, salt);

    // 64 біти дайджесту: зсув від `% 100` тут порядку 10^-17 на кошик і на
    // тисячі пристроїв не спостережний.
    std::uint64_t value = 0;
    for (std::size_t i = 0; i < 8; ++i) {
        value = (value << 8) | static_cast<std::uint64_t>(digest[i]);
    }
    return static_cast<std::uint8_t>(value % kBuckets);
}

std::uint8_t bucket_fnv1a(const DeviceId& id, std::span<const std::byte> salt) noexcept
{
    std::uint32_t hash = 2166136261u;
    const auto absorb = [&hash](std::span<const std::byte> data) noexcept {
        for (std::byte b : data) {
            hash ^= static_cast<std::uint32_t>(b);
            hash *= 16777619u;
        }
    };
    absorb(id);
    absorb(salt);

    // Молодші біти FNV-1a лавинують гірше за старші, а залишок від ділення
    // бере саме їх — тому спершу підмішуємо старшу половину в молодшу.
    hash ^= hash >> 16;
    hash *= 2246822519u;
    hash ^= hash >> 13;

    return static_cast<std::uint8_t>(hash % kBuckets);
}

} // namespace

DeviceId chip_id()
{
    // Серійний номер цього вузла парку.
    return DeviceId{std::byte{0x30}, std::byte{0x54}, std::byte{0x35}, std::byte{0x51},
                    std::byte{0x33}, std::byte{0x37}, std::byte{0x39}, std::byte{0x31},
                    std::byte{0x00}, std::byte{0x27}, std::byte{0x00}, std::byte{0x1B},
                    std::byte{0x00}, std::byte{0x00}, std::byte{0x00}, std::byte{0x00}};
}

CohortAssigner::CohortAssigner(std::string_view campaign_salt, HashKind kind)
    : kind_(kind)
{
    salt_.reserve(campaign_salt.size());
    for (char c : campaign_salt) {
        salt_.push_back(static_cast<std::byte>(c));
    }
}

std::uint8_t CohortAssigner::bucket(const DeviceId& id) const noexcept
{
    return (kind_ == HashKind::Sha256) ? bucket_sha256(id, salt_) : bucket_fnv1a(id, salt_);
}

bool CohortAssigner::eligible(const DeviceId& id, std::uint8_t stage_percent) const noexcept
{
    if (stage_percent >= kBuckets) {
        return true;   // фаза 100%: увесь парк
    }
    return bucket(id) < stage_percent;
}

bool CohortAssigner::Distribution::acceptable() const noexcept
{
    // Менш ніж по п'ять пристроїв на кошик — критерій уже нічого не судить.
    if (total < 5u * kBuckets) {
        return false;
    }
    return chi_square <= kChiSquareCritical;
}

CohortAssigner::Distribution CohortAssigner::survey(std::span<const DeviceId> fleet) const
{
    Distribution d;
    if (fleet.empty()) {
        return d;
    }

    for (const DeviceId& id : fleet) {
        ++d.counts[bucket(id)];
    }
    d.total = static_cast<std::uint32_t>(fleet.size());

    const auto [min_it, max_it] = std::ranges::minmax_element(d.counts);
    d.min = *min_it;
    d.max = *max_it;

    const double expected = static_cast<double>(fleet.size()) / kBuckets;
    for (std::uint32_t n : d.counts) {
        const double diff = static_cast<double>(n) - expected;
        d.chi_square += diff * diff / expected;
    }
    return d;
}

} // namespace fleet
