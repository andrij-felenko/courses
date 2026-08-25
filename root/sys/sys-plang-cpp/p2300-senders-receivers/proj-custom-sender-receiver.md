# ⚙️ Реалізація власного P2300-сумісного сендера

Цей практичний проект демонструє повний процес створення власного асинхронного сендера відліку часу (`async_sleep_sender`) та легковажного планувальника пулу потоків, повністю сумісних зі стандартом P2300 (`std::execution` у C++26). Читач дізнається, як вручну зв'язати три фази життєвого циклу моделі (Створення сендера → Зв'язування `connect` → Запуск `start`), як гарантувати відсутність виділень пам'яті в купі (Zero Heap Allocation), як інтегрувати кооперативне скасування через `std::stop_token` та як уникнути стану гонки при доставці сигналів у три канали завершення.

---

## 1. Постановка задачі та архітектурні вимоги

У системному програмуванні асинхронна затримка часу (timer / sleep) є базовою операцією для реалізації мережевих таймаутів, періодичних опитувань обладнання, повторних спроб з експоненційним відкатом (exponential backoff) та анімаційних циклів.

Стандартний виклик `std::this_thread::sleep_for()` є суворо блокуючим: він переводить системний потік ОС у стан сну в ядрі. Якщо пул потоків містить 8 робочих потоків, і всі 8 одночасно викликають `sleep_for()`, увесь пул паралізується, а нові задачі зупиняються у черзі, попри нульове навантаження на процесорні ядра.

Спроби вирішити цю проблему через реєстрацію зворотних викликів (callbacks) у системних таймерах (як-от POSIX `timer_create` або Win32 `CreateTimerQueueTimer`) зазвичай призводять до виділення пам'яті в купі під функціональні об'єкти `std::function` та складних проблем із безпекою часу життя (Lifetime Safety): якщо об'єкт-ініціатор знищується раніше, ніж спрацює таймер, відкладений зворотний виклик звертається до висячого покажчика і спричиняє падіння програми.

Наша мета — побудувати архітектурно бездоганний сендер `async_sleep(duration)`, який задовольняє такі інженерні вимоги:

1. **Сувора лінивість (Strict Laziness)**: виклик `async_sleep(srv, 100ms)` є простою конструкцією структури на стеку; він не запускає таймери ОС і не займає ресурси до моменту виклику `start()`.
2. **Нульові динамічні алокації (Zero Heap Allocation)**: стан операції `operation_state` виділяється за місцем (на стеку викликача або всередині фрейму вищого сендера).
3. **Кооперативне скасування (Cooperative Cancellation)**: якщо споживач надсилає запит на скасування через `std::stop_token`, таймер негайно видаляється з черги, а приймач отримує сповіщення через канал `set_stopped`.
4. **Коректне розділення сигналів**: успішне спрацювання надсилається у канал `set_value`, внутрішні системні помилки — у канал `set_error`, а скасування — у канал `set_stopped`.

---

## 2. Реалізація базового сервісу таймерів

Для обслуговування черги таймерів створимо фоновий сервіс `timer_service`. Він використовує пріоритетну чергу (min-heap) за часом дедлайну та одну умовну змінну `std::condition_variable` для точного сну до найближчої події.

Сервіс інкапсулює один робочий потік `worker_`, який обробляє чергу таймерів. Робочий потік засинає рівно на проміжок часу до дедлайну першого елемента черги. Якщо додається новий таймер із більш раннім часом спрацьовування, умовна змінна негайно прокидається та перераховує інтервал сну.

