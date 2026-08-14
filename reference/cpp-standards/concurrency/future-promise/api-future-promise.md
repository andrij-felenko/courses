# 📋 Повна специфікація std::future, std::shared_future, std::promise та std::packaged_task

Ця довідкова вставка містить вичерпний інтерфейс, сигнали помилок, гарантії потокобезпеки та деталізовану специфікацію методів шаблонів `std::promise`, `std::future`, `std::shared_future` та `std::packaged_task` у заголовочному файлі `<future>` стандартної бібліотеки C++.

## 1. Архітектурний огляд заголовочного файла та типів даних

Усі типи для підтримки одноразового асинхронного обміну даними між потоками виконання зібрані у стандартному заголовочному файлі `<future>` в просторі імен `std`:

```cpp
#include <future>
```

Архітектура асинхронного зв'язку заснована на чотирьох базових шаблонах класів та трьох допоміжних перелічуваних типах. Кожен із класів виконує строго визначену функцію в життєвому циклі зв'язку між потоками:

| Тип | Роль у системі | Семантика копіювання | Семантика переміщення |
| :--- | :--- | :--- | :--- |
| `std::promise<R>` | Виробник (Producer): приймає та зберігає результат або виняток | Заборонено (`= delete`) | Дозволено (`noexcept`) |
| `std::future<R>` | Споживач (Consumer): очікує та зчитує результат у режимі 1:1 | Заборонено (`= delete`) | Дозволено (`noexcept`) |
| `std::shared_future<R>` | Споживач (Consumer): очікує та зчитує результат у режимі 1:N | Дозволено (`copy-constructible`) | Дозволено (`noexcept`) |
| `std::packaged_task<R(Args...)>` | Обгортка над функцією, що зв'язує результат виконання із `std::promise` | Заборонено (`= delete`) | Дозволено (`noexcept`) |

Фундаментальним принципом дизайну цих типів є несиметричність доступу. Потік-виробник тримає об'єкт `std::promise` і має дозвіл лише на одноразовий запис значення чи винятку. Потік-споживач тримає об'єкт `std::future` і має дозвіл лише на зчитування або блокуюче очікування. Сам обчисливальний результат зберігається в ізольованому динамічному об'єкті Shared State (спільному стані), захованому всередині рантайму стандартної бібліотеки.

---

## 2. Шаблон класу std::promise<R>

Шаблон класу `std::promise<R>` забезпечує механізм для запису значення або винятку, який згодом буде прочитаний через відповідний об'єкт `std::future<R>`. Об'єкт `promise` конструюється без готового значення й створює всередині себе новий Shared State.

### Спеціалізації шаблону:
1. `std::promise<R>` — загальна форма шаблону для збереження об'єктів довільного типу `R`.
2. `std::promise<R&>` — спеціалізація для передачі посилання на існуючий об'єкт у пам'яті без створення копій чи переміщення.
3. `std::promise<void>` — спеціалізація для сигналізації про завершення операції чи події без передачі будь-якого значення.

### Публічний інтерфейс класу:

```cpp
namespace std {

template <typename R>
class promise {
public:
    // 1. Конструктори та деструктор
    promise();
    template <typename Alloc>
    promise(allocator_arg_t alloc, const Alloc& a);
    
    promise(const promise&) = delete;
    promise(promise&& rhs) noexcept;
    
    ~promise();

    // 2. Оператори присвоєння
    promise& operator=(const promise&) = delete;
    promise& operator=(promise&& rhs) noexcept;

    void swap(promise& other) noexcept;

    // 3. Отримання зв'язаного future
    future<R> get_future();

    // 4. Запис результату (для загальної форми R)
    void set_value(const R& value);
    void set_value(R&& value);
    void set_exception(exception_ptr p);

    // 5. Запис результату зі зсувом сповіщення до завершення потоку
    void set_value_at_thread_exit(const R& value);
    void set_value_at_thread_exit(R&& value);
    void set_exception_at_thread_exit(exception_ptr p);
};

// Спеціалізація для посилань
template <typename R>
class promise<R&> {
public:
    promise();
    ~promise();
    future<R&> get_future();
    void set_value(R& value);
    void set_exception(exception_ptr p);
    void set_value_at_thread_exit(R& value);
    void set_exception_at_thread_exit(exception_ptr p);
};

// Спеціалізація для void
template <>
class promise<void> {
public:
    promise();
    ~promise();
    future<void> get_future();
    void set_value();
    void set_exception(exception_ptr p);
    void set_value_at_thread_exit();
    void set_exception_at_thread_exit(exception_ptr p);
};

} // namespace std
```

