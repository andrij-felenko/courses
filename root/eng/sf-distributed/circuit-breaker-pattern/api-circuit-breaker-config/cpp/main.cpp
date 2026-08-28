namespace resilience {

class ICircuitBreaker {
public:
    virtual ~ICircuitBreaker() = default;

    // Основний цикл виконання
    virtual bool allow_request() noexcept = 0;
    virtual void record_success(std::chrono::nanoseconds duration) noexcept = 0;
    virtual void record_error(std::chrono::nanoseconds duration, const std::exception& error) noexcept = 0;

    // Запит поточного стану та метрик
    virtual State get_state() const noexcept = 0;
    virtual Metrics get_metrics() const noexcept = 0;

    // Примусове операційне втручання
    virtual void transition_to_disabled_state() noexcept = 0;   // Запобіжник вимкнено (завжди пропускає)
    virtual void transition_to_forced_open_state() noexcept = 0; // Запобіжник примусово розімкнено (блокує все)
    virtual void reset() noexcept = 0;                          // Скидання статистики та повернення в CLOSED
};

} // namespace resilience
