# 📋 Довідник API: std::stop_token, std::stop_source та std::stop_callback

Заголовок `<stop_token>` стандарту C++20 визначає уніфіковану інфраструктуру для безпечного, потокобезпечного та кооперативного скасування асинхронних операцій, обчислень і потоків виконання. Цей довідник містить вичерпний опис сигнатур, конструкторів, методів, інваріантів пам'яті, гарантій винятків (`noexcept`), правил виведення типів та умов синхронізації для класів `std::stop_token`, `std::stop_source`, `std::stop_callback`, допоміжного тегу `std::nostopstate`, а також спеціалізованих перевантажень `std::condition_variable_any`.

---

## 1. Загальний огляд типів заголовка `<stop_token>`

Усі типи простору імен `std` для кооперативного скасування спираються на концепцію спільного стану скасування (Shared Stop State), виділеного у динамічній пам'яті:

```cpp
namespace std {
    // Неволодіючий спостерігач стану скасування
    class stop_token;

    // Володіюче джерело ініціації сигналу скасування
    class stop_source;

    // RAII-підписка на подію скасування
    template<class Callback>
    class stop_callback;

    // Теговий тип і константа для створення без спільного стану
    struct nostopstate_t { explicit nostopstate_t() = default; };
    inline constexpr nostopstate_t nostopstate{};
}
```

Спільний стан `stop_state` створюється автоматично при виклику конструктора `std::stop_source()` за замовчуванням і знищується тоді, коли лічильник спільних посилань від усіх пов'язаних `std::stop_source`, `std::stop_token` та активних `std::stop_callback` стає рівним нулю. Якщо всі об'єкти `std::stop_source` знищуються до надходження сигналу скасування, спільний стан переходить у режим, коли зупинка стає неможливою, про що спостерігачі сповіщаються через метод `stop_possible() == false`.

---

## 2. Клас std::stop_token

Клас `std::stop_token` надає доступ лише для читання до спільного стану скасування. Він дозволяє перевіряти, чи був надісланий запит на зупинку, а також чи є зупинка в принципі можливою. Об'єкт є копійованим, переміщуваним і за розміром у пам'яті дорівнює одному вказівнику.

```cpp
class stop_token {
public:
    // Конструктори та деструктор
    stop_token() noexcept;
    stop_token(const stop_token& other) noexcept;
    stop_token(stop_token&& other) noexcept;
    ~stop_token();

    // Оператори присвоєння
    stop_token& operator=(const stop_token& other) noexcept;
    stop_token& operator=(stop_token&& other) noexcept;

    // Модифікатори
    void swap(stop_token& other) noexcept;

    // Спостереження стану
    [[nodiscard]] bool stop_requested() const noexcept;
    [[nodiscard]] bool stop_possible() const noexcept;

    // Порівняння
    [[nodiscard]] friend bool operator==(const stop_token& lhs, const stop_token& rhs) noexcept;
};

// Нечленні функції обміну
void swap(stop_token& lhs, stop_token& rhs) noexcept;
```

### Детальний опис методів std::stop_token

#### Конструктори та деструктор
- `stop_token() noexcept;`
  - **Призначення**: Створює порожній об'єкт `stop_token`, який не асоційований із жодним спільним станом скасування. Використовується за замовчуванням, коли потрібно передати токен-заглушку в функцію, що підтримує скасування, але викликач не планує переривати операцію.
  - **Пост-умова**: `stop_possible() == false`, `stop_requested() == false`.
- `stop_token(const stop_token& other) noexcept;`
  - **Призначення**: Конструктор копіювання. Збільшує лічильник посилань на спільний стан скасування (якщо стан існує). Операція є надзвичайно дешевою і зводиться до одного атомарного інкременту в стилі `std::shared_ptr`.
  - **Пост-умова**: `*this == other`.
- `stop_token(stop_token&& other) noexcept;`
  - **Призначення**: Конструктор переміщення. Забирає володіння посиланням на спільний стан у `other`. Після переміщення `other` переходить у стан за замовчуванням.
  - **Пост-умова**: `other.stop_possible() == false`, `other.stop_requested() == false`.
