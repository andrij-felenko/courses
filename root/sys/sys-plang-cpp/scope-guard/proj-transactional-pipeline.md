# ⚙️ Транзакційний конвеєр: надійна модифікація файлів із відкатом

Оновлення критичних конфігураційних файлів, образів пам'яті та баз даних на диску вимагає суворої транзакційної атомарності: збій на будь-якому етапі запису чи валідації не повинен залишати пошкоджений файл або неузгоджений кеш у пам'яті процесу.

## Задача та модель відкату

Розгляньмо практичну задачу збереження критичного файлу конфігурації (наприклад, параметрів роботи мережевого демона або стану польотного контролера). Процес оновлення складається з кількох послідовних кроків, кожен з яких взаємодіє з операційною системою та пам'яттю процесу:

1. **Створення унікального тимчасового файлу** `config.tmp` у тій самій файловій системі, де розташований цільовий файл (щоб зберегти можливість атомарного перейменування в межах одного розділу накопичувача).
2. **Серіалізація та запис нових даних** у тимчасовий файл із примусовим скиданням системних сторінкових буферів ядра ОС на фізичний накопичувач за допомогою виклику `fsync`.
3. **Перевірка цілісності та валідація** (обчислення контрольної суми CRC32, верифікація схеми серіалізації, перевірка допустимих діапазонів числових значень, валідність мережевих адрес та портів).
4. **Створення резервної копії** поточного дійсного файлу `config.bak` (якщо попередній робочий конфігураційний файл уже існував на накопичувачі).
5. **Атомарне перейменування** тимчасового файлу на цільове ім'я `config.json` за допомогою системного виклику `rename`.
6. **Оновлення кешу в оперативній пам'яті** процесу та сповіщення підсистем-обробників про зміну параметрів.

