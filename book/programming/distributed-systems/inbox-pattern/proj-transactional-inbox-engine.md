# ⚙️ Практична реалізація рушія Transactional Inbox

Рушій вхідної скриньки розв'язує задачу надійної обробки вхідних подій із гарантією дедуплікації: він атомарно поєднує перевірку унікальності ідентифікатора повідомлення, мутацію доменного стану та управління життєвим циклом обробки (лізи, повторні спроби й фіксація помилок).

Нижче наведено повнофункціональну реалізацію споживача з підтримкою транзакційної дедуплікації, блокувань ліз для конкурентних воркерів та обробки збоїв на C++20 та TypeScript.

## Повний вихідний код рушія

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <memory>
#include <optional>
#include <expected>
#include <mutex>
#include <unordered_map>
#include <format>

// Перелік станів повідомлення у вхідній скриньці
enum class InboxStatus {
    Received,
    Processing,
    Processed,
    Failed
};

// Структура вхідного повідомлення
struct InboxMessage {
    std::string message_id;
    std::string event_type;
    std::string payload;
    InboxStatus status{InboxStatus::Received};
    int retry_count{0};
    int max_retries{5};
    std::chrono::system_clock::time_point locked_until{};
    std::string locked_by{};
    std::chrono::system_clock::time_point created_at{std::chrono::system_clock::now()};
    std::optional<std::chrono::system_clock::time_point> processed_at{std::nullopt};
    std::optional<std::string> last_error{std::nullopt};
};

// Імітація транзакційного сховища (на практиці — PostgreSQL / SQLite)
class TransactionalDatabase {
public:
    struct AccountState {
        int64_t user_id;
        double balance;
    };

    // Початок транзакції
    class Transaction {
    public:
        Transaction(TransactionalDatabase& db) : db_(db), committed_(false) {
            db_.lock();
        }

        ~Transaction() {
            if (!committed_) {
                rollback();
            }
            db_.unlock();
        }

        // 1. Атомарне резервування або перевірка унікальності в inbox
        bool try_insert_or_acquire_inbox(const std::string& msg_id, 
                                         const std::string& event_type, 
                                         const std::string& payload,
                                         std::string_view worker_id,
                                         std::chrono::seconds lease_duration) {
            auto it = db_.inbox_table_.find(msg_id);
            auto now = std::chrono::system_clock::now();

            if (it == db_.inbox_table_.end()) {
                // Нове повідомлення — вставляємо одразу в стані Processing
                InboxMessage msg;
                msg.message_id = msg_id;
                msg.event_type = event_type;
                msg.payload = payload;
                msg.status = InboxStatus::Processing;
                msg.locked_until = now + lease_duration;
                msg.locked_by = std::string(worker_id);
                staged_inbox_inserts_[msg_id] = msg;
                return true;
            }

            // Повідомлення вже є
            if (it->second.status == InboxStatus::Processed) {
                // Уже успішно оброблено — дублікат відхиляється
                return false;
            }

            if (it->second.status == InboxStatus::Processing && it->second.locked_until > now) {
                // Обробляється іншим активним воркером
                return false;
            }

            // Повідомлення очікує або ліза попереднього воркера спливла
            InboxMessage updated = it->second;
            updated.status = InboxStatus::Processing;
            updated.locked_until = now + lease_duration;
            updated.locked_by = std::string(worker_id);
            staged_inbox_updates_[msg_id] = updated;
            return true;
        }

        // 2. Бізнес-операція: модифікація балансу
        void update_balance(int64_t user_id, double delta) {
            double current = db_.accounts_[user_id].balance;
            staged_balances_[user_id] = current + delta;
        }

        // 3. Успішне завершення обробки
        void mark_processed(const std::string& msg_id) {
            staged_processed_ids_.push_back(msg_id);
        }

        // 4. Фіксація помилки обробки
        void mark_failed(const std::string& msg_id, std::string_view error_msg) {
            staged_errors_[msg_id] = std::string(error_msg);
        }

