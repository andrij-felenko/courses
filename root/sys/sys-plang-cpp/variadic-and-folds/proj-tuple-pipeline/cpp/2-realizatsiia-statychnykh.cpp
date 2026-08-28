// Фільтр 1: Перевірка валідності часової мітки (застосовується до всіх подій)
struct TimestampFilter {
    uint64_t min_allowed_time;

    template <typename Event>
    constexpr bool operator()(const Event& event) const noexcept {
        return event.timestamp >= min_allowed_time;
    }
};

// Фільтр 2: Перевірка параметрів живлення (діє виключно на TelemetryEvent)
struct PowerFilter {
    double max_voltage;
    double max_current;

    constexpr bool operator()(const TelemetryEvent& telemetry) const noexcept {
        return telemetry.voltage <= max_voltage && 
               telemetry.current <= max_current && 
               telemetry.current >= 0.0;
    }

    template <typename OtherEvent>
    constexpr bool operator()(const OtherEvent&) const noexcept {
        return true; // Інші події не підлягають перевірці живлення
    }
};

// Фільтр 3: Перевірка пріоритету команд (діє виключно на CommandEvent)
struct CommandPriorityFilter {
    int min_priority;

    constexpr bool operator()(const CommandEvent& cmd) const noexcept {
        return cmd.priority >= min_priority;
    }

    template <typename OtherEvent>
    constexpr bool operator()(const OtherEvent&) const noexcept {
        return true;
    }
};