- `~stop_token();`
  - **Призначення**: Зменшує атомарний лічильник посилань на спільний стан. Якщо це було останнє посилання (разом із джерелами та колбеками), пам'ять `stop_state` у купі повністю звільняється.

#### Методи спостереження стану
- `[[nodiscard]] bool stop_requested() const noexcept;`
  - **Призначення**: Перевіряє, чи було для асоційованого спільного стану викликано `request_stop()`.
  - **Повертає**: `true`, якщо спільний стан існує і для нього вже зафіксовано запит на зупинку; інакше `false`.
  - **Синхронізація**: Виконує атомарне читання з семантикою `std::memory_order_acquire`, що синхронізується з операцією `request_stop()` (яка виконує запис із семантикою `std::memory_order_release` або `std::memory_order_acq_rel`). Це гарантує, що всі зміни пам'яті, зроблені ініціатором до запиту зупинки, стають повністю видимими для поточного потоку. Компілятор не має права кешувати це значення в регістрах CPU або виносити перевірку за межі циклу.
- `[[nodiscard]] bool stop_possible() const noexcept;`
  - **Призначення**: Перевіряє, чи може поточний токен коли-небудь отримати сигнал скасування.
  - **Повертає**: `true`, якщо токен володіє спільним станом і або запит на зупинку вже надіслано (`stop_requested() == true`), або ще існує хоча б один живий асоційований `std::stop_source` (`stop_source::stop_possible() == true`). Якщо всі асоційовані `stop_source` були знищені до надходження сигналу зупинки, метод повертає `false`. Це дозволяє оптимізувати робочий цикл: якщо зупинка фізично неможлива, можна пропустити витратні перевірки або реєстрації колбеків.

#### Оператори порівняння та утиліти
- `friend bool operator==(const stop_token& lhs, const stop_token& rhs) noexcept;`
  - **Повертає**: `true`, якщо обидва токени посилаються на один і той самий спільний стан скасування або обидва не мають асоційованого стану; інакше `false`.
- `void swap(stop_token& other) noexcept;`
  - **Призначення**: Атомарно обмінює внутрішні вказівники на спільний стан між двома токенами без виділення динамічної пам'яті.

---

## 3. Клас std::stop_source

Клас `std::stop_source` є ініціатором сигналу скасування. Об'єкт контролює спільний стан і надає ексклюзивне право на виклик `request_stop()`.

```cpp
class stop_source {
public:
    // Конструктори та деструктор
    stop_source();
    explicit stop_source(std::nostopstate_t) noexcept;
    stop_source(const stop_source& other) noexcept;
    stop_source(stop_source&& other) noexcept;
    ~stop_source();

    // Оператори присвоєння
    stop_source& operator=(const stop_source& other) noexcept;
    stop_source& operator=(stop_source&& other) noexcept;

    // Модифікатори
    void swap(stop_source& other) noexcept;
    bool request_stop() noexcept;

    // Спостереження стану
    [[nodiscard]] stop_token get_token() const noexcept;
    [[nodiscard]] bool stop_requested() const noexcept;
    [[nodiscard]] bool stop_possible() const noexcept;

    // Порівняння
    [[nodiscard]] friend bool operator==(const stop_source& lhs, const stop_source& rhs) noexcept;
};

// Нечленні функції обміну
void swap(stop_source& lhs, stop_source& rhs) noexcept;
```

### Детальний опис методів std::stop_source

#### Конструктори та деструктор
- `stop_source();`
  - **Призначення**: Виділяє новий спільний стан скасування у динамічній пам'яті (купа) та ініціалізує внутрішні лічильники посилань і прапорці.
  - **Винятки**: Викидає `std::bad_alloc`, якщо не вдалося виділити пам'ять під блок керування `stop_state`.
  - **Пост-умова**: `stop_possible() == true`, `stop_requested() == false`.
- `explicit stop_source(std::nostopstate_t) noexcept;`
  - **Призначення**: Створює порожній об'єкт джерела без виділення спільного стану в купі. Використовується як оптимізація для уникнення накладних витрат там, де скасування не потрібне.
  - **Пост-умова**: `stop_possible() == false`, `stop_requested() == false`.
- `stop_source(const stop_source& other) noexcept;`
  - **Призначення**: Конструктор копіювання. Збільшує лічильник джерел у спільному стані. Дозволяє декільком незалежним компонентам програми володіти правом на ініціацію зупинки однієї операції.
  - **Пост-умова**: `*this == other`.