        void commit() {
            // Застосовуємо всі підготовлені мутації
            for (auto& [id, msg] : staged_inbox_inserts_) {
                db_.inbox_table_[id] = msg;
            }
            for (auto& [id, msg] : staged_inbox_updates_) {
                db_.inbox_table_[id] = msg;
            }
            for (auto& [user_id, balance] : staged_balances_) {
                db_.accounts_[user_id] = {user_id, balance};
            }
            auto now = std::chrono::system_clock::now();
            for (const auto& id : staged_processed_ids_) {
                db_.inbox_table_[id].status = InboxStatus::Processed;
                db_.inbox_table_[id].processed_at = now;
                db_.inbox_table_[id].locked_by.clear();
            }
            for (auto& [id, err] : staged_errors_) {
                auto& msg = db_.inbox_table_[id];
                msg.retry_count++;
                msg.last_error = err;
                if (msg.retry_count >= msg.max_retries) {
                    msg.status = InboxStatus::Failed;
                } else {
                    msg.status = InboxStatus::Received; // повертаємо для повтору
                }
                msg.locked_by.clear();
            }
            committed_ = true;
        }

        void rollback() {
            staged_inbox_inserts_.clear();
            staged_inbox_updates_.clear();
            staged_balances_.clear();
            staged_processed_ids_.clear();
            staged_errors_.clear();
        }

    private:
        TransactionalDatabase& db_;
        bool committed_;
        std::unordered_map<std::string, InboxMessage> staged_inbox_inserts_;
        std::unordered_map<std::string, InboxMessage> staged_inbox_updates_;
        std::unordered_map<int64_t, double> staged_balances_;
        std::vector<std::string> staged_processed_ids_;
        std::unordered_map<std::string, std::string> staged_errors_;
    };

    std::unique_ptr<Transaction> begin_transaction() {
        return std::make_unique<Transaction>(*this);
    }

    double get_balance(int64_t user_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        return accounts_[user_id].balance;
    }

    bool is_processed(const std::string& msg_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = inbox_table_.find(msg_id);
        return it != inbox_table_.end() && it->second.status == InboxStatus::Processed;
    }

private:
    void lock() { mutex_.lock(); }
    void unlock() { mutex_.unlock(); }

    std::mutex mutex_;
    std::unordered_map<std::string, InboxMessage> inbox_table_;
    std::unordered_map<int64_t, AccountState> accounts_;
};

// Сервіс обробника вхідних повідомлень
class InboxConsumer {
public:
    InboxConsumer(TransactionalDatabase& db, std::string worker_id)
        : db_(db), worker_id_(std::move(worker_id)) {}

    // Обробка вхідного повідомлення з гарантією дедуплікації
    enum class ProcessOutcome {
        Success,
        DuplicateIgnored,
        TransientFailure,
        TerminalFailure
    };

    ProcessOutcome handle_payment_event(const std::string& msg_id, 
                                         int64_t user_id, 
                                         double amount) {
        auto tx = db_.begin_transaction();

        // 1. Атомарне захоплення повідомлення
        bool acquired = tx->try_insert_or_acquire_inbox(
            msg_id, "PaymentReceived", std::to_string(amount), worker_id_, std::chrono::seconds(30)
        );

        if (!acquired) {
            // Дубль або повідомлення зайняте іншим воркером
            return ProcessOutcome::DuplicateIgnored;
        }

        // 2. Виконання бізнес-логіки
        if (amount <= 0.0) {
            // Некоректні вхідні дані — термінальна помилка
            tx->mark_failed(msg_id, "Сума платежу повинна бути додатною");
            tx->commit();
            return ProcessOutcome::TerminalFailure;
        }

        try {
            // Зміна стану балансу
            tx->update_balance(user_id, amount);

            // 3. Позначення повідомлення обробленим у тій самій транзакції
            tx->mark_processed(msg_id);

            // 4. Фіксація транзакції
            tx->commit();
            return ProcessOutcome::Success;

        } catch (const std::exception& ex) {
            tx->rollback();
            
            // Відкриваємо окрему транзакцію для фіксації помилки
            auto err_tx = db_.begin_transaction();
            err_tx->mark_failed(msg_id, ex.what());
            err_tx->commit();
            return ProcessOutcome::TransientFailure;
        }
    }

private:
    TransactionalDatabase& db_;
    std::string worker_id_;
};

