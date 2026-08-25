# ⚙️ Практика побудови множин перевантажень та інтерфейсів через using

Ключове слово `using` у сучасному C++ є потужним інструментом метапрограмування, композиції типів, формування статичного поліморфізму та тонкого керування відкритими контрактами класів. У цій практичній роботі реалізовано п'ять виробничих архітектурних рішень: універсальний функціональний відвідувач варіантів (Overload Pattern) для диспетчеризації `std::visit`, скінченний автомат переходів станів (State Machine), композицію міксинів (Mixin Composition) з усуненням колізій імен, конвеєр обробки проміжних шарів (Middleware Pipeline) та вибірковий адаптер низькорівневих ресурсів на базі приватного успадкування. Також наведено детальний аналіз генерації машинного коду, взаємодії з концептами C++20 та порівняння з новітнім механізмом явного об'єктного параметра (Deducing this) у C++23.

---

## 1. Патерн Overload для std::variant та std::visit

Тип `std::variant` (алгебраїчний тип суми, або типізоване об'єднання) є стандартом сучасного C++ для представлення значень, які в кожен момент часу можуть належати до одного з кількох фіксованих типів. На відміну від класичного динамічного поліморфізму на основі віртуальних функцій, `std::variant` зберігає об'єкти безпосередньо у виділеному стековому буфері без динамічного виділення пам'яті в купі (heap allocation) та без покажчиків на таблиці віртуальних методів (vtable).

Проте для обробки значення у `std::variant` функція `std::visit` вимагає передати функціональний об'єкт (відвідувач, англ. *visitor*), який повинен мати перевантажений `operator()` для кожного можливого типу, що зберігається у варіанті.

### Архітектурна проблема монолітного відвідувача

Якщо писати окремий клас відвідувача вручну, доводиться створювати окрему структуру з кількома методами `operator()`:

```cpp
struct ManualVisitor {
    void operator()(const ConnectionEvent& e) { /* ... */ }
    void operator()(const DataPacketEvent& e) { /* ... */ }
    void operator()(const TimeoutEvent& e)    { /* ... */ }
};
```

Такий підхід розриває контекст коду: логіка обробки подій опиняється далеко від точки виклику, а локальні змінні доводиться вручну захоплювати в поля структури `ManualVisitor` через конструктор. Це призводить до розростання допоміжних структур і ускладнює читання програми.

Набагато зручніше створювати анонімні лямбда-функції безпосередньо на місці виклику `std::visit`. Проте кожна лямбда є окремим унікальним безіменним типом, і виникає завдання: як скомпонувати кілька незалежних лямбд в один функціональний об'єкт з єдиним набором перевантажень?

### Реалізація патерну Overload

Завдяки варіативному успадкуванню та пакетним using-оголошенням C++17 це завдання вирішується двома рядками коду:

```cpp
#include <iostream>
#include <variant>
#include <string>
#include <string_view>
#include <vector>
#include <cstdint>
#include <type_traits>

// 1. Структура Overload успадковує всі передані функціональні об'єкти (лямбди)
template <typename... Ts>
struct Overload : Ts... {
    // Втягуємо всі operator() з кожного базового типу в область видимості Overload:
    using Ts::operator()...;
};

// 2. Deduction Guide для автоматичного виведення типів аргументів шаблону (CTAD):
template <typename... Ts>
Overload(Ts...) -> Overload<Ts...>;

// Допоміжний трейт для статичної перевірки вичерпності (Exhaustiveness Check)
template <typename T>
struct always_false : std::false_type {};

// Приклад предметної області: події мережевого стека
struct ConnectionEvent {
    std::string peer_ip;
    uint16_t port;
};

struct DataPacketEvent {
    std::vector<uint8_t> payload;
    bool is_encrypted;
};

struct HeartbeatEvent {
    uint64_t sequence_number;
};

struct DisconnectEvent {
    std::string reason;
};

// Тип суми для всіх можливих мережевих повідомлень:
using NetworkMessage = std::variant<ConnectionEvent, DataPacketEvent, HeartbeatEvent, DisconnectEvent>;

// Функція диспетчеризації повідомлень
void handle_network_message(const NetworkMessage& message) {
    std::visit(Overload{
        [](const ConnectionEvent& ev) {
            std::cout << "[З'єднання] Вузол " << ev.peer_ip << ":" << ev.port << " підключено.\n";
        },
        [](const DataPacketEvent& ev) {
            std::cout << "[Дані] Отримано пакет на " << ev.payload.size() 
                      << " байтів (шифрування: " << (ev.is_encrypted ? "так" : "ні") << ").\n";
        },
        [](const HeartbeatEvent& ev) {
            std::cout << "[Heartbeat] Пульс #" << ev.sequence_number << " підтверджено.\n";
        },
        [](const DisconnectEvent& ev) {
            std::cout << "[Відключення] Причина: " << ev.reason << '\n';
        }
    }, message);
}
```

### Покроковий розбір механізму компіляції

Розглянемо детально, що відбувається під час компіляції виклику `std::visit`:

1. **Генерація типів замикань**: Компілятор створює чотири окремі анонімні класи-замикання (по одному для кожної лямбди), кожен із яких містить константний метод `operator()` із відповідним типом параметра (`const ConnectionEvent&`, `const DataPacketEvent&` тощо).
2. **Формування типу Overload**: Інстанціюється тип `Overload<Lambda1, Lambda2, Lambda3, Lambda4>`, який стає прямим спадкоємцем усіх чотирьох класів.
3. **Роль `using Ts::operator()...;`**: Якби цього рядка не було, компілятор побачив би, що в класі `Overload` є чотири різні методи з однаковою назвою `operator()` у чотирьох незв'язаних базових класах. За правилами пошуку імен виклик `visitor(event)` завершився б фатальною помилкою неоднозначності (Ambiguous Lookup), оскільки пошук імен не зміг би обрати жоден базовий клас. Рядок `using Ts::operator()...;` явно втягує всі чотири оператори в єдину область видимості похідного класу `Overload`.
4. **Розв'язання перевантажень (Overload Resolution)**: Тепер у класі `Overload` сформовано єдину множину з чотирьох перевантажень. Компілятор безпомилково зіставляє тип фактичного значення всередині `std::variant` із точно відповідною лямбдою.
5. **Нульова вартість виконання (Zero-Overhead)**: Усі виклики повністю інлайняться оптимізатором. У машинному коді формується пряма таблиця переходів за індексом типу у варіанті або коротка послідовність порівнянь без жодного виділення пам'яті та без непрямих викликів через покажчики на функції.

### Гарантія вичерпності та пастка static_assert(false)

Якщо розробник додає новий тип у `std::variant` (наприклад, `struct ErrorEvent`), але забуває додати відповідну лямбду в `Overload`, компілятор зупиняє збирання програми з повідомленням про те, що для `ErrorEvent` немає відповідного перевантаження.

Якщо ж у відвідувач додається універсальна лямбда-пастка `[](const auto& unhandled) { ... }`, компілятор припиняє перевіряти вичерпність. Щоб контролювати типи на етапі компіляції, використовують трейт `always_false`:

```cpp
[](const auto& unhandled) {
    using T = std::decay_t<decltype(unhandled)>;
    static_assert(always_false<T>::value, "Необроблений тип події в std::visit!");
}
```

Прямий запис `static_assert(false, ...)` не працює, оскільки компілятор обчислює його на першій фазі розбору шаблону ще до інстанціювання. Використання залежного типу `always_false<T>` відкладає перевірку до моменту, коли в гілку потрапить невідомий тип.

---

## 2. Реалізація скінченного автомата станів (State Machine) з Overload

Поєднання `std::variant` та `Overload` дозволяє створювати елегантні скінченні автомати, де поточний стан і вхідна подія обробляються через двоаргументний `std::visit`.

### Архітектура таблиці переходів

```cpp
#include <iostream>
#include <variant>
#include <string>

// Стани з'єднання:
struct DisconnectedState {};
struct ConnectingState { int retry_count{0}; };
struct ConnectedState { std::string session_id; };

using State = std::variant<DisconnectedState, ConnectingState, ConnectedState>;

// Вхідні події автомата:
struct ConnectCommand { std::string target_host; };
struct HandshakeOk { std::string session_id; };
struct NetworkError { std::string message; };
struct DisconnectCommand {};

using Event = std::variant<ConnectCommand, HandshakeOk, NetworkError, DisconnectCommand>;

// Функція переходу між станами:
State on_event(State current_state, Event event) {
    return std::visit(Overload{
        // 1. З Disconnected реагуємо на команду підключення:
        [](DisconnectedState, ConnectCommand cmd) -> State {
            std::cout << "Перехід: Disconnected -> Connecting до " << cmd.target_host << '\n';
            return ConnectingState{1};
        },
        // 2. З Connecting при успішному рукостисканні переходимо в Connected:
        [](ConnectingState, HandshakeOk ok) -> State {
            std::cout << "Перехід: Connecting -> Connected (ID: " << ok.session_id << ")\n";
            return ConnectedState{ok.session_id};
        },
        // 3. З Connecting при помилці повертаємося в Disconnected:
        [](ConnectingState st, NetworkError err) -> State {
            std::cout << "Помилка зв'язку (" << err.message << "), спроба #" << st.retry_count << '\n';
            return DisconnectedState{};
        },
        // 4. З Connected на команду відключення переходимо в Disconnected:
        [](ConnectedState, DisconnectCommand) -> State {
            std::cout << "Перехід: Connected -> Disconnected\n";
            return DisconnectedState{};
        },
        // 5. Усі інші комбінації стану та події ігноруються (стан не змінюється):
        [](auto state, auto) -> State {
            std::cout << "Ігнорування недоречної події для поточного стану.\n";
            return state;
        }
    }, current_state, event);
}

int main() {
    State current = DisconnectedState{};

    current = on_event(current, ConnectCommand{"api.service.internal"});
    current = on_event(current, HandshakeOk{"sess-9988"});
    current = on_event(current, ConnectCommand{"інший_сервер"}); // ігнорується
    current = on_event(current, DisconnectCommand{});

    return 0;
}
```

Коли у `std::visit` передається два об'єкти варіантів (`current_state` та `event`), компілятор обчислює декартовий добуток усіх можливих пар типів (3 стани × 4 події = 12 комбінацій) і диспетчеризує виклик через відповідну лямбду в `Overload`. Завдяки `using Ts::operator()...;` усі 5 перевантажень зливаються в один відвідувач, що робить код таблиці переходів компактним і структурованим.

---

## 3. Композиція міксинів (Mixin Composition) з усуненням колізій

Міксини (англ. *mixins*) — це шаблонні класи, які додають до цільового типу ортогональні функціональні можливості (наприклад, підтримку серіалізації в різні формати, логування, валідацію чи порівняння) без побудови монолітних ієрархій успадкування.

### Проблема затуляння при множинному успадкуванні міксинів

Коли різні міксини надають методи з однаковою назвою, але для різних цільових типів (наприклад, метод `export_to` для текстового потоку, бінарного буфера та рядка), пряме успадкування стикається з проблемою затуляння або неоднозначності:

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <span>
#include <cstdint>

// Міксин 1: експорт у потік std::ostream через CRTP
template <typename Derived>
struct StreamExportable {
    void export_to(std::ostream& os) const {
        static_cast<const Derived*>(this)->format_stream(os);
    }
};

// Міксин 2: експорт у бінарний вектор байтів
template <typename Derived>
struct BinaryExportable {
    void export_to(std::vector<uint8_t>& buffer) const {
        static_cast<const Derived*>(this)->format_binary(buffer);
    }
};

// Міксин 3: експорт у рядок для швидкого логування
template <typename Derived>
struct TextExportable {
    void export_to(std::string& output) const {
        std::ostringstream ss;
        static_cast<const Derived*>(this)->format_stream(ss);
        output = ss.str();
    }
};

// Цільовий клас доменної сутності
class TelemetryFrame : public StreamExportable<TelemetryFrame>,
                       public BinaryExportable<TelemetryFrame>,
                       public TextExportable<TelemetryFrame> {
private:
    uint64_t timestamp_ns_;
    double temperature_;
    double pressure_;

public:
    TelemetryFrame(uint64_t ts, double temp, double press)
        : timestamp_ns_(ts), temperature_(temp), pressure_(press) {}

    // ОБ'ЄДНАННЯ ПЕРЕВАНТАЖЕНЬ: втягуємо всі export_to з усіх трьох міксинів:
    using StreamExportable<TelemetryFrame>::export_to;
    using BinaryExportable<TelemetryFrame>::export_to;
    using TextExportable<TelemetryFrame>::export_to;

    // Внутрішні методи реалізації, які викликаються міксинами через CRTP:
    void format_stream(std::ostream& os) const {
        os << "[Telemetry] ts=" << timestamp_ns_ 
           << " temp=" << temperature_ << "C press=" << pressure_ << "hPa";
    }

    void format_binary(std::vector<uint8_t>& buffer) const {
        auto append_pod = [&buffer](const auto& val) {
            const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&val);
            buffer.insert(buffer.end(), ptr, ptr + sizeof(val));
        };
        append_pod(timestamp_ns_);
        append_pod(temperature_);
        append_pod(pressure_);
    }
};

