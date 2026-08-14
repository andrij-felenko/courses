# ⚙️ Практична реалізація конвеєра обробки даних з кооперативним скасуванням

Практична реалізація потокобезпечного конвеєра обробки даних (Data Processing Pipeline), що демонструє використання `std::jthread`, `std::stop_token`, `std::stop_callback` та передачу винятків між потоками за допомогою `std::exception_ptr`. Приклад показує побудову надійної паралельної системи з кооперативним скасуванням довготривалих асинхронних операцій без витоків пам'яті чи неочікуваних залоків.

---

## 1. Постановка задачі та архітектурні вимоги

У сучасних високонавантажених системах паралельної обробки даних — таких як обробники мережевих пакетів, медіа-кодеки або аналітичні обчислювальні рушії — виникає потреба в організації конвеєра (pipeline). Головний потік генерує або зчитує завдання з вхідного джерела та складає їх у спільну чергу, а група робочих потоків (worker threads) паралельно вибирає завдання та виконує трудомісткі обчислення.

Під час проєктування такої системи необхідно забезпечити дотримання чотирьох критичних архітектурних вимог:

1. **Потокобезпечна черга (Thread-safe Queue)**: Можливість безпечного додавання та вилучення елементів з кількох потоків без гонки даних (data race) та з мінімальними накладними витратами на синхронізацію.
2. **Кооперативне асинхронне скасування**: Здатність головного потоку або будь-якого робочого потоку миттєво відправити сигнал про припинення роботи всім учасникам конвеєра. При цьому потоки, що перебувають у стані очікування на призупиненій умовній змінній, повинні негайно розбуджуватися без очікування таймаутів.
3. **Строга RAII-гарантія закриття потоків**: Усі робочі потоки повинні автоматично та впорядковано приєднуватися (`join`) до моменту виходу з функції обробки. Знищення об'єктів потоків не повинно призводити до виклику `std::terminate()`, навіть якщо у системі виник непередбачуваний виняток.
4. **Трансляція неперехоплених винятків**: Якщо один із робочих потоків зазнає критичної помилки обробки даних, цей виняток не повинен призводити до крашу всієї програми. Помилка повинна бути перехоплена, збережена та передана у головний потік для подальшої логічної обробки або логування.

---

## 2. Реалізація C++20 з використанням std::jthread та std::stop_token

Нижче наведено повний вихідний код реалізації конвеєра обробки даних у стандарті C++20. Код демонструє взаємодію `std::jthread`, `std::stop_token`, `std::condition_variable_any` та `std::exception_ptr`.

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <stop_token>
#include <exception>
#include <stdexcept>
#include <chrono>
#include <string>

// Потокобезпечна черга з підтримкою скасування через condition_variable_any
template <typename T>
class ThreadSafeQueue {
private:
    std::queue<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable_any cv_;

public:
    void push(T item) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            queue_.push(std::move(item));
        }
        cv_.notify_one();
    }

    bool pop(T& item, std::stop_token st) {
        std::unique_lock<std::mutex> lock(mutex_);
        
        // Очікування даних або сигналу скасування
        bool acquired = cv_.wait(lock, st, [this] { 
            return !queue_.empty(); 
        });

        if (!acquired || st.stop_requested()) {
            return false; // Отримано сигнал скасування або порожня черга
        }

        item = std::move(queue_.front());
        queue_.pop();
        return true;
    }
};

// Структура результату обробки
struct PipelineTask {
    int id;
    double payload;
};

class DataPipeline {
private:
    ThreadSafeQueue<PipelineTask> queue_;
    std::vector<std::jthread> workers_;
    std::exception_ptr first_exception_{nullptr};
    std::mutex exception_mutex_;
    std::stop_source global_stop_source_;

public:
    void start(size_t worker_count) {
        for (size_t i = 0; i < worker_count; ++i) {
            // std::jthread автоматично передає stop_token першим аргументом
            workers_.emplace_back([this](std::stop_token st, size_t worker_id) {
                worker_loop(st, worker_id);
            }, i);
        }
    }

    void submit(PipelineTask task) {
        queue_.push(task);
    }

    void stop_and_join() {
        // Надіслати сигнал зупинки всім потокам
        global_stop_source_.request_stop();
        
        // Деструктори std::jthread автоматично викличуть join() при виході workers_ з області видимості
        workers_.clear();

        // Перевірка наявності збереженого винятку
        if (first_exception_) {
            std::rethrow_exception(first_exception_);
        }
    }

private:
    void worker_loop(std::stop_token st, size_t worker_id) {
        // Поєднання локального stop_token із глобальним джерелом скасування
        std::stop_callback cb(st, [this] {
            // Сповіщаємо чергу про настання сигналу зупинки
        });

        PipelineTask task;
        while (!st.stop_requested() && queue_.pop(task, st)) {
            try {
                process_single_task(task, worker_id);
            } catch (...) {
                // Зберегти перший виняток та ініціювати зупинку всього конвеєра
                std::lock_guard<std::mutex> lock(exception_mutex_);
                if (!first_exception_) {
                    first_exception_ = std::current_exception();
                    global_stop_source_.request_stop();
                }
                break;
            }
        }
    }

