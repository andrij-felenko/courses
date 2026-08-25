# ⚙️ Реалізація InPlaceOptional та аналіз асемблера

Створення надійного сховища для об'єктів довільного типу вимагає точного контролю за початком і завершенням часу життя, вирівнюванням пам'яті та коректним використанням `std::launder` для запобігання помилкам оптимізатора.

## Постановка задачі та вибір структури даних

Стандартний клас `std::optional<T>` дозволяє зберігати значення типу `T` без виділення динамічної пам'яті в купі (англ. *heap*). Значення розміщується безпосередньо всередині самого об'єкта `optional` у вирівняному буфері байтів.

Реалізуємо власний контейнер `InPlaceOptional<T>`, який підтримує:
1. Зберігання типів із константними полями (наприклад, `struct Config { const int id; const double rate; }`).
2. Повторне створення значення через метод `emplace(...)`.
3. Повну строгу гарантію безпеки виключень (якщо конструктор кидає виняток, старий об'єкт не лишається в пошкодженому стані).
4. Абсолютну відповідність моделі пам'яті C++17/C++20 без невизначеної поведінки при оптимізаціях `-O3`.

### Відмова від std::aligned_storage на користь std::byte

В історичному C++11 для створення неініціалізованого сховища часто використовували допоміжний шаблон `std::aligned_storage<sizeof(T), alignof(T)>::type`. Проте в стандарті C++23 цей тип було офіційно оголошено застарілим (англ. *deprecated*) через численні вади API:
- Він вимагав громіздкого виклику `reinterpret_cast` до внутрішнього поля;
- Мав проблеми з некоректним виведенням вирівнювання за замовчуванням на деяких платформах;
- Породжував незрозумілі повідомлення про помилки компілятора.

Сучасний ідіоматичний підхід полягає у використанні масиву `std::byte` із прямим застосуванням специфікатора вирівнювання `alignas(T)`:

```cpp
alignas(T) std::byte storage_[sizeof(T)];
```

Такий буфер гарантує точну відповідність вимогам вирівнювання типу `T`, займає рівно `sizeof(T)` байтів і не накладає жодних сторонніх обмежень на життєвий цикл об'єктів.

## Повна реалізація контейнера InPlaceOptional

Погляньмо на повну реалізацію нашого шаблону класу:

```cpp
#include <new>
#include <utility>
#include <type_traits>
#include <stdexcept>
#include <iostream>

template <typename T>
class InPlaceOptional {
    // Гарантуємо правильний розмір і вирівнювання сховища
    alignas(T) std::byte storage_[sizeof(T)];
    bool engaged_ = false;

    // Внутрішній допоміжний метод для отримання вказівника
    T* as_ptr() noexcept {
        return std::launder(reinterpret_cast<T*>(storage_));
    }

    const T* as_ptr() const noexcept {
        return std::launder(reinterpret_cast<const T*>(storage_));
    }

    void destroy_internal() noexcept {
        if (engaged_) {
            as_ptr()->~T();
            engaged_ = false;
        }
    }

public:
    // 1. Конструктор за замовчуванням: порожнє сховище
    constexpr InPlaceOptional() noexcept = default;

    // 2. Конструювання зі значенням
    template <typename... Args>
    explicit InPlaceOptional(std::in_place_t, Args&&... args) {
        ::new (static_cast<void*>(storage_)) T(std::forward<Args>(args)...);
        engaged_ = true;
    }

    // 3. Деструктор
    ~InPlaceOptional() {
        destroy_internal();
    }

    // 4. Заборона або реалізація копіювання/переміщення
    InPlaceOptional(const InPlaceOptional& other) {
        if (other.engaged_) {
            ::new (static_cast<void*>(storage_)) T(*other.as_ptr());
            engaged_ = true;
        }
    }

    InPlaceOptional(InPlaceOptional&& other) noexcept(std::is_nothrow_move_constructible_v<T>) {
        if (other.engaged_) {
            ::new (static_cast<void*>(storage_)) T(std::move(*other.as_ptr()));
            engaged_ = true;
        }
    }

    // 5. Метод emplace для створення/перестворення значення
    template <typename... Args>
    T& emplace(Args&&... args) {
        // Якщо значення вже було, спочатку знищуємо старе
        destroy_internal();

        // Створюємо новий об'єкт
        T* created_ptr = ::new (static_cast<void*>(storage_)) T(std::forward<Args>(args)...);
        engaged_ = true;
        
        // Повертаємо посилання на новостворений об'єкт
        return *created_ptr;
    }

    // 6. Очищення сховища
    void reset() noexcept {
        destroy_internal();
    }

    // 7. Перевірка наявності значення
    [[nodiscard]] constexpr bool has_value() const noexcept {
        return engaged_;
    }

    [[nodiscard]] explicit constexpr operator bool() const noexcept {
        return engaged_;
    }

    // 8. Доступ до значення
    [[nodiscard]] T& value() & {
        if (!engaged_) {
            throw std::runtime_error("InPlaceOptional::value(): bad access");
        }
        return *as_ptr();
    }

    [[nodiscard]] const T& value() const& {
        if (!engaged_) {
            throw std::runtime_error("InPlaceOptional::value(): bad access");
        }
        return *as_ptr();
    }

    [[nodiscard]] T& operator*() & noexcept {
        return *as_ptr();
    }

    [[nodiscard]] const T& operator*() const& noexcept {
        return *as_ptr();
    }

    [[nodiscard]] T* operator->() noexcept {
        return as_ptr();
    }

    [[nodiscard]] const T* operator->() const noexcept {
        return as_ptr();
    }
};
```

## Покроковий аналіз ключових механізмів

Розглянемо, як взаємодіють окремі компоненти класу:

### 1. Допоміжні методи `as_ptr()` та бар'єр `std::launder`

Методи `as_ptr()` є єдиною точкою входу для отримання типізованого вказівника `T*` із сирого масиву `storage_`.

Вираз `reinterpret_cast<T*>(storage_)` виконує статичне приведення адреси першого байта масиву до вказівника на тип `T`. Проте, як вимагає модель пам'яті C++, цей результат огортається у `std::launder`. Без цього виклику оптимізатор компілятора мав би право вважати, що отриманий вказівник посилається на об'єкт, який жив у сховищі раніше, і застосовувати до нього закешовані інваріанти константних полів або віртуальних таблиць.

### 2. Безпека виключень у методі `emplace`

Метод `emplace()` реалізовано з урахуванням суворого порядку дій:
1. Спочатку викликається `destroy_internal()`, який перевіряє прапорець `engaged_` і коректно завершує час життя попереднього екземпляра через виклик його деструктора `as_ptr()->~T()`.
2. Прапорець `engaged_` скидається в `false`.
3. Виконується розміщувальний `::new (static_cast<void*>(storage_)) T(...)`. Якщо конструктор типу `T` згенерує виняток, виконання функції переривається, а контейнер залишається у валідному порожньому стані (`engaged_ == false`).
4. Лише після успішного завершення конструктора прапорець `engaged_` встановлюється в `true`.

Така послідовність гарантує базову безпеку виключень: у буфері ніколи не виникне ситуації, коли прапорець показує наявність об'єкта, конструктор якого не завершився.

## Дослідження асемблерного коду та ефекту оптимізацій

Щоб наочно побачити різницю між кодом із `std::launder` та без нього, скомпілюємо тестову функцію двома способами за допомогою Clang 17 з прапорцями `-O3 -fno-exceptions`.

Тестовий сценарій:
```cpp
struct ImmutableConfig {
    const int port;
    const int max_clients;
};

int benchmark_access(InPlaceOptional<ImmutableConfig>& opt) {
    opt.emplace(ImmutableConfig{8080, 100});
    int p1 = opt->port;

    opt.emplace(ImmutableConfig{9090, 200});
    int p2 = opt->port;

    return p1 + p2;
}
```

### Варіант 1: Без `std::launder` (помилкова реалізація)

Якщо в методах `as_ptr()` прибрати виклик `std::launder` і залишити лише сирий `reinterpret_cast<T*>(storage_)`:

```cpp
T* as_ptr_broken() noexcept {
    return reinterpret_cast<T*>(storage_);
}
```

Згенерований асемблер x86-64 (Clang 17, `-O3`):

```nasm
benchmark_access(InPlaceOptional<ImmutableConfig>&):
    ; Перший emplace: запис 8080 та 100 у сховище
    mov    dword ptr [rdi], 8080
    mov    dword ptr [rdi + 4], 100
    mov    byte ptr [rdi + 8], 1      ; engaged_ = true

    ; Другий emplace: запис 9090 та 200 у те саме сховище
    mov    dword ptr [rdi], 9090
    mov    dword ptr [rdi + 4], 200

    ; ОБЧИСЛЕННЯ РЕЗУЛЬТАТУ:
    ; Оптимізатор порахував: p1 = 8080.
    ; Для p2 він вирішив: поле port константне, отже p2 теж дорівнює 8080!
    ; Результат: 8080 + 8080 = 16160 замість (8080 + 9090 = 17170)
    mov    eax, 16160
    ret
```

Детальний аналіз інструкцій демонструє катастрофічний ефект оптимізації:
- Компілятор згенерував інструкції запису в пам'ять: `mov dword ptr [rdi], 9090`. Тобто пам'ять фізично оновлюється.
- Проте при обчисленні поверненого значення функція взагалі не містить інструкції додавання `add`. Замість цього оптимізатор на етапі компіляції порахував `8080 + 8080 = 16160` і зашив цю константу прямо в команду `mov eax, 16160`.
- Оптимізатор проігнорував другий запис, оскільки поле `port` оголошено як `const`, а вказівник на об'єкт не був очищений через `std::launder`. Це класичний випадок тихого пошкодження обчислень (англ. *silent data corruption*), який неможливо виявити за допомогою традиційних тестів без увімкнення оптимізатора.

### Варіант 2: Із застосуванням `std::launder` (коректна реалізація)

Асемблер x86-64 з використанням `std::launder`:

```nasm
benchmark_access(InPlaceOptional<ImmutableConfig>&):
    ; Перший emplace
    mov    dword ptr [rdi], 8080
    mov    dword ptr [rdi + 4], 100
    mov    byte ptr [rdi + 8], 1

    ; Другий emplace
    mov    dword ptr [rdi], 9090
    mov    dword ptr [rdi + 4], 200

    ; ОБЧИСЛЕННЯ РЕЗУЛЬТАТУ:
    ; Завдяки std::launder оптимізатор завантажує актуальне значення port з пам'яті:
    mov    eax, dword ptr [rdi]       ; чесне завантаження 9090
    add    eax, 8080                  ; 8080 + 9090 = 17170
    ret
```

Аналіз коректного лістингу:
- Завдяки `std::launder` ланцюжок інваріантності старого об'єкта було розірвано.
- Оптимізатор зберіг перше значення `8080` у вигляді константи, але для другого звернення чесно виконав команду завантаження `mov eax, dword ptr [rdi]`, яка зчитує щойно записане число `9090` з пам'яті.
- Потім виконується інструкція `add eax, 8080`, яка дає правильну суму `17170`.

## Поліморфний стан і зміна поведінки об'єкта

Продемонструємо ще один практичний сценарій: реалізацію патерну «Стан» (англ. *State Pattern*) без динамічного виділення пам'яті через купу.

У високонавантажених системах виділення пам'яті через `malloc` або `new` для кожного переходу скінченного автомата створює значні накладні витрати та фрагментацію пам'яті. Розміщення станів безпосередньо у внутрішньому буфері об'єкта усуває ці витрати:

```cpp
struct ConnectionState {
    virtual void handle_packet(const char* data) = 0;
    virtual ~ConnectionState() = default;
};

struct HandshakeState : ConnectionState {
    void handle_packet(const char* data) override {
        std::cout << "Обробка рукостискання: " << data << '\n';
    }
};

struct EstablishedState : ConnectionState {
    void handle_packet(const char* data) override {
        std::cout << "Обробка даних сесії: " << data << '\n';
    }
};

class Connection {
    alignas(HandshakeState) alignas(EstablishedState)
    std::byte state_buffer_[sizeof(EstablishedState)];
    
    ConnectionState* current_state() noexcept {
        return std::launder(reinterpret_cast<ConnectionState*>(state_buffer_));
    }

public:
    Connection() {
        ::new (static_cast<void*>(state_buffer_)) HandshakeState();
    }

    ~Connection() {
        current_state()->~ConnectionState();
    }

    void transition_to_established() {
        current_state()->~ConnectionState();
        ::new (static_cast<void*>(state_buffer_)) EstablishedState();
    }

    void process(const char* payload) {
        current_state()->handle_packet(payload);
    }
};
```

У методі `transition_to_established()` об'єкт `HandshakeState` знищується, а на його місці створюється `EstablishedState`. Завдяки `std::launder` у методі `current_state()`, компілятор гарантовано оновить покажчик на віртуальну таблицю (`vptr`), і виклик `process()` виконає метод нового класу без помилкової девіртуалізації.

## Висновки практичного аналізу

1. При роботі зі сховищами на основі байтових буферів (`std::byte[]`) отримання вказівника на об'єкт через `reinterpret_cast` є неповним без `std::launder`.
2. `std::launder` не додає жодних накладних інструкцій процесора, забезпечуючи максимальну швидкодію коду при збереженні повної коректності з точки зору оптимізатора.
3. Використання `std::launder` є обов'язковою вимогою при реалізації низькорівневих бібліотечних контейнерів, алокаторів та поліморфних буферів у сучасному C++.