int main() {
    TelemetryFrame frame{1718000000000ULL, 23.5, 1013.25};

    // 1. Експорт у консоль через StreamExportable
    std::cout << "1. Потік: ";
    frame.export_to(std::cout);
    std::cout << '\n';

    // 2. Експорт у бінарний вектор через BinaryExportable
    std::vector<uint8_t> bin_data;
    frame.export_to(bin_data);
    std::cout << "2. Бінарний буфер: " << bin_data.size() << " байтів.\n";

    // 3. Експорт у рядок через TextExportable
    std::string text_str;
    frame.export_to(text_str);
    std::cout << "3. Рядок: " << text_str << '\n';

    return 0;
}
```

### Чому без using код не компілюється

Якщо закоментувати або прибрати три директиви `using ...::export_to;`, компілятор під час аналізу виклику `frame.export_to(std::cout)` запустить некваліфікований пошук імені. Він перегляне батьківські класи й виявить, що ім'я `export_to` наявне в трьох незалежних гілках базових класів одночасно. 

Компілятор не має права віддати перевагу жодному з них на етапі пошуку імені. Пошук завершується помилкою `error: member 'export_to' found in multiple base classes of different types (ambiguous lookup)`. 

Директиви `using` явно переносять усі три сигнатури `export_to` безпосередньо в область видимості класу `TelemetryFrame`. Тепер вони вважаються оголошеними локально всередині класу `TelemetryFrame`, об'єднуючись у відкриту множину перевантажень. Компілятор безпомилково викликає відповідний метод на основі типу переданого параметра (`std::ostream&`, `std::vector<uint8_t>&` чи `std::string&`).

---

## 4. Конвеєр обробки проміжних шарів (Middleware Pipeline)

Ще один потужний патерн — побудова конвеєрів обробки запитів, де кожен проміжний обробник (middleware) спеціалізується на певному типі корисного навантаження (JSON, Protobuf, RawBytes).

### Архітектура конвеєра з об'єднанням через using

```cpp
#include <iostream>
#include <string>
#include <span>
#include <vector>

