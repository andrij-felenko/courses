# ⚙️ Анатомія ціни: монолітна ACID-транзакція проти Saga та Transactional Outbox

Гаряча дискусія про моноліти й мікросервіси часто зупиняється на загальних концептуальних поняттях. Проте справжня ціна архітектурного вибору вимірюється не слайдами й не абстрактними схемами, а конкретними рядками коду, обробкою крайових випадків, додатковими інфраструктурними компонентами та складностями відлагодження. 

Щоб побачити цю різницю наочно, проаналізуємо реалізацію однієї й тієї самої бізнес-операції — **«Оформлення замовлення»** (списання балансу користувача + резервування товару на складі + створення підтвердженого замовлення) — у двох протилежних архітектурних парадигмах: у межах атомарної транзакції моноліта та у вигляді розподіленого патерну Saga з використанням Transactional Outbox у мікросервісах.

---

## Частина 1: Атомарна транзакція в моноліті (ACID)

У монолітній архітектурі сервіси списання коштів, управління складськими залишками та оформлення замовлень живуть у єдиному процесі та звертаються до однієї реляційної бази даних. Гарантія консистентності даних забезпечується безпосередньо СУБД через стандартний механізм ACID-транзакцій.

### Механіка роботи в єдиній СУБД

Під час виклику `BEGIN TRANSACTION` база даних створює транзакційний контекст. Усі подальші SQL-запити (`UPDATE accounts`, `UPDATE inventory`, `INSERT INTO orders`) виконуються в межах цього контексту. 

1. **Гарантія атомарності (Atomicity):** СУБД веде журнал попереднього запису (Write-Ahead Log, WAL). Якщо на третьому кроці з'ясовується, що товару немає в наявності або виникла мережева помилка з диском, команда `ROLLBACK` скасовує всі попередні зміни в пам'яті та на диску за мілісекунди. Проміжний стан ніколи не стає видимим для інших сесій.
2. **Гарантія ізоляції (Isolation):** на рівні `Read Committed` або `Repeatable Read` СУБД гарантує, що інші паралельні транзакції не побачать списані гроші або зарезервований товар доти, доки не буде викликано `COMMIT`.
3. **Простота коду:** розробнику не потрібно писати логіку відкату чи створювати компенсуючі подіях у коді — весь тягар скасування лежить на рушії реляційної бази даних.

### Реалізація монолітної транзакції

:::tabs
```go
// Go: Атомарне оформлення замовлення у модульному моноліті
func (s *OrderService) CreateOrderMonolith(ctx context.Context, userID string, itemID string, amount int64) error {
    // Відкриття атомарної транзакції в єдиній СУБД
    tx, err := s.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
    if err != nil {
        return fmt.Errorf("помилка відкриття транзакції: %w", err)
    }
    // RAII-подібний захист: Rollback автоматично ігнорується, якщо вже викликано Commit
    defer tx.Rollback()

    // Крок 1. Перевірка та списання балансу користувача
    res, err := tx.ExecContext(ctx, 
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2 AND balance >= $1", 
        amount, userID)
    if err != nil {
        return fmt.Errorf("помилка виконання SQL списання: %w", err)
    }
    if rows, _ := res.RowsAffected(); rows == 0 {
        return errors.New("недостатньо коштів на балансі користувача")
    }

    // Крок 2. Резервування позиції товару на складі
    res, err = tx.ExecContext(ctx, 
        "UPDATE inventory SET stock = stock - 1 WHERE item_id = $1 AND stock >= 1", 
        itemID)
    if err != nil {
        return fmt.Errorf("помилка виконання SQL резервування: %w", err)
    }
    if rows, _ := res.RowsAffected(); rows == 0 {
        return errors.New("товару немає в наявності на складі")
    }

    // Крок 3. Створення підтвердженого запису замовлення
    _, err = tx.ExecContext(ctx, 
        "INSERT INTO orders (user_id, item_id, amount, status) VALUES ($1, $2, $3, 'COMPLETED')", 
        userID, itemID, amount)
    if err != nil {
        return fmt.Errorf("помилка створення запису замовлення: %w", err)
    }

    // Фіксація всіх трьох оновлень атомарно
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("помилка фіксації транзакції: %w", err)
    }
    return nil
}
```
```cpp
// C++20: Атомарне оформлення замовлення у моноліті (із застосуванням RAII для транзакції)
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

class DatabaseTransaction {
public:
    explicit DatabaseTransaction(void* db_conn) : conn_(db_conn), committed_(false) {}
    
    ~DatabaseTransaction() {
        if (!committed_) {
            try {
                rollback();
            } catch (...) {}
        }
    }
    
    void commit() {
        // Запит до СУБД: COMMIT TRANSACTION
        committed_ = true;
    }
    
    void rollback() {
        // Запит до СУБД: ROLLBACK TRANSACTION
    }
    
    void execute(const std::string& query) {
        // Виконання SQL-запиту в межах транзакційного контексту
    }

private:
    void* conn_;
    bool committed_;
};

class OrderService {
public:
    void createOrderMonolith(const std::string& user_id, const std::string& item_id, int64_t amount) {
        DatabaseTransaction tx(db_conn_);

        // 1. Перевірка та списання балансу
        tx.execute("UPDATE accounts SET balance = balance - " + std::to_string(amount) + 
                   " WHERE id = '" + user_id + "' AND balance >= " + std::to_string(amount));

        // 2. Резервування товару
        tx.execute("UPDATE inventory SET stock = stock - 1 WHERE item_id = '" + item_id + "' AND stock >= 1");

        // 3. Створення запису замовлення
        tx.execute("INSERT INTO orders (user_id, item_id, amount, status) VALUES ('" + 
                   user_id + "', '" + item_id + "', " + std::to_string(amount) + ", 'COMPLETED')");

        // Атомарна фіксація. Якщо виникне виняток вище, деструктор tx виконає rollback()
        tx.commit();
    }
private:
    void* db_conn_{nullptr};
};
```
:::

