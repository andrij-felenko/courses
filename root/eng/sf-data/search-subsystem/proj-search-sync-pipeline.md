# Надійний конвеєр синхронізації: Transactional Outbox, контроль версій та ротація аліасів

Коли вебсервіс розділяє дані між первинною транзакційною базою (PostgreSQL) та пошуковим рушієм (Elasticsearch або OpenSearch), головним інженерним викликом стає надійність синхронізації. Спроба оновлювати пошуковий індекс прямим викликом із HTTP-контролера неминуче призводить до втрати даних при мережевих збоях або до перезапису свіжого стану запізнілими пакетами.

Цей проєкт реалізує повний виробничий конвеєр узгодження «первинна база → пошуковий індекс». Він поєднує патерн Transactional Outbox для гарантії доставки «щонайменше раз» (англ. *at-least-once*), монотонний контроль версій для захисту від перегонів оновлень (англ. *out-of-order updates*) та механізм безшовного перемикання псевдонімів індексів (англ. *zero-downtime alias rotation*) під час зміни схем або повної переіндексації.

## Архітектурний дизайн конвеєра

Спроба зробити прямий подвійний запис виду «збережи в PostgreSQL, потім відправ у Elasticsearch» розбивається об неможливість розподіленої транзакції у ненадійній мережі. Якщо додаток успішно зафіксував зміни в реляційній базі, але впав за мілісекунду до мережевого виклику в пошуковий кластер (або отримав таймаут сокета), дані назавжди розійдуться. Первинна база міститиме актуальний стан, а пошуковий індекс повертатиме застарілі дані або взагалі не знатиме про існування нового запису.

Щоб усунути цей розрив, конвеєр синхронізації розділяється на чіткі шари з ізольованою відповідальністю:

```
[ HTTP Запит клієнта ]
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Первинна база даних (ACID Транзакція)                     │
│  ├── 1. Збереження сутності в таблицю 'products' (стан)     │
│  └── 2. Запис події в таблицю 'outbox' (seq_id + version)   │
└─────────────────────────────────────────────────────────────┘
          │
          │ (Асинхронне опитування: SELECT FOR UPDATE SKIP LOCKED)
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Outbox Relay Worker (Фоновий диспетчер)                    │
│  ├── Накопичення батчу подій (NDJSON)                       │
│  └── Відправка в чергу / Elasticsearch _bulk API            │
└─────────────────────────────────────────────────────────────┘
          │
          │ (POST /_bulk з опцією version_type=external_gte)
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Пошуковий кластер (OpenSearch / Elasticsearch)            │
│  ├── Перевірка: incoming.version >= stored.version          │
│  ├── Індекс 'products_v1'                                   │
│  └── Псевдонім (Alias): 'products_live'                     │
└─────────────────────────────────────────────────────────────┘
```

Конвеєр спирається на чотири фундаментальні інженерні принципи:

1. **Транзакційний запис (Atomic Producer):** Зміна бізнес-сутності та генерація події про зміну фіксуються в межах єдиної транзакції реляційної бази. Це дає залізобетонну гарантію: подія в черзі з'являється тоді й тільки тоді, коли бізнес-стан зафіксовано на диску первинної бази.
2. **Асинхронний релей без блокувань (Non-blocking Dispatcher):** Фоновий воркер вичитує невідправлені події з таблиці `outbox`. Завдяки конструкції `FOR UPDATE SKIP LOCKED` кілька паралельних воркерів можуть одночасно забирати різні порції подій без взаємних дедлоків і без подвійної обробки тих самих рядків.
3. **Монотонне зовнішнє версіонування (External Versioning):** Кожне оновлення сутності в первинній базі супроводжується інкрементом цілочисельної версії (`version`). Пошуковий рушій приймає цю версію і відкидає будь-яке повідомлення, якщо його версія менша або дорівнює версії вже проіндексованого документа. Це нівелює ризик перестановки подій у черзі.
4. **Індексні псевдоніми та двофазний бекфіл (Zero-Downtime Migration):** Клієнтський шар читання завжди шле запити до псевдоніма `products_live`, який вказує на поточну фізичну версію індексу. Під час міграції створюється новий індекс, наповнюється знімком із первинної бази, доганяє чергу дельти з Outbox і миттєво перемикається однією атомарною командою на рівні метаданих кластера.

## Схема реляційної бази даних для Outbox

Для коректної роботи конвеєра в первинній базі PostgreSQL створюються дві ключові таблиці:

```
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    version BIGINT NOT NULL DEFAULT 1,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE outbox_events (
    seq_id BIGSERIAL PRIMARY KEY,
    aggregate_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    version BIGINT NOT NULL,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outbox_unprocessed ON outbox_events (seq_id) WHERE processed = FALSE;
```

