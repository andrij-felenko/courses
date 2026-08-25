# ⚙️ Реалізація клієнта безперервної ротації секретів із захистом пам'яті

Цей практичний розбір присвячено побудові виробничого клієнта для безперервної ротації динамічних облікових даних без перезапуску сервісу та втрати з'єднань. У розборі розглядаються механізми ізоляції конфіденційних даних в оперативній пам'яті через блокування сторінок (`mlock`), гарантоване очищення буферів для запобігання оптимізаціям компілятора та атомарне перемикання активного секрету між робочими потоками без блокувань (*lock-free double buffering*).

---

### Постановка задачі та модель загроз

У високонавантажених розподілених сервісах ротація паролів баз даних або симетричних ключів шифрування повинна відбуватися кожні кілька годин. Перезапуск процесу або примусове переривання активних з'єднань пулу призводить до каскадного падіння системи (*thundering herd problem*), коли сотні екземплярів застосунку одночасно намагаються перевстановити з'єднання з базою даних.

Крім того, типові клієнтські реалізації припускаються критичних помилок при роботі з конфіденційною пам'яттю процесу:
1. **Вимивання секретів у swap-простір**: Якщо операційна система відчуває брак фізичної оперативної пам'яті, підсистема підкачування сторінок ядра Linux скидає анонімні сторінки віртуальної пам'яті процесу на жорсткий диск або SSD у swap-розділ. Конфіденційний рядок залишається записаним у блоках накопичувача у відкритому вигляді навіть після аварійного або планового завершення програми.
2. **Знищення зачистки оптимізатором компілятора (*Dead Store Elimination*)**: Традиційний виклик `memset(buffer, 0, size)` перед викликом `free()` видаляється компілятором під час оптимізації (наприклад, з прапорцем `-O2` або `-O3`), оскільки за правилами абстрактної машини C/C++ пам'ять після звільнення більше ніколи не читається легітимним кодом.
3. **Витік через аварійні дампи пам'яті (*Core Dumps*)**: Під час неочікуваного збою програми (наприклад, за сигналом `SIGSEGV`) ядро операційної системи формує повний знімок адресного простору процесу та записує його на диск. Сторонні інструменти збору телеметрії можуть надіслати цей файл у зовнішнє сховище звітів.
4. **Стан гонки під час оновлення (*Data Race*)**: Зміна пароля або токена в спільній глобальній структурі конфігурації без атомарної синхронізації призводить до того, що робочий потік зчитує наполовину оновлені байти, спричиняючи раптовий збій автентифікації на боці зовнішнього ресурсу.

---

### Архітектура рішення: Подвійний буфер та фоновий потік оновлення

Архітектура захищеного менеджера секретів базується на трьох взаємопов'язаних інженерних принципах:

1. **Захищений буфер пам'яті (`SecureBuffer`)**: Виділяє пам'ять через вирівняні межі сторінок (`posix_memalign`), фіксує їх у фізичній пам'яті через виклик `mlock()` для запобігання перенесенню у swap та маркує сторінку прапорцем ядра `MADV_DONTDUMP` (що виключає сторінку з будь-яких аварійних дампів). Звільнення структури супроводжується гарантованою фізичною зачисткою через виклик `explicit_bzero()`.
2. **Атомарний покажчик на активний секрет (*Lock-free Read*)**: Робочі потоки застосунку отримують посилання на поточний стан облікових даних через атомарне завантаження `atomic_load()`. Це гарантує час доступу `O(1)` без використання важких м'ютексів (`pthread_mutex_t`), усуваючи взаємні блокування та затримки під час високого навантаження.
3. **Фоновий потік оренди (*Lease Worker*)**: Автономний потік періодично взаємодіє зі сховищем секретів (наприклад, HashiCorp Vault), подовжує термін дії поточної оренди (*Heartbeat Renewal*), а при досягненні порогу ротації отримує нову пару облікових даних, конструює новий захищений буфер і виконує атомарну підміну покажчика за одну інструкцію.

---

### Програмна реалізація

Нижче наведено завершені production-орієнтовані реалізації мовами C та C++.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/mman.h>
#include <time.h>

#define SECRET_MAX_LEN 256

/* Структура захищеного облікового запису */
typedef struct {
    char username[SECRET_MAX_LEN];
    char password[SECRET_MAX_LEN];
    char lease_id[SECRET_MAX_LEN];
    time_t expires_at;
    _Atomic int ref_count;
} secret_entry_t;

/* Стан менеджера секретів */
typedef struct {
    _Atomic(secret_entry_t*) active_secret;
    pthread_t worker_thread;
    atomic_bool running;
    int rotation_interval_sec;
} secret_manager_t;