---

## Частина 2: Розподілена Saga з патерном Transactional Outbox

У мікросервісній архітектурі дотримується принцип **Database per Service**. Сервіс замовлень (Order Service), сервіс платежів (Payment Service) та сервіс складу (Inventory Service) розгорнуті в різних контейнерах і працюють з трьома повністю ізольованими базами даних. 

Прямий двохфазний коміт (2PC) у розподілених Web-системах використовувати заборонено через високий ризик залюднення блокувань і падіння доступності. Тому єдиним робочим варіантом стає побудова **асинхронної Saga** з кінцевою узгодженістю (Eventual Consistency).

### Складові частини інфраструктурного ланцюжка

Для гарантування того, що подія про створення замовлення гарантовано дійде до брокера повідомлень (Kafka чи RabbitMQ) і не загубиться при аварійному перезавантаженні сервісу, застосовують паттерн **Transactional Outbox**:

1. **Order Service DB:** містить основну таблицю `orders` та додаткову таблицю `outbox`.
2. **Outbox Relay (Debezium / CDC або Worker):** окремий фоновий процес, який вичитає нові записи з таблиці `outbox` (через лог транзакцій PostgreSQL WAL або періодичний poll) і відправляв їх у Kafka.
3. **Payment Service Consumer:** слухає тему Kafka, виконує локальне списання у своїй БД і публікує подію `PaymentProcessed` або `PaymentFailed`.
4. **Inventory Service Consumer:** слухає події від Payment Service, резервує товар у своїй БД і публікує `InventoryReserved` або `InventoryFailed`.
5. **Compensating Engine (Логіка компенсації):** якщо на етапі резервування товару сталася помилка, Order Service або оркестратор змушений відправити компенсуючу команду `RefundPayment` до Payment Service для повернення раніше списаних коштів.

### Код збереження події через Transactional Outbox (Order Service)

