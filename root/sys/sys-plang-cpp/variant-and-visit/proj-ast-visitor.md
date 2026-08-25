# 🛠️ Практичні проєкти: Синтаксичне дерево виразів (AST) та Автомат станів (FSM)

Вставка розгортає два практичних проєкти промислового рівня, де застосування `std::variant` та `std::visit` забезпечує статичну безпеку типів, відсутність виділення пам'яті у купі та обробку за один крок O(1).

---

## Проєкт 1: Побудова та обчислення синтаксичного дерева виразів (AST Evaluator)

У компіляторах, інтерпретаторах та парсерах математичних виразів фундаментальним завданням є представлення синтаксичного дерева виразу (Abstract Syntax Tree, AST).

Традиційний об'єктно-орієнтований підхід вимагав створення базового абстрактного класу `AstNode` з віртуальним методом `eval()` та похідних класів `NumberNode`, `AddNode`, `MultiplyNode`. Це змушувало виділяти кожен вузол дерева у динамічній купі через `std::unique_ptr<AstNode>` та здійснювати переходи за покажчиками vtable, що катастрофічно знижувало локальність кешу процесора.

Використання `std::variant` дозволяє виразити вузли дерева як тип-суму значення та вузлів бінарних операцій з індирекцією через `std::unique_ptr`.

### Порівняльний аналіз архітектури AST: ООП Visitor проти std::variant

При використанні класичного ООП-патерну Visitor створення нового проходу по дереву (наприклад, оптимізації, генерації коду чи форматування) вимагає додавання віртуального методу в базовий клас або створення нового класу-відвідувача, який повинен бути прописаний у всіх похідних вузлах. Це створює жорстку зв'язаність коду.

Натомість підхід на основі `std::variant` відокремлює структуру даних (вузли AST) від алгоритмів їх обробки (функцій-відвідувачів). Новий прохід по дереву додається як звичайна вільна функція із застосуванням `std::visit`, не вимагаючи внесення жодних змін у визначення самих типів вузлів.

### Механіка згортання констант (Constant Folding)

Згортання констант є однією з ключових оптимізацій у компіляторах. Під час аналізу AST-дерева оптимізаційний прохід знаходить вузли бінарних або унарних операцій, обидва операнди яких є відомими літеральними значеннями на етапі компіляції чи оптимізації, і замінює цілий піддерево-вузол єдиним обчисленим літералом.

У реалізації нижче метод `fold_constants` рекурсивно обходить дерево за допомогою `std::visit`. Завдяки `std::holds_alternative` функція перевіряє, чи стали обидва дочірні вузли літералами після рекурсивного проходу. Якщо так, замість збереження вузлів додавання чи множення обчислюється їхня сума чи добуток, а унікальний вказівник на вузол замінюється простим значенням `Literal`.

```cpp
#include <variant>
#include <memory>
#include <iostream>
#include <string>
#include <cmath>

// Структури вузлів синтаксичного дерева
struct Literal {
    double value;
};

struct Add;
struct Multiply;
struct Negate;

// Тип-сума для представлення будь-якого вузла AST
using ExprNode = std::variant<
    Literal,
    std::unique_ptr<Add>,
    std::unique_ptr<Multiply>,
    std::unique_ptr<Negate>
>;

struct Add {
    ExprNode left;
    ExprNode right;
};

struct Multiply {
    ExprNode left;
    ExprNode right;
};

struct Negate {
    ExprNode child;
};

// Ідіома Overloaded для патерн-матчингу
template <typename... Ts>
struct overloaded : Ts... {
    using Ts::operator()...;
};

template <typename... Ts>
overloaded(Ts...) -> overloaded<Ts...>;

// Обчислювач значення AST-дерева через std::visit
double evaluate(const ExprNode& expr) {
    return std::visit(overloaded{
        [](const Literal& num) -> double {
            return num.value;
        },
        [](const std::unique_ptr<Add>& bin) -> double {
            return evaluate(bin->left) + evaluate(bin->right);
        },
        [](const std::unique_ptr<Multiply>& bin) -> double {
            return evaluate(bin->left) * evaluate(bin->right);
        },
        [](const std::unique_ptr<Negate>& un) -> double {
            return -evaluate(un->child);
        }
    }, expr);
}

// Оптимізаційний прохід: Згортання констант (Constant Folding)
ExprNode fold_constants(ExprNode expr) {
    return std::visit(overloaded{
        [](Literal num) -> ExprNode {
            return num;
        },
        [](std::unique_ptr<Add>& bin) -> ExprNode {
            bin->left = fold_constants(std::move(bin->left));
            bin->right = fold_constants(std::move(bin->right));
            
            // Якщо обидва операнди є літералами — обчислюємо їх під час оптимізації!
            if (std::holds_alternative<Literal>(bin->left) && 
                std::holds_alternative<Literal>(bin->right)) {
                double l_val = std::get<Literal>(bin->left).value;
                double r_val = std::get<Literal>(bin->right).value;
                return Literal{l_val + r_val};
            }
            return std::move(bin);
        },
        [](std::unique_ptr<Multiply>& bin) -> ExprNode {
            bin->left = fold_constants(std::move(bin->left));
            bin->right = fold_constants(std::move(bin->right));
            
            if (std::holds_alternative<Literal>(bin->left) && 
                std::holds_alternative<Literal>(bin->right)) {
                double l_val = std::get<Literal>(bin->left).value;
                double r_val = std::get<Literal>(bin->right).value;
                return Literal{l_val * r_val};
            }
            return std::move(bin);
        },
        [](std::unique_ptr<Negate>& un) -> ExprNode {
            un->child = fold_constants(std::move(un->child));
            if (std::holds_alternative<Literal>(un->child)) {
                return Literal{-std::get<Literal>(un->child).value};
            }
            return std::move(un);
        }
    }, expr);
}

int main() {
    // Побудова виразу: (5 + 3) * -2
    ExprNode expr = std::make_unique<Multiply>(Multiply{
        std::make_unique<Add>(Add{ Literal{5.0}, Literal{3.0} }),
        std::make_unique<Negate>(Negate{ Literal{2.0} })
    });

    std::cout << "Результат обчислення AST: " << evaluate(expr) << "\n"; // Друкує -16

    // Виконання оптимізації згортання констант
    ExprNode folded = fold_constants(std::move(expr));

    if (std::holds_alternative<Literal>(folded)) {
        std::cout << "Дерево повністю згорнуто у єдиний літерал: " 
                  << std::get<Literal>(folded).value << "\n";
    }
}
```

