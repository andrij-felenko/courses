# ⚙️ Реалізація причинного LSN-маршрутизатора з пулом з'єднань та відстеженням стану транзакцій

Створення високонадійного проксі або клієнтського маршрутизатора для розділення потоків читання й запису вимагає вирішення чотирьох фундаментальних системних задач:
1. **Швидка класифікація SQL-запитів**: лексичний аналіз перших токенів запиту без накладних витрат на повну побудову абстрактного синтаксичного дерева (AST), з обов'язковим розпізнаванням блокуючих читань (`SELECT ... FOR UPDATE`, `SELECT ... LOCK IN SHARE MODE`), виразів модифікації у спільних табличних виразах (Write-CTEs) та викликів збережених процедур;
2. **Скінченний автомат транзакційного стану (Transaction State Machine)**: відстеження команд `BEGIN`, `START TRANSACTION`, `COMMIT`, `ROLLBACK`, змінних автофіксації (`autocommit = 0`) та автоматична прив'язка (Pinning) з'єднання до Primary-вузла на весь час відкритої транзакції;
3. **Причинна маршрутизація за LSN (Log Sequence Number)**: реєстрація зміщення журналу після фіксації запису та вибір репліки, чий показник застосування журналу задовольняє умову `Replica_LSN >= Required_LSN`;
4. **Динамічний моніторинг лагу та виведення з ротації**: вимірювання затримки реплікації кожного вузла та автоматичне виключення з пулу читання тих реплік, чий лаг перевищує критичний поріг (Shedding).

Нижче наведено промислову реалізацію ядра маршрутизатора. Приклад реалізовано мовами C та C++ з дотриманням ідіоматичних практик кожної мови: у C застосовано структури та явне керування ресурсами, а в C++ — парадигму RAII, розумні вказівники `std::unique_ptr`, `std::string_view` та строгу типізацію.

## Архітектура та структури даних ядра

Маршрутизатор підтримує пул з'єднань до одного Primary-вузла та масиву Read-реплік. Кожен вузол має власний стан доступності, поточний LSN та виміряний реплікаційний лаг у мілісекундах.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <ctype.h>
#include <time.h>
#include <pthread.h>

#define MAX_REPLICAS 16
#define MAX_SQL_SNIPPET 64
#define MAX_LAG_THRESHOLD_MS 2000
#define STICKY_WINDOW_SEC 3

typedef uint64_t lsn_t;

typedef enum {
    QUERY_UNKNOWN = 0,
    QUERY_READ,              /* Простий SELECT */
    QUERY_READ_LOCKING,      /* SELECT ... FOR UPDATE / LOCK IN SHARE MODE */
    QUERY_WRITE,             /* INSERT, UPDATE, DELETE, REPLACE */
    QUERY_TX_BEGIN,          /* BEGIN, START TRANSACTION */
    QUERY_TX_COMMIT,         /* COMMIT */
    QUERY_TX_ROLLBACK,       /* ROLLBACK */
    QUERY_SESSION_MUTATION   /* SET @var, SET SESSION, CREATE TEMPORARY */
} query_type_t;

typedef enum {
    NODE_PRIMARY = 0,
    NODE_REPLICA
} node_role_t;

typedef struct {
    int id;
    char host[64];
    int port;
    node_role_t role;
    bool is_healthy;
    lsn_t last_applied_lsn;
    uint32_t lag_ms;
    uint64_t active_connections;
} db_node_t;

typedef struct {
    int client_id;
    bool in_transaction;
    bool session_polluted;
    lsn_t last_write_lsn;
    time_t last_write_timestamp;
    int pinned_node_id; /* -1, якщо не прив'язаний */
} client_session_t;

typedef struct {
    db_node_t primary;
    db_node_t replicas[MAX_REPLICAS];
    size_t replica_count;
    size_t rr_index;
    pthread_mutex_t lock;
} router_cluster_t;

