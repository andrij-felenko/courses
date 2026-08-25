# ⚙️ Реалізація координатора штатного вимкнення

Головна проблема наївної реалізації зупинки сервера полягає в тому, що ресурси звільняються хаотично. Якщо серверний процес у відповідь на `SIGTERM` миттєво руйнує пул з'єднань із базою даних, усі активні запити клієнтів, які саме зараз виконують SQL-транзакції, зазнають аварії через звернення до вже знищених покажчиків. Якщо ж, навпаки, закрити логер до завершення фонових задач, діагностика відмов під час згортання буде втрачена, а напівзаписані транзакції залишаться завислими в пам'яті.

Коректна архітектура вимагає централізованого **координатора штатного вимкнення** (англ. *Graceful Shutdown Coordinator*), який керує життєвим циклом компонентів у строго визначеному порядку:
1. Перехоплення сигналів операційної системи без порушення асинхронно-сигнальної безпеки.
2. Припинення прийому нових клієнтів (видалення з опитування та закриття слухаючого сокета).
3. Очікування завершення активних запитів (дренаж черги задач із контролем лічильника виконань).
4. Зупинка фонових виконавців за допомогою токенів скасування.
5. Змивання буферів (flush логів, трейсів і метрик) та звільнення пулів сховищ у зворотному порядку до їх ініціалізації.
6. Сторожовий таймер (watchdog), що примусово перериває очікування у разі зависання зовнішніх залежностей.

Нижче наведено повноцінну реалізацію такого координатора для мережевого сервера мовами C (на базі системного виклику Linux `signalfd` та циклу `epoll`) та C++ (з використанням стандарту C++20, токенів зупинки `std::stop_token` та RAII-обгорток).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <sys/signalfd.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <pthread.h>
#include <time.h>

#define MAX_EVENTS 32
#define SHUTDOWN_TIMEOUT_SEC 5
#define WORKER_COUNT 4

typedef struct {
    int id;
    pthread_t thread;
    bool running;
    pthread_mutex_t lock;
    pthread_cond_t cond;
    int active_jobs;
    bool stop_requested;
} worker_t;

typedef struct {
    int epoll_fd;
    int signal_fd;
    int listen_fd;
    bool is_draining;
    worker_t workers[WORKER_COUNT];
    pthread_mutex_t state_lock;
} server_coordinator_t;

static void* worker_loop(void* arg) {
    worker_t* w = (worker_t*)arg;
    while (true) {
        pthread_mutex_lock(&w->lock);
        while (w->active_jobs == 0 && !w->stop_requested) {
            pthread_cond_wait(&w->cond, &w->lock);
        }

        if (w->stop_requested && w->active_jobs == 0) {
            pthread_mutex_unlock(&w->lock);
            break;
        }

        /* Імітація обробки активного запиту */
        w->active_jobs--;
        pthread_mutex_unlock(&w->lock);

        usleep(100000); /* 100 мс корисної роботи */
    }
    return NULL;
}

