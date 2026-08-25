# ⚙️ Безпечний клієнт реляційної бази даних на C та C++

Взаємодія прикладного програмного забезпечення з реляційною базою даних через інтерфейс SQL вимагає суворого дотримання правил безпеки пам'яті, транзакційної ізоляції та захисту від ін'єкцій шкідливого коду. Динамічна конкатенація рядків запиту за допомогою функцій на зразок `sprintf` або оператора `+` у мові C++ відкриває критичні вразливості та змушує рушій СУБД щоразу повторно виконувати дорогі операції лексичного розбору, побудови AST та оптимізації плану. Єдиним промисловим стандартом побудови надійних клієнтів є використання підготовлених виразів (Prepared Statements) з типізованою бінарною прив'язкою параметрів і керуванням транзакцій через патерн RAII.

## Архітектура взаємодії клієнта з реляційним рушієм

Прикладний клієнт виконує роботу з реляційним рушієм через чітко розмежований життєвий цикл стадій:

```
[Ініціалізація з'єднання]
          │
          ▼
[Компіляція запиту: prepare] ──► Отримання бінарного дескриптора (sqlite3_stmt / Plan)
          │
          ▼
[Прив'язка параметрів: bind] ──► Передача типізованих скалярів (int, text, blob)
          │
          ▼
[Ітерація курсора: step]    ──► Порядкове зчитування кортежів (column_*)
          │
          ▼
[Скидання або фіналізація]  ──► reset / finalize для повернення ресурсів
```

### Протокол передачі: текстовий проти бінарного

У мережевих протоколах реляційних систем (PostgreSQL Frontend/Backend Protocol, MySQL Client/Server Protocol) взаємодія може відбуватися за двома моделями:
1. **Простий текстовий протокол (Simple Query Protocol):** Клієнт надсилає повний текст SQL-запиту у форматі ASCII/UTF-8. Сервер змушений щоразу запускати лексер, парсер, перевіряти каталог метаданих, генерувати фізичний план виконання та повертати результати у вигляді текстових рядків.
2. **Розширений бінарний протокол (Extended Query / Prepared Protocol):** Взаємодія розбивається на окремі повідомлення: `Parse` (компіляція шаблону запиту на сервері), `Bind` (передача двійкових значень параметрів у нативному форматі архітектури без перетворення на текст), `Execute` (виконання скомпільованого плану) та `Sync`. Це не лише унеможливлює зміну синтаксичної структури запиту зловмисником, а й суттєво зменшує обсяг мережевого трафіку та навантаження на процесор.

### Правила індексації та володіння пам'яттю

Під час низькорівневої роботи з клієнтським API (зокрема SQLite C API) інженер стикається з двома важливими особливостями:
- **Асиметрія нумерації:** Параметри підготовленого виразу у функціях `sqlite3_bind_*` нумеруються починаючи з **одиниці** (`1, 2, ...`), тоді як колонки результуючої вибірки у функціях `sqlite3_column_*` нумеруються починаючи з **нуля** (`0, 1, ...`). Плутанина в цій індексації є поширеним джерелом помилок часу виконання.
- **Стратегії володіння пам'яттю (`SQLITE_STATIC` проти `SQLITE_TRANSIENT`):** При прив'язці рядків або двійкових масивів `bind_text` прапорець `SQLITE_STATIC` вказує рушію, що буфер пам'яті належить викликаючій програмі і буде валідним протягом усього часу виконання запиту. Прапорець `SQLITE_TRANSIENT` змушує рушій негайно зробити власну копію рядка в оперативну пам'ять, що необхідно у випадках, коли вихідний буфер є тимчасовим (наприклад, локальна змінна стека).

## Реалізація клієнта: C проти сучасного C++20

Нижче наведено повноцінний робочий приклад клієнтського модуля бази даних (на прикладі C API вбудованого рушія SQLite), який реалізує безпечний транзакційний переказ коштів між банківськими рахунками та параметризоване читання даних.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sqlite3.h>