---

## Проєкт 2: Автомат станів мережевого протоколу (Network Protocol FSM)

Другим практичним застосуванням `std::variant` є побудова автоматів скінченних станів (Finite State Machine, FSM) для мережевих з'єднань, обробки транспортних карт або протоколів аутентифікації.

Автомат станів складається з двох типів-сум:
- `State`: список усіх можливих станів системи (`DisconnectedState`, `ConnectingState`, `ConnectedState`, `ErrorState`).
- `Event`: список усіх подій, що можуть виникнути у системі (`ConnectEvent`, `DisconnectEvent`, `DataReceivedEvent`, `TimeoutEvent`).

### Переваги використання мульти-диспетчеризації у FSM

Традиційні підходи до побудови FSM вимагали створення двовимірних масивів покажчиків на функції або вкладених операторів `switch(state) { switch(event) { ... } }`. Такий код є важким для підтримки: додавання нового стану чи події змушує ручно перевіряти десятки гілок оператора `switch`.

Використання двоаргументного виклику `std::visit(transition_table, current_state, incoming_event)` дозволяє виразити таблицю переходів через перевантажений об'єкт `TransitionHandler`. Якщо певна комбінація стану та події не реалізована окремо, шаблонний оператор `operator()` автоматично перехоплює непідтримувані переходи (fallback rule), гарантуючи стабільність програми.

### Реалізація FSM мережевого сокета