struct JsonPayload { std::string json_text; };
struct BinaryPayload { std::vector<uint8_t> raw_bytes; };
struct TextPayload { std::string plain_text; };

struct JsonHandler {
    void handle_message(const JsonPayload& p) {
        std::cout << "Обробка JSON: " << p.json_text << '\n';
    }
};

struct BinaryHandler {
    void handle_message(const BinaryPayload& p) {
        std::cout << "Обробка Binary: " << p.raw_bytes.size() << " байтів\n";
    }
};

struct TextHandler {
    void handle_message(const TextPayload& p) {
        std::cout << "Обробка PlainText: " << p.plain_text << '\n';
    }
};

// Конвеєр об'єднує всі обробники в єдиний ієрархічний диспетчер:
template <typename... Handlers>
struct MessagePipeline : Handlers... {
    using Handlers::handle_message...; // C++17 варіативне using-оголошення!
};

int main() {
    MessagePipeline<JsonHandler, BinaryHandler, TextHandler> pipeline;

    pipeline.handle_message(JsonPayload{"{\"user_id\": 42}"});
    pipeline.handle_message(BinaryPayload{{0x01, 0x02, 0x03}});
    pipeline.handle_message(TextPayload{"Звичайне повідомлення журналу"});

    return 0;
}
```

Усі методи `handle_message` із трьох незалежних класів обробників зливаються в один клас `MessagePipeline` без написання жодної проміжної функції. Компілятор на етапі компіляції визначає точний маршрут виклику для кожного типу повідомлення.

---

## 5. Вибірковий адаптер низькорівневих ресурсів через приватне успадкування

Приватне успадкування (`class Derived : private Base`) є фундаментальним архітектурним патерном мови C++, коли потрібно виразити відношення «реалізовано за допомогою» (*implemented-in-terms-of*), а не «є підтипом» (*is-a*). 

Приватне успадкування використовують у трьох головних сценаріях:
1. Похідний клас повинен перевизначити захищені віртуальні функції базового класу або отримати доступ до його захищених полів.
2. Необхідно задіяти оптимізацію порожнього базового класу (Empty Base Class Optimization / EBCO), яка гарантує нульовий розмір базового підкласу в пам'яті.
3. Необхідно запобігти випадковому неявному приведенню покажчика на похідний клас до покажчика на базовий клас (захист від зрізання об'єктів / *object slicing*).

### Проблема монотонного ручного делегування

Якщо клас використовує композицію через поле (`RawHandle handle_;`), для відкриття потрібних клієнтам операцій доводиться писати проміжні функції-делегати:

```cpp
class SafeWrapper {
    RawResource res_;
public:
    void safe_action() { res_.safe_action(); }
    int get_status() const { return res_.get_status(); }
};
```

Якщо базовий клас має десятки корисних методів із різними специфікаторами `const`, `noexcept` або перевантаженнями для rvalue-посилань, написання таких делегатів вимагає сотень рядків монотонного коду. Будь-яке додавання нового перевантаження в базовий клас змушує вручну оновлювати обгортку.

### Використання using для вибіркового переекспорту інтерфейсу

За допомогою using-оголошень у публічній секції похідного класу відкриття потрібних методів здійснюється декларативно в один рядок:

```cpp
#include <iostream>
#include <span>
#include <vector>
#include <cstdint>
#include <stdexcept>