Індекс `idx_outbox_unprocessed` є частковим індексом (англ. *partial index*). Він індексує лише ті рядки, де `processed = FALSE`. У міру того, як воркер обробляє події та ставить `processed = TRUE`, розмір цього індексу залишається мінімальним (кілька кілобайт замість гігабайтів), що дозволяє запиту вибірки виконуватися миттєво навіть у базі з мільярдами історичних рядків.

## Програмна реалізація

Нижче наведено повноцінну реалізацію конвеєра, що охоплює модель транзакційного запису, диспетчеризацію черги, оптимістичний контроль версій і живий перерахунок індексу з нульовим простоєм.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <optional>
#include <memory>
#include <chrono>
#include <algorithm>
#include <stdexcept>

// DTO бізнес-сутності товару
struct ProductRecord {
    int64_t id;
    std::string title;
    std::string category;
    double price;
    int64_t version;
    bool is_deleted;
};

// Запис у таблиці Transactional Outbox
struct OutboxEvent {
    int64_t seq_id;
    int64_t aggregate_id;
    std::string event_type; // "UPSERT" або "DELETE"
    std::string payload_json;
    int64_t version;
    bool processed;
};

// Документ у пошуковому індексі
struct IndexedDocument {
    int64_t id;
    std::string title;
    std::string category;
    double price;
    int64_t version;
};

// Імітація пошукового індексу (Elasticsearch / OpenSearch Shard)
class SearchIndex {
public:
    explicit SearchIndex(std::string name) : name_(std::move(name)) {}

    // Індексація з оптимістичним контролем версій (external versioning)
    bool index_document(const IndexedDocument& doc) {
        auto it = storage_.find(doc.id);
        if (it != storage_.end()) {
            // Захист від гонки оновлень: ігноруємо старі або повторні версії
            if (doc.version < it->second.version) {
                std::cout << "[" << name_ << "] Відкинуто застарілу версію doc#" 
                          << doc.id << " (поточна: " << it->second.version 
                          << ", отримана: " << doc.version << ")\n";
                return false;
            }
        }
        storage_[doc.id] = doc;
        std::cout << "[" << name_ << "] Успішно проіндексовано doc#" << doc.id 
                  << " (версія: " << doc.version << ", назва: '" << doc.title << "')\n";
        return true;
    }

    bool delete_document(int64_t id, int64_t version) {
        auto it = storage_.find(id);
        if (it != storage_.end()) {
            if (version < it->second.version) {
                return false;
            }
            storage_.erase(it);
            std::cout << "[" << name_ << "] Видалено doc#" << id << " v" << version << "\n";
            return true;
        }
        return false;
    }

    [[nodiscard]] std::optional<IndexedDocument> get(int64_t id) const {
        auto it = storage_.find(id);
        if (it != storage_.end()) return it->second;
        return std::nullopt;
    }

    [[nodiscard]] size_t size() const { return storage_.size(); }
    [[nodiscard]] const std::string& name() const { return name_; }

private:
    std::string name_;
    std::unordered_map<int64_t, IndexedDocument> storage_;
};

// Менеджер псевдонімів пошуку (Index Alias Registry)
class SearchCluster {
public:
    void register_index(std::shared_ptr<SearchIndex> index) {
        indices_[index->name()] = index;
    }

    void set_alias(const std::string& alias, const std::string& target_index) {
        if (indices_.find(target_index) == indices_.end()) {
            throw std::runtime_error("Цільовий індекс не знайдено: " + target_index);
        }
        aliases_[alias] = target_index;
        std::cout << "[CLUSTER] Аліас '" << alias << "' тепер вказує на '" << target_index << "'\n";
    }

    std::shared_ptr<SearchIndex> get_by_alias(const std::string& alias) {
        auto it = aliases_.find(alias);
        if (it == aliases_.end()) return nullptr;
        return indices_[it->second];
    }

    std::shared_ptr<SearchIndex> get_index(const std::string& name) {
        auto it = indices_.find(name);
        if (it == indices_.end()) return nullptr;
        return it->second;
    }

private:
    std::unordered_map<std::string, std::shared_ptr<SearchIndex>> indices_;
    std::unordered_map<std::string, std::string> aliases_;
};

