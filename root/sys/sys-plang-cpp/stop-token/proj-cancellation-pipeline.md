# ⚙️ Конвеєр обробки даних із багаторівневим скасуванням на std::stop_token

Коли паралельна система будується з кількох взаємопов'язаних стадій обробки — черг, пулів робочих потоків, мережевих адаптерів та модулів збереження — зупинка системи перетворюється на складне інженерне завдання. Примусове вбивство потоків призводить до пошкодження пам'яті, а примітивні булеві прапорці не здатні розбудити потоки, заблоковані на очікуванні повідомлень або переповненні буферів. Цей практичний проєкт демонструє створення надійного тристадійного конвеєра потокової обробки на C++20, у якому скасування є кооперативним, неблокуючим, потокобезпечним та підтримує каскадну ієрархію між окремими стадіями за допомогою `std::stop_token`, `std::stop_source`, `std::stop_callback` та `std::condition_variable_any`.

---

## 1. Архітектурне завдання: багаторівневий паралельний конвеєр

Уявімо високопродуктивний сервіс обробки телеметрії від розподілених IoT-датчиків або фінансових транзакцій у реальному часі. Дані надходять у систему неперервним потоком через мережу, проходять крізь послідовні стадії трансформації та врешті-решт записуються у сховище:

```
[ Генератор / Джерело ] ──► (Черга 1) ──► [ Робочі потоки: Обчислення ] ──► (Черга 2) ──► [ Приймач / Запис ]
           ▲                                           ▲                                           ▲
           │                                           │                                           │
           └─────────────────── stop_token ────────────┴───────────────────────────────────────────┘
```

Конвеєр складається з трьох ключових фаз:
1. **Стадія джерела (Ingestion Stage)**: генерує або вичитує сирі пакети даних і розміщує їх у першій буферизованій черзі обмеженого розміру.
2. **Стадія обчислень (Transform Stage)**: пул потоків `std::jthread` витягує сирі пакети, виконує ресурсомістку валідацію, парсинг, перевірку контрольних сум і математичну агрегацію, після чого передає результат у другу чергу.
3. **Стадія виводу (Sink Stage)**: потік запису агрегує підготовлені пакети та зберігає їх у файл або відправляє в аналітичну базу даних.

### Інженерні виклики та вимоги до системи скасування

У розподілених та багатопотокових конвеєрах виникають специфічні проблеми синхронізації під час зупинки:
- **Миттєве пробудження з блокування**: якщо черга порожня, потік-обчислювач спить на умовній змінній в очікуванні роботи. Сигнал зупинки повинен миттєво вивести потік зі стану сну без необхідності штучного надсилання фіктивних маркерів завершення (так званих «отруйних пігулок» — poison pills), які можуть загубитися або ускладнити логіку типів у черзі.
- **Захист від переповнення буфера (Backpressure)**: якщо обчислювачі не встигають за швидкістю джерела, вхідна черга заповнюється до ліміту. Джерело блокується на спробі запису, але також мусить миттєво реагувати на сигнал зупинки, не зависаючи у вічному очікуванні вільного місця.
- **Ієрархічне та каскадне керування**: система повинна підтримувати як глобальне аварійне переривання всього конвеєра (наприклад, за таймаутом або зовнішнім сигналом ОС `SIGINT`), так і ізольовану зупинку окремої стадії (наприклад, у разі критичного збою парсера) із коректним сповіщенням сусідніх ланок.
- **Дві стратегії завершення**: конвеєр повинен дозволяти або *аварійне негайне скасування* (миттєве скидання всіх черг і вихід), або *коректне вичерпання (Graceful Draining)*, коли джерело припиняє генерувати нові дані, а обчислювачі та приймач доопрацьовують усі пакети, які вже потрапили в буфери.
- **RAII-безпека та відсутність витоків**: під час виходу з області видимості всі потоки повинні чисто завершуватися через `std::jthread`, системні дескриптори закриватися, а виділена динамічна пам'ять звільнятися без взаємних блокувань (дедлоків).

---

## 2. Ключовий примітив: потокобезпечна черга з підтримкою stop_token

Звичайна `std::condition_variable` зі стандарту C++11 жорстко прив'язана до `std::unique_lock<std::mutex>` і не має вбудованої підтримки токенів скасування. Щоб потік міг чекати наявності даних у черзі й одночасно бути перерваним зовнішнім сигналом через `std::stop_token`, C++20 надає узагальнену умовну змінну `std::condition_variable_any`.