:::tabs
```go
// Go: Створення замовлення та збереження події в Outbox у межах однієї локальної транзакції
func (s *OrderService) CreateOrderOutbox(ctx context.Context, orderID, userID, itemID string, amount int64) error {
    tx, err := s.db.BeginTx(ctx, nil)
    if err != nil {
        return fmt.Errorf("помилка відкриття транзакції: %w", err)
    }
    defer tx.Rollback()

    // 1. Запис замовлення у тимчасовому статусі PENDING
    _, err = tx.ExecContext(ctx, 
        "INSERT INTO orders (id, user_id, item_id, amount, status) VALUES ($1, $2, $3, $4, 'PENDING')",
        orderID, userID, itemID, amount)
    if err != nil {
        return fmt.Errorf("помилка створення PENDING замовлення: %w", err)
    }

    // 2. Атомарний запис події у локальну таблицю Outbox у ТІЙ СМІЙ транзакції БД
    eventPayload := fmt.Sprintf(`{"order_id":"%s","user_id":"%s","item_id":"%s","amount":%d}`, 
        orderID, userID, itemID, amount)
    
    _, err = tx.ExecContext(ctx, 
        "INSERT INTO outbox (id, aggregate_type, aggregate_id, type, payload, created_at) VALUES ($1, 'Order', $2, 'OrderCreated', $3, NOW())",
        uuid.New().String(), orderID, eventPayload)
    if err != nil {
        return fmt.Errorf("помилка запису в outbox: %w", err)
    }

    // Коміт гарантує: подія в Outbox з'явиться ТІЛЬКИ якщо замовлення збережено в БД
    return tx.Commit()
}
```
```cpp
// C++20: Атомарне збереження бізнес-сутності та Outbox-події
#include <string>
#include <stdexcept>

class OutboxPublisher {
public:
    void createOrderWithOutbox(const std::string& order_id, const std::string& user_id, 
                               const std::string& item_id, int64_t amount) {
        DatabaseTransaction tx(db_conn_);

        // 1. Запис замовлення зі статусом PENDING
        tx.execute("INSERT INTO orders (id, user_id, item_id, amount, status) VALUES ('" +
                   order_id + "', '" + user_id + "', '" + item_id + "', " + std::to_string(amount) + ", 'PENDING')");

        // 2. Гарантований запис події в Outbox-таблицю
        std::string payload = "{\"order_id\":\"" + order_id + "\",\"user_id\":\"" + user_id + 
                              "\",\"amount\":" + std::to_string(amount) + "}";
        tx.execute("INSERT INTO outbox (aggregate_type, aggregate_id, type, payload) VALUES ('Order', '" +
                   order_id + "', 'OrderCreated', '" + payload + "')");

        tx.commit(); // Обидва записи комітяться атомарно
    }
private:
    void* db_conn_{nullptr};
};
```
:::

### Код обробки компенсації та перевірки ідемпотентності у Payment Service

Оскільки Kafka гарантує доставку повідомлень за рівнем «at-least-once» (щонайменше один раз), один і той самий сигнал про компенсацію може прийти повторно. Обробник зобов'язаний бути **суворо ідемпотентним**.

:::tabs
```go
// Go: Обробка компенсуючої події (повернення коштів) з перевіркою ідемпотентності
func (p *PaymentConsumer) HandleRefundCompensation(ctx context.Context, msg KafkaMessage) error {
    var event CompensatePaymentEvent
    if err := json.Unmarshal(msg.Value, &event); err != nil {
        return fmt.Errorf("помилка десеріалізації події: %w", err)
    }

    tx, err := p.db.BeginTx(ctx, nil)
    if err != nil {
        return err
    }
    defer tx.Rollback()

    // 1. Перевірка на повторну обробку події (Idempotency Key Check)
    var processed bool
    err = tx.QueryRowContext(ctx, 
        "SELECT EXISTS(SELECT 1 FROM processed_events WHERE event_id = $1)", 
        msg.EventID).Scan(&processed)
    if err != nil {
        return fmt.Errorf("помилка перевірки ідемпотентності: %w", err)
    }
    if processed {
        // Подія вже була оброблена раніше — мирно пропускаємо дублікат
        return nil 
    }

    // 2. Виконання компенсуючої операції: Повернення коштів на рахунок
    _, err = tx.ExecContext(ctx, 
        "UPDATE accounts SET balance = balance + $1 WHERE id = $2", 
        event.Amount, event.UserID)
    if err != nil {
        return fmt.Errorf("помилка повернення коштів: %w", err)
    }

    // 3. Реєстрація event_id у таблиці оброблених подій для майбутніх перевірок
    _, err = tx.ExecContext(ctx, 
        "INSERT INTO processed_events (event_id, processed_at) VALUES ($1, NOW())", 
        msg.EventID)
    if err != nil {
        return fmt.Errorf("помилка фіксації event_id: %w", err)
    }

    return tx.Commit()
}
```
```cpp
// C++20: Ідемпотентна обробка компенсуючого списання
#include <string>

class PaymentConsumer {
public:
    bool handleRefundCompensation(const std::string& event_id, const std::string& user_id, int64_t amount) {
        DatabaseTransaction tx(db_conn_);

        // 1. Перевірка таблиці прослуханих подій на дублікати
        if (isEventProcessed(tx, event_id)) {
            return true; // Пропускаємо дубльоване повідомлення z Kafka
        }

        // 2. Повернення балансу користувачу (компенсація)
        tx.execute("UPDATE accounts SET balance = balance + " + std::to_string(amount) +
                   " WHERE id = '" + user_id + "'");

        // 3. Збереження ідемпотентного ключа
        tx.execute("INSERT INTO processed_events (event_id) VALUES ('" + event_id + "')");

        tx.commit();
        return true;
    }
private:
    bool isEventProcessed(DatabaseTransaction& tx, const std::string& event_id) {
        // SQL запит до processed_events
        return false;
    }
    void* db_conn_{nullptr};
};
```
:::

