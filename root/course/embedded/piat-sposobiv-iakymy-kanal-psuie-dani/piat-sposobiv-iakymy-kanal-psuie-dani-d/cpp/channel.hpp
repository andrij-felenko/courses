#pragma once

#include <array>
#include <optional>
#include <random>

#include "link.hpp"

// Імітатор фізичного каналу з усіма п'ятьма руйнівними режимами: спотворення бітів
// пачкою, втрата, дублювання, перевпорядкування і — на виході — розрізання
// та склеювання байтового потоку.
class Channel {
public:
    struct Profile {
        unsigned drop_permille{};       // завмирання, колізія, скидання апаратним FIFO
        unsigned duplicate_permille{};  // кадр пройшов лінією двічі
        unsigned reorder_permille{};    // кадр пропускає наступний уперед
        unsigned burst_permille{};      // пачка спотворених сусідніх бітів
    };

    struct Stats {
        std::uint32_t offered{};
        std::uint32_t dropped{};
        std::uint32_t corrupted{};
        std::uint32_t duplicated{};
        std::uint32_t reordered{};
        std::uint32_t overflow{};   // черга лінії переповнена
    };

    static constexpr std::size_t kStreamCap = 4096;
    static constexpr std::size_t kMaxChunk  = 24;

    Channel(Profile profile, std::uint32_t seed) : profile_(profile), rng_(seed) {}

    // Передавач віддає в канал готовий кадр разом із роздільником.
    void send(link::Bytes frame);

    // Приймач вичитує стільки, скільки встигло прийти: шматок довільного розміру.
    void pump(const link::ByteSink& sink);

    [[nodiscard]] bool idle() const noexcept { return stream_len_ == 0 && !held_; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    struct Packet {
        std::array<std::uint8_t, link::kMaxWire> bytes{};
        std::size_t                              len{0};
    };

    bool roll(unsigned permille);
    void corrupt_burst(std::span<std::uint8_t> data);
    void push(link::Bytes bytes);

    Profile      profile_;
    std::mt19937 rng_;

    std::array<std::uint8_t, kStreamCap> stream_{};   // байти в дорозі, кільцем
    std::size_t                          stream_head_{0};
    std::size_t                          stream_len_{0};

    std::optional<Packet> held_;   // затриманий кадр (перевпорядкування)
    Stats                 stats_{};
};