/* Безпечне виділення пам'яті з блокуванням у RAM */
static secret_entry_t* secure_entry_create(const char* user, const char* pass, const char* lease, int ttl_sec) {
    long page_size = sysconf(_SC_PAGESIZE);
    size_t alloc_size = (sizeof(secret_entry_t) + page_size - 1) & ~(page_size - 1);

    secret_entry_t* entry = NULL;
    if (posix_memalign((void**)&entry, page_size, alloc_size) != 0) {
        return NULL;
    }

    /* Заборона вивантаження сторінки у swap */
    if (mlock(entry, alloc_size) != 0) {
        free(entry);
        return NULL;
    }

    /* Виключення з дампу пам'яті під час аварії */
#ifdef MADV_DONTDUMP
    madvise(entry, alloc_size, MADV_DONTDUMP);
#endif

    strncpy(entry->username, user, SECRET_MAX_LEN - 1);
    entry->username[SECRET_MAX_LEN - 1] = '\0';

    strncpy(entry->password, pass, SECRET_MAX_LEN - 1);
    entry->password[SECRET_MAX_LEN - 1] = '\0';

    strncpy(entry->lease_id, lease, SECRET_MAX_LEN - 1);
    entry->lease_id[SECRET_MAX_LEN - 1] = '\0';

    entry->expires_at = time(NULL) + ttl_sec;
    atomic_init(&entry->ref_count, 1);

    return entry;
}

/* Гарантоване очищення пам'яті перед звільненням */
static void secure_entry_release(secret_entry_t* entry) {
    if (!entry) return;

    if (atomic_fetch_sub(&entry->ref_count, 1) == 1) {
        long page_size = sysconf(_SC_PAGESIZE);
        size_t alloc_size = (sizeof(secret_entry_t) + page_size - 1) & ~(page_size - 1);

        /* Гарантоване занулення буфера без оптимізацій компілятора */
        explicit_bzero(entry, sizeof(secret_entry_t));

        munlock(entry, alloc_size);
        free(entry);
    }
}

/* Емуляція отримання нового динамічного секрету з Vault */
static secret_entry_t* fetch_secret_from_vault(int version) {
    char user[SECRET_MAX_LEN];
    char pass[SECRET_MAX_LEN];
    char lease[SECRET_MAX_LEN];

    snprintf(user, sizeof(user), "app_user_v%d", version);
    snprintf(pass, sizeof(pass), "vault_gen_pass_%lx_%d", (unsigned long)time(NULL), version);
    snprintf(lease, sizeof(lease), "database/creds/app-role/%d", version);

    /* TTL = 10 секунд для демонстрації ротації */
    return secure_entry_create(user, pass, lease, 10);
}

/* Фоновий потік ротації та оновлення оренди */
static void* rotation_worker(void* arg) {
    secret_manager_t* mgr = (secret_manager_t*)arg;
    int version = 1;

    while (atomic_load(&mgr->running)) {
        sleep(mgr->rotation_interval_sec);

        if (!atomic_load(&mgr->running)) break;

        version++;
        secret_entry_t* new_sec = fetch_secret_from_vault(version);
        if (new_sec) {
            /* Атомарна підміна покажчика на новий секрет */
            secret_entry_t* old_sec = atomic_exchange(&mgr->active_secret, new_sec);
            printf("[Worker] Ротація: новий користувач %s (Lease: %s)\n", 
                   new_sec->username, new_sec->lease_id);

            /* Зменшуємо лічильник посилань попереднього секрету */
            secure_entry_release(old_sec);
        }
    }
    return NULL;
}

/* Ініціалізація менеджера */
int secret_manager_init(secret_manager_t* mgr, int rotation_interval_sec) {
    mgr->rotation_interval_sec = rotation_interval_sec;
    atomic_init(&mgr->running, true);

    secret_entry_t* initial_secret = fetch_secret_from_vault(1);
    if (!initial_secret) return -1;

    atomic_init(&mgr->active_secret, initial_secret);

    if (pthread_create(&mgr->worker_thread, NULL, rotation_worker, mgr) != 0) {
        secure_entry_release(initial_secret);
        return -1;
    }
    return 0;
}

/* Отримання поточного секрету клієнтом (Lock-free) */
secret_entry_t* secret_manager_acquire(secret_manager_t* mgr) {
    secret_entry_t* sec = atomic_load(&mgr->active_secret);
    if (sec) {
        atomic_fetch_add(&sec->ref_count, 1);
    }
    return sec;
}

/* Повернення секрету після використання */
void secret_manager_release(secret_entry_t* sec) {
    secure_entry_release(sec);
}

