namespace truetime {

class ITimeService {
public:
    virtual ~ITimeService() = default;

    /* Повертає поточний довірчий інтервал часу */
    [[nodiscard]] virtual Interval now() const = 0;

    /* Перевірка настання моменту в минулому */
    [[nodiscard]] virtual bool after(Nanoseconds target_time) const = 0;

    /* Перевірка знаходження моменту в майбутньому */
    [[nodiscard]] virtual bool before(Nanoseconds target_time) const = 0;

    /* Бар'єр Commit Wait */
    virtual void commit_wait(Nanoseconds commit_timestamp) const = 0;

    /* Отримання повної діагностики підсистеми */
    [[nodiscard]] virtual Diagnostics get_diagnostics() const = 0;
};

} // namespace truetime