int main() {
    TransactionalDatabase db;
    InboxConsumer worker1(db, "worker-node-1");
    InboxConsumer worker2(db, "worker-node-2");

    int64_t user = 42;
    std::string msg1 = "evt-pay-1001";

    std::cout << "[Крок 1] Первинна обробка повідомлення " << msg1 << "\n";
    auto res1 = worker1.handle_payment_event(msg1, user, 250.0);
    std::cout << "Результат: " << (res1 == InboxConsumer::ProcessOutcome::Success ? "Успіх" : "Збій") << "\n";
    std::cout << "Поточний баланс: " << db.get_balance(user) << " грн\n\n";

    std::cout << "[Крок 2] Брокер повторно надсилає дублікат " << msg1 << "\n";
    auto res2 = worker2.handle_payment_event(msg1, user, 250.0);
    std::cout << "Результат: " << (res2 == InboxConsumer::ProcessOutcome::DuplicateIgnored ? "Дублікат безпечно проігноровано" : "Помилка") << "\n";
    std::cout << "Баланс після повтору (захищено від дубля): " << db.get_balance(user) << " грн\n";

    return 0;
}
```
```ts
import { Pool, PoolClient } from 'pg';

export interface InboxEvent {
    messageId: string;
    eventType: string;
    payload: Record<string, unknown>;
}

export class TransactionalInboxConsumer {
    private pool: Pool;
    private workerId: string;
    private leaseSeconds: number;

    constructor(pool: Pool, workerId: string, leaseSeconds = 30) {
        this.pool = pool;
        this.workerId = workerId;
        this.leaseSeconds = leaseSeconds;
    }