### Вичерпний опис методів та їхніх семантичних гарантій:

#### `promise()` та `promise(allocator_arg_t, const Alloc& a)`
- **Призначення:** Конструює об'єкт `std::promise` та ініціалізує новий порожній Shared State у динамічній пам'яті. У разі використання версії з алокатором, пам'ять під Shared State виділяється за допомогою переданого об'єкта алокатора `a`. Це дозволяє уникнути стандартного виклику `global operator new` у системах із жорсткими вимогами до аллокацій або в реальному часі.
- **Гарантія винятків:** Може кидати виняток `std::bad_alloc`, якщо не вдалося виділити пам'ять під Shared State.

#### `future<R> get_future()`
- **Призначення:** Створює та повертає об'єкт `std::future<R>`, який зв'язується з тим самим Shared State, що й даний `promise`.
- **Предумови:** Об'єкт `promise` повинен мати дійсний Shared State (тобто не бути переміщеним).
- **Обмеження:** Метод можна викликати строго **один раз** для кожного об'єкта `promise`. Повторний виклик для того самого каналу є заборонений.
- **Винятки:** Кидає виняток `std::future_error` із кодами помилок:
  - `future_already_retrieved` — якщо метод `get_future()` уже викликався раніше для цього конкретного Shared State.
  - `no_state` — якщо об'єкт `promise` не утримує дійсного Shared State.

#### `void set_value(const R& value)` / `void set_value(R&& value)`
- **Призначення:** Атомарно копіює або переміщує обчислений результат `value` у внутрішній буфер Shared State і переводить його у стан `Ready` (готовий). Після зміни стану відбувається атомарна сигналізація через умовну змінну (`notify_all()`), що негайно розблоковує всі потоки, які перебувають у стані очікування в методах `wait()` або `get()`.
- **Гарантії синхронізації:** Запис значення здійснюється з семантикою `std::memory_order_release`. Всі зміни пам'яті, зроблені потоком-виробником до виклику `set_value()`, стають гарантовано видимими для потоку-споживача після повернення з `future::get()`.
- **Винятки:** Кидає `std::future_error` з кодами:
  - `promise_already_satisfied` — якщо результат (значення або виняток) уже був раніше записаний у Shared State.
  - `no_state` — якщо об'єкт `promise` втратив дійсний Shared State.

#### `void set_exception(std::exception_ptr p)`
- **Призначення:** Атомарно зберігає вказувач на виняток `p` у Shared State і переводить стан у `Ready`. Метод дозволяє прокинути будь-яку виняткову ситуацію з фонового потоку в потік-споживач.
- **Предумови:** Аргумент `p` не повинен дорівнювати `nullptr`. Якщо передати `nullptr`, поведінка стандартної бібліотеки вважається некоректною або призводить до кидання `std::invalid_argument`.
- **Винятки:** Кидає `std::future_error` з кодами `promise_already_satisfied` або `no_state`.

