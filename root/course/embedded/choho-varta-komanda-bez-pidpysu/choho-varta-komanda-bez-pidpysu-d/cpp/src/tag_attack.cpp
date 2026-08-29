#include "tag_attack.hpp"

#include <ranges>

namespace {

/// Скільки разів надіслати той самий кадр, щоб усереднити джитер стенда.
/// На чистій моделі вистачило б одного пострілу — на живому залізі ні.
constexpr unsigned kProbesPerGuess = 24;

/// Чим забиваємо ще не підібраний хвіст тегу. Значення не важить.
constexpr std::uint8_t kFillerByte = 0xCC;

}  // namespace

namespace ct {

std::expected<Recovered, Rejected> recover_tag(TimingOracle& oracle)
{
    const std::uint64_t start = oracle.queries();
    Tag guess{};
    guess.fill(kFillerByte);

    const auto spent = [&] { return oracle.queries() - start; };

    for (const std::size_t position : std::views::iota(std::size_t{0}, kTagLen)) {
        std::uint64_t best_cost = 0;
        std::uint8_t best_byte = 0;
        bool decided = false;

        for (const unsigned candidate : std::views::iota(0u, 256u)) {
            guess[position] = static_cast<std::uint8_t>(candidate);

            std::uint64_t cost_sum = 0;
            for (unsigned probe = 0; probe < kProbesPerGuess; ++probe) {
                const Reply reply = oracle.ask(guess);
                if (reply.accepted) {
                    // Останній байт підібрано: приймач прийняв цілий кадр.
                    return Recovered{guess, spent()};
                }
                cost_sum += reply.cost;
            }

            // Строге «більше» лишає перший максимум: за сталого часу всі
            // кандидати рівні, і нападник не дістає ніякої переваги.
            if (!decided || cost_sum > best_cost) {
                best_cost = cost_sum;
                best_byte = static_cast<std::uint8_t>(candidate);
                decided = true;
            }
        }

        guess[position] = best_byte;
    }

    // Хвіст зібрано, а прийняття не було — питаємо приймач прямо.
    if (oracle.ask(guess).accepted) {
        return Recovered{guess, spent()};
    }
    return std::unexpected(Rejected{guess, spent()});
}

}  // namespace ct
