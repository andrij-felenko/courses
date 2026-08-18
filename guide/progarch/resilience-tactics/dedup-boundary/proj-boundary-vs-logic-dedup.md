# ⚙️ Практична реалізація: Дедуплікатор на межі шлюзу vs транзакційна перевірка в базі даних

Ця вставка демонструє практичну реалізацію обох підходів до дедуплікації: швидкий in-memory / TTL фільтр на межі API Gateway для масового відсікання дубльованого трафіку та суворий транзакційний дедуплікатор на рівні бізнес-логіки з підтримкою ACID-гарантій.

## Інженерний контекст та вимоги до реалізації

При побудові високонавантажених шлюзів (API Gateway / Ingest Proxy) інженер стикається з викликом розмежування відповідальності між швидкодією та суворістю цілісності. 

Шлюз межі оперує в умовах екстремально жорсткого бюджету затримок (Latency Budget): обробка кожного вхідного пакета або HTTP-запиту не повинна перевищувати 1-2 мілісекунди. Застосування важких мережевих викликів до реляційних баз даних на межі є неприпустимим, оскільки це спричиняє вичерпання пулу сокетів і різкий стрибок затримок у дев'яносто дев'ятому перцентилі (P99 latency).

З іншого боку, доменний сервіс бізнес-логіки не може покладатися лише на тимчасові кеші шлюзу, оскільки будь-яке аварійне завершення процесу (process crash, Out-Of-Memory killer, мережеве розщеплення split-brain) знищує вміст оперативної пам'яті. Отже, доменний шар змушений застосовувати транзакційний запис у постійне сховище (OLTP Database).

Нижче наведено вичерпні реалізації обох підходів мовами C, C++ та Go, що ілюструють принципові відмінності керування пам'яттю, потокобезпечністю та атомарністю.

## Детальний розбір реалізацій

### 1. Реалізація мовою C: Низькорівневе керування пам'яттю та хеш-таблиця з TTL

У реалізації мовою C фільтр дедуплікації на межі побудовано як хеш-таблицю з ланцюжковим вирішенням колізій (chaining). Кожен елемент таблиці зберігає копію рядкового ключа та абсолютний штамп часу закінчення терміну придатності (`expires_at`).

Особливості низькорівневого підходу на C:
- **Хеш-функція:** Застосовується алгоритм djb2, який забезпечує рівномірний розподіл рядкових ключів по бакетах.
- **Очищення пам'яті:** Функція `edge_dedup_destroy` явно вивільняє кожен вузол зв'язаного списку у всіх бакетах для запобігання витокам пам'яті (memory leaks).
- **Перевірка TTL:** При виявленні наявного ключа перевіряється поточний системний час `time(NULL)`. Якщо ключ застарів, його TTL автоматично оновлюється без повторного виділення пам'яті через `malloc`.

Доменний шар симулює виконання SQL-транзакції, де роль обмеження унікальності виконує перевірка прапорця в ізольованому транзакційному контексті.

### 2. Реалізація мовою C++: Сучасний C++20, RAII та `std::expected`

У реалізації мовою C++ застосовуються новітні стандарти мови (C++20), що гарантує суворий контроль ресурсів без ризику витоків пам'яті:
- **RAII та автоматичний lifetime:** Контейнери `std::unordered_map` самостійно керують виділенням та звільненням пам'яті під ключі.
- **Ефективне передавання рядків:** Використання `std::string_view` у параметрах методів позбавляє від необхідності створювати тимчасові копії рядків при викликах перевірки.
- **Часовий apparatus:** Модуль `std::chrono::steady_clock` захищає від стрибків системного часу (наприклад, при синхронізації NTP), на відміну від монотонного системного часу.
- **Явна обробка помилок:** Замість винятків або повернення сирих від'ємних кодів помилок застосовується `std::expected<void, DomainError>`, що робить обробку невдачі унікального індексу явною на рівні типів даних.

### 3. Реалізація мовою Go: Конкурентна безпека та `sync.Mutex`

Реалізація мовою Go орієнтована на мережеві веб-сервіси, де кожен вхідний запит обробляється в окремій легковажній рутині (goroutine).
- **Потокобезпечність:** Доступ до карти `map[string]time.Time` захищено взаємним блокуванням `sync.Mutex`, що унеможливлює гонку даних (data race) при паралельних викликах.
- **Контекст виклику:** Передавання `context.Context` у доменну транзакцію дозволяє скасувати виконання операції в базі даних, якщо клієнт розірвав з'єднання до завершення транзакції.

