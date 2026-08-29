#include "rollout.hpp"

#include <algorithm>
#include <array>

namespace fleet {

Rng::Rng(const DeviceId& id)
    : engine_([&id] {
          // На кристалі сюди йдуть TRNG, молодші біти непідключеного входу АЦП
          // і коливання таймера між перериваннями; на хості їхню роль виконує
          // random_device з годинником. Ідентифікатор кристала домішується не
          // заради випадковості, а заради гарантії: навіть коли жодне джерело
          // ентропії не працює, два вузли не підуть у мережу в одну мілісекунду.
          std::random_device source;
          const auto now = static_cast<std::uint32_t>(
              std::chrono::steady_clock::now().time_since_epoch().count());

          std::array<std::uint32_t, 8> seed{source(), source(), now, 0, 0, 0, 0, 0};
          for (std::size_t i = 0; i < 4; ++i) {
              seed[4 + i] = (static_cast<std::uint32_t>(id[4 * i + 0]) << 24) |
                            (static_cast<std::uint32_t>(id[4 * i + 1]) << 16) |
                            (static_cast<std::uint32_t>(id[4 * i + 2]) << 8) |
                            (static_cast<std::uint32_t>(id[4 * i + 3]));
          }
          std::seed_seq sequence(seed.begin(), seed.end());
          return std::mt19937(sequence);
      }())
{
}

std::uint32_t Rng::below(std::uint32_t bound)
{
    if (bound == 0) {
        return 0;
    }
    // uniform_int_distribution сама відкидає хвіст, який не ділиться на
    // діапазон націло: писати `% bound` тут означало б тихо збити джитер до
    // початку вікна.
    std::uniform_int_distribution<std::uint32_t> dist(0, bound - 1);
    return dist(engine_);
}

Millis Rng::between(Millis lo, Millis hi)
{
    if (hi <= lo) {
        return lo;
    }
    std::uniform_int_distribution<std::int64_t> dist(lo.count(), hi.count());
    return Millis{dist(engine_)};
}

Millis initial_jitter(Rng& rng, Millis window)
{
    if (window <= Millis{0}) {
        return Millis{0};
    }
    return Millis{rng.below(static_cast<std::uint32_t>(window.count()))};
}

DecorrelatedBackoff::DecorrelatedBackoff(Millis base, Millis max) noexcept
    : base_(base <= Millis{0} ? Millis{1} : base),
      max_(std::max(max, base <= Millis{0} ? Millis{1} : base)),
      previous_(base_)
{
}

Millis DecorrelatedBackoff::next(Rng& rng)
{
    // Верхня межа росте втричі від ПОПЕРЕДНЬОЇ фактичної затримки, а не від
    // номера спроби: саме через це вузли не збираються назад в одну фазу.
    const Millis high = std::min(max_, previous_ * 3);
    previous_ = std::min(max_, rng.between(base_, high));
    ++attempts_;
    return previous_;
}

} // namespace fleet
