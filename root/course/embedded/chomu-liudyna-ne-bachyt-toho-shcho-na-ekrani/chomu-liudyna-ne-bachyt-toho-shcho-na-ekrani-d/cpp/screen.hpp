#pragma once

#include <cstddef>
#include <deque>
#include <functional>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

#include "channel.hpp"

namespace gcs {

// Темна кабіна: у спокої екран мовчить сірим, колір з'являється лише на аномалію.
enum class State { Calm, Caution, Emergency };

// Незнищенне ядро (стан, режим, зв'язок, здоров'я) не ховається ніколи.
enum class Tier { Core, Secondary };

enum class Draw { Full, Dim, Hidden };
enum class Ink { Gray, Amber, Red };

struct Cell {
    std::string label;
    Draw draw{Draw::Full};
    Ink ink{Ink::Gray};
    std::string text;
};

struct Frame {
    State state{State::Calm};
    std::vector<Cell> cells;
    std::vector<std::string> banners;
    std::size_t bannersSuppressed{0};
    std::size_t hidden{0};
    bool flood{false};
};

class Screen {
public:
    // Канал живе довше за екран — власник каналів той, хто складає HUD.
    void addMetric(std::string label, Tier tier, const Channel& source);
    void addStatic(std::string label, Tier tier, std::string text);

    Frame render(Millis now);

private:
    // Джерело віджета: або канал, або статичний напис — без void* і тегів.
    using Source = std::variant<std::reference_wrapper<const Channel>, std::string>;

    struct Widget {
        std::string label;
        Tier tier{Tier::Secondary};
        Source source;
        Severity lastSeen{Severity::Normal};
    };

    [[nodiscard]] static const Channel* channelOf(const Widget& w) noexcept;
    [[nodiscard]] static Severity severityOf(const Widget& w) noexcept;
    [[nodiscard]] static std::string valueText(const Widget& w, Millis now);
    [[nodiscard]] static std::string bannerText(const Widget& w, Millis now);
    void advanceState(State target, Millis now) noexcept;
    void noteAlarm(Millis now);

    std::vector<Widget> widgets_;
    std::deque<Millis> alarmLog_;

    State state_{State::Calm};
    State pending_{State::Calm};
    Millis pendingSince_{0};

    static constexpr std::size_t kMaxBanners{3};       // більше трьох людина не читає
    static constexpr std::size_t kFloodLimit{10};      // EEMUA 191: понад 10 за вікно — лавина
    static constexpr Millis kFloodWindow{std::chrono::minutes{10}};
    static constexpr Millis kReleaseHold{std::chrono::seconds{5}};
};

std::string_view stateName(State s) noexcept;
std::string_view inkName(Ink c) noexcept;

} // namespace gcs
