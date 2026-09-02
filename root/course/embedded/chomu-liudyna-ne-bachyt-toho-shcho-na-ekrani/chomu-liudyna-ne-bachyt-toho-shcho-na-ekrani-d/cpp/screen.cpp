#include "screen.hpp"

#include <algorithm>
#include <format>
#include <limits>
#include <ranges>

namespace gcs {

void Screen::addMetric(std::string label, Tier tier, const Channel& source) {
    widgets_.push_back(Widget{std::move(label), tier, std::cref(source), Severity::Normal});
}

void Screen::addStatic(std::string label, Tier tier, std::string text) {
    widgets_.push_back(Widget{std::move(label), tier, std::move(text), Severity::Normal});
}

const Channel* Screen::channelOf(const Widget& w) noexcept {
    if (const auto* ref = std::get_if<std::reference_wrapper<const Channel>>(&w.source)) {
        return &ref->get();
    }
    return nullptr;
}

Severity Screen::severityOf(const Widget& w) noexcept {
    const Channel* c = channelOf(w);
    return c ? c->effectiveSeverity() : Severity::Normal;
}

std::string Screen::valueText(const Widget& w, Millis now) {
    const Channel* c = channelOf(w);
    if (c == nullptr) {
        return std::get<std::string>(w.source);
    }
    const float secs = std::chrono::duration<float>(c->silence(now)).count();
    if (c->stale()) {
        return std::format("{:.1f} {}  СТАРІ ДАНІ ({:.0f} с)", c->value(), c->unit(), secs);
    }
    const auto left = c->timeToLimit();
    const bool trending = c->limits().maxDriftRate > 0.0f &&
                          c->driftRate() >= c->limits().maxDriftRate * 0.5f && left.has_value();
    if (trending) {
        return std::format("{:.1f} {}  тренд {:.3f} {}/с  ліміт через {:.0f} с",
                           c->value(), c->unit(), c->driftRate(), c->unit(), left->count());
    }
    return std::format("{:.1f} {}", c->value(), c->unit());
}

std::string Screen::bannerText(const Widget& w, Millis now) {
    const Channel& c = *channelOf(w);
    if (c.stale()) {
        return std::format("!  {}: ДАНІ ЗАСТИГЛИ {:.0f} с — показник на екрані вже неправда",
                           w.label, std::chrono::duration<float>(c.silence(now)).count());
    }
    const auto left = c.timeToLimit();
    if (c.severity() == Severity::Critical && left && left->count() > 0.0f) {
        return std::format("!! {} {:.1f} {}: ліміт {:.1f} {} через {:.0f} с", w.label, c.value(),
                           c.unit(), c.limits().crit, c.unit(), left->count());
    }
    if (c.severity() == Severity::Critical) {
        return std::format("!! {} {:.1f} {}: за критичним лімітом {:.1f} {}", w.label, c.value(),
                           c.unit(), c.limits().crit, c.unit());
    }
    return std::format("!  {} {:.1f} {}: прихований дрейф {:.3f} {}/с", w.label, c.value(),
                       c.unit(), c.driftRate(), c.unit());
}

void Screen::noteAlarm(Millis now) {
    alarmLog_.push_back(now);
    while (!alarmLog_.empty() && now - alarmLog_.front() > kFloodWindow) {
        alarmLog_.pop_front();
    }
}

// Стан падає вниз лише після витримки: екран, що клацає туди-сюди, гірший за
// постійно аварійний — кожне перемальовування маскує решту змін на сітківці.
void Screen::advanceState(State target, Millis now) noexcept {
    if (target >= state_) {
        state_ = target;
        pending_ = target;
        pendingSince_ = now;
        return;
    }
    if (pending_ != target) {
        pending_ = target;
        pendingSince_ = now;
    } else if (now - pendingSince_ >= kReleaseHold) {
        state_ = target;
    }
}

Frame Screen::render(Millis now) {
    Frame frame;
    Severity worst = Severity::Normal;
    std::vector<std::size_t> alarming;

    // 1. Фронти тривог: лавину робить поява нових алярмів, а не їхня наявність.
    for (std::size_t i = 0; i < widgets_.size(); ++i) {
        Widget& w = widgets_[i];
        const Severity s = severityOf(w);
        if (s > w.lastSeen && s >= Severity::Warning) {
            noteAlarm(now);
        }
        w.lastSeen = s;
        worst = std::max(worst, s);
        if (s >= Severity::Warning) {
            alarming.push_back(i);
        }
    }
    while (!alarmLog_.empty() && now - alarmLog_.front() > kFloodWindow) {
        alarmLog_.pop_front();
    }
    frame.flood = alarmLog_.size() > kFloodLimit;

    // 2. Стан екрана.
    const State target = worst == Severity::Critical ? State::Emergency
                       : worst == Severity::Warning  ? State::Caution
                                                     : State::Calm;
    advanceState(target, now);
    frame.state = state_;

    // 3. Розхаращення: аварія забирає весь фовеальний бюджет собі.
    frame.cells.reserve(widgets_.size());
    for (const Widget& w : widgets_) {
        const Severity s = severityOf(w);
        Cell cell;
        cell.label = w.label;
        cell.ink = s == Severity::Critical ? Ink::Red : s == Severity::Warning ? Ink::Amber : Ink::Gray;
        cell.text = valueText(w, now);

        if (s >= Severity::Warning || w.tier == Tier::Core) {
            cell.draw = Draw::Full;
        } else if (state_ == State::Emergency) {
            cell.draw = Draw::Hidden;
            ++frame.hidden;
        } else if (state_ == State::Caution) {
            cell.draw = Draw::Dim;
        }
        frame.cells.push_back(std::move(cell));
    }

    // 4. Банери: спершу критичні, серед рівних — ті, до чийого ліміту ближче.
    std::ranges::sort(alarming, [this](std::size_t a, std::size_t b) {
        const Severity sa = severityOf(widgets_[a]);
        const Severity sb = severityOf(widgets_[b]);
        if (sa != sb) {
            return sa > sb;
        }
        const auto secs = [this](std::size_t i) {
            const auto left = channelOf(widgets_[i])->timeToLimit();
            return left ? left->count() : std::numeric_limits<float>::infinity();
        };
        return secs(a) < secs(b);
    });

    for (std::size_t rank = 0; rank < alarming.size(); ++rank) {
        if (rank < kMaxBanners) {
            frame.banners.push_back(bannerText(widgets_[alarming[rank]], now));
        } else {
            ++frame.bannersSuppressed;   // решта згортається в один підсумковий рядок
        }
    }
    return frame;
}

std::string_view stateName(State s) noexcept {
    switch (s) {
    case State::Emergency: return "АВАРІЯ";
    case State::Caution:   return "увага";
    default:               return "спокій";
    }
}

std::string_view inkName(Ink c) noexcept {
    switch (c) {
    case Ink::Red:   return "red";
    case Ink::Amber: return "amber";
    default:         return "gray";
    }
}

} // namespace gcs