---

## Глибокий порівняльний аналіз архітектурних режимів відмов

Порівнюючи два підходи, неможливо обмежитися лише підрахунком рядків коду. Справжня різниця полягає у **режимах відмов**, які з'являються при виході за межі одного процесу.

### 1. Каскад відмов та аномалії читання
У моноліті операція створення замовлення або виконується повністю, або залишає базу недоторканою. Система не може потрапити у стан, коли гроші спислися, а замовлення не створилося.

У Saga з Outbox протягом 500–2000 мілісекунд система знаходиться у **неконсистентному проміжному стані**. Поки подія іде через Kafka до сервісу складу, користувач може відкрити мобільний застосунок і побачити, що гроші спислися, але замовлення висить у статусі `PENDING`. Якщо на складі не виявилося позиції товару, запускається процес компенсації. Протягом наступних 1–2 секунд користувач спостерігає «завислі» гроші, які потім раптово повертаються на рахунок. Бізнес змушений проєктувати додаткові UI-стани та обробляти звернення у службу підтримки через подібні аномалії кінцевої узгодженості.

### 2. Складність інфраструктури та відлагодження
Для підтримки монолітної транзакції потрібна лише одна реляційна СУБД (PostgreSQL або MySQL). Відлагодження помилки полягає у читанні локального stack trace.

Для підтримки Saga + Outbox потрібні:
- Брокер повідомлень (Apache Kafka / RabbitMQ) у високодоступному кластерному режимі.
- Система Change Data Capture (Debezium / Kafka Connect) для вичитання Outbox-таблиць.
- Механізми Dead Letter Queue (DLQ) для обробки «отруйних» повідомлень, які викликають винятки під час десеріалізації.
- Робочі крон-жоби санітарного узгодження (Reconciliation Jobs), які раз на добу сканують бази даних усіх трьох сервісів і знаходять завислі Saga-транзакції, що не завершилися через аварійне падіння вузлів.

### 3. Зведена підсумкова порівняльна характеристика

| Критерій порівняння | Модульний моноліт (ACID) | Мікросервіси (Saga + Outbox) |
| :--- | :--- | :--- |
| **Кількість процесів і БД** | 1 процес, 1 PostgreSQL | 3+ сервіси, 3 БД, Kafka, Debezium, DLQ |
| **Обсяг коду бізнес-операції** | ~30–40 рядків чистої бізнес-логіки | ~350–600 рядків (Outbox, Handlers, Saga State Machine) |
| **Режими відмов** | 1 (помилка з'єднання з СУБД) | 8+ (мережевий розділ, втрата події, дублікат, збій компенсації) |
| **Час досягнення консистентності** | Строга мгновенна (2–5 мс) | Кінцева (Eventual Consistency, 500–3000 мс) |
| **Потреба у таблицях ідемпотентності** | Відсутня (СУБД робить Rollback) | **Обов'язкова** для кожної події та кожної компенсації |
| **Моніторинг та аналіз аварій** | Єдиний stack trace у лог-файлі | Distributed Tracing (OpenTelemetry), аналіз DLQ, санітарні скрипти |

Отже, застосування Saga та Transactional Outbox є виправданим і необхідним кроком лише тоді, коли розділення на окремі бази даних викличене непереборними організаційними або технічними вимогами. Використання цих розподілених патернів «про всяк випадок» у невеликих системах є фундаментальною архітектурною помилкою, яка збільшує складність коду й операційні витрати у десятки разів.
