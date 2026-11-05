#pragma once

#include <chrono>
#include <cstdint>
#include <string_view>
#include <vector>

/**
 * @brief Клас для діагностики та моніторингу стабільності електричного контакту Pogo Pin.
 * 
 * Здійснює детектування короткочасних розмикань (мікророзривів), фільтрацію брязкоту
 * та підрахунок кумулятивної статистики надійності при вібраційних тестах.
 */
class PogoPinContactMonitor {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;
    using Microseconds = std::chrono::microseconds;

    /**
     * @brief Конфігураційні параметри аналізу контакту.
     */
    struct Config {
        Microseconds min_glitch_duration{10};  ///< Мінімальна тривалість збою для фіксації (мкс)
        Microseconds noise_filter_threshold{2}; ///< Поріг відсікання високочастотного шуму (мкс)
    };

    /**
     * @brief Запис про окрему подію розмикання контакту.
     */
    struct GlitchEvent {
        TimePoint timestamp;     ///< Момент початку розмикання
        Microseconds duration;   ///< Тривалість відсутності контакту
    };

    /**
     * @brief Зведена статистика випробування на вібростійкість.
     */
    struct Report {
        size_t total_glitch_count{0};     ///< Кількість зафіксованих мікророзривів
        Microseconds total_loss_time{0};  ///< Сумарний час розриву ланцюга
        Microseconds max_glitch_time{0};  ///< Найтриваліший зареєстрований розрив
        double failure_rate_percent{0.0}; ///< Відсоток втрати контакту від загального часу тесту
    };

    explicit PogoPinContactMonitor(Config config = Config{});

    /**
     * @brief Реєструє зміну фізичного стану контакту.
     * @param closed true, якщо контакт замкнений (пружина притиснута), false при розриві.
     * @param now Часова мітка події (за замовчуванням Clock::now()).
     */
    void registerEdge(bool closed, TimePoint now = Clock::now());

    /**
     * @brief Завершує тестову сесію та розраховує підсумкові метрики.
     * @param total_test_duration Загальна тривалість випробування.
     * @return Зведена статистика надійності контакту.
     */
    Report finalizeReport(Microseconds total_test_duration);

    /**
     * @brief Виводить форматований діагностичний звіт у стандартний потік виводу.
     * @param report Розрахований звіт випробування.
     */
    void printReport(const Report& report) const;

    [[nodiscard]] const std::vector<GlitchEvent>& getEvents() const noexcept { return events_; }
    [[nodiscard]] bool isCurrentlyClosed() const noexcept { return is_closed_; }

private:
    Config config_;
    bool is_closed_{true};
    TimePoint last_transition_time_{Clock::now()};
    std::vector<GlitchEvent> events_;
};
