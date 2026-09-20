#include "sql_order_adapter.hpp"

#include <algorithm>
#include <cmath>
#include <sstream>
#include <stdexcept>

SqlOrderFulfillmentAdapter::SqlOrderFulfillmentAdapter(size_t batch_size)
    : batch_size_(batch_size == 0 ? 1 : batch_size) {}

std::optional<Order> SqlOrderFulfillmentAdapter::fetchNextPendingOrder() {
    // Якщо локальний буфер партії порожній — виконуємо наступний пакетний SQL-запит
    if (prefetch_buffer_.empty()) {
        executeSqlBatchFetch();
    }

    if (prefetch_buffer_.empty()) {
        return std::nullopt;
    }

    Order next_order = std::move(prefetch_buffer_.front());
    prefetch_buffer_.pop_front();
    return next_order;
}

void SqlOrderFulfillmentAdapter::executeSqlBatchFetch() {
    // Симуляція SQL-запиту:
    // SELECT * FROM orders WHERE status_code = 'PENDING' ORDER BY db_id LIMIT :batch_size;
    std::vector<RelationalRow*> pending_rows;
    for (auto& [uuid, row] : database_table_) {
        if (row.status_code == "PENDING") {
            pending_rows.push_back(&row);
        }
    }

    if (pending_rows.empty()) {
        return;
    }

    // Детерміноване сортування за первинним ключем таблиці (ORDER BY db_id ASC)
    std::sort(pending_rows.begin(), pending_rows.end(), [](const RelationalRow* a, const RelationalRow* b) {
        return a->db_id < b->db_id;
    });

    // Обмежуємо партію лімітом batch_size_
    const size_t fetch_count = std::min(batch_size_, pending_rows.size());
    ++batch_fetch_execution_count_;

    for (size_t i = 0; i < fetch_count; ++i) {
        RelationalRow* row = pending_rows[i];

        // Фіксуємо версію рядка на момент читання для захисту від колізій
        tracked_row_versions_[row->order_uuid] = row->row_version;

        // Позначаємо рядок у сховищі як взятий у комплектацію (PROCESSING)
        row->status_code = "PROCESSING";

        // Транслюємо реляційні колонки у доменну сутність та додаємо в буфер
        prefetch_buffer_.push_back(mapRowToDomain(*row));
    }
}

void SqlOrderFulfillmentAdapter::save(const Order& order) {
    const std::string& uuid = order.id().value();
    auto it = database_table_.find(uuid);
    if (it == database_table_.end()) {
        throw std::runtime_error(
            "SQL помилка: запис для замовлення " + uuid + " не знайдено в реляційній таблиці."
        );
    }

    RelationalRow& row = it->second;

    // Захист від колізій (Optimistic Concurrency Control / Collision Protection):
    // Перевіряємо, чи не було рядок змінено іншою транзакцією з моменту вибірки
    auto version_it = tracked_row_versions_.find(uuid);
    const int32_t expected_version = (version_it != tracked_row_versions_.end())
                                         ? version_it->second
                                         : row.row_version;

    if (row.row_version != expected_version) {
        throw std::runtime_error(
            "SQL колізія: рядок замовлення " + uuid +
            " було модифіковано паралельною транзакцією (очікувана версія: " +
            std::to_string(expected_version) + ", поточна версія в БД: " +
            std::to_string(row.row_version) + ")."
        );
    }

    // Симуляція виконання SQL-запиту:
    // UPDATE orders SET status_code = :status, total_cents = :cents,
    // row_version = row_version + 1 WHERE order_uuid = :uuid AND row_version = :expected_version;
    switch (order.status()) {
        case OrderStatus::Pending:
            row.status_code = "PENDING";
            break;
        case OrderStatus::Processing:
            row.status_code = "PROCESSING";
            break;
        case OrderStatus::Fulfilled:
            row.status_code = "FULFILLED";
            break;
        case OrderStatus::Failed:
            row.status_code = "FAILED";
            break;
    }

    // Мапінг доменного числа у копійки реляційної таблиці
    row.total_cents = static_cast<int64_t>(std::round(order.totalAmount() * 100.0));

    // Інкремент версії для захисту від майбутніх колізій
    row.row_version++;
    tracked_row_versions_[uuid] = row.row_version;
}

std::optional<Order> SqlOrderFulfillmentAdapter::findById(const OrderId& id) {
    auto it = database_table_.find(id.value());
    if (it == database_table_.end()) {
        return std::nullopt;
    }
    return mapRowToDomain(it->second);
}

Order SqlOrderFulfillmentAdapter::mapRowToDomain(const RelationalRow& row) const {
    // 1. Десеріалізація CSV рядка товарів
    std::vector<std::string> items;
    std::stringstream ss(row.items_csv);
    std::string item;
    while (std::getline(ss, item, ',')) {
        if (!item.empty()) {
            items.push_back(item);
        }
    }

    // 2. Трансляція коду статусу таблиці в доменний OrderStatus
    OrderStatus domain_status = OrderStatus::Pending;
    if (row.status_code == "PROCESSING") {
        domain_status = OrderStatus::Processing;
    } else if (row.status_code == "FULFILLED") {
        domain_status = OrderStatus::Fulfilled;
    } else if (row.status_code == "FAILED") {
        domain_status = OrderStatus::Failed;
    }

    // 3. Конвертація цілих копійок у дійсне число грошового значення
    const double amount = static_cast<double>(row.total_cents) / 100.0;

    return Order(OrderId(row.order_uuid), row.customer_name, amount, std::move(items), domain_status);
}

void SqlOrderFulfillmentAdapter::insertDirectRow(RelationalRow row) {
    tracked_row_versions_[row.order_uuid] = row.row_version;
    database_table_.insert_or_assign(row.order_uuid, std::move(row));
}

std::optional<SqlOrderFulfillmentAdapter::RelationalRow>
SqlOrderFulfillmentAdapter::queryDirectRow(const std::string& order_uuid) const {
    auto it = database_table_.find(order_uuid);
    if (it == database_table_.end()) {
        return std::nullopt;
    }
    return it->second;
}

size_t SqlOrderFulfillmentAdapter::totalTableRows() const noexcept {
    return database_table_.size();
}

size_t SqlOrderFulfillmentAdapter::batchFetchExecutionCount() const noexcept {
    return batch_fetch_execution_count_;
}

size_t SqlOrderFulfillmentAdapter::activePrefetchBufferSize() const noexcept {
    return prefetch_buffer_.size();
}
