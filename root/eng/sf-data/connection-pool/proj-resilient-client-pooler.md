# ⚙️ Резильєнтний клієнт транзакційного пулера

Цей проект демонструє побудову високопродуктивного та відмовостійкого клієнтського адаптера до бази даних мовами C та C++, спеціально спроектованого для взаємодії з проміжними транзакційними пулерами (зокрема PgBouncer). Проект охоплює механізм неблокуючої перевірки здоров'я TCP-дескриптора на рівні ядра операційної системи, алгоритм експоненційного відступу з повним джитером, обробку сигналів операційної системи та безпечне управління транзакційними межами.

## Специфіка роботи клієнта через транзакційний проксі

Пряме підключення застосунку до СУБД відрізняється від роботи через проміжний проксі-шар. У разі використання PgBouncer або ProxySQL клієнт взаємодіє не з фізичним ядром бази даних, а з проксі-демоном, який динамічно комутує клієнтські сокети на обмежений пул бекендів.

Така архітектура породжує три критичні інженерні виклики:

1. **Несподіване закриття сокета проксі-сервером**: PgBouncer регулярно закриває клієнтські сокети за таймаутом бездіяльності (`client_idle_timeout`), під час виконання планової ротації серверних з'єднань (`server_lifetime`) або при примусовому перезапуску сервісу для оновлення конфігурації. Якщо клієнт наївно спробує надіслати новий SQL-запит у такий розірваний сокет, операційна система згенерує сигнал `SIGPIPE` або поверне помилку `EPIPE` / `ECONNRESET`, що призведе до аварійного завершення потоку застосунку або падіння вхідного HTTP-запиту користувача.
2. **Неможливість збереження сесійного контексту**: у режимі `pool_mode = transaction` спроба використання іменованих підготовлених виразів (`PREPARE stmt_name`) або змінних сесії (`SET timezone`) призводить до мовчазних помилок, оскільки наступний запит може бути виконаний на зовсім іншому бекенді. Клієнт повинен працювати в режимі суворої ізоляції транзакцій.
3. **Проблема лавини повторних підключень (Thundering Herd)**: якщо під час планового перемикання майстер-вузла бази даних (failover) сотні мікросервісів одночасно втрачають зв'язок із проксі і починають миттєво штурмувати його повторними викликами `connect()`, вони повністю забивають мережевий стек ядра (`TCP SYN backlog queue`), не даючи пулеру піднятися.

## Детальний розбір компонентів архітектури

Реалізація складається з трьох ключових інженерних блоків:

### 1. Неблокуюча перевірка сокета (Zero-RTT Socket Peeking)

Класичний підхід із виконанням перевірочного запиту `SELECT 1` перед кожною транзакцією (`test-on-borrow`) додає повний мережевий RTT (Round Trip Time), що неприпустимо сповільнює високонавантажену систему. 

Натомість ми використовуємо системний виклик `poll()` разом із `recv(..., MSG_PEEK | MSG_DONTWAIT)`. Цей системний виклик перевіряє чергу сокета безпосередньо в пам'яті ядра операційної системи за 0 мілісекунд:
- якщо сокет отримав пакет `TCP FIN` або `TCP RST` від проксі, `poll()` повертає прапорець `POLLRDHUP` або `POLLHUP`;
- виклик `recv` із прапорцем `MSG_PEEK` дивиться на перший байт буфера без його вилучення: якщо повертається `0`, це означає отримання сигналу `EOF` (з'єднання закрито віддаленою стороною);
- якщо сокет у нормі, `recv` повертає помилку `EAGAIN` чи `EWOULDBLOCK`, що свідчить про відкритий і готовий до роботи канал.

### 2. Експоненційний відступ з повним джитером (Full Jitter Backoff)

Алгоритм повторних підключень використовує математичну модель експоненційного збільшення вікна очікування, помножену на рівномірний випадковий джитер (Full Jitter):

```
T_backoff = min(T_max, T_base * 2^attempt)
T_sleep = Uniform(0, T_backoff)
```

Завдяки рівномірному розподілу `Uniform(0, T_backoff)` сотні клієнтів, що одночасно втратили зв'язок, рівномірно розсіюють свої спроби підключення по всій часовій шкалі, запобігаючи виникненню резонансних сплесків трафіку.

### 3. Транзакційний бар'єр та RAII-очищення ресурсів

Кожна операція загортається в явні межі `BEGIN` та `COMMIT`. У разі виникнення будь-якої помилки під час виконання запиту або розриву зв'язку адаптер гарантовано викликає `ROLLBACK` та звільняє виділені ресурси пам'яті за допомогою ідіоми RAII (Resource Acquisition Is Initialization) у версії для C++.

## Програмні реалізації

Нижче наведено повні виробничі реалізації адаптера мовами C та C++ для бібліотеки `libpq`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <libpq-fe.h>

#define BASE_BACKOFF_MS 50
#define MAX_BACKOFF_MS 2000
#define MAX_RETRIES 5

typedef struct {
    PGconn *conn;
    char conninfo[256];
} DbClient;

/* Неблокуюча перевірка стану TCP-дескриптора в ядрі ОС */
static bool is_socket_alive(PGconn *conn) {
    if (!conn || PQstatus(conn) != CONNECTION_OK) {
        return false;
    }
    int fd = PQsocket(conn);
    if (fd < 0) return false;

    struct pollfd pfd = { 
        .fd = fd, 
        .events = POLLIN | POLLRDHUP | POLLERR | POLLHUP, 
        .revents = 0 
    };

    int ret = poll(&pfd, 1, 0); // 0 мс — миттєве неблокуюче опитування буферів ядра
    if (ret < 0) return false;
    if (ret > 0) {
        if (pfd.revents & (POLLERR | POLLHUP | POLLRDHUP)) {
            return false;
        }
        if (pfd.revents & POLLIN) {
            char buf[1];
            ssize_t n = recv(fd, buf, sizeof(buf), MSG_PEEK | MSG_DONTWAIT);
            if (n == 0) return false; // Отримано FIN від пулера (EOF)
            if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) return false;
        }
    }
    return true;
}

