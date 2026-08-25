# ⚙️ Практична реалізація багатопотокової обробки на SQLite та DuckDB

Вбудована база даних функціонує безпосередньо в адресному просторі застосунку, тому керування дескрипторами з'єднань, життєвим циклом покажчиків, виділенням пам'яті та синхронізацією багатопотокового доступу покладається виключно на хост-процес. На відміну від клієнт-серверних систем, де пул з'єднань керує віддаленими TCP-сокетами, у вбудованій системі дескриптор бази даних є локальною структурою в купі (Heap), яка тримає файлові дескриптори ОС, буфери сторінок та м'ютекси.

---

### Частина 1: Архітектура та інваріанти багатопотокового доступу в SQLite

Для досягнення максимальної пропускної здатності при паралельному читанні з багатьох робочих потоків застосунку та записі з окремого виділеного потоку SQLite налаштовується в режимі багатопотоковості (`SQLITE_OPEN_NOMUTEX`) у комбінації з журналом випереджального запису (`WAL`).

Головні архітектурні інваріанти:

1. **Ізоляція дескрипторів `sqlite3*` за потоками**: Внутрішні структури з'єднання SQLite не містять блокувань для одночасного доступу, якщо активовано прапорець `SQLITE_OPEN_NOMUTEX`. Передача одного дескриптора між потоками без зовнішнього м'ютекса призводить до гонитви за ресурси (Data Race) у стані віртуальної машини VDBE. Кожен потік зобов'язаний відкривати власне локальне з'єднання.
2. **Активація режиму WAL (`journal_mode=WAL`)**: У традиційному режимі rollback-журналу будь-який записувач захоплює ексклюзивне блокування всього файлу бази даних через системний виклик `fcntl()`, блокуючи всі паралельні читання. Перемикання у WAL переносить операції запису в окремий файл логу (`.db-wal`), що дозволяє читачам паралельно сканувати стабільний знімок даних без зупинки записувача.
3. **Керування блокуваннями та обробка конкурентних колізій (`sqlite3_busy_timeout`)**: Якщо два потоки одночасно намагаються розпочати транзакцію запису (`BEGIN IMMEDIATE`), другий потік отримає код помилки `SQLITE_BUSY`. Функція `sqlite3_busy_timeout()` налаштовує ядро SQLite на автоматичне очікування зі ступінчастою експоненційною затримкою (Exponential Backoff), усуваючи збої при короткочасних блокуваннях.
4. **Безкопійний доступ (Zero-Copy BLOB)**: Виклик функції `sqlite3_column_blob()` повертає прямий покажчик на внутрішній буфер сторінки у пам'яті процесу. Це усуває виділення динамічної пам'яті через `malloc()` та копіювання байтів.

Нижче наведено повну реалізацію багатопотокового читання та запису мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <sqlite3.h>

#define DB_PATH "embedded_storage.db"
#define NUM_READERS 4

/* Конфігурація з'єднання: WAL, синхронізація NORMAL, таймаут 5000 мс */
static sqlite3* open_configured_connection(int flags) {
    sqlite3 *db = NULL;
    int rc = sqlite3_open_v2(DB_PATH, &db, flags, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка відкриття БД: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return NULL;
    }

    /* Налаштування очікування при блокуванні файлу */
    sqlite3_busy_timeout(db, 5000);

    /* Увімкнення журналу WAL та оптимізації синхронізації */
    char *err_msg = NULL;
    rc = sqlite3_exec(db, "PRAGMA journal_mode=WAL;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка встановлення WAL: %s\n", err_msg);
        sqlite3_free(err_msg);
    }
    sqlite3_exec(db, "PRAGMA synchronous=NORMAL;", NULL, NULL, NULL);

    return db;
}