// Первинна реляційна база з підтримкою Outbox (PostgreSQL Mock)
class RelationalDatabase {
public:
    // Атомарна бізнес-операція збереження товару
    void save_product(int64_t id, const std::string& title, const std::string& category, double price) {
        int64_t current_ver = 1;
        auto it = products_.find(id);
        if (it != products_.end()) {
            current_ver = it->second.version + 1;
        }

        ProductRecord record{id, title, category, price, current_ver, false};
        products_[id] = record;

        // В тій самій транзакції створюємо запис в Outbox
        int64_t next_seq = static_cast<int64_t>(outbox_.size() + 1);
        std::string json_repr = "{\"title\":\"" + title + "\",\"category\":\"" + category + "\"}";
        
        outbox_.push_back(OutboxEvent{
            next_seq,
            id,
            "UPSERT",
            json_repr,
            current_ver,
            false // ще не оброблено
        });

        std::cout << "[DB] Збережено товар #" << id << " v" << current_ver 
                  << " та додано outbox event seq#" << next_seq << "\n";
    }

    // Вибірка невідправлених подій для Outbox Relay Worker
    std::vector<OutboxEvent> fetch_unprocessed_outbox(size_t batch_size) {
        std::vector<OutboxEvent> batch;
        for (auto& ev : outbox_) {
            if (!ev.processed) {
                batch.push_back(ev);
                if (batch.size() >= batch_size) break;
            }
        }
        return batch;
    }

    void mark_outbox_processed(int64_t seq_id) {
        for (auto& ev : outbox_) {
            if (ev.seq_id == seq_id) {
                ev.processed = true;
                break;
            }
        }
    }

    // Вивантаження історичного знімка для бекфілу
    std::vector<ProductRecord> get_all_active_products() const {
        std::vector<ProductRecord> list;
        for (const auto& [id, prod] : products_) {
            if (!prod.is_deleted) {
                list.push_back(prod);
            }
        }
        return list;
    }

    [[nodiscard]] int64_t get_current_max_seq() const {
        return static_cast<int64_t>(outbox_.size());
    }

    std::vector<OutboxEvent> get_events_after(int64_t after_seq) const {
        std::vector<OutboxEvent> delta;
        for (const auto& ev : outbox_) {
            if (ev.seq_id > after_seq) {
                delta.push_back(ev);
            }
        }
        return delta;
    }

private:
    std::unordered_map<int64_t, ProductRecord> products_;
    std::vector<OutboxEvent> outbox_;
};

// Служба синхронізації та міграції індексів
class SearchSyncPipeline {
public:
    SearchSyncPipeline(RelationalDatabase& db, SearchCluster& cluster)
        : db_(db), cluster_(cluster) {}

    // Цикл диспетчера Outbox: передає події в активний індекс
    void process_outbox_batch(const std::string& write_alias) {
        auto index = cluster_.get_by_alias(write_alias);
        if (!index) throw std::runtime_error("Активний індекс не знайдено для аліаса");

        auto batch = db_.fetch_unprocessed_outbox(10);
        for (const auto& ev : batch) {
            if (ev.event_type == "UPSERT") {
                // У реальній системі тут відбувається парсинг JSON
                IndexedDocument doc{
                    ev.aggregate_id,
                    "Sony WH-1000XM5", // спрощений розбір для ілюстрації
                    "audio",
                    14999.0,
                    ev.version
                };
                index->index_document(doc);
            }
            db_.mark_outbox_processed(ev.seq_id);
        }
    }

    // Повна жива переіндексація з нульовим простоєм (Zero-Downtime Reindex)
    void execute_zero_downtime_reindex(
        const std::string& alias_name, 
        const std::string& new_index_name) 
    {
        std::cout << "\n=== СТАРТ ЖИВОЇ ПЕРЕІНДЕКСАЦІЇ: " << new_index_name << " ===\n";

        // Крок 1: Створення нового індексу
        auto new_index = std::make_shared<SearchIndex>(new_index_name);
        cluster_.register_index(new_index);

        // Фіксуємо точку відліку змін перед початком знімка
        int64_t snapshot_seq = db_.get_current_max_seq();
        std::cout << "[MIGRATION] Точка фіксації послідовності (LSN): seq#" << snapshot_seq << "\n";

        // Крок 2: Пакетний бекфіл з первинної бази (Bulk backfill)
        auto snapshot_data = db_.get_all_active_products();
        std::cout << "[MIGRATION] Бекфіл: перенесення " << snapshot_data.size() << " документів...\n";
        for (const auto& prod : snapshot_data) {
            new_index->index_document(IndexedDocument{
                prod.id, prod.title, prod.category, prod.price, prod.version
            });
        }

        // Крок 3: Доганяння подій, які виникли під час бекфілу (Catch-up replay)
        auto delta_events = db_.get_events_after(snapshot_seq);
        std::cout << "[MIGRATION] Доганяння черги: застосування " << delta_events.size() << " дельта-подій...\n";
        for (const auto& ev : delta_events) {
            new_index->index_document(IndexedDocument{
                ev.aggregate_id, "Оновлений товар", "audio", 15500.0, ev.version
            });
        }

        // Крок 4: Атомарне перемикання псевдоніма
        cluster_.set_alias(alias_name, new_index_name);
        std::cout << "=== ПЕРЕІНДЕКСАЦІЮ ЗАВЕРШЕНО УСПІШНО ===\n\n";
    }

private:
    RelationalDatabase& db_;
    SearchCluster& cluster_;
};
```
```ts
// DTO сутностей для TypeScript / Node.js реалізації
interface ProductRecord {
  id: number;
  title: string;
  category: string;
  price: number;
  version: number;
  isDeleted: boolean;
}