/* Відновлення з'єднання з експоненційним відступом та джитером */
static bool db_reconnect(DbClient *client) {
    if (client->conn) {
        PQfinish(client->conn);
        client->conn = NULL;
    }

    int delay_ms = BASE_BACKOFF_MS;
    for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        client->conn = PQconnectdb(client->conninfo);
        if (PQstatus(client->conn) == CONNECTION_OK) {
            return true;
        }

        PQfinish(client->conn);
        client->conn = NULL;

        // Full Jitter = random(0, delay_ms)
        int jitter = rand() % (delay_ms + 1);
        usleep((useconds_t)jitter * 1000);

        delay_ms *= 2;
        if (delay_ms > MAX_BACKOFF_MS) delay_ms = MAX_BACKOFF_MS;
    }
    return false;
}

DbClient* db_client_create(const char *conninfo) {
    DbClient *client = (DbClient*)malloc(sizeof(DbClient));
    if (!client) return NULL;
    strncpy(client->conninfo, conninfo, sizeof(client->conninfo) - 1);
    client->conninfo[sizeof(client->conninfo) - 1] = '\0';
    client->conn = NULL;

    if (!db_reconnect(client)) {
        free(client);
        return NULL;
    }
    return client;
}

void db_client_destroy(DbClient *client) {
    if (!client) return;
    if (client->conn) PQfinish(client->conn);
    free(client);
}

/* Виконання атомарної транзакції через транзакційний пулер */
bool db_execute_transaction(DbClient *client, const char *sql_update, const char *sql_log) {
    if (!is_socket_alive(client->conn)) {
        if (!db_reconnect(client)) return false;
    }

    PGresult *res = PQexec(client->conn, "BEGIN");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        return false;
    }
    PQclear(res);

    res = PQexec(client->conn, sql_update);
    if (PQresultStatus(res) != PGRES_COMMAND_OK && PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(client->conn, "ROLLBACK");
        return false;
    }
    PQclear(res);

    res = PQexec(client->conn, sql_log);
    if (PQresultStatus(res) != PGRES_COMMAND_OK && PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(client->conn, "ROLLBACK");
        return false;
    }
    PQclear(res);

    res = PQexec(client->conn, "COMMIT");
    bool ok = (PQresultStatus(res) == PGRES_COMMAND_OK);
    PQclear(res);
    return ok;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <chrono>
#include <random>
#include <thread>
#include <expected>
#include <system_error>
#include <poll.h>
#include <sys/socket.h>
#include <libpq-fe.h>

class DatabaseError : public std::runtime_error {
public:
    explicit DatabaseError(const std::string& msg) : std::runtime_error(msg) {}
};

/* RAII-керування життєвим циклом низькорівневих C-структур libpq */
struct PgConnDeleter { 
    void operator()(PGconn* p) const noexcept { 
        if (p) PQfinish(p); 
    } 
};

struct PgResultDeleter { 
    void operator()(PGresult* p) const noexcept { 
        if (p) PQclear(p); 
    } 
};

using UniquePgConn = std::unique_ptr<PGconn, PgConnDeleter>;
using UniquePgResult = std::unique_ptr<PGresult, PgResultDeleter>;

class ResilientDbClient {
public:
    explicit ResilientDbClient(std::string conninfo)
        : conninfo_(std::move(conninfo)), rng_(std::random_device{}()) {
        if (!reconnect()) {
            throw DatabaseError("Не вдалося встановити початкове з'єднання з пулером");
        }
    }