#### `void set_value_at_thread_exit(...)` / `void set_exception_at_thread_exit(...)`
- **Призначення:** Зберігає значення або виняток у Shared State, але **затримує** перехід стану у `Ready` та сповіщення чекаючих потоків до моменту повного завершення потоку, що викликав цей метод.
- **Механізм роботи:** Перехід у стан `Ready` та виклик `notify_all()` відбуваються в самому кінці життєвого циклу потоку — після того, як виконано руйнування всіх об'єктів із модифікатором тривалості життя `thread_local`.
- **Практичне значення:** Усуває критичні стани гонки (data race), коли потік-споживач після отримання результату через `set_value()` міг би негайно знищити спільні ресурси або завершити програму до того, як фоновий потік встигне виконати очищення своїх `thread_local` деструкторів.

#### Деструктор `~promise()`
- **Поведінка при руйнуванні:** Якщо об'єкт `promise` руйнується до того, як розробник явно викликав `set_value()` або `set_exception()`, але при цьому зв'язаний `future` все ще існує й очікує на результат, деструктор `promise` здійснює аварійні дії:
  1. Атомарно зберігає у Shared State виняток `std::future_error` із кодом `broken_promise`.
  2. Переводить Shared State у стан `Ready`.
  3. Сигналізує умовній змінній про можливість розблокування споживачів.

---

## 3. Шаблон класу std::future<R>

Шаблон класу `std::future<R>` реалізує точку читання асинхронного каналу. Об'єкт `std::future` володіє ексклюзивним правом на зчитування результату із Shared State у режимі «один до одного».

### Публічний інтерфейс класу:

```cpp
namespace std {

template <typename R>
class future {
public:
    // 1. Конструктори та деструктор
    constexpr future() noexcept;
    future(future&& rhs) noexcept;
    future(const future&) = delete;
    ~future();

    // 2. Оператори присвоєння
    future& operator=(const future&) = delete;
    future& operator=(future&& rhs) noexcept;

    // 3. Конвертація у shared_future
    shared_future<R> share() noexcept;

    // 4. Отримання результату
    R get(); // Для первинного шаблону R
             // Для R& повертає R&
             // Для void повертає void

    // 5. Перевірка валідності
    bool valid() const noexcept;

    // 6. Блокуюче очікування
    void wait() const;
    
    template <typename Rep, typename Period>
    future_status wait_for(const chrono::duration<Rep, Period>& timeout_duration) const;
    
    template <typename Clock, typename Duration>
    future_status wait_until(const chrono::time_point<Clock, Duration>& timeout_time) const;
};

} // namespace std
```

### Вичерпний опис методів та їхніх семантичних гарантій:

#### `bool valid() const noexcept`
- **Призначення:** Перевіряє, чи утримує поточний об'єкт `future` посилання на дійсний Shared State.
- **Повертає:** `true`, якщо об'єкт зв'язаний зі станом; `false`, якщо об'єкт сконструйований за замовчуванням, був переміщений в інший об'єкт або якщо метод `get()` уже вилучив результат.

#### `R get()`
- **Призначення:** Блокує поточний потік виконання доти, доки Shared State не стане готовим (`Ready`), після чого повертає збережений результат або повторно кидає збережений виняток.
- **Поведінка залежно від типу `R`:**
  - Для `std::future<R>` — повертає обчислений об'єкт `R` шляхом переміщення або копіювання з внутрішнього буфера.
  - Для `std::future<R&>` — повертає збережене посилання `R&`.
  - Для `std::future<void>` — не повертає значення, виконуючи суто роль бар'єра синхронізації.
- **Постумова:** Після завершення виклику `get()` Shared State вилучається з об'єкта `future`, а сам `future` переходить у невалідний стан (`valid() == false`).
- **Винятки:**
  - Якщо в Shared State був збережений виняток через `set_exception()`, метод `get()` повторно кидає цей виняток у потоці споживача за допомогою виклику `std::rethrow_exception()`.
  - Якщо виклику `get()` передувала ситуація `valid() == false`, метод кидає `std::future_error` з кодом `no_state` або призводить до некоректної поведінки (Undefined Behavior).