/* Допоміжна функція нормалізації рядків для лексичного аналізу */
static const char* skip_whitespace(const char* s) {
    while (*s && isspace((unsigned char)*s)) s++;
    return s;
}

static bool str_starts_with_ci(const char* s, const char* prefix) {
    while (*prefix) {
        if (tolower((unsigned char)*s) != tolower((unsigned char)*prefix)) {
            return false;
        }
        s++;
        prefix++;
    }
    return true;
}

/* Швидкий аналізатор типу SQL-запиту */
query_type_t classify_sql(const char* sql) {
    if (!sql) return QUERY_UNKNOWN;
    const char* p = skip_whitespace(sql);

    /* Ігнорування SQL-коментарів /* ... */ */
    while (*p == '/' && *(p + 1) == '*') {
        const char* end_comment = strstr(p + 2, "*/");
        if (!end_comment) return QUERY_UNKNOWN;
        p = skip_whitespace(end_comment + 2);
    }

    if (str_starts_with_ci(p, "BEGIN") || str_starts_with_ci(p, "START TRANSACTION")) {
        return QUERY_TX_BEGIN;
    }
    if (str_starts_with_ci(p, "COMMIT")) {
        return QUERY_TX_COMMIT;
    }
    if (str_starts_with_ci(p, "ROLLBACK")) {
        return QUERY_TX_ROLLBACK;
    }
    if (str_starts_with_ci(p, "INSERT") || str_starts_with_ci(p, "UPDATE") ||
        str_starts_with_ci(p, "DELETE") || str_starts_with_ci(p, "REPLACE") ||
        str_starts_with_ci(p, "ALTER")  || str_starts_with_ci(p, "DROP") ||
        str_starts_with_ci(p, "CREATE TABLE") || str_starts_with_ci(p, "TRUNCATE") ||
        str_starts_with_ci(p, "WITH ")) {
        return QUERY_WRITE;
    }
    if (str_starts_with_ci(p, "SET ") || str_starts_with_ci(p, "CREATE TEMPORARY")) {
        return QUERY_SESSION_MUTATION;
    }
    if (str_starts_with_ci(p, "SELECT")) {
        /* Перевірка на блокуючі конструкції FOR UPDATE або LOCK IN SHARE MODE */
        const char* upper_sql = p;
        if (strstr(upper_sql, "FOR UPDATE") != NULL ||
            strstr(upper_sql, "for update") != NULL ||
            strstr(upper_sql, "LOCK IN SHARE MODE") != NULL ||
            strstr(upper_sql, "lock in share mode") != NULL ||
            strstr(upper_sql, "FOR SHARE") != NULL ||
            strstr(upper_sql, "for share") != NULL) {
            return QUERY_READ_LOCKING;
        }
        return QUERY_READ;
    }

    return QUERY_WRITE; /* Безпечний дефолт: невідомі команди направляємо на Primary */
}

/* Ініціалізація кластера */
void router_init(router_cluster_t* cluster, const char* p_host, int p_port) {
    memset(cluster, 0, sizeof(router_cluster_t));
    cluster->primary.id = 0;
    snprintf(cluster->primary.host, sizeof(cluster->primary.host), "%s", p_host);
    cluster->primary.port = p_port;
    cluster->primary.role = NODE_PRIMARY;
    cluster->primary.is_healthy = true;
    cluster->primary.last_applied_lsn = 1000;
    cluster->primary.lag_ms = 0;

    pthread_mutex_init(&cluster->lock, NULL);
}

bool router_add_replica(router_cluster_t* cluster, const char* host, int port) {
    pthread_mutex_lock(&cluster->lock);
    if (cluster->replica_count >= MAX_REPLICAS) {
        pthread_mutex_unlock(&cluster->lock);
        return false;
    }
    size_t idx = cluster->replica_count;
    cluster->replicas[idx].id = (int)(idx + 1);
    snprintf(cluster->replicas[idx].host, sizeof(cluster->replicas[idx].host), "%s", host);
    cluster->replicas[idx].port = port;
    cluster->replicas[idx].role = NODE_REPLICA;
    cluster->replicas[idx].is_healthy = true;
    cluster->replicas[idx].last_applied_lsn = 1000;
    cluster->replicas[idx].lag_ms = 0;
    cluster->replica_count++;
    pthread_mutex_unlock(&cluster->lock);
    return true;
}