interface OutboxEvent {
  seqId: number;
  aggregateId: number;
  eventType: 'UPSERT' | 'DELETE';
  payload: Record<string, unknown>;
  version: number;
  processed: boolean;
}

interface IndexedDocument {
  id: number;
  title: string;
  category: string;
  price: number;
  version: number;
}

// Пошуковий індекс з оптимістичним контролем версій
class SearchIndex {
  private storage = new Map<number, IndexedDocument>();

  constructor(public readonly name: string) {}

  public indexDocument(doc: IndexedDocument): boolean {
    const existing = this.storage.get(doc.id);
    if (existing && doc.version < existing.version) {
      console.log(`[${this.name}] Відкинуто застарілу версію doc#${doc.id} (поточна: ${existing.version}, вхідна: ${doc.version})`);
      return false;
    }
    this.storage.set(doc.id, doc);
    console.log(`[${this.name}] Проіндексовано doc#${doc.id} (v${doc.version}: '${doc.title}')`);
    return true;
  }

  public get(id: number): IndexedDocument | undefined {
    return this.storage.get(id);
  }

  public size(): number {
    return this.storage.size;
  }
}

// Кластер із підтримкою аліасів
class SearchCluster {
  private indices = new Map<string, SearchIndex>();
  private aliases = new Map<string, string>();

  public registerIndex(index: SearchIndex): void {
    this.indices.set(index.name, index);
  }

  public setAlias(alias: string, targetIndexName: string): void {
    if (!this.indices.has(targetIndexName)) {
      throw new Error(`Цільовий індекс ${targetIndexName} не зареєстровано`);
    }
    this.aliases.set(alias, targetIndexName);
    console.log(`[CLUSTER] Аліас '${alias}' перемкнуто на '${targetIndexName}'`);
  }

  public getByAlias(alias: string): SearchIndex | undefined {
    const target = this.aliases.get(alias);
    return target ? this.indices.get(target) : undefined;
  }
}

// Реляційна база з Transactional Outbox
class RelationalDatabase {
  private products = new Map<number, ProductRecord>();
  private outbox: OutboxEvent[] = [];

  public saveProduct(id: number, title: string, category: string, price: number): void {
    const current = this.products.get(id);
    const nextVer = current ? current.version + 1 : 1;

    const record: ProductRecord = {
      id,
      title,
      category,
      price,
      version: nextVer,
      isDeleted: false,
    };
    this.products.set(id, record);

    const seqId = this.outbox.length + 1;
    this.outbox.push({
      seqId,
      aggregateId: id,
      eventType: 'UPSERT',
      payload: { title, category, price },
      version: nextVer,
      processed: false,
    });

    console.log(`[DB] Збережено товар #${id} v${nextVer}, додано outbox seq#${seqId}`);
  }

  public fetchUnprocessedOutbox(limit: number): OutboxEvent[] {
    return this.outbox.filter((e) => !e.processed).slice(0, limit);
  }

  public markProcessed(seqId: number): void {
    const ev = this.outbox.find((e) => e.seqId === seqId);
    if (ev) ev.processed = true;
  }

  public getAllActiveProducts(): ProductRecord[] {
    return Array.from(this.products.values()).filter((p) => !p.isDeleted);
  }

  public getCurrentMaxSeq(): number {
    return this.outbox.length;
  }

  public getEventsAfter(seq: number): OutboxEvent[] {
    return this.outbox.filter((e) => e.seqId > seq);
  }
}

// Конвеєр живої міграції та синхронізації
class SearchSyncPipeline {
  constructor(
    private db: RelationalDatabase,
    private cluster: SearchCluster,
  ) {}

  public processOutbox(aliasName: string): void {
    const index = this.cluster.getByAlias(aliasName);
    if (!index) throw new Error(`Аліас ${aliasName} не знайдено`);

    const batch = this.db.fetchUnprocessedOutbox(10);
    for (const ev of batch) {
      if (ev.eventType === 'UPSERT') {
        index.indexDocument({
          id: ev.aggregateId,
          title: String(ev.payload.title),
          category: String(ev.payload.category),
          price: Number(ev.payload.price),
          version: ev.version,
        });
      }
      this.db.markProcessed(ev.seqId);
    }
  }