/* Зупинка менеджера та очищення ресурсів */
void secret_manager_destroy(secret_manager_t* mgr) {
    atomic_store(&mgr->running, false);
    pthread_join(mgr->worker_thread, NULL);

    secret_entry_t* sec = atomic_exchange(&mgr->active_secret, NULL);
    secure_entry_release(sec);
}

int main(void) {
    secret_manager_t mgr;
    if (secret_manager_init(&mgr, 3) != 0) {
        fprintf(stderr, "Не вдалося ініціалізувати менеджер секретів\n");
        return 1;
    }

    /* Емуляція роботи застосунку протягом 8 секунд */
    for (int i = 0; i < 4; i++) {
        secret_entry_t* sec = secret_manager_acquire(&mgr);
        if (sec) {
            printf("[Main App] Запит %d: активний логін = %s, пароль = %s\n", 
                   i + 1, sec->username, sec->password);
            secret_manager_release(sec);
        }
        sleep(2);
    }

    secret_manager_destroy(&mgr);
    printf("[Main App] Менеджер успішно зупинено, пам'ять очищено.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <memory>
#include <atomic>
#include <thread>
#include <chrono>
#include <cstring>
#include <unistd.h>
#include <sys/mman.h>

namespace security {

/* RAII-обгортка для захищеного рядка з блокуванням у пам'яті */
class SecureString {
public:
    explicit SecureString(std::string_view data) : size_(data.size()) {
        long page_size = sysconf(_SC_PAGESIZE);
        size_t alloc_size = (size_ + 1 + page_size - 1) & ~(page_size - 1);

        if (posix_memalign(reinterpret_cast<void**>(&buffer_), page_size, alloc_size) != 0) {
            throw std::bad_alloc();
        }

        if (mlock(buffer_, alloc_size) != 0) {
            free(buffer_);
            throw std::runtime_error("mlock failed to lock secure memory");
        }

#ifdef MADV_DONTDUMP
        madvise(buffer_, alloc_size, MADV_DONTDUMP);
#endif

        std::memcpy(buffer_, data.data(), size_);
        buffer_[size_] = '\0';
    }

    ~SecureString() {
        if (buffer_) {
            long page_size = sysconf(_SC_PAGESIZE);
            size_t alloc_size = (size_ + 1 + page_size - 1) & ~(page_size - 1);

            /* Гарантоване занулення без усунення оптимізатором */
            explicit_bzero(buffer_, size_ + 1);

            munlock(buffer_, alloc_size);
            free(buffer_);
        }
    }

    // Заборона копіювання для запобігання дублюванню секретів у пам'яті
    SecureString(const SecureString&) = delete;
    SecureString& operator=(const SecureString&) = delete;

    // Дозвіл переміщення
    SecureString(SecureString&& other) noexcept : buffer_(other.buffer_), size_(other.size_) {
        other.buffer_ = nullptr;
        other.size_ = 0;
    }

    SecureString& operator=(SecureString&& other) noexcept {
        if (this != &other) {
            this->~SecureString();
            buffer_ = other.buffer_;
            size_ = other.size_;
            other.buffer_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::string_view view() const noexcept {
        return buffer_ ? std::string_view(buffer_, size_) : std::string_view{};
    }

private:
    char* buffer_{nullptr};
    size_t size_{0};
};

/* Структура облікових даних сервісу */
struct SecretCredentials {
    SecureString username;
    SecureString password;
    std::string lease_id;
    std::chrono::system_clock::time_point expires_at;

    SecretCredentials(std::string_view u, std::string_view p, std::string_view lease, std::chrono::seconds ttl)
        : username(u), password(p), lease_id(lease),
          expires_at(std::chrono::system_clock::now() + ttl) {}
};

/* Менеджер ротації секретів */
class SecretRotationManager {
public:
    explicit SecretRotationManager(std::chrono::seconds rotation_interval)
        : rotation_interval_(rotation_interval), running_(true) {
        
        // Отримання початкового секрету
        auto initial = fetch_from_vault(1);
        active_secret_.store(initial);

        // Запуск фонового потоку ротації
        worker_thread_ = std::thread(&SecretRotationManager::rotation_loop, this);
    }

    ~SecretRotationManager() {
        running_.store(false);
        if (worker_thread_.joinable()) {
            worker_thread_.join();
        }
    }

    /* Lock-free читання активного секрету */
    [[nodiscard]] std::shared_ptr<const SecretCredentials> get_secret() const noexcept {
        return std::atomic_load(&active_secret_);
    }

private:
    std::shared_ptr<SecretCredentials> fetch_from_vault(int version) {
        std::string user = "app_user_v" + std::to_string(version);
        std::string pass = "vault_sec_cpp_" + std::to_string(version) + "_xyz";
        std::string lease = "database/creds/app-cpp/" + std::to_string(version);
        
        return std::make_shared<SecretCredentials>(user, pass, lease, std::chrono::seconds(10));
    }

    void rotation_loop() {
        int version = 1;
        while (running_.load()) {
            std::this_thread::sleep_for(rotation_interval_);
            if (!running_.load()) break;

            version++;
            auto new_secret = fetch_from_vault(version);
            if (new_secret) {
                // Атомарна заміна спільного покажчика
                std::atomic_store(&active_secret_, new_secret);
                std::cout << "[CPP-Worker] Успішна ротація: користувач "
                          << new_secret->username.view() << " (Lease: "
                          << new_secret->lease_id << ")\n";
            }
        }
    }

    std::chrono::seconds rotation_interval_;
    std::atomic<bool> running_{false};
    std::shared_ptr<SecretCredentials> active_secret_{nullptr};
    std::thread worker_thread_;
};

} // namespace security

int main() {
    using namespace std::chrono_literals;

    security::SecretRotationManager manager(3s);

    for (int i = 0; i < 4; ++i) {
        auto secret = manager.get_secret();
        if (secret) {
            std::cout << "[CPP-Main] Запит " << (i + 1) << ": логін = "
                      << secret->username.view() << ", пароль = "
                      << secret->password.view() << "\n";
        }
        std::this_thread::sleep_for(2s);
    }

    std::cout << "[CPP-Main] Завершення роботи програми.\n";
    return 0;
}
```
:::

---

### Детальний розбір механізмів безпеки

#### 1. Захист від оптимізацій компілятора (`explicit_bzero`)
У стандартній бібліотеці C виклик `memset()` сприймається оптимізатором компілятора як операція без побічних ефектів. Якщо після занулення буфер передається функції `free()` або локальна змінна знищується при виході зі стекового фрейму, компілятор розцінює такий запис як «мертвий» (*Dead Store*) і повністю видаляє інструкцію занулення згенерованого асемблерного коду. 

Щоб змусити компілятор виконати фізичне перезаписування пам'яті нулями незалежно від рівня оптимізації, стандарт POSIX та операційна система Linux надають системну функцію `explicit_bzero()`. У середовищі Windows для цієї мети використовується `SecureZeroMemory()`, а в стандарті C11 — функція з контролем меж `memset_s()`.

#### 2. Запобігання вивантаженню у swap (`mlock`)
Системний виклик `mlock(addr, len)` звертається безпосередньо до підсистеми віртуальної пам'яті ядра Linux і виставляє біт фіксації сторінки в таблиці сторінок процесу. Це гарантує, що сторінка залишатиметься у фізичній пам'яті RAM і ядро ніколи не запише її вміст у swap-файл на диску. Для успішного виконання виклику процес повинен мати достатній ліміт блокування пам'яті `RLIMIT_MEMLOCK` (налаштовується через `/etc/security/limits.conf` або директиву `LimitMEMLOCK` у systemd).

#### 3. Атомарна зміна без блокувань (*Lock-Free Double Buffering*)
Використання `std::atomic<std::shared_ptr<T>>` у C++ та атомарного лічильника посилань у C усуває потребу в блокуваннях `pthread_mutex_t` під час кожного звернення до бази даних. Робочі потоки ніколи не блокують один одного: вони за лічені наносекунди зчитують атомарний покажчик на активну структуру. 

Під час ротації потік оновлення конструює новий об'єкт і змінює покажчик однією атомарною інструкцією `LOCK CMPXCHG` (або `atomic_exchange`). Старий об'єкт автоматично знищується та очищується, щойно останній робочий потік завершує його використання і декрементує лічильник посилань до нуля.

#### 4. Обробка помилок та мережевих збоїв під час оновлення
У реальних розподілених системах зв'язок зі сховищем секретів може тимчасово обриватися через мережеві збої. Реалізація клієнта повинна передбачати стратегію повторних спроб (*Retry Policy*):
- Якщо черговий запит на продовження оренди повернув помилку тайм-ауту або статус `500 Internal Error`, клієнт не повинен негайно скидати активний секрет. Секрет залишається дійсним до закінчення початкового часу життя `expires_at`;
- Клієнт повторює спробу продовження оренди з експоненційним зростанням інтервалу та додаванням випадкового зсуву (*Full Jitter*), щоб уникнути одночасного перевантаження кластера сховища сотнями мікросервісів;
- Лише у випадку, коли Vault повертає статус `403 Forbidden` або `404 Not Found` (що свідчить про повне анулювання оренди на боці сховища), клієнт ініціює аварійний цикл переавтентифікації машини.