// Низькорівневий драйвер апаратного каналу зв'язку
class HardwareChannelBase {
public:
    void open_channel(uint32_t channel_id, uint32_t baud_rate) {
        std::cout << "Hardware: відкрито канал #" << channel_id << " на швидкості " << baud_rate << " бод.\n";
        is_active_ = true;
    }

    void close_channel() noexcept {
        std::cout << "Hardware: канал закрито.\n";
        is_active_ = false;
    }

    bool is_active() const noexcept {
        return is_active_;
    }

    // Небезпечний низькорівневий метод прямого запису в регістри:
    void direct_register_write(uint32_t reg_offset, uint32_t raw_value) {
        std::cout << "Hardware: прямий запис у регістр 0x" << std::hex << reg_offset 
                  << " значення 0x" << raw_value << std::dec << '\n';
    }

    // Низькорівневе читання статусу з шини:
    uint32_t read_hardware_flags() const noexcept {
        return 0x00000001; // статус готовності
    }

protected:
    void raw_transmit_bytes(std::span<const uint8_t> data) {
        std::cout << "Hardware: передано " << data.size() << " байтів у фізичний канал.\n";
    }

private:
    bool is_active_{false};
};

// Високорівневий клієнтський драйвер для безпечної передачі пакетів
class SafePacketTransceiver : private HardwareChannelBase {
public:
    SafePacketTransceiver(uint32_t channel_id, uint32_t baud_rate) {
        open_channel(channel_id, baud_rate);
    }

