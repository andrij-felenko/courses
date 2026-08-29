/*
 * frame_pipeline.cpp — той самий конвеєр кадрів на C++20.
 *
 * Арена під тимчасове, пул під сесії, володіння виражене unique_ptr.
 * Динамічної пам'яті немає: обидва сховища — поля об'єкта вузла.
 * Вивід через <iostream> — хостова демонстрація, у прошивці його не буде.
 */
#include "fixed_pool.hpp"
#include "memory_arena.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <span>
#include <string>
#include <string_view>

namespace {

inline constexpr std::size_t kMaxSessions = 8u;
inline constexpr std::size_t kArenaBytes  = 1024u;
inline constexpr std::size_t kKeyLen      = 32u;
inline constexpr std::size_t kHeaderLen   = 5u;   /* тип + номер сесії (big-endian) */
inline constexpr std::byte   kMask{0x5A};

struct ClientSession {
    std::uint32_t                  id{};
    std::uint32_t                  last_active_ms{};
    std::array<std::byte, kKeyLen> key{};
};

enum class FrameType : std::uint8_t { Open = 0x01, Data = 0x02, Close = 0x03 };

enum class FrameStatus {
    Ok,
    TooShort,
    ArenaFull,
    PoolExhausted,
    NoSession,
    Duplicate,
    BadType
};

[[nodiscard]] std::string_view describe(FrameStatus status) noexcept {
    switch (status) {
    case FrameStatus::Ok:            return "OK";
    case FrameStatus::TooShort:      return "кадр закороткий";
    case FrameStatus::ArenaFull:     return "арена переповнена";
    case FrameStatus::PoolExhausted: return "пул сесій вичерпано";
    case FrameStatus::NoSession:     return "невідома сесія";
    case FrameStatus::Duplicate:     return "сесія вже відкрита";
    case FrameStatus::BadType:       return "невідомий тип кадру";
    }
    return "?";
}

[[nodiscard]] std::uint32_t read_be32(std::span<const std::byte, 4> bytes) noexcept {
    return (std::to_integer<std::uint32_t>(bytes[0]) << 24) |
           (std::to_integer<std::uint32_t>(bytes[1]) << 16) |
           (std::to_integer<std::uint32_t>(bytes[2]) << 8) |
           std::to_integer<std::uint32_t>(bytes[3]);
}

}  // namespace

class TelemetryNode {
public:
    using Pool    = nofree::FixedPool<ClientSession, kMaxSessions>;
    using Session = Pool::UniquePtr;

    [[nodiscard]] FrameStatus process(std::span<const std::byte> frame,
                                      std::uint32_t              now_ms) noexcept {
        /* Межа кадру: усе тимчасове попереднього зникло одним рухом. */
        arena_.reset();

        if (frame.size() < kHeaderLen) {
            return FrameStatus::TooShort;
        }

        const auto type = static_cast<FrameType>(std::to_integer<std::uint8_t>(frame[0]));
        const auto id   = read_be32(frame.subspan<1, 4>());
        const auto body = frame.subspan(kHeaderLen);

        /* Мітка області: навіть якщо нижче спрацює будь-який ранній return,
           курсор арени повернеться сам. */
        auto guard = arena_.scope();

        std::span<std::byte> plain{};
        if (!body.empty()) {
            auto buffer = arena_.create_span<std::byte>(body.size());
            if (!buffer) {
                return FrameStatus::ArenaFull;   /* кадр більший за бюджет арени */
            }
            plain = *buffer;
            for (std::size_t i = 0u; i < body.size(); ++i) {
                plain[i] = body[i] ^ kMask;
            }
        }

        switch (type) {
        case FrameType::Open:   return open_session(id, plain, now_ms);
        case FrameType::Data:   return feed_session(id, plain, now_ms);
        case FrameType::Close:  return close_session(id);
        }
        return FrameStatus::BadType;
    }

    [[nodiscard]] std::size_t arena_peak() const noexcept { return arena_.peak_bytes(); }
    [[nodiscard]] std::size_t sessions_open() const noexcept {
        return pool_.capacity() - pool_.available();
    }
    [[nodiscard]] std::size_t worst_free_blocks() const noexcept { return pool_.min_available(); }

private:
    Pool                                  pool_{};
    nofree::MemoryArena<kArenaBytes>      arena_{};
    std::array<Session, kMaxSessions>     sessions_{};

    [[nodiscard]] Session *find(std::uint32_t id) noexcept {
        for (auto &slot : sessions_) {
            if (slot && slot->id == id) {
                return &slot;
            }
        }
        return nullptr;
    }

    [[nodiscard]] Session *free_slot() noexcept {
        for (auto &slot : sessions_) {
            if (!slot) {
                return &slot;
            }
        }
        return nullptr;
    }

