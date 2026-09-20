#pragma once

#include "order_domain.hpp"

#include <cstdint>
#include <deque>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

/// @brief Вторинний persistence-адаптер реляційного сховища.
///
/// РОЛЬ АНТИКОРУПЦІЙНОГО ШАРУ (Anti-Corruption Layer):
/// 1. Реалізує чистий доменний контракт IOrderFulfillmentPort.
/// 2. Повністю інкапсулює всередині реляційну схему (SQL-колонки, первинні ключі db_id).
/// 3. Самостійно керує пакетами вибірки (batch fetching) з бази даних, приховуючи від
///    доменного ядра технічну оптимізацію запитів.
/// 4. Захищає від колізій паралельного оновлення за допомогою версіонування рядків
///    (Optimistic Concurrency Control).
/// 5. Транслює сирі реляційні типи в доменні сутності та навпаки.
class SqlOrderFulfillmentAdapter : public IOrderFulfillmentPort {
public:
    /// @brief Реляційний рядок таблиці `orders` у базі даних.
    struct RelationalRow {
        int64_t db_id{0};             ///< Первинний ключ таблиці (BIGINT PRIMARY KEY)
        std::string order_uuid;       ///< Бізнес-ідентифікатор (VARCHAR(64))
        std::string customer_name;    ///< Ім'я замовника (VARCHAR(128))
        int64_t total_cents{0};       ///< Сума в копійках для реляційного обліку (BIGINT)
        std::string status_code;      ///< Рядковий статус: "PENDING", "PROCESSING", "FULFILLED"
        int32_t row_version{1};       ///< Версія рядка для захисту від колізій (Optimistic Lock)
        std::string items_csv;        ///< Список товарів у форматі CSV у колонці таблиці
    };

    /// @brief Створює SQL-адаптер із заданим розміром партії вибірки.
    /// @param batch_size Розмір партії запитів до СКБД для оптимізації читання.
    explicit SqlOrderFulfillmentAdapter(size_t batch_size = 2);

    ~SqlOrderFulfillmentAdapter() override = default;

    // --- Реалізація рольового контракту IOrderFulfillmentPort ---
    [[nodiscard]] std::optional<Order> fetchNextPendingOrder() override;
    void save(const Order& order) override;
    [[nodiscard]] std::optional<Order> findById(const OrderId& id) override;

    // --- Методи наповнення та аудиту стану таблиці бази даних (для тестів) ---
    void insertDirectRow(RelationalRow row);
    [[nodiscard]] std::optional<RelationalRow> queryDirectRow(const std::string& order_uuid) const;
    [[nodiscard]] size_t totalTableRows() const noexcept;
    [[nodiscard]] size_t batchFetchExecutionCount() const noexcept;
    [[nodiscard]] size_t activePrefetchBufferSize() const noexcept;

private:
    /// @brief Виконує SQL-запит на вибірку наступної партії замовлень зі статусом PENDING.
    void executeSqlBatchFetch();

    /// @brief Перетворює рядок таблиці бази даних у доменну сутність Order.
    [[nodiscard]] Order mapRowToDomain(const RelationalRow& row) const;

    size_t batch_size_;
    size_t batch_fetch_execution_count_{0};

    /// @brief Внутрішній буфер попередньо завантажених із СКБД замовлень.
    std::deque<Order> prefetch_buffer_;

    /// @brief Симульована реляційна таблиця бази даних (персистентне сховище).
    std::unordered_map<std::string, RelationalRow> database_table_;

    /// @brief Збережені версії вичитаних рядків для перевірки колізій при збереженні.
    std::unordered_map<std::string, int32_t> tracked_row_versions_;
};