typedef struct {
    int64_t id;
    char name[64];
    int64_t balance_cents;
} Account;

/* Виконання транзакційного переказу коштів між рахунками */
int transfer_funds(sqlite3 *db, int64_t from_id, int64_t to_id, int64_t amount_cents) {
    sqlite3_stmt *stmt_debit = NULL;
    sqlite3_stmt *stmt_credit = NULL;
    char *err_msg = NULL;
    int rc = SQLITE_OK;

    /* 1. Початок ексклюзивної транзакції */
    rc = sqlite3_exec(db, "BEGIN IMMEDIATE TRANSACTION;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка відкриття транзакції: %s\n", err_msg);
        sqlite3_free(err_msg);
        return rc;
    }

    /* 2. Підготовка виразів для списання та зарахування */
    const char *sql_debit = "UPDATE accounts SET balance_cents = balance_cents - ? "
                            "WHERE id = ? AND balance_cents >= ?;";
    const char *sql_credit = "UPDATE accounts SET balance_cents = balance_cents + ? "
                             "WHERE id = ?;";

    rc = sqlite3_prepare_v2(db, sql_debit, -1, &stmt_debit, NULL);
    if (rc != SQLITE_OK) goto rollback;

    rc = sqlite3_prepare_v2(db, sql_credit, -1, &stmt_credit, NULL);
    if (rc != SQLITE_OK) goto rollback;

    /* 3. Прив'язка параметрів до виразу списання */
    sqlite3_bind_int64(stmt_debit, 1, amount_cents);
    sqlite3_bind_int64(stmt_debit, 2, from_id);
    sqlite3_bind_int64(stmt_debit, 3, amount_cents);

    rc = sqlite3_step(stmt_debit);
    if (rc != SQLITE_DONE) goto rollback;

    /* Перевірка, чи було оновлено рядок (наявність коштів) */
    if (sqlite3_changes(db) == 0) {
        fprintf(stderr, "Недостатньо коштів або рахунок не знайдено: id=%lld\n", (long long)from_id);
        goto rollback;
    }

    /* 4. Прив'язка параметрів до виразу зарахування */
    sqlite3_bind_int64(stmt_credit, 1, amount_cents);
    sqlite3_bind_int64(stmt_credit, 2, to_id);

    rc = sqlite3_step(stmt_credit);
    if (rc != SQLITE_DONE) goto rollback;

    if (sqlite3_changes(db) == 0) {
        fprintf(stderr, "Рахунок отримувача не знайдено: id=%lld\n", (long long)to_id);
        goto rollback;
    }

    /* 5. Фіксація транзакції */
    rc = sqlite3_exec(db, "COMMIT TRANSACTION;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка COMMIT: %s\n", err_msg);
        sqlite3_free(err_msg);
        goto rollback;
    }

    sqlite3_finalize(stmt_debit);
    sqlite3_finalize(stmt_credit);
    return SQLITE_OK;

rollback:
    sqlite3_exec(db, "ROLLBACK TRANSACTION;", NULL, NULL, NULL);
    if (stmt_debit) sqlite3_finalize(stmt_debit);
    if (stmt_credit) sqlite3_finalize(stmt_credit);
    return SQLITE_ERROR;
}

/* Безпечна параметризована вибірка даних */
int query_account(sqlite3 *db, int64_t account_id, Account *out_account) {
    sqlite3_stmt *stmt = NULL;
    const char *sql = "SELECT id, name, balance_cents FROM accounts WHERE id = ?;";

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка підготовки виразу: %s\n", sqlite3_errmsg(db));
        return rc;
    }

    sqlite3_bind_int64(stmt, 1, account_id);

    rc = sqlite3_step(stmt);
    if (rc == SQLITE_ROW) {
        out_account->id = sqlite3_column_int64(stmt, 0);
        const unsigned char *text = sqlite3_column_text(stmt, 1);
        snprintf(out_account->name, sizeof(out_account->name), "%s", text ? (const char*)text : "");
        out_account->balance_cents = sqlite3_column_int64(stmt, 2);
        sqlite3_finalize(stmt);
        return SQLITE_OK;
    }

    sqlite3_finalize(stmt);
    return SQLITE_NOTFOUND;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <cstdint>
