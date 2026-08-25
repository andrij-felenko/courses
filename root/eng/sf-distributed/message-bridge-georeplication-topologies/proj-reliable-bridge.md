# ⚙️ Розробка надійного асинхронного моста повідомлень: подвійне підтвердження, запобігання петлям та дисковий буфер

У розподілених корпоративних системах та периферійних IoT-контурах міст повідомлень виконує роль критичного ретранслятора між ізольованими брокерами. Він функціонує на стику двох різних середовищ передачі: з одного боку виступає як повноцінний споживач (Consumer), а з іншого — як надійний видавець (Producer). Створення промислового моста вимагає вирішення комплексу складних інженерних задач, пов'язаних із відсутністю спільної пам'яті, несиметричними мережевими затримками між дата-центрами та ризиком нескінченного циклічного зациклення трафіку.

```
+---------------------------------------------------------------------------------------+
|                                  MESSAGE BRIDGE PIPELINE                              |
|                                                                                       |
|  [Source Broker]                                                     [Target Broker]  |
|         │                                                                   ▲         |
|         │ 1. Poll / Fetch (Unacked)                                         │         |
|         ▼                                                                   │         |
|  +---------------+      +-------------------+      +---------------------+  │         |
|  | Ingress Queue | ---> | Loop Detection &  | ---> | Bounded FIFO Buffer |  │         |
|  | Consumer      |      | Envelope Adapt    |      | (Backpressure Lock) |  │         |
|  +---------------+      +-------------------+      +---------------------+  │         |
|                                                               │             │         |
|                                                               │ 2. Produce  │         |
|                                                               ▼             │         |
|  +---------------+                                 +---------------------+  │         |
|  | Commit Source | <--- 4. Confirm OK (Dual Ack) ─ | Target Dispatcher   | ─┘         |
|  | Ack / Offset  |                                 | (Wait Target Ack 3.)|            |
|  +---------------+                                 +---------------------+            |
+---------------------------------------------------------------------------------------+
```

## Інженерні вимоги та виклики розробки моста

Під час проектування моста між двома незалежними кластерами виникають чотири фундаментальні обмеження, які неможливо вирішити стандартними бібліотеками передачі даних без побудови спеціалізованого конвеєра:

1. **Відсутність розподіленої транзакційності (No 2PC across Heterogeneous Brokers):**
   Вихідний і цільовий брокери не підтримують спільний координатор розподілених транзакцій (Two-Phase Commit). Якщо вихідний брокер працює за протоколом MQTT або RabbitMQ, а цільовий — за протоколом Apache Kafka, об'єднати читання з одного брокера та запис в інший в одну неподільну атомарну транзакцію на рівні сховищ неможливо. Єдиним життєздатним механізмом забезпечення надійності є протокол **подвійного підтвердження** (Dual Acknowledgment): повідомлення позначається обробленим у вихідному брокері лише тоді, коли від цільового брокера отримано підтвердження збереження (Write Acknowledgment).

2. **Захист від нескінченних петель і лавиноподібного шторму (Echo Loop Storms):**
   У двоспрямованих топологіях типу Active-Active або в кільцевих топологіях із кількома дата-центрами повідомлення, опубліковане в кластері `EU`, передається мостом до кластера `US`. Якщо кластер `US` має власний зворотний міст до кластера `EU`, повідомлення буде повторно прочитане й надіслане назад у вихідний топік. Без механізму векторного відстеження шляху повідомлення почне циркулювати нескінченно, експоненціально множачись і за лічені хвилини переповнюючи диски та канали зв'язку обох дата-центрів.

3. **Керування пам'яттю та наскрізний протитиск (Backpressure Management):**
   Якщо цільовий брокер тимчасово сповільнює обробку через дискове перевантаження (Disk I/O Choke) або глобальний канал WAN втрачає пропускну здатність, швидкість вичитування з локального джерела значно перевищуватиме швидкість відправки на ціль. Якщо міст накопичуватиме всі зчитані повідомлення в оперативній пам'яті без обмеження, процес неминуче впаде через вичерпання пам'яті (Out-Of-Memory Killer). Міст повинен мати обмежений буфер і передавати протитиск назад: при заповненні буфера потік споживача блокується, змушуючи вихідний брокер накопичувати повідомлення у своєму власному персистентному сховищі.

4. **Коректне плавне вимкнення (Graceful Drain & Shutdown):**
   Під час зупинки процесу для оновлення міст зобов'язаний коректно завершити обробку. Не можна просто розірвати процес: пакети, які вже надіслані в цільовий брокер, але ще не підтверджені у джерелі, або пакети у внутрішньому буфері мають бути або повністю доставлені та зафіксовані, або повернені у вихідну чергу.

## Архітектура автомата станів та структура даних

Конвеєр моста організовано навколо скінченного автомата станів кожного повідомлення:

```
[INGRESS_FETCH]
       │  (Отримання пакета з черги джерела)
       ▼
[LOOP_DETECTION_CHECK] ──(Петля виявлена)──► [DROP_AND_COMMIT_SOURCE]
       │
       │  (Пакет валідний: додаємо цільовий Cluster-ID у Hop-вектор)
       ▼
[BUFFER_PUSH_WAIT] ──(Буфер повний)──► [BACKPRESSURE_BLOCK_CONSUMER]
       │
       ▼
[IN_FLIGHT_DISPATCH]
       │  (Відправка в сокет цільового брокера)
       ▼
[WAIT_TARGET_ACK] ──(Таймаут або збій)──► [RETRY_WITH_EXPONENTIAL_BACKOFF]
       │
       │  (Ціль підтвердила запис на диск)
       ▼
[SOURCE_COMMIT_OFFSET]
       │  (Фіксація на джерелі: цикл завершено успішно)
       ▼
    [DONE]
```

### Структура метаданих та конверта повідомлення

Для забезпечення прозорої ретрансляції та контролю циклів кожне повідомлення огортається у службовий конверт (Bridge Message Envelope), який містить:
* `msg_id` — глобальний унікальний ідентифікатор повідомлення або UUID.
* `source_offset` — порядковий номер або зміщення у вихідному журналі чи черзі.
* `origin_cluster_id` — числовий ідентифікатор кластера первинної генерації події.
* `hop_path` — упорядкований масив ідентифікаторів вузлів та мостів, які ретранслювали даний пакет.
* `payload` — незмінний масив корисного навантаження (JSON, Protobuf, Avro).

## Збереження порядку та стратегії мапінгу партицій

Коли міст з'єднує чергу «точка-точка» (наприклад, чергу RabbitMQ) із розподіленим журналом (наприклад, топіком Kafka на 64 партиції), виникає критична проблема збереження порядку бізнес-подій.

Якщо міст випадковим чином розподіляє повідомлення по партиціях Kafka (Round-Robin), події, що стосуються одного банківського рахунку чи одного замовлення (`OrderCreated`, `PaymentReceived`, `OrderShipped`), опиняться в різних партиціях і будуть оброблені паралельними споживачами у довільному порядку, що спричинить порушення бізнес-інваріантів.

Для усунення цієї проблеми міст застосовує детерміноване хешування бізнес-ключа:
1. Міст витягує бізнес-ідентифікатор сутності з корисного навантаження або службового заголовка (`routing_key` або `entity_id`).
2. Номер цільової партиції розраховується за формулою:
```
target_partition = murmur3_hash(entity_id) % num_target_partitions
```
3. Усі події з однаковим `entity_id` гарантовано потрапляють в одну й ту саму партицію цільового логу, зберігаючи суворий монотонний порядок доставки.

## Дисковий буфер скидання (Disk Spooling) при тривалих обривах зв'язку

Якщо зв'язок із цільовим дата-центром зникає на кілька годин (наприклад, внаслідок пошкодження магістрального оптоволоконного кабелю чи аварії хмарного провайдера), зупинки читання через протитиск може виявитися недостатньо. Якщо вихідний брокер — це легкий периферійний MQTT-сервер на шлюзі з обмеженою SD-картою, його локальна черга швидко переповниться, змушуючи брокер відкидати нові телеметричні пакети.

Для таких сценаріїв промислові мости застосовують дворівневу буферизацію:
* **Оперативний буфер першого рівня (L1 RAM Buffer):** Кільцева черга в оперативній пам'яті фіксованого розміру (наприклад, 10 000 повідомлень) для згладжування мікросплесків затримки.
* **Персистентний буфер другого рівня (L2 Disk Spooler):** При заповненні L1 або при розриві TCP-сесії з цільовим брокером понад 5 секунд міст перемикає запис на локальне вбудоване сховище типу RocksDB, SQLite або файл циклічного логу (Write-Ahead Log, WAL).
* **Відновлення зв'язку (Drain Mode):** Після відновлення з'єднання з цільовим брокером фоновий потік вичитує накопичені на диску пакети з контролем швидкості (Throttling), щоб не перевантажити цільовий кластер, після чого міст повертається до прямої ретрансляції з оперативної пам'яті.

## Еволюція схем і трансляція заголовків крізь міст

У гетерогенних середовищах вихідний брокер та цільові споживачі часто використовують різні формати серіалізації даних або різні версії реєстрів схем (Schema Registry). Наприклад, сервіси на джерелі публікують події у форматі Apache Avro з ідентифікатором схеми `schema_id = 42`, зареєстрованим у локальному реєстрі кластера `EU`.

Якщо передати ці байти безпосередньо в кластер `US`, американські споживачі не зможуть десеріалізувати пакет, оскільки в їхньому локальному реєстрі схема під номером 42 або відсутня, або відповідає зовсім іншому типу даних.

