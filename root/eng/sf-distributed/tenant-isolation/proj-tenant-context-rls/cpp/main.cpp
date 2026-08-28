#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <format>
#include <utility>

// Незмінний контекст орендаря для поточного запиту
class TenantContext {
public:
    explicit TenantContext(std::string tenant_id)
        : tenant_id_(std::move(tenant_id)) {
        if (tenant_id_.empty()) {
            throw std::invalid_argument("Tenant ID cannot be empty");
        }
    }

    [[nodiscard]] std::string_view tenant_id() const noexcept {
        return tenant_id_;
    }

private:
    std::string tenant_id_;
};

// Імітація низькорівневого клієнта підключення до PostgreSQL
class DbConnection {
public:
    void execute(std::string_view sql) {
        std::cout << "  [SQL Exec]: " << sql << "\n";
    }

    void begin_transaction() {
        execute("BEGIN;");
    }

    void commit() {
        execute("COMMIT;");
    }

    void rollback() {
        execute("ROLLBACK;");
    }
};

// RAII-обгортка транзакції, що гарантує встановлення та автоматичне скидання RLS
class TenantScopedTransaction {
public:
    TenantScopedTransaction(std::shared_ptr<DbConnection> conn, const TenantContext& ctx)
        : conn_(std::move(conn)), active_(true) {
        if (!conn_) {
            throw std::runtime_error("Database connection cannot be null");
        }
        conn_->begin_transaction();
        
        // SET LOCAL обмежує дію змінної сесії виключно поточною транзакцією.
        // Це гарантує повне скидання контексту при поверненні з'єднання в пул.
        std::string set_tenant_sql = std::format(
            "SET LOCAL app.current_tenant_id = '{}';", ctx.tenant_id());
        conn_->execute(set_tenant_sql);
    }

    ~TenantScopedTransaction() {
        if (active_) {
            try {
                conn_->rollback();
            } catch (...) {
                // Деструктор ніколи не викидає винятків
            }
        }
    }

    void commit() {
        if (!active_) {
            throw std::logic_error("Transaction is already completed");
        }
        conn_->commit();
        active_ = false;
    }

    // Заборона копіювання для збереження суворої семантики володіння
    TenantScopedTransaction(const TenantScopedTransaction&) = delete;
    TenantScopedTransaction& operator=(const TenantScopedTransaction&) = delete;

    TenantScopedTransaction(TenantScopedTransaction&&) noexcept = default;
    TenantScopedTransaction& operator=(TenantScopedTransaction&&) noexcept = default;

private:
    std::shared_ptr<DbConnection> conn_;
    bool active_{false};
};

// Репозиторій сутностей із підтримкою багатоорендної ізоляції
class DocumentRepository {
public:
    explicit DocumentRepository(std::shared_ptr<DbConnection> conn)
        : conn_(std::move(conn)) {}

    void insert_document(const TenantContext& ctx, std::string_view title, std::string_view content) {
        TenantScopedTransaction tx(conn_, ctx);

        // SQL-запит передає tenant_id, який верифікується політикою RLS
        std::string sql = std::format(
            "INSERT INTO documents (tenant_id, title, content) VALUES ('{}', '{}', '{}');",
            ctx.tenant_id(), title, content);
        conn_->execute(sql);

        tx.commit();
    }

    void query_all_documents(const TenantContext& ctx) {
        TenantScopedTransaction tx(conn_, ctx);

        // Запит не містить явного 'WHERE tenant_id = ...' у прикладному коді.
        // Ядро СУБД на рівні RLS автоматично фільтрує лише рядки поточного орендаря!
        conn_->execute("SELECT id, title, content FROM documents;");

        tx.commit();
    }

private:
    std::shared_ptr<DbConnection> conn_;
};

int main() {
    auto conn = std::make_shared<DbConnection>();
    DocumentRepository repo(conn);

    std::cout << "=== Запит від Орендаря Alpha ===\n";
    TenantContext ctx_alpha("tenant-alpha-101");
    repo.insert_document(ctx_alpha, "Financial Report Q3", "Confidential balances");
    repo.query_all_documents(ctx_alpha);

    std::cout << "\n=== Запит від Орендаря Beta ===\n";
    TenantContext ctx_beta("tenant-beta-202");
    repo.query_all_documents(ctx_beta);

    return 0;
}