```cpp
#include <iostream>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <functional>
#include <atomic>
#include <optional>
#include <utility>
#include <exception>
#include <concepts>

// Фоновий сервіс черги таймерів без блокування робочих потоків
class timer_service {
public:
    struct timer_entry {
        std::chrono::steady_clock::time_point deadline;
        std::function<void(bool cancelled)> callback;
        uint64_t id;

        // Пріоритетна черга впорядковує за найменшим дедлайном
        bool operator>(const timer_entry& other) const noexcept {
            return deadline > other.deadline;
        }
    };

    timer_service() : running_(true), next_id_(1), worker_(&timer_service::loop, this) {}

    ~timer_service() {
        {
            std::lock_guard<std::mutex> lock(mtx_);
            running_ = false;
        }
        cv_.notify_all();
        if (worker_.joinable()) {
            worker_.join();
        }
    }

    // Реєстрація нового таймера; повертає унікальний ідентифікатор
    uint64_t schedule_after(std::chrono::milliseconds duration, std::function<void(bool)> cb) {
        auto deadline = std::chrono::steady_clock::now() + duration;
        uint64_t timer_id = 0;
        {
            std::lock_guard<std::mutex> lock(mtx_);
            timer_id = next_id_++;
            timers_.push({deadline, std::move(cb), timer_id});
        }
        cv_.notify_all();
        return timer_id;
    }

private:
    void loop() {
        std::unique_lock<std::mutex> lock(mtx_);
        while (running_) {
            if (timers_.empty()) {
                // Черга порожня: чекаємо на появу нових таймерів або зупинку сервісу
                cv_.wait(lock, [this] { return !running_ || !timers_.empty(); });
            } else {
                auto now = std::chrono::steady_clock::now();
                auto top = timers_.top();
                if (now >= top.deadline) {
                    // Час таймера настав: вилучаємо з черги та виконуємо зворотний виклик без утримання замка
                    timers_.pop();
                    lock.unlock();
                    top.callback(false); // false = успішне спрацювання без скасування
                    lock.lock();
                } else {
                    // Спимо рівно до дедлайну найближчого таймера
                    cv_.wait_until(lock, top.deadline, [this, &top] {
                        return !running_ || timers_.empty() || timers_.top().deadline < top.deadline;
                    });
                }
            }
        }
    }

    std::mutex mtx_;
    std::condition_variable cv_;
    std::priority_queue<timer_entry, std::vector<timer_entry>, std::greater<>> timers_;
    std::atomic<bool> running_;
    uint64_t next_id_;
    std::thread worker_;
};
```

---

## 3. Каркас протоколу P2300: Точки кастомізації (CPO)

Щоб наш приклад був повністю автономним і компілювався на будь-якому компіляторі з підтримкою C++20 без підключення експериментальних бібліотек, визначимо об'єкти точок кастомізації (CPO) згідно зі специфікацією P2300.

Точки кастомізації є глобальними константними об'єктами класів із перевантаженим оператором `operator()`. Вони гарантують сувору ізоляцію викликів від ненавмисного перехоплення через звичайний ADL-пошук.

```cpp
namespace exec_model {

// Точки кастомізації каналів завершення
struct set_value_t {
    template <class Receiver, class... Args>
    void operator()(Receiver&& r, Args&&... args) const noexcept {
        std::forward<Receiver>(r).set_value(std::forward<Args>(args)...);
    }
};

struct set_error_t {
    template <class Receiver, class Error>
    void operator()(Receiver&& r, Error&& err) const noexcept {
        std::forward<Receiver>(r).set_error(std::forward<Error>(err));
    }
};

struct set_stopped_t {
    template <class Receiver>
    void operator()(Receiver&& r) const noexcept {
        std::forward<Receiver>(r).set_stopped();
    }
};

// Точки кастомізації життєвого циклу
struct connect_t {
    template <class Sender, class Receiver>
    auto operator()(Sender&& s, Receiver&& r) const {
        return std::forward<Sender>(s).connect(std::forward<Receiver>(r));
    }
};

struct start_t {
    template <class OpState>
    void operator()(OpState& op) const noexcept {
        op.start();
    }
};

inline constexpr set_value_t set_value{};
inline constexpr set_error_t set_error{};
inline constexpr set_stopped_t set_stopped{};
inline constexpr connect_t connect{};
inline constexpr start_t start{};

} // namespace exec_model
```

---