#### `void wait() const`
- **Призначення:** Призупиняє виконання поточного потоку до моменту переходу Shared State у стан `Ready`.
- **Семантична відмінність від `get()`:** Метод `wait()` не вилучає результат із Shared State і не змінює прапор `valid()`. Об'єкт `future` можна продовжувати опитувати або згодом викликати `get()`.

#### `template <class Rep, class Period> future_status wait_for(...) const` / `wait_until(...) const`
- **Призначення:** Виконує блокуюче очікування готовності результату з обмеженням за часом. `wait_for` приймає відносний інтервал тривалості (`std::chrono::duration`), а `wait_until` — абсолютну точку часу (`std::chrono::time_point`).
- **Повертає значення:** Значення перелічуваного типу `std::future_status`:
  - `std::future_status::ready` — результат обчислено й збережено. Подальший виклик `get()` поверне значення негайно без блокування.
  - `std::future_status::timeout` — виділений інтервал часу вичерпано, а потік-виробник ще не записав результат.
  - `std::future_status::deferred` — асинхронна задача була сформована з відкладеним запуском (`std::launch::deferred`). Обчислення не розпочнеться автоматично у фоновому потоці; для його запуску необхідно явно викликати `wait()` або `get()`.

#### `shared_future<R> share() noexcept`
- **Призначення:** Трансформує поточний об'єкт `std::future<R>` у передаваний об'єкт `std::shared_future<R>` шляхом переміщення Shared State.
- **Постумова:** Початковий об'єкт `future` стає невалідним (`valid() == false`).

---

## 4. Шаблон класу std::shared_future<R>

Класовий шаблон `std::shared_future<R>` розширює можливості `std::future`, дозволяючи кільком автономним потокам виконання одночасно чекати й прочитати один і той самий асинхронний результат у режимі «один до багатьох» (1:N).

### Публічний інтерфейс класу:

```cpp
namespace std {

template <typename R>
class shared_future {
public:
    constexpr shared_future() noexcept;
    shared_future(const shared_future& rhs) noexcept;
    shared_future(shared_future&& rhs) noexcept;
    shared_future(future<R>&& rhs) noexcept;
    ~shared_future();

    shared_future& operator=(const shared_future& rhs) noexcept;
    shared_future& operator=(shared_future&& rhs) noexcept;

    bool valid() const noexcept;

    // Зверніть увагу: get() повертає const R& для загального типу R
    const R& get() const;

    void wait() const;
    template <class Rep, class Period>
    future_status wait_for(const chrono::duration<Rep, Period>& timeout_duration) const;
    template <class Clock, class Duration>
    future_status wait_until(const chrono::time_point<Clock, Duration>& timeout_time) const;
};

// Спеціалізація для посилань
template <typename R>
class shared_future<R&> {
public:
    R& get() const;
};

// Спеціалізація для void
template <>
class shared_future<void> {
public:
    void get() const;
};

} // namespace std
```

### Ключові відмінності інтерфейсу std::shared_future:
1. **Підтримка копіювання:** На відміну від `std::future`, об'єкт `std::shared_future` має конструктор копіювання та оператор копіювального присвоєння. Кілька об'єктів `shared_future` можуть тримати посилання на один і той самий Shared State через внутрішній лічильник посилань.
2. **Багаторазове зчитування:** Виклик `get()` не руйнує Shared State і не переводить `valid()` у `false`. Метод `get()` можна викликати повторно.
3. **Тип повернення:** Для загальної форми `std::shared_future<R>::get()` повертає константне посилання `const R&`. Це гарантує, що кілька потоків можуть одночасно читати об'єкт без виникнення станів гонки за пам'ять (data race).

---

## 5. Шаблон класу std::packaged_task<R(Args...)>