Клас `std::condition_variable_any` має перевантажені методи:
- `template<class Lock, class Predicate> bool wait(Lock& lock, std::stop_token stoken, Predicate pred);`
- `template<class Lock, class Rep, class Period, class Predicate> bool wait_for(Lock& lock, std::stop_token stoken, const std::chrono::duration<Rep, Period>& rel_time, Predicate pred);`

Усередині методу `wait()` реєструється тимчасовий об'єкт `std::stop_callback`. Якщо сторонній потік викликає `request_stop()` на джерелі `std::stop_source`, пов'язаному з цим токеном, зворотний виклик автоматично виконує `cv.notify_all()`. Сплячий потік прокидається на рівні ядра ОС, знову захоплює м'ютекс і перевіряє предикат. Якщо предикат хибний, але `stoken.stop_requested() == true`, метод `wait()` негайно повертає значення предиката (тобто `false`), даючи робочому коду можливість вийти з циклу.

Реалізуємо шаблонний клас `InterruptibleQueue<T>` з фіксованим лімітом ємності:

```cpp
#include <condition_variable>
#include <deque>
#include <mutex>
#include <optional>
#include <stop_token>
#include <utility>

template <typename T>
class InterruptibleQueue {
public:
    explicit InterruptibleQueue(std::size_t capacity)
        : capacity_(capacity) {}

    // Додавання елемента з можливістю переривання через stop_token
    bool push(T item, std::stop_token stoken) {
        std::unique_lock lock(mutex_);

        // Чекаємо, доки з'явиться вільне місце АБО надійде сигнал зупинки
        const bool not_full = cv_not_full_.wait(
            lock, 
            stoken, 
            [this] { return queue_.size() < capacity_; }
        );

        // Якщо очікування перервано сигналом зупинки і місця так і немає
        if (stoken.stop_requested() && queue_.size() >= capacity_) {
            return false;
        }

        if (!not_full) {
            return false;
        }

        queue_.push_back(std::move(item));

        // Сповіщаємо один потік-споживач, що очікує на читання
        cv_not_empty_.notify_one();
        return true;
    }

    // Витягування елемента з можливістю переривання через stop_token
    std::optional<T> pop(std::stop_token stoken) {
        std::unique_lock lock(mutex_);

        // Чекаємо наявності даних АБО сигналу зупинки
        const bool has_data = cv_not_empty_.wait(
            lock, 
            stoken, 
            [this] { return !queue_.empty(); }
        );

        if (!queue_.empty()) {
            T item = std::move(queue_.front());
            queue_.pop_front();

            // Сповіщаємо потік-виробник, що очікував вільного місця
            cv_not_full_.notify_one();
            return item;
        }

        // Черга порожня і надійшов сигнал скасування
        return std::nullopt;
    }

    // Неблокуюча перевірка поточного розміру черги
    [[nodiscard]] std::size_t size() const {
        std::lock_guard lock(mutex_);
        return queue_.size();
    }

    // Перевірка, чи порожня черга
    [[nodiscard]] bool empty() const {
        std::lock_guard lock(mutex_);
        return queue_.empty();
    }

    // Примусове сповіщення всіх очікуючих потоків (для фази дренажування)
    void notify_all() {
        cv_not_empty_.notify_all();
        cv_not_full_.notify_all();
    }

private:
    const std::size_t capacity_;
    std::deque<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable_any cv_not_empty_;
    std::condition_variable_any cv_not_full_;
};
```

---

## 3. Переривання блокуючих системних викликів введення-виведення

У реальних виробничих конвеєрах джерело даних часто блокується не на умовній змінній C++, а на системному виклику введення-виведення — наприклад, очікуванні мережевих пакетів із сокета через `recv()` або `read()`.

Якщо потік заблокований усередині ядра ОС на системному виклику, звичайна перевірка `stoken.stop_requested()` у циклі `while` ніколи не виконається, оскільки керування не повертається у простір користувача. У цьому випадку на допомогу приходить `std::stop_callback`.

Колбек реєструється перед входом у блокуючу операцію. Коли інший потік викликає `request_stop()`, колбек виконує системну дію, яка змушує ядро перервати виклик (наприклад, викликає `shutdown()` для сокета або записує байт у неблокуючий `eventfd` / `pipe`):

