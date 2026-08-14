# 📋 Довідник паттернів CRTP та їх модернізація у C++23

<preknowlist>
- [Шаблони: параметризація типом](book:cpp-standards/templates-basics) — синтаксис та вимоги підстановки аргументів.
- [Коректність за const](book:cpp-standards/const-correctness) — правила виклику const/non-const методів.
- [Явний параметр об'єкта](book:cpp-standards/deducing-this) — синтаксис deducing this у C++23.
</preknowlist>

Цей довідник систематизує стандартні й прикладні конструкти на основі CRTP, показує їхні сигнатури, інваріанти й захисні механізми та наводить таблицю еквівалентів у C++23.

Шаблон CRTP є універсальним інструментом узагальненого програмування, який формує фундаментальний контракт між базовим шаблонним класом та похідним типом. На відміну від класичного ООП-інтерфейсу на основі віртуальних функцій, де зв'язок між базовим і похідним класом виражається через індирекцію таблиці віртуальних методів під час виконання програми, контракт CRTP повністю обчислюється, перевіряється та оптимізується компілятором під час збірки.

Основними завданнями цього довідника є надання вичерпного опису інтерфейсних контрактів, аналіз поведінки системи в крайових випадках, розбір реалізації CRTP у стандартній бібліотеці C++ та зведена специфікація для переходу на нові стандарти мови.

---

## 1. Специфікація фундаментальних паттернів CRTP

### А. Паттерн Static Interface (Статичний шаблонний метод)

Паттерн статичного інтерфейсу є безпосередньою альтернативою класичному віртуальному поліморфізму. Головне призначення цього паттерну полягає у визначенні єдиного алгоритму обробки у базовому класі з викликом точкових реалізацій із похідного класу без використання віртуальних таблиць.

#### Контракт та інваріанти:
1. Базовий клас `StaticInterface<Derived>` визначає публічний non-virtual метод `execute()`, який є єдиною точкою входу для зовнішніх клієнтів.
2. Похідний клас `Derived` зобов'язаний надати приватну або публічну реалізацію `execute_impl()` із сумісним типом повернення.
3. Усі виклики реалізації здійснюються через елевацію типів `static_cast<Derived*>(this)` або `static_cast<const Derived*>(this)`.
4. Якщо похідний клас не реалізує метод `execute_impl()`, помилка компіляції виникає безпосередньо у місці виклику `execute()`, а не під час створення об'єкта.
5. Приведення `static_cast<Derived*>(this)` гарантує відсутність винятків (`nothrow`), якщо реалізація `execute_impl()` позначена кваліфікатором `noexcept`.

#### Захисні механізми та перевірка контрактів:

Для того щоб унеможливити випадкове помилкове успадкування, коли один похідний клас випадково передає інший тип у базовий шаблон (наприклад, `class DerivedB : public StaticInterface<DerivedA>`), базовий конструктор роблять приватним і надають доступ похідному класу через `friend`:

```cpp
#include <concepts>
#include <type_traits>

template <typename Derived>
class StaticInterface {
private:
    StaticInterface() = default;
    friend Derived;

public:
    void execute() noexcept(noexcept(std::declval<Derived&>().execute_impl())) {
        Derived& self = *static_cast<Derived*>(this);
        
        static_assert(requires(Derived d) { d.execute_impl(); },
            "Похідний клас зобов'язаний реалізувати void execute_impl()");
            
        self.execute_impl();
    }

    void execute() const noexcept(noexcept(std::declval<const Derived&>().execute_impl())) {
        const Derived& self = *static_cast<const Derived*>(this);
        
        static_assert(requires(const Derived d) { d.execute_impl(); },
            "Похідний клас зобов'язаний реалізувати void execute_impl() const");
            
        self.execute_impl();
    }
};
```

Використання статичних тверджень `static_assert` разом із концептами C++20 дозволяє отримати зрозуміле повідомлення про помилку під час збірки проєкту замість незрозумілих простирадл помилок компілятора.

---

### Б. Паттерн Mixin Functionality (Композиція міксинів)

Міксини призначені для автоматичного розширення функціональних можливостей похідного класу шляхом унаслідування від кількох незалежних CRTP-шаблонів. Головною перевагою цього підходу є відсутність будь-яких накладних витрат пам'яті.

#### Контракт та інваріанти:
1. Кожен міксин є безпосередньою базою для похідного класу і не містить власних полів даних чи віртуальних методів.
2. Завдяки оптимізації порожньої бази (Empty Base Optimization, EBO) під час розташування у пам'яті компілятор не виділяє жодного байта під базові класи, тому підсумковий розмір об'єкта похідного класу дорівнює розміру його власних полів.
3. Кожен міксин звертається до методів або полів похідного класу через `static_cast<const Derived*>(this)`.
4. Міксини є повністю незалежними між собою, що дозволяє довільно комбінувати їх у будь-яких поєднаннях.

#### Реалізація комплексу міксинів для логування та форматування:

```cpp
#include <iostream>
#include <string>

template <typename Derived>
class Formattable {
public:
    void print() const {
        const auto& self = *static_cast<const Derived*>(this);
        std::cout << self.to_string() << "\n";
    }
};

template <typename Derived>
class Sizable {
public:
    size_t byte_size() const noexcept {
        return sizeof(Derived);
    }
};

class UserPayload : public Formattable<UserPayload>, public Sizable<UserPayload> {
public:
    uint64_t user_id{0};
    uint32_t flags{0};

    std::string to_string() const {
        return "UserPayload[id=" + std::to_string(user_id) + "]";
    }
};
```

Завдяки такій структурі клас `UserPayload` отримує функціональність двох розширень без додавання `vptr` чи службових полів.

---

### В. Паттерн Fluent Builder (Метод-чейнінг із збереженням типу)

Паттерн призначений для побудови розширюваних інтерфейсів покрокового конфігурування об'єктів (паттерн Builder). У класичному спадкуванні методи базового класу повертають посилання на базовий тип, що унеможливлює продовження ланцюжка викликів методами похідного класу. У CRTP цей недолік повністю усувається.

#### Контракт та інваріанти:
1. Базовий клас `FluentBuilder<Derived>` повертає посилання `Derived&` із кожного модифікуючого метода.
2. При багаторівневих ієрархіях тип повернення не втрачає інформацію про кінцевий похідний клас.
3. Для rvalue-об'єктів розробляються перевантаження, які повертають `Derived&&`, дозволяючи ефективне переміщення тимчасових об'єктів у ланцюжках.

#### Реалізація конфігуратора мережевого з'єднання:

```cpp
template <typename Derived>
class NetworkBuilder {
public:
    Derived& set_host(std::string host) & {
        Derived& self = *static_cast<Derived*>(this);
        self.host_ = std::move(host);
        return self;
    }

    Derived&& set_host(std::string host) && {
        Derived& self = *static_cast<Derived*>(this);
        self.host_ = std::move(host);
        return std::move(self);
    }

    Derived& set_port(uint16_t port) & {
        Derived& self = *static_cast<Derived*>(this);
        self.port_ = port;
        return self;
    }
};

class SecureNetworkBuilder : public NetworkBuilder<SecureNetworkBuilder> {
    friend class NetworkBuilder<SecureNetworkBuilder>;
    std::string host_;
    uint16_t port_{80};
    std::string tls_certificate_;

public:
    SecureNetworkBuilder& set_certificate(std::string cert) & {
        tls_certificate_ = std::move(cert);
        return *this;
    }
};
```

---

### Г. Паттерн Static Counter (Підрахунок екземплярів у пам'яті)

Паттерн призначений для ведення точного обліку живих екземплярів об'єктів у пам'яті окремо для кожного похідного типу.

#### Контракт та інваріанти:
1. Статична змінна-лічильник існує окремо для кожної спеціалізації `InstanceCounter<T>`.
2. Конструктори копіювання, переміщення та деструктор підтримують актуальний стан лічильника.
3. Для підтримки багатопотокового середовища використовується атомарний тип `std::atomic<size_t>` із розслабленим порядком пам'яті `memory_order_relaxed`. Вплив на крізьпотокову синхронізацію відсутній, що забезпечує мінімальні затримки процесора.

```cpp
#include <atomic>

template <typename Derived>
class ThreadSafeCounter {
public:
    ThreadSafeCounter() noexcept {
        counter_.fetch_add(1, std::memory_order_relaxed);
    }

    ThreadSafeCounter(const ThreadSafeCounter&) noexcept {
        counter_.fetch_add(1, std::memory_order_relaxed);
    }

    ThreadSafeCounter(ThreadSafeCounter&&) noexcept {
        counter_.fetch_add(1, std::memory_order_relaxed);
    }

    ~ThreadSafeCounter() noexcept {
        counter_.fetch_sub(1, std::memory_order_relaxed);
    }

    static size_t active_instances() noexcept {
        return counter_.load(std::memory_order_relaxed);
    }

private:
    inline static std::atomic<size_t> counter_{0};
};

class ConnectionHandle : public ThreadSafeCounter<ConnectionHandle> {};
class DatabaseSession : public ThreadSafeCounter<DatabaseSession> {};
```

---

### Д. Паттерн Static Visitor (Відвідувач під час компіляції)

Паттерн «Відвідувач» у класичному ООП вимагає подвійної індирекції через подвійне перевизначення віртуальних методів `accept(IVisitor&)` та `visit(ConcreteNode&)`. За допомогою CRTP відвідувач будується повністю у статичному просторі типів.

#### Контракт та інваріанти:
1. Базовий клас `StaticVisitor<Derived>` надає метод `visit_node(Node& node)`, який переспрямовує обробку на відповідний спеціалізований метод похідного відвідувача.
2. Жодного віртуального виклику не виконується; компілятор будує пряму таблицю переходів або підставляє тіла обробників безпосередньо за допомогою шаблонів.
3. Додавання нових вузлів або методів обробки перевіряється під час збірки проєкту без створення невидимих помилок під час виконання.

```cpp
template <typename Derived>
class StaticVisitor {
public:
    template <typename NodeTy>
    void dispatch(NodeTy& node) {
        Derived& self = *static_cast<Derived*>(this);
        self.handle(node);
    }
};

struct ASTNodeA {};
struct ASTNodeB {};

class ASTInspector : public StaticVisitor<ASTInspector> {
public:
    void handle(ASTNodeA& a) {
        std::cout << "Inspecting ASTNodeA\n";
    }
    void handle(ASTNodeB& b) {
        std::cout << "Inspecting ASTNodeB\n";
    }
};
```

---

### Е. Паттерн Polyfilled Optional Interface (Опційні методи з SFINAE/Concepts)

У багатьох фреймворках базовий CRTP-клас викликає метод похідного класу лише за умови, що похідний клас дійсно його реалізував. Якщо похідний клас не реалізує метод (наприклад, `pre_process()`), базовий клас упевнено викликає порожню заглушку за замовчуванням.

#### Контракт та інваріанти:
1. Базовий клас перевіряє наявність метода у похідному класі за допомогою `if constexpr` та виразів концептів C++20.
2. Похідний клас має можливість не перевизначати опційні методи, що знижує обсяг обов'язкового коду для простих об'єктів.
3. Оптимізатор компілятора повністю видаляє гілку `if constexpr`, якщо умова є хибною, усуваючи навіть порожню інструкцію виклику.

```cpp
template <typename Derived>
class EventPipeline {
public:
    void process_event() {
        Derived& self = *static_cast<Derived*>(this);
        
        // Перевірка наявності опційного метода під час компіляції
        if constexpr (requires { self.before_process(); }) {
            self.before_process();
        }
        
        self.main_process();
        
        if constexpr (requires { self.after_process(); }) {
            self.after_process();
        }
    }
};

class SimpleHandler : public EventPipeline<SimpleHandler> {
public:
    void main_process() {
        std::cout << "Executing main event handler\n";
    }
};
```

---

### Ж. Паттерн Static State Machine (Скінченний автомат на CRTP)

Паттерн «Скінченний автомат» на основі CRTP дозволяє описувати стани та переходи системи під час компіляції без виділення пам'яті у купі (heap allocations) та без віртуальних функцій.

#### Контракт та інваріанти:
1. Кожен стан автомата є окремим типом, який успадковується від `StateBase<DerivedState>`.
2. Переходи між станами виконуються шляхом повернення нових об'єктів станів або через статичний диспетчер подій.
3. Компілятор повністю інлайнить усі переходи між станами у єдину послідовність машинних інструкцій.

```cpp
template <typename DerivedState>
class StateBase {
public:
    template <typename Event>
    void handle_event(const Event& event) {
        DerivedState& self = *static_cast<DerivedState*>(this);
        self.on_event(event);
    }
};

struct ConnectEvent {};

class DisconnectedState : public StateBase<DisconnectedState> {
public:
    void on_event(const ConnectEvent&) {
        std::cout << "Transitioning from Disconnected to Connecting\n";
    }
};
```

---

### З. Паттерн Thin Template Base (Захист від роздуття коду)

Для запобігання дублювання однакового машинного коду під час інстанціювання CRTP-шаблону для десятків похідних класів використовується комбінація нешаблонної бази та CRTP-інтерфейсу.

#### Контракт та інваріанти:
1. Загальна логіка, що не залежить від типів (наприклад, управління пам'яттю, робота з системними ресурсами, низькорівневе логування), виноситься у приватний або захищений нешаблонний базовий клас `NonTemplateBase`.
2. CRTP-шаблон успадковує `NonTemplateBase` і містить лише тонкі шаблони викликів через `static_cast<Derived*>(this)`.
3. Завдяки цьому згенерований двійковий файл не роздувається від нескінченних дублів мономорфного машинного коду.

```cpp
class NonTemplateStorage {
protected:
    void raw_write(const void* data, size_t size) {
        // Звичайний нешаблонний код, що існує в бінарнику в єдиному примірнику
    }
};

template <typename Derived>
class DataWriter : private NonTemplateStorage {
public:
    void write_object() {
        Derived& self = *static_cast<Derived*>(this);
        this->raw_write(&self, sizeof(Derived));
    }
};
```

---

### И. Паттерн Static Clone (Віртуальне клонування без vtable)

Паттерн статичного клонування дозволяє створювати дублікати об'єктів у графічних та ігрових системах із збереженням точного типу повернення через розумні вказівники.

#### Контракт та інваріанти:
1. Базовий клас `Cloneable<Derived>` надає метод `clone()`, який повертає `std::unique_ptr<Derived>`.
2. Виклик `clone()` виконує пряму ініціалізацію нового об'єкта через конструктор копіювання `Derived`.
3. Тип повернення точно відповідає похідному класу, усуваючи потребу у `dynamic_cast` або `static_cast` на стороні користувача.

```cpp
#include <memory>

template <typename Derived>
class Cloneable {
public:
    std::unique_ptr<Derived> clone() const {
        const auto& self = *static_cast<const Derived*>(this);
        return std::make_unique<Derived>(self);
    }
};

class GraphicPrimitive : public Cloneable<GraphicPrimitive> {
public:
    int x{0};
    int y{0};
};
```

---

### К. Паттерн Compile-time Property Map (Карта властивостей типу)

Паттерн карти властивостей дозволяє асоціювати метадані та властивості типів під час збірки без використання RTTI (`typeid`).

#### Контракт та інваріанти:
1. Базовий клас `PropertyMap<Derived>` надає статичні методи доступу до ідентифікаторів та метаданих типу.
2. Похідний клас оголошує статичні константи або `constexpr`-методи, які зчитуються базовим шаблоном без жодних інструкцій у коді виконання.

```cpp
template <typename Derived>
struct PropertyMap {
    static constexpr const char* name() noexcept {
        return Derived::type_name;
    }
    static constexpr uint32_t type_id() noexcept {
        return Derived::type_identifier;
    }
};

struct PacketA : PropertyMap<PacketA> {
    static constexpr const char* type_name = "PacketA";
    static constexpr uint32_t type_identifier = 0x1001;
};
```

---

### Л. Паттерн Static Serializer (Статична бінарна серіалізація)

Паттерн статичної серіалізації використовується у мережевих протоколах низької затримки для пакування структур даних без виділення динамічної пам'яті.

#### Контракт та інваріанти:
1. Базовий клас `StaticSerializer<Derived>` реалізує методи `encode()` та `decode()`, які звертаються до точної маски полів похідного класу.
2. Серіалізатор гарантує сумісність із порядком байтів (endianness) та підтримує нульове копіювання (Zero-Copy) завдяки прямому відображенню буфера.
3. Уся перевірка вирівнювання полів даних у пам'яті виконується під час збірки за допомогою `static_assert(alignof(Derived) <= 8)`.

```cpp
template <typename Derived>
class StaticSerializer {
public:
    size_t write_to_stream(uint8_t* stream) const {
        const auto& self = *static_cast<const Derived*>(this);
        std::memcpy(stream, &self, sizeof(Derived));
        return sizeof(Derived);
    }
};
```

---

## 2. Глибокий розбір CRTP у Стандартній Бібліотеці C++

### А. `std::enable_shared_from_this<T>`

Клас `std::enable_shared_from_this<T>` є найвідомішим прикладом застосування CRTP у стандартній бібліотеці C++. Його мета — надати об'єкту можливість безпечно створювати новий екземпляр `std::shared_ptr<T>`, який володіє цим самим об'єктом, зсередини своїх власних методів.

#### Внутрішня механіка роботи та інваріанти:
1. Клас `T` зобов'язаний відкрито (`public`) успадковуватися від `std::enable_shared_from_this<T>`.
2. Базовий клас `std::enable_shared_from_this` містить приватне поле `mutable std::weak_ptr<T> weak_this_`.
3. Під час виклику конструктора `std::shared_ptr<T>(T* ptr)` чи створення об'єкта через `std::make_shared<T>()`, конструктор розумного вказівника перевіряє, чи успадковується `T` від `std::enable_shared_from_this`. Якщо так, він ініціалізує поле `weak_this_` посиланням на створений керований блок (control block).
4. Під час виклику метода `shared_from_this()` здійснюється створення нового `std::shared_ptr<T>` з поля `weak_this_`, що автоматично збільшує спільний лічильник власників.
5. Для const-об'єктів надається перевантажений метод `shared_from_this() const`, який повертає екземпляр `std::shared_ptr<const T>`.

#### Критичні крайові випадки та помилки:
- **Виклик у конструкторі**: Якщо викликати `shared_from_this()` у конструкторі об'єкта `T`, поле `weak_this_` ще не буде ініціалізовано, оскільки зовнішній `shared_ptr` створюється лише після завершення роботи конструктора `T`. Це викликає виняток `std::bad_weak_ptr`.
- **Створення об'єкта на стеку**: Якщо об'єкт типу `T` розміщено на стеку або як приватне поле іншого класу без загортання у `shared_ptr`, виклик `shared_from_this()` так само кидає виняток `std::bad_weak_ptr`.
- **Багаторазове успадкування**: Якщо клас успадковується від двох різних CRTP-баз, кожна з яких базується на `enable_shared_from_this`, це створює невизначеність типів під час інстанціювання і вимагає створення проміжного нешаблонного інтерфейсу.
- **Управління пам'яттю**: Внутрішній weak_ptr утримує розмір керованого блоку у пам'яті до моменту знищення останньої weak-посилання, навіть після виклику деструктора об'єкта `T`.

```cpp
#include <memory>
#include <iostream>

class WorkerNode : public std::enable_shared_from_this<WorkerNode> {
public:
    void register_in_cluster() {
        std::shared_ptr<WorkerNode> self_ptr = shared_from_this();
        std::cout << "Node registered with use_count: " << self_ptr.use_count() << "\n";
    }
};
```

---

### Б. `std::ranges::view_interface<Derived>`

У C++20 стандартна бібліотека отримала модуль діапазонів (Ranges), у якому клас `std::ranges::view_interface<Derived>` використовує CRTP для швидкого проективання власних видів (views).

#### Інтерфейсний контракт та вимоги:
Для того щоб отримати повноцінний вид із багатим інтерфейсом, розробникові достатньо реалізувати у своєму класі лише два методи: `begin()` та `end()`.

На основі цих двох методів CRTP-база `view_interface` автоматично підставляє такі методи:
- `empty()` — перевіряє рівність `begin() == end()`.
- `operator bool()` — повертає `!empty()`.
- `data()` — повертає сирий вказівник на елементи для суцільних діапазонів (contiguous ranges).
- `size()` — повертає кількість елементів, якщо відстань між ітераторами обчислювана.
- `front()` та `back()` — повертають посилання на перший та останній елементи.
- `operator[]` — надає доступ за індексом для діапазонів випадкового доступу.

Завдяки цьому використання CRTP у бібліотеці діапазонів економить тисячі рядків дубльованого коду та забезпечує повний інлайнінг усіх операцій обходу.

---

## 3. Таблиця порівняння та міграції: CRTP проти C++23 `deducing this`

Стандарт C++23 впровадив пропозицію P0847R7 (Explicit Object Parameter / `deducing this`), яка радикально спрощує реалізацію статичного поліморфізму та міксинів, роблячи шаблонне успадкування класичного CRTP застарілим для більшості нових завдань.

Основними перевагами нового підходу є спрощення синтаксису оголошення класів, відсутність необхідності використання шаблонного успадкування видів `class Derived : public Base<Derived>` та повне усунення явних операцій примусового кастування через `static_cast`. Крім того, явний параметр об'єкта повністю вирішує давню проблему обробки методів із різними кваліфікаторами константності та категорії значень (lvalue/rvalue).

Для проєктування нових бібліотек у C++23 рекомендовано надавати перевагу саме явному параметру об'єкта, залишаючи класичний CRTP для сумісності зі старими стандартами мови C++98–C++20.

### Зведена порівняльна таблиця характеристик

| Параметр / Особливість | Класичний CRTP (C++98–C++20) | C++23 Deducing This (`this auto&& self`) |
| :--- | :--- | :--- |
| **Природа базового класу** | Шаблонний клас (`template <class D> struct Base`) | Звичайний нешаблонний клас (`struct Base`) |
| **Синтаксис оголошення похідного класу** | `class Derived : public Base<Derived>` | `class Derived : public Base` |
| **Механізм доступу до Derived** | Неявний каст `static_cast<Derived*>(this)` | Явний параметр об'єкта `self` вже має тип `Derived` |
| **Обробка кваліфікаторів const/rvalue** | Вимагає окремих методів чи шаблонних кастів | Одне тіло функції для всіх варіацій |
| **Захист від помилок у назві типу** | Потребує `private` конструктора й `friend` | Неможливо припуститися помилки (немає параметра шаблону) |
| **Вплив на розмір бінарного файлу** | Створює окрему спеціалізацію шаблону для кожного похідного типу | Єдиний нешаблонний базовий клас (завдяки EBO) |
| **Придатність для `std::enable_shared_from_this`** | Повна підтримка | Зберігається у вигляді CRTP для зворотної сумісності |

---

### Приклади еквівалентного перетворення коду

#### 1. Статичний міксин друку

:::tabs
```cpp
// C++17 CRTP
template <typename Derived>
struct PrintableCRTP {
    void print() const {
        const auto& self = *static_cast<const Derived*>(this);
        std::cout << self.get_name() << "\n";
    }
};

class Item : public PrintableCRTP<Item> {
public:
    std::string get_name() const { return "ItemA"; }
};
```
```cpp
// C++23 Deducing This
struct Printable23 {
    void print(this const auto& self) {
        std::cout << self.get_name() << "\n";
    }
};

class Item : public Printable23 {
public:
    std::string get_name() const { return "ItemA"; }
};
```
:::

#### 2. Плавний інтерфейс (Fluent Builder)

:::tabs
```cpp
// C++17 CRTP Fluent Builder
template <typename Derived>
class ButtonBuilderCRTP {
public:
    Derived& set_label(std::string lbl) {
        Derived& self = *static_cast<Derived*>(this);
        self.label_ = std::move(lbl);
        return self;
    }
};

class IconButton : public ButtonBuilderCRTP<IconButton> {
public:
    std::string label_;
};
```
```cpp
// C++23 Deducing This Fluent Builder
class ButtonBuilder23 {
public:
    template <typename Self>
    auto&& set_label(this Self&& self, std::string lbl) {
        self.label_ = std::move(lbl);
        return std::forward<Self>(self);
    }
};

class IconButton : public ButtonBuilder23 {
public:
    std::string label_;
};
```
:::

Завдяки C++23 явний параметр об'єкта витісняє CRTP у повсякденних завданнях створення міксинів, роблячи код простішим, виразнішим та безпечнішим, при цьому повністю зберігаючи нульову ціну виконання під час роботи програми.