    ~SafePacketTransceiver() {
        if (is_active()) {
            close_channel();
        }
    }

    // 1. Відкриваємо публічно безпечні методи перевірки та закриття:
    using HardwareChannelBase::is_active;
    using HardwareChannelBase::close_channel;

    // 2. Реалізуємо високорівневий безпечний метод відправлення з валідацією:
    void send_packet(std::span<const uint8_t> packet) {
        if (!is_active()) {
            throw std::runtime_error("Канал не активний для відправлення!");
        }
        if (packet.empty() || packet.size() > 1024) {
            throw std::invalid_argument("Некоректний розмір пакета (1..1024 байтів)!");
        }
        // Викликаємо protected-метод базового класу:
        raw_transmit_bytes(packet);
    }

    // Небезпечні методи direct_register_write та read_hardware_flags 
    // залишаються приватними й повністю недоступними для клієнтів SafePacketTransceiver!
};

int main() {
    SafePacketTransceiver transceiver(1, 115200);

    if (transceiver.is_active()) {
        std::cout << "Трансивер готовий до роботи.\n";
    }

    std::vector<uint8_t> payload = {0x01, 0x02, 0x03, 0x04};
    transceiver.send_packet(payload);

    // Спроба виклику низькорівневих операцій заблокована компілятором:
    // transceiver.direct_register_write(0x10, 0xFF); 
    // ^ Помилка: 'direct_register_write' is private within this context

    // transceiver.open_channel(2, 9600);
    // ^ Помилка: 'open_channel' is private within this context

    return 0;
}
```

### Порівняльний аналіз переваг підходу

1. **Автоматична підтримка перевантажень**: Якщо базовий клас `HardwareChannelBase` додасть нові перевантаження методу `is_active()` (наприклад, з перевіркою прапорців помилок `is_active(CheckFlags flags)`), рядок `using HardwareChannelBase::is_active;` автоматично експортує всі нові перевантаження без необхідності вносити зміни в код похідного класу.
2. **Абсолютна нульова вартість (Zero Runtime Cost)**: Using-оголошення не генерує жодних додаткових функцій-пересилачів, інструкцій виклику `call` чи переходів `jmp`. Це суто інструкція для таблиці прав доступу компілятора.
3. **Надійне збереження інваріантів**: Клієнтський код позбавлений можливості випадково пошкодити внутрішній стан обладнання викликом `direct_register_write`, оскільки цей метод залишається невидимим за межами класу.

---

## 6. Аналіз продуктивності та оптимізації машинного коду

Щоб переконатися у відсутності накладних витрат під час виконання, розглянемо згенерований компілятором x86-64 асемблерний код (GCC 13 `-O3`) для виклику `std::visit` з об'єктом `Overload`.

Традиційний динамічний поліморфізм через `std::unique_ptr<BaseEvent>` породжує таку послідовність інструкцій:
1. Завантаження покажчика на таблицю віртуальних функцій з об'єкта: `mov rax, [rdi]`.
2. Завантаження адреси методу зі зміщенням: `mov rax, [rax + 16]`.
3. Непрямий виклик функції: `call rax`.

Непрямий виклик `call rax` створює навантаження на блок передбачення переходів процесора (Branch Target Buffer) і може спричинити промах конвеєра (pipeline stall), якщо типи подій чергуються хаотично. Крім того, об'єкти в купі розкидані по різних ділянках пам'яті, що збільшує кількість промахів кешу даних L1/L2.

На противагу цьому, диспетчеризація `std::variant` за допомогою `Overload`:
1. Читає цілочисельний дискримінатор типу (індекс активного елемента у варіанті): `mov eax, [rdi + offset]`.
2. Виконує прямий стрибок за статичною таблицею переходів або коротку серію інлайнових інструкцій: `jmp [table + rax*8]`.
3. Оскільки всі тіла лямбд є короткими, оптимізатор повністю інлайнить їхній код безпосередньо в точки переходу, усуваючи будь-які виклики підпрограм.

Усі об'єкти варіантів зберігаються в єдиному локальному стековому буфері, що гарантує 100% потрапляння в найшвидший кеш L1 процесора.

---

## 7. Взаємодія з концептами C++20 (Concepts & Constraints)

У C++20 патерн `Overload` отримує додаткову гнучкість завдяки поєднанню з концептами. Якщо ми хочемо додати у відвідувач обробку цілих категорій типів (наприклад, усіх числових типів, усіх контейнерів або всіх типів, що підтримують логування), ми можемо обмежити лямбди за допомогою `requires`:

```cpp
#include <concepts>
#include <iostream>
#include <variant>
#include <vector>
#include <string>