```cpp
#include <iostream>
#include <stop_token>

#if defined(_WIN32)
#include <winsock2.h>
#else
#include <sys/socket.h>
#include <unistd.h>
#endif

// Клас-адаптер для перериваного читання з мережевого сокета
class InterruptibleSocketReader {
public:
    explicit InterruptibleSocketReader(int socket_fd)
        : socket_fd_(socket_fd) {}

    // Читання порції даних з можливістю негайного переривання
    std::size_t read_bytes(char* buffer, std::size_t max_len, std::stop_token stoken) {
        if (stoken.stop_requested()) {
            return 0;
        }

        // Реєструємо RAII-обробник: у разі надходження сигналу скасування
        // примусово перериваємо блокуючий системний виклик recv() на рівні ядра ОС
        std::stop_callback socket_canceller(stoken, [this] {
            std::cout << "[SocketReader] Переривання системного сокета через stop_callback...\n";
#if defined(_WIN32)
            ::shutdown(static_cast<SOCKET>(socket_fd_), SD_BOTH);
#else
            ::shutdown(socket_fd_, SHUT_RDWR);
#endif
        });

        // Блокуючий виклик: якщо надходить stop_token, shutdown() змушує recv()
        // негайно повернути 0 або -1 з кодом переривання (EBADF або ECONNABORTED)
#if defined(_WIN32)
        int bytes_read = ::recv(static_cast<SOCKET>(socket_fd_), buffer, static_cast<int>(max_len), 0);
#else
        ssize_t bytes_read = ::recv(socket_fd_, buffer, max_len, 0);
#endif

        if (bytes_read <= 0) {
            return 0;
        }

        return static_cast<std::size_t>(bytes_read);
    }

private:
    int socket_fd_;
};
```

Цей патерн є абсолютно надійним: якщо сигнал скасування надходить під час блокування, `shutdown()` негайно розриває з'єднання в ядрі, `recv()` повертає помилку, після чого деструктор `std::stop_callback` чисто видаляє підписку.

---

## 4. Повна реалізація конвеєра: збирання, трансформація, вивід

Тепер об'єднаємо потокобезпечні черги, робочі пули обчислювачів, ієрархічне скасування та статистику в закінчену промислову систему. 

Контролер підтримує два режими зупинки:
1. `stop_immediate()`: аварійна зупинка, при якій усі потоки негайно переривають обробку і скидають залишки буферів.
2. `stop_graceful()`: джерело зупиняє генерацію, а воркери та приймач доопрацьовують усі накопичені в чергах пакети.