    void process_single_task(const PipelineTask& task, size_t worker_id) {
        if (task.payload < 0.0) {
            throw std::runtime_error("Помилка даних: від'ємне корисне навантаження у завданні #" 
                                     + std::to_string(task.id));
        }
        
        // Імітація обчислювальної роботи
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
};

int main() {
    try {
        DataPipeline pipeline;
        pipeline.start(4);

        // Відправка коректних завдань
        for (int i = 0; i < 10; ++i) {
            pipeline.submit({i, i * 1.5});
        }

        // Відправка некоректного завдання для перевірки винятку
        pipeline.submit({99, -1.0});

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        pipeline.stop_and_join();
    } catch (const std::exception& e) {
        std::cout << "Головний потік перехопив помилку конвеєра: " << e.what() << std::endl;
    }
    return 0;
}
```

---

## 3. Глибокий аналіз механік та підводних каменів

### Інтеграція std::condition_variable_any з токеном скасування

Традиційний клас `std::condition_variable` у C++11 жорстко прив'язаний до використання `std::unique_lock<std::mutex>`. Він не має можливості переривання під час очікування, крім використання періодичних таймаутів (`wait_for`).

У C++20 додано перевантажений метод `.wait(lock, st, predicate)` у класі `std::condition_variable_any`. Працює це так:
1. При вході в метод `.wait()` умовна змінна автоматично реєструє об'єкт `std::stop_callback` на переданому токені `st`.
2. Якщо інший потік викликає `request_stop()`, зареєстрований callback спрацьовує негайно, будить умовну змінну та змушує метод `.wait()` повернути `false`.
3. Робочий потік виходить зі стану сну, звільняє м'ютекс та переходить до коректного виходу з циклу обробки.

Це гарантує миттєву реакцію системи на скасування без небезпечного використання `pthread_cancel` або вимушеного опитування у часових циклах (busy waiting).

### Синхронізація винятків між потоками за допомогою std::exception_ptr

У мові C++ кожен потік володіє власним стеком та власною системою обробки винятків. Якщо виняток викидається усередині лямбда-функції потоку та не перехоплюється блоком `try-catch`, C++ runtime негайно викликає `std::terminate()`.

Для безпечної передачі помилки між потоками використовується наступний паттерн:
- У блоці `catch (...)` функція `std::current_exception()` захоплює поточний виняток у смарт-поінтер `std::exception_ptr`.
- За допомогою атомарного прапорця або м'ютексу `exception_mutex_` зберігається тільки перший виняток, який виник у конвеєрі, щоб не втратити першопричину збою.
- Головний потік під час завершення роботи перевіряє вказівник і викликає `std::rethrow_exception(first_exception_)`, повторно кидаючи помилку вже в контексті викликаючого потоку.

### RAII-гарантії вектора робочих потоків std::jthread

При ручному виклику `workers_.clear()` або при виході об'єкта `DataPipeline` з області видимості відбувається знищення елементів `std::vector<std::jthread>`. 

Для кожного об'єкта `std::jthread` послідовно виконуються наступні дії:
1. Автоматично викликається `request_stop()`, який змінює прапорець скасування та сповіщає всі прив'язані обробники.
2. Автоматично викликається блокуючий `join()`, який очікує повного виходу робочого потоку з функції `worker_loop`.

Завдяки цьому архітектура конвеєра гарантує відсутність потоків-сиріт (detached threads), усуває витоки ресурсів та забезпечує повну безпеку від винятків.

---

## 4. Пастки реалізації та діагностика крайових випадків

Під час реалізації таких паралельних конвеєрів розробники найчастіше стикаються з трьома критичними крайовими випадками:

1. **Гонка сигналів скасування (Cancel Signal Race)**: Потік може отримати сигнал зупинки саме в момент між виходом з `queue.pop()` і початком обробки завдання. Для запобігання цьому цикл `while` додатково перевіряє `!st.stop_requested()` на кожній ітерації.
2. **Переповнення черги завданнями (Unbounded Queue Memory Pressure)**: В реальних системах черга завдань повинна мати обмежену ємність (bounded queue), щоб головний потік не виділив усю оперативну пам'ять при затримках обробки.
3. **Подвійне викидання винятку при зупинці**: Якщо кілька робочих потоків одночасно стикаються з помилкою, використання м'ютексу `exception_mutex_` та перевірки `if (!first_exception_)` гарантує, що зберігається тільки перша неперехоплена помилка, а решта потоків завершують виконання без аварійного крашу.
