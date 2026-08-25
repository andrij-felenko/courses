# ⚙️ Власний цикл подій на epoll з таймерами та сокетами

Створення власного циклу подій розкриває внутрішню механіку роботи асинхронних рушіїв. Практична цінність власноруч написаного циклу полягає у розумінні того, як саме апаратні сигнали та системні виклики операційної системи транслюються у виклики функцій зворотного виклику (callbacks), як обчислюється час очікування ядра та як уникати деградації продуктивності при великій кількості одночасних клієнтів.

Цей проєкт реалізує самодостатній, виробничий однопотоковий цикл подій на базі системного виклику epoll ядра Linux та двійкової мін-купи для точного обліку таймерів.

---

### Принципова схема та компоненти системи

Архітектура міні-циклу подій будується навколо трьох взаємопов’язаних підсистем:

1. **Демультиплексор введення-виведення (I/O Multiplexer)**: Обгортка над підсистемою epoll. Відповідає за реєстрацію, зміну та видалення дескрипторів сокетів у червоно-чорному дереві ядра через виклик epoll_ctl(), а також за очікування подій через epoll_wait().
2. **Підсистема обліку таймерів (Timer Min-Heap)**: Двійкова мін-купа, що зберігає заплановані події у порядку зростання абсолютного монотонного часу їхнього дедлайну. Вершина купи завжди містить подію, яка має відбутися найшвидше.
3. **Головний диспетчер циклу (Event Dispatcher)**: Нескінченний цикл loop_run(), який на кожному оберті координує роботу демультиплексора та таймерної купи, викликає зареєстровані обробники сокетів та виконує прострочені таймери.

Вся система функціонує в межах одного потоку виконання без блокувань читання-запису, забезпечуючи високу швидкість обробки тисяч сокетів за константний час.

---

### Повна реалізація мовами C та C++

Нижче наведено повний вихідний код власного циклу подій. Усі сокети переводяться в неблокуючий режим за допомогою прапорця O_NONBLOCK.

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <time.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define MAX_EVENTS 64

typedef void (*event_cb)(int fd, uint32_t events, void *user_data);
typedef void (*timer_cb)(void *user_data);

typedef struct {
    uint64_t deadline_ms;
    timer_cb callback;
    void *user_data;
    uint64_t timer_id;
} timer_entry_t;

typedef struct {
    int epoll_fd;
    bool running;
    timer_entry_t *timers;
    size_t timer_count;
    size_t timer_capacity;
    uint64_t next_timer_id;
} event_loop_t;

static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

static void heap_swap(timer_entry_t *a, timer_entry_t *b) {
    timer_entry_t tmp = *a;
    *a = *b;
    *b = tmp;
}

static void heap_sift_up(event_loop_t *loop, size_t idx) {
    while (idx > 0) {
        size_t parent = (idx - 1) / 2;
        if (loop->timers[idx].deadline_ms < loop->timers[parent].deadline_ms) {
            heap_swap(&loop->timers[idx], &loop->timers[parent]);
            idx = parent;
        } else {
            break;
        }
    }
}

static void heap_sift_down(event_loop_t *loop, size_t idx) {
    while (2 * idx + 1 < loop->timer_count) {
        size_t left = 2 * idx + 1;
        size_t right = 2 * idx + 2;
        size_t smallest = idx;

        if (loop->timers[left].deadline_ms < loop->timers[smallest].deadline_ms) {
            smallest = left;
        }
        if (right < loop->timer_count && loop->timers[right].deadline_ms < loop->timers[smallest].deadline_ms) {
            smallest = right;
        }
        if (smallest != idx) {
            heap_swap(&loop->timers[idx], &loop->timers[smallest]);
            idx = smallest;
        } else {
            break;
        }
    }
}