`std::packaged_task` є високорівневою обгорткою, яка зв'язує довільний викликний об'єкт (функцію, лямбду, функтор) із внутрішнім `std::promise`. При виклику `packaged_task` виконує обгортаємий об'єкт, перехоплює повернене значення або виняток і автоматично зберігає його у Shared State.

### Публічний інтерфейс класу:

```cpp
namespace std {

template <typename Signature>
class packaged_task; // Невизначений первинний шаблон

template <typename R, typename... Args>
class packaged_task<R(Args...)> {
public:
    // Конструктори
    packaged_task() noexcept;
    
    template <typename F>
    explicit packaged_task(F&& f);
    
    template <typename F, typename Alloc>
    packaged_task(allocator_arg_t alloc, const Alloc& a, F&& f);

    ~packaged_task();

    // Заборона копіювання, дозвіл переміщення
    packaged_task(const packaged_task&) = delete;
    packaged_task(packaged_task&& rhs) noexcept;
    
    packaged_task& operator=(const packaged_task&) = delete;
    packaged_task& operator=(packaged_task&& rhs) noexcept;

    void swap(packaged_task& other) noexcept;

    bool valid() const noexcept;

    // Отримання зв'язаного future
    future<R> get_future();

    // Виконання задачі
    void operator()(Args... args);
    void make_ready_at_thread_exit(Args... args);

    // Скидання стану для повторного використання
    void reset();
};

} // namespace std
```

### Механіка функціонування std::packaged_task:
- **`operator()(Args... args)`:** Викликає внутрішню функцію із переданими аргументами. Якщо функція повертає значення `R`, воно зберігається у Shared State через `set_value()`. Якщо функція кидає виняток, виклик перехоплюється у блоці `catch (...)`, і виняток зберігається через `set_exception()`.
- **`reset()`:** Залишає збережену цільову функцію, але конструює новий Shared State і скидає стан внутрішнього `promise`. Це дозволяє повторно запускати обгортку в циклі або пулі потоків.

---

## 6. Ієрархія помилок: std::future_error та enum std::future_errc

Усі системні й логічні збої при роботі з асинхронними каналами виражаються через стандартний виняток `std::future_error`, який успадковується від `std::logic_error`.

### Специфікація типів помилок:

```cpp
namespace std {

enum class future_errc {
    broken_promise = 1,
    future_already_retrieved = 2,
    promise_already_satisfied = 3,
    no_state = 4
};

const error_category& future_category() noexcept;

make_error_code(future_errc e) noexcept;
make_error_condition(future_errc e) noexcept;

class future_error : public logic_error {
public:
    explicit future_error(error_code ec);
    const error_code& code() const noexcept;
    const char* what() const noexcept override;
};

} // namespace std
```

### Деталізована семантика кодів помилок:

| Код помилки `future_errc` | Точна умова виникнення у рантаймі |
| :--- | :--- |
| `broken_promise` | Об'єкт `promise` або `packaged_task` було знищено до того, як було явно записано значення або виняток, але при цьому зв'язаний `future` все ще існує. |
| `future_already_retrieved` | Метод `get_future()` викликано повторно для одного й того самого об'єкта `promise` або `packaged_task`. |
| `promise_already_satisfied` | Виклик `set_value()` або `set_exception()` зроблено для `promise`, у який вже раніше було записано результат. |
| `no_state` | Спроба виконати операцію над `future`, `promise` або `packaged_task`, який не утримує дійсного Shared State (наприклад, після переміщення). |

---

## 7. Детальні гарантії потокобезпеки та впорядкування пам'яті

Специфікація стандарту ISO C++ визначає наступні суворі гарантії щодо потокобезпеки та впорядкування операцій із пам'яттю (Memory Ordering):

