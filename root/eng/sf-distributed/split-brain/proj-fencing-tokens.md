# ⚙️ Реалізація сервера сховища з перевіркою фенсингових токенів

Розподілене сховище не може покладатися на чесність або своєчасність клієнтів: якщо вузол-лідер вважає себе діючим, але насправді був замінений іншим лідером через таймаут зв'язку чи довгу паузу збирання сміття, його запізнілі операції запису повинні бути відхилені безпосередньо в точці збереження. Єдиний математично надійний спосіб досягти цього без апаратного знеструмлення сервера — супровід кожного запиту монотонно зростаючим токеном епохи (англ. *fencing token* або *epoch term*).

У цій практичній реалізації ми побудуємо повноцінну модель розподіленої системи, що складається з трьох ключових компонентів:
1. **Координатора кластера (англ. *Cluster Coordinator*):** сервісу консенсусу (аналог Raft / etcd), який веде облік активних лідерів, відстежує серцебиття та генерує монотонно зростаючі токени епохи під час кожного переобрання.
2. **Сервера сховища (англ. *Storage Engine Server*):** кінцевого сховища ключ-значення, яке атомарно веде облік найвищого зареєстрованого токена `max_accepted_epoch` і відхиляє будь-яку транзакцію із застарілим токеном.
3. **Клієнтських вузлів-лідерів (англ. *Leader Clients*):** процесів, що виконують бізнес-транзакції та можуть зазнавати раптових штучних пауз (емуляція тривалої паузи Garbage Collection Stop-The-World або асиметричного зависання мережевого інтерфейсу).

## Чому перевірка на боці клієнта принципово безпорадна

Найчастіша помилка архітекторів-початківців — спроба перевірити статус лідерства перед виконанням операції:

```
if (coordinator.is_leader(self)) {
    // Вузол зависає тут на 15 секунд через GC Stop-The-World...
    storage.write(key, value); // Небезпечний запис уже нелігітимного лідера!
}
```

У часовому проміжку між перевіркою `is_leader()` та безпосереднім виконанням `storage.write()` може минути довільний інтервал часу: операційна система може перемкнути контекст, віртуальна машина може потрапити під гіпервізорну міграцію, або середовище виконання може запустити збирання пам'яті. Поки лідер стоїть на паузі, координатор встигає зафіксувати таймаут, провести вибори та призначити нового лідера.

Коли старий процес прокидається, він уже не перевіряє свій статус повторно, а відразу шле підготовлений запис у мережу. Навіть якби він перевірив статус ще раз перед самим викликом системного виклику `send()`, затримка може виникнути вже всередині мережевого стека ядра, у буфері мережевої карти або в черзі комутатора дата-центру.

Отже, перевірка лідерства повинна відбуватися не *до* відправлення, а *всередині* сховища в момент атомарної модифікації стану. Сховище є останньою лінією оборони, яка володіє актуальним контекстом усього кластера.

## Архітектурний контракт і протокол обміну

Перед написанням коду визначимо чіткий протокол взаємодії та структури даних.