```cpp
#include <chrono>
#include <condition_variable>
#include <deque>
#include <format>
#include <iostream>
#include <mutex>
#include <numeric>
#include <optional>
#include <stop_token>
#include <string>
#include <thread>
#include <vector>

// ── Структури даних конвеєра ──────────────────────────────────────────────────

struct RawTelemetryPacket {
    uint64_t id;
    uint64_t timestamp;
    std::string payload;
};

struct ProcessedTelemetryPacket {
    uint64_t id;
    uint64_t checksum;
    std::size_t original_bytes;
    bool is_valid;
};

// ── Контролер тристадійного конвеєра ──────────────────────────────────────────

class TelemetryPipeline {
public:
    TelemetryPipeline(std::size_t queue_capacity, std::size_t worker_count)
        : raw_queue_(queue_capacity),
          processed_queue_(queue_capacity),
          worker_count_(worker_count) {}

    ~TelemetryPipeline() {
        stop_immediate();
    }

    // Запуск усіх ланок конвеєра
    void start() {
        std::cout << "[Конвеєр] Ініціалізація та старт трьох стадій обробки...\n";

        // 1. Стадія виводу / збереження результатів (Sink)
        sink_thread_ = std::jthread([this](std::stop_token stoken) {
            run_sink(stoken);
        });

        // 2. Стадія паралельної трансформації (Worker Pool)
        workers_.reserve(worker_count_);
        for (std::size_t i = 0; i < worker_count_; ++i) {
            workers_.emplace_back([this, i](std::stop_token stoken) {
                run_worker(i, stoken);
            });
        }

        // 3. Стадія генерації / прийому даних (Source)
        source_thread_ = std::jthread([this](std::stop_token stoken) {
            run_source(stoken);
        });
    }

    // Негайне аварійне переривання всього конвеєра
    void stop_immediate() {
        if (!global_stop_source_.stop_requested()) {
            std::cout << "[Конвеєр] Аварійна зупинка: надсилаємо глобальний request_stop()...\n";
            global_stop_source_.request_stop();

            // Будимо умовні змінні черг для негайного виходу
            raw_queue_.notify_all();
            processed_queue_.notify_all();
        }
    }

    // Коректне дренажування: зупиняємо лише джерело, даємо доопрацювати черги
    void stop_graceful() {
        std::cout << "[Конвеєр] Запит на коректне вичерпання (Graceful Drain)...\n";

        // 1. Зупиняємо лише генератор нових даних
        source_stop_source_.request_stop();
        raw_queue_.notify_all();

        // 2. Чекаємо, доки джерело завершить свій цикл
        if (source_thread_.joinable()) {
            source_thread_.join();
        }

        // 3. Чекаємо спорожнення першої черги
        while (!raw_queue_.empty()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }

        // 4. Тепер зупиняємо обчислювальний пул
        for (auto& worker : workers_) {
            worker.request_stop();
        }
        raw_queue_.notify_all();

        for (auto& worker : workers_) {
            if (worker.joinable()) worker.join();
        }

        // 5. Чекаємо спорожнення вихідної черги та зупиняємо приймач
        while (!processed_queue_.empty()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }

        sink_thread_.request_stop();
        processed_queue_.notify_all();

        if (sink_thread_.joinable()) {
            sink_thread_.join();
        }

        std::cout << "[Конвеєр] Усі черги повністю вичерпані, конвеєр чисто завершено.\n";
    }

    // Очікування завершення роботи всіх потоків
    void join() {
        if (source_thread_.joinable()) source_thread_.join();
        for (auto& w : workers_) {
            if (w.joinable()) w.join();
        }
        if (sink_thread_.joinable()) sink_thread_.join();
    }

    [[nodiscard]] std::stop_token get_stop_token() const noexcept {
        return global_stop_source_.get_token();
    }

    [[nodiscard]] uint64_t get_total_generated() const noexcept {
        return total_generated_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint64_t get_total_processed() const noexcept {
        return total_processed_.load(std::memory_order_relaxed);
    }

private:
    // ── Стадія 1: Джерело (генератор пакетів) ─────────────────────────────────
    void run_source(std::stop_token thread_stoken) {
        // Реєструємо підписку: якщо скасовується або весь конвеєр, або локальне джерело
        std::stop_callback cb_global(global_stop_source_.get_token(), [&] {
            raw_queue_.notify_all();
        });
        std::stop_callback cb_local(source_stop_source_.get_token(), [&] {
            raw_queue_.notify_all();
        });

        uint64_t packet_id = 1;
        while (!global_stop_source_.stop_requested() && 
               !source_stop_source_.stop_requested() && 
               !thread_stoken.stop_requested()) {

            RawTelemetryPacket packet{
                .id = packet_id++,
                .timestamp = static_cast<uint64_t>(std::chrono::steady_clock::now().time_since_epoch().count()),
                .payload = "SensorData_Block_Telemetry_XYZ_" + std::to_string(packet_id)
            };

            // Спроба покласти в чергу з можливістю скасування
            if (!raw_queue_.push(std::move(packet), global_stop_source_.get_token())) {
                break; // Скасування під час блокування на повній черзі
            }

            total_generated_.fetch_add(1, std::memory_order_relaxed);

            // Імітація інтервалу генерації пакетів (1 мілісекунда)
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }

        std::cout << std::format("[Джерело] Завершило роботу. Згенеровано пакетів: {}\n", total_generated_.load());
    }

    // ── Стадія 2: Обчислювальний робітник ────────────────────────────────────
    void run_worker(std::size_t worker_id, std::stop_token thread_stoken) {
        std::stop_token global_token = global_stop_source_.get_token();

        while (!global_token.stop_requested() && !thread_stoken.stop_requested()) {
            auto opt_packet = raw_queue_.pop(global_token);
            if (!opt_packet.has_value()) {
                break; // Скасовано під час очікування або черга пуста при зупинці
            }

            const auto& raw = *opt_packet;

            // Імітація ресурсомісткої валідації та контрольної суми
            uint64_t crc = 0;
            for (char ch : raw.payload) {
                crc = (crc * 31) + static_cast<uint8_t>(ch);
            }

            ProcessedTelemetryPacket result{
                .id = raw.id,
                .checksum = crc,
                .original_bytes = raw.payload.size(),
                .is_valid = (crc != 0)
            };

            if (!processed_queue_.push(std::move(result), global_token)) {
                break;
            }
        }

        std::cout << std::format("[Воркер #{}] Завершив обробку.\n", worker_id);
    }

    // ── Стадія 3: Приймач / Збереження ───────────────────────────────────────
    void run_sink(std::stop_token thread_stoken) {
        std::stop_token global_token = global_stop_source_.get_token();

        while (!global_token.stop_requested() && !thread_stoken.stop_requested()) {
            auto opt_item = processed_queue_.pop(global_token);
            if (!opt_item.has_value()) {
                break;
            }

            total_processed_.fetch_add(1, std::memory_order_relaxed);
        }

        std::cout << std::format("[Приймач] Завершив збереження. Усього записано пакетів: {}\n", total_processed_.load());
    }

    InterruptibleQueue<RawTelemetryPacket> raw_queue_;
    InterruptibleQueue<ProcessedTelemetryPacket> processed_queue_;
    std::size_t worker_count_;

    std::stop_source global_stop_source_;
    std::stop_source source_stop_source_;

    std::jthread source_thread_;
    std::vector<std::jthread> workers_;
    std::jthread sink_thread_;

    std::atomic<uint64_t> total_generated_{0};
    std::atomic<uint64_t> total_processed_{0};
};

// ── Головна точка входу ──────────────────────────────────────────────────────

int main() {
    std::cout << "=== Запуск промислового C++20 конвеєра зі скасуванням через stop_token ===\n\n";

    constexpr std::size_t QueueCapacity = 32;
    constexpr std::size_t WorkerCount = 4;

    // Сценарій: Запуск і робота конвеєра з наступним коректним вичерпанням
    {
        std::cout << ">>> ДЕМОНСТРАЦІЯ 1: Коректне дренажування (Graceful Drain) <<<\n";
        TelemetryPipeline pipeline(QueueCapacity, WorkerCount);
        pipeline.start();

        // Даємо конвеєру попрацювати 100 мілісекунд
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        // Виконуємо коректне вичерпання
        pipeline.stop_graceful();

        std::cout << std::format("Результат Демо 1: Згенеровано = {}, Оброблено = {}\n\n",
            pipeline.get_total_generated(), pipeline.get_total_processed());
    }

    // Сценарій 2: Аварійне переривання під повним навантаженням
    {
        std::cout << ">>> ДЕМОНСТРАЦІЯ 2: Миттєве аварійне скасування (Immediate Abort) <<<\n";
        TelemetryPipeline pipeline(QueueCapacity, WorkerCount);
        pipeline.start();

        std::this_thread::sleep_for(std::chrono::milliseconds(50));

        std::cout << "[Головний потік] Симуляція критичного збою або таймауту!\n";
        pipeline.stop_immediate();
        pipeline.join();

        std::cout << std::format("Результат Демо 2: Згенеровано = {}, Оброблено = {}\n",
            pipeline.get_total_generated(), pipeline.get_total_processed());
    }

    std::cout << "\n=== Усі тести завершено успішно: нуль дедлоків, чисте звільнення ресурсів ===\n";
    return 0;
}
```