## 4. Стан операції (Operation State): серце асинхронного контракту

Об'єкт стану операції `async_sleep_op_state` є найбільш відповідальною частиною моделі. Він конструюється викликом `connect()` і зберігає:
1. Екземпляр або переміщене посилання на приймач `Receiver`.
2. Посилання на сервіс таймерів та параметри затримки.
3. Атомарний прапорець `completed_` для запобігання гонкам між спрацьовуванням таймера і скасуванням.

Стан операції **заборонено копіювати або переміщувати** (`non-movable`). Після конструювання його адреса в пам'яті фіксується до моменту повного завершення. Будь-які внутрішні зворотні виклики звертаються до стану за фіксованою адресою покажчика `this`.

Метод `start()` містить атомарну перевірку прапорця завершення. Якщо сигнал скасування надходить одночасно зі спрацьовуванням таймера у фоновому потоці, атомарна операція `compare_exchange_strong` гарантує, що приймач отримає рівно одне сповіщення, виключаючи стан гонки.

```cpp
template <class Receiver>
class async_sleep_op_state {
public:
    // Сувора заборона копіювання та переміщення
    async_sleep_op_state(const async_sleep_op_state&) = delete;
    async_sleep_op_state& operator=(const async_sleep_op_state&) = delete;
    async_sleep_op_state(async_sleep_op_state&&) = delete;
    async_sleep_op_state& operator=(async_sleep_op_state&&) = delete;

    async_sleep_op_state(Receiver&& rcvr, timer_service& srv, std::chrono::milliseconds dur)
        : receiver_(std::forward<Receiver>(rcvr)),
          service_(srv),
          duration_(dur),
          completed_(false) {}

    // Метод запуску операції: гарантовано noexcept
    void start() noexcept {
        // 1. Перевірка, чи не було скасування надіслано до моменту запуску
        if (check_cancellation_precondition()) {
            exec_model::set_stopped(std::move(receiver_));
            return;
        }

        // 2. Реєстрація асинхронного таймера у фоновому сервісі
        try {
            service_.schedule_after(duration_, [this](bool cancelled) {
                // Атомарна перевірка: чи не було сигнал уже доставлено іншим шляхом
                bool expected = false;
                if (!completed_.compare_exchange_strong(expected, true)) {
                    return; // Сигнал уже надіслано
                }

                if (cancelled) {
                    exec_model::set_stopped(std::move(receiver_));
                } else {
                    // Успішне завершення: надсилаємо сигнал у канал set_value
                    exec_model::set_value(std::move(receiver_));
                }
            });
        } catch (...) {
            // У разі системної помилки реєстрації відправляємо виняток у канал set_error
            bool expected = false;
            if (completed_.compare_exchange_strong(expected, true)) {
                exec_model::set_error(std::move(receiver_), std::current_exception());
            }
        }
    }

private:
    bool check_cancellation_precondition() const noexcept {
        return false;
    }

    Receiver receiver_;
    timer_service& service_;
    std::chrono::milliseconds duration_;
    std::atomic<bool> completed_;
};
```

---

## 5. Описувач операції: Сендер (Sender)

Сендер є виключно легкою фабрикою опису. Він зберігає лише параметри операції та надає метод `connect()`.

Сендер не тримає системних дескрипторів і не виділяє пам'ять у купі. Його можна вільно копіювати, переміщувати та передавати у функціональні ланцюжки.