/* Потік-записувач: виконує періодичні вставки у транзакціях */
void* writer_thread(void *arg) {
    (void)arg;
    sqlite3 *db = open_configured_connection(SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_NOMUTEX);
    if (!db) return NULL;

    const char *sql_insert = "INSERT INTO sensor_payloads (device_id, payload) VALUES (?, ?);";
    sqlite3_stmt *stmt = NULL;
    sqlite3_prepare_v3(db, sql_insert, -1, 0, &stmt, NULL);

    uint8_t buffer[64];
    for (int i = 0; i < 100; ++i) {
        memset(buffer, (uint8_t)i, sizeof(buffer));

        /* Явний початок транзакції запису для запобігання авто-комітам на кожен рядок */
        sqlite3_exec(db, "BEGIN IMMEDIATE TRANSACTION;", NULL, NULL, NULL);
        sqlite3_reset(stmt);
        sqlite3_bind_int(stmt, 1, 1000 + i);
        sqlite3_bind_blob(stmt, 2, buffer, sizeof(buffer), SQLITE_STATIC);

        if (sqlite3_step(stmt) != SQLITE_DONE) {
            fprintf(stderr, "Помилка запису: %s\n", sqlite3_errmsg(db));
        }
        sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return NULL;
}

/* Потік-читач: демонструє Zero-Copy доступ до BLOB-даних */
void* reader_thread(void *arg) {
    int thread_id = *(int*)arg;
    sqlite3 *db = open_configured_connection(SQLITE_OPEN_READONLY | SQLITE_OPEN_NOMUTEX);
    if (!db) return NULL;

    const char *sql_select = "SELECT id, device_id, payload FROM sensor_payloads ORDER BY id DESC LIMIT 5;";
    sqlite3_stmt *stmt = NULL;
    sqlite3_prepare_v3(db, sql_select, -1, 0, &stmt, NULL);

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        int dev_id = sqlite3_column_int(stmt, 1);
        
        /* Zero-copy: отримання прямого покажчика у внутрішній кеш сторінки */
        const void *blob_ptr = sqlite3_column_blob(stmt, 2);
        int blob_size = sqlite3_column_bytes(stmt, 2);

        /* Пряма обробка байтів за адресою без виклику malloc() */
        uint8_t first_byte = (blob_size > 0 && blob_ptr) ? *((const uint8_t*)blob_ptr) : 0;
        (void)first_byte;
        (void)id;
        (void)dev_id;
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return NULL;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <thread>
#include <expected>
#include <sqlite3.h>

namespace embedded_db {

/* RAII-обгортка для безпечного керування дескриптором sqlite3 */
class DatabaseConnection {
public:
    static std::expected<DatabaseConnection, std::string> open(std::string_view path, int flags) {
        sqlite3* raw_db = nullptr;
        int rc = sqlite3_open_v2(path.data(), &raw_db, flags, nullptr);
        if (rc != SQLITE_OK) {
            std::string err = raw_db ? sqlite3_errmsg(raw_db) : "Невідома помилка";
            if (raw_db) sqlite3_close(raw_db);
            return std::unexpected(err);
        }

        DatabaseConnection conn(raw_db);
        conn.configure();
        return conn;
    }

    ~DatabaseConnection() {
        if (db_) {
            sqlite3_close_v2(db_);
        }
    }

    DatabaseConnection(DatabaseConnection&& other) noexcept : db_(other.db_) {
        other.db_ = nullptr;
    }

    DatabaseConnection& operator=(DatabaseConnection&& other) noexcept {
        if (this != &other) {
            if (db_) sqlite3_close_v2(db_);
            db_ = other.db_;
            other.db_ = nullptr;
        }
        return *this;
    }

    DatabaseConnection(const DatabaseConnection&) = delete;
    DatabaseConnection& operator=(const DatabaseConnection&) = delete;

    sqlite3* handle() const noexcept { return db_; }

private:
    explicit DatabaseConnection(sqlite3* db) noexcept : db_(db) {}

    void configure() {
        sqlite3_busy_timeout(db_, 5000);
        char* err_msg = nullptr;
        sqlite3_exec(db_, "PRAGMA journal_mode=WAL;", nullptr, nullptr, &err_msg);
        if (err_msg) sqlite3_free(err_msg);
        sqlite3_exec(db_, "PRAGMA synchronous=NORMAL;", nullptr, nullptr, nullptr);
    }

    sqlite3* db_{nullptr};
};

/* Обробник запитів із Zero-Copy доступом через безпечні типи std::span */
class QueryEngine {
public:
    explicit QueryEngine(sqlite3* db) : db_(db) {}

    void process_payloads() {
        constexpr std::string_view sql = "SELECT id, device_id, payload FROM sensor_payloads ORDER BY id DESC LIMIT 5;";
        sqlite3_stmt* raw_stmt = nullptr;
        
        if (sqlite3_prepare_v3(db_, sql.data(), -1, 0, &raw_stmt, nullptr) != SQLITE_OK) {
            return;
        }

        /* Автоматичне звільнення компільованого виразу через кастомний делетер */
        std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(raw_stmt, sqlite3_finalize);

        while (sqlite3_step(stmt.get()) == SQLITE_ROW) {
            int64_t id = sqlite3_column_int64(stmt.get(), 0);
            int32_t device_id = sqlite3_column_int(stmt.get(), 1);

            /* Отримання прямого константного покажчика на комірку пам'яті */
            const auto* data = static_cast<const uint8_t*>(sqlite3_column_blob(stmt.get(), 2));
            int size = sqlite3_column_bytes(stmt.get(), 2);

            /* Представлення як std::span без додаткового виділення динамічної пам'яті */
            std::span<const uint8_t> payload_view(data, static_cast<size_t>(size));

            if (!payload_view.empty()) {
                volatile uint8_t marker = payload_view[0];
                (void)marker;
            }
            (void)id;
            (void)device_id;
        }
    }

private:
    sqlite3* db_;
};

} // namespace embedded_db
```
:::

---

### Частина 2: Векторизована стовпцева аналітика у DuckDB

DuckDB реалізує векторизоване виконання запитів, оптимізоване для обробки великих аналітичних масивів даних. Результати запиту повертаються не окремими кортежами, а блоками стовпців `DataChunk` фіксованого розміру (за замовчуванням 2048 значень).

Основні етапи виконання:
1. **Ініціалізація інстансу в пам'яті або на диску**: Функція `duckdb_open()` ініціалізує буферний пул та планувальник запитів безпосередньо в хост-процесі.
2. **Паралельне виконання**: Рушій розбиває операції сканування таблиці на дрібні кванти (Morsels) і розподіляє їх між потоками процесу без додаткових міжпроцесних синхронізацій.
3. **Прямий доступ до стовпцевих масивів**: Функція `duckdb_vector_get_data()` повертає покажчик на неперервний масив значень конкретного типу в пам'яті, що дозволяє застосовувати векторизовані інструкції процесора (SIMD).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <duckdb.h>

void execute_vectorized_analytics(void) {
    duckdb_database db;
    duckdb_connection con;

    /* Створення in-memory бази даних у адресному просторі процесу */
    if (duckdb_open(NULL, &db) == DuckDBError) {
        fprintf(stderr, "Помилка ініціалізації in-memory бази DuckDB\n");
        return;
    }

    if (duckdb_connect(db, &con) == DuckDBError) {
        duckdb_close(&db);
        return;
    }

    /* Створення таблиці та генерація 100 000 рядків тестових даних */
    duckdb_query(con, "CREATE TABLE telemetry (id BIGINT, sensor_val DOUBLE, status INTEGER);", NULL);
    duckdb_query(con, "INSERT INTO telemetry SELECT range, random() * 100.0, (range % 5)::INT FROM range(100000);", NULL);

    /* Виконання фільтрації та вибірки */
    duckdb_result result;
    if (duckdb_query(con, "SELECT id, sensor_val FROM telemetry WHERE status = 0;", &result) == DuckDBError) {
        fprintf(stderr, "Помилка запиту: %s\n", duckdb_result_error(&result));
        duckdb_destroy_result(&result);
        duckdb_disconnect(&con);
        duckdb_close(&db);
        return;
    }

    /* Отримання результатів через векторизовані пакети DataChunk */
    idx_t chunk_count = duckdb_result_chunk_count(result);
    for (idx_t i = 0; i < chunk_count; ++i) {
        duckdb_data_chunk chunk = duckdb_result_get_chunk(result, i);
        idx_t row_count = duckdb_data_chunk_get_size(chunk);

        /* Отримання векторів відповідних стовпців */
        duckdb_vector id_vec = duckdb_data_chunk_get_vector(chunk, 0);
        duckdb_vector val_vec = duckdb_data_chunk_get_vector(chunk, 1);

        /* Прямі покажчики на неперервні масиви пам'яті */
        int64_t *id_data = (int64_t*)duckdb_vector_get_data(id_vec);
        double *val_data = (double*)duckdb_vector_get_data(val_vec);

        /* Пакетне опрацювання векторів без копіювання */
        for (idx_t r = 0; r < row_count; ++r) {
            int64_t record_id = id_data[r];
            double value = val_data[r];
            (void)record_id;
            (void)value;
        }

        duckdb_destroy_data_chunk(&chunk);
    }

    duckdb_destroy_result(&result);
    duckdb_disconnect(&con);
    duckdb_close(&db);
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <duckdb.hpp>

namespace analytics {

class InProcessAnalytics {
public:
    InProcessAnalytics() : db_(nullptr), con_(db_) {
        con_.Query("CREATE TABLE metrics (timestamp BIGINT, value DOUBLE);");
        con_.Query("INSERT INTO metrics SELECT range, random() * 50.0 FROM range(500000);");
    }

    /* Вибірка з безкопійним читанням через нативний C++ API DuckDB */
    double calculate_parallel_aggregate() {
        auto result = con_.Query("SELECT value FROM metrics WHERE value > 25.0;");
        if (!result->success) {
            throw std::runtime_error(result->GetError());
        }

        double total_sum = 0.0;
        size_t total_rows = 0;

        /* Ітерація по векторних чанках DataChunk */
        while (auto chunk = result->Fetch()) {
            if (!chunk || chunk->size() == 0) break;

            /* Отримання стовпцевого масиву */
            auto& vector = chunk->data[0];
            const auto* values = duckdb::FlatVector::GetData<double>(vector);
            size_t count = chunk->size();

            /* Безпечний діапазон std::span */
            std::span<const double> value_span(values, count);

            for (double v : value_span) {
                total_sum += v;
            }
            total_rows += count;
        }

        return total_rows > 0 ? (total_sum / static_cast<double>(total_rows)) : 0.0;
    }

private:
    duckdb::DuckDB db_;
    duckdb::Connection con_;
};

} // namespace analytics
```
:::

---

### Частина 3: Пакетний запис у RocksDB через WriteBatch

У сховищах на базі LSM-дерева (RocksDB) виконання окремих точкових вставок створює надлишкове навантаження на журнал попереднього запису (WAL). Для максимальної пропускної здатності операції групуються в атомарні пакети `WriteBatch`.

Всі операції у `WriteBatch` додаються до пам'яті активного `MemTable` та записуються в єдиний послідовний блок WAL без блокування паралельних потоків читання.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <rocksdb/c.h>

void execute_rocksdb_batch(void) {
    rocksdb_options_t *options = rocksdb_options_create();
    rocksdb_options_set_create_if_missing(options, 1);
    rocksdb_options_increase_parallelism(options, 4);

    char *err = NULL;
    rocksdb_t *db = rocksdb_open(options, "embedded_kv.db", &err);
    if (err) {
        fprintf(stderr, "Помилка RocksDB: %s\n", err);
        rocksdb_free(err);
        rocksdb_options_destroy(options);
        return;
    }

    rocksdb_writebatch_t *batch = rocksdb_writebatch_create();
    for (int i = 0; i < 1000; ++i) {
        char key[32], val[64];
        snprintf(key, sizeof(key), "device:%04d:metric", i);
        snprintf(val, sizeof(val), "voltage=220.%d;temp=36.%d", i % 10, i % 10);
        rocksdb_writebatch_put(batch, key, strlen(key), val, strlen(val));
    }

    rocksdb_writeoptions_t *write_opts = rocksdb_writeoptions_create();
    rocksdb_writeoptions_set_sync(write_opts, 0); /* Асинхронний запис у буфер WAL */

    rocksdb_write(db, write_opts, batch, &err);
    if (err) {
        fprintf(stderr, "Помилка пакетного запису: %s\n", err);
        rocksdb_free(err);
    }

    rocksdb_writebatch_destroy(batch);
    rocksdb_writeoptions_destroy(write_opts);
    rocksdb_close(db);
    rocksdb_options_destroy(options);
}
```
```cpp
#include <iostream>
#include <string>
#include <memory>
#include <span>
#include <rocksdb/db.h>
#include <rocksdb/write_batch.h>

namespace kv_store {

class EmbeddedKeyValueStore {
public:
    explicit EmbeddedKeyValueStore(const std::string& db_path) {
        rocksdb::Options options;
        options.create_if_missing = true;
        options.IncreaseParallelism(4);
        options.OptimizeLevelStyleCompaction();

        rocksdb::DB* raw_db = nullptr;
        rocksdb::Status status = rocksdb::DB::Open(options, db_path, &raw_db);
        if (!status.ok()) {
            throw std::runtime_error("Не вдалося відкрити RocksDB: " + status.ToString());
        }
        db_.reset(raw_db);
    }

    void insert_batch(std::span<const std::pair<std::string, std::string>> records) {
        rocksdb::WriteBatch batch;
        for (const auto& [key, value] : records) {
            batch.Put(key, value);
        }

        rocksdb::WriteOptions write_opts;
        write_opts.sync = false;

        rocksdb::Status s = db_->Write(write_opts, &batch);
        if (!s.ok()) {
            throw std::runtime_error("Помилка запису пакета: " + s.ToString());
        }
    }

private:
    std::unique_ptr<rocksdb::DB> db_;
};

} // namespace kv_store
```
:::

---

### Керування контрольними точками та профілювання викликів

Окрім читання та запису, хост-процес несе відповідальність за життєвий цикл файлових сегментів та моніторинг швидкодії.

#### Режими контрольної точки WAL у SQLite

Скидання накопичених змін із файлу `.db-wal` в основний файл `.db` виконується функцією `sqlite3_wal_checkpoint_v2()` з одним із чотирьох режимів:
* **`SQLITE_CHECKPOINT_PASSIVE`**: Записує стільки сторінок, скільки можливо, без очікування завершення читачів. Не блокує паралельні потоки, але може перенести файл не повністю.
* **`SQLITE_CHECKPOINT_FULL`**: Очікує завершення всіх поточних читачів, блокує відкриття нових транзакцій читання і скидає всі сторінки до кінця логу.
* **`SQLITE_CHECKPOINT_RESTART`**: Працює аналогічно до `FULL`, але додатково гарантує, що наступні операції запису почнуть заповнювати WAL з самого початку файлу (зсув 0).
* **`SQLITE_CHECKPOINT_TRUNCATE`**: Після перезапуску логу обрізає розмір файлу `.db-wal` до 0 байтів через системний виклик `ftruncate()`, звільняючи місце на файловій системі.

#### Профілювання через хуки `sqlite3_trace_v2`

Оскільки у вбудованій СУБД немає мережевого аналізатора запитів (як `pg_stat_statements`), діагностика виконується реєстрацією колбеків у самому процесі:

```text
sqlite3_trace_v2(db, SQLITE_TRACE_STMT | SQLITE_TRACE_PROFILE, trace_callback, NULL);
```

Колбек отримує дескриптор `sqlite3_stmt*` та тривалість виконання у наносекундах (`nanoseconds`), що дозволяє реєструвати повільні запити безпосередньо у внутрішню систему метрик або OpenTelemetry хост-застосунку.

---

### Діагностика та критичні пастки реалізації

1. **Інвалідація Zero-Copy покажчиків при ітерації**:
   Покажчик на блок пам'яті, отриманий через `sqlite3_column_blob()` або `sqlite3_column_text()`, залишається валідним лише до наступного виклику `sqlite3_step()`, `sqlite3_reset()` або `sqlite3_finalize()`. Під час переходу до наступного рядка рушій бази даних може звільнити або повторно використати сторінку B-дерева в буферному пулі. Використання збереженого покажчика після ітерації створює невизначену поведінку (Use-After-Free).
2. **Блокування контрольної точки (Checkpoint Starvation)**:
   Коли потік відкриває операцію читання і залишає вираз активним без виклику `sqlite3_reset()`, у файлі спільної пам'яті `.db-shm` фіксується постійна відмітка читача (`Read Mark`). Якщо в цей час інший потік виконує інтенсивний запис, розмір файлу `.db-wal` постійно збільшується, оскільки автоматичний чекпойнт не може перенести сторінки, новіші за найстарішого активного читача. Це призводить до вичерпання дискового простору та падіння швидкодії.
3. **Лімітування пам'яті під керуванням cgroups**:
   Усі кеші вбудованих СУБД (пул сторінок SQLite, Block Cache у RocksDB, буфери DuckDB) ділять ліміт Resident Set Size (RSS) разом із кодом застосунку. Якщо розмір кешу бази даних встановлено без урахування пікового навантаження програми, операційна система надішле сигнал `SIGKILL` через механізм OOM Killer, що призведе до негайної зупинки всього сервісу.
