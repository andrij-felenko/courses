# ⚙️ Реалізація надійного рушія Outbox: опитування з FOR UPDATE SKIP LOCKED

Ця проєктна вставка демонструє створення високопродуктивного та стійкого до збоїв фонового ретранслятора (*Polling Publisher Engine*), який вичитує невідправлені події з реляційної таблиці PostgreSQL, пакетно публікує їх у транспортний брокер та атомарно видаляє підтверджені записи без взаємних блокувань між паралельними воркерами.

## Проблема конкурентного опитування та блокування рядків

У промисловій архітектурі сервіс зазвичай розгортається у вигляді кількох паралельних процесів або контейнерів (наприклад, 4–8 реплік у кластері Kubernetes). Якщо кожен екземпляр сервісу періодично запускає фоновий потік для вивантаження подій із таблиці `outbox`, виникає класична проблема конкурентного доступу до спільних ресурсів.

Наївний підхід полягає у виконанні стандартного запиту вибірки:

```sql
-- НАЇВНИЙ ЗАПИТ: ПРИЗВОДИТЬ ДО ГОНОК ТА ДУБЛЮВАННЯ РОБОТИ
SELECT id, payload FROM outbox ORDER BY created_at ASC LIMIT 50;
```

Якщо два воркери одночасно виконують цей запит, вони отримують ідентичний набір з 50 рядків. Обидва процеси починають паралельно відправляти однакові повідомлення в Apache Kafka, подвоюючи трафік і навантажуючи брокер зайвими дублікатами. Після відправки обидва воркери намагаються виконати `DELETE FROM outbox WHERE id = ...`, що викликає конфлікти блокування на рівні рядків (*Row-Level Lock Contention*) та взаємні блокування (*Deadlocks*).

Спроба вирішити проблему додаванням блокування `FOR UPDATE`:

```sql
-- БЛОКУЮЧИЙ ЗАПИТ: ПРИЗВОДИТЬ ДО СЕРІАЛІЗАЦІЇ ТА ПРОСТОЮ
SELECT id, payload FROM outbox ORDER BY created_at ASC LIMIT 50 FOR UPDATE;
```

також виявляється неефективною. Перший воркер блокує перші 50 рядків. Другий воркер, виконавши той самий запит, не може отримати наступні записи: він повністю зупиняється і чекає, поки перший процес завершить надсилання повідомлень мережею та зафіксує транзакцію. Замість паралельної обробки система деградує до строго послідовної черги з високими затримками.

### Механізм FOR UPDATE SKIP LOCKED та рівні ізоляції

Починаючи з PostgreSQL 9.5, стандарт мови SQL підтримує директиву **`SKIP LOCKED`**. Працюючи в парі з `FOR UPDATE`, ця конструкція вказує рушію бази даних:
1. Заблокувати та повернути перші `N` доступних рядків, які на цей момент не заблоковані жодною іншою активною транзакцією.
2. Якщо рядок уже утримується іншим паралельним воркером, **не чекати його звільнення**, а негайно пропустити його і перейти до наступного вільного рядка за індексом.

Для коректної роботи ретранслятора критично важливо використовувати рівень ізоляції транзакцій **`READ COMMITTED`**. На вищих рівнях ізоляції (`REPEATABLE READ` або `SERIALIZABLE`) знімок видимості фіксується на початку транзакції воркера. Якщо інший процес вставив нові події після відкриття транзакції, воркер не побачить їх до перезапуску транзакції, а при спробі блокування конкуруючих рядків виникне помилка серіалізації `could not serialize access due to concurrent update` (код помилки `40001`). На рівні `READ COMMITTED` кожен запит `SELECT ... FOR UPDATE SKIP LOCKED` бачить найсвіжіший зафіксований стан таблиці.

## Реалізація рушія ретрансляції мовами C та C++

Нижче наведено повнофункціональний багатопотоковий рушій публікації. Програма підключається до бази даних PostgreSQL через клієнтську бібліотеку `libpq`, виконує конкурентну вибірку пачки подій, імітує надійне надсилання в брокер і фіксує видалення в одній транзакції.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <signal.h>
#include <unistd.h>
#include <libpq-fe.h>

