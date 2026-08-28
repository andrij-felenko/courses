// C++ контракт інтерфейсу стадії посередництва
enum class StageResult {
    Continue,      // Успішна обробка, передати конверт наступній стадії
    Filtered,      // Повідомлення відсіяно фільтром (нормальне завершення)
    Fault,         // Виникла непереборна помилка обробки
    Retry,         // Тимчасовий збій, запит на повторну спробу
    AsyncSuspend   // Асинхронна пауза (очікування I/O або сигналу події)
};

class IPipelineStage {
public:
    virtual ~IPipelineStage() = default;
    
    // Унікальне ім'я стадії для метрик, трасування та конфігурації
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    
    // Ініціалізація внутрішніх ресурсів стадії
    virtual bool initialize(const StageConfig& config) = 0;
    
    // Головний метод обробки повідомлення
    virtual StageResult process(Exchange& exchange) = 0;
    
    // Коректне звільнення ресурсів при зупинці конвеєра (Graceful Shutdown)
    virtual void destroy() noexcept = 0;
};