- `stop_source(stop_source&& other) noexcept;`
  - **Призначення**: Конструктор переміщення. Передає право володіння спільним станом.
  - **Пост-умова**: `other.stop_possible() == false`.
- `~stop_source();`
  - **Призначення**: Зменшує лічильник активних джерел. Якщо це було останнє джерело і `stop_requested() == false`, усі пов'язані токени перейдуть у стан `stop_possible() == false`.

#### Методи керування та спостереження
- `bool request_stop() noexcept;`
  - **Призначення**: Атомарно надсилає запит на зупинку всім підписникам та асоційованим токенам.
  - **Повертає**: `true`, якщо цей конкретний виклик перевів стан зі значення «не зупинено» у «зупинено»; `false`, якщо запит уже надсилався раніше іншим джерелом або стан порожній (`stop_possible() == false`).
  - **Синхронізація та ефекти**:
    1. Виконує атомарну операцію `compare_exchange_strong` над внутрішнім прапорцем стану з пам'яттєвим порядком `std::memory_order_acq_rel`.
    2. Поточний потік, який успішно встановив прапорець, негайно та синхронно виконує всі зареєстровані об'єкти `std::stop_callback` прямо в поточному потоці.
    3. Якщо виклик методу `request_stop()` відбувається конкурентно з реєстрацією нового `stop_callback`, гарантується, що функція зворотного виклику виконається рівно один раз.
    4. **Критична вимога до винятків**: Якщо будь-яка функція зворотного виклику викидає виняток, C++ runtime негайно викликає `std::terminate()`. Метод `request_stop()` оголошено як `noexcept`.
- `[[nodiscard]] stop_token get_token() const noexcept;`
  - **Призначення**: Повертає асоційований об'єкт `std::stop_token`, прив'язаний до цього ж спільного стану.
- `[[nodiscard]] bool stop_requested() const noexcept;`
  - **Повертає**: `true`, якщо спільний стан активний і було успішно викликано `request_stop()`.
- `[[nodiscard]] bool stop_possible() const noexcept;`
  - **Повертає**: `true`, якщо об'єкт асоційований із дійсним спільним станом скасування.

---

## 4. Шаблонний клас std::stop_callback

Клас `std::stop_callback<Callback>` реалізує патерн підписки RAII (Resource Acquisition Is Initialization). Він реєструє функціональний об'єкт у списку зворотних викликів спільного стану при конструюванні та автоматично знімає реєстрацію при знищенні.

```cpp
template<class Callback>
class stop_callback {
public:
    using callback_type = Callback;

    // Конструктори з реєстрацією
    template<class C>
    explicit stop_callback(const stop_token& st, C&& cb)
        noexcept(std::is_nothrow_constructible_v<Callback, C>);

    template<class C>
    explicit stop_callback(stop_token&& st, C&& cb)
        noexcept(std::is_nothrow_constructible_v<Callback, C>);

    // Деструктор зі зняттям підписки та блокуванням
    ~stop_callback();

    // Заборона копіювання та переміщення
    stop_callback(const stop_callback&) = delete;
    stop_callback(stop_callback&&) = delete;
    stop_callback& operator=(const stop_callback&) = delete;
    stop_callback& operator=(stop_callback&&) = delete;
};

// Настанова виведення типів аргументів шаблону (CTAD)
template<class Callback>
stop_callback(stop_token, Callback) -> stop_callback<Callback>;
```

### Вимоги до типів та алгоритми життєвого циклу

- **Концептуальні обмеження**: Тип `Callback` повинен задовольняти концепт `std::destructible` та бути викликаним без аргументів: `std::is_invocable_v<Callback> == true`.
- **Поведінка конструктора**:
  - Конструює внутрішній функціональний об'єкт типу `Callback` із переданого аргументу `cb`.
  - Якщо переданий токен має стан `st.stop_requested() == true`, конструктор **негайно виконує** збережений зворотний виклик у поточному потоці прямо під час конструювання об'єкта. Це виключає ситуацію, коли сигнал було надіслано за мить до створення колбека і подія пройшла непоміченою.
  - Якщо `st.stop_possible() == true` і запиту на зупинку ще не було, об'єкт додає себе в потокобезпечний зв'язний список реєстрацій усередині `stop_state`.
  - Якщо `st.stop_possible() == false`, реєстрація не виконується.
