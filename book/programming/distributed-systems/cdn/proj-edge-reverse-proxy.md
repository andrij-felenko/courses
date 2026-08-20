# ⚙️ Реалізація периферійного кешувального проксі з механізмом Request Coalescing

Робоча реалізація високопродуктивного периферійного кешувального проксі-сервера (Edge Reverse Proxy) мовами C та C++ демонструє архітектуру усунення «шторму запитів» (Cache Stampede) через механізм згортання паралельних запитів (Request Coalescing / Single-Flight): коли сотні клієнтів одночасно звертаються за холодним ресурсом, до сервера-джерела виконується рівно один вихідний запит, а його результат транслюється всім очікуючим клієнтам.

---

### Архітектурний виклик: проблема паралельних промахів

У високонавантажених системах критичною точкою відмови є момент закінчення терміну життя кешу (TTL Expiry) для популярного ресурсу. Якщо сторінку або фрагмент відео запитують 10 000 клієнтів за секунду, то в першу ж мілісекунду після інвалідації або видалення запису з пам'яті всі 10 000 паралельних потоків одночасно фіксують стан Cache MISS.

Без спеціального механізму координації кожен із цих потоків ініціює окреме з'єднання до сервера-джерела (Origin). Це спричиняє лавиноподібне перевантаження центральної бази даних, вичерпання пулу з'єднань бекенда та деградацію часу відповіді для всієї інфраструктури (явище Thundering Herd). 

Центральний сервер починає витрачати всі процесорні ресурси на обробку однотипних запитів, черги TCP-сокетів переповнюються, і система зазнає відмови типу каскадного колапсу.

---

### Архітектурне рішення: патерн Single-Flight (Request Collapsing)

Механізм згортання запитів базується на відстеженні активних мережевих операцій у реальному часі за допомогою таблиці запитів у польоті (`inflight_map`):

1. **Нормалізація та обчислення ключа:** Проксі очищує URI від зайвих параметрів сортування, нормалізує регістр літер та обчислює унікальний хеш-ключ ресурсу.
2. **Перевірка локального кешу:**
   * Якщо знайдено валідний запис із невичерпаним TTL (Cache HIT), дані негайно повертаються клієнту з пам'яті без блокувань.
3. **Обробка промаху (Cache MISS):**
   * Потік захоплює м'ютекс та перевіряє таблицю активних запитів `inflight_map`.
   * **Якщо запит за цим ключем уже виконується іншим потоком:** поточний потік не створює нове мережеве з'єднання. Він реєструється у списку очікування та блокується на умовній змінній (`pthread_cond_t` / `std::condition_variable`), звільняючи процесорний час.
   * **Якщо цей потік є першим (Leader):** він створює структуру стану `InflightRequest`, реєструє її в таблиці, звільняє глобальний м'ютекс і самостійно здійснює мережевий виклик до Origin.
4. **Трансляція та пробудження (Fan-Out Broadcast):**
   * Отримавши відповідь від Origin, потік-лідер знову захоплює м'ютекс, записує отримані байти в локальну хеш-таблицю кешу з новим TTL, встановлює прапорець завершення `is_done = 1` і надсилає широкомовний сигнал пробудження (`broadcast` / `notify_all`) усім сплячим потокам.
   * Розблоковані потоки-підписники одночасно зчитують свіжі дані з кешу та повертають їх своїм клієнтським з'єднанням.

---

### Реалізація механізму кешування та Single-Flight

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAX_KEY_LEN 128
#define MAX_VAL_LEN 4096
#define HASH_TABLE_SIZE 1024

/* Запис у кеші з таймером свіжості (TTL) */
typedef struct CacheEntry {
    char key[MAX_KEY_LEN];
    char data[MAX_VAL_LEN];
    size_t data_len;
    time_t expires_at;
    struct CacheEntry* next;
} CacheEntry;

/* Стан активного вихідного запиту до Origin (In-flight request) */
typedef struct InflightRequest {
    char key[MAX_KEY_LEN];
    int is_done;
    int error_code;
    pthread_cond_t cond;
    struct InflightRequest* next;
} InflightRequest;

/* Структура кешувального рушія */
typedef struct {
    CacheEntry* cache_buckets[HASH_TABLE_SIZE];
    InflightRequest* inflight_buckets[HASH_TABLE_SIZE];
    pthread_mutex_t mutex;
} EdgeCache;