Для вирішення цієї проблеми міст інтегрує адаптер трансляції схем:
1. **Реплікація реєстру схем (Schema Sync):** Спеціалізований фоновий потік синхронізує визначення схем між реєстрами кластерів, реєструючи відсутні структури та створюючи таблицю трансляції числових ідентифікаторів `EU_Schema_ID <-> US_Schema_ID`.
2. **Переписування магічного байта:** Міст зчитує 5-байтовий заголовок Confluent Wire Format (1 магічний байт + 4 байти `schema_id`), замінює ідентифікатор вихідної схеми на відповідний номер у цільовому реєстрі та передає тіло повідомлення без повної повторної десеріалізації.
3. **Трансляція заголовків трасування:** Службові метадані відкритого трасування W3C TraceContext (`traceparent`, `tracestate`) автоматично копіюються з AMQP-властивостей у Kafka Record Headers, зберігаючи наскрізну видимість запиту крізь брокери.

## Пакетування та оптимізація пропускної здатності

При передачі сотень тисяч дрібних телеметричних подій щосекунди надсилання кожного повідомлення окремим TCP-пакетом породжує колосальний накладний оверхед на системні виклики ядра `write()` та заголовки мережевих пакетів.

Промисловий міст застосовує алгоритм коалесценції (Micro-Batching):
* **Таймер очікування пачки (`linger_ms`):** Потік відправника очікує накопичення повідомлень у буфері протягом 5–20 мілісекунд.
* **Поріг розміру пачки (`batch_size_bytes`):** Якщо сумарний обсяг корисного навантаження досягає 64–256 КБ раніше спливання таймера, пачка негайно відправляється в мережу.
* **Стиснення на льоту:** Уся пачка стискається алгоритмами LZ4 або Zstandard безпосередньо в пам'яті моста перед відправкою, зменшуючи використання пропускної здатності глобального каналу WAN у 3–5 разів.
* **Групова фіксація зміщень (Coalesced Commit):** Після того як цільовий брокер підтверджує прийом усієї стисненої пачки, міст викликає єдину операцію `commit_offset(max_batch_offset)` на джерелі, знижуючи навантаження на базу метаданих джерела в тисячі разів.

## Інтеграція з патерном Transactional Outbox

Окремим різновидом моста повідомлень є міст на основі фіксації змін даних (Change Data Capture, CDC). У мікросервісній архітектурі бізнес-сервіс записує зміни сутності (наприклад, створення замовлення) у власну базу даних PostgreSQL та одночасно вставляє запис у спеціальну таблицю `outbox` у межах однієї локальної ACID-транзакції.

Міст повідомлень виступає як зовнішній агент, який підключається до слота логічної реплікації PostgreSQL (Logical Decoding via `pgoutput`), безперервно читає бінарний потік журналу транзакцій (Write-Ahead Log, WAL) та ретранслює події з таблиці `outbox` у цільовий топік Kafka.

Переваги CDC-моста перед ручною відправкою з коду:
* **Гарантована атомарність:** Стан бази даних і відправка події не можуть розійтися, навіть якщо процес прикладного сервісу зазнає аварії в момент запису.
* **Мінімальне навантаження на БД:** Міст не виконує періодичні SQL-запити `SELECT ... FROM outbox WHERE processed = false`, які спричиняють блокування рядків і навантажують пул з'єднань, а читає послідовний бінарний потік логу змін.
* **Точний порядок:** Події публікуються в цільовий брокер у точному порядку їхньої фіксації в транзакційному журналі СУБД.

## Стратегії дедуплікації на боці споживачів

Оскільки міст повідомлень забезпечує семантику At-Least-Once через протокол подвійного підтвердження, у разі аварії моста після запису в ціль, але до фіксації на джерелі, певна кількість повідомлень буде надіслана в цільовий брокер повторно.

Для запобігання повторному виконанню бізнес-операцій цільові споживачі застосовують стратегії [ідемпотентної обробки](topic:sf-distributed/idempotency):
1. **Збереження стану оброблених ідентифікаторів:** Споживач підтримує ковзне вікно оброблених `msg_id` (або `origin_cluster_id + source_offset`) у швидкому сховищі в пам'яті (наприклад, Redis із TTL у 24 години) або у фільтрі Блума (Bloom Filter).
2. **Унікальні обмеження бази даних (Database Unique Constraints):** Споживач записує `msg_id` в окрему таблицю `processed_messages` або використовує унікальний ключ у цільовій таблиці сутностей (`INSERT ... ON CONFLICT DO NOTHING`).
3. **Ідемпотентні бізнес-мутації:** Оновлення стану проектуються як операції заміни (`SET status = 'PAID' WHERE id = 101 AND status = 'NEW'`), що є безпечними до багаторазового виконання.

## Реалізація ядра моста мовами C++ та C