Кожна операція модифікації стану сховища складається з кортежу трьох полів:
- `epoch` (64-бітне беззнакове число) — порядковий номер терму лідера, отриманий від координатора;
- `key` — текстовий ідентифікатор запису (наприклад, ім'я рахунку або ключ блокування);
- `value` — нове значення, яке необхідно записати.

Під час передавання мережею заголовок запиту містить 64-бітне поле епохи у форматі прямого порядку байтів (англ. *Big-Endian / Network Byte Order*), що дозволяє апаратним мережевим картам із підтримкою eBPF або апаратного розбору протоколів відфільтровувати застарілі пакети ще на рівні мережевого адаптера (NIC) без переривання процесора.

Сервер сховища підтримує інваріант безпеки:

```
∀ req ∈ Writes:
  req.epoch ≥ storage.max_accepted_epoch ⟹ state' = apply(req), max_accepted_epoch = req.epoch, result = OK
  req.epoch < storage.max_accepted_epoch ⟹ state' = state, result = ERR_STALE_EPOCH
```

Якщо до сховища надходить запит із токеном `req.epoch`, що дорівнює або перевищує поточний `max_accepted_epoch`, сховище оновлює свій внутрішній лічильник `max_accepted_epoch = req.epoch`, фіксує нові дані в пам'яті та повертає успішний статус `STATUS_OK`.

Якщо ж токен менший за `max_accepted_epoch`, сховище відхиляє операцію з кодом помилки `ERR_STALE_EPOCH`, не змінюючи внутрішній словник даних. Клієнт, отримавши таку відповідь, розуміє: він більше не є дійсним лідером кластера і повинен негайно скласти повноваження та перейти в режим відновлення.

## Модель станів клієнта та обробка відмови

Клієнтський процес-лідер функціонує як скінченний автомат (англ. *finite state machine*), що має три основні стани:
1. **`FOLLOWER` (Очікування):** вузол стежить за серцебиттям лідера. Якщо серцебиття зникає, він подає заявку координатору на отримання нового токена.
2. **`LEADER` (Активна робота):** отримавши токен `e`, вузол приймає запити від користувачів і супроводжує кожен запис міткою `e`.
3. **`FENCED / STEPPED_DOWN` (Складання повноважень):** якщо будь-яке звернення до сховища повертає `STORAGE_ERR_STALE_EPOCH`, вузол миттєво анулює свої локальні кеші, закриває клієнтські з'єднання і переходить у стан `FOLLOWER`.

Така симетрія гарантує, що лідер ніколи не продовжує обслуговувати клієнтів після першого ж виявленого розходження з актуальним станом сховища.

## Багатопотокові інваріанти та послідовна узгодженість

У багатопотоковому сервері сховища перевірка епохи та оновлення даних повинні виконуватися атомарно. Якщо окремий потік спочатку перевірить токен, а потім відпустить блокування перед записом у геш-таблицю, виникне стан гонитви (англ. *race condition*): інший потік із вищою епохою може оновити `max_accepted_epoch` між цими двома діями.

Для захисту пам'яті використовують або глобальний м'ютекс захисту таблиці, або атомарні операції Compare-And-Swap (CAS) над 64-бітним словом епохи з бар'єрами послідовної узгодженості (`std::memory_order_seq_cst`). Кожен запис у сховищі маркується не лише часом модифікації, а й токеном епохи, що створила цей стан.

## Повний робочий приклад реалізації

Наведений нижче код демонструє роботу сховища з фенсингом, переобрання лідера координатором та успішне блокування запізнілого запису від старого завислого лідера.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ENTRIES 64
#define MAX_KEY_LEN 32
#define MAX_VAL_LEN 64

/* Коди результатів виконання операцій */
typedef enum {
    STORAGE_OK = 0,
    STORAGE_ERR_STALE_EPOCH = -1,
    STORAGE_ERR_FULL = -2,
    STORAGE_ERR_NOT_FOUND = -3
} storage_status_t;

/* Запис у сховищі ключ-значення */
typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    uint64_t last_modified_epoch;
    bool active;
} storage_entry_t;

/* Стан сервера сховища даних */
typedef struct {
    uint64_t max_accepted_epoch;
    storage_entry_t entries[MAX_ENTRIES];
    size_t count;
} storage_server_t;

/* Запит на запис від клієнта-лідера */
typedef struct {
    uint64_t epoch;
    const char *key;
    const char *value;
} write_request_t;

/* Відповідь сервера сховища */
typedef struct {
    storage_status_t status;
    uint64_t current_storage_epoch;
    const char *message;
} write_response_t;

/* Ініціалізація сервера сховища */
void storage_init(storage_server_t *server) {
    server->max_accepted_epoch = 0;
    server->count = 0;
    for (size_t i = 0; i < MAX_ENTRIES; i++) {
        server->entries[i].active = false;
    }
}