/* Хеш-функція djb2 для ключів URI */
static unsigned long hash_key(const char* str) {
    unsigned long hash = 5381;
    int c;
    while ((c = (unsigned char)*str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_TABLE_SIZE;
}

void edge_cache_init(EdgeCache* ec) {
    memset(ec->cache_buckets, 0, sizeof(ec->cache_buckets));
    memset(ec->inflight_buckets, 0, sizeof(ec->inflight_buckets));
    pthread_mutex_init(&ec->mutex, NULL);
}

/* Симуляція мережевого запиту до сервера-джерела (Origin) */
static int fetch_from_origin(const char* key, char* out_buf, size_t* out_len) {
    /* Симуляція затримки магістрального каналу 100 мс */
    usleep(100000);
    int written = snprintf(out_buf, MAX_VAL_LEN, "Payload for [%s] generated at %ld", key, time(NULL));
    if (written < 0 || written >= MAX_VAL_LEN) {
        return -1;
    }
    *out_len = (size_t)written;
    return 0;
}

/* Отримання даних з кешу або завантаження через Single-Flight */
int edge_cache_get(EdgeCache* ec, const char* key, int ttl_seconds, char* out_buf, size_t* out_len) {
    unsigned long h = hash_key(key);
    time_t now = time(NULL);

    pthread_mutex_lock(&ec->mutex);

    /* 1. Перевірка наявності валідного запису в кеші */
    CacheEntry* ce = ec->cache_buckets[h];
    while (ce) {
        if (strcmp(ce->key, key) == 0) {
            if (ce->expires_at > now) {
                /* Cache HIT */
                memcpy(out_buf, ce->data, ce->data_len);
                *out_len = ce->data_len;
                pthread_mutex_unlock(&ec->mutex);
                return 0;
            }
            break; /* Запис застарів, потрібне оновлення */
        }
        ce = ce->next;
    }

    /* 2. Перевірка, чи запит за цим ключем уже виконується іншим потоком */
    InflightRequest* inf = ec->inflight_buckets[h];
    while (inf) {
        if (strcmp(inf->key, key) == 0) {
            break;
        }
        inf = inf->next;
    }

    if (inf) {
        /* Запит вже в польоті: блокуємося та очікуємо завершення */
        while (!inf->is_done) {
            pthread_cond_wait(&inf->cond, &ec->mutex);
        }
        
        /* Після пробудження читаємо збережений кеш */
        ce = ec->cache_buckets[h];
        while (ce) {
            if (strcmp(ce->key, key) == 0 && ce->expires_at > now) {
                memcpy(out_buf, ce->data, ce->data_len);
                *out_len = ce->data_len;
                pthread_mutex_unlock(&ec->mutex);
                return 0;
            }
            ce = ce->next;
        }
        pthread_mutex_unlock(&ec->mutex);
        return -1; /* Помилка завантаження першим потоком */
    }

    /* 3. Ми — перший потік: створюємо InflightRequest */
    InflightRequest new_inf;
    strncpy(new_inf.key, key, MAX_KEY_LEN - 1);
    new_inf.key[MAX_KEY_LEN - 1] = '\0';
    new_inf.is_done = 0;
    new_inf.error_code = 0;
    pthread_cond_init(&new_inf.cond, NULL);

    new_inf.next = ec->inflight_buckets[h];
    ec->inflight_buckets[h] = &new_inf;

    /* Звільняємо блокування на час мережевого запиту до Origin */
    pthread_mutex_unlock(&ec->mutex);

    char origin_data[MAX_VAL_LEN];
    size_t origin_len = 0;
    int res = fetch_from_origin(key, origin_data, &origin_len);

    /* 4. Завершення виклику: збереження в кеш та сповіщення очікуючих потоків */
    pthread_mutex_lock(&ec->mutex);

    if (res == 0) {
        /* Збереження або оновлення в кеші */
        ce = ec->cache_buckets[h];
        while (ce && strcmp(ce->key, key) != 0) {
            ce = ce->next;
        }
        if (!ce) {
            ce = (CacheEntry*)malloc(sizeof(CacheEntry));
            strncpy(ce->key, key, MAX_KEY_LEN - 1);
            ce->key[MAX_KEY_LEN - 1] = '\0';
            ce->next = ec->cache_buckets[h];
            ec->cache_buckets[h] = ce;
        }
        memcpy(ce->data, origin_data, origin_len);
        ce->data_len = origin_len;
        ce->expires_at = time(NULL) + ttl_seconds;

        memcpy(out_buf, origin_data, origin_len);
        *out_len = origin_len;
    }

    /* Видалення з inflight_buckets */
    InflightRequest** curr = &ec->inflight_buckets[h];
    while (*curr) {
        if (*curr == &new_inf) {
            *curr = new_inf.next;
            break;
        }
        curr = &(*curr)->next;
    }

    new_inf.is_done = 1;
    new_inf.error_code = res;
    pthread_cond_broadcast(&new_inf.cond);
    pthread_mutex_unlock(&ec->mutex);

    pthread_cond_destroy(&new_inf.cond);
    return res;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
#include <expected>
#include <vector>

class EdgeCacheProxy {
public:
    struct CacheEntry {
        std::string data;
        std::chrono::steady_clock::time_point expires_at;
    };

    struct InflightState {
        bool is_done{false};
        std::string error_message;
        std::condition_variable cv;
    };

    explicit EdgeCacheProxy(std::chrono::seconds default_ttl) 
        : default_ttl_(default_ttl) {}

    // Отримання ресурсу з кешу або через єдиний запит до Origin
    std::expected<std::string, std::string> get(std::string_view key) {
        std::string key_str(key);
        std::unique_lock<std::mutex> lock(mutex_);

        auto now = std::chrono::steady_clock::now();

        // 1. Перевірка валідного запису в кеші
        auto cache_it = cache_.find(key_str);
        if (cache_it != cache_.end() && cache_it->second.expires_at > now) {
            return cache_it->second.data; // Cache HIT
        }

        // 2. Перевірка, чи запит уже виконується іншим потоком
        auto inflight_it = inflight_.find(key_str);
        if (inflight_it != inflight_.end()) {
            auto state = inflight_it->second;
            // Очікуємо завершення запиту першим потоком
            state->cv.wait(lock, [&state]() { return state->is_done; });

            if (!state->error_message.empty()) {
                return std::unexpected(state->error_message);
            }

            auto updated_cache_it = cache_.find(key_str);
            if (updated_cache_it != cache_.end()) {
                return updated_cache_it->second.data;
            }
            return std::unexpected("Запис відсутній після розблокування");
        }

        // 3. Ми — перший потік: реєструємо об'єкт InflightState
        auto state = std::make_shared<InflightState>();
        inflight_[key_str] = state;

        // Звільняємо м'ютекс на час звернення до мережі
        lock.unlock();

        auto origin_result = fetch_from_origin(key_str);

        // 4. Повертаємо блокування та оновлюємо стан для всіх очікуючих
        lock.lock();

        if (origin_result.has_value()) {
            cache_[key_str] = CacheEntry{
                .data = origin_result.value(),
                .expires_at = std::chrono::steady_clock::now() + default_ttl_
            };
        } else {
            state->error_message = origin_result.error();
        }

        state->is_done = true;
        inflight_.erase(key_str);

        // Сповіщаємо всі очікуючі потоки
        state->cv.notify_all();

        return origin_result;
    }

private:
    std::chrono::seconds default_ttl_;
    std::mutex mutex_;
    std::unordered_map<std::string, CacheEntry> cache_;
    std::unordered_map<std::string, std::shared_ptr<InflightState>> inflight_;

    // Симуляція запиту до Origin (затримка 100 мс)
    static std::expected<std::string, std::string> fetch_from_origin(const std::string& key) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        return "Вміст для ресурсу [" + key + "] з джерела Origin";
    }
};
```
:::

---

### Тонкощі реалізації та аналіз крайових випадків

1. **Захист від фальшивих пробуджень (Spurious Wakeups):**
   У стандартах POSIX Threads та C++11 умовна змінна може випадково вийти зі стану очікування без отримання сигналу від іншого потоку через внутрішні переривання ядра операційної системи. Тому виклик `pthread_cond_wait` обов'язково розміщується всередині циклу перевірки стану `while (!inf->is_done)`, а в C++ використовується перевантажений метод `state->cv.wait(lock, [&state]() { return state->is_done; })`, який автоматично повторює засинання, доки умова не стане істинною.

2. **Гарантія розблокування при аваріях (Deadlock Prevention):**
   Якщо мережевий виклик до Origin завершується помилкою таймауту або обривом з'єднання, потік-лідер зобов'язаний гарантовано перевести стан `InflightState` у `is_done = true` та викликати `notify_all()`. Якщо потік аварійно вийде за межі функції через виняток без сповіщення, усі очікуючі клієнтські потоки назавжди зависнуть у стані блокування, вичерпавши пам'ять та дескриптори сокетів.

3. **Стійкість до повільних клієнтів (Slow Client Backpressure):**
   У реальних CDN трансляція відповіді тисячам клієнтів не повинна блокувати основний цикл обробки подій (Event Loop). Якщо один із клієнтів зчитує дані на низькій швидкості мобільного з'єднання 2G, проксі не накопичує байти в пам'яті нескінченно, а регулює розмір буфера сокета через механізми реактивного протитиску (Backpressure).

4. **Керування пам'яттю та витіснення (LRU Eviction):**
   Обсяг оперативної пам'яті на периферійному вузлі є скінченним. Промислові реалізації доповнюють хеш-таблицю двобічно зв'язаним списком витіснення за алгоритмом LRU (Least Recently Used) або ARC (Adaptive Replacement Cache). При перевищенні ліміту пам'яті проксі витісняє найменш популярні записи, вивільняючи буфери під нові гарячі об'єкти.

5. **Сегментація блокувань (Fine-Grained Sharded Locking):**
   Використання єдиного глобального м'ютекса для всієї таблиці кешу створює високу конкуренцію між ядрами процесора (Lock Contention) на багатоядерних серверах із 64–128 ядрами. Професійні рушії розділяють хеш-таблицю на сотні незалежних сегментів (Shards), кожен із яких має власний м'ютекс або `std::shared_mutex` для паралельного неблокуючого читання багатьма потоками.

6. **Негативне кешування помилок (Negative Caching):**
   Якщо сервер-джерело повертає помилку `500 Internal Server Error` або `503 Service Unavailable`, проксі не повинен кешувати такий результат на стандартний TTL. Проте повна відмова від кешування призведе до того, що наступні тисячі запитів миттєво доб'ють сервер, який намагається відновитися. Встановлення мікро-TTL тривалістю 1–3 секунди захищає Origin під час інцидентів.