    [[nodiscard]] FrameStatus open_session(std::uint32_t              id,
                                           std::span<const std::byte> plain,
                                           std::uint32_t              now_ms) noexcept {
        if (plain.size() < kKeyLen) {
            return FrameStatus::TooShort;
        }
        if (find(id) != nullptr) {
            return FrameStatus::Duplicate;
        }
        Session *slot = free_slot();
        if (slot == nullptr) {
            return FrameStatus::PoolExhausted;
        }

        auto session = pool_.make();
        if (!session) {
            return FrameStatus::PoolExhausted;   /* ліміт вичерпано — відмова, не аварія */
        }
        session->id             = id;
        session->last_active_ms = now_ms;
        std::copy_n(plain.begin(), kKeyLen, session->key.begin());

        *slot = std::move(session);              /* володіння переїхало в таблицю */
        return FrameStatus::Ok;
    }

    [[nodiscard]] FrameStatus feed_session(std::uint32_t              id,
                                           std::span<const std::byte> plain,
                                           std::uint32_t              now_ms) noexcept {
        Session *slot = find(id);
        if (slot == nullptr) {
            return FrameStatus::NoSession;
        }
        (*slot)->last_active_ms = now_ms;

        std::uint32_t sum = 0u;
        for (std::byte value : plain) {
            sum += std::to_integer<std::uint32_t>(value);
        }
        static_cast<void>(sum);
        return FrameStatus::Ok;
    }

    [[nodiscard]] FrameStatus close_session(std::uint32_t id) noexcept {
        Session *slot = find(id);
        if (slot == nullptr) {
            return FrameStatus::NoSession;
        }
        /* reset() кличе видаляч: деструктор відпрацював, блок повернувся в пул. */
        slot->reset();
        return FrameStatus::Ok;
    }
};

/* ------------------------------------------------------------------ */
/*  Демонстрація                                                        */
/* ------------------------------------------------------------------ */

namespace {

[[nodiscard]] std::span<std::byte> build_frame(std::span<std::byte>       out,
                                               FrameType                  type,
                                               std::uint32_t              id,
                                               std::span<const std::byte> body) noexcept {
    if (out.size() < kHeaderLen + body.size()) {
        return {};
    }
    out[0] = static_cast<std::byte>(type);
    out[1] = static_cast<std::byte>(id >> 24);
    out[2] = static_cast<std::byte>(id >> 16);
    out[3] = static_cast<std::byte>(id >> 8);
    out[4] = static_cast<std::byte>(id);
    for (std::size_t i = 0u; i < body.size(); ++i) {
        out[kHeaderLen + i] = body[i] ^ kMask;   /* «шифруємо» */
    }
    return out.subspan(0, kHeaderLen + body.size());
}

void run(TelemetryNode &node, std::string_view label,
         std::span<const std::byte> frame, std::uint32_t now_ms) {
    std::cout << label << " -> " << describe(node.process(frame, now_ms)) << '\n';
}

}  // namespace

int main() {
    static TelemetryNode                node;
    static std::array<std::byte, 2048>  rx{};
    static std::array<std::byte, kKeyLen> key{};
    static std::array<std::byte, 1500>  blob{};

    for (std::size_t i = 0u; i < key.size(); ++i) {
        key[i] = static_cast<std::byte>(0x40u + i);
    }
    blob.fill(std::byte{0x11});

    /* 1. Стільки сесій, скільки має пул, і ще одна зайва. */
    for (std::uint32_t id = 1u; id <= kMaxSessions + 1u; ++id) {
        auto frame = build_frame(rx, FrameType::Open, id, key);
        run(node, "OPEN сесія " + std::to_string(id), frame, id * 100u);
    }

    /* 2. Дані у відому й у невідому сесію. */
    run(node, "DATA сесія 3", build_frame(rx, FrameType::Data, 3u,
                                          std::span{blob}.first(200)), 1000u);
    run(node, "DATA сесія 42", build_frame(rx, FrameType::Data, 42u,
                                           std::span{blob}.first(8)), 1100u);

    /* 3. Закриття повертає блок у пул — слот знову вільний. */
    run(node, "CLOSE сесія 3", build_frame(rx, FrameType::Close, 3u, {}), 1200u);
    run(node, "OPEN сесія 9", build_frame(rx, FrameType::Open, 9u, key), 1300u);

    /* 4. Кадр, більший за арену: відмова, пам'ять ціла. */
    run(node, "DATA 1500 Б", build_frame(rx, FrameType::Data, 1u, blob), 1400u);

    /* 5. Обрубаний кадр. */
    run(node, "уламок 3 Б", std::span<const std::byte>{rx}.first(3), 1500u);

    std::cout << "Пул сесій:   зайнято " << node.sessions_open() << " з " << kMaxSessions
              << ", найгірший запас " << node.worst_free_blocks() << " блоків\n"
              << "Арена кадру: пік " << node.arena_peak() << " з " << kArenaBytes
              << " байтів (" << (node.arena_peak() * 100u / kArenaBytes) << "% бюджету)\n";
    return 0;
}