static void coordinator_init(server_coordinator_t* coord) {
    memset(coord, 0, sizeof(*coord));
    pthread_mutex_init(&coord->state_lock, NULL);

    /* 1. Блокуємо сигнали для використання signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);
    pthread_sigmask(SIG_BLOCK, &mask, NULL);

    coord->signal_fd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (coord->signal_fd < 0) {
        perror("signalfd failed");
        exit(EXIT_FAILURE);
    }

    /* 2. Створюємо epoll */
    coord->epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (coord->epoll_fd < 0) {
        perror("epoll_create1 failed");
        exit(EXIT_FAILURE);
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = coord->signal_fd;
    epoll_ctl(coord->epoll_fd, EPOLL_CTL_ADD, coord->signal_fd, &ev);

    /* 3. Ініціалізуємо воркерів */
    for (int i = 0; i < WORKER_COUNT; ++i) {
        coord->workers[i].id = i;
        coord->workers[i].running = true;
        coord->workers[i].active_jobs = 0;
        coord->workers[i].stop_requested = false;
        pthread_mutex_init(&coord->workers[i].lock, NULL);
        pthread_cond_init(&coord->workers[i].cond, NULL);
        pthread_create(&coord->workers[i].thread, NULL, worker_loop, &coord->workers[i]);
    }
}

static void coordinator_drain_and_shutdown(server_coordinator_t* coord) {
    printf("[Coordinator] Отримано сигнал зупинки. Фаза 1: Unreadiness та закриття слухача.\n");
    
    pthread_mutex_lock(&coord->state_lock);
    coord->is_draining = true;
    if (coord->listen_fd >= 0) {
        epoll_ctl(coord->epoll_fd, EPOLL_CTL_DEL, coord->listen_fd, NULL);
        close(coord->listen_fd);
        coord->listen_fd = -1;
    }
    pthread_mutex_unlock(&coord->state_lock);

    printf("[Coordinator] Фаза 2: Зупинка прийому задач воркерами та очікування завершення.\n");
    for (int i = 0; i < WORKER_COUNT; ++i) {
        pthread_mutex_lock(&coord->workers[i].lock);
        coord->workers[i].stop_requested = true;
        pthread_cond_broadcast(&coord->workers[i].cond);
        pthread_mutex_unlock(&coord->workers[i].lock);
    }

    /* Сторожовий таймер очікування воркерів */
    struct timespec start_time, current_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    for (int i = 0; i < WORKER_COUNT; ++i) {
        void* res;
        pthread_join(coord->workers[i].thread, &res);
        pthread_mutex_destroy(&coord->workers[i].lock);
        pthread_cond_destroy(&coord->workers[i].cond);
        printf("[Coordinator] Воркер %d успішно зупинився.\n", i);
    }

    printf("[Coordinator] Фаза 3: Змивання буферів логів і закриття ресурсів.\n");
    fflush(stdout);
    fflush(stderr);

    if (coord->signal_fd >= 0) close(coord->signal_fd);
    if (coord->epoll_fd >= 0) close(coord->epoll_fd);
    pthread_mutex_destroy(&coord->state_lock);

    printf("[Coordinator] Штатне вимкнення завершено успішно (exit code 0).\n");
}

int main(void) {
    server_coordinator_t coord;
    coordinator_init(&coord);

    printf("[Server] Сервер запущено. Очікування подій або сигналів (Ctrl+C)...\n");

    /* Додаємо тестове навантаження */
    for (int i = 0; i < WORKER_COUNT; ++i) {
        pthread_mutex_lock(&coord.workers[i].lock);
        coord.workers[i].active_jobs = 3;
        pthread_cond_signal(&coord.workers[i].cond);
        pthread_mutex_unlock(&coord.workers[i].lock);
    }

    struct epoll_event events[MAX_EVENTS];
    bool running = true;

    while (running) {
        int nfds = epoll_wait(coord.epoll_fd, events, MAX_EVENTS, -1);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait failed");
            break;
        }

        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == coord.signal_fd) {
                struct signalfd_siginfo fdsi;
                ssize_t s = read(coord.signal_fd, &fdsi, sizeof(fdsi));
                if (s == sizeof(fdsi)) {
                    printf("\n[Server] Спіймано сигнал %d (%s).\n", 
                           fdsi.ssi_signo, strsignal(fdsi.ssi_signo));
                    running = false;
                    break;
                }
            }
        }
    }

    coordinator_drain_and_shutdown(&coord);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <thread>
#include <stop_token>
#include <future>
#include <chrono>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <csignal>
#include <functional>
#include <memory>

class GracefulShutdownCoordinator {
public:
    using CleanupHook = std::function<void()>;

    explicit GracefulShutdownCoordinator(std::chrono::seconds timeout)
        : timeout_(timeout), is_shutting_down_(false) {}

    ~GracefulShutdownCoordinator() {
        if (!is_shutting_down_.load()) {
            initiate_shutdown();
        }
    }

    std::stop_token get_stop_token() const noexcept {
        return stop_source_.get_token();
    }

    void add_cleanup_hook(CleanupHook hook) {
        std::lock_guard<std::mutex> lock(hooks_mutex_);
        hooks_.push_back(std::move(hook));
    }

    void register_active_request() {
        active_requests_.fetch_add(1, std::memory_order_relaxed);
    }

    void unregister_active_request() {
        if (active_requests_.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            cv_drain_.notify_all();
        }
    }