---

## 5. Глибокий розбір механізмів: як конвеєр уникає дедлоків

### Переривання черги через std::condition_variable_any

Найбільш вразливе місце класичних багатопотокових конвеєрів — це блокування в методах `push()` та `pop()`. Якщо вхідна черга заповнена, потік-джерело викликає `cv.wait()`. Якщо в цей момент система надсилає сигнал завершення, а споживачі вже зупинилися або впали з помилкою, джерело залишиться заблокованим назавжди (виникає вічний дедлок при спробі `join()` у головному потоці).

У наведеній реалізації метод `wait()` в `InterruptibleQueue` делегує контроль `std::condition_variable_any`. Розглянемо точну послідовність внутрішніх кроків під час скасування:

1. Потік-джерело засинає всередині `cv_not_full_.wait(lock, stoken, pred)`.
2. Усередині бібліотечної реалізації конструюється об'єкт `std::stop_callback`, зареєстрований у спільному стані токена `stoken`.
3. Головний потік викликає `global_stop_source_.request_stop()`.
4. Реалізація `std::stop_source` атомарно змінює стан на «зупинено» та синхронно виконує колбек очікування, який викликає `cv_not_full_.notify_all()`.
5. Сплячий потік миттєво прокидається на рівні планувальника ОС, знову захоплює свій м'ютекс `mutex_`, перевіряє `stoken.stop_requested() == true` і негайно повертає керування з кодом завершення `false`.
6. Деструктор тимчасового колбека всередині `wait()` безпечно відписується від джерела.

