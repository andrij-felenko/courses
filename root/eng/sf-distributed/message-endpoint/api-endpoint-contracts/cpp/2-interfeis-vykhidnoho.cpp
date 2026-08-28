#include <future>
#include <chrono>

template <typename TRequest, typename TResponse = void>
class IMessagingGateway {
public:
    virtual ~IMessagingGateway() = default;

    // Асинхронна одностороння публікація події (Fire-and-Forget)
    // Повертає future, який виконується після передачі в локальний буфер або Outbox.
    virtual std::future<void> sendAsync(const Message<TRequest>& message) = 0;

    // Синхронна відправка з очікуванням підтвердження від брокера
    // Блокує викликальний потік до отримання мережевого Publisher Confirm.
    virtual void sendSync(
        const Message<TRequest>& message,
        std::chrono::milliseconds timeout
    ) = 0;

    // Асинхронний запит-відповідь (Request-Reply)
    // Створює тимчасову чергу відповідей і повертає майбутній результат.
    virtual std::future<Message<TResponse>> sendAndReceiveAsync(
        const Message<TRequest>& request,
        std::chrono::milliseconds timeout
    ) = 0;
};
