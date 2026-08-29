#pragma once

#include <chrono>
#include <cmath>
#include <cstdint>
#include <span>

#include "edge/ring_buffer.hpp"
#include "edge/welford.hpp"

namespace edge {

/// Час у мілісекундах на 32 бітах — рівно те, що віддає лічильник тиків RTOS.
/// Тип свій, а не голий uint32_t: переплутати мітку часу з довжиною кадру
/// компілятор тепер не дасть, а обгортання на 49.7 добі лишається коректним,
/// бо різниця беззнакових представлень визначена стандартом.
using Millis = std::chrono::duration<std::uint32_t, std::milli>;

/// 32 вибірки на 100 Гц — 0.32 с сигналу ДО моменту аварії.
inline constexpr std::size_t snapshot_depth = 32;

enum class Action : std::uint8_t {
    Discard      = 0,  ///< у межах зони нечутливості — в ефір нічого
    Heartbeat    = 1,  ///< планове зведення норми або зсув понад deadband
    AnomalyAlarm = 2   ///< викид або відмова давача — термінова відправка
};

struct Report {
    Action action{Action::Discard};
    float  value{0.0f};
    float  mean{0.0f};
    float  stddev{0.0f};
    float  z{0.0f};
    Millis timestamp{0};
    bool   sensor_fault{false};
};

/**
 * Бортовий модуль: Велфорд, поріг за z, зона нечутливості, передісторія.
 * Пороги — static constexpr, а не поля: пристрій має один режим роботи,
 * і кожне налаштовуване поле коштувало б RAM, яка ніколи не змінюється.
 */
class AnomalyDetector {
public:
    static constexpr float         deadband             = 0.5f;
    static constexpr float         z_threshold          = 3.0f;
    static constexpr std::uint32_t min_training_samples = 30;
    static constexpr Millis        heartbeat_interval{60'000};

    explicit constexpr AnomalyDetector(Millis now) noexcept : last_heartbeat_{now} {}

    /// Уся робота на вибірку: сталий час, жодного звертання до купи.
    Report process(float sample, Millis now) noexcept
    {
        Report report;
        report.timestamp = now;
        report.value     = sample;

        // Відмова давача. NaN приходить з обірваного входу АЦП і з ділення на
        // нуль у калібрувальній формулі драйвера. Такій вибірці не місце ні в
        // статистиці, ні в передісторії — але мовчати про неї не можна:
        // непрацездатний давач це аварія, і про неї треба в ефір.
        if (!std::isfinite(sample)) {
            report.action       = Action::AnomalyAlarm;
            report.sensor_fault = true;
            report.mean         = stats_.mean();
            report.stddev       = stats_.stddev();
            last_heartbeat_     = now;
            return report;
        }

        // Передісторія пишеться ЗАВЖДИ, ще до рішень: заради викинутих
        // вибірок вона й існує.
        history_.push(sample);

        // Доки не набралося min_training_samples, оцінка дисперсії сміттєва,
        // і поріг по ній дав би хибні тривоги на перших секундах після старту.
        bool anomaly = false;
        float z = 0.0f;
        if (stats_.count() >= min_training_samples) {
            z = stats_.z_score(sample);
            anomaly = z > z_threshold;
        }

        // Модель норми вчиться лише на нормі. Пустити викиди в акумулятор —
        // роздути сигму серією аварійних коливань; поріг у три сигми
        // розповзеться, і наступний справжній дефект пройде як норма.
        if (!anomaly) {
            stats_.update(sample);
        }

        report.mean   = stats_.mean();
        report.stddev = stats_.stddev();
        report.z      = z;

        if (anomaly) {
            report.action   = Action::AnomalyAlarm;
            last_sent_      = sample;
            last_heartbeat_ = now;
            has_sent_       = true;
            return report;
        }

        // Дельта-стиснення рахує різницю з ОСТАННІМ ПЕРЕДАНИМ значенням, а не
        // з попередньою вибіркою: інакше повільний дрейф ніколи не перетнув би
        // поріг і хмара роками бачила б перше ж значення.
        const bool moved         = std::fabs(sample - last_sent_) >= deadband;
        const bool heartbeat_due = (now - last_heartbeat_) >= heartbeat_interval;

        if (!has_sent_ || moved || heartbeat_due) {
            report.action   = Action::Heartbeat;
            last_sent_      = sample;
            last_heartbeat_ = now;
            has_sent_       = true;
        } else {
            report.action = Action::Discard;
        }
        return report;
    }

    /// Лінійний знімок передісторії для аварійного пакета.
    [[nodiscard]] std::size_t snapshot(std::span<float> dest) const noexcept
    {
        return history_.copy_oldest_first(dest);
    }

    [[nodiscard]] const Welford& statistics() const noexcept { return stats_; }

    /// Диспетчер кличе це раз на добу: так модель відпускає повільний дрейф
    /// робочої точки (сезонний нагрів, зміна режиму навантаження).
    void reset(Millis now) noexcept
    {
        stats_.reset();
        history_.clear();
        last_sent_      = 0.0f;
        last_heartbeat_ = now;
        has_sent_       = false;
    }

private:
    Welford                              stats_{};
    RingBuffer<float, snapshot_depth>    history_{};
    float                                last_sent_{0.0f};
    Millis                               last_heartbeat_{0};
    bool                                 has_sent_{false};
};

}  // namespace edge