event_loop_t* loop_create(void) {
    event_loop_t *loop = calloc(1, sizeof(event_loop_t));
    if (!loop) return NULL;

    loop->epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (loop->epoll_fd < 0) {
        free(loop);
        return NULL;
    }
    loop->running = false;
    loop->timer_capacity = 16;
    loop->timers = malloc(loop->timer_capacity * sizeof(timer_entry_t));
    return loop;
}

void loop_destroy(event_loop_t *loop) {
    if (!loop) return;
    if (loop->epoll_fd >= 0) close(loop->epoll_fd);
    free(loop->timers);
    free(loop);
}

int loop_add_fd(event_loop_t *loop, int fd, uint32_t events, event_cb cb, void *user_data) {
    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = events;
    void **binding = malloc(2 * sizeof(void*));
    binding[0] = (void*)cb;
    binding[1] = user_data;
    ev.data.ptr = binding;

    return epoll_ctl(loop->epoll_fd, EPOLL_CTL_ADD, fd, &ev);
}

uint64_t loop_add_timer(event_loop_t *loop, uint64_t delay_ms, timer_cb cb, void *user_data) {
    if (loop->timer_count == loop->timer_capacity) {
        loop->timer_capacity *= 2;
        loop->timers = realloc(loop->timers, loop->timer_capacity * sizeof(timer_entry_t));
    }
    size_t idx = loop->timer_count++;
    uint64_t id = ++loop->next_timer_id;
    loop->timers[idx] = (timer_entry_t){
        .deadline_ms = get_monotonic_ms() + delay_ms,
        .callback = cb,
        .user_data = user_data,
        .timer_id = id
    };
    heap_sift_up(loop, idx);
    return id;
}

