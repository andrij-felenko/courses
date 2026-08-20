# ⚙️ Практична реалізація сховища з валідацією токенів огорожі

Цей проект демонструє закінчену інженерну реалізацію розподіленої огорожі (англ. *fencing*): координатор блокувань із генератором монотонних епох, клієнтський агент із моделюванням асинхронної паузи та кінцеве сховище з бар'єром валідації токенів.

## Призначення та архітектура системи

У практичній розробці розподілених систем найважче відтворювати баги, пов'язані з непередбачуваними затримками виконання. Коли процес зависає через збирач сміття (GC) або витіснення в пам'ять підкачки (swap), локальні таймери перестають відповідати фізичній дійсності. Цей симулятор створює контрольоване середовище, у якому наочно видно, як саме токени огорожі захищають спільний стан від руйнування зомбі-процесами.

Система складається з трьох ключових вузлів:

```
                      [ Координатор замків ]
                      (LockCoordinator)
                      - token_generator = 0 -> 1 -> 2
                      - lease_deadline
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
     ┌──────────────┐                  ┌──────────────┐
     │  Воркер A    │                  │  Воркер B    │
     │  (Клієнт 1)  │                  │  (Клієнт 2)  │
     │  token = 1   │                  │  token = 2   │
     │  [GC-ПАУЗА]  │                  │  [АКТИВНИЙ]  │
     └──────────────┘                  └──────────────┘
            │                                 │
   4. write(token=1, $3000)          3. write(token=2, $6500)
      (запізнілий запис)                (своєчасний запис)
            │                                 │
            └────────────────┬────────────────┘
                             ▼
                 ┌───────────────────────┐
                 │    Спільне сховище    │
                 │    (FencedStorage)    │
                 │ highest_token_seen: 2 │
                 │                       │
                 │ T=2 >= 0 -> ПРИЙНЯТО  │
                 │ T=1 <  2 -> ВІДХИЛЕНО │
                 └───────────────────────┘
```

1. **Координатор розподілених замків (`LockCoordinator`)**:
   * Зберігає ідентифікатор поточного власника замка, дедлайн активної лізи та монотонний лічильник поколінь `token_generator`.
   * Для вимірювання інтервалів використовує виключно монотонний системний таймер, захищений від стрибків настінного часу.
   * Під час кожної видачі замка атомарно інкрементує номер епохи, гарантуючи умову строгого монотонного зростання: `token_{n+1} > token_n`.

2. **Спільне сховище даних (`FencedStorage`)**:
   * Зберігає прикладний ресурс (у прикладі — грошовий баланс рахунку) та метадані найвищого побаченого токена `highest_token_seen`.
   * Забезпечує потокобезпечність операцій через м'ютекси.
   * Виступає остаточним арбітром: якщо токен у запиті менший за `highest_token_seen`, сховище відхиляє операцію, запобігаючи незворотному пошкодженню даних.

3. **Клієнтські воркери (`Worker-A` та `Worker-B`)**:
   * Отримують лізу від координатора.
   * Читають поточний стан, планують транзакцію та відправляють оновлення разом із токеном.
   * `Worker-A` штучно призупиняється на час, що перевищує TTL лізи, моделюючи поведінку процесу-зомбі.

---

## Повна реалізація мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#if defined(_WIN32)
#include <windows.h>
static void sleep_ms(uint32_t ms) { Sleep(ms); }
#else
#include <unistd.h>
static void sleep_ms(uint32_t ms) { usleep(ms * 1000); }
#endif

/* ── 1. Монотонний таймер мілісекунд ─────────────────────────────────────── */
static uint64_t get_time_ms(void) {
#if defined(_WIN32)
    static LARGE_INTEGER freq;
    static int init = 0;
    if (!init) {
        QueryPerformanceFrequency(&freq);
        init = 1;
    }
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (uint64_t)((counter.QuadPart * 1000) / freq.QuadPart);
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
#endif
}

/* ── 2. Координатор розподілених замків ───────────────────────────────────── */
typedef struct {
    char     current_owner[32];
    uint64_t current_token;
    uint64_t lease_deadline_ms;
    uint64_t token_generator;
} LockCoordinator;

typedef struct {
    bool     granted;
    uint64_t token;
    uint64_t ttl_ms;
} LockGrant;

void coordinator_init(LockCoordinator* c) {
    c->current_owner[0] = '\0';
    c->current_token = 0;
    c->lease_deadline_ms = 0;
    c->token_generator = 0;
}