```cpp
#include <variant>
#include <string>
#include <iostream>

// Опис станів системи
struct DisconnectedState {};

struct ConnectingState {
    std::string endpoint_address;
    int attempt_count;
};

struct ConnectedState {
    uint32_t session_id;
    size_t bytes_transferred;
};

struct ErrorState {
    std::string error_message;
};

using State = std::variant<DisconnectedState, ConnectingState, ConnectedState, ErrorState>;

// Опис подій системи
struct ConnectEvent {
    std::string address;
};

struct ConnectedSuccessEvent {
    uint32_t session_id;
};

struct DataPacketEvent {
    size_t packet_size;
};

struct ErrorOccurredEvent {
    std::string message;
};

using Event = std::variant<ConnectEvent, ConnectedSuccessEvent, DataPacketEvent, ErrorOccurredEvent>;

// Двовимірний відвідувач для реакції на пару (State, Event)
struct TransitionHandler {

    // 1. З DisconnectedState + ConnectEvent -> ConnectingState
    State operator()(DisconnectedState, const ConnectEvent& evt) const {
        std::cout << "[FSM] Спроба підключення до: " << evt.address << "\n";
        return ConnectingState{evt.address, 1};
    }

    // 2. З ConnectingState + ConnectedSuccessEvent -> ConnectedState
    State operator()(const ConnectingState& st, const ConnectedSuccessEvent& evt) const {
        std::cout << "[FSM] Успішно підключено до " << st.endpoint_address 
                  << ", session_id: " << evt.session_id << "\n";
        return ConnectedState{evt.session_id, 0};
    }

    // 3. З ConnectedState + DataPacketEvent -> ConnectedState (оновлення перерахованих байтів)
    State operator()(ConnectedState st, const DataPacketEvent& evt) const {
        st.bytes_transferred += evt.packet_size;
        std::cout << "[FSM] Отримано пакет " << evt.packet_size 
                  << " байт. Всього передано: " << st.bytes_transferred << "\n";
        return st;
    }

    // 4. Будь-який стан + ErrorOccurredEvent -> ErrorState
    template <typename CurrentState>
    State operator()(const CurrentState&, const ErrorOccurredEvent& evt) const {
        std::cout << "[FSM] Критична помилка: " << evt.message << "\n";
        return ErrorState{evt.message};
    }

    // 5. Непідтримувані переходи (fallback rule)
    template <typename CurrentState, typename IncomingEvent>
    State operator()(const CurrentState& st, const IncomingEvent&) const {
        std::cout << "[FSM] Ігнорування невалідної події для даного стану.\n";
        return st;
    }
};

class NetworkSocketFSM {
    State current_state_;

public:
    NetworkSocketFSM() : current_state_(DisconnectedState{}) {}

    void dispatch(const Event& event) {
        // Статична двовимірна диспетчеризація пари (current_state_, event)
        current_state_ = std::visit(TransitionHandler{}, current_state_, event);
    }

    void print_status() const {
        std::visit(overloaded{
            [](DisconnectedState) { std::cout << "Статус: Відключено\n"; },
            [](const ConnectingState& st) { std::cout << "Статус: В процесі підключення до " << st.endpoint_address << "\n"; },
            [](const ConnectedState& st) { std::cout << "Статус: Підключено (сесія " << st.session_id << ")\n"; },
            [](const ErrorState& st) { std::cout << "Статус: Помилка (" << st.error_message << ")\n"; }
        }, current_state_);
    }
};

int main() {
    NetworkSocketFSM fsm;
    fsm.print_status();

    // Симуляція життєвого циклу мережевого з'єднання
    fsm.dispatch(ConnectEvent{"192.168.1.100:8080"});
    fsm.print_status();

    fsm.dispatch(ConnectedSuccessEvent{42});
    fsm.print_status();

    fsm.dispatch(DataPacketEvent{512});
    fsm.dispatch(DataPacketEvent{1024});
    fsm.print_status();

    fsm.dispatch(ErrorOccurredEvent{"Мережевий таймаут"});
    fsm.print_status();
}
```

---

## Глибокий інженерний розбір пам'яті та кеш-ефективності AST-вузлів при масштабуванні

При спроектуванні реальних компіляторів або обробників виразів промислового масштабу (наприклад, у двигунах баз даних для виконання SQL-запитів) структура AST-дерева на основі `std::variant` надає суттєві переваги над традиційним ООП.

По-перше, листові вузли дерева (`Literal`) розміщуються безпосередньо у варіанті без створення динамічного вказівника `std::unique_ptr`. Для виразів із великою кількістю констант та простих змінних це позбавляє програму від виділення пам'яті в купі на кожен листок дерева.

По-друге, обхід AST-дерева через `std::visit` не викликає непотрібних розіменувань вказівників vtable. Якщо в класичному поліморфізмі кожен виклик `eval()` виконує додатковий інструкційний стрибок через таблицю віртуальних методів, то у `std::visit` компілятор будує прямий інлайновий виклик або швидкий `switch` за індексом.

Нарешті, використання алокаторів плоских масивів (Arena Allocation / Monolithic Memory Pool) у поєднанні з `std::variant` дозволяє розмістити всі вузли синтаксичного дерева в єдиному суцільному буфері пам'яті. Це забезпечує ідеальну кеш-локальність під час аналізу та обчислення виразів будь-якої складності.

---

## Зауваження щодо розміру комбінаторного коду та бінарного роздування (Code Bloat)

Під час використання мульти-диспетчеризації `std::visit(vis, v1, v2, v3)` компілятор будує комбінаторну таблицю викликів. Якщо передати K варіантів, кожен з яких має N альтернатив, компілятор створить N у степені K можливих інстанціацій оператора виклику.

Для мінімізації бінарного роздування у промислових системах рекомендується застосовувати наступні інженерні прийоми:
1. **Декомпозиція відвідувачів:** Розбивати мульти-відвідування трьох і більше варіантів на послідовний ланцюжок одноаргументних викликів `std::visit`.
2. **Явне зведення типів повернення у C++23:** Використовувати `std::visit<R>` для уникнення генерації дубльованих шаблонів функцій із різними виведеними типами повернення.
3. **Винесення спільного коду з лямбда-функцій:** Уникати великих обсягів коду всередині відвідувачів; лямбда-функція повинна лише викликати зовнішні не-шаблонні функції.