/* Атомарна обробка запиту на запис із перевіркою токена фенсингу */
write_response_t storage_write(storage_server_t *server, const write_request_t *req) {
    write_response_t res;
    
    /* Головна перевірка фенсингу: відхиляємо старі епохи */
    if (req->epoch < server->max_accepted_epoch) {
        res.status = STORAGE_ERR_STALE_EPOCH;
        res.current_storage_epoch = server->max_accepted_epoch;
        res.message = "REJECTED: Stale fencing token (epoch expired)";
        return res;
    }

    /* Оновлюємо найбільшу бачену епоху сховища */
    server->max_accepted_epoch = req->epoch;

    /* Пошук наявного ключа */
    for (size_t i = 0; i < MAX_ENTRIES; i++) {
        if (server->entries[i].active && strcmp(server->entries[i].key, req->key) == 0) {
            strncpy(server->entries[i].value, req->value, MAX_VAL_LEN - 1);
            server->entries[i].value[MAX_VAL_LEN - 1] = '\0';
            server->entries[i].last_modified_epoch = req->epoch;

            res.status = STORAGE_OK;
            res.current_storage_epoch = server->max_accepted_epoch;
            res.message = "SUCCESS: Key updated";
            return res;
        }
    }

    /* Додавання нового запису */
    for (size_t i = 0; i < MAX_ENTRIES; i++) {
        if (!server->entries[i].active) {
            strncpy(server->entries[i].key, req->key, MAX_KEY_LEN - 1);
            server->entries[i].key[MAX_KEY_LEN - 1] = '\0';
            strncpy(server->entries[i].value, req->value, MAX_VAL_LEN - 1);
            server->entries[i].value[MAX_VAL_LEN - 1] = '\0';
            server->entries[i].last_modified_epoch = req->epoch;
            server->entries[i].active = true;
            server->count++;

            res.status = STORAGE_OK;
            res.current_storage_epoch = server->max_accepted_epoch;
            res.message = "SUCCESS: Key inserted";
            return res;
        }
    }

    res.status = STORAGE_ERR_FULL;
    res.current_storage_epoch = server->max_accepted_epoch;
    res.message = "ERROR: Storage table full";
    return res;
}

/* Читання поточного значення зі сховища */
storage_status_t storage_read(const storage_server_t *server, const char *key, char *out_val, size_t max_len) {
    for (size_t i = 0; i < MAX_ENTRIES; i++) {
        if (server->entries[i].active && strcmp(server->entries[i].key, key) == 0) {
            strncpy(out_val, server->entries[i].value, max_len - 1);
            out_val[max_len - 1] = '\0';
            return STORAGE_OK;
        }
    }
    return STORAGE_ERR_NOT_FOUND;
}

/* Координатор кластера (емуляція Raft / etcd) */
typedef struct {
    uint64_t current_epoch;
    const char *current_leader_name;
} cluster_coordinator_t;

void coordinator_init(cluster_coordinator_t *coord) {
    coord->current_epoch = 0;
    coord->current_leader_name = "None";
}

/* Обрання нового лідера з монотонним збільшенням номера епохи */
uint64_t coordinator_elect_leader(cluster_coordinator_t *coord, const char *new_leader_name) {
    coord->current_epoch++;
    coord->current_leader_name = new_leader_name;
    printf("[COORDINATOR] Elected new leader '%s' with Fencing Token (Epoch) = %llu\n",
           coord->current_leader_name, (unsigned long long)coord->current_epoch);
    return coord->current_epoch;
}