LockGrant coordinator_acquire(LockCoordinator* c, const char* client_id, uint64_t ttl_ms) {
    uint64_t now = get_time_ms();
    LockGrant grant = { .granted = false, .token = 0, .ttl_ms = 0 };

    /* Якщо замок вільний або попередня ліза спливла */
    if (c->current_owner[0] == '\0' || now >= c->lease_deadline_ms) {
        c->token_generator++; /* Атомарний інкремент монотонного лічильника епохи */
        c->current_token = c->token_generator;
        strncpy(c->current_owner, client_id, sizeof(c->current_owner) - 1);
        c->current_owner[sizeof(c->current_owner) - 1] = '\0';
        c->lease_deadline_ms = now + ttl_ms;

        grant.granted = true;
        grant.token = c->current_token;
        grant.ttl_ms = ttl_ms;

        printf("[КООРДИНАТОР] Замок надано '%s' | Токен: %llu | TTL: %llu мс\n",
               client_id, (unsigned long long)grant.token, (unsigned long long)ttl_ms);
    } else {
        printf("[КООРДИНАТОР] Запит від '%s' ВІДХИЛЕНО: замок утримує '%s' (ще %llu мс)\n",
               client_id, c->current_owner, (unsigned long long)(c->lease_deadline_ms - now));
    }
    return grant;
}

/* ── 3. Захищене сховище з валідацією токенів ────────────────────────────── */
typedef struct {
    int64_t  balance;
    uint64_t highest_token_seen;
    uint64_t total_writes;
    uint64_t stale_rejections;
} FencedStorage;

typedef enum {
    WRITE_ACCEPTED,
    WRITE_REJECTED_STALE
} WriteResult;

void storage_init(FencedStorage* s, int64_t initial_balance) {
    s->balance = initial_balance;
    s->highest_token_seen = 0;
    s->total_writes = 0;
    s->stale_rejections = 0;
}

WriteResult storage_write(FencedStorage* s, const char* client_id,
                          uint64_t token, int64_t new_balance) {
    printf("[СХОВИЩЕ] Запит від '%s' | Токен: %llu | Новий баланс: $%lld | Найвищий відомий: %llu\n",
           client_id, (unsigned long long)token, (long long)new_balance,
           (unsigned long long)s->highest_token_seen);

    /* Головний інваріант огорожі: перевірка монотонності */
    if (token >= s->highest_token_seen) {
        s->highest_token_seen = token;
        s->balance = new_balance;
        s->total_writes++;
        printf("[СХОВИЩЕ] -> УСПІХ: токен %llu >= %llu. Баланс оновлено до $%lld\n",
               (unsigned long long)token, (unsigned long long)s->highest_token_seen,
               (long long)s->balance);
        return WRITE_ACCEPTED;
    } else {
        s->stale_rejections++;
        printf("[СХОВИЩЕ] -> ВІДХИЛЕНО (ОГОРОЖА): токен %llu < %llu! Застарілий запис відкинуто.\n",
               (unsigned long long)token, (unsigned long long)s->highest_token_seen);
        return WRITE_REJECTED_STALE;
    }
}

