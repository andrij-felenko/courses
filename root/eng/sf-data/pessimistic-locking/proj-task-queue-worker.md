# ⚙️ Реалізація паралельної черги завдань на основі FOR UPDATE SKIP LOCKED

Коли розподіленій системі потрібна надійна черга завдань із гарантією доставки «щонайменше один раз» (*At-Least-Once Delivery*) та збереженням транзакційної цілісності з іншими бізнес-таблицями, використання окремого брокера повідомлень створює проблему узгодженості двох систем (*Dual-Write Problem*). Якщо бізнес-транзакція записує нове замовлення в реляційну таблицю, а потім надсилає подію в зовнішній брокер повідомлень (RabbitMQ або Apache Kafka), падіння мережі або аварія сервера між цими двома діями призводить або до втрати повідомлення, або до появи фантомного завдання без відповідного запису в базі даних.

Найелегантнішим інженерним рішенням є патерн транзакційної черги (*Transactional Outbox / Task Queue*), реалізований безпосередньо в реляційній базі даних за допомогою оператора `SELECT ... FOR UPDATE SKIP LOCKED`. Такий підхід гарантує, що створення завдання та зміна бізнес-даних відбуваються в одній неподільній ACID-транзакції.

## Схема бази даних та індексна оптимізація

Для забезпечення максимальної пропускної здатності та запобігання повному скануванню таблиці (*Sequential Scan*) при вибірці нових завдань критично важливо створити частковий індекс (*Partial Index*). Частковий індекс містить посилання лише на активні рядки зі статусом `pending`, що мінімізує його розмір в оперативній пам'яті та усуває навантаження на підсистему дискового вводу-виводу:

```sql
CREATE TABLE task_queue (
    id BIGSERIAL PRIMARY KEY,
    payload TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Частковий індекс для миттєвого пошуку активних завдань за пріоритетом та ідентифікатором
CREATE INDEX idx_task_queue_pending ON task_queue (status, id) 
WHERE status = 'pending';
```

## Алгоритм паралельного споживача (Worker)

Кожен фоновий потік споживача працює в безкінечному циклі, виконуючи суворо регламентований ланцюжок дій:
1. **Відкриття транзакції:** надсилається команда `BEGIN;`.
2. **Неблокуюче захоплення завдання:** виконується вибірка з модифікатором `FOR UPDATE SKIP LOCKED`:
   ```sql
   SELECT id, payload, attempts
   FROM task_queue
   WHERE status = 'pending'
   ORDER BY id ASC
   LIMIT 1
   FOR UPDATE SKIP LOCKED;
   ```
3. **Обробка та фіксація:**
   - Якщо вільний рядок знайдено, рушій накладає ексклюзивний рядковий замок (X-lock) і повертає кортеж клієнту. Воркер виконує бізнес-обчислення.
   - У разі успішного завершення воркер оновлює статус: `UPDATE task_queue SET status = 'completed', updated_at = NOW() WHERE id = $1;` і фіксує транзакцію через `COMMIT;`. Усі замки знімаються автоматично.
   - У разі виникнення помилки збільшується лічильник спроб `attempts`. Якщо лічильник перевищує `max_attempts`, завдання переводиться у термінальний статус `failed` (патерн Dead Letter Queue); інакше статус залишається `pending` для повторної спроби наступним воркером.
4. **Порожня черга та режим сну:** якщо запит повернув нуль рядків (усі завдання або вже оброблені, або заблоковані іншими воркерами), транзакція фіксується (`COMMIT;`), а потік засинає на короткий інтервал (наприклад, 100 мс) або переходить у режим очікування асинхронного сповіщення СУБД (`LISTEN/NOTIFY`).

## Реалізація на C та C++

Нижче наведено вихідний код багатопотокового воркера черги. У C-версії використовується низькорівневий інтерфейс `libpq` з ручним керуванням пам'яттю та дескрипторами з'єднання. У C++-версії реалізовано сучасні ідіоми: інкапсуляцію ресурсів у класи RAII, унікальні покажчики `std::unique_ptr`, безпечну типізацію та роботу з потоками через `std::chrono` та `std::thread`.

:::tabs
@tab c
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libpq-fe.h>

#define MAX_PAYLOAD_LEN 1024

typedef struct {
    long long id;
    char payload[MAX_PAYLOAD_LEN];
    int attempts;
} task_item_t;

