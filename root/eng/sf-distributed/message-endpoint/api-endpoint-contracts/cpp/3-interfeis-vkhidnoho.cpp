#include <memory>
#include <string>
#include <exception>

// Дескриптор явного підтвердження обробки повідомлення
class IAcknowledgmentHandle {
public:
    virtual ~IAcknowledgmentHandle() = default;

    // Успішна фіксація: видалити повідомлення з черги брокера (Commit/ACK)
    virtual void ack() = 0;

    // Тимчасова відмова: повернути повідомлення в чергу для повторної спроби (NACK/Requeue)
    virtual void nack(bool requeue, const std::string& reason) = 0;

    // Фатальна помилка (отруйний пакет): перемістити повідомлення в Dead-Letter Queue (DLQ)
    virtual void rejectToDlq(const std::string& error_code, const std::string& error_details) = 0;
};

// Інтерфейс зворотного виклику для вхідних бізнес-повідомлень
template <typename TPayload>
class IMessageListener {
public:
    virtual ~IMessageListener() = default;

    // Викликається воркером при успішній десеріалізації вхідного повідомлення
    virtual void onMessage(
        const Message<TPayload>& message,
        std::unique_ptr<IAcknowledgmentHandle> ack_handle
    ) = 0;

    // Викликається при пошкодженні даних, невідомому форматі або помилці схеми
    virtual void onSystemError(
        const std::string& raw_payload_bytes,
        const MessageHeaders& raw_headers,
        const std::exception& error,
        std::unique_ptr<IAcknowledgmentHandle> ack_handle
    ) = 0;
};