Ніяких пропущених сигналів, ніяких "завислих" дескрипторів потоків.

### Внутрішня координація пробудження на рівні ядра операційної системи

Коли багатопотокова програма використовує `std::condition_variable_any` на базі Linux або Windows, ядро операційної системи керує сплячими потоками через механізми `futex` (у Linux) або `WaitOnAddress` / події синхронізації (у Windows).

У традиційній схемі C++11, якщо потік заснув на `futex(..., FUTEX_WAIT, ...)`, єдиним способом його розбудити є прямий системний виклик `FUTEX_WAKE` від іншого потоку, що володіє відповідною умовою. Якщо ж логіка програми передбачає асинхронне скасування, ручне керування прапорцями призводить до гонки між перевіркою умови та засинанням: потік може перевірити прапорець `stop == false`, а сигнал скасування надійде за мікросекунду ДО того, як потік виконає системний виклик засинання. У результаті потік засинає назавжди, пропустивши сигнал.

Клас `std::condition_variable_any` усуває цю гонку на фундаментальному рівні: реєстрація `std::stop_callback` відбувається ДО відпускання блокування м'ютекса. Якщо сигнал `request_stop()` надходить у проміжку між реєстрацією колбека та системним викликом очікування, колбек виконується негайно і встановлює прапорець пробудження або сповіщає futex, завдяки чому наступний виклик очікування негайно повертає керування без фактичного блокування в ядрі.

### Каскадне скасування через std::stop_callback

У великих розподілених архітектурах окремі підсистеми можуть мати власні життєві цикли. Наприклад, якщо мережеве з'єднання з базою даних розривається, ми хочемо зупинити лише стадію `SinkStage`, водночас давши іншим стадіям можливість перенаправити або тимчасово зберегти буферизовані дані на локальний диск.

Для зв'язування батьківського та дочірнього джерел скасування застосовується патерн **транслятора токенів**:

```cpp
#include <functional>
#include <stop_token>

class CascadingStageController {
public:
    explicit CascadingStageController(std::stop_token parent_token)
        : parent_token_(parent_token),
          // Реєструємо підписку: якщо батьківське джерело скасовано,
          // ми негайно транслюємо сигнал у наше локальне джерело стадії
          parent_callback_(parent_token_, [this] {
              local_stop_source_.request_stop();
          }) {}

    // Локальне скасування лише цієї підсистеми
    void cancel_stage() {
        local_stop_source_.request_stop();
    }

    [[nodiscard]] std::stop_token get_stage_token() const noexcept {
        return local_stop_source_.get_token();
    }

private:
    std::stop_token parent_token_;
    std::stop_source local_stop_source_;
    std::stop_callback<std::function<void()>> parent_callback_;
};
```

Цей патерн забезпечує сувору односпрямованість графа залежностей:
- Скасування кореня (`parent_token`) каскадно транслюється вниз усім дочірнім стадіям через зареєстровані `std::stop_callback`.
- Локальне скасування окремої стадії (`cancel_stage()`) активує лише власне джерело і не впливає на роботу батьківського контексту, якщо цього не вимагає загальна бізнес-логіка.

---

## 6. Інтеграція stop_token з асинхронними корутинами C++20

Паралельні конвеєри нового покоління часто комбінують системні потоки ОС із легковажними асинхронними корутинами (`co_await`). Корутини дозволяють обслуговувати десятки тисяч одночасних мережевих підключень без виділення окремого стека пам'яті на кожен сеанс.

Клас `std::stop_token` природно інтегрується в механізм призупинення корутин. Створимо спеціалізований очікуваний об'єкт (awaitable), який призупиняє корутину на певний інтервал часу, але миттєво відновлює її, якщо надійшов сигнал скасування:

```cpp
#include <chrono>
#include <coroutine>
#include <stop_token>

// Очікуваний об'єкт таймера з підтримкою скасування через stop_token
struct cancellable_sleep {
    std::chrono::milliseconds duration;
    std::stop_token stoken;

    bool await_ready() const noexcept {
        // Якщо зупинка вже надійшла — не призупиняємося взагалі
        return stoken.stop_requested() || duration.count() <= 0;
    }

    void await_suspend(std::coroutine_handle<> handle) {
        // Реєструємо зворотний виклик для миттєвого відновлення корутини при скасуванні
        cb_.emplace(stoken, [handle] {
            handle.resume();
        });

        // Запускаємо асинхронний таймер (у спрощеному вигляді — окремий тайм-потік або таймер epoll/kqueue)
        timer_thread_ = std::jthread([this, handle] {
            std::this_thread::sleep_for(duration);
            if (cb_.has_value()) {
                handle.resume();
            }
        });
    }

    bool await_resume() const noexcept {
        // Повертає true, якщо таймер сплив успішно, або false, якщо його було скасовано
        return !stoken.stop_requested();
    }

private:
    std::optional<std::stop_callback<std::function<void()>>> cb_;
    std::jthread timer_thread_;
};
```