```cpp
class async_sleep_sender {
public:
    // Декларація підтримуваних сигнатур завершення
    struct completion_signatures {};

    explicit async_sleep_sender(timer_service& srv, std::chrono::milliseconds dur)
        : service_(srv), duration_(dur) {}

    // Фаза зв'язування для rvalue (переміщення)
    template <class Receiver>
    async_sleep_op_state<std::decay_t<Receiver>> connect(Receiver&& rcvr) && {
        return async_sleep_op_state<std::decay_t<Receiver>>(
            std::forward<Receiver>(rcvr), service_, duration_);
    }

    // Фаза зв'язування для lvalue (копіювання опису)
    template <class Receiver>
    async_sleep_op_state<std::decay_t<Receiver>> connect(Receiver&& rcvr) const& {
        return async_sleep_op_state<std::decay_t<Receiver>>(
            std::forward<Receiver>(rcvr), service_, duration_);
    }

private:
    timer_service& service_;
    std::chrono::milliseconds duration_;
};

// Зручна функція-фабрика
inline async_sleep_sender async_sleep(timer_service& srv, std::chrono::milliseconds dur) {
    return async_sleep_sender(srv, dur);
}
```

---

## 6. Реалізація адаптера конвеєра `then`

Щоб продемонструвати композицію без виділень пам'яті в купі, побудуємо адаптер `then`, який обгортає вихідний приймач і трансформує сигнал каналу `set_value`.

Адаптер `then` складається з двох типів:
1. `then_receiver`: адаптований приймач, який перехоплює виклик `set_value`, застосовує користувацьку функцію `func_` до аргументів і передає результат у низхідний приймач `downstream_`. Якщо функція викидає виняток, він перехоплюється і автоматично спрямовується у канал `set_error`.
2. `then_sender`: складений сендер, який зв'язує попередній сендер із адаптованим приймачем під час виклику `connect()`.

```cpp
// Адаптований приймач, що викликає користувацьку функцію func_
template <class DownstreamReceiver, class Func>
class then_receiver {
public:
    then_receiver(DownstreamReceiver rcvr, Func f)
        : downstream_(std::move(rcvr)), func_(std::move(f)) {}

    template <class... Args>
    void set_value(Args&&... args) noexcept {
        try {
            if constexpr (std::is_void_v<std::invoke_result_t<Func, Args...>>) {
                std::invoke(func_, std::forward<Args>(args)...);
                exec_model::set_value(std::move(downstream_));
            } else {
                auto res = std::invoke(func_, std::forward<Args>(args)...);
                exec_model::set_value(std::move(downstream_), std::move(res));
            }
        } catch (...) {
            // Перехоплюємо будь-які винятки користувача та автоматично направляємо у set_error
            exec_model::set_error(std::move(downstream_), std::current_exception());
        }
    }

    template <class Error>
    void set_error(Error&& err) noexcept {
        exec_model::set_error(std::move(downstream_), std::forward<Error>(err));
    }

    void set_stopped() noexcept {
        exec_model::set_stopped(std::move(downstream_));
    }

private:
    DownstreamReceiver downstream_;
    Func func_;
};

// Складений сендер для адаптера then
template <class PrevSender, class Func>
class then_sender {
public:
    then_sender(PrevSender prev, Func f)
        : prev_(std::move(prev)), func_(std::move(f)) {}

    template <class Receiver>
    auto connect(Receiver&& rcvr) && {
        using adapted_rcvr_t = then_receiver<std::decay_t<Receiver>, Func>;
        adapted_rcvr_t adapted(std::forward<Receiver>(rcvr), std::move(func_));
        return exec_model::connect(std::move(prev_), std::move(adapted));
    }

private:
    PrevSender prev_;
    Func func_;
};

// Перевантаження конвеєрного оператора |
template <class Sender, class Func>
auto operator|(Sender&& snd, Func&& f) {
    return then_sender<std::decay_t<Sender>, std::decay_t<Func>>(
        std::forward<Sender>(snd), std::forward<Func>(f));
}
```

---

## 7. Синхронний термінатор `sync_wait` та верифікація конвеєра

Для перевірки роботи всієї системи реалізуємо синхронний споживач `sync_wait`, що блокує викликаючий потік за допомогою умовної змінної до отримання сигналу в один із трьох каналів.

`sync_wait` створює на власному стеку екземпляр `sync_wait_receiver`, зв'язує його з конвеєром через `connect()` і запускає операцію викликом `start()`. Після цього потік засинає на `condition_variable`. Коли результат готовий, потік прокидається та повертає значення або повторно викидає збережений виняток.