- **Поведінка деструктора**:
  - Атомарно вилучає себе зі списку підписників `stop_state`.
  - **Критична гарантія блокування**: Якщо відповідна функція зворотного виклику прямо зараз виконується в іншому потоці (внаслідок виклику `request_stop()`), деструктор `~stop_callback()` **блокує поточний потік** до повного завершення виконання тіла колбека. Це гарантує, що ресурси, захоплені лямбдою за посиланням на локальному стеку, не будуть знищені доти, доки колбек не закінчить роботу.
  - **Захист від дедлоку**: Якщо деструктор викликається всередині самого колбека (у тому самому потоці), блокування не відбувається.

---

## 5. Розширення std::condition_variable_any для скасування

Стандарт C++20 додав у клас `std::condition_variable_any` перевантаження, які приймають `std::stop_token`. Це дозволяє безпечно виводити потік зі стану сну при надходженні сигналу скасування без штучних періодичних таймаутів та циклічних опитувань.

```cpp
namespace std {
    class condition_variable_any {
    public:
        // Базове переривне очікування
        template<class Lock, class Predicate>
        bool wait(Lock& lock, stop_token stoken, Predicate pred);

        // Переривне очікування з відносним таймаутом
        template<class Lock, class Rep, class Period, class Predicate>
        bool wait_for(Lock& lock, stop_token stoken,
                      const chrono::duration<Rep, Period>& rel_time,
                      Predicate pred);

        // Переривне очікування з абсолютним часом
        template<class Lock, class Clock, class Duration, class Predicate>
        bool wait_until(Lock& lock, stop_token stoken,
                        const chrono::time_point<Clock, Duration>& abs_time,
                        Predicate pred);
    };
}
```

### Чому std::condition_variable не отримала stop_token
Клас `std::condition_variable` у мові C++11 спроектований як максимально тонка обгортка навколо нативних примітивів операційної системи (таких як `pthread_cond_wait` у POSIX або `SleepConditionVariableSRW` у Windows API). Ці системні функції вимагають нативного м'ютекса ОС (`pthread_mutex_t` або `SRWLOCK`) і не мають вбудованого механізму реєстрації зовнішніх користувацьких функцій розблокування.

На противагу цьому, `std::condition_variable_any` реалізує власний рівень внутрішньої синхронізації та здатний працювати з будь-яким типом замка `Lock`, що задовольняє вимогам BasicLockable (методи `.lock()` та `.unlock()`), включаючи `std::unique_lock`, `std::shared_lock`, замки сторонніх бібліотек чи власні спінлоки.

### Алгоритм виконання `wait(lock, stoken, pred)`

1. Перевіряє предикат: якщо `pred()` повертає `true`, негайно повертає `true`.
2. Перевіряє токен: якщо `stoken.stop_requested() == true`, повертає поточне значення `pred()`.
3. Конструює внутрішній тимчасовий об'єкт `std::stop_callback`, який при надходженні сигналу скасування виконує `this->notify_all()`.
4. Входить у цикл блокуючого очікування:
   - Атомарно відпускає `lock` і переводить потік у стан сну на рівні операційної системи.
   - При пробудженні (через `notify_all`, виклик колбека зупинки або хибне пробудження) потік повторно захоплює `lock`.
   - Перевіряє предикат `pred()` або стан `stoken.stop_requested()`.
5. Знищує внутрішній `stop_callback` і повертає фінальне значення `pred()`.

---

## 6. Внутрішня будова stop_state та інваріанти моделі пам'яті

У стандартних бібліотеках C++ (GNU `libstdc++`, LLVM `libc++`, Microsoft MSVC STL) об'єкт `stop_state` реалізує компактне представлення лічильників та прапорців у єдиному атомарному слові:

```cpp
// Концептуальна структура stop_state у runtime
struct stop_state {
    // Пакування лічильників та прапорців в одне 64-бітне атомарне слово
    // [1 біт: stop_requested] [1 біт: locked] [31 біт: source_count] [31 біт: token_count]
    std::atomic<uint64_t> state_flags_{0};

    // Ідентифікатор потоку, який наразі виконує request_stop()
    std::atomic<std::thread::id> executing_thread_{};

    // Вказівник на початок зв'язного списку зареєстрованих об'єктів stop_callback
    stop_callback_base* head_callback_{nullptr};

    // М'ютекс або атомарний спінлок для захисту операцій вставки/видалення зі списку
    std::atomic_flag list_lock_ = ATOMIC_FLAG_INIT;
};
```

### Порядок пам'яті (Memory Ordering) та синхронізація

- Операція `request_stop()` встановлює біт запиту зупинки з семантикою `std::memory_order_acq_rel` або `std::memory_order_release`. На апаратних архітектурах x86-64 це відповідає звичайній інструкції запису або атомарній інструкції `lock bts` / `lock cmpxchg`, а на архітектурах ARMv8 транслюється в інструкцію `stlr` (Store-Release).
- Операція `stop_requested()` зчитує біт із семантикою `std::memory_order_acquire` (на ARMv8 — `ldar`, Load-Acquire).
- Між потоком, що викликав `request_stop()`, та потоком, що виконує `stop_requested()` або конструює `stop_callback`, формується відношення **synchronizes-with**. Усі операції запису в пам'ять, здійснені ініціатором до відправки сигналу, гарантовано стають видимими для робочого потоку (відношення **happens-before**). Це дозволяє безпечно передавати додаткові діагностичні структури або прапорці причини зупинки без використання додаткових м'ютексів.
- Застосування тегу `std::nostopstate` при конструюванні джерела дозволяє взагалі уникнути системного виклику алокатора динамічної пам'яті, створюючи дескриптор із нульовими накладними витратами.

---

## 7. Крайові випадки та поведінкові інваріанти

Під час використання компонентів `<stop_token>` виникають специфічні багатопотокові ситуації, поведінка яких строго регламентована стандартом:

### Рекурсивний виклик request_stop()
Якщо функція зворотного виклику всередині `std::stop_callback` сама викликає `request_stop()` для того самого або іншого пов'язаного об'єкта `std::stop_source`, другий виклик миттєво повертає `false`. Повторна ітерація по списку колбеків не запускається, що запобігає зацикленню.

### Реєстрація нового stop_callback під час виконання існуючих
Якщо один із колбеків під час свого виконання створює новий об'єкт `std::stop_callback` на той самий токен, новий колбек не додається у список активної ітерації, а негайно виконується синхронно в поточному потоці прямо під час виконання свого конструктора.

### Знищення stop_source до завершення обчислень
Якщо всі екземпляри `std::stop_source` знищуються в головному потоці, робочий потік із копією `std::stop_token` продовжує безпечно працювати. Метод `stoken.stop_requested()` повертає `false`, а `stoken.stop_possible()` стає `false`. Пам'ять спільного стану `stop_state` не звільняється, доки живе хоча б один `stop_token`.

### Винятки всередині stop_callback
Усі операції з `std::stop_callback` повинні бути виняткобезпечними. Якщо користувацька лямбда або функтор викидає виняток під час виконання в тілі `request_stop()`, runtime C++ не передає виняток викликачу `request_stop()`, а негайно викликає `std::terminate()`. Тому будь-які потенційні винятки всередині колбека мають оброблятися локально через `try/catch`.

### Трансляція та каскадування скасування (Forwarding Stop Sources)
Часто виникає потреба створити композитний токен, який скасовується або за сигналом батьківського джерела, або за локальним таймаутом. Для цього створюється локальний `std::stop_source`, а на батьківський токен реєструється колбек, який транслює запит зупинки:

```cpp
// Ідіома трансляції сигналу скасування
std::stop_source local_source;
std::stop_callback forwarder(parent_token, [&local_source] {
    local_source.request_stop();
});
// Тепер local_source.get_token() реагуватиме і на parent_token, і на власні події
```

---

## 8. Зведена таблиця характеристик методів