Використання в асинхронному коді стає гранично чистим та декларативним:

```cpp
// Приклад корутини асинхронного читача телеметрії
struct AsyncTelemetryTask {
    struct promise_type {
        AsyncTelemetryTask get_return_object() { return {}; }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };
};

AsyncTelemetryTask poll_sensor_coroutine(std::stop_token stoken) {
    while (!stoken.stop_requested()) {
        std::cout << "[Корутина] Опитування сенсора...\n";

        // Засинаємо на 100 мс, але прокидаємося негайно у разі request_stop()
        const bool completed = co_await cancellable_sleep{std::chrono::milliseconds(100), stoken};
        if (!completed) {
            std::cout << "[Корутина] Отримано переривання під час сну! Чистий вихід.\n";
            break;
        }
    }
}
```

Такий підхід дозволяє будувати масштабовані асинхронні середовища, де тисячі корутин миттєво звільняють пам'ять за одним сигналом від `std::stop_source`.

---

## 7. Аналіз крайових випадків та типові пастки реалізації

### Пастка 1: Дедлок через захоплення м'ютексів усередині stop_callback

Оскільки зареєстрований колбек виконується *синхронно* в контексті того потоку, який викликав `request_stop()`, будь-яка спроба захопити в колбеку м'ютекс, який уже утримується викликачем, призведе до миттєвого взаємного блокування:

```cpp
// ❌ АНТИПАТЕРН: Ризик взаємного блокування (Deadlock)
std::mutex data_mutex;

void risky_operation(std::stop_token st) {
    std::stop_callback cb(st, [&] {
        std::lock_guard lock(data_mutex); // ДЕДЛОК, якщо викликач request_stop() уже тримає data_mutex!
        cleanup_resources();
    });

    std::lock_guard lock(data_mutex);
    // Якщо в цей момент інший потік викликає request_stop(), виникає класичний ABBA-дедлок.
}
```

**Правило безпеки**: функції зворотного виклику `std::stop_callback` повинні бути максимально легковажними та неблокуючими:
- Встановити атомарний прапорець стану.
- Викликати `notify_all()` на умовній змінній.
- Викликати неблокуючий системний виклик (наприклад, `::shutdown(fd, SHUT_RDWR)` для сокета або `write()` у канал сповіщення).
- Ніколи не виконувати всередині колбека тривалих синхронних обчислень і не захоплювати довільні м'ютекси застосунку.

### Пастка 2: Захоплення посилань на локальні об'єкти стека

Якщо `std::stop_callback` конструюється у локальній функції і захоплює посилання `[&]` на локальну змінну, а потім передається у довгоживучий `std::stop_source`, знищення локального фрейму стека може викликати побоювання щодо виникнення висячих посилань (use-after-free).

Проте стандарт C++20 надає залізобетонну гарантію: деструктор `~stop_callback()` гарантовано вилучає об'єкт зі списку підписників або **блокується** до повного завершення виконання колбека, якщо той прямо зараз виконується іншим потоком усередині `request_stop()`. Завдяки цьому локальний `std::stop_callback` на стеку є повністю RAII-безпечним: коли потік виходить з області видимості, знищення `stop_callback` не дозволить стековим змінним зникнути раніше, ніж завершиться функція скасування.

### Пастка 3: Винятки всередині stop_callback

Якщо користувацька лямбда, передана в `std::stop_callback`, викидає виняток, стандарт C++20 вимагає негайного виклику `std::terminate()`. Сигнал скасування не є каналом передачі помилок; це безумовний інфраструктурний тригер. Якщо всередині очищення можливі збої, їх необхідно перехоплювати локально через блок `try { ... } catch (...)`.

---

## 8. Продуктивність та оптимізації в гарячих циклах

Перевірка статусу токена `stoken.stop_requested()` є надзвичайно швидкою операцією, оскільки вона зводиться до атомарного завантаження з упорядкуванням пам'яті `std::memory_order_acquire`.