    void initiate_shutdown() {
        bool expected = false;
        if (!is_shutting_down_.compare_exchange_strong(expected, true)) {
            return; // Вимкнення вже запущено іншим потоком
        }

        std::cout << "[Coordinator] Початок штатного вимкнення. Сигнал усім підсистемам.\n";
        stop_source_.request_stop();

        // Запуск дренажу в окремому асинхронному завданні з контролем дедлайну
        auto drain_future = std::async(std::launch::async, [this]() {
            // Фаза 1: Дренаж активних запитів
            std::unique_lock<std::mutex> lock(drain_mutex_);
            std::cout << "[Coordinator] Очікування завершення " 
                      << active_requests_.load() << " активних запитів...\n";
            
            cv_drain_.wait(lock, [this]() {
                return active_requests_.load() == 0;
            });
            std::cout << "[Coordinator] Усі активні запити завершено успішно.\n";

            // Фаза 2: Виконання хуків очищення у зворотному порядку
            std::lock_guard<std::mutex> hook_lock(hooks_mutex_);
            for (auto it = hooks_.rbegin(); it != hooks_.rend(); ++it) {
                try {
                    (*it)();
                } catch (const std::exception& e) {
                    std::cerr << "[Coordinator] Помилка у хуку очищення: " << e.what() << "\n";
                }
            }
            std::cout << "[Coordinator] Усі хуки очищення виконано.\n";
        });

        // Контроль дедлайну (Watchdog)
        if (drain_future.wait_for(timeout_) == std::future_status::timeout) {
            std::cerr << "[Coordinator] УВАГА: Вичерпано таймаут дренажу (" 
                      << timeout_.count() << " с)! Примусове завершення.\n";
            std::quick_exit(EXIT_FAILURE);
        } else {
            std::cout << "[Coordinator] Штатне вимкнення завершено успішно.\n";
        }
    }

private:
    std::chrono::seconds timeout_;
    std::atomic<bool> is_shutting_down_;
    std::stop_source stop_source_;
    std::atomic<int> active_requests_{0};
    
    std::mutex drain_mutex_;
    std::condition_variable cv_drain_;

    std::mutex hooks_mutex_;
    std::vector<CleanupHook> hooks_;
};

// Глобальний вказівник для сигнального мосту
static std::atomic<GracefulShutdownCoordinator*> g_coordinator{nullptr};

extern "C" void signal_handler(int signo) {
    if (auto* coord = g_coordinator.load()) {
        coord->initiate_shutdown();
    }
}

