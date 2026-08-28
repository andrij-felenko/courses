enum class AdapterState {
    STOPPED,        // Адаптер ініціалізовано, але з'єднання не відкриті
    CONNECTING,     // Триває встановлення TCP-сесії, TLS та аутентифікація
    RUNNING,        // Активне вичитування повідомлень і передача воркерам
    PAUSED,         // Тимчасова зупинка вичитування через протитиск або спрацювання запобіжника
    RECONNECTING,   // Втрата зв'язку: триває експоненційне очікування перед новою спробою
    DRAINING        // Зупинка: нові пакети не приймаються, триває завершення активних задач
};

class IChannelAdapterLifecycle {
public:
    virtual ~IChannelAdapterLifecycle() = default;

    // Відкриття з'єднань, реєстрація споживачів та запуск диспетчера
    virtual void start() = 0;

    // Тимчасове призупинення вичитування сокета (Backpressure / Circuit Breaker)
    virtual void pause() = 0;

    // Відновлення вичитування після нормалізації черг або відновлення БД
    virtual void resume() = 0;

    // Безпечне дренування активних завдань і плавне закриття ресурсів
    virtual void stop(std::chrono::milliseconds drain_timeout) = 0;

    // Отримання поточного стану автомата
    virtual AdapterState getState() const = 0;
};
