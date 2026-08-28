namespace concurrency {

enum class Priority {
    Critical = 0,   // Авторизація, платіжні транзакції, Health Checks
    Standard = 1,   // Типові користувацькі операції читання та запису
    Background = 2  // Пакетні задачі, аналітика, оновлення індексів
};

struct RequestTelemetry {
    double duration_ms;       // Фактична тривалість обробки запиту
    bool is_success;          // Чи завершився запит успішно
    int http_status;          // Код відповіді HTTP або gRPC
    Priority priority;        // Пріоритет запиту
};

class ILimiterToken {
public:
    virtual ~ILimiterToken() = default;
    
    // Завершення обробки з явною передачею телеметрії
    virtual void complete(const RequestTelemetry& telemetry) = 0;
    
    // Скасування операції без врахування у вибірці затримок
    virtual void cancel() = 0;
};

class IAdaptiveConcurrencyLimiter {
public:
    virtual ~IAdaptiveConcurrencyLimiter() = default;

    // Спроба отримати допуск до виконання
    virtual std::unique_ptr<ILimiterToken> try_acquire(Priority priority) = 0;

    // Поточні показники стану для моніторингу
    virtual double get_current_limit() const noexcept = 0;
    virtual int get_in_flight() const noexcept = 0;
    virtual double get_min_rtt_ms() const noexcept = 0;
};

} // namespace concurrency
