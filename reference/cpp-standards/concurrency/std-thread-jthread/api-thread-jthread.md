# 📋 Довідник інтерфейсу std::thread, std::jthread та інструментів скасування

Повна технічна специфікація типів `std::thread`, `std::jthread`, `std::stop_token`, `std::stop_source` та `std::stop_callback` у стандартах C++11, C++20 та C++23. Цей довідник надає вичерпний опис сигнатур методів, правил конструювання, інваріантів станів, гарантій безпеки винятків та низькорівневої взаємодії з системними викликами операційної системи.

---

## 1. Клас std::thread (Заголовок `<thread>`)

Клас `std::thread` являє собою абстракцію над єдиним системним потоком виконання ОС. Він володіє системним дескриптором і керує життєвим циклом потоку. Об'єкт не підтримує копіювання, але гарантує повну підтримку семантики переміщення (`std::move`).

### 1.1. Конструктори, оператори присвоєння та деструктор

```cpp
// 1. Default-конструктор (створює неактивний потік)
constexpr thread() noexcept;

// 2. Шаблонний конструктор запуску потоку
template <class Function, class... Args>
explicit thread(Function&& f, Args&&... args);

// 3. Конструктор переміщення
thread(thread&& other) noexcept;

// 4. Заборона копіювання
thread(const thread&) = delete;

// 5. Оператор переміщувального присвоєння
thread& operator=(thread&& other) noexcept;

// 6. Заборона присвоєння копіюванням
thread& operator=(const thread&) = delete;

// 7. Деструктор
~thread();
```

#### Детальні правила роботи конструкторів та деструктора:

- **`constexpr thread() noexcept`**: Створює об'єкт `std::thread`, який не представлений жодним реальним потоком виконання ОС. Для нового об'єкта гарантується `joinable() == false`, а виклик `get_id()` повертає порожній ідентифікатор `std::thread::id()`. Конструктор не виділяє пам'ять у купі та виконується за сталий час `O(1)`.
- **`explicit thread(Function&& f, Args&&... args)`**: Створює та негайно запускає новий потік виконання на рівні ОС.
  - *Механіка аргументів*: Передана функція `f` та всі аргументи `args...` копіюються або переміщуються у внутрішній буфер пам'яті (decay-copy), який виділяється у купі для передачі в точку входу системного потоку. Аргументи передаються за значенням, якщо вони не обгорнуті у `std::ref()` або `std::cref()`.
  - *Системні виклики*: У середовищі POSIX викликається `pthread_create()`, у середовищі Windows — `CreateThread()` або `_beginthreadex()`.
  - *Винятки*: Якщо виділення пам'яті під внутрішній буфер зазнає невдачі (`std::bad_alloc`) або операційна система не може створити потік через перевищення лімітів (наприклад, `EAGAIN` у POSIX), конструктор кидає виняток `std::system_error`.
- **`thread(thread&& other) noexcept`**: Передає володіння системним потоком від `other` до новоствореного об'єкта. Після виконання виклику об'єкт `other` переходить у порожній стан (`joinable() == false`), а новий об'єкт отримує унікальний ідентифікатор `get_id()` та системний дескриптор.
- **`thread& operator=(thread&& other) noexcept`**: Якщо перед викликом оператора присвоєння поточний об'єкт `*this` був у стані `joinable() == true`, C++ runtime негайно викликає `std::terminate()`. В іншому разі володіння переходить від `other` до `*this`, а `other` стає порожнім.
- **`~thread()`**: Перевіряє інваріант `joinable()`. Якщо `joinable() == true`, деструктор вважає це порушенням контракту управління ресурсами та викликає `std::terminate()`. Для уникнення аварійного завершення програми розробник зобов'язаний явно викликати `.join()` або `.detach()` до моменту знищення об'єкта `std::thread`.

---

### 1.2. Методи управління станом та зв'язком з ОС

```cpp
// Перевірка активності потоку
bool joinable() const noexcept;

// Блокуюче очікування завершення потоку
void join();

// Асинхронне від'єднання потоку від C++ об'єкта
void detach();

// Отримання унікального ідентифікатора потоку
std::thread::id get_id() const noexcept;

// Отримання платформно-залежного системного дескриптора
native_handle_type native_handle();

// Оцінка кількості логічних ядер апаратного забезпечення
static unsigned int hardware_concurrency() noexcept;
```