static int fetch_and_lock_task(PGconn *conn, task_item_t *task) {
    PGresult *res = PQexec(conn, "BEGIN;");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        return -1;
    }
    PQclear(res);

    const char *query = 
        "SELECT id, payload, attempts "
        "FROM task_queue "
        "WHERE status = 'pending' "
        "ORDER BY id ASC "
        "LIMIT 1 "
        "FOR UPDATE SKIP LOCKED;";

    res = PQexec(conn, query);
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(conn, "ROLLBACK;");
        return -1;
    }

    int rows = PQntuples(res);
    if (rows == 0) {
        PQclear(res);
        PQexec(conn, "COMMIT;");
        return 0; // Черга порожня
    }

    task->id = atoll(PQgetvalue(res, 0, 0));
    strncpy(task->payload, PQgetvalue(res, 0, 1), sizeof(task->payload) - 1);
    task->payload[sizeof(task->payload) - 1] = '\0';
    task->attempts = atoi(PQgetvalue(res, 0, 2));

    PQclear(res);
    return 1; // Завдання успішно захоплено
}

static int complete_task(PGconn *conn, long long task_id) {
    char query[256];
    snprintf(query, sizeof(query),
             "UPDATE task_queue SET status = 'completed', updated_at = NOW() WHERE id = %lld;",
             task_id);

    PGresult *res = PQexec(conn, query);
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        PQexec(conn, "ROLLBACK;");
        return -1;
    }
    PQclear(res);

    res = PQexec(conn, "COMMIT;");
    PQclear(res);
    return 0;
}

void run_worker(const char *conninfo) {
    PGconn *conn = PQconnectdb(conninfo);
    if (PQstatus(conn) != CONNECTION_OK) {
        PQfinish(conn);
        return;
    }

    while (1) {
        task_item_t task;
        int status = fetch_and_lock_task(conn, &task);
        if (status > 0) {
            // Обробка корисного навантаження
            complete_task(conn, task.id);
        } else if (status == 0) {
            usleep(100000); // 100 мс паузи перед наступним опитуванням
        } else {
            usleep(500000); // Пауза при помилці бази
        }
    }

    PQfinish(conn);
}
```
@tab cpp
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <memory>
#include <chrono>
#include <thread>
#include <stdexcept>
#include <libpq-fe.h>

struct TaskItem {
    int64_t id;
    std::string payload;
    int attempts;
};

// RAII обгортка для результатів запитів PostgreSQL
class PgResult {
public:
    explicit PgResult(PGresult* res) : res_(res) {}
    ~PgResult() { if (res_) PQclear(res_); }

    PgResult(const PgResult&) = delete;
    PgResult& operator=(const PgResult&) = delete;

    PgResult(PgResult&& other) noexcept : res_(other.res_) { other.res_ = nullptr; }
    PgResult& operator=(PgResult&& other) noexcept {
        if (this != &other) {
            if (res_) PQclear(res_);
            res_ = other.res_;
            other.res_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] PGresult* get() const noexcept { return res_; }
    [[nodiscard]] ExecStatusType status() const noexcept { return PQresultStatus(res_); }
    [[nodiscard]] int rowCount() const noexcept { return PQntuples(res_); }
    [[nodiscard]] const char* getValue(int row, int col) const { return PQgetvalue(res_, row, col); }

private:
    PGresult* res_{nullptr};
};

// RAII обгортка для керування життєвим циклом з'єднання СУБД
class DatabaseConnection {
public:
    explicit DatabaseConnection(std::string_view conninfo) {
        conn_ = PQconnectdb(conninfo.data());
        if (PQstatus(conn_) != CONNECTION_OK) {
            std::string err = PQerrorMessage(conn_);
            PQfinish(conn_);
            throw std::runtime_error("Database connection failed: " + err);
        }
    }

    ~DatabaseConnection() {
        if (conn_) {
            PQfinish(conn_);
        }
    }

    DatabaseConnection(const DatabaseConnection&) = delete;
    DatabaseConnection& operator=(const DatabaseConnection&) = delete;

    PgResult execute(std::string_view sql) {
        return PgResult(PQexec(conn_, sql.data()));
    }

private:
    PGconn* conn_{nullptr};
};

class TaskQueueWorker {
public:
    explicit TaskQueueWorker(std::string_view conninfo)
        : db_(std::make_unique<DatabaseConnection>(conninfo)) {}

    std::optional<TaskItem> fetchAndLockNextTask() {
        auto beginRes = db_->execute("BEGIN;");
        if (beginRes.status() != PGRES_COMMAND_OK) {
            return std::nullopt;
        }

        constexpr std::string_view fetchSql = 
            "SELECT id, payload, attempts "
            "FROM task_queue "
            "WHERE status = 'pending' "
            "ORDER BY id ASC "
            "LIMIT 1 "
            "FOR UPDATE SKIP LOCKED;";

        auto res = db_->execute(fetchSql);
        if (res.status() != PGRES_TUPLES_OK) {
            db_->execute("ROLLBACK;");
            return std::nullopt;
        }

        if (res.rowCount() == 0) {
            db_->execute("COMMIT;");
            return std::nullopt;
        }

        TaskItem item{
            .id = std::stoll(res.getValue(0, 0)),
            .payload = res.getValue(0, 1),
            .attempts = std::stoi(res.getValue(0, 2))
        };

        return item;
    }

    void completeTask(int64_t taskId) {
        std::string updateSql = 
            "UPDATE task_queue SET status = 'completed', updated_at = NOW() WHERE id = " 
            + std::to_string(taskId) + ";";

        auto res = db_->execute(updateSql);
        if (res.status() != PGRES_COMMAND_OK) {
            db_->execute("ROLLBACK;");
            throw std::runtime_error("Failed to complete task");
        }

        db_->execute("COMMIT;");
    }

    void run() {
        while (running_) {
            try {
                auto task = fetchAndLockNextTask();
                if (task) {
                    // Обробка бізнес-логіки
                    completeTask(task->id);
                } else {
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                }
            } catch (const std::exception& ex) {
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }
        }
    }

    void stop() noexcept {
        running_ = false;
    }

private:
    std::unique_ptr<DatabaseConnection> db_;
    bool running_{true};
};
```
:::