  public executeZeroDowntimeReindex(aliasName: string, newIndexName: string): void {
    console.log(`\n=== СТАРТ МІГРАЦІЇ В ${newIndexName} ===`);
    const newIndex = new SearchIndex(newIndexName);
    this.cluster.registerIndex(newIndex);

    const snapshotSeq = this.db.getCurrentMaxSeq();
    const items = this.db.getAllActiveProducts();

    console.log(`[MIGRATION] Бекфіл: перенесення ${items.length} записів...`);
    for (const item of items) {
      newIndex.indexDocument({
        id: item.id,
        title: item.title,
        category: item.category,
        price: item.price,
        version: item.version,
      });
    }

    const delta = this.db.getEventsAfter(snapshotSeq);
    console.log(`[MIGRATION] Доганяння: застосування ${delta.length} подій...`);
    for (const ev of delta) {
      newIndex.indexDocument({
        id: ev.aggregateId,
        title: String(ev.payload.title),
        category: String(ev.payload.category),
        price: Number(ev.payload.price),
        version: ev.version,
      });
    }

    this.cluster.setAlias(aliasName, newIndexName);
    console.log(`=== МІГРАЦІЮ ЗАВЕРШЕНО ===\n`);
  }
}
```
:::

## Поглиблений розбір механізмів конвеєра

### 1. Механіка вибірки Outbox без конкурентних блокувань

У високонавантажених системах кілька екземплярів фонового сервісу (англ. *worker pool*) паралельно вичитують таблицю `outbox`. Якщо використовувати звичайний запит `SELECT ... WHERE processed = false LIMIT 100`, воркери блокуватимуть одні й ті самі рядки або спричинятимуть взаємне очікування на рівні блокувань сторінок (англ. *lock contention*).

Виробниче рішення полягає у використанні конструкції `FOR UPDATE SKIP LOCKED` у PostgreSQL:

```
SELECT seq_id, aggregate_id, event_type, payload, version
FROM outbox_events
WHERE processed = FALSE
ORDER BY seq_id ASC
LIMIT 100
FOR UPDATE SKIP LOCKED;
```

Коли перший воркер захоплює 100 рядків, ядро бази даних блокує їх для поточної транзакції. Другий воркер, виконуючи той самий запит у паралельному потоці, не чекає на завершення першого, а миттєво «перестрибує» заблоковані рядки та отримує наступні 100 записів. Це забезпечує лінійне масштабування пропускної здатності вичитування за кількістю робочих процесів.

Тут криється важлива тонкість щодо рівнів ізоляції транзакцій. У стандартному режимі `READ COMMITTED` дві паралельні транзакції можуть отримати номери `seq_id` у порядку `101` та `102`, але транзакція `102` може зафіксуватися раніше за `101`. Якщо воркер просто пам'ятає `last_seen_seq_id = 102`, він назавжди пропустить подію `101`. Завдяки булевому прапорцю `processed = FALSE` та частковому індексу ця небезпека повністю зникає: воркер обирає будь-які незафіксовані рядки незалежно від дірок у нумерації.

### 2. Захист від гонки перестановки та формат Elasticsearch Bulk API

У розподіленому середовищі повідомлення з черги можуть надходити споживачам із затримкою або оброблятися паралельними потоками з різною швидкістю. Розглянемо класичний аварійний сценарій перестановки оновлень:

```
t1: Потік 1: Оновлення ціни товару (версія v=2) ──> Затримка в черзі / мережі (150 мс)
t2: Потік 2: Оновлення опису товару (версія v=3) ─> Доставлено миттєво (v=3 зафіксовано)
t3: Потік 1: Запізніле повідомлення v=2 нарешті прибуло до пошукового рушія
```

Якщо запізніле повідомлення від Потоку 1 сліпо перезапише стан документа, ціна оновиться, але опис повернеться до застарілого значення версії `v=2` — виникне прихована розсинхронізація між базою та пошуком.

Щоб цьому запобігти, воркер відправляє документи до Elasticsearch/OpenSearch через пакетний інтерфейс `_bulk` у форматі NDJSON (англ. *Newline Delimited JSON*), явно вказуючи тип версіонування `version_type=external_gte`:

```
action_and_meta_data\n
optional_source\n
```

Приклад реального пакетного тіла:

```
{"index": {"_index": "products_live", "_id": "42", "version": 3, "version_type": "external_gte"}}
{"title": "Sony WH-1000XM5", "category": "audio", "price": 14999.0, "version": 3}
{"index": {"_index": "products_live", "_id": "42", "version": 2, "version_type": "external_gte"}}
{"title": "Sony WH-1000XM5", "category": "audio", "price": 13500.0, "version": 2}
```

Пошуковий рушій виконує внутрішню перевірку: якщо надіслана версія менша за версію, яка вже зберігається в Lucene-сегменті для цього документа, операція відхиляється зі статусом HTTP `409 Conflict` (англ. *VersionConflictEngineException*). Воркер сприймає статус 409 не як критичну помилку, а як штатно відкинуте старе оновлення, безпечно продовжуючи роботу.

### 3. Порівняння підходів: Transactional Outbox проти CDC (Change Data Capture)

Поряд із патерном Outbox у великих архітектурах застосовують Change Data Capture (CDC) на базі вичитування бінарного журналу WAL (наприклад, за допомогою Debezium або власних слотів логічної реплікації PostgreSQL `pgoutput`):

| Критерій | Transactional Outbox | Change Data Capture (CDC / Debezium) |
| :--- | :--- | :--- |
| **Місце збереження** | Окрема таблиця в первинній БД | Журнал транзакцій бази (WAL / binlog) |
| **Вплив на БД** | Додатковий `INSERT` у транзакції | Нульовий оверхед на час транзакції |
| **Трансформація даних** | Формується на рівні сервісу (DTO) | Вимагає окремого конвеєра збагачення |
| **Складність інфраструктури** | Мінімальна (лише таблиця та воркер) | Висока (Kafka Connect, Debezium, ZooKeeper/KRaft) |
| **Ризик відмови** | Роздування таблиці при падінні воркера | Переповнення диска WAL при зависанні слота |

Для більшості вебсервісів патерн Transactional Outbox є оптимальним стартовим рішенням: він дозволяє сервісу самостійно формувати денормалізований JSON-документ прямо під час транзакції, не розгортаючи важку інфраструктуру реплікаційних коннекторів.

### 4. Точка фіксації послідовності під час бекфілу (Snapshot Isolation)

Найнебезпечніший момент під час створення нового індексу `products_v2` — це поява розривів між історичними даними та потоковими змінами, які надходять під час копіювання таблиці:

1. **Фіксація точки старту:** Конвеєр зчитує поточний максимальний номер послідовності `snapshot_seq = MAX(seq_id)` з таблиці `outbox`.
2. **Пакетне вивантаження знімка:** Конвеєр копіює мільйони рядків із таблиці `products`. Цей процес може тривати десятки хвилин.
3. **Потік дельти:** Усі зміни, які користувачі здійснювали протягом цього часу, накопичуються в таблиці `outbox` з номерами `seq_id > snapshot_seq`.
4. **Доганяння дельти (Catch-up phase):** Після завершення копіювання таблиці конвеєр робить вибірку `SELECT * FROM outbox_events WHERE seq_id > snapshot_seq ORDER BY seq_id ASC` і проганяє всі ці події через новий індекс. Завдяки контролю версій `external_gte` навіть якщо якась зміна потрапила і в знімок, і в дельту, документ отримає фінальний коректний стан.

### 5. Атомарне перемикання псевдоніма (Zero-Downtime Alias Switch)

Клієнтський шар програми ніколи не знає фізичної назви індексу. Додаток шле пошукові запити на псевдонім `products_live`.

Перемикання виконується однією атомарною HTTP-командою на рівні метаданих кластера:

```
POST /_aliases
{
  "actions": [
    { "remove": { "index": "products_v1", "alias": "products_live" } },
    { "add":    { "index": "products_v2", "alias": "products_live" } }
  ]
}
```

Операція виконується в пам'яті головного вузла (англ. *Cluster Master*) за лічені мілісекунди. Жоден клієнтський запит не отримає помилку `404 Not Found`, а видача пошуку миттєво переходить на нову структуру даних.

### 6. Денормалізація та каскадні оновлення (Fan-Out Invalidation)

У реляційній базі дані нормалізовані: таблиця `products` містить `category_id`, що посилається на таблицю `categories`. У пошуковому індексі для високої швидкості фільтрації та фасетів категорія зберігається денормалізовано прямо всередині документа товару (`{"category_name": "Аудіотехніка"}`).

Це породжує проблему каскадних оновлень: коли адміністратор змінює назву категорії з «Аудіотехніка» на «Аудіо та акустика», у первинній базі оновлюється рівно один рядок. Проте в пошуковому індексі необхідно оновити 50 000 товарів, що належать до цієї категорії.

Конвеєр розв'язує цю проблему через спеціальні віялові події (англ. *fan-out events*):
1. Транзакція зміни категорії додає в Outbox подію `CategoryRenamedEvent { category_id: 5, new_title: "..." }`.
2. Спеціальний фоновий воркер вичитує всі `product_id` цієї категорії з первинної бази порціями по 1000 штук.
3. Воркер генерує масові запити на часткове оновлення поля (англ. *Update By Query*) або додає дельти в чергу індексації, зберігаючи інкремент версії для кожного товару.

### 7. Обробка видалень та надгробки (Tombstones)

Коли товар видаляється в первинній базі даних, реляційна таблиця або повністю видаляє рядок (`DELETE FROM products`), або ставить прапорець м'якого видалення (`is_deleted = TRUE`).

Для пошукового індексу обидва випадки мають перетворитися на явну команду видалення з обов'язковим контролем версії. Подія в таблиці `outbox_events` отримує тип `DELETE`, а тіло пакетного запиту до Elasticsearch виглядає так:

```
{"delete": {"_index": "products_live", "_id": "42", "version": 4, "version_type": "external_gte"}}
```

Якщо видалення товару відбулося після його оновлення (версія 4 після версії 3), документ видаляється з індексу. Якщо ж запізніле оновлення версії 3 надійде після видалення версії 4, Elasticsearch відхилить спробу воскресити видалений документ через невідповідність зовнішньої версії.

### 8. Взаємодія з кешами пошукових результатів (Cache Invalidation)

У системах з високим навантаженням результати пошуку часто кешуються в Redis на 15–60 секунд за хешем параметрів запиту (`search:hash(q, filters, sort)`).

Коли конвеєр індексує оновлення товару, він не може точково витерти всі кешовані пошукові видачі, куди міг потрапити цей товар, оскільки таких комбінацій фільтрів можуть бути мільйони.

Виробниче рішення полягає в застосуванні версіонування простору ключів (англ. *epoch/generation invalidation*):
1. Кластер підтримує лічильник покоління каталогу `catalog_epoch = 142` у Redis.
2. Ключ кешу формується з урахуванням поточної епохи: `search:v142:q=sony`.
3. Коли Outbox-диспетчер фіксує масові зміни або завершує ротацію аліаса, він інкрементує `catalog_epoch = 143`. Усі старі кешовані пошукові сторінки миттєво стають недійсними й поступово витісняються за TTL, запобігаючи показу «примарних» товарів.

### 9. Автоматизована верифікація та перевірка інваріантів узгодженості

У зрілих інженерних командах надійність конвеєра перевіряється спеціальними фоновими задачами звірки (англ. *reconciliation jobs*), які запускаються щоночі:

- **Інваріант повноти кількості:** Загальна кількість активних документів у первинній базі повинна точно дорівнювати кількості документів у пошуковому індексі (`COUNT(db.products WHERE is_deleted=FALSE) == es.count(products_live)`).
- **Інваріант версійної монотонності:** Вибіркова звірка 10 000 випадкових записів перевіряє умову `db.product.version == es.doc.version`. Будь-яке відхилення сигналізує про збій у черзі або зависання воркера.
- **Хаос-тестування:** Періодичний аварійний перезапуск воркера під час передачі великого батчу (`kill -9`) доводить, що механізм `at-least-once` повторно зчитує незафіксовані рядки без дублювання записів та без помилок у пошуковому індексі. Перевіряється також реакція на штучні затримки мережі між базою та брокером повідомлень.

## Простеження життєвого циклу: наскрізний тестовий сценарій

Щоб наочно побачити, як взаємодіють усі компоненти конвеєра в нештатних ситуаціях, простежимо покроковий життєвий цикл товару `#101` у системі:

```
Хронологія подій у системі:
-------------------------------------------------------------------------------------------------------------
Крок 1 [t=0 мс]:   POST /products  →  Збережено в DB (id=101, v=1, title="Sony XM4", price=9000)
                   Outbox: додано seq=1 (v=1)
Крок 2 [t=10 мс]:  Outbox Relay вичитує seq=1  →  POST /_bulk  →  Індекс v1 містить doc#101 v=1
-------------------------------------------------------------------------------------------------------------
Крок 3 [t=100 мс]: Користувач змінює ціну: PUT /products/101  →  DB оновлено (v=2, price=8500)
                   Outbox: додано seq=2 (v=2)
Крок 4 [t=105 мс]: Менеджер змінює назву: PUT /products/101   →  DB оновлено (v=3, title="Sony WH-1000XM4")
                   Outbox: додано seq=3 (v=3)
-------------------------------------------------------------------------------------------------------------
Крок 5 [t=110 мс]: Воркер A бере seq=2, але через сплеск навантаження зависає в мережі на 300 мс
Крок 6 [t=112 мс]: Воркер B бере seq=3, миттєво відправляє в індекс v1  →  Індекс v1 містить doc#101 v=3
Крок 7 [t=410 мс]: Воркер A нарешті надсилає запізнілий seq=2  →  Elasticsearch бачить: вхідна v=2 < наявна v=3
                   Результат: HTTP 409 Conflict  →  подію seq=2 відкинуто, стан doc#101 v=3 НЕ пошкоджено!
-------------------------------------------------------------------------------------------------------------
Крок 8 [t=500 мс]: Запуск міграції на products_v2:
                   - snapshot_seq зафіксовано як 3
                   - бекфіл скопіював doc#101 v=3 у products_v2
                   - дельта після seq=3 порожня
                   - перемикання аліаса products_live: products_v1 → products_v2
-------------------------------------------------------------------------------------------------------------
```