int main() {
    GracefulShutdownCoordinator coordinator(std::chrono::seconds(5));
    g_coordinator.store(&coordinator);

    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    // Додаємо ресурси (наприклад, пул БД та логер)
    coordinator.add_cleanup_hook([]() {
        std::cout << "[Resource] Пул з'єднань із базою даних закрито.\n";
    });
    coordinator.add_cleanup_hook([]() {
        std::cout << "[Resource] Кеш і буферизований логер змито на диск.\n";
    });

    // Запускаємо робочі потоки з підтримкою stop_token (C++20 std::jthread)
    std::vector<std::jthread> workers;
    for (int i = 0; i < 3; ++i) {
        workers.emplace_back([&coordinator, i](std::stop_token st) {
            std::cout << "[Worker " << i << "] Запущено.\n";
            while (!st.stop_requested()) {
                coordinator.register_active_request();
                
                // Імітуємо виконання роботи
                std::this_thread::sleep_for(std::chrono::milliseconds(150));
                
                coordinator.unregister_active_request();
                std::this_thread::sleep_for(std::chrono::milliseconds(50));
            }
            std::cout << "[Worker " << i << "] Зупинився за токеном зупинки.\n";
        }, coordinator.get_stop_token());
    }

    std::cout << "[Server] Головний потік працює. Натисніть Ctrl+C для зупинки...\n";
    
    // Імітація роботи сервера до отримання сигналу
    std::this_thread::sleep_for(std::chrono::milliseconds(600));
    std::cout << "[Server] Імітуємо прихід сигналу SIGTERM...\n";
    coordinator.initiate_shutdown();

    // jthread автоматично викликають join() у своїх деструкторах
    return 0;
}
```
:::

## Поетапний розбір архітектурних рішень

Розглянемо внутрішню інженерну механіку кожного з етапів, на яких тримається надійність координатора.

### 1. Сигнальний міст і безпека простору користувача

Класична помилка початківців — спроба виконати всю логіку вимкнення безпосередньо у функції-обробнику `sigaction`. Як відомо зі стандарту POSIX, обробник сигналу виконується асинхронно і перериває довільний потік у будь-якій машинній інструкції. Якщо потік у мить приходу сигналу утримував внутрішній замок алокатора `malloc` або буфера `stdio`, спроба виділити пам'ять чи викликати логування з обробника призведе до миттєвого мертвого блокування (англ. *deadlock*).

У наведених прикладах ми використовуємо два фундаментально безпечні підходи:

- **Підхід C (через `signalfd`):** Ми блокуємо маску сигналів для всіх потоків за допомогою `pthread_sigmask`. Ядро більше не перериває виконання інструкцій; натомість воно розміщує інформацію про сигнал у внутрішній черзі дескриптора `signalfd`. Цей дескриптор додається до звичайного мультиплексора `epoll`. Сигнал стає звичайною подією готовності до читання. Обробка сигналу виконується на звичайному стеку в головному циклі подій, де дозволено виділяти пам'ять, брати м'ютекси та викликати будь-які системні API.
- **Підхід C++ (через `std::atomic` та `std::stop_source`):** Обробник сигналу виконує рівно одну дію — запис у глобальний атомарний покажчик та виклик методу `initiate_shutdown()`, який використовує `compare_exchange_strong`. Це гарантує ідемпотентність: якщо операційна система надішле кілька сигналів поспіль (або користувач гарячково натисне `Ctrl+C` тричі), код згортання буде викликано рівно один раз.

### 2. Керування конкурентністю та атомарні бар'єри пам'яті

Для відстеження кількості активних запитів використовується змінна `active_requests_` із модифікатором `std::atomic<int>`.

Зверніть увагу на використання семантики пам'яті (англ. *memory ordering*):
- Під час реєстрації нового запиту (`register_active_request`) викликається `fetch_add` із розслабленою семантикою `std::memory_order_relaxed`. Тут нам потрібна лише атомарність лічильника без синхронізації сторонніх змінних пам'яті, оскільки сам запит ще не модифікував спільний стан.
- Під час декременту (`unregister_active_request`) використовується `std::memory_order_acq_rel` (acquire-release). Це критично: ми повинні гарантувати, що всі модифікації пам'яті, зроблені в процесі обробки клієнтського запиту (запис результатів у буфери, збереження транзакцій у кеш), стануть видимими іншим потокам до того, як лічильник досягне нуля і спрацює сповіщення `cv_drain_.notify_all()`.

Завдяки умові `fetch_sub(...) == 1` системний виклик сповіщення умовної змінної виконується лише тоді, коли систему залишає останній активний клієнт. Це повністю усуває паразитне навантаження на планувальник потоків (запобігає проблемі thundering herd, коли сотні заснулих потоків без потреби прокидаються на кожен декремент).

### 3. Токени зупинки C++20 та кооперативна багатопотоковість

У версії на C++ застосовано стандартний механізм C++20 `std::stop_source` та `std::stop_token`. На відміну від застарілих практик примусового вбивства потоків через `pthread_cancel` (який залишає пам'ять у неконсистентному стані та не викликає деструктори локальних об'єктів), токени зупинки реалізують **кооперативну зупинку**:
- Координатор викликає `stop_source_.request_stop()`.
- Усі робочі потоки `std::jthread` регулярно перевіряють стан токена за допомогою `st.stop_requested()`.
- Потік самостійно завершує поточну ітерацію, скидає свій локальний стан і виходить із робочої функції.
- Деструктор `std::jthread` автоматично виконує `join()`, гарантуючи повне очищення стека кожного потоку до того, як процес перейде до руйнування глобальних об'єктів.

### 4. Порядок вивільнення ресурсів і топологічне сортування

Ланцюжок залежностей у будь-якому виробничому сервісі має вигляд спрямованого ациклічного графа (DAG):
```
Мережевий слухач (Listener)
   ↓
Пул активних з'єднань (Connection Pool)
   ↓
Воркери бізнес-логіки (Workers)
   ↓
Клієнти кешу та зовнішніх RPC (Redis, HTTP-клієнти)
   ↓