/* ── 4. Демонстраційний сценарій відтворення збою ────────────────────────── */
int main(void) {
    LockCoordinator coordinator;
    FencedStorage storage;

    coordinator_init(&coordinator);
    storage_init(&storage, 5000); /* Початковий баланс: $5000 */

    printf("=== СТАРТ СИМУЛЯЦІЇ РОЗПОДІЛЕНОЇ ОГОРОЖІ ===\n");
    printf("Початковий баланс у сховищі: $%lld\n\n", (long long)storage.balance);

    /* Крок 1: Воркер A бере замок на 300 мс і отримує токен 1 */
    printf("--- Крок 1: Воркер A бере замок ---\n");
    LockGrant grant_a = coordinator_acquire(&coordinator, "Worker-A", 300);
    if (!grant_a.granted) {
        printf("Помилка захоплення замка Воркером A\n");
        return 1;
    }

    /* Крок 2: Воркер A готує транзакцію (списання $2000), але засинає на 500 мс (GC-пауза) */
    printf("\n--- Крок 2: Воркер A засинає в GC-паузі на 500 мс (ліза спливає на 300 мс) ---\n");
    int64_t prepared_balance_a = storage.balance - 2000; /* $5000 - $2000 = $3000 */
    sleep_ms(500);

    /* Крок 3: Воркер B бачить, що ліза A спливла, перехоплює замок і отримує токен 2 */
    printf("\n--- Крок 3: Воркер B перехоплює замок після спливання лізи A ---\n");
    LockGrant grant_b = coordinator_acquire(&coordinator, "Worker-B", 300);
    if (!grant_b.granted) {
        printf("Помилка захоплення замка Воркером B\n");
        return 1;
    }

    /* Крок 4: Воркер B успішно поповнює баланс на $1500 ($5000 + $1500 = $6500) */
    printf("\n--- Крок 4: Воркер B записує новий баланс $6500 із токеном 2 ---\n");
    int64_t new_balance_b = storage.balance + 1500;
    WriteResult res_b = storage_write(&storage, "Worker-B", grant_b.token, new_balance_b);
    if (res_b != WRITE_ACCEPTED) {
        printf("Помилка запису Воркера B\n");
        return 1;
    }

    /* Крок 5: Воркер A прокидається після GC-паузи і відправляє свій застарілий запис $3000 */
    printf("\n--- Крок 5: Воркер A прокидається і надсилає застарілий запис $3000 із токеном 1 ---\n");
    WriteResult res_a = storage_write(&storage, "Worker-A", grant_a.token, prepared_balance_a);

    /* Перевірка результатів */
    printf("\n=== ПІДСУМКИ ТЕСТУ ===\n");
    printf("Фінальний баланс у базі: $%lld (Очікується: $6500)\n", (long long)storage.balance);
    printf("Кількість відхилених застарілих записів: %llu (Очікується: 1)\n",
           (unsigned long long)storage.stale_rejections);

    if (storage.balance == 6500 && storage.stale_rejections == 1) {
        printf(">>> РЕЗУЛЬТАТ: УСПІХ! Токен огорожі врятував дані від затирання. <<<\n");
    } else {
        printf(">>> РЕЗУЛЬТАТ: ВАДА! Дані пошкоджено. <<<\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <optional>
#include <cstdint>
#include <mutex>

namespace distributed {

// ── 1. Результати операцій ──────────────────────────────────────────────────
enum class FencingStatus {
    Accepted,
    RejectedStaleToken
};

struct LockGrant {
    bool        granted{false};
    uint64_t    fencing_token{0};
    std::chrono::milliseconds ttl{0};
};

// ── 2. Координатор блокувань ────────────────────────────────────────────────
class LockCoordinator {
public:
    LockGrant acquire(std::string_view client_id, std::chrono::milliseconds ttl) {
        std::unique_lock lock(mutex_);
        auto now = std::chrono::steady_clock::now();

        if (owner_.empty() || now >= lease_deadline_) {
            current_token_ = ++token_counter_; // Монотонне зростання епохи
            owner_ = client_id;
            lease_deadline_ = now + ttl;

            std::cout << "[КООРДИНАТОР] Замок надано '" << client_id
                      << "' | Токен: " << current_token_
                      << " | TTL: " << ttl.count() << " мс\n";

            return LockGrant{
                .granted = true,
                .fencing_token = current_token_,
                .ttl = ttl
            };
        }

        auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(lease_deadline_ - now);
        std::cout << "[КООРДИНАТОР] Відмова для '" << client_id
                  << "': зайнято '" << owner_ << "' (ще " << remaining.count() << " мс)\n";

        return LockGrant{.granted = false};
    }

private:
    std::mutex mutex_;
    std::string owner_;
    uint64_t current_token_{0};
    uint64_t token_counter_{0};
    std::chrono::steady_clock::time_point lease_deadline_{};
};

// ── 3. Захищене сховище даних ───────────────────────────────────────────────
class FencedStorage {
public:
    explicit FencedStorage(int64_t initial_balance)
        : balance_(initial_balance) {}

    FencingStatus write(std::string_view client_id, uint64_t token, int64_t new_balance) {
        std::unique_lock lock(mutex_);

        std::cout << "[СХОВИЩЕ] Запит від '" << client_id
                  << "' | Токен: " << token
                  << " | Новий баланс: $" << new_balance
                  << " | Найвищий відомий: " << highest_token_seen_ << "\n";

        if (token >= highest_token_seen_) {
            highest_token_seen_ = token;
            balance_ = new_balance;
            ++total_writes_;
            std::cout << "[СХОВИЩЕ] -> УСПІХ: токен " << token << " >= "
                      << highest_token_seen_ << ". Баланс = $" << balance_ << "\n";
            return FencingStatus::Accepted;
        }

        ++stale_rejections_;
        std::cout << "[СХОВИЩЕ] -> ВІДХИЛЕНО (ОГОРОЖА): токен " << token
                  << " < " << highest_token_seen_ << "! Застарілий запис відкинуто.\n";
        return FencingStatus::RejectedStaleToken;
    }

    [[nodiscard]] int64_t balance() const {
        std::unique_lock lock(mutex_);
        return balance_;
    }

    [[nodiscard]] uint64_t stale_rejections() const {
        std::unique_lock lock(mutex_);
        return stale_rejections_;
    }

private:
    mutable std::mutex mutex_;
    int64_t balance_{0};
    uint64_t highest_token_seen_{0};
    uint64_t total_writes_{0};
    uint64_t stale_rejections_{0};
};

} // namespace distributed

// ── 4. Запуск сценарію тестування ───────────────────────────────────────────
int main() {
    using namespace std::chrono_literals;

    distributed::LockCoordinator coordinator;
    distributed::FencedStorage storage(5000); // Початковий баланс: $5000

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ РОЗПОДІЛЕНОЇ ОГОРОЖІ (C++) ===\n";
    std::cout << "Початковий баланс: $" << storage.balance() << "\n\n";

    // 1. Воркер A бере замок на 300 мс
    std::cout << "--- Крок 1: Воркер A бере замок ---\n";
    auto grant_a = coordinator.acquire("Worker-A", 300ms);
    if (!grant_a.granted) return 1;

    // 2. Воркер A планує списати $2000, але потрапляє в GC-паузу на 500 мс
    std::cout << "\n--- Крок 2: Воркер A засинає в GC-паузі на 500 мс (ліза 300 мс спливає) ---\n";
    int64_t prepared_a = storage.balance() - 2000;
    std::this_thread::sleep_for(500ms);

    // 3. Воркер B перехоплює замок після спливання лізи A
    std::cout << "\n--- Крок 3: Воркер B перехоплює замок ---\n";
    auto grant_b = coordinator.acquire("Worker-B", 300ms);
    if (!grant_b.granted) return 1;

    // 4. Воркер B успішно записує $6500 з токеном 2
    std::cout << "\n--- Крок 4: Воркер B записує баланс $6500 із токеном 2 ---\n";
    int64_t balance_b = storage.balance() + 1500;
    auto res_b = storage.write("Worker-B", grant_b.fencing_token, balance_b);
    if (res_b != distributed::FencingStatus::Accepted) return 1;

    // 5. Воркер A прокидається і надсилає застарілий запис $3000 з токеном 1
    std::cout << "\n--- Крок 5: Воркер A прокидається і надсилає запис із токеном 1 ---\n";
    auto res_a = storage.write("Worker-A", grant_a.fencing_token, prepared_a);

    // Підсумки
    std::cout << "\n=== ПІДСУМКИ ТЕСТУ ===\n";
    std::cout << "Фінальний баланс: $" << storage.balance() << " (Очікується: $6500)\n";
    std::cout << "Відхилено застарілих записів: " << storage.stale_rejections() << " (Очікується: 1)\n";

    if (storage.balance == 6500 && storage.stale_rejections == 1) {
        std::cout << ">>> РЕЗУЛЬТАТ: УСПІХ! Огорожа зберегла стан сховища. <<<\n";
    } else {
        std::cout << ">>> РЕЗУЛЬТАТ: ВАДА! Дані було пошкоджено. <<<\n";
    }

    return 0;
}
```
:::

---

## Покроковий розбір виконання

### Фаза 1: Первинне захоплення замка
`Worker-A` звертається до координатора із запитом на взяття лізи тривалістю `300 мс`.
1. Координатор перевіряє стан: активного власника немає (`owner_.empty() == true`).
2. Координатор інкрементує лічильник епохи: `token_counter_` стає рівним `1`.
3. Фіксується дедлайн оренди: `lease_deadline_ = now + 300 мс`.
4. `Worker-A` отримує підтвердження `granted = true` та токен огорожі `1`.

### Фаза 2: Виникнення асинхронної паузи
`Worker-A` читає початковий стан сховища (баланс `$5000`), планує операцію списання `$2000` (підготовлений новий баланс `$3000`) і потрапляє в штучну паузу на `500 мс` (`sleep_ms(500)` або `std::this_thread::sleep_for(500ms)`).
* На `300-й мілісекунді` ліза на координаторі вичерпується. З точки зору координатора, `Worker-A` вважається відсутнім, а ресурс — повністю вільним.
* Сам `Worker-A` нічого про це не знає, оскільки його потік виконання фізично зупинено планувальником або збирачем сміття.

### Фаза 3: Перехоплення володіння новим клієнтом
На `500-й мілісекунді` до координатора звертається `Worker-B`:
1. Координатор бачить, що дедлайн попередньої лізи минув (`now >= lease_deadline_`).
2. Генерується наступний токен епохи: `token_counter_` збільшується до `2`.
3. `Worker-B` стає новим законним власником замка і дістає токен `2`.
4. `Worker-B` зчитує актуальний баланс `$5000`, додає суму поповнення `$1500` і відправляє у сховище запис `$6500` із токеном `2`.
5. Сховище порівнює токен із локальним максимумом: умова `2 >= 0` виконується. Сховище фіксує значення `balance = $6500` та запам'ятовує новий поріг огорожі: `highest_token_seen = 2`.

### Фаза 4: Атака зомбі-процесу та спрацьовування бар'єра
`Worker-A` прокидається після завершення паузи:
1. Потік продовжує виконання з того самого рядка, де був зупинений, і відправляє свій заздалегідь обчислений баланс `$3000` із токеном `1`.
2. Сховище перевіряє інваріант:
```text
token_req < highest_token_seen
1 < 2 -> ІСТИНА (спроба застарілого запису)
```
3. Сховище блокує мутацію, збільшує лічильник `stale_rejections_` і повертає статус `RejectedStaleToken`.
4. Баланс `$6500`, записаний `Worker-B`, залишається незмінним. Безпека даних збережена.

---

## Інженерні особливості реалізації

1. **Монотонний таймер замість настінного часу**:
   У реалізації на C застосовано `QueryPerformanceCounter` для Windows та `clock_gettime(CLOCK_MONOTONIC)` для Linux. У C++ використовується `std::chrono::steady_clock`. На відміну від `std::chrono::system_clock` або функції `gettimeofday()`, монотонний таймер фізично не може піти назад під час коригувань демоном NTP або синхронізації часу віртуальної машини.

2. **Ідіоматичність C++ версії**:
   C++ версія не є простим переписуванням C-коду. Вона використовує:
   * Типізовані часові інтервали `std::chrono::milliseconds` замість «магічних» цілих чисел.
   * `std::string_view` для уникнення зайвого копіювання рядків при передачі ідентифікаторів клієнтів.
   * RAII-блокування `std::unique_lock<std::mutex>`, що гарантує своєчасне звільнення м'ютекса навіть у разі виникнення виключень.
   * Сильні переліки `enum class FencingStatus` замість сирих цілих кодів помилок.

3. **Реакція клієнта на відхилення**:
   Отримання статусу `RejectedStaleToken` є сигналом для клієнта про те, що він втратив право власності на ресурс під час обробки. Коректний клієнт повинен скасувати транзакцію, очистити локальний кеш і, за необхідності, перезапустити всю бізнес-операцію від самого початку.

4. **Тестування надійності та Chaos Engineering**:
   Для перевірки стійкості реальної розподіленої системи в конвеєрах інтеграційного тестування (CI/CD) застосовують ін'єкцію штучних затримок (*fault injection*). Мікросервіси воркерів запускаються під навантаженням із випадковими викликами команди `SIGSTOP` / `SIGCONT` через утиліти Chaos Mesh або Toxiproxy. Якщо бодай один тест фіксує пошкодження кінцевого стану без виникнення помилки `RejectedStaleToken`, це свідчить про наявність дірки в контракті валідації сховища.

5. **Адаптація до розподіленої мережі**:
   Для перетворення цього прикладу на промисловий розподілений сервіс:
   * Локальний `LockCoordinator` замінюється клієнтом до etcd або ZooKeeper, де токен отримується через транзакційну ревізію `etcdctl txn` або послідовний ephemeral-вузол ZooKeeper (`cversion` / `zxid`).
   * Локальне `FencedStorage` замінюється кластерною СКБД з умовними виразами `UPDATE ... WHERE token <= :req_token` або NoSQL-сховищем із підтримкою умовних операцій.
   * Клієнтська бібліотека огорожі огортається у прозорий проксі-драйвер бази даних, який автоматично додає отриманий токен до кожного генерованого SQL-запиту, звільняючи прикладних розробників від ручного прокидання аргументів у кожен метод.