Цей покроковий сценарій доводить, що система зберігає математичну строгість на кожному етапі: жодні затримки процесів або мережеві глічі не можуть порушити узгодженість стану між первинною базою даних та пошуковим кластером.

## Виробничі пастки та тюнінг продуктивності

- **Тюнінг швидкості бекфілу (Bulk Tuning):** Під час початкового наповнення нового індексу мільйонами документів стандартні налаштування Lucene сповільнюють запис. Необхідно тимчасово вимкнути скидання сегментів у пам'яті та реплікацію:
  - Встановити `"index.refresh_interval": "-1"`.
  - Встановити `"index.number_of_replicas": 0`.
  Після завершення вивантаження повертають `"refresh_interval": "1s"` та `"number_of_replicas": 1`, запускають примусове скидання сегментів (`POST /products_v2/_refresh`) і лише після цього перемикають аліас.
- **Отруйні повідомлення та мертва черга (Poison Message / Dead Letter Queue):** Якщо через помилку в коді або мапінгу документ не може бути проіндексований (наприклад, у поле типу `float` передано рядок `"N/A"`), спроба повторити запис зациклить воркер. Конвеєр повинен мати лічильник спроб: після 3 невдалих спроб подія переміщується в окрему таблицю `outbox_dead_letter` з фіксацією тексту помилки, а черга продовжує рух.
- **Очищення оброблених рядків Outbox (Compaction):** Накопичення мільйонів рядків зі статусом `processed = true` роздуває таблицю та індекси в PostgreSQL (англ. *table bloat*). Необхідно або налаштувати періодичний фоновий крон-скрипт видалення старих рядків батчами (`DELETE FROM outbox_events WHERE processed = TRUE AND created_at < NOW() - INTERVAL '3 days' LIMIT 5000`), або використовувати секціонування таблиці Outbox за днями (англ. *table partitioning*) зі скиданням старих секцій через `DROP TABLE`.
- **Затримка видалення старого індексу:** Після перемикання аліаса старий індекс `products_v1` не слід видаляти негайно. Розумно перевести його в режим «лише для читання» (`"index.blocks.read_only": true`) і зберегти на 24–48 годин. Якщо у новій схемі `v2` виявиться критична помилка в алгоритмі ранжування або аналізаторі, відкат назад до `v1` займе 10 мілісекунд через повторне перемикання аліаса.
- **Обробка вичерпання пулу з'єднань і тиску черги (Backpressure):** Якщо пошуковий кластер перевантажений і повертає HTTP `429 Too Many Requests` (англ. *es_rejected_execution_exception*), Outbox-воркер зобов'язаний застосувати експоненційне відступання з джипом (англ. *exponential backoff with full jitter*). Спроба продовжувати бомбардувати чергу запитами `_bulk` призведе до колапсу черги завдань на вузлах кластера (англ. *write threadpool saturation*).
- **Масштабування вичитування та шардинг Outbox:** Якщо обсяг мутацій перевищує 50 000 транзакцій на секунду, єдина таблиця `outbox_events` стає вузьким місцем транзакційного лога PostgreSQL. У такому масштабі таблицю секціонують за хешем від `aggregate_id` на `N` фізичних партицій (`outbox_events_0`, `outbox_events_1`, ... `outbox_events_15`), і кожен воркер обслуговує виключно свою партицію, що повністю ліквідує конкуренцію за блокування рядків.
- **Метрики спостережуваності та алерти:** Виробничий конвеєр зобов'язаний експортувати три критичні метрики:
  - `outbox_replication_lag_seconds` — різниця між поточним часом і `created_at` найстарішого необробленого рядка. Якщо лаг перевищує 5–10 секунд, черга не встигає за темпом мутацій.
  - `elasticsearch_bulk_rejected_total` — лічильник відповідей 429, що сигналізує про вичерпання дискового вводу-виводу або процесорів на вузлах даних.
  - `outbox_dead_letter_count` — кількість отруйних повідомлень, що вимагає втручання інженера для виправлення схеми чи коду DTO.