int main(void) {
    printf("=== СИМУЛЯЦІЯ ЗАХИСТУ ВІД SPLIT-BRAIN ЧЕРЕЗ FENCING TOKENS ===\n\n");

    storage_server_t storage;
    storage_init(&storage);

    cluster_coordinator_t coordinator;
    coordinator_init(&coordinator);

    /* 1. Початкові вибори: Вузол 1 стає лідером */
    uint64_t leader1_token = coordinator_elect_leader(&coordinator, "Node-1");

    /* 2. Вузол 1 успішно записує дані на рахунок */
    write_request_t req1 = {
        .epoch = leader1_token,
        .key = "account:UA8842",
        .value = "balance:1000_UAH"
    };

    printf("[LEADER 1] Sending write: key='%s', val='%s', epoch=%llu\n",
           req1.key, req1.value, (unsigned long long)req1.epoch);
    write_response_t resp1 = storage_write(&storage, &req1);
    printf("[STORAGE] Status: %d, ServerEpoch: %llu, Msg: %s\n\n",
           resp1.status, (unsigned long long)resp1.current_storage_epoch, resp1.message);

    /* 3. Симуляція зависання Вузла 1 (GC Pause / мережевий обрив) */
    printf(">>> [ALARM] Node-1 frozen on GC pause (Stop-The-World)! Heartbeat lost.\n");

    /* 4. Координатор фіксує таймаут і обирає Вузол 2 новим лідером */
    uint64_t leader2_token = coordinator_elect_leader(&coordinator, "Node-2");

    /* 5. Вузол 2 записує нову транзакцію з новим токеном */
    write_request_t req2 = {
        .epoch = leader2_token,
        .key = "account:UA8842",
        .value = "balance:750_UAH"
    };

    printf("[LEADER 2] Sending write: key='%s', val='%s', epoch=%llu\n",
           req2.key, req2.value, (unsigned long long)req2.epoch);
    write_response_t resp2 = storage_write(&storage, &req2);
    printf("[STORAGE] Status: %d, ServerEpoch: %llu, Msg: %s\n\n",
           resp2.status, (unsigned long long)resp2.current_storage_epoch, resp2.message);

    /* 6. Вузол 1 прокидається після GC і намагається виконати старий запізнілий запис */
    printf(">>> [RESUME] Node-1 wakes up from GC! It still believes it is the leader.\n");
    write_request_t stale_req = {
        .epoch = leader1_token, /* Старий токен = 1 */
        .key = "account:UA8842",
        .value = "balance:500_UAH" /* Конфліктний запізнілий запис */
    };

    printf("[LEADER 1 (STALE)] Trying to write: key='%s', val='%s', epoch=%llu\n",
           stale_req.key, stale_req.value, (unsigned long long)stale_req.epoch);
    write_response_t stale_resp = storage_write(&storage, &stale_req);
    printf("[STORAGE] Status: %d, ServerEpoch: %llu, Msg: %s\n\n",
           stale_resp.status, (unsigned long long)stale_resp.current_storage_epoch, stale_resp.message);

    /* 7. Фінальна перевірка цілісності даних у сховищі */
    char final_val[MAX_VAL_LEN];
    storage_read(&storage, "account:UA8842", final_val, sizeof(final_val));
    printf("=== ПІДСУМОК: Фінальний стан у сховищі: '%s' ===\n", final_val);
    printf("Цілісність збережено: запізнілий запис відхилено завдяки фенсингу.\n");

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <cstdint>
#include <expected>
#include <memory>
#include <format>

// Коди помилок операцій зі сховищем
enum class StorageError {
    StaleEpoch,
    NotFound,
    InvalidToken
};

// Структура інформації про збережений запис
struct StorageEntry {
    std::string value;
    uint64_t last_modified_epoch;
};

// Запит на модифікацію даних із фенсинговим токеном
struct WriteRequest {
    uint64_t epoch;
    std::string_view key;
    std::string_view value;
};

// Сервер сховища ключ-значення з перевіркою епохи
class StorageServer {
public:
    StorageServer() : max_accepted_epoch_(0) {}

    // Атомарна обробка запиту на запис
    [[nodiscard]] std::expected<uint64_t, StorageError> write(const WriteRequest& req) {
        // Інваріант фенсингу: відхиляємо будь-яку епоху, меншу за max_accepted_epoch_
        if (req.epoch < max_accepted_epoch_) {
            return std::unexpected(StorageError::StaleEpoch);
        }

        // Оновлюємо найвищу зафіксовану епоху сховища
        max_accepted_epoch_ = req.epoch;

        // Зберігаємо або оновлюємо значення
        data_[std::string(req.key)] = StorageEntry{
            .value = std::string(req.value),
            .last_modified_epoch = req.epoch
        };

        return max_accepted_epoch_;
    }

    // Читання поточного значення
    [[nodiscard]] std::expected<std::string, StorageError> read(std::string_view key) const {
        auto it = data_.find(std::string(key));
        if (it == data_.end()) {
            return std::unexpected(StorageError::NotFound);
        }
        return it->second.value;
    }

    [[nodiscard]] uint64_t current_epoch() const noexcept {
        return max_accepted_epoch_;
    }

private:
    uint64_t max_accepted_epoch_;
    std::unordered_map<std::string, StorageEntry> data_;
};

// Координатор кластера, що генерує монотонні токени терму
class ClusterCoordinator {
public:
    ClusterCoordinator() : current_epoch_(0), active_leader_("None") {}

    // Вибори нового лідера з монотонним збільшенням токена
    uint64_t elect_leader(std::string_view new_leader_name) {
        ++current_epoch_;
        active_leader_ = new_leader_name;
        std::cout << std::format("[COORDINATOR] Elected new leader '{}' with Fencing Token (Epoch) = {}\n",
                                 active_leader_, current_epoch_);
        return current_epoch_;
    }

    [[nodiscard]] uint64_t current_epoch() const noexcept {
        return current_epoch_;
    }

    [[nodiscard]] std::string_view active_leader() const noexcept {
        return active_leader_;
    }

private:
    uint64_t current_epoch_;
    std::string active_leader_;
};

int main() {
    std::cout << "=== СИМУЛЯЦІЯ ЗАХИСТУ ВІД SPLIT-BRAIN ЧЕРЕЗ FENCING TOKENS (C++23) ===\n\n";

    StorageServer storage;
    ClusterCoordinator coordinator;

    // 1. Початкові вибори лідера
    const uint64_t leader1_token = coordinator.elect_leader("Node-1");

    // 2. Вузол 1 успішно записує дані на рахунок
    WriteRequest req1{
        .epoch = leader1_token,
        .key = "account:UA8842",
        .value = "balance:1000_UAH"
    };

    std::cout << std::format("[LEADER 1] Sending write: key='{}', val='{}', epoch={}\n",
                             req1.key, req1.value, req1.epoch);

    auto res1 = storage.write(req1);
    if (res1.has_value()) {
        std::cout << std::format("[STORAGE] SUCCESS: Write accepted, Current Server Epoch = {}\n\n", *res1);
    }

    // 3. Симуляція раптового зависання Вузла 1 (GC Pause)
    std::cout << ">>> [ALARM] Node-1 frozen on GC pause (Stop-The-World)! Heartbeat lost.\n";

    // 4. Координатор обирає Вузол 2 новим лідером
    const uint64_t leader2_token = coordinator.elect_leader("Node-2");

    // 5. Вузол 2 записує дані з токеном e=2
    WriteRequest req2{
        .epoch = leader2_token,
        .key = "account:UA8842",
        .value = "balance:750_UAH"
    };

    std::cout << std::format("[LEADER 2] Sending write: key='{}', val='{}', epoch={}\n",
                             req2.key, req2.value, req2.epoch);

    auto res2 = storage.write(req2);
    if (res2.has_value()) {
        std::cout << std::format("[STORAGE] SUCCESS: Write accepted, Current Server Epoch = {}\n\n", *res2);
    }

    // 6. Вузол 1 прокидається і надсилає запізнілий запис зі старим токеном e=1
    std::cout << ">>> [RESUME] Node-1 wakes up from GC! It still believes it is the leader.\n";
    WriteRequest stale_req{
        .epoch = leader1_token, // Старий токен = 1
        .key = "account:UA8842",
        .value = "balance:500_UAH" // Застаріле перезаписування
    };

    std::cout << std::format("[LEADER 1 (STALE)] Trying to write: key='{}', val='{}', epoch={}\n",
                             stale_req.key, stale_req.value, stale_req.epoch);

    auto stale_res = storage.write(stale_req);
    if (!stale_res.has_value()) {
        if (stale_res.error() == StorageError::StaleEpoch) {
            std::cout << std::format("[STORAGE] REJECTED: Stale fencing token! (ReqEpoch {} < ServerEpoch {})\n\n",
                                     stale_req.epoch, storage.current_epoch());
        }
    }

    // 7. Фінальна верифікація цілісності сховища
    auto final_value = storage.read("account:UA8842");
    if (final_value.has_value()) {
        std::cout << std::format("=== ПІДСУМОК: Фінальний стан у сховищі: '{}' ===\n", *final_value);
    }
    std::cout << "Цілісність збережено: запізнілий запис відхилено завдяки фенсингу.\n";

    return 0;
}
```
:::

## Покроковий аналіз виконання програми

Погляньмо на консольний вивід наведеного вище коду, щоб простежити кожну стадію захисту від розщеплення:

```
=== СИМУЛЯЦІЯ ЗАХИСТУ ВІД SPLIT-BRAIN ЧЕРЕЗ FENCING TOKENS ===

[COORDINATOR] Elected new leader 'Node-1' with Fencing Token (Epoch) = 1
[LEADER 1] Sending write: key='account:UA8842', val='balance:1000_UAH', epoch=1
[STORAGE] Status: 0, ServerEpoch: 1, Msg: SUCCESS: Key inserted

>>> [ALARM] Node-1 frozen on GC pause (Stop-The-World)! Heartbeat lost.
[COORDINATOR] Elected new leader 'Node-2' with Fencing Token (Epoch) = 2
[LEADER 2] Sending write: key='account:UA8842', val='balance:750_UAH', epoch=2
[STORAGE] Status: 0, ServerEpoch: 2, Msg: SUCCESS: Key updated

>>> [RESUME] Node-1 wakes up from GC! It still believes it is the leader.
[LEADER 1 (STALE)] Trying to write: key='account:UA8842', val='balance:500_UAH', epoch=1
[STORAGE] Status: -1, ServerEpoch: 2, Msg: REJECTED: Stale fencing token (epoch expired)

=== ПІДСУМОК: Фінальний стан у сховищі: 'balance:750_UAH' ===
Цілісність збережено: запізнілий запис відхилено завдяки фенсингу.
```

Зверніть увагу на ключові моменти, що захистили стан рахунку:
1. **Перший запис лідера 1:** Сервер сховища стартував із нульовою епохою. Запит із токеном `epoch=1` був прийнятий, а лічильник сховища `max_accepted_epoch` перейшов у стан `1`.
2. **Пауза та перевибори:** Поки вузол 1 завис у пам'яті, координатор законно збільшив терм до `2` та видав цей токен вузлу 2.
3. **Запис лідера 2:** Вузол 2 звернувся до сховища з `epoch=2`. Оскільки `2 > 1`, сховище підтвердило актуальність нового лідера, записало залишок `750_UAH` і підняло планку `max_accepted_epoch` до `2`.
4. **Запізнілий запис лідера 1:** Коли вузол 1 прокинувся, він не мав жодної можливості дізнатися, що в кластері відбулися вибори, адже його локальний стан не оновлювався. Він надіслав запит зі своїм старим токеном `epoch=1`.
5. **Невідворотне відсікання:** Сховище порівняло `1` проти `2` і повернуло помилку `STORAGE_ERR_STALE_EPOCH`. Небезпечне перезаписування балансу на `500_UAH` було відвернено.

## Зв'язок із реальними розподіленими протоколами

Наведена спрощена модель токенів безпосередньо відображає роботу промислових систем консенсусу:

- **ZooKeeper zxid:** 64-бітне число `zxid` складається з двох частин: старші 32 біти — це номер епохи виборів майстра (`epoch`), а молодші 32 біти — монотонний лічильник транзакцій усередині цієї епохи. Будь-який запит від старого лідера, що містить меншу епоху, відкидається послідовниками на стадії верифікації пакета.
- **Raft Term:** у протоколі Raft кожен RPC-пакет (`AppendEntries` або `RequestVote`) обов'язково несе номер поточного терму `term`. Якщо отримувач бачить повідомлення із термом, меншим за його власний збережений терм, запит негайно відхиляється. Якщо ж сервер виявляє у вхідному пакеті терм, *більший* за власний, він миттєво складає повноваження лідера і стає простим фоловером.
- **etcd Raft Index та Lease ID:** у etcd блокування (ключі з TTL) прив'язуються до монотонно зростаючого номеру ревізії `header.revision`. Клієнт передає цю ревізію у транзакційних умовах (англ. *compare-and-swap*).
- **PostgreSQL Patroni DCS Revision:** Patroni зберігає ключ лідера у etcd/Consul разом із номером ревізії. Якщо вузол втрачає зв'язок і ревізія змінюється іншим сервером, локальний демон Patroni негайно переводить PostgreSQL у режим «тільки для читання» (`pg_ctl promote / demote`) та викликає сторожовий таймер.

## Як інтегрувати фенсинг у реляційні та документоорієнтовані СУБД

Якщо ви використовуєте готову базу даних (PostgreSQL, MySQL, DynamoDB, MongoDB), вам не потрібно писати власний мережевий сервер із нуля. Фенсинг можна реалізувати на рівні схеми даних та умовних SQL-виразів:

**1. Оптимістичний фенсинг в SQL (Conditional Update):**
У таблицю бізнес-сутності додається колонка `last_fencing_epoch BIGINT`. Кожен запис лідера супроводжується перевіркою:

```sql
UPDATE accounts
SET balance = balance - 250,
    last_fencing_epoch = :current_leader_epoch
WHERE account_id = 'UA8842'
  AND last_fencing_epoch <= :current_leader_epoch;
```

Якщо запізнілий лідер надішле старий `epoch`, умова `WHERE` поверне `0 rows affected`. Клієнтський шар виявляє нульову кількість оновлених рядків, фіксує конфлікт епохи та відкочує транзакцію.

**2. Умовні вирази в NoSQL (DynamoDB Condition Expressions):**
У Amazon DynamoDB операція `PutItem` або `UpdateItem` підтримує параметр `ConditionExpression`:

```
ConditionExpression: "attribute_not_exists(fencing_epoch) OR fencing_epoch <= :epoch"
```

Якщо інший вузол уже записав документ із вищим значенням `fencing_epoch`, DynamoDB атомарно повертає помилку `ConditionalCheckFailedException`, запобігаючи перезапису свіжих даних старими.

## Мережевий бінарний протокол: як фенсинг виглядає на дроті

У реальних мережевих сховищах (наприклад, Apache BookKeeper або Ceph OSD) запит на модифікацію даних упаковується у двійковий фрейм фіксованого формату. Заголовок кожного TCP-пакета містить службові поля, які парсер мережевого демона читає ще до виділення пам'яті під тіло запиту:

```
+---------------+---------------+-----------------------+---------------+
| Magic (4B)    | Version (2B)  | Epoch / Term (8B)     | OpCode (2B)   |
| 0x53504C54    | 0x0001        | 0x000000000000002A    | 0x0001 (WRITE)|
+---------------+---------------+-----------------------+---------------+
| Key Length    | Val Length    | Request ID (8B)       | Payload CRC32 |
| (2B)          | (4B)          | 0x1A2B3C4D5E6F7081    | (4B)          |
+---------------+---------------+-----------------------+---------------+
| Key Data (Key Length байтів)  | Value Data (Val Length байтів)        |
+-------------------------------+---------------------------------------+
```

Коли демон сховища вичитує перші 16 байтів фрейму із сокета, він миттєво витягує поле `Epoch`. Якщо `Epoch < max_accepted_epoch`, сервер навіть не вичитує залишок корисного навантаження (англ. *payload*) із сокета, а негайно повертає короткий пакет помилки та закриває TCP-з'єднання. Це захищає сховище не лише від логічного розщеплення, а й від перевантаження пам'яті запізнілим трафіком мертвого лідера.

## Ідемпотентність повторів: триплет (Client, Request, Epoch)

Фенсинговий токен захищає від конфлікту між старим і новим лідером, але сам по собі не захищає від дублювання запитів від одного й того самого чинного лідера під час мережевих повторів (англ. *retries*).

Якщо мережевий пакет підтвердження від сховища загубився дорогою до лідера, клієнт повторно надішле той самий запит із тим самим номером епохи `e`. Оскільки `e == max_accepted_epoch`, сховище сприйме запит як новий і повторно виконає операцію (наприклад, спише гроші вдруге).

Для досягнення суворої лінеаризовності (англ. *strict linearizability*) сховище повинно перевіряти комбінований триплет:
1. `epoch` — перевірка легітимності лідера серед інших лідерів кластера;
2. `client_id` — ідентифікатор клієнтської сесії;
3. `request_id` (або `sequence_number`) — монотонний номер запиту в межах даної сесії.

Сховище зберігає таблицю останніх відповідей для кожного активного `client_id`. Якщо надходить запит із чинним токеном `epoch`, але вже обробленим `request_id`, сховище повертає збережений раніше результат без повторного виконання модифікації стану.

## Пакетні транзакції та атомарний багатоключовий фенсинг

Коли бізнес-операція охоплює не один ключ, а цілий набір записів у різних шардах або таблицях (англ. *multi-partition batch write*), одного скалярного порівняння стає недостатньо. Якщо під час оновлення трьох ключів перші два оновляться з `epoch = 1`, а третій ключ поверне `STORAGE_ERR_STALE_EPOCH` через те, що інший лідер уже записав туди `epoch = 2`, виникає часткове застосування транзакції (англ. *partial write*).

Для запобігання цьому використовують двофазну фіксацію (2PC) або протокол підготовки зі спільним токеном:
1. **Фаза Prepare:** лідер надсилає всім залученим шардам команду `PREPARE(tx_id, epoch, keys)`. Кожен шард атомарно перевіряє умову `epoch >= max_accepted_epoch`, тимчасово блокує ключі від записів із меншою епохою та оновлює `max_accepted_epoch = epoch`.
2. **Фаза Commit:** лише якщо всі шарди успішно відповіли `PREPARE_OK`, лідер розсилає команду `COMMIT(tx_id, epoch)`. Якщо хоча б один шард відхилив підготовку через застарілий токен, вся транзакція миттєво відкочується (`ABORT`).

## Тестування фенсингу: ін'єкція збоїв та верифікація за Jepsen

Надійність механізму фенсингу неможливо гарантувати простими модульними тестами, адже стан гонитви виникає лише під недетермінованим мережевим навантаженням.

Для повної верифікації реалізації застосовують інструменти фаззингу та ін'єкції збоїв (зокрема фреймворк Jepsen Кайла Кінгсбері, відомого під псевдонімом *aphyr*):
- **Штучні мережеві розділення (`iptables -A INPUT -s ... -j DROP`):** створення асиметричних та симетричних мережевих ізоляцій на рівні ядра операційної системи.
- **Призупинення процесів (`kill -STOP` та `kill -CONT`):** імітація довгих пауз JVM або Kernel I/O stall тривалістю від 5 до 60 секунд.
- **Дрейф часу (`chrony / ntpd chaos`):** штучне переведення годинників уперед і назад на випадкову величину.
- **Втрата дисків та емуляція збоїв контролерів:** моделювання раптового перезавантаження сервера сховища за допомогою ін'єкції збоїв введення-виведення на рівні драйвера блокового пристрою (DM-Flakey / SCSI fault injection).

Тест вважається пройденим лише тоді, коли аналізатор історії операцій Кніра (англ. *Knossos linearizability checker*) підтверджує, що для кожного ключа існує єдиний лінійний послідовний порядок переходів стану, у якому жоден запис від старого лідера не затер результат запису нового лідера. Будь-яке розходження в історії транзакцій трактується як критична аварія цілісності.

## Типові архітектурні пастки та їх розв'язання

Впровадження фенсингових токенів на практиці стикається з кількома підступними крайовими випадками, які вимагають суворої дисципліни проєктування:

**1. Частковий запис до кількох сховищ (Dual-Write Hazard).**
Якщо транзакція лідера повинна оновити одночасно реляційну базу даних та чергу Kafka, відхилення токена в базі не відкликає автоматично повідомлення, вже надіслане в чергу. Розв'язанням є використання патерна Transactional Outbox: повідомлення до черги записуються в ту саму таблицю бази даних під захистом того самого фенсингового токена в межах однієї ACID-транзакції. Окремий фоновий процес (CDC) вичитує журнал бази та пересилає події в Kafka, гарантуючи, що жодне повідомлення від мертвого лідера не вийде назовні.

**2. Переповнення лічильника епохи (Epoch Overflow).**
Використання 32-бітного лічильника для токенів створює небезпеку обнулення (англ. *wraparound*) після 2³² виборів або перезапусків, після чого новий лідер отримає токен `0`, що буде меншим за старий `4294967295`. Використання 64-бітного беззнакового цілого числа (`uint64_t`) повністю знімає цю загрозу: навіть за 1000 переобрань лідера на секунду лічильник вичерпається лише через 584 мільйони років безперервної роботи.

**3. Збереження максимального токена на диск (Crash Recovery).**
Якщо сам сервер сховища перезавантажиться після аварії живлення, він не має права скидати `max_accepted_epoch` у нуль, інакше старий лідер зі старим токеном зможе пошкодити відновлений стан. Поточний максимальний токен епохи повинен скидатися на енергонезалежний накопичувач (SSD/WAL) у складі кожного запису перед поверненням підтвердження клієнту (`fsync`).

**4. Асинхронний дрейф годинників і таймаути сокетів.**
Фенсинговий токен не залежить від системного годинника `gettimeofday()`, оскільки є логічним лічильником послідовності. Це робить його невразливим до стрибків NTP або переведення годинників на літній час, що вирізняє токени серед усіх часових механізмів відсікання. Логічний порядок транзакцій визначається виключно відношенням «сталося раніше» (англ. *happens-before*).