template <typename... Ts>
struct Overload : Ts... {
    using Ts::operator()...;
};
template <typename... Ts>
Overload(Ts...) -> Overload<Ts...>;

using DynamicValue = std::variant<int, double, std::string, std::vector<int>>;

void inspect_value(const DynamicValue& val) {
    std::visit(Overload{
        // Спеціалізована обробка для рядків:
        [](const std::string& s) {
            std::cout << "Рядок: \"" << s << "\", довжина: " << s.size() << '\n';
        },
        // Концепт для всіх числових типів (int, double тощо):
        []<std::floating_point T>(T num) {
            std::cout << "Дробове число: " << num << '\n';
        },
        []<std::integral T>(T num) {
            std::cout << "Ціле число: " << num << '\n';
        },
        // Концепт для контейнерів, що підтримують ітерацію:
        []<typename T>(const std::vector<T>& vec) {
            std::cout << "Вектор розміром: " << vec.size() << '\n';
        }
    }, val);
}
```

Завдяки правилам розв'язання перевантажень C++20 більш обмежені перевантаження (більш специфічні концепти) мають пріоритет над менш обмеженими, що дозволяє будувати ієрархічні статичні обробники без конфліктів затуляння.

---

## 8. C++23 Deducing This проти CRTP з using-оголошеннями

У стандарті C++23 з'явилася можливість явного вказування об'єктного параметра (англ. *Explicit Object Parameter*, або *Deducing this*). Раніше для створення міксинів доводилося застосовувати ідіому CRTP (Curiously Recurring Template Pattern), передаючи тип спадкоємця як шаблонний аргумент `struct Mixin<Derived>`.

У C++23 міксин можна написати значно простіше:

```cpp
struct ModernStreamExportable {
    // Явний об'єктний параметр замінює CRTP і static_cast:
    void export_to(this const auto& self, std::ostream& os) {
        self.format_stream(os);
    }
};