    /**
     * Атомарна обробка вхідного повідомлення з дедуплікацією
     */
    async consume(
        event: InboxEvent, 
        businessHandler: (client: PoolClient, payload: Record<string, unknown>) => Promise<void>
    ): Promise<'PROCESSED' | 'DUPLICATE' | 'FAILED'> {
        const client = await this.pool.connect();
        try {
            await client.query('BEGIN');

            // 1. Спроба вставити або перевірити ідентифікатор у таблиці inbox
            const insertQuery = `
                INSERT INTO inbox_messages (message_id, event_type, payload, status, locked_until, locked_by)
                VALUES ($1, $2, $3, 'PROCESSING', NOW() + ($4 || ' seconds')::INTERVAL, $5)
                ON CONFLICT (message_id) DO UPDATE
                SET status = 'PROCESSING',
                    locked_until = NOW() + ($4 || ' seconds')::INTERVAL,
                    locked_by = $5
                WHERE inbox_messages.status = 'RECEIVED'
                   OR (inbox_messages.status = 'PROCESSING' AND inbox_messages.locked_until < NOW())
                RETURNING status;
            `;

            const res = await client.query(insertQuery, [
                event.messageId,
                event.eventType,
                JSON.stringify(event.payload),
                this.leaseSeconds,
                this.workerId
            ]);

            if (res.rowCount === 0) {
                // Повідомлення вже оброблено ('PROCESSED') або активне в іншого воркера
                await client.query('ROLLBACK');
                return 'DUPLICATE';
            }

            // 2. Виконання бізнес-логіки в тій самій локальній транзакції
            await businessHandler(client, event.payload);

            // 3. Оновлення статусу повідомлення на PROCESSED
            const completeQuery = `
                UPDATE inbox_messages
                SET status = 'PROCESSED',
                    processed_at = NOW(),
                    locked_until = NULL,
                    locked_by = NULL
                WHERE message_id = $1;
            `;
            await client.query(completeQuery, [event.messageId]);

            // 4. Фіксація транзакції
            await client.query('COMMIT');
            return 'PROCESSED';

        } catch (error: any) {
            await client.query('ROLLBACK');

            // Окремо фіксуємо невдачу та збільшуємо лічильник спроб
            try {
                const failQuery = `
                    UPDATE inbox_messages
                    SET retry_count = retry_count + 1,
                        last_error = $2,
                        status = CASE WHEN retry_count + 1 >= max_retries THEN 'FAILED' ELSE 'RECEIVED' END,
                        locked_until = NULL,
                        locked_by = NULL
                    WHERE message_id = $1;
                `;
                await this.pool.query(failQuery, [event.messageId, error.message || String(error)]);
            } catch (loggingErr) {
                console.error('Не вдалося зберегти статус помилки в inbox:', loggingErr);
            }

            return 'FAILED';
        } finally {
            client.release();
        }
    }
}
```
:::

## Покроковий розбір архітектурних рішень

### 1. Неподільність блокування та мутації бізнес-даних

Ключовий інваріант обох реалізацій полягає в тому, що перевірка унікальності ключа `message_id` та зміна стану доменних сутностей (балансу користувача чи створення замовлення) відбуваються в межах одного нерозривного транзакційного блоку (`BEGIN ... COMMIT`).

У реалізації на C++20 клас `TransactionalDatabase::Transaction` застосовує патерн RAII (Resource Acquisition Is Initialization): деструктор транзакції гарантує автоматичний виклик `rollback()` та зняття м'ютекса, якщо транзакція завершилася винятком або аварійним виходом до виклику `commit()`. Завдяки цьому проміжний стан ніколи не витікає в базу даних, а пам'ять залишається захищеною від витоків ресурсів.

У реалізації на TypeScript на базі `pg.PoolClient` клієнтське з'єднання обов'язково повертається до пулу у блоці `finally`, а при виникненні будь-якої помилки виконується команда `ROLLBACK`, що повертає стан бази даних до початкової точки до початку виклику бізнес-обробника.

### 2. Розподілені часові лізи (Leases) замість вічних блокувань

Коли обробка завдання вимагає значного часу, виникає ризик аварії процесу-споживача посеред роботи (наприклад, зупинка контейнера в Kubernetes через переповнення пам'яті OOMKilled або перезапуск хоста).

Якщо зафіксувати повідомлення у стані `PROCESSING` без часового обмеження, воно зависне назавжди, оскільки ніхто більше не візьметься за його обробку.

Для усунення цієї вразливості впроваджено концепцію розподіленої лізи через поле `locked_until`:

- При захопленні завдання воркер записує час завершення лізи: `locked_until = NOW() + 30s`.
- Запит вибірки у TypeScript-реалізації використовує атомарне оновлення з умовою:
  ```sql
  WHERE status = 'RECEIVED' OR (status = 'PROCESSING' AND locked_until < NOW())
  ```
- Якщо воркер успішно завершує транзакцію, статус змінюється на `PROCESSED`, а ліза знімається (`locked_until = NULL`).
- Якщо ж воркер гине, через 30 секунд будь-який інший паралельний воркер отримує легітимне право перехопити це повідомлення та виконати його повторно.

### 3. Ізоляція реєстрації збоїв та захист від «отруйних» повідомлень

Якщо бізнес-обробник стикається з винятком (наприклад, некоректні дані або тимчасова недоступність внутрішньої підсистеми), основна транзакція негайно відкочується (`ROLLBACK`), щоб не залишити часткових змін у доменних таблицях.

Проте сам факт невдачі повинен бути зафіксований, інакше система втратить лічильник спроб `retry_count`. Для цього відкривається коротка ізольована транзакція:

```
[Помилка в бізнес-коді]
          │
          ▼
   1. ROLLBACK основної транзакції (баланс НЕ змінено)
          │
          ▼
   2. BEGIN окремої службової транзакції
          │
          ▼
   3. UPDATE inbox SET retry_count = retry_count + 1, last_error = ...
          │
          ▼
   4. Якщо retry_count >= max_retries ──► status = 'FAILED' (Dead Letter)
      Інакше ───────────────────────────► status = 'RECEIVED' (Backoff)
          │
          ▼
   5. COMMIT службової транзакції