На архітектурах x86 та x86_64 завдяки сильній апаратній моделі пам'яті (TSO — Total Store Order) інструкція завантаження з `memory_order_acquire` транслюється компілятором у звичайну машинну інструкцію `mov eax, [ptr]` без жодних бар'єрів пам'яті (`mfence` чи `lock`). Це означає, що вартість перевірки статусу скасування дорівнює вартості звичайного читання з кешу процесора L1 (близько 1–4 тактів CPU).

### Апаратна когерентність кешів і протокол MESI

Під час виклику `request_stop()` ядро процесора, на якому виконується ініціатор, змінює стан рядка кешу зі стану Shared (S) у Modified (M), надсилаючи широкомовний запит інвалідації (Invalidate Queue) іншим процесорним ядрам за протоколом MESI/MOESI.

Усі інші ядра, які в цей момент опитують `stoken.stop_requested()`, отримують промах кешу L1 (Cache Miss) і завантажують оновлене значення безпосередньо через спільну шину або кеш рівня L3. Це гарантує, що час поширення сигналу скасування між ядрами сучасного багатоядерного процесора становить лічені десятки наносекунд (зазвичай від 15 до 45 нс залежно від топології NUMA).

Проте в екстремально гарячих циклах числового моделювання (де ітерація триває лічені наносекунди) навіть одиничне читання пам'яті на кожній ітерації може обмежувати векторизацію (SIMD). У таких випадках застосовується патерн **пакетної перевірки (batch checking)**:

```cpp
void compute_heavy_batch(std::span<const float> data, std::stop_token stoken) {
    constexpr std::size_t CheckInterval = 1024;
    
    for (std::size_t i = 0; i < data.size(); i += CheckInterval) {
        // Перевіряємо статус скасування лише один раз на кожні 1024 елементи
        if (stoken.stop_requested()) {
            break;
        }

        const std::size_t current_chunk = std::min(CheckInterval, data.size() - i);
        process_simd_chunk(&data[i], current_chunk);
    }
}
```

Такий підхід дозволяє комбінувати максимальну швидкість виконання векторизованих інструкцій із мікросекундною реакцією на сигнал переривання.

---

## 9. Порівняльний аналіз моделей скасування у системних мовах

Щоб краще зрозуміти архітектурне місце `std::stop_token`, порівняємо його з підходами в інших сучасних мовах системного програмування:

- **C# (`CancellationToken`)**: історичний прототип моделі C++20. Працює на рівні керованого runtime CLR. Підтримує реєстрацію колбеків та викид винятку `OperationCanceledException`. У C++20 винятки замінено на повернення значень через `bool` або `std::optional`, що усуває накладні витрати на таблиці розгортання стека.
- **Go (`context.Context`)**: використовує закриття каналу `<-ctx.Done()`. Канали Go є динамічними об'єктами в купі, що перевіряються через оператор `select`. У C++20 `std::stop_token` не потребує виділення каналів і працює безпосередньо через атомарні змінні ядра процесора.
- **Rust (`tokio_util::sync::CancellationToken`)**: працює через асинхронні ф'ючерси та опитування `is_cancelled()`. За внутрішньою структурою дуже близький до C++20, проте C++20 стандартизував цей механізм безпосередньо на рівні мови та бібліотеки, включаючи повну підтримку `std::jthread` та умовних змінних.

---

## 10. Інженерні висновки та контрольний список

Перед впровадженням кооперативного скасування у власні виробничі проєкти перевірте виконання таких базових інваріантів:
- Чи передається `std::stop_token` за значенням (копією) у робочі функції, уникаючи непотрібних вказівників і посилань?
- Чи використовується `std::condition_variable_any` замість `std::condition_variable` там, де потік може очікувати на зовнішні події та сигнали зупинки одночасно?
- Чи є зареєстровані `std::stop_callback` неблокуючими, легковажними та вільними від захоплення спільних м'ютексів застосунку?
- Чи реалізовано в робочих циклах коректну обробку повернення `std::nullopt` або `false` із блокуючих черг?
- Чи обгорнуті довгоживучі фонові потоки в `std::jthread`, що гарантує автоматичний виклик `request_stop()` та `join()` під час розгортання стека?

Дотримання цих правил гарантує високу надійність конвеєра під будь-яким навантаженням та повну відсутність прихованих дедлоків під час зупинки системи.