Нижче наведено дві повнофункціональні реалізації ядра асинхронного моста повідомлень: ідіоматичний багатопотоковий конвеєр мовою сучасного C++ (із застосуванням стандартних м'ютексів, умовних змінних, безпеки винятків та RAII) та низькорівнева високопродуктивна реалізація мовою C стандарту POSIX.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <deque>
#include <unordered_set>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <memory>
#include <atomic>
#include <optional>
#include <sstream>

// ── 1. Структура метаданих та конверта повідомлення ──────────────────────────
struct BridgeMessage {
    uint64_t msg_id{0};
    uint64_t source_offset{0};
    uint32_t origin_cluster_id{0};
    std::vector<uint32_t> hop_path;
    std::string payload;

    [[nodiscard]] std::string format_hops() const {
        std::ostringstream oss;
        oss << "[";
        for (size_t i = 0; i < hop_path.size(); ++i) {
            if (i > 0) oss << " -> ";
            oss << "0x" << std::hex << hop_path[i] << std::dec;
        }
        oss << "]";
        return oss.str();
    }
};

// ── 2. Потокобезпечний буфер з обмеженою ємністю та протитиском ──────────────
class BoundedBridgeQueue {
public:
    explicit BoundedBridgeQueue(size_t max_capacity)
        : max_capacity_(max_capacity), is_shutdown_(false) {}

    // Додавання повідомлення: блокує споживача при заповненні буфера (протитиск)
    bool push(BridgeMessage msg, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        bool space_available = not_full_cv_.wait_for(lock, timeout, [this]() {
            return queue_.size() < max_capacity_ || is_shutdown_;
        });

        if (is_shutdown_ || !space_available) {
            return false;
        }

        queue_.push_back(std::move(msg));
        not_empty_cv_.notify_one();
        return true;
    }

    // Витягування повідомлення для відправки в цільовий брокер
    std::optional<BridgeMessage> pop(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        bool item_available = not_empty_cv_.wait_for(lock, timeout, [this]() {
            return !queue_.empty() || is_shutdown_;
        });

        if (queue_.empty()) {
            return std::nullopt;
        }

        BridgeMessage msg = std::move(queue_.front());
        queue_.pop_front();
        not_full_cv_.notify_one();
        return msg;
    }

    void shutdown() {
        std::unique_lock<std::mutex> lock(mutex_);
        is_shutdown_ = true;
        not_empty_cv_.notify_all();
        not_full_cv_.notify_all();
    }

    [[nodiscard]] size_t size() const {
        std::unique_lock<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t max_capacity_;
    std::deque<BridgeMessage> queue_;
    mutable std::mutex mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable not_full_cv_;
    bool is_shutdown_;
};

// ── 3. Моделювання зовнішніх брокерів (Джерело та Ціль) ─────────────────────
class MockSourceBroker {
public:
    explicit MockSourceBroker(uint32_t cluster_id) : cluster_id_(cluster_id), current_offset_(0) {}

    std::optional<BridgeMessage> fetch_next() {
        if (current_offset_ >= 6) {
            return std::nullopt; // Кінець тестового потоку
        }

        BridgeMessage msg;
        msg.msg_id = 1000 + current_offset_;
        msg.source_offset = current_offset_++;
        
        // Симуляція відлуння (повідомлення 3 прийшло з цільового кластера 0x02)
        if (msg.source_offset == 3) {
            msg.origin_cluster_id = 0x02;
            msg.hop_path = {0x02, cluster_id_};
            msg.payload = "{\"event\":\"order_echo_test\",\"id\":404}";
        } else {
            msg.origin_cluster_id = cluster_id_;
            msg.hop_path = {cluster_id_};
            msg.payload = "{\"event\":\"order_created\",\"amount\":" + std::to_string(msg.source_offset * 150) + "}";
        }

        return msg;
    }

    void commit_offset(uint64_t offset) {
        std::lock_guard<std::mutex> lock(commit_mutex_);
        last_committed_offset_ = offset;
        std::cout << "  [Джерело 0x" << std::hex << cluster_id_ << std::dec 
                  << "] Офсет " << offset << " успішно ЗАФІКСОВАНО (Source Ack)\n";
    }

    [[nodiscard]] uint64_t get_committed_offset() const {
        std::lock_guard<std::mutex> lock(commit_mutex_);
        return last_committed_offset_;
    }

private:
    uint32_t cluster_id_;
    uint64_t current_offset_;
    uint64_t last_committed_offset_{0};
    mutable std::mutex commit_mutex_;
};

class MockTargetBroker {
public:
    explicit MockTargetBroker(uint32_t cluster_id) : cluster_id_(cluster_id) {}

    // Запис повідомлення в цільовий лог
    bool produce(const BridgeMessage& msg) {
        // Симуляція мережевої затримки запису на диск / реплікації
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        std::cout << "  [Ціль 0x" << std::hex << cluster_id_ << std::dec 
                  << "] Записано msg_id=" << msg.msg_id 
                  << " (Hops: " << msg.format_hops() << ")\n";
        return true;
    }

private:
    uint32_t cluster_id_;
};

// ── 4. Ядро моста повідомлень (Message Bridge Core) ──────────────────────────
class MessageBridge {
public:
    MessageBridge(uint32_t bridge_id, uint32_t target_cluster_id,
                  MockSourceBroker& source, MockTargetBroker& target, size_t buffer_size)
        : bridge_id_(bridge_id),
          target_cluster_id_(target_cluster_id),
          source_broker_(source),
          target_broker_(target),
          queue_(buffer_size),
          running_(false),
          forwarded_count_(0),
          dropped_loops_count_(0) {}

    ~MessageBridge() {
        stop();
    }

    void start() {
        running_ = true;
        consumer_thread_ = std::thread(&MessageBridge::consume_worker, this);
        dispatcher_thread_ = std::thread(&MessageBridge::dispatch_worker, this);
    }

    void stop() {
        if (!running_.exchange(false)) return;

        queue_.shutdown();
        if (consumer_thread_.joinable()) consumer_thread_.join();
        if (dispatcher_thread_.joinable()) dispatcher_thread_.join();
    }

    [[nodiscard]] size_t get_forwarded_count() const { return forwarded_count_.load(); }
    [[nodiscard]] size_t get_dropped_loops_count() const { return dropped_loops_count_.load(); }

private:
    void consume_worker() {
        while (running_) {
            auto msg_opt = source_broker_.fetch_next();
            if (!msg_opt) {
                // Джерело тимчасово порожнє
                std::this_thread::sleep_for(std::chrono::milliseconds(30));
                break; // У тестовому сценарії завершуємо після вичитки
            }

            BridgeMessage msg = std::move(*msg_opt);

            // Крок А: Перевірка на циклічну петлю (Loop Detection)
            if (detect_cycle(msg)) {
                std::cout << "  [Міст] ⚠️ ВИЯВЛЕНО ПЕТЛЮ у msg_id=" << msg.msg_id 
                          << " (Шлях: " << msg.format_hops() << ") -> ВІДКИДАННЯ\n";
                // Фіксуємо офсет у джерелі, щоб не зависати на відкинутому повідомленні
                source_broker_.commit_offset(msg.source_offset);
                dropped_loops_count_++;
                continue;
            }

            // Крок Б: Додаємо цільовий кластер у шлях передачі
            msg.hop_path.push_back(target_cluster_id_);

            // Крок В: Запис у внутрішній буфер (із протитиском)
            while (running_) {
                if (queue_.push(std::move(msg), std::chrono::milliseconds(50))) {
                    break;
                }
            }
        }
    }

    void dispatch_worker() {
        while (running_ || queue_.size() > 0) {
            auto msg_opt = queue_.pop(std::chrono::milliseconds(50));
            if (!msg_opt) {
                if (!running_) break;
                continue;
            }

            const BridgeMessage& msg = *msg_opt;

            // Крок Г: Відправка в цільовий брокер
            bool write_ok = target_broker_.produce(msg);

            // Крок Ґ: Подвійне підтвердження (Dual Ack)
            if (write_ok) {
                // Лише після успішного підтвердження від цілі фіксуємо офсет на джерелі
                source_broker_.commit_offset(msg.source_offset);
                forwarded_count_++;
            } else {
                std::cerr << "  [Міст] ✗ Помилка запису в ціль msg_id=" << msg.msg_id << "\n";
            }
        }
    }

    [[nodiscard]] bool detect_cycle(const BridgeMessage& msg) const {
        for (uint32_t hop : msg.hop_path) {
            if (hop == target_cluster_id_) {
                return true; // Цільовий кластер уже бачив це повідомлення
            }
        }
        return false;
    }

    uint32_t bridge_id_;
    uint32_t target_cluster_id_;
    MockSourceBroker& source_broker_;
    MockTargetBroker& target_broker_;
    BoundedBridgeQueue queue_;
    std::atomic<bool> running_;
    std::thread consumer_thread_;
    std::thread dispatcher_thread_;
    std::atomic<size_t> forwarded_count_;
    std::atomic<size_t> dropped_loops_count_;
};

// ── 5. Демонстраційний сценарій роботи моста ─────────────────────────────────
int main() {
    std::cout << "=== ЗАПУСК МОСТА ПОВІДОМЛЕНЬ (C++20 Pipeline) ===\n";
    const uint32_t CLUSTER_EU = 0x01;
    const uint32_t CLUSTER_US = 0x02;

    MockSourceBroker source_eu(CLUSTER_EU);
    MockTargetBroker target_us(CLUSTER_US);

    {
        MessageBridge bridge(101, CLUSTER_US, source_eu, target_us, 500);
        bridge.start();

        // Очікуємо обробки всіх повідомлень конвеєром
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
        bridge.stop();

        std::cout << "\n=== ПІДСУМОК РОБОТИ МОСТА ===\n";
        std::cout << "Успішно ретрансльовано: " << bridge.get_forwarded_count() << " повідомлень\n";
        std::cout << "Відсіяно циклічних петель: " << bridge.get_dropped_loops_count() << "\n";
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_HOPS 16
#define PAYLOAD_SIZE 128
#define QUEUE_CAPACITY 64

// ── 1. Структура конверта повідомлення моста ─────────────────────────────────
typedef struct {
    uint64_t msg_id;
    uint64_t source_offset;
    uint32_t origin_cluster_id;
    uint32_t hop_path[MAX_HOPS];
    size_t hop_count;
    char payload[PAYLOAD_SIZE];
} BridgeMessage;

// ── 2. Обмежена потокобезпечна черга (POSIX Mutex & Cond) ────────────────────
typedef struct {
    BridgeMessage items[QUEUE_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    bool is_shutdown;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty_cv;
    pthread_cond_t not_full_cv;
} BoundedQueue;

static void queue_init(BoundedQueue *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->is_shutdown = false;
    pthread_mutex_init(&q->mutex, NULL);
    pthread_cond_init(&q->not_empty_cv, NULL);
    pthread_cond_init(&q->not_full_cv, NULL);
}

static void queue_destroy(BoundedQueue *q) {
    pthread_mutex_destroy(&q->mutex);
    pthread_cond_destroy(&q->not_empty_cv);
    pthread_cond_destroy(&q->not_full_cv);
}

static bool queue_push(BoundedQueue *q, const BridgeMessage *msg) {
    pthread_mutex_lock(&q->mutex);
    while (q->count == QUEUE_CAPACITY && !q->is_shutdown) {
        pthread_cond_wait(&q->not_full_cv, &q->mutex);
    }

    if (q->is_shutdown) {
        pthread_mutex_unlock(&q->mutex);
        return false;
    }

    q->items[q->tail] = *msg;
    q->tail = (q->tail + 1) % QUEUE_CAPACITY;
    q->count++;

    pthread_cond_signal(&q->not_empty_cv);
    pthread_mutex_unlock(&q->mutex);
    return true;
}

static bool queue_pop(BoundedQueue *q, BridgeMessage *out_msg) {
    pthread_mutex_lock(&q->mutex);
    while (q->count == 0 && !q->is_shutdown) {
        pthread_cond_wait(&q->not_empty_cv, &q->mutex);
    }

    if (q->count == 0 && q->is_shutdown) {
        pthread_mutex_unlock(&q->mutex);
        return false;
    }

    *out_msg = q->items[q->head];
    q->head = (q->head + 1) % QUEUE_CAPACITY;
    q->count--;

    pthread_cond_signal(&q->not_full_cv);
    pthread_mutex_unlock(&q->mutex);
    return true;
}

static void queue_shutdown(BoundedQueue *q) {
    pthread_mutex_lock(&q->mutex);
    q->is_shutdown = true;
    pthread_cond_broadcast(&q->not_empty_cv);
    pthread_cond_broadcast(&q->not_full_cv);
    pthread_mutex_unlock(&q->mutex);
}

// ── 3. Моделювання брокерів та контексту моста ──────────────────────────────
typedef struct {
    uint32_t bridge_id;
    uint32_t source_cluster_id;
    uint32_t target_cluster_id;
    BoundedQueue queue;
    bool running;
    size_t forwarded_count;
    size_t dropped_loops_count;
} BridgeContext;

static bool detect_cycle(const BridgeMessage *msg, uint32_t target_id) {
    for (size_t i = 0; i < msg->hop_count; ++i) {
        if (msg->hop_path[i] == target_id) {
            return true;
        }
    }
    return false;
}

static void* consumer_thread_func(void *arg) {
    BridgeContext *ctx = (BridgeContext*)arg;
    for (uint64_t offset = 0; offset < 6; ++offset) {
        BridgeMessage msg;
        memset(&msg, 0, sizeof(msg));
        msg.msg_id = 1000 + offset;
        msg.source_offset = offset;

        // Тестова петля на повідомленні 3
        if (offset == 3) {
            msg.origin_cluster_id = ctx->target_cluster_id;
            msg.hop_path[0] = ctx->target_cluster_id;
            msg.hop_path[1] = ctx->source_cluster_id;
            msg.hop_count = 2;
            snprintf(msg.payload, sizeof(msg.payload), "{\"event\":\"echo_test\",\"id\":%lu}", (unsigned long)offset);
        } else {
            msg.origin_cluster_id = ctx->source_cluster_id;
            msg.hop_path[0] = ctx->source_cluster_id;
            msg.hop_count = 1;
            snprintf(msg.payload, sizeof(msg.payload), "{\"event\":\"order_created\",\"offset\":%lu}", (unsigned long)offset);
        }

        // Перевірка петель
        if (detect_cycle(&msg, ctx->target_cluster_id)) {
            printf("  [Міст C] ⚠️ ВИЯВЛЕНО ПЕТЛЮ msg_id=%lu -> ВІДКИДАННЯ\n", (unsigned long)msg.msg_id);
            printf("  [Джерело 0x%02x] Офсет %lu ЗАФІКСОВАНО (Source Ack loop-skip)\n", 
                   ctx->source_cluster_id, (unsigned long)msg.source_offset);
            ctx->dropped_loops_count++;
            continue;
        }

        // Додаємо ціль до шляху
        if (msg.hop_count < MAX_HOPS) {
            msg.hop_path[msg.hop_count++] = ctx->target_cluster_id;
        }

        queue_push(&ctx->queue, &msg);
    }
    return NULL;
}

static void* dispatcher_thread_func(void *arg) {
    BridgeContext *ctx = (BridgeContext*)arg;
    BridgeMessage msg;

    while (queue_pop(&ctx->queue, &msg)) {
        // Симуляція запису в ціль
        usleep(20000); // 20ms
        printf("  [Ціль 0x%02x] Записано msg_id=%lu\n", ctx->target_cluster_id, (unsigned long)msg.msg_id);

        // Фіксація на джерелі (Dual Ack)
        printf("  [Джерело 0x%02x] Офсет %lu успішно ЗАФІКСОВАНО (Source Ack)\n", 
               ctx->source_cluster_id, (unsigned long)msg.source_offset);
        ctx->forwarded_count++;
    }
    return NULL;
}

// ── 4. Запуск демонстраційного конвеєра ──────────────────────────────────────
int main(void) {
    printf("=== ЗАПУСК МОСТА ПОВІДОМЛЕНЬ (POSIX C Pipeline) ===\n");
    BridgeContext ctx;
    memset(&ctx, 0, sizeof(ctx));
    ctx.bridge_id = 101;
    ctx.source_cluster_id = 0x01;
    ctx.target_cluster_id = 0x02;
    queue_init(&ctx.queue);

    pthread_t consumer_tid, dispatcher_tid;
    pthread_create(&consumer_tid, NULL, consumer_thread_func, &ctx);
    pthread_create(&dispatcher_tid, NULL, dispatcher_thread_func, &ctx);

    pthread_join(consumer_tid, NULL);
    queue_shutdown(&ctx.queue);
    pthread_join(dispatcher_tid, NULL);

    printf("\n=== ПІДСУМОК РОБОТИ МОСТА ===\n");
    printf("Успішно ретрансльовано: %lu повідомлень\n", (unsigned long)ctx.forwarded_count);
    printf("Відсіяно циклічних петель: %lu\n", (unsigned long)ctx.dropped_loops_count);

    queue_destroy(&ctx.queue);
    return 0;
}
```
:::

## Покроковий розбір виконання конвеєра

Під час виконання демонстраційної програми конвеєр моста обробляє тестовий потік із 6 повідомлень, згенерованих вихідним брокером кластера `0x01` для передачі в цільовий кластер `0x02`. Повідомлення з індексом 3 є тестовим відлунням (повідомлення було згенероване в `0x02`, потрапило в `0x01` і намагається повернутися назад у `0x02`).

Нижче наведено протокол роботи конвеєра:

```
=== ЗАПУСК МОСТА ПОВІДОМЛЕНЬ (C++20 Pipeline) ===
  [Ціль 0x2] Записано msg_id=1000 (Hops: [0x1 -> 0x2])
  [Джерело 0x1] Офсет 0 успішно ЗАФІКСОВАНО (Source Ack)
  [Ціль 0x2] Записано msg_id=1001 (Hops: [0x1 -> 0x2])
  [Джерело 0x1] Офсет 1 успішно ЗАФІКСОВАНО (Source Ack)
  [Ціль 0x2] Записано msg_id=1002 (Hops: [0x1 -> 0x2])
  [Джерело 0x1] Офсет 2 успішно ЗАФІКСОВАНО (Source Ack)
  [Міст] ⚠️ ВИЯВЛЕНО ПЕТЛЮ у msg_id=1003 (Шлях: [0x2 -> 0x1]) -> ВІДКИДАННЯ
  [Джерело 0x1] Офсет 3 успішно ЗАФІКСОВАНО (Source Ack)
  [Ціль 0x2] Записано msg_id=1004 (Hops: [0x1 -> 0x2])
  [Джерело 0x1] Офсет 4 успішно ЗАФІКСОВАНО (Source Ack)
  [Ціль 0x2] Записано msg_id=1005 (Hops: [0x1 -> 0x2])
  [Джерело 0x1] Офсет 5 успішно ЗАФІКСОВАНО (Source Ack)

=== ПІДСУМОК РОБОТИ МОСТА ===
Успішно ретрансльовано: 5 повідомлень
Відсіяно циклічних петель: 1
```

### Аналіз ключових дій конвеєра

1. **Нормальна ретрансляція (`msg_id` 1000, 1001, 1002, 1004, 1005):**
   * Споживач вичитує пакет із джерела, додає ідентифікатор цілі `0x02` у вектор шляху `hop_path` і поміщає його в чергу `BoundedBridgeQueue`.
   * Відправник витягує пакет, передає його в цільовий брокер і блокується до завершення операції запису.
   * Після повернення `write_ok == true` міст викликає `source_broker_.commit_offset()`, фіксуючи зміщення на джерелі.

2. **Обробка та гасіння петлі (`msg_id` 1003):**
   * Повідомлення містить у векторі хопів `hop_path = {0x02, 0x01}`.
   * Функція `detect_cycle()` виявляє, що цільовий кластер `0x02` уже присутній у векторі пройденого шляху.
   * Міст не передає повідомлення у відправник, а негайно реєструє попередження, збільшує лічильник відкинутих петель і викликає `commit_offset(3)` на джерелі. Це гарантує, що покажчик читання джерела просунеться вперед, і конвеєр не зависне на цьому повідомленні при наступному перезапуску.

## Спостережуваність, моніторинг та метрики надійності

У виробничій експлуатації міст повідомлень є критичною точкою інфраструктури, що вимагає безперервного моніторингу за допомогою систем OpenTelemetry та Prometheus. Основними метриками здоров'я моста є:

1. `bridge_records_forwarded_total` — лічильник успішно доставлених та підтверджених повідомлень (розбитий за мітками джерела й цілі).
2. `bridge_records_dropped_loops_total` — кількість відсіяних циклічних повідомлень. Стрибок цієї метрики свідчить про помилку в топології маршрутизації або неправильну конфігурацію дзеркальних топіків.
3. `bridge_in_flight_messages` — поточна кількість повідомлень, які вже зчитані з джерела, але ще не отримали підтвердження від цілі. Якщо ця величина досягає розміру `max_capacity`, конвеєр перебуває під станом жорсткого протитиску.
4. `bridge_lag_source_records` — відставання (лаг) читання моста від найсвіжішого зміщення у вихідному топіку. Зростання лагу вказує на те, що пропускна здатність мережі WAN або швидкість запису цільового брокера є вузьким місцем системи.
5. `bridge_dispatch_duration_seconds` — гістограма затримки запису повідомлень у цільовий брокер (включаючи мережевий RTT між дата-центрами та час дискового скидання fsync).

## Інженерні пастки та правила надійної експлуатації

* **Пастка передчасного підтвердження (Premature Ack Anti-Pattern):**
  Найнебезпечніша помилка в розробці мостів — виклик підтвердження джерела одразу після вичитування пакета в оперативну пам'ять моста. Якщо після цього процес зазнає падіння (SIGKILL або апаратний збій вузла), усі повідомлення у внутрішньому буфері будуть назавжди втрачені: джерело вважає їх обробленими, а ціль їх не отримала.

* **Пастка отруйних повідомлень (Poison Pill Lock):**
  Якщо повідомлення містить пошкоджені байти, які цільовий брокер відхиляє з фатальною помилкою схеми або формату, міст не повинен повторювати спробу відправки нескінченно, блокуючи чергу. Після вичерпання ліміту повторів (наприклад, 5 спроб із експоненційним відступом) повідомлення має переміщатися до [мертвої черги](topic:sf-distributed/dead-letter-queue), після чого міст фіксує зміщення на джерелі й переходить до наступного пакета.

* **Пакетна фіксація (Batching & Coalesced Commits):**
  Для досягнення високої пропускної здатності (понад 100 000 msg/sec) фіксація кожного повідомлення окремо створює неприпустимий оверхед. Промислові мости групують повідомлення в пачки (batches) по 500–2000 штук, відправляють усю пачку на ціль за один мережевий виклик і фіксують максимальне зміщення пачки у джерелі лише після підтвердження всієї групи.

* **Обробка напіввідкритих TCP-з'єднань (TCP Half-Open Sockets):**
  При збоях у глобальних мережах WAN сокет відправника може годинами залишатися у стані `ESTABLISHED` без надходження відповідей від цілі, якщо відсутній контроль на рівні прикладних пінґів. Мости обов'язково повинні налаштовувати `SO_KEEPALIVE` із короткими інтервалами (наприклад, `tcp_keepalive_time = 15s`, `tcp_keepalive_intvl = 5s`, `tcp_keepalive_probes = 3`) та встановлювати жорсткі прикладні дедлайни на запис пакетів.