Пул з'єднань із базою даних (DB Pool)
   ↓
Буферизований логер та OpenTelemetry-експортер (Log/Trace Flush)
```

Якщо порушити цей порядок і знищити базу даних до того, як воркер завершить обробку запиту, застосунок викличе звернення за нульовим покажчиком (Null Pointer Dereference) або аварійно завершиться з кодом `SIGSEGV`.

У реалізації на C++ координатор реєструє хуки очищення у списку `hooks_` і виконує їх у зворотному порядку (`rbegin()` до `rend()`). Це повністю відповідає принципу RAII: ресурси звільняються у послідовності, строго зворотній до їхнього захоплення. Якщо під час виконання хука виникає виняток, блок `try-catch` перехоплює його, записує помилку в журнал діагностики й продовжує згортання решти підсистем, не дозволяючи аварії одного компонента заблокувати звільнення інших.

### 5. Сторожовий таймер (Watchdog) і дедлайни

У розподілених системах найнебезпечніший сценарій — це зависання на сторонньому блокуванні. Наприклад, воркер надіслав HTTP-запит до сторонньої платіжної системи, а та перестала відповідати, не розриваючи TCP-з'єднання. Якщо воркер не має локального таймауту сокета, він буде чекати відповіді вічно, блокуючи умову `active_requests_ == 0`.

Координатор вирішує цю проблему за допомогою асинхронного дедлайну:
- Операція дренажу запускається в асинхронному завданні через `std::async(std::launch::async, ...)`.
- Головний потік очікує завершення майбутнього результату (future) з фіксованим тайм-аутом `drain_future.wait_for(timeout_)`.
- Якщо за відведений час (наприклад, 5 секунд) воркери не встигли згорнутися, координатор фіксує аварійне перевищення ліміту в логах і викликає `std::quick_exit(EXIT_FAILURE)`.

Виклик `std::quick_exit` замість звичайного `exit()` є важливим інженерним вибором: він завершує виконання процесу негайно, не викликаючи стандартні деструктори статичних об'єктів (які в цей момент можуть перебувати під блокуваннями завислих потоків), але закриває файлові дескриптори та повертає статус помилки батьківському процесу.

### 6. Дескрипторна гігієна та системні ресурси

Під час роботи під високим навантаженням серверний процес утримує тисячі відкритих файлових дескрипторів сокетів, каналів IPC та пайпів. Якщо координатор перед виходом не виконає явне видалення дескрипторів із мультиплексора `epoll` через `epoll_ctl(..., EPOLL_CTL_DEL, fd)`, операційна система Linux автоматично закриє їх при завершенні процесу, але пов'язані з ними внутрішні структури ядра (наприклад, сокетні буфери `sk_buff` та структури черги очікування `wait_queue_head_t`) можуть залишатися в пам'яті ядра до повного вичерпання TCP-таймаутів. Явне закриття дескрипторів координатором звільняє пам'ять ядра негайно, зменшуючи навантаження на мережевий стек хоста під час частих оновлень у кластері.

## Робота з вбудованими сховищами та транзакціями

Окремим класом ресурсів під час штатного згортання є вбудовані бази даних (наприклад, SQLite чи RocksDB). На відміну від мережевих СУБД, де клієнт лише надсилає команду закриття з'єднання через сокет, вбудовані рушії зберігають буферизований стан сторінок безпосередньо в адресному просторі процесу:

1. **Журнал випереджального запису (WAL checkpoint):** Якщо процес використовує SQLite у режимі WAL (`PRAGMA journal_mode=WAL`), записи транзакцій спочатку потрапляють у файл `-wal`. Під час штатного вимкнення координатор зобов'язаний виконати явну фіксацію контрольної точки:

:::tabs
```c
int rc = sqlite3_wal_checkpoint_v2(db, NULL, SQLITE_CHECKPOINT_TRUNCATE, NULL, NULL);
```
```cpp
if (int rc = sqlite3_wal_checkpoint_v2(db.get(), nullptr, SQLITE_CHECKPOINT_TRUNCATE, nullptr, nullptr); rc != SQLITE_OK) {
    throw std::runtime_error(sqlite3_errmsg(db.get()));
}
```
:::

Це гарантує перенесення всіх змінених сторінок пам'яті в основний файл бази даних `.db` та обнулення журналу.
 Якщо пропустити цей крок, наступний запуск застосунку витратить відчутний час на відновлення після збою, сповільнюючи ініціалізацію нового екземпляра сервісу.
2. **Мемтейбли RocksDB та LSM-дерева:** Для систем на основі LSM-дерев (Log-Structured Merge-tree) обов'язковою є операція примусового скидання оперативної таблиці `MemTable` на постійний диск у форматі SSTable (`FlushWAL(true)`). Без цього дані залишаються в нескомпактованому стані, що збільшує навантаження на дискову підсистему при холодному старті.

## Акторні моделі, реактивні потоки та Саги

У складних розподілених мікросервісних архітектурах штатне вимкнення не обмежується лише локальними потоками ОС:

1. **Акторні системи (Erlang/OTP, Akka, ProtoActor):** Під час отримання сигналу вимкнення акторний координатор надсилає системне повідомлення `PoisonPill` або викликає `GracefulStop()`. Актор перестає приймати нові повідомлення зі своєї поштової скриньки (англ. *mailbox*), дообробляє накопичену чергу, зберігає свій внутрішній стан у персистентне сховище (Event Sourcing snapshot) і лише після цього надсилає повідомлення `Terminated` своєму супервізору.
2. **Реактивні потоки зі зворотним тиском (Reactive Streams / Backpressure):** У разі використання реактивних конвеєрів видавець (Publisher) під час дренажу викликає метод `onComplete()`. Це сигналізує всім підписникам униз по ланцюгу про планове завершення потоку даних, дозволяючи їм коректно закрити вихідні буфери без генерації помилок `onError()`.
3. **Розподілені саги та компенсації (Saga Orchestration):** Якщо під час ініціації зупинки екземпляр сервісу виконує багатоетапну розподілену транзакцію (наприклад, бронювання готелю після списання коштів), координатор повинен розрізняти два випадки:
   - Якщо поточний локальний крок може бути завершений у межах виділеного вікна дедлайну, крок доводиться до кінця, а стан саги фіксується у зовнішній базі даних (Outbox table).
   - Якщо крок вимагає тривалого очікування сторонніх систем, координатор негайно ініціює компенсуючу транзакцію (скасування списання) або передає стан саги в чергу відкладеного виконання, запобігаючи «зависанню» користувацьких замовлень у невизначеному стані.
4. **Специфіка Serverless та FaaS (AWS Lambda, Cloudflare Workers):** У безсерверних середовищах життєвий цикл процесу контролюється платформою. Після обробки виклику середовище заморожує процес (freeze). Під час остаточного вимкнення контейнера FaaS надсилає сигнал зупинки через внутрішній Runtime API (наприклад, `SHUTDOWN` event). Координатор у середовищі Lambda має коротке вікно (від 500 мс до 2 с) для виклику `force_flush` телеметрії, оскільки сокети та фонові потоки примусово заморожуються платформою між викликами.

## Крайові випадки та виробничі пастки

Під час експлуатації таких координаторів у високонавантажених середовищах слід враховувати кілька тонких системних аспектів:

1. **Пастка повільних клієнтів (Slowloris під час дренажу):** Якщо клієнт повільно передає тіло запиту (наприклад, надсилає 1 байт кожні 2 секунди), він може навмисно утримувати сервер у стані дренажу до вичерпання дедлайну. Тому в момент переходу в режим дренажу координатор повинен примусово скорочувати тайм-аути читання сокетів (`SO_RCVTIMEO`) для всіх існуючих з'єднань до кількох секунд.
2. **Поведінка сокетів і прапорець `SO_LINGER`:** Якщо закрити TCP-сокет за допомогою `close()`, коли у вхідному буфері ядра ще залишаються непрочитані дані, стек TCP операційної системи надішле клієнту пакет `RST` (скидання) замість штатного `FIN`. Клієнт отримає помилку `Connection reset by peer` замість успішної відповіді 200 OK. Щоб уникнути цього, перед закриттям сокета необхідно або повністю вичитати вхідний буфер, або викликати системний виклик `shutdown(fd, SHUT_WR)` і дочекатися підтвердження від клієнта.
3. **Опитування дескрипторів у багатопотоковому середовищі:** Якщо кілька потоків одночасно викликають `epoll_wait` на одному дескрипторі epoll (патерн multi-threaded event loop), додавання прапорця `EPOLLEXCLUSIVE` або `EPOLLONESHOT` є обов'язковим для уникнення пробудження всіх потоків на одну подію сигналу.
4. **Очищення черг повідомлень і відміна оренди задач:** У разі використання брокерів повідомлень (RabbitMQ, Apache Kafka, Amazon SQS) воркер, отримавши сигнал зупинки, зобов'язаний негайно відкликати підписку на чергу (`basic.cancel` в AMQP). Для задач, які вже взяті в обробку, але гарантовано не встигнуть завершитися за час дедлайну, воркер повинен відмовитися від оренди (`nack` із повторним поверненням у чергу або явне обнулення поля `lease_until = now()` у базі даних). Це дає змогу сусіднім серверам негайно підхопити завдання, не чекаючи вичерпання загального таймауту блокування.
5. **Втрата буферизованої телеметрії:** Сучасні бібліотеки збору метрик (Prometheus Client, StatsD) та трейсингу (OpenTelemetry) накопичують діагностичні події в пам'яті у вигляді кільцевих буферів і скидають їх на диск або відправляють по мережі періодичними батчами (раз на 1–5 секунд). Якщо координатор завершить процес без примусового виклику `TracerProvider::force_flush()`, останні спани найбільш критичних транзакцій — тих, що виконувалися безпосередньо перед зупинкою або зазнали тайм-ауту під час дренажу, — будуть безповоротно втрачені.

## Тестування та верифікація в CI/CD конвеєрі

Надійність координатора штатного вимкнення не можна оцінювати теоретично; її необхідно регулярно перевіряти за допомогою автоматизованих інтеграційних тестів:

1. **Синтетичний генератор навантаження:** Під час виконання тестів запускається утиліта генерації запитів (наприклад, `wrk`, `hey` або `k6`), яка надсилає тисячі конкурентних HTTP-запитів у секунду з підтримкою HTTP/1.1 Keep-Alive та HTTP/2 multiplexing.
2. **Впорскування сигналу зупинки:** Посеред генерації навантаження автоматизований скрипт надсилає процесу сигнал:
   ```bash
   kill -15 $(pgrep coordinator_server)
   ```
3. **Критерій проходження тесту (Zero-Error Invariant):**
   - Кількість помилок з боку клієнта (`5xx Server Error`, `Connection Reset`, `Connection Refused`) повинна дорівнювати **рівно нулю**.
   - Усі запити, надіслані до моменту видалення слухача, мають отримати валідну відповідь `200 OK`.
   - Застосунок зобов'язаний завершитися з кодом виходу `0` до спрацьвування примусового таймауту тестера.
   - У логах діагностики повинні бути присутні підтвердження закриття всіх пулів та змивання буферів без повідомлень про `use-after-free` чи витоки пам'яті під керуванням Valgrind або AddressSanitizer (ASan).

## Простеження та діагностика в Linux

Перевірити коректність роботи реалізованого координатора на рівні ядра можна за допомогою утиліти `strace`:

```bash
strace -f -e trace=signalfd4,epoll_ctl,epoll_wait,close,futex ./coordinator_server
```

У виводі утиліти ви чітко побачите всі етапи протоколу:
1. Виклик `signalfd4` блокує сигнали та створює дескриптор.
2. `epoll_ctl(..., EPOLL_CTL_DEL, listen_fd)` видаляє слухаючий сокет із черги подій.
3. `close(listen_fd)` повертає порт системі, унеможливлюючи нові з'єднання.
4. Серія системних викликів `futex` будить заснулі потоки воркерів.
5. Фінальний вихід через `exit_group(0)` без витоків дескрипторів та завислих процесів.

Крім того, за допомогою утиліти `ss` (Socket Statistics) можна перевірити поведінку з'єднань під час дренажу:
```bash
ss -t -a 'sport = :8080'
```
У процесі штатного вимкнення слухаючий сокет (`LISTEN`) зникає миттєво після отримання сигналу, тоді як активні клієнтські з'єднання плавно переходять у стан `TIME_WAIT` або `CLOSE_WAIT` без раптових обривів, підтверджуючи коректне доведення всіх активних потоків даних.