#### Детальні специфікації та контракти методів:

- **`bool joinable() const noexcept`**: Повертає `true`, якщо об'єкт зв'язаний з дійсним потоком виконання ОС (який може перебувати на стадії запуску, виконання або вже завершити свою функцію, але ще не був приєднаний). Повертає `false` у чотирьох випадках:
  1. Після default-конструювання `std::thread t;`.
  2. Після переміщення з об'єкта `std::thread t2 = std::move(t1);`.
  3. Після успішного завершення виклику `t.join()`.
  4. Після успішного завершення виклику `t.detach()`.
- **`void join()`**: Блокує викликаючий потік до тих пір, поки потік, представлений об'єктом `*this`, повністю не завершить виконання своєї функції та не вийде з точки входу.
  - *Низькорівнева робота*: У POSIX викликає `pthread_join()`, у Windows — `WaitForSingleObject()` з наступним викликом `CloseHandle()`. Приєднуваний потік синхронізується з викликаючим потоком за принципом *happens-before*: усі записи в пам'ять, здійснені приєднуваним потоком, стають повністю видимими викликаючому потоку після повернення з `join()`.
  - *Передумова*: `joinable() == true`.
  - *Постумова*: `joinable() == false`, `get_id() == std::thread::id()`.
  - *Винятки*: Кидає `std::system_error` з кодом `std::errc::resource_deadlock_would_occur`, якщо потік намагається приєднати сам себе (`std::this_thread::get_id() == t.get_id()`), або `std::errc::invalid_argument`, якщо `joinable() == false`.
- **`void detach()`**: Відокремлює системний потік від C++ об'єкта `std::thread`. Системний потік продовжує виконання у фоновому режимі (daemon/background thread). Після завершення функції потоку операційна система самостійно звільняє стек та ресурси.
  - *Передумова*: `joinable() == true`.
  - *Постумова*: `joinable() == false`, `get_id() == std::thread::id()`.
  - *Небезпека*: Якщо від'єднаний потік звертається до об'єктів з автоматичною тривалістю життя (на стеку головного потоку) або локальних статичних об'єктів, знищених під час виходу з `main()`, виникає невизначена поведінка (Undefined Behavior).
- **`std::thread::id get_id() const noexcept`**: Повертає об'єкт `std::thread::id`. Для не-joinable потоків повертає значення за замовчуванням, яке порівнюється як рівне для всіх порожніх потоків.
- **`native_handle_type native_handle()`**: Повертає платформно-залежний тип (наприклад, `pthread_t` під Linux/macOS або `HANDLE` під Windows). Дозволяє викликати низькорівневі системні API (наприклад, встановлення пріоритетів реального часу `pthread_setschedparam` або affinity-масок CPU `pthread_setaffinity_np`).
- **`static unsigned int hardware_concurrency() noexcept`**: Повертає оціночну кількість логічних процесорних ядер (hardware thread contexts). Якщо система не може визначити значення або воно недоступне, повертає `0`.

---

## 2. Клас std::jthread (C++20, Заголовок `<thread>`)

Клас `std::jthread` (Joining Thread) є розширенням `std::thread` у стандарту C++20. Він впроваджує повну RAII-семантику володіння потоком та вбудовану підтримку сигналів скасування `std::stop_token`.

### 2.1. Конструктори та RAII-деструктор

```cpp
// 1. Default-конструктор
jthread() noexcept;

// 2. Шаблонний конструктор із підтримкою stop_token
template <class Function, class... Args>
explicit jthread(Function&& f, Args&&... args);

// 3. Конструктор переміщення
jthread(jthread&& other) noexcept;

// 4. Оператор переміщувального присвоєння
jthread& operator=(jthread&& other) noexcept;

// 5. RAII-деструктор з авто-приєднанням
~jthread();
```

#### Особливості роботи C++20 конструкторів та деструктора:

- **`explicit jthread(Function&& f, Args&&... args)`**: Конструює об'єкт та ініціалізує новий внутрішній стан скасування `std::stop_source`.
  - *Ін'єкція stop_token*: Якщо першим параметром виконуваної функції `f` є тип `std::stop_token` (або `const std::stop_token&`), компілятор неявно передає токен скасування `get_stop_token()` як перший аргумент. Решта аргументів `args...` сопоставляються з наступними параметрами `f`.
- **`~jthread()`**: Гарантує безпечне приєднання ресурсу без небезпеки виклику `std::terminate()`. Послідовність дій деструктора строго детермінована:
  ```cpp
  if (joinable()) {
      request_stop(); // 1. Надіслати сигнал скасування
      join();         // 2. Блокуючи зачекати завершення потоку
  }
  ```
  Завдяки цьому при виникненні винятку у викликаючому потоці (stack unwinding) деструктор `std::jthread` сигналізує робочому потоку про зупинку та очікує його коректного завершення.

---

### 2.2. API управління скасуванням у std::jthread

`std::jthread` надає прямий доступ до внутрішнього механізму скасування:

```cpp
// Надіслати сигнал скасування
bool request_stop() noexcept;

// Отримати об'єкт джерела скасування
std::stop_source get_stop_source() noexcept;

// Отримати токен скасування
std::stop_token get_stop_token() const noexcept;
```

- **`bool request_stop() noexcept`**: Передає виклик внутрішньому `std::stop_source`. Атомарно встановлює прапорець `stop_requested` у `true` та викликає всі підписані обробники `std::stop_callback`. Повертає `true`, якщо цей виклик вперше встановив прапорець зупинки.
- **`std::stop_source get_stop_source() noexcept`**: Повертає об'єкт `std::stop_source`, який розділяє спільний стан скасування із цим `jthread`.
- **`std::stop_token get_stop_token() const noexcept`**: Повертає токен `std::stop_token`, прив'язаний до стану скасування цього потоку.

---

## 3. Інструменти кооперативного скасування (Заголовок `<stop_token>`)

Кооперативне скасування у C++20 складається з трьох типів, що взаємодіють через спільний атомарний лічильник посилань `stop_state`, який розміщується в динамічній пам'яті.

### 3.1. Клас std::stop_source

`std::stop_source` відповідає за створення та відправку сигналу зупинки.

```cpp
// Створити нове джерело із власним stop_state
stop_source();

// Створити неактивне джерело без stop_state
explicit stop_source(std::nostopstate_t) noexcept;

// Конструктор та оператор переміщення
stop_source(stop_source&&) noexcept;
stop_source& operator=(stop_source&&) noexcept;

// Конструктор та оператор копіювання (збільшує ref-count)
stop_source(const stop_source&) noexcept;
stop_source& operator=(const stop_source&) noexcept;

// Запитати зупинку
bool request_stop() noexcept;

// Перевірити, чи надіслано сигнал зупинки
bool stop_requested() const noexcept;

// Перевірити, чи можлива зупинка
bool stop_possible() const noexcept;

// Отримати токен спостереження
std::stop_token get_token() const noexcept;
```

#### Детальні інваріанти std::stop_source:
- **`stop_requested()`**: Атомарно зчитує прапорець зупинки із `stop_state`. Метод повністю lock-free.
- **`stop_possible()`**: Повертає `true`, якщо об'єкт зв'язаний із дійсним `stop_state` та ще не було скасовано можливість видачі сигналу. Повертає `false` для об'єктів, створених через `std::nostopstate`.
- **`request_stop()`**: Якщо прапорець `stop_requested` вже був `true`, метод негайно повертає `false`. В іншому разі атомарно встановлює прапорець у `true` та викликає всі зареєстровані `stop_callback` послідовно в поточному потоці.

---

### 3.2. Клас std::stop_token

`std::stop_token` надає пасивний інтерфейс перевірки прапорця зупинки. Об'єкт легко копіюється (`O(1)` атомарна зміна лічильника посилань).

```cpp
// Порожній токен
stop_token() noexcept;

// Перевірка наявності сигналу скасування
bool stop_requested() const noexcept;

// Перевірка можливості отримання сигналу у майбутньому
bool stop_possible() const noexcept;
```