| Метод / Операція | Потокобезпека | Гарантія винятків | Складність за часом |
| :--- | :--- | :--- | :--- |
| `stop_token::stop_requested()` | Потокобезпечний (Lock-free atomic load) | `noexcept` | `O(1)` |
| `stop_token::stop_possible()` | Потокобезпечний | `noexcept` | `O(1)` |
| `stop_token` (копіювання / переміщення) | Потокобезпечний (Atomic refcount increment) | `noexcept` | `O(1)` |
| `stop_source::request_stop()` | Потокобезпечний (Atomic CAS + послідовний виклик колбеків) | `noexcept` | `O(N)`, де `N` — кількість зареєстрованих колбеків |
| `stop_source::get_token()` | Потокобезпечний | `noexcept` | `O(1)` |
| Конструктор `stop_callback` | Потокобезпечний (Захищене додавання до списку стану) | `noexcept`, якщо конструктор копіювання/переміщення `cb` є `noexcept` | `O(1)` або час виклику колбека при негайному запуску |
| Деструктор `~stop_callback` | Потокобезпечний (Видалення зі списку + блокуюче очікування) | `noexcept` | `O(1)` або час очікування завершення паралельного виклику |
| `cv_any.wait(lock, stoken, pred)` | Потокобезпечний відносно `lock` та `stoken` | Може викидати винятки, якщо операції з `lock` або `pred()` кидають | Залежить від тривалості очікування події |

На відміну від простого `std::atomic<bool>`, який вимагає окремого створення умовних змінних та ручного керування блокуваннями для сповіщення сплячих потоків, архітектура `std::stop_token` забезпечує цілісну систему зворотних викликів із повною апаратною гарантією захисту від стану гонитви між надходженням сигналу та реєстрацією нової підписки.

---

## 9. Практичні ідіоми застосування API

### Регулярне опитування токена в обчислювальному ядрі

Найпростіший патерн застосовується в циклах числової обробки, де потік періодично перевіряє стан токена без потреби в асинхронних перериваннях:

```cpp
#include <stop_token>
#include <iostream>
#include <vector>

void process_matrix_blocks(std::stop_token stoken, const std::vector<double>& matrix) {
    for (size_t block = 0; block < matrix.size(); ++block) {
        // Періодична атомарна перевірка запиту на скасування
        if (stoken.stop_requested()) {
            std::cout << "Обчислення перервано на блоці " << block << "\n";
            return;
        }
        // Виконання ресурсомісткого математичного кроку
    }
}
```

### Асинхронне переривання системного ресурсу через stop_callback

Коли потік виконує блокуючий ввід-вивід на мережевому сокеті, звичайне опитування `stop_requested()` безсиле, оскільки потік спить усередині ядра ОС. У цьому випадку `stop_callback` реєструє функцію примусового закриття сокета:

```cpp
#include <stop_token>
#include <iostream>

struct SocketHandler {
    int socket_fd = 42;

    void shutdown_socket() {
        std::cout << "Виклик shutdown() для сокета " << socket_fd << "\n";
    }
};

void handle_network_stream(std::stop_token stoken) {
    SocketHandler handler;

    // Реєстрація зворотного виклику: якщо надійде сигнал зупинки,
    // сокет буде переведено в стан shutdown, що миттєво розблокує системний виклик read()
    std::stop_callback callback(stoken, [&handler] {
        handler.shutdown_socket();
    });

    // Блокуюче читання з дескриптора
}
```

### Переривна черга завдань на condition_variable_any

Об'єднання `std::condition_variable_any` та `std::stop_token` формує надійний базис для пулів потоків, де робітники можуть миттєво прокидатися при завершенні роботи програми:

```cpp
#include <condition_variable>
#include <mutex>
#include <queue>
#include <stop_token>
#include <iostream>

template<typename T>
class InterruptibleQueue {
    std::queue<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable_any cv_;

public:
    void push(T value) {
        {
            std::lock_guard lock(mutex_);
            queue_.push(std::move(value));
        }
        cv_.notify_one();
    }

    bool pop(T& value, std::stop_token stoken) {
        std::unique_lock lock(mutex_);
        // Очікування завершується при надходженні елемента АБО сигналу скасування
        bool success = cv_.wait(lock, stoken, [this] {
            return !queue_.empty();
        });

        if (!success || queue_.empty()) {
            return false; // Скасовано або черга порожня
        }

        value = std::move(queue_.front());
        queue_.pop();
        return true;
    }
};
```