:::tabs
```c
/* C: Реалізація Edge Filter (in-memory hash table з TTL)
   та Domain Transactional Check */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

#define TABLE_SIZE 1024
#define DEFAULT_TTL_SECONDS 300

typedef struct CacheEntry {
    char key[64];
    time_t expires_at;
    struct CacheEntry* next;
} CacheEntry;

typedef struct {
    CacheEntry* buckets[TABLE_SIZE];
} EdgeDeduplicator;

/* Проста хеш-функція djb2 */
static unsigned long hash_key(const char* str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % TABLE_SIZE;
}

EdgeDeduplicator* edge_dedup_create(void) {
    EdgeDeduplicator* dedup = (EdgeDeduplicator*)calloc(1, sizeof(EdgeDeduplicator));
    return dedup;
}

void edge_dedup_destroy(EdgeDeduplicator* dedup) {
    if (!dedup) return;
    for (int i = 0; i < TABLE_SIZE; i++) {
        CacheEntry* entry = dedup->buckets[i];
        while (entry) {
            CacheEntry* tmp = entry;
            entry = entry->next;
            free(tmp);
        }
    }
    free(dedup);
}

/* 1. Дедуплікація на межі (Edge Deduplication Check) */
bool edge_dedup_check_and_register(EdgeDeduplicator* dedup, const char* key, int ttl_seconds) {
    time_t now = time(NULL);
    unsigned long idx = hash_key(key);
    CacheEntry* entry = dedup->buckets[idx];

    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            if (entry->expires_at > now) {
                /* Знайдено активний дублікат на межі! */
                return false; 
            } else {
                /* Ключ застарів — оновлюємо TTL */
                entry->expires_at = now + ttl_seconds;
                return true;
            }
        }
        entry = entry->next;
    }

    /* Новий ключ — додаємо в кеш межі */
    CacheEntry* new_entry = (CacheEntry*)malloc(sizeof(CacheEntry));
    strncpy(new_entry->key, key, sizeof(new_entry->key) - 1);
    new_entry->key[sizeof(new_entry->key) - 1] = '\0';
    new_entry->expires_at = now + ttl_seconds;
    new_entry->next = dedup->buckets[idx];
    dedup->buckets[idx] = new_entry;

    return true; /* Запит унікальний для вікна межі */
}

/* 2. Дедуплікація у логіці / DB (Domain Transactional Check) */
typedef struct {
    bool is_duplicate_in_db;
} MockDatabaseTransaction;

bool domain_process_order_transactional(MockDatabaseTransaction* tx, const char* order_id, const char* key) {
    /* Симуляція виконання в межах BEGIN ... COMMIT */
    if (tx->is_duplicate_in_db) {
        /* UNIQUE constraint rollback у DB */
        printf("[Domain DB] UNIQUE constraint violation for key: %s. Rolling back!\n", key);
        return false;
    }

    /* Атомарний запис у БД: INSERT INTO orders + INSERT INTO processed_keys */
    printf("[Domain DB] Successfully inserted order %s with idempotency key %s (COMMITTED)\n", order_id, key);
    return true;
}

int main(void) {
    EdgeDeduplicator* edge = edge_dedup_create();
    const char* req_key = "REQ-PAYMENT-99812";

    printf("--- Траєкторія 1: Перший запит ---\n");
    if (edge_dedup_check_and_register(edge, req_key, DEFAULT_TTL_SECONDS)) {
        printf("[Edge Gateway] Key %s passed filter.\n", req_key);
        MockDatabaseTransaction tx1 = { .is_duplicate_in_db = false };
        domain_process_order_transactional(&tx1, "ORD-101", req_key);
    }

    printf("\n--- Траєкторія 2: Швидкий повтор (Retry) через 500мс ---\n");
    if (!edge_dedup_check_and_register(edge, req_key, DEFAULT_TTL_SECONDS)) {
        printf("[Edge Gateway] BLOCKED DUPLICATE key %s at boundary! DB not touched.\n", req_key);
    }

    edge_dedup_destroy(edge);
    return 0;
}
```
```cpp
// C++20: Ідіоматичний Edge Filter та Domain Deduplication з RAII та std::unordered_map

#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <chrono>
#include <memory>
#include <optional>
#include <expected>

class EdgeDeduplicator {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    explicit EdgeDeduplicator(std::chrono::seconds default_ttl)
        : default_ttl_(default_ttl) {}

    // Повертає true, якщо запит унікальний і зареєстрований; false якщо це дублікат
    bool check_and_register(std::string_view key) {
        const auto now = Clock::now();
        cleanup_expired(now);

        auto it = cache_.find(std::string(key));
        if (it != cache_.end()) {
            if (it->second > now) {
                return false; // Запит є дублікатом у межах TTL вікна
            }
        }

        cache_[std::string(key)] = now + default_ttl_;
        return true;
    }

private:
    void cleanup_expired(TimePoint now) {
        for (auto it = cache_.begin(); it != cache_.end(); ) {
            if (it->second <= now) {
                it = cache_.erase(it);
            } else {
                ++it;
            }
        }
    }

    std::chrono::seconds default_ttl_;
    std::unordered_map<std::string, TimePoint> cache_;
};

enum class DomainError {
    DuplicateKeyInDatabase,
    DatabaseConnectionFailed
};

class DomainRepository {
public:
    std::expected<void, DomainError> process_order_atomically(std::string_view order_id, std::string_view key) {
        if (processed_keys_.contains(std::string(key))) {
            return std::unexpected(DomainError::DuplicateKeyInDatabase);
        }

        // Атомарна мутація в DB
        processed_keys_.insert(std::string(key));
        std::cout << "[Domain C++] Executed order " << order_id << " with key " << key << " inside DB transaction.\n";
        return {};
    }

private:
    std::unordered_set<std::string> processed_keys_;
};

int main() {
    EdgeDeduplicator edge_gateway(std::chrono::seconds(60));
    DomainRepository db_repo;

    const std::string idempotency_key = "IDEM-KEY-7721";

    auto handle_request = [&](std::string_view req_id) {
        std::cout << "Handling request " << req_id << "...\n";
        if (!edge_gateway.check_and_register(idempotency_key)) {
            std::cout << "  -> Rejected at GATEWAY BOUNDARY (Duplicate key in Redis/Memory)\n";
            return;
        }

        auto res = db_repo.process_order_atomically(req_id, idempotency_key);
        if (!res) {
            std::cout << "  -> Rejected at DOMAIN DB LEVEL (ACID Unique Constraint)\n";
        }
    };

    handle_request("REQ-1");
    handle_request("REQ-1-RETRY-1"); // Зрізається на межі

    return 0;
}
```
```go
// Go 1.22: Гібридна дедуплікація на межі та в домені

package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type EdgeFilter struct {
	mu    sync.Mutex
	cache map[string]time.Time
	ttl   time.Duration
}

func NewEdgeFilter(ttl time.Duration) *EdgeFilter {
	return &EdgeFilter{
		cache: make(map[string]time.Time),
		ttl:   ttl,
	}
}

func (f *EdgeFilter) Allow(key string) bool {
	f.mu.Lock()
	defer f.mu.Unlock()

	now := time.Now()
	if exp, exists := f.cache[key]; exists && exp.After(now) {
		return false // Дублікат на межі!
	}

	f.cache[key] = now.Add(f.ttl)
	return true
}

type DomainService struct {
	mu           sync.Mutex
	dbUniqueKeys map[string]bool
}

func (s *DomainService) ExecuteTransaction(ctx context.Context, orderID, key string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.dbUniqueKeys[key] {
		return fmt.Errorf("DB_UNIQUE_VIOLATION: key %s already processed", key)
	}

	s.dbUniqueKeys[key] = true
	fmt.Printf("[Domain Go] Processed order %s with key %s\n", orderID, key)
	return nil
}

func main() {
	edge := NewEdgeFilter(5 * time.Minute)
	domain := &DomainService{dbUniqueKeys: make(map[string]bool)}

	key := "IDEM-GO-1001"

	// Запит 1
	if edge.Allow(key) {
		_ = domain.ExecuteTransaction(context.Background(), "ORD-1", key)
	}

	// Запит 2 (Retry) — блокується на межі
	if !edge.Allow(key) {
		fmt.Println("[Edge Go] Blocked duplicate request at gateway boundary.")
	}
}
```
:::