    /* Виконання функції всередині безпечної транзакції з RAII-відкатом */
    template <typename Func>
    auto withTransaction(Func&& action) -> std::expected<void, std::string> {
        ensureHealthyConnection();

        auto resBegin = execQuery("BEGIN");
        if (!resBegin || PQresultStatus(resBegin.get()) != PGRES_COMMAND_OK) {
            return std::unexpected("Помилка старту транзакції (BEGIN): " + getLastError());
        }

        try {
            action(conn_.get());
        } catch (...) {
            execQuery("ROLLBACK");
            throw;
        }

        auto resCommit = execQuery("COMMIT");
        if (!resCommit || PQresultStatus(resCommit.get()) != PGRES_COMMAND_OK) {
            execQuery("ROLLBACK");
            return std::unexpected("Помилка фіксації транзакції (COMMIT): " + getLastError());
        }

        return {};
    }

    UniquePgResult execQuery(std::string_view sql) {
        return UniquePgResult(PQexec(conn_.get(), sql.data()));
    }

private:
    std::string conninfo_;
    UniquePgConn conn_;
    std::mt19937 rng_;

    static constexpr int kBaseBackoffMs = 50;
    static constexpr int kMaxBackoffMs = 2000;
    static constexpr int kMaxRetries = 5;

    bool isSocketAlive() const noexcept {
        if (!conn_ || PQstatus(conn_.get()) != CONNECTION_OK) return false;
        int fd = PQsocket(conn_.get());
        if (fd < 0) return false;

        pollfd pfd{ .fd = fd, .events = POLLIN | POLLRDHUP | POLLERR | POLLHUP, .revents = 0 };
        int ret = poll(&pfd, 1, 0);
        if (ret < 0) return false;
        if (ret > 0) {
            if (pfd.revents & (POLLERR | POLLHUP | POLLRDHUP)) return false;
            if (pfd.revents & POLLIN) {
                char buf[1];
                ssize_t n = recv(fd, buf, sizeof(buf), MSG_PEEK | MSG_DONTWAIT);
                if (n == 0) return false;
                if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) return false;
            }
        }
        return true;
    }

    void ensureHealthyConnection() {
        if (!isSocketAlive()) {
            if (!reconnect()) {
                throw DatabaseError("Втрата з'єднання з пулером, повторні спроби вичерпано");
            }
        }
    }

    bool reconnect() {
        conn_.reset();
        int currentBackoff = kBaseBackoffMs;

        for (int attempt = 1; attempt <= kMaxRetries; ++attempt) {
            conn_.reset(PQconnectdb(conninfo_.c_str()));
            if (PQstatus(conn_.get()) == CONNECTION_OK) {
                return true;
            }

            conn_.reset();
            std::uniform_int_distribution<int> dist(0, currentBackoff);
            int sleepTime = dist(rng_);
            std::this_thread::sleep_for(std::chrono::milliseconds(sleepTime));

            currentBackoff = std::min(currentBackoff * 2, kMaxBackoffMs);
        }
        return false;
    }

    std::string getLastError() const {
        return conn_ ? PQerrorMessage(conn_.get()) : "Немає активного сокета";
    }
};
```
:::

## Тестування та обробка крайових випадків

Під час розгортання клієнта у виробничому середовищі слід враховувати такі крайові сценарії:

1. **Мережеві розділення (Network Partitions)**: якщо мережеве обладнання мовчки відкидає пакети без надсилання `RST`, сокет залишається відкритим у стані `ESTABLISHED`. Для детекції таких «завислих» з'єднань на рівні операційної системи необхідно вмикати системні таймери TCP Keepalive (`TCP_KEEPIDLE = 60`, `TCP_KEEPINTVL = 10`, `TCP_KEEPCNT = 3`).
2. **Переривання системних викликів сигналами ОС**: виклик `poll()` може повернути `-1` з кодом `errno == EINTR` у разі отримання сигналу процесом (наприклад, під час ротації логів чи отримання сигналів таймера). У продакшн-коді перевірку `poll()` слід загортати в цикл повтору при `EINTR`, щоб запобігти хибному розриву з'єднання.
3. **Обмеження розміру буферів читання**: під час виконання важких аналітичних вибірок результат `PGresult` виділяється в оперативній пам'яті клієнта повністю. Для стрімінгу гігабайтних даних через транзакційний пулер слід використовувати механізм курсорів з виділеним сесійним з'єднанням або розбиття вибірки на порції (пагінацію за первинним ключем).
4. **Поведінка під час автоматичного Failover**: коли кластер перемикає лідера на репліку, PgBouncer тимчасово повертає помилку `server login failed: server closed the connection unexpectedly` або переводить базу в стан `PAUSE`. Клієнтський адаптер за допомогою експоненційного відступу плавно пережидає період перемикання (зазвичай 3–10 секунд) і відновлює виконання транзакцій на новому лідері без втручання оператора.
5. **Потокобезпечність та ізоляція дескрипторів**: дескриптор `PGconn` не є потокобезпечним (thread-safe) для одночасного запису з кількох системних потоків. Кожен робочий потік або володіє власним екземпляром `ResilientDbClient`, або бере адаптер у короткострокову оренду з локального пулу на час виконання одного запиту, що гарантує відсутність гонитви даних (data races) у буферах `libpq`.