Якщо на будь-якому з кроків виникає аварійна ситуація (вичерпався вільний простір на диску, збій контрольної суми, помилка прав доступу, апаратний збій або виняток через брак пам'яті під час ініціалізації мережевих сокетів), система зобов'язана чисто відкотитися до вихідного стану:
- створений тимчасовий файл `config.tmp` має бути негайно видалений із накопичувача, щоб не засмічувати файлову систему;
- резервна копія `config.bak` має бути повернута на місце основного файлу (якщо основний файл уже встигли підмінити);
- кеш у пам'яті процесу повинен гарантовано зберегти старі налаштування;
- жоден системний дескриптор чи ресурс не повинен витекти.

Застосування патерна Scope Guard дозволяє прив'язати дію компенсації (відкату) безпосередньо до моменту створення кожного ресурсу, гарантуючи виконання відкату у порядку LIFO (англ. *last in, first out*) під час виходу з області видимості.

## Реалізація узагальненого охоронця ScopeGuard

Для побудови надійного конвеєра реалізуємо повнофункціональний клас `ScopeGuard`. Клас повинен володіти виконуваним об'єктом за семантикою переміщення, забороняти небезпечне копіювання, надавати метод `dismiss()` для скасування відкату та гарантувати безпеку винятків у деструкторі:

```cpp
#include <utility>
#include <type_traits>

template <typename Callback>
class ScopeGuard {
    Callback callback_;
    bool active_{true};

public:
    // Конструктор захоплює довільний функціональний об'єкт
    explicit ScopeGuard(Callback&& cb) noexcept(std::is_nothrow_move_constructible_v<Callback>)
        : callback_(std::move(cb)) {}

    explicit ScopeGuard(const Callback& cb) noexcept(std::is_nothrow_copy_constructible_v<Callback>)
        : callback_(cb) {}

    // Заборона копіювання: відповідальність за відкат належить одному екземпляру
    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;

    // Переміщення передає обов'язок відкату новому об'єкту, знеструмлюючи джерело
    ScopeGuard(ScopeGuard&& other) noexcept(std::is_nothrow_move_constructible_v<Callback>)
        : callback_(std::move(other.callback_)),
          active_(std::exchange(other.active_, false)) {}

    ScopeGuard& operator=(ScopeGuard&& other) noexcept {
        if (this != &other) {
            if (active_) {
                callback_();
            }
            callback_ = std::move(other.callback_);
            active_ = std::exchange(other.active_, false);
        }
        return *this;
    }

    // Деструктор викликає дію відкату, якщо охоронець не був скасований
    ~ScopeGuard() {
        if (active_) {
            callback_();
        }
    }

    // Скасування відкату після успішного завершення операції
    void dismiss() noexcept {
        active_ = false;
    }
};

// Фабрична функція для автоматичного виведення типів аргументів
template <typename Callback>
[[nodiscard]] auto make_scope_guard(Callback&& cb) {
    return ScopeGuard<std::decay_t<Callback>>(std::forward<Callback>(cb));
}
```

Атрибут `[[nodiscard]]` над фабричною функцією захищає від критичної помилки: якщо викликати `make_scope_guard([&]{ ... });` без збереження результату в іменовану змінну, тимчасовий об'єкт знищиться негайно в кінці повного виразу, виконавши відкат завчасно замість очікування виходу з області видимості.

## Порівняння реалізацій: C проти C++

Розгляньмо повний приклад транзакційної функції оновлення конфігурації. У вкладці C показано класичний низькорівневий підхід із ручним відстеженням міток помилок `goto fail`, а у вкладці C++ — сучасну ідіоматичну реалізацію з автоматичним відкатом через деструктори охоронців.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>

typedef struct {
    int log_level;
    char server_addr[64];
    int port;
} ServerConfig;

// Глобальний кеш налаштувань у процесі
static ServerConfig g_active_config;

bool save_and_apply_config_c(const char* target_path, const ServerConfig* new_cfg) {
    char tmp_path[256];
    char bak_path[256];
    snprintf(tmp_path, sizeof(tmp_path), "%s.tmp", target_path);
    snprintf(bak_path, sizeof(bak_path), "%s.bak", target_path);

    bool tmp_created = false;
    bool bak_created = false;
    ServerConfig prev_cache;

    // 1. Створення та запис у тимчасовий файл
    FILE* f = fopen(tmp_path, "wb");
    if (!f) {
        return false;
    }
    tmp_created = true;

    if (fwrite(new_cfg, sizeof(ServerConfig), 1, f) != 1) {
        fclose(f);
        goto fail;
    }

    // Примусове скидання буферів ОС на накопичувач
    fflush(f);
    fsync(fileno(f));
    fclose(f);

    // 2. Валідація параметрів конфігурації
    if (new_cfg->port <= 0 || new_cfg->port > 65535) {
        goto fail;
    }
    if (strlen(new_cfg->server_addr) == 0) {
        goto fail;
    }

    // 3. Створення резервної копії попереднього файлу
    if (access(target_path, F_OK) == 0) {
        if (rename(target_path, bak_path) != 0) {
            goto fail;
        }
        bak_created = true;
    }

    // 4. Атомарне перейменування тимчасового файлу на цільовий
    if (rename(tmp_path, target_path) != 0) {
        goto fail;
    }
    tmp_created = false; // файл зайняв цільове місце

    // 5. Оновлення стану в оперативній пам'яті
    memcpy(&prev_cache, &g_active_config, sizeof(ServerConfig));
    memcpy(&g_active_config, new_cfg, sizeof(ServerConfig));

    // Успішне завершення: видаляємо старий бекап
    if (bak_created) {
        unlink(bak_path);
    }
    return true;

fail:
    // Ручний каскад відкату у зворотному порядку створення
    if (tmp_created) {
        unlink(tmp_path);
    }
    if (bak_created) {
        rename(bak_path, target_path);
    }
    return false;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>

namespace fs = std::filesystem;

struct ServerConfig {
    int log_level{1};
    std::string server_addr{"127.0.0.1"};
    int port{8080};
};

// Глобальний стан сервісу
static ServerConfig g_active_config;

void validate_config(const ServerConfig& cfg) {
    if (cfg.port <= 0 || cfg.port > 65535) {
        throw std::invalid_argument("Неприпустимий порт сервера");
    }
    if (cfg.server_addr.empty()) {
        throw std::invalid_argument("Порожня адреса сервера");
    }
}

void notify_subsystems(const ServerConfig& cfg) {
    // Симуляція сповіщення інших потоків або виділення пам'яті під мережевий сокет
    if (cfg.server_addr == "invalid.local") {
        throw std::runtime_error("Мережева підсистема відхилила нову адресу");
    }
}

void save_and_apply_config_cpp(const fs::path& target_path, const ServerConfig& new_cfg) {
    const fs::path tmp_path = target_path.string() + ".tmp";
    const fs::path bak_path = target_path.string() + ".bak";

    // 1. Запис даних у тимчасовий файл
    {
        std::ofstream out(tmp_path, std::ios::binary | std::ios::trunc);
        if (!out.is_open()) {
            throw std::runtime_error("Неможливо створити тимчасовий файл: " + tmp_path.string());
        }
        out << new_cfg.log_level << "\n"
            << new_cfg.server_addr << "\n"
            << new_cfg.port << "\n";
        out.flush();
    }

    // Охоронець 1: видалення тимчасового файлу у разі будь-якого збою
    auto remove_tmp_guard = make_scope_guard([&tmp_path] noexcept {
        std::error_code ec;
        fs::remove(tmp_path, ec);
    });

    // 2. Валідація структури налаштувань (може викинути виняток)
    validate_config(new_cfg);

    // 3. Створення резервної копії поточного конфігураційного файлу
    bool had_backup = false;
    if (fs::exists(target_path)) {
        fs::rename(target_path, bak_path);
        had_backup = true;
    }

    // Охоронець 2: повернення резервної копії, якщо щось зламається далі
    auto restore_bak_guard = make_scope_guard([&, had_backup] noexcept {
        if (had_backup) {
            std::error_code ec;
            fs::rename(bak_path, target_path, ec);
        }
    });

    // 4. Атомарна підміна основного файлу
    fs::rename(tmp_path, target_path);

    // Тимчасовий файл став основним, видаляти його як сміття більше не потрібно
    remove_tmp_guard.dismiss();

    // 5. Оновлення кешу налаштувань у пам'яті
    ServerConfig old_cache = g_active_config;
    g_active_config = new_cfg;

    // Охоронець 3: відновлення пам'яті у разі помилки в підсистемах
    auto restore_cache_guard = make_scope_guard([&old_cache] noexcept {
        g_active_config = std::move(old_cache);
    });

    // 6. Сповіщення підсистем процесу (може викинути виняток під час ініціалізації сокета)
    notify_subsystems(new_cfg);

    // Всі кроки пройшли успішно: скасовуємо відкати й прибираємо бекап
    restore_cache_guard.dismiss();
    restore_bak_guard.dismiss();

    if (had_backup) {
        std::error_code ec;
        fs::remove(bak_path, ec);
    }
}
```
:::

## Архітектурний аналіз: чому Scope Guard перевершує goto

Порівнюючи наведені фрагменти, можна чітко виокремити ключові інженерні переваги автоматичного відкату через деструктори над процедурним керуванням потоком виконання:

### Локальність коду відкату та зменшення когнітивного навантаження

У C-стилі код очищення принципово відірваний від місця створення ресурсу: створення файлу відбувається на початку функції, а виклик `unlink(tmp_path)` розташований наприкінці за міткою `fail:`. У міру розростання складності функції розробник змушений підтримувати карту допоміжних булевих прапорців (`tmp_created`, `bak_created`) і тримати в голові всю матрицю переходів.

Будь-яка модифікація алгоритму (наприклад, додавання проміжного кроку між 2 і 3) вимагає не лише написання прямої дії, а й уважного аналізу всього ланцюжка міток `goto` внизу функції. Помилка в одній мітці призводить до витоку ресурсу або, що значно небезпечніше, до спроби видалити ресурс, який ще не був створений.

У версії на C++ код скасування розташований безпосередньо у наступному рядку після виділення:

```cpp
fs::rename(target_path, bak_path);
auto restore_bak_guard = make_scope_guard([&, had_backup] noexcept {
    if (had_backup) {
        std::error_code ec;
        fs::rename(bak_path, target_path, ec);
    }
});
```

Читач коду бачить пряму дію та її компенсаційний відкат як єдиний логічний крок. Якщо в майбутньому цей фрагмент знадобиться перенести, загорнути в умовний оператор або видалити, дію та її відкат переносять разом як неподільну пару, без потреби вичитувати решту функції.

### Автоматичний порядок LIFO без людського фактора

Компілятор C++ гарантує, що деструктори автоматичних об'єктів виконуються у порядку, строго протилежному до їх створення на стеку. Це усуває класичний клас помилок мови C, коли розробник помилково переставляє виклики `free` чи `close` у блоці `fail:` або пропускає очищення проміжного кроку при додаванні нової перевірки в середину функції.

Оскільки об'єкти на стеку реєструються послідовно, порядок розгортання є природним дзеркальним відображенням порядку ініціалізації: остання змінена сутність відкочується першою.

### Стійкість до будь-якої моделі сигналізації про помилки

У мові C будь-яка помилка повинна виражатися кодом повернення. Якщо в C++ викликати функцію, здатну викинути виняток (наприклад, конструктор `std::string` чи метод стандартної бібліотеки), виконання негайно залишає функцію через механізм розгортання стека. Ручний блок `goto fail` у цьому випадку взагалі не виконається.

Scope Guard однаково бездоганно працює з обома парадигмами:
- **У коді на базі винятків:** будь-який виняток автоматично запускає деструктори зареєстрованих охоронців під час проходження фреймів стека.
- **У коді на базі кодів помилок / `std::expected`:** ранній вихід через `return std::unexpected(err);` знищує стекові охоронці в точці виходу, забезпечуючи ідентичний повний відкат без дублювання викликів очищення перед кожним оператором `return`.

## Багаторесурсний системний конвеєр: пам'ять, IPC та м'ютекси

Для демонстрації універсальності охоронця області розгляньмо складніший системний сценарій: ініціалізацію спільного сегмента пам'яті (POSIX Shared Memory), створення файлового відображення `mmap`, блокування міжпроцесного м'ютекса та реєстрацію дескриптора подій.

У цьому сценарії помилка на етапі захоплення м'ютекса повинна звільнити відображення `munmap`, закрити файловий дескриптор `close` та видалити спільний сегмент `shm_unlink`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pthread.h>
#include <stdbool.h>

typedef struct {
    pthread_mutex_t lock;
    int counter;
} SharedRegion;

bool init_shared_service_c(const char* shm_name, size_t size) {
    int fd = -1;
    SharedRegion* ptr = (SharedRegion*)MAP_FAILED;
    bool shm_created = false;

    // 1. Створення спільного сегмента
    fd = shm_open(shm_name, O_CREAT | O_RDWR | O_EXCL, 0600);
    if (fd < 0) {
        return false;
    }
    shm_created = true;

    // 2. Встановлення розміру сегмента
    if (ftruncate(fd, (off_t)size) != 0) {
        goto fail;
    }

    // 3. Відображення в адресний простір процесу
    ptr = (SharedRegion*)mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) {
        goto fail;
    }

    // 4. Ініціалізація міжпроцесного м'ютекса
    pthread_mutexattr_t mattr;
    pthread_mutexattr_init(&mattr);
    pthread_mutexattr_setpshared(&mattr, PTHREAD_PROCESS_SHARED);

    if (pthread_mutex_init(&ptr->lock, &mattr) != 0) {
        pthread_mutexattr_destroy(&mattr);
        goto fail;
    }
    pthread_mutexattr_destroy(&mattr);

    ptr->counter = 0;
    close(fd);
    return true;

fail:
    if (ptr != MAP_FAILED) {
        munmap(ptr, size);
    }
    if (fd >= 0) {
        close(fd);
    }
    if (shm_created) {
        shm_unlink(shm_name);
    }
    return false;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <system_error>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pthread.h>

struct SharedRegion {
    pthread_mutex_t lock;
    int counter{0};
};

void init_shared_service_cpp(std::string_view shm_name, size_t size) {
    const std::string name_str(shm_name);

    // 1. Створення сегмента пам'яті
    int fd = ::shm_open(name_str.c_str(), O_CREAT | O_RDWR | O_EXCL, 0600);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "shm_open failed");
    }

    // Охоронець 1: видалення імені сегмента з системи
    auto unlink_guard = make_scope_guard([&name_str] noexcept {
        ::shm_unlink(name_str.c_str());
    });

    // Охоронець 2: закриття файлового дескриптора на виході
    auto close_guard = make_scope_guard([fd] noexcept {
        ::close(fd);
    });

    // 2. Встановлення розміру
    if (::ftruncate(fd, static_cast<off_t>(size)) != 0) {
        throw std::system_error(errno, std::generic_category(), "ftruncate failed");
    }

    // 3. Відображення в адресний простір
    void* raw_ptr = ::mmap(nullptr, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (raw_ptr == MAP_FAILED) {
        throw std::system_error(errno, std::generic_category(), "mmap failed");
    }
    auto* region = static_cast<SharedRegion*>(raw_ptr);

    // Охоронець 3: скидання відображення у разі збою ініціалізації м'ютекса
    auto unmap_guard = make_scope_guard([raw_ptr, size] noexcept {
        ::munmap(raw_ptr, size);
    });

    // 4. Налаштування міжпроцесного м'ютекса
    pthread_mutexattr_t mattr;
    ::pthread_mutexattr_init(&mattr);
    auto mattr_guard = make_scope_guard([&mattr] noexcept {
        ::pthread_mutexattr_destroy(&mattr);
    });

    if (::pthread_mutexattr_setpshared(&mattr, PTHREAD_PROCESS_SHARED) != 0 ||
        ::pthread_mutex_init(&region->lock, &mattr) != 0) {
        throw std::system_error(errno, std::generic_category(), "mutex init failed");
    }

    region->counter = 0;

    // Успіх: сегмент ініціалізовано. Відв'язуємо охоронці, які знищували б створене середовище:
    unlink_guard.dismiss();
    unmap_guard.dismiss();
    // close_guard спрацює в кінці функції за планом, бо дескриптор після mmap більше не потрібен
    // mattr_guard спрацює в кінці функції, звільнивши атрибути м'ютекса
}
```
:::

У цій програмі чітко видно різницю між постійними ресурсами та транзакційними діями відкату:
- `close_guard` та `mattr_guard` діють як класичні RAII-деструктори (виконуються завжди на виході з блоку);
- `unlink_guard` та `unmap_guard` діють як транзакційні відкати (скасовуються через `dismiss()` лише після успішної підготовки всіх залежностей).

## Простеження системних викликів ядра ОС (strace)

Щоб наочно переконатися у бездоганності роботи механізму відкату, розгляньмо журнал системних викликів ядра Linux (за допомогою утиліти `strace`) для двох сценаріїв виконання функції оновлення конфігурації:

### Журнал успішного виконання

```
openat(AT_FDCWD, "config.json.tmp", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 3
write(3, "1\n127.0.0.1\n8080\n", 17) = 17
fdatasync(3)                            = 0
close(3)                                = 0
statx(AT_FDCWD, "config.json", ...)     = 0
rename("config.json", "config.json.bak") = 0
rename("config.json.tmp", "config.json") = 0
unlink("config.json.bak")               = 0
```

На успішному шляху тимчасовий файл атомарно стає основним, а старий бекап видаляється. Жодної зайвої операції або витоку дескрипторів не відбувається.

### Журнал аварійного відкату при збої валідації

```
openat(AT_FDCWD, "config.json.tmp", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 3
write(3, "1\ninvalid.local\n8080\n", 21) = 21
fdatasync(3)                            = 0
close(3)                                = 0
unlink("config.json.tmp")               = 0
--- SIGABRT / C++ exception unwind ---
```

Охоронець `remove_tmp_guard` під час розкручування стека миттєво посилає ядру запит `unlink("config.json.tmp")`. Тимчасовий файл зникає з файлової таблиці до того, як виняток дійде до зовнішнього обробника.

## Динамічні конвеєри та масиви охоронців

В описаних прикладах кількість кроків була фіксованою та відомою під час компіляції. Проте в реальних системах часто виникає потреба у транзакційній обробці динамічних колекцій — наприклад, створенні кількох тимчасових каталогів на різних дисках або захопленні довільної кількості ресурсів у циклі.

Оскільки наш `ScopeGuard` підтримує семантику переміщення, екземпляри охоронців можна зберігати у стандартному контейнері `std::vector`:

```cpp
#include <vector>
#include <functional>

void setup_distributed_workspace(const std::vector<std::string>& node_dirs) {
    // Вектор анонімних охоронців для відкату динамічної кількості дій
    std::vector<ScopeGuard<std::function<void()>>> rollbacks;
    rollbacks.reserve(node_dirs.size());

    // Якщо функція перерветься винятком на 5-му вузлі,
    // деструктор вектора знищить усі збережені охоронці,
    // які автоматично відкотять перші 4 вузли!
    auto all_guard = make_scope_guard([&rollbacks] noexcept {
        // Очищення у зворотному порядку (LIFO)
        for (auto it = rollbacks.rbegin(); it != rollbacks.rend(); ++it) {
            // деструктор кожного елемента виконає збережену дію
        }
    });

    for (const auto& dir : node_dirs) {
        fs::create_directories(dir);
        rollbacks.emplace_back(make_scope_guard([dir] noexcept {
            std::error_code ec;
            fs::remove_all(dir, ec);
        }));
    }

    // Додаткові операції ініціалізації
    // initialize_network_mesh(node_dirs);

    // Успіх: скасовуємо відкат усіх створених каталогів
    for (auto& g : rollbacks) {
        g.dismiss();
    }
    all_guard.dismiss();
}
```

Ця техніка забезпечує сильну виняткову гарантію для масивів ресурсів довільної довжини без необхідності написання спеціалізованих контейнерів-обгорток.

## Взаємодія з асинхронним кодом та сопрограмами (C++20 Coroutines)

Особливу увагу слід звертати на поведінку охоронців області видимості всередині сопрограм (англ. *coroutines*), що використовують інструкції `co_await`, `co_yield` та `co_return`.

Коли сопрограма призупиняє своє виконання через `co_await`, локальні стекові змінні **не знищуються**: вони зберігаються всередині динамічного фрейму сопрограми в купі (англ. *coroutine frame*). Відповідно, деструктори `ScopeGuard` **не виконуються** під час призупинення:

```cpp
#include <coroutine>

// Приклад поведінки охоронця у сопрограмі
Task<void> async_transaction_step(Database& db) {
    db.acquire_lock();
    auto lock_guard = make_scope_guard([&db] noexcept {
        db.release_lock();
    });

    // Призупинення сопрограми: деструктор lock_guard НЕ викликається!
    co_await async_network_fetch();

    // Відновлення виконання: lock_guard залишається активним
    db.apply_changes();

    // Завершення сопрограми (co_return): lock_guard знищується тут
}
```

Якщо ж сопрограму буде примусово знищено ззовні через виклик методу дескриптора `coroutine_handle<>::destroy()`, фрейм сопрограми розгортається, і деструктори всіх активних об'єктів (включно зі `ScopeGuard`) будуть коректно викликані, забезпечуючи надійний відкат навіть в асинхронному контексті.

## Інтеграція з монадичною моделлю помилок (C++23 std::expected)

У сучасному коді, що уникає важких винятків на користь обробки помилок через значення (`std::expected`), Scope Guard залишається не менш актуальним.

Без охоронця ранній вихід через `return std::unexpected(...)` змушує дублювати код очищення перед кожною перевіркою результату:

```cpp
#include <expected>
#include <string>

enum class ErrorCode { DiskFull, BadChecksum, PermissionDenied };

std::expected<void, ErrorCode> write_data_monadic(const fs::path& target) {
    const fs::path tmp = target.string() + ".tmp";
    if (!create_file(tmp)) {
        return std::unexpected(ErrorCode::PermissionDenied);
    }

    // Охоронець гарантує видалення тимчасового файлу при будь-якому ранньому return
    auto tmp_guard = make_scope_guard([&tmp] noexcept {
        std::error_code ec;
        fs::remove(tmp, ec);
    });

    auto write_res = write_payload(tmp);
    if (!write_res) {
        return std::unexpected(write_res.error()); // tmp_guard видалить файл тут!
    }

    auto check_res = verify_checksum(tmp);
    if (!check_res) {
        return std::unexpected(check_res.error()); // tmp_guard видалить файл тут!
    }

    fs::rename(tmp, target);
    tmp_guard.dismiss(); // успіх: файл залишається
    return {};
}
```

Як видно з прикладу, Scope Guard природно поєднує виразність деструкторів RAII з функціональним стилем передачі результатів через `std::expected`.

## Порівняння з двофазною фіксацією (2-Phase Commit)

Розглянута схема модифікації файлів за своєю суттю є мініатюрною реалізацією протоколу двофазної фіксації (англ. *two-phase commit*, 2PC), адаптованою до локального процесу та файлової системи:

1. **Фаза підготовки (Prepare Phase):** Створення тимчасового файлу `config.tmp`, запис корисного навантаження, верифікація структури та примусовий `fsync`. На цьому етапі перевіряється, чи взагалі можливо виконати операцію. Якщо на фазі підготовки виникає будь-яка помилка, всі охоронці залишаються активними, а їхні деструктори повністю анулюють підготовлені дані.
2. **Точка неповернення (Commit Point):** Атомарна заміна основного файлу через `rename`. Після успіху цього виклику операція вважається зафіксованою на диску.
3. **Фаза фіксації (Commit Phase):** Виклик `dismiss()` на охоронцях відкату, видалення застарілих резервних копій та застосування змін до кешу в пам'яті.

Такий розподіл гарантує, що система ніколи не опиниться в проміжному «напівзаписаному» стані: до моменту виклику `dismiss()` будь-який збій повертає стару версію, а після `dismiss()` нова версія вже повністю гарантована накопичувачем.

## Тестування відкату та ін'єкція збоїв (Fault Injection)

Критичною вимогою до надійності транзакційних конвеєрів є їхнє регулярне тестування на стійкість до збоїв. На практиці це реалізується за допомогою методів ін'єкції збоїв (англ. *fault injection*):

- **Мокування системних викликів:** У модульних тестах виклики функцій запису або перейменування підміняються функціями, які імітують помилку `ENOSPC` (закінчилося місце) або `EACCES` (відмова в доступі) на конкретному N-му кроці транзакції.
- **Верифікація стану після збою:** Тест перевіряє, що після викидання штучного винятку цільовий файл залишається у попередній версії, тимчасовий файл зник, а лічильники активних ресурсів повернулися до нуля.
- **Динамічний аналіз пам'яті (AddressSanitizer):** Компіляція тестів із прапорцями `-fsanitize=address,undefined` дозволяє переконатися, що під час розгортання стека не виникає помилок подвійного звільнення пам'яті (англ. *double free*) або витоків покажчиків.

## Асинхронні сигнали операційної системи та межі застосування

Важливо розрізняти винятки C++ та асинхронні сигнали POSIX (`SIGINT`, `SIGTERM`, `SIGSEGV`, `SIGKILL`):

- **Розгортання стека C++** є синхронним процесом, керованим середовищем виконання мови, яке послідовно викликає деструктори.
- **Асинхронний сигнал ОС** (наприклад, `kill -9` або необроблений `SIGTERM`) перериває процес на рівні ядра. При раптовому завершенні процесу ядром жодні деструктори C++ (і, відповідно, жодні охоронці `ScopeGuard`) **не виконуються**.

Для захисту критичних транзакцій від переривання сигналами `SIGINT` або `SIGTERM` під час модифікації файлів застосовують маскування сигналів через `pthread_sigmask`:

```cpp
#include <signal.h>

void safe_signal_transaction() {
    sigset_t block_mask, old_mask;
    sigemptyset(&block_mask);
    sigaddset(&block_mask, SIGINT);
    sigaddset(&block_mask, SIGTERM);

    // Блокуємо сигнали на час критичної секції
    pthread_sigmask(SIG_BLOCK, &block_mask, &old_mask);
    auto sig_guard = make_scope_guard([&old_mask] noexcept {
        // Гарантоване відновлення маски сигналів на виході
        pthread_sigmask(SIG_SETMASK, &old_mask, nullptr);
    });

    // Виконання атомарного збереження конфігурації...
}
```

У такій конфігурації охоронець `sig_guard` надійно відновлює маску сигналів навіть у разі викидання винятку з тіла транзакції.

## Низькорівневий механізм: генерація коду компілятором

Для розуміння ефективності патерна розгляньмо, у що перетворюється `ScopeGuard` на рівні асемблера:

1. **Інлайнінг лямбда-функції:** Оскільки лямбда-вираз не має віртуальних методів і передається безпосередньо за шаблоном, сучасні оптимізувальні компілятори (GCC, Clang, MSVC) повністю вбудовують (інлайнять) тіло лямбди в точку виходу.
2. **Нульова вартість нормального виходу:** Якщо в блоці коду немає винятків, компілятор розгортає `if (active_) callback_()` у пряму послідовність машинних інструкцій в епілозі функції. Якщо компілятор бачить, що на успішному шляху викликано `dismiss()`, він повністю усуває перевірку умови за допомогою аналізу мертвого коду (англ. *dead code elimination*).
3. **Таблиці розгортання стека (zero-cost exceptions):** В архітектурах x86-64 (згідно з Itanium C++ ABI) на звичайному шляху виконання немає жодних накладних витрат на реєстрацію охоронців. Компілятор генерує статичну таблицю відповідності адрес інструкцій діапазонам обробки (англ. *landing pads*). Лише коли виникає виняток, середовище виконання аналізує таблицю й викликає деструктори охоронців.

## Крайові випадки та правила безпеки

При проектуванні систем на базі Scope Guard критично враховувати такі інженерні правила:

1. **Сувора заборона винятків усередині відкату (`noexcept`).** Якщо функція відкату викине власний виняток у той час, коли стек уже розгортається через первинний виняток, середовище C++ негайно викличе `std::terminate()`. Тому всі виклики у лямбді охоронця повинні бути захищені за допомогою перевантажень із кодами помилок (`std::error_code`) або внутрішніх блоків `try-catch`.
2. **Семантика захоплення змінних: посилання проти копії.** Змінні, що відображають стан на момент створення охоронця (наприклад, початкове значення лічильника, копія структури кешу або прапорець `had_backup`), слід захоплювати **за значенням** (`[old_cache]` або `[&, had_backup]`). Якщо захопити їх за посиланням `[&]`, на момент виклику деструктора посилання вказуватиме на вже змінене значення, і відкат застосує некоректний стан.
3. **Атомарність операцій файлової системи.** Системний виклик `rename` гарантує атомарну підміну файлу лише в межах однієї файлової системи (англ. *mount point*). Створення тимчасового файлу в іншій точці монтування (наприклад, у `/tmp`, що живе на tmpfs у RAM) призведе до помилки `EXDEV` (Cross-device link) або неатомарного копіювання, що руйнує транзакційні гарантії.
4. **Скидання метаданих каталогу.** Для гарантованої стійкості до раптового відключення живлення недостатньо викликати `fsync` на самому файлі. Слід також відкрити дескриптор батьківського каталогу й викликати `fsync` на ньому після виконання операції `rename`, щоб гарантувати запис оновленого запису каталогу на фізичні пластини чи флеш-пам'ять накопичувача.