- **`bool stop_requested() const noexcept`**: Повертає `true`, якщо для пов'язаного `stop_state` було викликано `request_stop()`. Операція є lock-free та гарантує послідовну узгодженість пам'яті (`memory_order_seq_cst` або `memory_order_acquire`).
- **`bool stop_possible() const noexcept`**: Повертає `true`, якщо токен пов'язаний з активним `stop_state`, і при цьому існує хоча б один живий об'єкт `std::stop_source` або сигнал зупинки вже було встановлено.

---

### 3.3. Шаблонний клас std::stop_callback

`std::stop_callback` впроваджує RAII-підписку на подію скасування. Переданий callable-об'єкт виконується у точці виклику `request_stop()`.

```cpp
template <class Callback>
class stop_callback {
public:
    using callback_type = Callback;

    // Реєстрація зворотного виклику
    template <class C>
    explicit stop_callback(const std::stop_token& st, C&& cb)
        noexcept(std::is_nothrow_constructible_v<Callback, C>);

    template <class C>
    explicit stop_callback(std::stop_token&& st, C&& cb)
        noexcept(std::is_nothrow_constructible_v<Callback, C>);

    // Деструктор (скасовує реєстрацію callback)
    ~stop_callback();

    stop_callback(const stop_callback&) = delete;
    stop_callback& operator=(const stop_callback&) = delete;
};
```

#### Поведінка конструктора та деструктора stop_callback:
1. Якщо під час виконання конструктора `stop_callback` прапорець `stop_requested()` вже дорівнює `true`, конструктор **негайно виконує callback у поточному потоці** прямо перед поверненням управління.
2. Якщо `request_stop()` викликається пізніше з іншого потоку, всі зареєстровані `stop_callback` виконуються послідовно у потоці, який викликав `request_stop()`.
3. Деструктор `~stop_callback()` атомарно видаляє функцію зі списку підписок. Якщо у цей момент інший потік виконує цей callback, деструктор блокується до завершення виконання callback.

---

## 4. Простір імен std::this_thread (Заголовок `<thread>`)

Утиліти для поточного потоку виконання:

```cpp
namespace std::this_thread {
    // Отримати ідентифікатор поточного потоку
    std::thread::id get_id() noexcept;

    // Добровільно віддати решту кванту часу CPU
    void yield() noexcept;

    // Заблокувати поточний потік на задану тривалість
    template <class Rep, class Period>
    void sleep_for(const std::chrono::duration<Rep, Period>& sleep_duration);

    // Заблокувати поточний потік до конкретного моменту часу
    template <class Clock, class Duration>
    void sleep_until(const std::chrono::time_point<Clock, Duration>& sleep_time);
}
```

#### Деталі роботи утиліт std::this_thread:
- **`get_id()`**: Надає швидкий доступ до ідентифікатора поточного потоку без виклику важких системних функцій.
- **`yield()`**: Підказує планивальнику ядра віддати решту кванту часу іншим потокам у черзі готовності. Зменшує тепловиділення та марне завантаження ядер CPU у спинлоках.
- **`sleep_for()` та `sleep_until()`**: Використовують системні точні таймери (`clock_nanosleep` під Linux або `NtDelayExecution` під Windows). Потік переводиться у стан сну і не споживає циклів CPU.

---

## 5. Порівняльна матриця специфікацій std::thread vs std::jthread

| Параметр / Характеристика | std::thread (C++11) | std::jthread (C++20) |
| :--- | :--- | :--- |
| **Деструктор при joinable() == true** | Викликає `std::terminate()` (краш) | `request_stop()` + `join()` (безпечно) |
| **Автоматичне скасування** | Відсутнє | Вбудоване через `std::stop_token` |
| **Неявна передача stop_token** | Ні | Так (якщо 1-й параметр функції `stop_token`) |
| **Розмір об'єкта (x86-64)** | 8 байтів (`sizeof(pthread_t)`) | 16 байтів (`thread` + `stop_source`) |
| **Винятки у деструкторі** | Кидає `std::terminate()` | Гарантовано `noexcept` |
| **Копіювання / Переміщення** | Тільки переміщення (`std::move`) | Тільки переміщення (`std::move`) |
| **Низькорівневий дескриптор** | `t.native_handle()` | `jt.native_handle()` |