## Крайові випадки та поведінка при відмовах

При проєктуванні реальних високопродуктивних систем інженер мусить враховувати такі крайові сценарії (edge cases):

1. **Мережевий партиціон до Redis (Redis Outage / Timeout):**
   Що робить Edge Gateway, якщо Redis дедуплікації відповідає з таймаутом у 50 мілісекунд?
   - **Fail-Open (Пропустити):** Шлюз ігнорує збій кешу й пропускає запит у доменний сервіс. Це захищає доступність системи (Availability), але переносить увесь шторм повторів на базу даних.
   - **Fail-Closed (Відхилити):** Шлюз повертає клієнту статус `503 Service Unavailable`. Це захищає базу даних від перевантаження, але блокує унікальні запити користувачів.
   В більшості критичних бізнес-систем застосовують схему *Fail-Open з включенням рейт-лімітингу*, довіряючи захисту доменного шару.

2. **Часткова відмова доменного воркера (Partial Worker Failure):**
   Якщо воркер обробив бізнес-операцію в БД, але впав за мілісекунду до оновлення кешу на шлюзі:
   - Кеш шлюзу лишається порожнім або в стані `In-Flight`.
   - Наступний повтор клієнта проходить шлюз і вдаряється в UNIQUE constraint бази даних.
   - Доменний сервіс перехоплює помилку `23505 (unique_violation)`, зчитує вже створене замовлення з БД та повертає успішну відповідь. Це підтверджує необхідність обов'язкової наявності дедуплікації у логіці як другого рубежу оборони.

3. **Асинхронний чищення застарілих ключів (Garbage Collection / Eviction):**
   У реалізації на C та C++ очищення застарілих ключів відбувається під час чергових викликів (`cleanup_expired`). У високонавантажених системах таке inline-очищення може викликати непропорційні затримки (latency spikes). Тому у промислових рішеннях (Redis EXPIRE, Aerospike TTL) видалення реалізується через окремі фонові потоки (active eviction) або ймовірнісне відсікання при доступі (passive eviction).