struct ModernBinaryExportable {
    void export_to(this const auto& self, std::vector<uint8_t>& buf) {
        self.format_binary(buf);
    }
};

// Цільовий клас у C++23:
struct ModernTelemetryFrame : public ModernStreamExportable,
                              public ModernBinaryExportable {
    // Using-оголошення залишаються НЕОБХІДНИМИ для об'єднання перевантажень!
    using ModernStreamExportable::export_to;
    using ModernBinaryExportable::export_to;

    void format_stream(std::ostream& os) const { os << "C++23 Telemetry"; }
    void format_binary(std::vector<uint8_t>& b) const { b.push_back(0xFF); }
};
```

Цей приклад наочно демонструє, що навіть із появою найновіших можливостей C++23 фундаментальні правила пошуку імен залишаються незмінними: без рядків `using ...::export_to;` виклик методу з кількох базових класів призведе до колізії пошуку імені. Ключове слово `using` залишається головним сполучним елементом компонентної архітектури мови.

---

## 9. Виробничі пастки та крайові випадки

Під час практичного застосування using-оголошень у великих проєктах слід уникати чотирьох класичних пасток:

### Пастка 1: Неоднозначність перетворень у лямбдах
Якщо в патерні `Overload` передати дві лямбди з числовими типами, між якими можливі неявні перетворення:
```cpp
auto visitor = Overload{
    [](int x) { std::cout << "int\n"; },
    [](double x) { std::cout << "double\n"; }
};
visitor(3.14f); // ✗ ПОМИЛКА: float однаково неявно перетворюється і на int, і на double!
```
Компілятор видасть помилку неоднозначності розв'язання перевантажень. Щоб уникнути цього, типи в лямбдах мають бути або точними, або використовувати явні шаблонні обмеження (concepts у C++20).

### Пастка 2: Залежні імена в шаблонних міксинах
Якщо міксин успадковує шаблонний базовий клас `Base<T>`, пошук імен не переглядає базовий клас на першій фазі трансляції шаблону. Спроба викликати метод базового класу без `this->` або без `using Base<T>::method;` призведе до помилки `identifier not found`. Використання `using` у тілі похідного шаблону є найбільш ідіоматичним способом вирішення цієї проблеми.

### Пастка 3: Віртуальні методи та приватне успадкування
Якщо базовий клас має відкритий віртуальний метод `virtual void tick()`, а клас успадковує його приватно й не оголошує `using Base::tick;`, метод залишається недоступним через об'єкт похідного класу `derived.tick()`. Проте якщо об'єкт передано в зовнішній код через базовий покажчик `Base*`, віртуальний виклик `base_ptr->tick()` виконається успішно, оскільки динамічний поліморфізм C++ перевіряє права доступу за статичним типом покажчика, а не за динамічним типом об'єкта.

### Пастка 4: Приховані друзі та ADL
Якщо базовий клас оголошує оператор через ідіому прихованого друга (`friend bool operator==(const Base&, const Base&)` всередині тіла класу), цей оператор не є членом класу. Спроба написати `using Base::operator==;` у похідному класі викличе помилку компіляції. Для підтримки порівняння похідний клас повинен або реалізувати власний оператор порівняння, або покладатися на C++20 `bool operator==(const Derived&) const = default;`.

---

## 10. Архітектурні рекомендації та діагностичні прапорці компілятора

Для підтримки чистоти та безпеки архітектури великих виробничих систем рекомендується вмикати діагностичні попередження компілятора, які виявляють ненавмисне затуляння:
- У GCC та Clang прапорець `-Woverloaded-virtual` повідомляє, якщо похідний клас оголошує метод, що затуляє віртуальний метод базового класу з іншою сигнатурою без явного `using Base::method;`.
- Прапорець `-Wshadow` виявляє затуляння локальних змінних та параметрів функцій зовнішніми оголошеннями.
- У MSVC прапорці `/w14263` та `/w14264` активують попередження про приховування віртуальних методів базового класу.

Загальний контрольний список архітектора:
1. **Завжди супроводжуйте перевизначення перевантаженого методу базового класу директивою `using Base::method;`**, якщо тільки вашою прямою метою не є свідоме приховування решти сигнатур базового класу. Це запобігає ненавмисному руйнуванню інтерфейсу предка та захищає від неявних некоректних приведень типів аргументів.
2. **Ніколи не розміщуйте using-директиви (`using namespace ...;`) у відкритих заголовних файлах** — це руйнує модульність і викликає колізії перевантажень у користувачів бібліотеки по всьому дереву включень.
3. **Уникайте дублювання функцій-делегатів**: якщо адаптер створюється через приватне успадкування, використовуйте публічні `using Base::method;` для вибіркового переекспорту методів із нульовими накладними витратами.
4. **Використовуйте `using` замість `typedef` у всьому новому коді**, що забезпечить однаковість стилю та можливість легкої трансформації псевдоніма у шаблонний синонім при подальшій еволюції системи.
