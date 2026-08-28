enum class ClaimResult {
    ACQUIRED_NEW,       // Повідомлення нове: блокування захоплено, виконати бізнес-домен
    DUPLICATE_RESOLVED, // Повідомлення вже було успішно оброблено раніше -> негайний ACK
    IN_FLIGHT_CONFLICT  // Повідомлення прямо зараз обробляється іншим воркером -> відкласти
};

class IIdempotencyStore {
public:
    virtual ~IIdempotencyStore() = default;

    // Спроба атомарно захопити право на обробку Message-ID
    // lock_ttl захищає від вічного зависання при падінні процесу
    virtual ClaimResult tryClaim(
        const std::string& message_id,
        std::chrono::milliseconds lock_ttl
    ) = 0;

    // Фіксація успішної обробки з тривалим часом зберігання запису
    virtual void markProcessed(
        const std::string& message_id,
        std::chrono::milliseconds record_ttl
    ) = 0;

    // Звільнення блокування при помилці для дозволу повторних спроб
    virtual void releaseClaim(const std::string& message_id) = 0;
};
