# ⚙️ Реалізація наскрізної ізоляції орендарів та Row-Level Security

У пуловій архітектурі (Pool Model), де всі клієнти спільно використовують єдиний екземпляр реляційної СУБД, найбільшу небезпеку становить випадковий міжклієнтський витік даних (Cross-Tenant Data Leakage). У великих командах розробників покладання на людську дисципліну («пам'ятати про додавання предикату `WHERE tenant_id = ?` у кожен запит») неминуче дає збій. Достатньо одного забутого фільтра в аналітичному звіті, складного внутрішнього об'єднання `JOIN` або невірного налаштування зв'язків у ORM (Object-Relational Mapping), щоб клієнт отримав доступ до конфіденційних фінансових чи медичних записів сусіднього орендаря.

Єдиним надійним архітектурним рішенням є багаторівневий захист (Defense-in-Depth), де логічний контроль на рівні коду дублюється примусовою фільтрацією на рівні ядра бази даних за допомогою механізму **Row-Level Security (RLS)** у поєднанні з наскрізною передачею контексту через проміжне програмне забезпечення (Middleware).

---

## Архітектурний дизайн багаторівневої ізоляції

Схема захисту реалізує нерозривний ланцюг обробки контексту орендаря, що складається з трьох послідовних рівнів:

1. **Рівень HTTP/gRPC Middleware:** Перехоплює вхідний мережевий виклик, витягує верифікований `tenant_id` із токена безпеки (JWT) та зберігає його в незмінному локальному контексті поточного потоку або корутини (Thread-Local / Request Context).
2. **Рівень адаптера підключень до СУБД (Connection Hook):** Перед виконанням будь-яких прикладних операцій у межах відкритої транзакції виконує низькорівневу команду встановлення сесійної змінної `SET LOCAL app.current_tenant_id = '<id>';`.
3. **Рівень рушія бази даних (PostgreSQL RLS):** Двигун СУБД на рівні побудови дерева плану запиту автоматично інжектує перевірочний предикат у кожну команду `SELECT`, `UPDATE`, `DELETE` та перевіряє права під час виконання `INSERT`.

```sql
-- 1. Створення цільової таблиці зі стовпчиком орендаря
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

-- 2. Увімкнення механізму RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 3. Примусове застосування RLS навіть для власника таблиці (захист від обходу)
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- 4. Створення політики повної ізоляції операцій читання та модифікації
CREATE POLICY tenant_isolation_policy ON documents
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));
```

Директива `FORCE ROW LEVEL SECURITY` є критично важливою: за замовчуванням у PostgreSQL користувач, який створив таблицю (table owner), ігнорує власні політики RLS. Опція `FORCE` змушує планувальник застосовувати фільтрацію абсолютно для всіх непривілейованих ролей підключення додатку.

---

## Робоча реалізація мовами C++ та Go

Нижче наведено повноцінні, ідіоматичні реалізації наскрізного контексту та безпечної обгортки транзакцій для мов C++ (C++20 із застосуванням RAII та розумних вказівників) та Go (з використанням стандартного пакету `context` та HTTP-middleware).

:::tabs
```cpp
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
```
```go
package main

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"log"
	"net/http"
)

type contextKey string

const tenantContextKey contextKey = "tenantID"

// TenantMiddleware вилучає та валідує ідентифікатор орендаря з вхідного HTTP-запиту
func TenantMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tenantID := r.Header.Get("X-Tenant-ID")
		if tenantID == "" {
			http.Error(w, "Unauthorized: missing X-Tenant-ID", http.StatusUnauthorized)
			return
		}

		// Збереження ідентифікатора у незмінному контексті запиту
		ctx := context.WithValue(r.Context(), tenantContextKey, tenantID)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// GetTenantID витягує ідентифікатор орендаря з поточного контексту
func GetTenantID(ctx context.Context) (string, error) {
	val, ok := ctx.Value(tenantContextKey).(string)
	if !ok || val == "" {
		return "", errors.New("tenant context is missing in execution context")
	}
	return val, nil
}

// WithTenantTx відкриває транзакцію та безпечно встановлює змінну сесії RLS
func WithTenantTx(ctx context.Context, db *sql.DB, fn func(tx *sql.Tx) error) error {
	tenantID, err := GetTenantID(ctx)
	if err != nil {
		return err
	}

	tx, err := db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// SET LOCAL обмежує дію змінної сесії межами поточної транзакції
	setQuery := "SET LOCAL app.current_tenant_id = $1;"
	if _, err := tx.ExecContext(ctx, setQuery, tenantID); err != nil {
		return fmt.Errorf("failed to inject tenant session context: %w", err)
	}

	// Виконання прикладної бізнес-логіки
	if err := fn(tx); err != nil {
		return err
	}

	return tx.Commit()
}

// QueryTenantDocuments демонструє безпечне читання даних без ручного WHERE tenant_id
func QueryTenantDocuments(ctx context.Context, db *sql.DB) error {
	return WithTenantTx(ctx, db, func(tx *sql.Tx) error {
		// Запит не вимагає ручного фільтра: СУБД автоматично застосує RLS
		rows, err := tx.QueryContext(ctx, "SELECT id, title, content FROM documents;")
		if err != nil {
			return err
		}
		defer rows.Close()

		for rows.Next() {
			var id, title, content string
			if err := rows.Scan(&id, &title, &content); err != nil {
				return err
			}
			fmt.Printf("Document retrieved: [%s] %s\n", id, title)
		}
		return rows.Err()
	})
}

func main() {
	fmt.Println("Мультиарендний сервіс із підтримкою RLS успішно ініціалізовано.")
}
```
:::

---

## Внутрішня механіка PostgreSQL та оптимізація кешу планів

Коли додаток використовує підготовлені запити (Prepared Statements) разом із RLS, виникає тонка взаємодія між кешем планів запитів та сесійними змінними:

### 1. Кешування планів виконання (Prepared Statement Plan Cache)

PostgreSQL підтримує два типи планів для підготовлених викликів: кастомні плани (Custom Plans), побудовані під конкретні значення параметрів, та загальні плани (Generic Plans), які використовуються повторно незалежно від параметрів. Політика RLS використовує вираз `current_setting('app.current_tenant_id')`. Оскільки це функція з категорією мінливості `STABLE`, оптимізатор PostgreSQL знає, що її результат є константним у межах одного запиту, але може змінюватися між транзакціями.

Завдяки цьому планувальник будує загальний параметризований план із безпечним індексним скануванням за стовпчиком `tenant_id`, запобігаючи деградації продуктивності при перемиканні сесій між орендарями.

### 2. Складені індекси B-Tree для таблиць під RLS

Оскільки кожен запит із RLS обов'язково фільтрується за `tenant_id`, структура всіх вторинних індексів повинна починатися з дискримінаційного стовпчика:

```sql
-- Ефективний складений індекс: спершу tenant_id, потім бізнес-поле
CREATE INDEX idx_documents_tenant_created 
ON documents (tenant_id, created_at DESC);
```

Якщо створити індекс лише за полем `created_at`, оптимізатор буде змушений сканувати глобальне B-дерево і відфільтровувати записи на фазі Heap Fetch, що при мільйонах записів у таблиці викликає різкий сплеск випадкового читання з диска.

---

## Аналіз типових архітектурних пасток та крайових випадків

Під час практичного розгортання RLS-ізоляції інженери найчастіше стикаються з чотирма критичними вразливостями:

1. **Забруднення сесій у пулі з'єднань (Connection Pool State Pollution):**
   Якщо виконати команду `SET app.current_tenant_id = 't1'` без ключового слова `LOCAL` або поза межами транзакції `BEGIN...COMMIT`, значення сесійної змінної залишиться закріпленим за конкретним фізичним TCP-сокетом. Коли це з'єднання повернеться в пул `pgbouncer` або HikariCP, наступний запит від орендаря `t2`, що отримає це ж з'єднання, автоматично прочитає або модифікує дані орендаря `t1`. Використання `SET LOCAL` всередині явної транзакції гарантує автоматичне очищення змінної в момент завершення транзакції.

2. **Небезпека підключення під правами суперкористувача (Superuser Bypass):**
   У реляційній базі даних PostgreSQL користувач `postgres` (Superuser) або ролі з атрибутом `BYPASSRLS` за замовчуванням повністю ігнорують усі політики безпеки рядків. Якщо мікросервіс підключається до бази під обліковим записом адміністратора, RLS вимикається непомітно для розробників. Додаток зобов'язаний підключатися під окремою службовою роллю (наприклад, `app_worker`), позбавленою привілеїв суперкористувача, а таблиці повинні містити декларацію `FORCE ROW LEVEL SECURITY`.

3. **Втрата контексту в асинхронних чергах та фонових завданнях:**
   Коли веб-сервіс ставить повідомлення в чергу Kafka або RabbitMQ для відкладеної обробки, HTTP-заголовки залишаються у завершеному HTTP-запиті. Якщо розробник не включить `tenant_id` у тіло (payload) або метадані самого повідомлення черги, фоновий обробник (Worker) виконає транзакцію з порожнім контекстом або впаде з помилкою. Архітектура повинна вимагати обов'язкової передачі контексту орендаря в кожній розподіленій події.

4. **Колізії ключів у розподіленому кеші Redis та Memcached:**
   Якщо зберігати об'єкти в кеші за простими ідентифікаторами сутностей (`user:1004`, `order:9912`), клієнти з однаковими внутрішніми автоінкрементними ID перезапишуть кеш один одного. Усі операції з кешем повинні використовувати строгу префіксацію: `tenant:<tenant_id>:<entity>:<id>`.