1. **Ізоляція об'єктів:** Потік-виробник і потік-споживач працюють із різними об'єктами (`promise` та `future`). Захист спільного внутрішнього стану Shared State забезпечується реалізацією стандартної бібліотеки (за допомогою системного мутекса або атомарних прапорців).
2. **Гарантія відносин Happens-Before:** Запис значення через `set_value()` або винятку через `set_exception()` створює точкову синхронізацію release-acquire. Будь-які модифікації даних у пам'яті, виконані потоком-виробником до виклику `set_value()`, гарантовано стають повністю видимими для потоку-споживача в момент повернення з викликів `wait()` або `get()`.
3. **Заборона паралельних викликів get() для std::future:** Одночасний виклик методів `get()` або `wait()` над одним і тим самим об'єктом `std::future` з двох різних потоків викликає стан гонки (data race) і призводить до некоректної поведінки (Undefined Behavior).
4. **Потокобезпечність std::shared_future:** Паралельні виклики `get()` над різними копіями `std::shared_future` (або навіть над одним об'єктом, оскільки `get()` є `const`-методом) є повністю потокобезпечними й не потребують додаткових зовнішніх замків.

---

## 8. Порівняльний аналіз абстракцій асинхронного виконання

Для обґрунтованого вибору інструмента передачі результатів у розробці програмного забезпечення нижче наведено структуроване порівняння чотирьох ключових абстракцій заголовочного файла `<future>`:

### 1. std::promise та std::future
- **Використання:** Низькорівневий ручний канал зв'язку.
- **Гнучкість:** Максимальна. Дозволяє передавати результати з обробників переривань, зворотних викликів (callbacks), пулів потоків чи мережевих сокетів.
- **Управління потоком:** Потік конструюється та запускається розробником вручну (через `std::thread` або `std::jthread`).

### 2. std::packaged_task
- **Використання:** Середній рівень абстракції. Зв'язує конкретну обчислювальну функцію з `std::promise`.
- **Гнучкість:** Зручно для передачі обчислень у черги задач (task queues) або пули потоків (thread pools), де потік-виконавець просто викликає `task()`.
- **Управління потоком:** Об'єкт задачі можна передати в інший потік виконання чи виконати синхронно за потреби.

### 3. std::async
- **Використання:** Високорівнева функція-фабрика.
- **Гнучкість:** Мінімальний boilerplate-код. Негайно повертає `std::future`, ховаючи створення `promise` та керування потоком всередині рантайму.
- **Особливості:** При виборі політики `std::launch::async` створює новий потік або бере потік з внутрішнього пулу; при `std::launch::deferred` відкладає виконання до першого виклику `get()`.

### 4. std::shared_future
- **Використання:** Широкомовна передача результату багатьом споживачам.
- **Гнучкість:** Дозволяє необмеженій кількості потоків чекати на завершення ініціалізації спільних даних (наприклад, конфігурації або кешу) без взаємного блокування при зчитуванні.

---

## 9. Управління пам'яттю та операції обміну (swap)

Спільний стан (Shared State) між виробником та споживачем виділяється у купі за допомогою системного або користувацького алокатора. Управління часом життя здійснюється атомарним лічильником посилань:

- Конструктор `std::promise` встановлює початковий лічильник посилань у 1.
- Виклик `get_future()` збільшує лічильник посилань у Shared State до 2 (один утримується `promise`, другий — `future`).
- Створення копії `std::shared_future` збільшує лічильник посилань на 1 для кожної створеної копії.
- При руйнуванні `promise` або `future` лічильник атомарно зменшується. Коли лічильник досягає 0, пам'ять під Shared State і збережене у ньому значення `R` остаточно звільняється.

Обмін внутрішніми станами об'єктів виконується через неблокуючі методи `swap`:
- `promise::swap(promise& other) noexcept` — атомарно обмінює вказувачі на Shared State між двома об'єктами обіцянок.
- `packaged_task::swap(packaged_task& other) noexcept` — обмінює збережені викликні об'єкти та зв'язані Shared State.
- Всі операції `swap` гарантовано виконуються за сталий час `O(1)` і не кидають винятків (`noexcept`).