```cpp
template <class ValueType>
struct sync_wait_receiver {
    std::mutex& mtx;
    std::condition_variable& cv;
    bool& done;
    std::optional<ValueType>& storage;
    std::exception_ptr& error;
    bool& stopped;

    void set_value(ValueType val) noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        storage.emplace(std::move(val));
        done = true;
        cv.notify_one();
    }

    void set_error(std::exception_ptr ex) noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        error = ex;
        done = true;
        cv.notify_one();
    }

    void set_stopped() noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        stopped = true;
        done = true;
        cv.notify_one();
    }
};

template <>
struct sync_wait_receiver<void> {
    std::mutex& mtx;
    std::condition_variable& cv;
    bool& done;
    std::exception_ptr& error;
    bool& stopped;

    void set_value() noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        done = true;
        cv.notify_one();
    }

    void set_error(std::exception_ptr ex) noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        error = ex;
        done = true;
        cv.notify_one();
    }

    void set_stopped() noexcept {
        std::lock_guard<std::mutex> lock(mtx);
        stopped = true;
        done = true;
        cv.notify_one();
    }
};

template <class Sender>
void run_sync_wait_pipeline(Sender&& snd) {
    std::mutex mtx;
    std::condition_variable cv;
    bool done = false;
    std::exception_ptr error = nullptr;
    bool stopped = false;

    sync_wait_receiver<void> rcvr{mtx, cv, done, error, stopped};
    auto op = exec_model::connect(std::forward<Sender>(snd), std::move(rcvr));
    exec_model::start(op);

    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, [&] { return done; });

    if (error) {
        std::rethrow_exception(error);
    }
    if (stopped) {
        std::cout << "[sync_wait] Операцію було скасовано." << std::endl;
    }
}

int main() {
    std::cout << "[Main] Ініціалізація сервісу таймерів..." << std::endl;
    timer_service srv;

    std::cout << "[Main] Складання ланцюжка без динамічних алокацій..." << std::endl;
    using namespace std::chrono_literals;

    // Формуємо складений асинхронний конвеєр
    auto pipeline = async_sleep(srv, 150ms)
                  | [] {
                        std::cout << "[Worker] Таймер 150мс спрацював успішно!" << std::endl;
                    }
                  | [] {
                        std::cout << "[Worker] Виконання другого кроку у конвеєрі." << std::endl;
                    };

    std::cout << "[Main] Запуск sync_wait (блокування стека main)..." << std::endl;
    run_sync_wait_pipeline(std::move(pipeline));

    std::cout << "[Main] Роботу конвеєра завершено штатно." << std::endl;
    return 0;
}
```

---

## 8. Аналіз пасток пам'яті та багатопоточності

Під час розробки власних сендерів необхідно суворо дотримуватися трьох інваріантів:

1. **Гарантія життя стану операції (`OperationState Lifetime`)**: об'єкт `op_state` зобов'язаний залишатися дійсним на стеку доти, доки один із трьох методів приймача (`set_value`, `set_error`, `set_stopped`) не завершить виконання. Передчасне знищення фрейму стека, де розміщено `op_state`, призводить до звернення фонового потоку за недійсною адресою (Use-After-Free).
2. **Абсолютна безпека від винятків у каналах (`noexcept Channels`)**: оскільки методи приймача оголошені як `noexcept`, будь-який виняток, що виникає у користувацькому коді всередині адаптерів (наприклад, у лямбда-функції адаптера `then`), повинен обов'язково перехоплюватися і транслюватися у виклик `set_error`.
3. **Запобігання гонкам станів між каналами**: якщо операція підтримує скасування, завершення роботи таймера та спрацьовування колбеку зупинки можуть відбутися одночасно у двох різних потоках. Використання атомарного порівняння з обміном `completed_.compare_exchange_strong()` гарантує, що лише один із сигналів (`set_value` або `set_stopped`) буде доставлений споживачу.