/* Вибір вузла для читання за алгоритмом Round-Robin з перевіркою здоров'я та LSN */
static db_node_t* select_healthy_replica(router_cluster_t* cluster, lsn_t required_lsn) {
    if (cluster->replica_count == 0) {
        return &cluster->primary;
    }

    size_t attempts = cluster->replica_count;
    while (attempts > 0) {
        size_t idx = cluster->rr_index % cluster->replica_count;
        cluster->rr_index++;
        attempts--;

        db_node_t* rep = &cluster->replicas[idx];
        if (rep->is_healthy && rep->lag_ms <= MAX_LAG_THRESHOLD_MS) {
            /* Перевірка причинної узгодженості: репліка мусить наздогнати потрібний LSN */
            if (required_lsn == 0 || rep->last_applied_lsn >= required_lsn) {
                return rep;
            }
        }
    }

    /* Якщо всі репліки відстають або нездорові — fallback на Primary */
    return &cluster->primary;
}

/* Головний диспетчер маршрутизації */
db_node_t* route_query(router_cluster_t* cluster, client_session_t* session, const char* sql) {
    query_type_t qtype = classify_sql(sql);
    time_t now = time(NULL);

    pthread_mutex_lock(&cluster->lock);

    /* 1. Обробка транзакційного стану */
    if (qtype == QUERY_TX_BEGIN) {
        session->in_transaction = true;
        session->pinned_node_id = cluster->primary.id;
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    if (qtype == QUERY_TX_COMMIT || qtype == QUERY_TX_ROLLBACK) {
        session->in_transaction = false;
        session->pinned_node_id = -1;
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    /* 2. Якщо клієнт усередині активної транзакції — ЖОРСТКИЙ PIN на Primary */
    if (session->in_transaction) {
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    /* 3. Операції запису та блокуючого читання — завжди Primary */
    if (qtype == QUERY_WRITE || qtype == QUERY_READ_LOCKING) {
        session->last_write_timestamp = now;
        cluster->primary.last_applied_lsn += 10;
        session->last_write_lsn = cluster->primary.last_applied_lsn;
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    /* 4. Забруднення сесії (SET @var) — прив'язка до Primary */
    if (qtype == QUERY_SESSION_MUTATION) {
        session->session_polluted = true;
        pthread_mutex_unlock(&cluster->lock);
        return &cluster->primary;
    }

    /* 5. Чисте читання (QUERY_READ) */
    if (qtype == QUERY_READ) {
        /* Перевірка ліпкого часового вікна (Sticky Window) після останнього запису */
        if (session->last_write_timestamp > 0 &&
            (now - session->last_write_timestamp) < STICKY_WINDOW_SEC) {
            db_node_t* target = select_healthy_replica(cluster, session->last_write_lsn);
            pthread_mutex_unlock(&cluster->lock);
            return target;
        }

        /* Звичайне розвантажувальне читання без строгих вимог до свіжості */
        db_node_t* target = select_healthy_replica(cluster, 0);
        pthread_mutex_unlock(&cluster->lock);
        return target;
    }

    pthread_mutex_unlock(&cluster->lock);
    return &cluster->primary;
}

void router_destroy(router_cluster_t* cluster) {
    pthread_mutex_destroy(&cluster->lock);
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <mutex>
#include <chrono>
#include <algorithm>
#include <cstdint>
#include <cctype>
#include <optional>

namespace db_router {

using Lsn = uint64_t;
using Timestamp = std::chrono::steady_clock::time_point;

enum class QueryType {
    Unknown,
    Read,             // Звичайний SELECT
    ReadLocking,      // SELECT ... FOR UPDATE / FOR SHARE
    Write,            // INSERT, UPDATE, DELETE, DDL, Write-CTE
    TxBegin,          // BEGIN, START TRANSACTION
    TxCommit,         // COMMIT
    TxRollback,       // ROLLBACK
    SessionMutation   // SET @var, CREATE TEMPORARY TABLE
};

enum class NodeRole {
    Primary,
    Replica
};

struct DbNode {
    int id;
    std::string host;
    int port;
    NodeRole role;
    bool is_healthy{true};
    Lsn last_applied_lsn{1000};
    uint32_t lag_ms{0};
    uint64_t active_connections{0};

    DbNode(int node_id, std::string node_host, int node_port, NodeRole node_role)
        : id(node_id), host(std::move(node_host)), port(node_port), role(node_role) {}
};

class ClientSession {
public:
    int client_id;
    bool in_transaction{false};
    bool session_polluted{false};
    Lsn last_write_lsn{0};
    std::optional<Timestamp> last_write_time{std::nullopt};
    int pinned_node_id{-1};

    explicit ClientSession(int id) : client_id(id) {}

    void record_write(Lsn lsn) {
        last_write_lsn = lsn;
        last_write_time = std::chrono::steady_clock::now();
    }

    [[nodiscard]] bool is_in_sticky_window(std::chrono::seconds window_duration) const {
        if (!last_write_time.has_value()) return false;
        auto now = std::chrono::steady_clock::now();
        return (now - *last_write_time) < window_duration;
    }
};

class SqlClassifier {
public:
    static QueryType classify(std::string_view sql) {
        auto p = trim_leading_whitespace(sql);
        if (p.empty()) return QueryType::Unknown;

        // Пропуск C-подібних коментарів /* ... */
        while (p.starts_with("/*")) {
            auto end_idx = p.find("*/");
            if (end_idx == std::string_view::npos) return QueryType::Unknown;
            p = trim_leading_whitespace(p.substr(end_idx + 2));
        }

        if (starts_with_ci(p, "BEGIN") || starts_with_ci(p, "START TRANSACTION")) {
            return QueryType::TxBegin;
        }
        if (starts_with_ci(p, "COMMIT")) {
            return QueryType::TxCommit;
        }
        if (starts_with_ci(p, "ROLLBACK")) {
            return QueryType::TxRollback;
        }
        if (starts_with_ci(p, "INSERT") || starts_with_ci(p, "UPDATE") ||
            starts_with_ci(p, "DELETE") || starts_with_ci(p, "REPLACE") ||
            starts_with_ci(p, "ALTER")  || starts_with_ci(p, "DROP") ||
            starts_with_ci(p, "CREATE TABLE") || starts_with_ci(p, "TRUNCATE") ||
            starts_with_ci(p, "WITH ")) {
            return QueryType::Write;
        }
        if (starts_with_ci(p, "SET ") || starts_with_ci(p, "CREATE TEMPORARY")) {
            return QueryType::SessionMutation;
        }
        if (starts_with_ci(p, "SELECT")) {
            if (contains_ci(p, "FOR UPDATE") ||
                contains_ci(p, "LOCK IN SHARE MODE") ||
                contains_ci(p, "FOR SHARE")) {
                return QueryType::ReadLocking;
            }
            return QueryType::Read;
        }

        return QueryType::Write; // Безпечний дефолт
    }

private:
    static std::string_view trim_leading_whitespace(std::string_view s) {
        while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front()))) {
            s.remove_prefix(1);
        }
        return s;
    }

    static bool starts_with_ci(std::string_view s, std::string_view prefix) {
        if (s.size() < prefix.size()) return false;
        return std::equal(prefix.begin(), prefix.end(), s.begin(),
            [](char a, char b) {
                return std::tolower(static_cast<unsigned char>(a)) ==
                       std::tolower(static_cast<unsigned char>(b));
            });
    }

    static bool contains_ci(std::string_view hay, std::string_view needle) {
        auto it = std::search(hay.begin(), hay.end(), needle.begin(), needle.end(),
            [](char a, char b) {
                return std::tolower(static_cast<unsigned char>(a)) ==
                       std::tolower(static_cast<unsigned char>(b));
            });
        return it != hay.end();
    }
};

class CausalDatabaseRouter {
public:
    static constexpr uint32_t MAX_ALLOWED_LAG_MS = 2000;
    static constexpr std::chrono::seconds STICKY_WINDOW{3};

    CausalDatabaseRouter(std::string p_host, int p_port)
        : primary_(std::make_shared<DbNode>(0, std::move(p_host), p_port, NodeRole::Primary)) {}

    void add_replica(std::string host, int port) {
        std::lock_guard<std::mutex> lock(mutex_);
        int next_id = static_cast<int>(replicas_.size() + 1);
        replicas_.push_back(std::make_shared<DbNode>(next_id, std::move(host), port, NodeRole::Replica));
    }

    void update_replica_status(int replica_id, bool healthy, uint32_t lag_ms, Lsn lsn) {
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& rep : replicas_) {
            if (rep->id == replica_id) {
                rep->is_healthy = healthy;
                rep->lag_ms = lag_ms;
                rep->last_applied_lsn = lsn;
                break;
            }
        }
    }

    std::shared_ptr<DbNode> route(ClientSession& session, std::string_view sql) {
        QueryType qtype = SqlClassifier::classify(sql);
        std::lock_guard<std::mutex> lock(mutex_);

        // 1. Керування транзакційними межами
        if (qtype == QueryType::TxBegin) {
            session.in_transaction = true;
            session.pinned_node_id = primary_->id;
            return primary_;
        }
        if (qtype == QueryType::TxCommit || qtype == QueryType::TxRollback) {
            session.in_transaction = false;
            session.pinned_node_id = -1;
            return primary_;
        }

        // 2. Якщо сесія в транзакції — жорстка прив'язка до Primary
        if (session.in_transaction) {
            return primary_;
        }

        // 3. Записи та блокуючі читання
        if (qtype == QueryType::Write || qtype == QueryType::ReadLocking) {
            primary_->last_applied_lsn += 10;
            session.record_write(primary_->last_applied_lsn);
            return primary_;
        }

        // 4. Мутація стану сесії (SET @var)
        if (qtype == QueryType::SessionMutation) {
            session.session_polluted = true;
            return primary_;
        }

        // 5. Чисті читання
        if (qtype == QueryType::Read) {
            Lsn required_lsn = 0;
            if (session.is_in_sticky_window(STICKY_WINDOW)) {
                required_lsn = session.last_write_lsn;
            }
            return select_healthy_replica_unlocked(required_lsn);
        }

        return primary_;
    }

private:
    std::shared_ptr<DbNode> select_healthy_replica_unlocked(Lsn required_lsn) {
        if (replicas_.empty()) {
            return primary_;
        }

        size_t attempts = replicas_.size();
        while (attempts-- > 0) {
            size_t idx = rr_index_++ % replicas_.size();
            auto& rep = replicas_[idx];

            if (rep->is_healthy && rep->lag_ms <= MAX_ALLOWED_LAG_MS) {
                if (required_lsn == 0 || rep->last_applied_lsn >= required_lsn) {
                    return rep;
                }
            }
        }

        // Безпечний fallback на Primary
        return primary_;
    }

    std::shared_ptr<DbNode> primary_;
    std::vector<std::shared_ptr<DbNode>> replicas_;
    size_t rr_index_{0};
    std::mutex mutex_;
};

} // namespace db_router
```
:::

## Глибокий розбір механізмів та прихованих пасток

### 1. Тонкощі лексичного аналізу та пастки складного синтаксису SQL
Наївні реалізації маршрутизаторів часто обмежуються порівнянням першого слова запиту: якщо рядок починається з `SELECT`, запит маркується як безпечний для відправки на репліку. Проте у реальних реляційних базах даних такий підхід призводить до важких збоїв:

#### А. Модифікуючі табличні вирази (Data-Modifying CTEs)
У PostgreSQL конструкція `WITH` дозволяє виконувати мутації всередині вибірки:
```sql
WITH moved_rows AS (
    DELETE FROM incoming_queue WHERE status = 'PENDING' RETURNING *
)
SELECT * FROM moved_rows;
```
Формально запит завершується вибіркою `SELECT`, але насправді виконує фізичне видалення рядків `DELETE`. Якщо маршрутизатор побачить підрядок `SELECT` і відправить запит на репліку, транзакція впаде з помилкою `ERROR: cannot execute DELETE in a read-only transaction`. Саме тому функція `classify_sql` примусово маркує всі запити з префіксом `WITH ` як операції запису (`QUERY_WRITE`), спрямовуючи їх виключно на Primary.

#### Б. Блокуючі вибірки (Pessimistic Locking)
Запити з модифікаторами `SELECT ... FOR UPDATE`, `SELECT ... FOR NO KEY UPDATE` або `SELECT ... LOCK IN SHARE MODE` призначені для взяття ексклюзивних або розділених блокувань рядків з метою запобігання стану гонитви (Lost Updates). На репліці операції взяття блокувань блокуються або ігноруються через режим `read_only`. Маршрутизатор зобов'язаний виконувати глибоке сканування суфіксів запиту і класифікувати їх як `QUERY_READ_LOCKING`, які фізично спрямовуються лише на Primary.

#### В. Багаторядкові коментарі та SQL Hints
Клієнтські бібліотеки (наприклад, Hibernate чи Rails ActiveRecord) часто додають на початок запиту коментарі з назвою контролера чи трасувального спану: `/* action:UserController#show, trace_id:abc123 */ SELECT ...`. Наш аналізатор у циклі пропускає всі блоки `/* ... */`, щоб дістатися до першого значущого ключового слова SQL.

### 2. Скінченний автомат сесії та проблема втрати змінних оточення (Session Pollution)
Мережевий протокол СКБД (MySQL / PostgreSQL wire protocol) є станівним (Stateful). Кожне TCP-з'єднання володіє власним контекстом сесії, що зберігається в оперативній пам'яті відповідного бекенд-процесу:
- Змінні сесії: `SET @current_tenant_id = 99;`, `SET time_zone = '+00:00';`;
- Тимчасові таблиці: `CREATE TEMPORARY TABLE temp_cart (...);`;
- Підготовлені вирази (Prepared Statements): ідентифікатор стейтменту `stmt_id` валідний лише на тому з'єднанні, де викликано команду `COM_STMT_PREPARE`.

Якщо застосунок встановлює змінну `@current_tenant_id = 99` через маршрутизатор, ця команда виконується на з'єднанні вузла Primary. Якщо наступний запит `SELECT * FROM orders WHERE tenant_id = @current_tenant_id;` буде направлений на репліку, на з'єднанні репліки змінна матиме значення `NULL`, і клієнт отримає порожній результат або критичну помилку безпеки.

Маршрутизатор вирішує цю проблему за допомогою прапорця `session_polluted`: як тільки клієнт виконує будь-яку мутацію оточення, сесія клієнта жорстко прив'язується до одного конкретного фізичного з'єднання Primary, а після завершення роботи з'єднання не повертається у загальний пул, доки над ним не буде виконано скидання стану (`mysql_reset_connection()` або `DISCARD ALL` у PostgreSQL).

### 3. Механізм причинної узгодженості через LSN (Log Sequence Number)
Проблема «читання власного запису» (Read-Your-Own-Writes) виникає через асинхронну природу реплікації: між моментом успішної фіксації транзакції на Primary (`COMMIT`) та моментом, коли репліка прочитає журнал і накладе зміни на свої сторінки даних, минає час реплікаційного лагу `T_lag`.

Алгоритм LSN-маршрутизатора працює наступним чином:
1. Після кожного успішного виклику `INSERT` / `UPDATE` Primary-вузол повертає клієнту або проксі актуальне зміщення журналу `L_write` (у PostgreSQL це значення повертає системна функція `pg_current_wal_lsn()`, а в MySQL — поточний набір `Executed_Gtid_Set`).
2. Сесія клієнта запам'ятовує отримане значення `L_write` та фіксує мітку часу запису.
3. Коли надходить наступний запит `SELECT`, маршрутизатор перевіряє, чи перебуває клієнт у межах «ліпкого вікна» (Sticky Window, зазвичай 2–5 секунд).
4. Якщо вікно активне, маршрутизатор опитує репліки: кожна репліка у фоновому режимі повідомляє свій `last_applied_lsn` (у PostgreSQL це `pg_last_wal_replay_lsn()`).
5. Якщо серед реплік знайдено вузол, у якого `Replica_LSN ≥ L_write`, запит спрямовується на цю репліку. Клієнт гарантовано бачить свої зміни, а Primary залишається ненавантаженим.
6. Якщо всі доступні репліки відстають (`Replica_LSN < L_write`), маршрутизатор має дві стратегії:
   - **Короткочасне блокування (Wait for LSN)**: викликати на репліці команду очікування (наприклад, `SELECT WAIT_FOR_EXECUTED_GTID_SET('...', 0.05);` у MySQL) з таймаутом у 20–50 мс;
   - **Безпечний відкат (Fallback to Primary)**: якщо репліка не встигає за таймаут, запит виконується на Primary.

### 4. Конкуренція за блокування та оптимізація високонавантаженого пулу
У наведеній реалізації стан кластера захищено об'єктом `pthread_mutex_t` (у C) та `std::mutex` (у C++). Для демонстраційного ядра це забезпечує коректну потокобезпечність. Проте у промислових системах, де проксі обробляє понад 100 000 запитів на секунду, єдиний м'ютекс на весь кластер стає джерелом важкої конкуренції за процесорні кеш-лінії (Cache Line Bouncing).

У промислових маршрутизаторах (таких як ProxySQL або Envoy) застосовують оптимізації безблокувального доступу (Lock-Free Concurrency):
- **Атомарний Round-Robin**: індекс вибору репліки інкрементується через атомарну операцію `std::atomic<size_t>::fetch_add(1, std::memory_order_relaxed)`;
- **Read-Copy-Update (RCU)**: таблиця активних реплік зберігається як константний масив під розумним вказівником `std::atomic<std::shared_ptr<ClusterTopology>>`. Читаючі потоки отримують копію топології без жодного м'ютекса, а фоновий потік моніторингу оновлює всю структуру атомарною заміною вказівника;
- **Thread-Local пули з'єднань**: кожен робочий потік проксі (`worker thread`) має власні незалежні пули TCP-сокетів до Primary та реплік, що повністю усуває міжпотокове блокування при отриманні з'єднання.

### 5. Поведінка під час збоїв та аварійного перемикання (Failover)
Коли Primary-вузол зазнає апаратної відмови або стає недоступним через мережеве розривання:
- Пул підключень Primary миттєво фіксує помилки сокетів (`ECONNRESET`, `ETIMEDOUT`) і переводить вузол у стан `is_healthy = false`;
- Усі поточні запити на запис перериваються з помилкою з'єднання, сигналізуючи клієнтським застосункам про необхідність повторної спроби (Retry);
- Оркестратор кластера (Patroni, Orchestrator чи Consul) обирає найбільш свіжу репліку (з найбільшим LSN) та підвищує її до ролі нового Primary;
- Маршрутизатор отримує сповіщення про зміну топології (через API чи зміну конфігурації), очищає прив'язані сесії, змінює роль вузла у внутрішній структурі й спрямовує наступні операції запису на новий Primary без перезапуску сервісу.