```

Такий підхід надійно захищає систему від нескінченних циклів падіння та автоматично відправляє безнадійні повідомлення на ручний аналіз інженерам підтримки.

## Взаємодія з брокерами повідомлень (Kafka, RabbitMQ, SQS)

Для повної надійності інтеграції програмний рушій вхідної скриньки повинен правильно узгоджувати власні транзакції з транспортним протоколом черги:

1. **Apache Kafka:**
   - Автоматичний комміт зміщень (`enable.auto.commit = true`) повинен бути **суворо вимкнений**.
   - Споживач викликає синхронний або асинхронний метод фіксації зміщення `consumer.commitSync()` або `commitAsync()` **виключно після успішного виконання `tx.commit()`**.
   - Якщо під час обробки виникає помилка, зміщення не фіксується, і повідомлення буде перечитане після перебалансування групи (Rebalance).
2. **RabbitMQ (AMQP):**
   - Увімкнено ручний режим підтвердження (`autoAck: false`, `no_ack = False`).
   - Після успішного завершення транзакції споживач викликає `channel.ack(deliveryTag)`.
   - При виникненні помилки або отриманні результату `DUPLICATE` викликається `channel.basicAck`, якщо дублікат уже безпечно зафіксований у базі, або `channel.basicNack(deliveryTag, requeue = false)` при фатальному збої.
3. **AWS SQS:**
   - Повідомлення отримується з черги з встановленням тайм-ауту видимості (`VisibilityTimeout`), який має перевищувати час дії лізи `locked_until`.
   - Після коміту транзакції споживач викликає `sqs.deleteMessage()`.

## Наскрізне трасування та контекст OpenTelemetry

У розподілених сервісах вкрай важливо зберігати наскрізний контекст трасування (Distributed Tracing) між відправником події, чергою повідомлень та вхідною скринькою:

1. **Витягнення заголовків (Trace Context Extraction):** Споживач зчитує метадані повідомлення (заголовки `traceparent` та `tracestate` стандарту W3C TraceContext).
2. **Створення локального спана:** Вхідна скринька створює дочірній спан `inbox.process_message`, зв'язуючи його з батьківським трейсом відправника.
3. **Атрибути спана:** До спана додаються атрибути `messaging.message_id`, `messaging.destination`, `inbox.status` та `inbox.retry_count`.
4. **Фіксація колізій:** Якщо повідомлення визнано дублікатом, у спан записується подія `inbox.duplicate_dropped`, що дозволяє в системі моніторингу (Jaeger / Tempo) чітко бачити, скільки разів брокер намагався повторити операцію.

## Методика тестування надійності та хаос-інженерія

Перевірка коректності роботи Transactional Inbox вимагає обов'язкового проведення спеціалізованих тестів на відмовостійкість:

- **Тест повторної доставки (Redelivery Test):** Емуляція надсилання ідентичного повідомлення 100 разів поспіль із 10 паралельних потоків. Очікуваний результат: рівно одна транзакція фіксується успішно, 99 спроб повертають `DuplicateIgnored`, баланс рахунку змінюється рівно один раз.
- **Тест обриву живлення (Crash-before-ACK Test):** Примусове завершення процесу споживача через виклик `_exit(1)` або `process.kill('SIGKILL')` безпосередньо після виконання `COMMIT` бази даних, але до виклику `ACK` брокера. Після перезапуску процесу брокер пересилає повідомлення, споживач відхиляє його як дублікат і надсилає коректний `ACK`.
- **Тест завислого воркера (Lease Timeout Test):** Штучне введення воркера в нескінченний сон `sleep(60)` під час обробки повідомлення у стані `PROCESSING`. Очікуваний результат: через 30 секунд сусідній воркер перехоплює прострочену лізу, успішно завершує завдання та переводить статус у `PROCESSED`.
- **Тест вичерпання пулу з'єднань (Connection Exhaustion Test):** Симуляція ситуації, коли всі з'єднання до СУБД зайняті. Рушій повинен коректно відхиляти нові повідомлення з поверненням брокеру сигналу NACK без втрати даних та без підтвердження необроблених пакетів.