#include <sqlite3.h>

struct Account {
    std::int64_t id{0};
    std::string name;
    std::int64_t balance_cents{0};
};

/* RAII-обгортка над дескриптором підготовленого виразу */
class PreparedStatement {
public:
    explicit PreparedStatement(sqlite3* db, std::string_view sql) {
        sqlite3_stmt* raw_stmt = nullptr;
        int rc = sqlite3_prepare_v2(db, sql.data(), static_cast<int>(sql.size()), &raw_stmt, nullptr);
        if (rc != SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(db));
        }
        stmt_.reset(raw_stmt);
    }

    void bind_int64(int index, std::int64_t value) {
        if (sqlite3_bind_int64(stmt_.get(), index, value) != SQLITE_OK) {
            throw std::runtime_error("Помилка прив'язки int64");
        }
    }

    void bind_text(int index, std::string_view text) {
        if (sqlite3_bind_text(stmt_.get(), index, text.data(), static_cast<int>(text.size()), SQLITE_TRANSIENT) != SQLITE_OK) {
            throw std::runtime_error("Помилка прив'язки text");
        }
    }

    bool step() {
        int rc = sqlite3_step(stmt_.get());
        if (rc == SQLITE_ROW) return true;
        if (rc == SQLITE_DONE) return false;
        throw std::runtime_error("Помилка під час ітерації курсора");
    }

    void reset() {
        sqlite3_reset(stmt_.get());
        sqlite3_clear_bindings(stmt_.get());
    }

    [[nodiscard]] sqlite3_stmt* get() const noexcept { return stmt_.get(); }

private:
    struct StmtDeleter {
        void operator()(sqlite3_stmt* s) const noexcept {
            if (s) sqlite3_finalize(s);
        }
    };
    std::unique_ptr<sqlite3_stmt, StmtDeleter> stmt_;
};

/* RAII-обгортка для автоматичного керування життєвим циклом транзакцій */
class ScopedTransaction {
public:
    explicit ScopedTransaction(sqlite3* db) : db_(db), committed_(false) {
        char* err_msg = nullptr;
        if (sqlite3_exec(db_, "BEGIN IMMEDIATE TRANSACTION;", nullptr, nullptr, &err_msg) != SQLITE_OK) {
            std::string err = err_msg ? err_msg : "Невідома помилка BEGIN";
            sqlite3_free(err_msg);
            throw std::runtime_error(err);
        }
    }

    void commit() {
        char* err_msg = nullptr;
        if (sqlite3_exec(db_, "COMMIT TRANSACTION;", nullptr, nullptr, &err_msg) != SQLITE_OK) {
            std::string err = err_msg ? err_msg : "Невідома помилка COMMIT";
            sqlite3_free(err_msg);
            throw std::runtime_error(err);
        }
        committed_ = true;
    }

    ~ScopedTransaction() noexcept {
        if (!committed_ && db_) {
            sqlite3_exec(db_, "ROLLBACK TRANSACTION;", nullptr, nullptr, nullptr);
        }
    }

    ScopedTransaction(const ScopedTransaction&) = delete;
    ScopedTransaction& operator=(const ScopedTransaction&) = delete;

private:
    sqlite3* db_;
    bool committed_;
};

