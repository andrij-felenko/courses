#pragma once

#include <cstdint>
#include <string>
#include <vector>

/// @brief Коди помилок реляційної бази даних.
/// ВИТІК ДЕТАЛЕЙ (Smell): прикладний шар змушений обробляти технічні статуси СКБД.
enum class SqlErrorCode {
    Ok = 0,
    RowLockedByOtherTransaction = 101,
    DeadlockDetected = 102,
    RecordNotFound = 404,
    ConstraintViolation = 500,
    ConnectionLost = 503
};

/// @brief Сирий табличний запис замовлення у схемі реляційної бази даних.
/// ВИТІК ДЕТАЛЕЙ (Smell):
/// 1. Числовий первинний ключ db_id (BIGINT) замість семантичного OrderId.
/// 2. Сирі символьні масиви фіксованої довжини (VARCHAR) замість доменних типів.
/// 3. Сума в копійках/центах total_cents замість грошового типу або об'єкта-значення.
/// 4. Технічні поля оптимістичного блокування та ідентифікатори транзакцій СКБД.
struct LeakyOrderRecord {
    int64_t db_id{0};               ///< Числовий первинний ключ таблиці СКБД
    char external_uuid[64]{};       ///< Зовнішній UUID замовлення
    char customer_name[128]{};      ///< Колонка VARCHAR(128)
    int64_t total_cents{0};         ///< Сума замовлення в копійках (цілочисельне представлення)
    char status_code[32]{};         ///< Рядковий статус: "PENDING", "PROCESSING", "FULFILLED"
    int32_t lock_version{0};        ///< Технічна колонка версії для контролю конкурентності
    int64_t active_tx_id{0};        ///< Ідентифікатор транзакції СКБД
};

/// @brief Демонстраційний інтерфейс антипатерну: порт із «запахом сховища» (Port Smelling of Storage).
///
/// ПРИЧИНИ АРХІТЕКТУРНОГО ДЕФЕКТУ:
/// 1. Інтерфейс виглядає як абстракція, але диктується не потребами прикладного сценарію
///    (Use Case), а структурою таблиць реляційної бази даних.
/// 2. Пагінація СКБД (limit, offset) витікає в бізнес-сервіс, перекладаючи на нього
///    керування розбиттям на сторінки та ітерацією по базі.
/// 3. Витік понять блокування рядків (SELECT FOR UPDATE) та прапорців коміту транзакцій
///    змушує бізнес-логіку відповідати за транзакційну узгодженість СКБД.
/// 4. Порушує Dependency Inversion Principle (DIP): ядро стає жорстко зв'язаним із парадигмою SQL.
class ILeakyOrderStoragePort {
public:
    virtual ~ILeakyOrderStoragePort() = default;

    /// @brief ЗАПАХ СХОВИЩА: пагінація бази даних (limit, offset) та SQL-коди помилок у сигнатурі.
    virtual SqlErrorCode queryOrdersByStatus(const char* status_code,
                                            int limit,
                                            int offset,
                                            std::vector<LeakyOrderRecord>& out_records) = 0;

    /// @brief ЗАПАХ СХОВИЩА: ручне керування блокуванням реляційного рядка таблиці.
    virtual SqlErrorCode lockOrderRowForUpdate(int64_t db_id, bool with_wait, int timeout_ms) = 0;

    /// @brief ЗАПАХ СХОВИЩА: передача транзакційних прапорців (commit_transaction) у бізнес-виклику.
    virtual SqlErrorCode updateOrderRecord(const LeakyOrderRecord& record, bool commit_transaction) = 0;

    /// @brief ЗАПАХ СХОВИЩА: прямий запис у таблицю аудиту СКБД із числовим ID транзакції.
    virtual SqlErrorCode insertAuditLog(int64_t db_id, const char* message, int64_t transaction_id) = 0;
};