## Пакетна обробка завдань (Batching) та масштабування пулу

У високонавантажених системах вибірка завдань по одному створює зайві накладні витрати на мережеві виклики (*Network Round-Trips*). Для підвищення пропускної здатності використовується пакетне захоплення кортежів через `LIMIT N`:

```sql
-- Захопити одразу 10 завдань для одного воркера
SELECT id, payload 
FROM task_queue 
WHERE status = 'pending' 
ORDER BY id ASC 
LIMIT 10 
FOR UPDATE SKIP LOCKED;
```

Воркер обробляє масив із 10 завдань у локальній пам'яті, після чого виконує одне групове оновлення статусів через масив ідентифікаторів `WHERE id = ANY($1::bigint[])`. Це знижує кількість мережевих запитів до СУБД у 10 разів і дає змогу обслуговувати десятки тисяч завдань на секунду на звичайному обладнанні.

## Підводні камені, аварійні стани та очищення роздутих таблиць

1. **Аварійне падіння воркера (Process Crash):** Якщо процес споживача раптово аварійно завершується через `SIGKILL`, переповнення оперативної пам'яті (OOM Killer) або апаратний збій хоста, операційна система закриває його TCP-сокет. Рушій PostgreSQL миттєво виявляє обрив зв'язку і автоматично виконує `ROLLBACK` незавершеної транзакції. Усі утримувані X-locks негайно знімаються, і завдання стає доступним для інших працюючих воркерів без необхідності ручного втручання адміністратора.
2. **Пастка тривалих транзакцій:** Якщо бізнес-обробка завдання вимагає значного часу (наприклад, генерація PDF-звіту тривалістю 30 секунд або завантаження відеофайлу), утримувати транзакційне блокування протягом усього цього часу категорично заборонено. Тривале блокування утримує слот пулу з'єднань СУБД і заважає роботі механізму очищення пам'яті (VACUUM). Правильне інженерне рішення для тривалих завдань полягає у двоетапному підході: воркер переводить статус завдання у `status = 'processing'` з фіксацією мітки `heartbeat_at = NOW()`, викликає `COMMIT;` і відпускає замок. Окремий фоновий потік перевіряє завислі завдання за умовою `status = 'processing' AND heartbeat_at < NOW() - INTERVAL '5 minutes'`.
3. **Роздуття таблиці (Table Bloat):** Оскільки черга завдань генерує інтенсивний потік операцій `INSERT`, `UPDATE` та `DELETE`, таблиця швидко накопичує «мертві кортежі» (*Dead Tuples*). Для запобігання деградації швидкодії необхідно налаштувати агресивні параметри автоочищення `autovacuum_vacuum_scale_factor = 0.05` для таблиці черги або періодично переносити оброблені записи в архівну таблицю за допомогою секціонування за часом (*Time-based Partitioning*).
4. **Коректна зупинка (Graceful Shutdown):** Під час перерозгортання сервісу споживачі отримують сигнал операційної системи `SIGTERM`. Обробник сигналу повинен виставити атомарний прапорець зупинки `running_ = false`, дочекатися завершення поточної транзакції для взятого завдання і закрити з'єднання з базою, не залишаючи незафіксованих змін.