/* Керування переказом коштів з автоматичним відкатом при винятках */
void transfer_funds(sqlite3* db, std::int64_t from_id, std::int64_t to_id, std::int64_t amount_cents) {
    ScopedTransaction tx(db);

    PreparedStatement stmt_debit(db, "UPDATE accounts SET balance_cents = balance_cents - ? "
                                     "WHERE id = ? AND balance_cents >= ?;");
    stmt_debit.bind_int64(1, amount_cents);
    stmt_debit.bind_int64(2, from_id);
    stmt_debit.bind_int64(3, amount_cents);

    stmt_debit.step();
    if (sqlite3_changes(db) == 0) {
        throw std::runtime_error("Недостатньо коштів або рахунок платника не знайдено");
    }

    PreparedStatement stmt_credit(db, "UPDATE accounts SET balance_cents = balance_cents + ? WHERE id = ?;");
    stmt_credit.bind_int64(1, amount_cents);
    stmt_credit.bind_int64(2, to_id);

    stmt_credit.step();
    if (sqlite3_changes(db) == 0) {
        throw std::runtime_error("Рахунок отримувача не знайдено");
    }

    tx.commit();
}
```
:::

## Механіка захисту від ін'єкцій та оптимізація кешу

Використання підготовлених виразів повністю ліквідує можливість SQL-ін'єкцій завдяки суворому розмежуванню стадій обробки:

1. **Ізоляція синтаксичного дерева (AST):** Під час виклику функції `prepare` парсер реляційного сервера будує абстрактне дерево запиту та фіксує його граматичну структуру. Усі динамічні значення позначаються спеціальними позиційними вузлами (`ParameterNode`). Зловмисник не може змінити структуру дерева (додати нові секції `WHERE`, оператори `UNION` чи коментарі `--`), оскільки граматичний аналіз завершується до передачі будь-яких користувацьких даних.
2. **Бінарна типізована прив'язка:** Під час виконання `bind` передані байти записуються у внутрішні змінні сесії як значення відповідного домену (ціле число, дата, двійковий блоб). Рядок `' OR 1=1; DROP TABLE users; --` сприймається рушієм виключно як текстовий літерал поля, а не як набір команд SQL.
3. **Економія ресурсів процесора через кешування планів:** Компіляція складного SQL-запиту з кількома `JOIN` та агрегаціями вимагає проходження лексичного аналізу, валідації типів у каталозі та перебору простору фізичних планів вартісним оптимізатором. При високому навантаженні (OLTP-профіль із тисячами однотипних транзакцій на секунду) компіляція може займати до 70% загального часу виконання запиту.
4. **Управління життєвим циклом ресурсів у C++:** Застосування патерну RAII у класах `ScopedTransaction` та `PreparedStatement` гарантує, що при виникненні будь-якої виняткової ситуації (помилка мережі, порушення обмеження зовнішнього ключа, збій алокації пам'яті) деструктори об'єктів автоматично викликають `ROLLBACK` та звільняють пам'ять дескрипторів без витоків ресурсів або блокувань бази даних.

## Блокування транзакцій та обробка інвалідації схеми

У високонавантажених прикладних системах важливу роль відіграють два додаткові аспекти роботи з клієнтським драйвером:

### 1. Рівні початкового блокування транзакцій
- При використанні команди `BEGIN DEFERRED` рушій бази даних не накладає блокувань до моменту першої операції запису. Якщо два конкурентні потоки одночасно зчитують баланс рахунку, а потім намагаються його оновити, один із них зазнає помилки `SQLITE_BUSY` (або `deadlock_detected` у мережевих СУБД) через взаємну ескалацію блокувань.
- Використання `BEGIN IMMEDIATE` змушує рушій відразу захопити блокування запису (`RESERVED lock`), запобігаючи одночасному старту конкурентних пишучих транзакцій та ліквідуючи взаємні блокування на рівні клієнтської логіки.

### 2. Інвалідація кешу підготовлених виразів (`SQLITE_SCHEMA`)
Якщо інший клієнт виконує операцію DDL (наприклад, `ALTER TABLE accounts ADD COLUMN status INT` або перестворює індекс), внутрішня версія схеми бази даних збільшується. При спробі виконати раніше скомпільований вираз через `sqlite3_step` рушій повертає код помилки `SQLITE_SCHEMA`. Промисловий клієнт повинен обробляти цей випадок через цикл автоматичної перекомпіляції: фіналізувати застарілий вираз, повторно викликати `prepare` над тим самим SQL-текстом з урахуванням нової схеми, заново виконати `bind` параметрів та продовжити роботу без аварійного завершення програми.