void loop_run(event_loop_t *loop) {
    struct epoll_event events[MAX_EVENTS];
    loop->running = true;

    while (loop->running) {
        uint64_t now = get_monotonic_ms();

        // 1. Обчислюємо таймаут для epoll_wait
        int timeout_ms = -1;
        if (loop->timer_count > 0) {
            if (loop->timers[0].deadline_ms <= now) {
                timeout_ms = 0; // Вже збіг — негайний вихід
            } else {
                timeout_ms = (int)(loop->timers[0].deadline_ms - now);
            }
        }

        // 2. Спимо у демультиплексорі ядра
        int nfds = epoll_wait(loop->epoll_fd, events, MAX_EVENTS, timeout_ms);
        if (nfds < 0 && errno != EINTR) {
            break;
        }

        // 3. Обробляємо готові сокетні події
        for (int i = 0; i < nfds; ++i) {
            void **binding = (void**)events[i].data.ptr;
            event_cb cb = (event_cb)binding[0];
            void *ud = binding[1];
            if (cb) {
                cb(0, events[i].events, ud);
            }
        }

        // 4. Обробляємо всі таймери, що збігли на поточний момент
        now = get_monotonic_ms();
        while (loop->timer_count > 0 && loop->timers[0].deadline_ms <= now) {
            timer_entry_t expired = loop->timers[0];
            loop->timers[0] = loop->timers[--loop->timer_count];
            if (loop->timer_count > 0) {
                heap_sift_down(loop, 0);
            }
            if (expired.callback) {
                expired.callback(expired.user_data);
            }
        }
    }
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <chrono>
#include <functional>
#include <memory>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>

class EventLoop {
public:
    using EventCallback = std::function<void(uint32_t events)>;
    using TimerCallback = std::function<void()>;

    EventLoop() {
        epoll_fd_ = epoll_create1(EPOLL_CLOEXEC);
        if (epoll_fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }
    }

    ~EventLoop() {
        if (epoll_fd_ >= 0) {
            ::close(epoll_fd_);
        }
    }

    void add_fd(int fd, uint32_t events, EventCallback cb) {
        auto cb_ptr = std::make_unique<EventCallback>(std::move(cb));
        epoll_event ev{};
        ev.events = events;
        ev.data.ptr = cb_ptr.get();

        if (epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, fd, &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD failed");
        }
        fd_callbacks_.push_back(std::move(cb_ptr));
    }

    void add_timer(std::chrono::milliseconds delay, TimerCallback cb) {
        auto deadline = std::chrono::steady_clock::now() + delay;
        timers_.push(TimerEntry{deadline, ++next_id_, std::move(cb)});
    }

    void stop() noexcept {
        running_ = false;
    }

    void run() {
        running_ = true;
        constexpr int max_events = 64;
        epoll_event events[max_events];

        while (running_) {
            auto now = std::chrono::steady_clock::now();

            // 1. Розрахунок таймауту для ядра
            int timeout_ms = -1;
            if (!timers_.empty()) {
                if (timers_.top().deadline <= now) {
                    timeout_ms = 0;
                } else {
                    auto diff = std::chrono::duration_cast<std::chrono::milliseconds>(
                        timers_.top().deadline - now
                    ).count();
                    timeout_ms = static_cast<int>(diff);
                }
            }

            // 2. Очікування подій від ядра
            int nfds = epoll_wait(epoll_fd_, events, max_events, timeout_ms);
            if (nfds < 0 && errno != EINTR) {
                throw std::system_error(errno, std::generic_category(), "epoll_wait failed");
            }

            // 3. Виклик обробників I/O
            for (int i = 0; i < nfds; ++i) {
                auto* cb = static_cast<EventCallback*>(events[i].data.ptr);
                if (cb && *cb) {
                    (*cb)(events[i].events);
                }
            }

            // 4. Виклик прострочених таймерів
            now = std::chrono::steady_clock::now();
            while (!timers_.empty() && timers_.top().deadline <= now) {
                auto entry = std::move(const_cast<TimerEntry&>(timers_.top()));
                timers_.pop();
                if (entry.callback) {
                    entry.callback();
                }
            }
        }
    }

private:
    struct TimerEntry {
        std::chrono::steady_clock::time_point deadline;
        uint64_t id;
        TimerCallback callback;

        bool operator>(const TimerEntry& other) const noexcept {
            return deadline > other.deadline;
        }
    };

    int epoll_fd_{-1};
    bool running_{false};
    uint64_t next_id_{0};
    std::priority_queue<TimerEntry, std::vector<TimerEntry>, std::greater<TimerEntry>> timers_;
    std::vector<std::unique_ptr<EventCallback>> fd_callbacks_;
};
```
:::

---

### Детальний розбір алгоритмів та внутрішнього стану

Розглянемо ключові інженерні рішення, закладені в реалізацію:

#### 1. Прапорець EPOLL_CLOEXEC при створенні дескриптора
Системний виклик `epoll_create1(EPOLL_CLOEXEC)` є обов’язковим для безпечних серверних застосунків. Прапорець `EPOLL_CLOEXEC` гарантує, що у випадку виклику сімейства функцій `execve()` новостворений процес нащадок не успадкує відкритий файловий дескриптор екземпляра `epoll`. Без цього прапорця виникає витік дескрипторів, що блокує закриття сокетів та коректне вивільнення портів.

#### 2. Забезпечення інваріанту двійкової купи (Min-Heap Invariants)
Масив таймерів організовано так, що для кожного вузла з індексом `i` лівий нащадок знаходиться за позицією `2*i + 1`, а правий — `2*i + 2`. Батьківський вузол обчислюється за формулою `(i - 1) / 2`.
* Додавання нового таймера (`loop_add_timer`) записує елемент у кінець масиву і піднімає його вгору (`heap_sift_up`) зі складністю `O(log N)`.
* Вилучення простроченого таймера замінює корінь останнім елементом масиву і опускає його вниз (`heap_sift_down`) зі складністю `O(log N)`.
* Пошук найближчого дедлайну виконується за константний час `O(1)`, оскільки найближчий таймер завжди розташований у нульовому елементі масиву `loop->timers[0]`.

#### 3. Реєстрація користувацьких контекстів через epoll_data_t
Структура `struct epoll_event` містить об’єднання `epoll_data_t`, де поле `ptr` дозволяє зберегти довільний вказівник. Ми виділяємо динамічну пару вказівників (адреса функції-колбека та користувацькі дані `user_data`). Це дозволяє диспетчеру виконувати обробник без додаткового пошуку в хеш-таблицях за дескриптором.

---

### Тонкощі та крайові випадки експлуатації

1. **Захист від стрибків часу (Monotonic Clock)**: Для обліку інтервалів таймерів категорично не можна використовувати системний астрономічний годинник (`CLOCK_REALTIME` або `gettimeofday`). Якщо системна служба NTP оновить час або оператор переведе годинник назад, таймери на базі астрономічного часу зависнуть на роки. Використання монотонного годинника (`CLOCK_MONOTONIC` у C або `std::chrono::steady_clock` у C++) гарантує, що лічильник часу рухається строго вперед із фіксованою швидкістю генератора тактів процесора.
2. **Коректна обробка переривань ядра (EINTR)**: Якщо потік очікує подій у системному виклику `epoll_wait()`, надходження будь-якого сигналу ОС (наприклад, `SIGCHLD`, `SIGHUP` або `SIGWINCH`) перериває системний виклик, повертаючи `-1` зі встановленням змінної `errno = EINTR`. Цикл зобов’язаний проігнорувати цю помилку, перерахувати поточний час і безпечно повторити виклик демультиплексора.
3. **Безпечне видалення сокетів під час диспетчеризації**: Якщо один із зворотних викликів всередині циклу закриває сокет через `close(fd)` або видаляє його з `epoll`, вказівник у масиві подій `events[i]` може стати недійсним. У промислових циклах подій (як-от `libuv`) структури прив’язки захищаються версіонуванням або двоетапним відкладеним видаленням на фазі очищення (Close Phase).
4. **Порівняння режимів сповіщення: Level-Triggered (LT) проти Edge-Triggered (ET)**: За замовчуванням демультиплексор `epoll` працює у режимі Level-Triggered. Це означає, що доки в буфері сокета залишаються непрочитані байти, кожен наступний виклик `epoll_wait()` негайно повертатиме подію готовності `EPOLLIN`. Якщо увімкнути прапорець `EPOLLET` (Edge-Triggered), ядро сповістить про готовність сокета рівно один раз — у момент переходу стану з «немає даних» на «дані з'явилися». У режимі ET застосунок зобов'язаний вичитувати сокет у циклі `while` блоками фіксованого розміру доти, доки виклик `read()` не поверне помилку `-1` зі значенням `errno == EAGAIN` або `EWOULDBLOCK`. Якщо цього не зробити, решта байтів зависне в буфері ядра назавжди, оскільки нових сповіщень ядро не надішле до прибуття наступного TCP-сегмента.
5. **Скасування таймерів та стратегія надгробків (Tombstones)**: Видалення довільного таймера з середини двійкової купи вимагає або лінійного пошуку елемента за `O(N)` з подальшим просіюванням, або підтримки зворотної індексної таблиці `timer_id -> heap_index`. Найпростішою та високоефективною альтернативою для високонавантажених систем є маркування таймера як скасованого (встановлення `callback = NULL` або прапорця `canceled = true`). Коли таймер згодом природно піднімається на вершину купи при настанні дедлайну, диспетчер просто вилучає його за `O(log N)` та пропускає виклик функції.
6. **Діагностика та трасування через системні утиліти**: Роботу власного циклу подій легко проінспектувати у режимі реального часу без модифікації коду за допомогою утиліти `strace`. Команда `strace -e epoll_create1,epoll_ctl,epoll_wait,clock_gettime -r ./mini_event_loop` дозволяє побачити точний відносний час між ітераціями, розраховані мілісекунди таймаутів для кожного виклику `epoll_wait`, а також усі реєстрації мережевих сокетів ядра.