#define BATCH_SIZE 50
#define POLL_INTERVAL_USEC 200000 // 200 мс

static volatile sig_atomic_t g_running = 1;

void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

// Імітація надійного відправлення повідомлення у брокер (Kafka/RabbitMQ)
bool mock_broker_publish(const char *topic, const char *key, const char *payload) {
    if (!topic || !key || !payload) return false;
    // У реальній системі тут викликається rd_kafka_producev() з очікуванням черги
    return true; 
}

// Обробка однієї пачки подій у межах транзакції
int process_outbox_batch(PGconn *conn) {
    PGresult *res = PQexec(conn, "BEGIN;");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        return -1;
    }
    PQclear(res);

    // Блокуємо та вибираємо пачку, пропускаючи вже зайняті рядки
    const char *fetch_sql = 
        "SELECT id, aggregate_type, aggregate_id, payload "
        "FROM outbox "
        "ORDER BY created_at ASC "
        "LIMIT $1 "
        "FOR UPDATE SKIP LOCKED;";

    const char *param_values[1];
    char batch_str[16];
    snprintf(batch_str, sizeof(batch_str), "%d", BATCH_SIZE);
    param_values[0] = batch_str;

    res = PQexecParams(conn, fetch_sql, 1, NULL, param_values, NULL, NULL, 0);
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(conn, "ROLLBACK;");
        return -1;
    }

    int rows = PQntuples(res);
    if (rows == 0) {
        PQclear(res);
        PQexec(conn, "COMMIT;");
        return 0; // Немає нових подій
    }

    bool batch_ok = true;
    for (int i = 0; i < rows; ++i) {
        const char *id = PQgetvalue(res, i, 0);
        const char *topic = PQgetvalue(res, i, 1);
        const char *key = PQgetvalue(res, i, 2);
        const char *payload = PQgetvalue(res, i, 3);

        if (!mock_broker_publish(topic, key, payload)) {
            batch_ok = false;
            break;
        }

        // Видаляємо оброблений рядок у тій самій транзакції
        const char *del_sql = "DELETE FROM outbox WHERE id = $1;";
        const char *del_params[1] = { id };
        PGresult *del_res = PQexecParams(conn, del_sql, 1, NULL, del_params, NULL, NULL, 0);
        if (PQresultStatus(del_res) != PGRES_COMMAND_OK) {
            PQclear(del_res);
            batch_ok = false;
            break;
        }
        PQclear(del_res);
    }

    PQclear(res);

    if (batch_ok) {
        res = PQexec(conn, "COMMIT;");
        if (PQresultStatus(res) == PGRES_COMMAND_OK) {
            PQclear(res);
            return rows;
        }
        PQclear(res);
    }

    PQexec(conn, "ROLLBACK;");
    return -1;
}

int main(void) {
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    const char *conninfo = "host=localhost port=5432 dbname=shop user=postgres password=secret";
    PGconn *conn = PQconnectdb(conninfo);

    if (PQstatus(conn) != CONNECTION_OK) {
        PQfinish(conn);
        return 1;
    }

    while (g_running) {
        int processed = process_outbox_batch(conn);
        if (processed == 0) {
            usleep(POLL_INTERVAL_USEC);
        } else if (processed < 0) {
            usleep(POLL_INTERVAL_USEC * 2); // Пауза при помилці
        }
    }

    PQfinish(conn);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <expected>
#include <chrono>
#include <thread>
#include <csignal>
#include <libpq-fe.h>

namespace outbox {

struct Event {
    std::string id;
    std::string topic;
    std::string key;
    std::string payload;
};

// RAII обгортка для з'єднання з базою даних PostgreSQL
class DbConnection {
public:
    explicit DbConnection(std::string_view conninfo)
        : conn_(PQconnectdb(conninfo.data()), &PQfinish) {
        if (PQstatus(conn_.get()) != CONNECTION_OK) {
            throw std::runtime_error("DB Connection failed: " + std::string(PQerrorMessage(conn_.get())));
        }
    }

    PGconn* get() const noexcept { return conn_.get(); }

private:
    std::unique_ptr<PGconn, decltype(&PQfinish)> conn_;
};

// RAII обгортка для результату SQL-запиту
class DbResult {
public:
    explicit DbResult(PGresult* res) : res_(res, &PQclear) {}

    PGresult* get() const noexcept { return res_.get(); }
    ExecStatusType status() const noexcept { return PQresultStatus(res_.get()); }
    int rowCount() const noexcept { return PQntuples(res_.get()); }
    
    std::string_view get(int row, int col) const noexcept {
        return std::string_view(PQgetvalue(res_.get(), row, col));
    }

private:
    std::unique_ptr<PGresult, decltype(&PQclear)> res_;
};

class OutboxPublisher {
public:
    explicit OutboxPublisher(DbConnection& db, size_t batchSize = 50)
        : db_(db), batchSize_(batchSize) {}

    // Повертає кількість успішно оброблених подій або помилку
    std::expected<size_t, std::string> processBatch() {
        if (!execCommand("BEGIN;")) {
            return std::unexpected("Failed to begin transaction");
        }

        const std::string fetchSql = 
            "SELECT id, aggregate_type, aggregate_id, payload "
            "FROM outbox "
            "ORDER BY created_at ASC "
            "LIMIT $1 "
            "FOR UPDATE SKIP LOCKED;";

        std::string limitStr = std::to_string(batchSize_);
        const char* params[1] = { limitStr.c_str() };

        DbResult res(PQexecParams(db_.get(), fetchSql.c_str(), 1, nullptr, params, nullptr, nullptr, 0));
        if (res.status() != PGRES_TUPLES_OK) {
            execCommand("ROLLBACK;");
            return std::unexpected("Fetch outbox events failed: " + std::string(PQerrorMessage(db_.get())));
        }

        int count = res.rowCount();
        if (count == 0) {
            execCommand("COMMIT;");
            return 0;
        }

        std::vector<std::string> publishedIds;
        publishedIds.reserve(count);

        for (int i = 0; i < count; ++i) {
            Event ev{
                std::string(res.get(i, 0)),
                std::string(res.get(i, 1)),
                std::string(res.get(i, 2)),
                std::string(res.get(i, 3))
            };

            if (!sendToBroker(ev)) {
                execCommand("ROLLBACK;");
                return std::unexpected("Broker publish failed for event: " + ev.id);
            }

            publishedIds.push_back(ev.id);
        }

        // Видаляємо всі опубліковані події пачки
        for (const auto& id : publishedIds) {
            const char* delParams[1] = { id.c_str() };
            DbResult delRes(PQexecParams(db_.get(), "DELETE FROM outbox WHERE id = $1;", 1, nullptr, delParams, nullptr, nullptr, 0));
            if (delRes.status() != PGRES_COMMAND_OK) {
                execCommand("ROLLBACK;");
                return std::unexpected("Delete event failed: " + id);
            }
        }

        if (!execCommand("COMMIT;")) {
            return std::unexpected("Failed to commit transaction");
        }

        return publishedIds.size();
    }

private:
    DbConnection& db_;
    size_t batchSize_;

    bool execCommand(std::string_view sql) {
        DbResult res(PQexec(db_.get(), sql.data()));
        return res.status() == PGRES_COMMAND_OK;
    }

    bool sendToBroker(const Event& ev) const noexcept {
        // У продакшені: виклик librdkafka продюсера з перевіркою доставки
        return !ev.id.empty() && !ev.topic.empty();
    }
};

} // namespace outbox

static volatile std::sig_atomic_t g_stop = 0;

int main() {
    std::signal(SIGINT, [](int) { g_stop = 1; });
    std::signal(SIGTERM, [](int) { g_stop = 1; });

    try {
        outbox::DbConnection db("host=localhost port=5432 dbname=shop user=postgres password=secret");
        outbox::OutboxPublisher publisher(db, 50);

        while (!g_stop) {
            auto result = publisher.processBatch();
            if (result.has_value()) {
                if (result.value() == 0) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(200));
                }
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }
        }
    } catch (const std::exception& e) {
        return 1;
    }

    return 0;
}
```
:::

## Аналіз архітектури та захист від аварійних відмов

1. **Ідіоматичне керування ресурсами (RAII):**
   У реалізації на C++ об'єкти `DbConnection` та `DbResult` інкапсулюють низькорівневі покажчики `PGconn` та `PGresult` за допомогою розумних покажчиків `std::unique_ptr` із власними делетерами (`&PQfinish`, `&PQclear`). Це гарантує відсутність витоків пам'яті та дескрипторів сокетів при будь-яких аварійних винятках або передчасних виходах із функцій.

2. **Поведінка при аварійному падінні під час відправки:**
   Якщо процес воркера примусово завершується операційною системою (наприклад, аварійне скидання живлення або сигнал `SIGKILL`) під час виконання виклику `sendToBroker()`, відкритий TCP-сокет до PostgreSQL обривається. Сервер бази даних автоматично фіксує розрив з'єднання і виконує неявний `ROLLBACK` поточної транзакції.
   У результаті всі заблоковані рядки повертаються у загальний пул. Інший активний воркер підхоплює ці записи під час наступного циклу опитування. Події гарантовано не втрачаються, хоча в брокері може з'явитися дублікат (семантика *At-Least-Once*).

3. **Захист від переповнення буферів (Batch Processing):**
   Параметр `batchSize_` жорстко обмежує максимальну кількість записів, які вибираються за один такт. Це усуває небезпеку вичерпання оперативної пам'яті процесу (*OOM Crash*) навіть у випадках, коли в системі стався тривалий збій мережі і в таблиці `outbox` накопичилися сотні тисяч невідправлених подій.

4. **Адаптивні паузи та коректне завершення (Graceful Shutdown):**
   Обробники системних сигналів `SIGINT` та `SIGTERM` встановлюють атомарний прапорець завершення. Програма коректно дочікується завершення поточної транзакції фіксації пачки перед закриттям з'єднання з базою даних, що виключає переривання транзакцій на півдорозі.

5. **Обробка отруйних повідомлень (Poison Messages):**
   Якщо брокер відхиляє окрему подію через невідповідність схемі або перевищення ліміту розміру повідомлення (`max.message.bytes`), наївний відкат `ROLLBACK` заблокує весь конвеєр: воркер нескінченно повторюватиме спробу відправки тієї самої пачки. Для запобігання цьому в таблицю `outbox` додається колонка `retry_count INT DEFAULT 0`. Якщо лічильник перевищує 5 спроб, подія переміщується в карантинну таблицю помилок `outbox_dead_letter`, а основна черга продовжує рух без блокування.

## Гібридне опитування: зменшення затримки через PostgreSQL LISTEN / NOTIFY

Класичне опитування з фіксованим сном (наприклад, 200 мс) змушує клієнта чекати в середньому 100 мс навіть при наявності щойно зафіксованої події.

Для ліквідації цієї затримки застосовують гібридний підхід: до таблиці `outbox` додається тригер `AFTER INSERT`, який виконує команду `PERFORM pg_notify('outbox_events', '1');`. Воркер виконує підписку `LISTEN outbox_events;` і замість звичайного виклику `sleep()` очікує надходження подій на файловому дескрипторі з'єднання через системний виклик `poll()` або `epoll_wait()`.

Щойно транзакція фіксує новий рядок у базі даних, ядро PostgreSQL миттєво надсилає сигнал сокетом. Воркер прокидається за частки мілісекунди і запускає обробку `process_outbox_batch()`. Якщо сповіщення губляться через перезапуск з'єднання, резервний таймаут `poll()` на 500 мс гарантує, що жодна подія не зависне в черзі.
