# ⚙️ Дослідження поліморфного руйнування та діагностика витоків

Цей практикум присвячено експериментальному дослідженню низькорівневих механізмів поліморфного руйнування в C++. Ми відтворимо діагностичні звіти AddressSanitizer і LeakSanitizer, проаналізуємо байтову розкладку пам'яті та зміщення покажчиків при множинному успадкуванні, дослідимо поведінку системних алокаторів при невідповідності розмірів вивільнення пам'яті та побудуємо безпечну архітектуру на основі статичного поліморфізму CRTP із захищеним деструктором.

## Лабораторія 1: Відтворення витоків ресурсів під AddressSanitizer

Перший експеримент демонструє, як невіртуальний деструктор у базовому класі призводить до мовчазного витоку динамічної пам'яті та системних ресурсів, і як сучасні інструменти динамічного аналізу фіксують цей дефект.

Розглянемо серверний компонент, який керує мережевими сесіями та виділяє динамічні буфери для обробки пакетів:

```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <cstring>

class BaseService {
public:
    void serve() { /* базовий цикл обробки */ }
    // Помилка: деструктор залишено невіртуальним за замовчуванням
    ~BaseService() = default;
};

class HeavyStreamingService : public BaseService {
    char* dynamic_payload{nullptr};
    std::size_t payload_size{0};
    std::vector<int> active_sessions;

public:
    HeavyStreamingService(std::size_t size)
        : payload_size(size), active_sessions(1000, 1) {
        dynamic_payload = new char[payload_size];
        std::memset(dynamic_payload, 0x55, payload_size);
        std::cout << "[+] HeavyStreamingService створено: " << payload_size << " байтів у купі\n";
    }

    ~HeavyStreamingService() {
        delete[] dynamic_payload;
        std::cout << "[-] HeavyStreamingService успішно зруйновано\n";
    }
};

int main() {
    std::cout << "=== Старт тесту: видалення через BaseService* ===\n";
    BaseService* service = new HeavyStreamingService(1024 * 1024); // 1 МБ
    
    // Поліморфне видалення через покажчик на базу
    delete service;
    
    std::cout << "=== Завершення main() ===\n";
    return 0;
}
```

### Механізм роботи AddressSanitizer і тіньової пам'яті

Щоб зрозуміти звіт санітайзера, розглянемо принцип його роботи. Інструмент AddressSanitizer (*ASan*) перехоплює всі виклики функцій виділення пам'яті (`malloc`, `operator new`) та вивільнення (`free`, `operator delete`). Для кожного виділеного блоку в купі ASan виділяє додаткову тіньову пам'ять (*shadow memory*), де фіксує статус кожного байта: чи є він доступним для читання/запису, чи належить до червоної зони безпеки (*redzone*), чи пам'ять уже вивільнено (*poisoned/freed memory*).

Паралельно модуль LeakSanitizer (*LSan*) на момент виходу з функції `main()` сканує весь адресний простір програми (стек, глобальні змінні, регістри процесора). Якщо в пам'яті більше немає жодного кореневого покажчика, що посилається на виділений раніше блок у купі, цей блок позначається як прямий витік пам'яті (*direct leak*).

Скомпілюємо та запустимо нашу програму:

```bash
clang++ -std=c++20 -fsanitize=address,undefined -g main.cpp -o leak_test
./leak_test
```

У консолі з'являється детальний звіт санітайзера:

```text
=== Старт тесту: видалення через BaseService* ===
[+] HeavyStreamingService створено: 1048576 байтів у купі
=== Завершення main() ===

=================================================================
==184920==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 1048576 byte(s) in 1 object(s) allocated from:
    #0 0x55d21a in operator new[](unsigned long)
    #1 0x55d3f2 in HeavyStreamingService::HeavyStreamingService(unsigned long) main.cpp:18
    #2 0x55d342 in main main.cpp:32

Direct leak of 4000 byte(s) in 1 object(s) allocated from:
    #0 0x55d140 in operator new(unsigned long)
    #1 0x55d780 in std::vector<int>::_M_default_initialize(unsigned long)
    #2 0x55d3e0 in HeavyStreamingService::HeavyStreamingService(unsigned long) main.cpp:17
    #3 0x55d342 in main main.cpp:32

SUMMARY: AddressSanitizer: 1052576 byte(s) leaked in 2 allocation(s).
```

### Аналіз результатів тесту

Звіт санітайзера наочно демонструє дві фундаментальні проблеми:

1. Рядок `[-] HeavyStreamingService успішно зруйновано` не був надрукований. Це означає, що компілятор повністю оминув тіло деструктора нащадка. Вказівник `dynamic_payload`, що утримував 1 мегабайт даних, був просто затертий без виклику `delete[]`.
2. Внутрішній буфер `std::vector<int>` розміром 4000 байтів (1000 елементів `int` по 4 байти) також витік. Оскільки деструктор вектора викликається всередині неявного деструктора `HeavyStreamingService`, пропуск деструктора класу автоматично блокує руйнування всіх його полів-членів.

Як тільки ми додаємо ключове слово `virtual` до оголошення деструктора базового класу `virtual ~BaseService() = default;`, компілятор починає здійснювати виклик через таблицю vtable. Деструктор нащадка отримує керування, коректно звільняє буфер і руйнує вектор. Повторний запуск під AddressSanitizer видає бездоганний результат: `0 leaks detected`.

## Лабораторія 2: Фізичне зміщення покажчиків при множинному успадкуванні

Найбільш руйнівна форма аварії виникає тоді, коли об'єкт успадковує кілька базових класів одночасно. У цьому разі мова C++ використовує концепцію підоб'єктів, де кожен базовий клас розташовується за власним зміщенням усередині загального блоку пам'яті.

Дослідимо внутрішню топологію об'єкта та покажемо, як невіртуальний деструктор призводить до фатального падіння аллокатора операційної системи.

```cpp
#include <iostream>
#include <iomanip>
#include <cstdint>

struct InterfaceA {
    virtual void methodA() = 0;
    virtual ~InterfaceA() = default; // Віртуальний деструктор
};

struct InterfaceB {
    virtual void methodB() = 0;
    // Помилка: деструктор НЕ є віртуальним
    ~InterfaceB() = default;
};

class ConcreteComponent : public InterfaceA, public InterfaceB {
    int payload_data[16]{};
public:
    ConcreteComponent() { payload_data[0] = 42; }
    void methodA() override { std::cout << "Виклик methodA()\n"; }
    void methodB() override { std::cout << "Виклик methodB()\n"; }
    ~ConcreteComponent() { std::cout << "Виклик ~ConcreteComponent()\n"; }
};

int main() {
    std::cout << "=== Дослідження зміщення покажчиків ===\n";
    ConcreteComponent* component = new ConcreteComponent();
    
    // Отримуємо поліморфні покажчики на різні інтерфейси одного об'єкта
    InterfaceA* ptrA = component;
    InterfaceB* ptrB = component;

    std::cout << std::hex << std::showbase;
    std::cout << "Адреса ConcreteComponent (початок блоку malloc): " << reinterpret_cast<uintptr_t>(component) << "\n";
    std::cout << "Адреса InterfaceA (зсув 0):                     " << reinterpret_cast<uintptr_t>(ptrA) << "\n";
    std::cout << "Адреса InterfaceB (зсув +8/+16):                " << reinterpret_cast<uintptr_t>(ptrB) << "\n";

    std::ptrdiff_t offset = reinterpret_cast<char*>(ptrB) - reinterpret_cast<char*>(component);
    std::cout << std::dec;
    std::cout << "Фізичний зсув покажчика InterfaceB: " << offset << " байтів\n";

    // Спроба видалення через InterfaceA (безпечно)
    delete ptrA;
    
    return 0;
}
```

### Результат роботи та аналіз адрес пам'яті

Запустивши програму на 64-бітній системі Linux x86_64, ми отримуємо такий вивід:

```text
=== Дослідження зміщення покажчиків ===
Адреса ConcreteComponent (початок блоку malloc): 0x55a1b420eeb0
Адреса InterfaceA (зсув 0):                     0x55a1b420eeb0
Адреса InterfaceB (зсув +8/+16):                0x55a1b420eeb8
Фізичний зсув покажчика InterfaceB: 8 байтів
Виклик ~ConcreteComponent()
```

### Анатомія збою при delete ptrB

Розглянемо покроково, що сталося б, якби в наведеній програмі ми викликали `delete ptrB;` замість `delete ptrA;`:

1. Системний алокатор `operator new` виділив єдиний неперервний блок пам'яті за базовою адресою `0x55a1b420eeb0`.
2. На початку блоку розташовано підоб'єкт `InterfaceA`, який містить свій покажчик на віртуальну таблицю (`vptr` розміром 8 байтів).
3. Наступним у пам'яті розташовано підоб'єкт `InterfaceB` — зі зміщенням рівно `+8` байтів, за адресою `0x55a1b420eeb8`.
4. Оскільки `~InterfaceB()` не оголошений як віртуальний, компілятор трактує вираз `delete ptrB;` як статичний виклик. Транслятор генерує виклик `free(0x55a1b420eeb8)`.
5. Системна бібліотека `glibc` або алокатор операційної системи шукає заголовок виділеного блока пам'яті перед переданою адресою (за адресою `ptr - 8` або `ptr - 16`). Проте за цією адресою лежать дані підоб'єкта `InterfaceA`, а не метадані алокатора.
6. Алокатор фіксує порушення цілісності купи та негайно генерує сигнал аварійної зупинки процесу:
   ```text
   free(): invalid pointer
   Aborted (core dumped)
   ```

Якщо ж ми оголошуємо `virtual ~InterfaceB() = default;`, компілятор розміщує в таблиці vtable класу `ConcreteComponent` так званий **адаптивний перехідний деструктор** (*adjustor thunk*). Ця функція перед викликом деструктора зчитує з vtable значення зміщення до вершини об'єкта (*offset-to-top*, у нашому випадку `-8`), автоматично віднімає 8 байтів від значення `ptrB` і передає в системну функцію `free()` правильну вихідну адресу `0x55a1b420eeb0`. Процес завершується чисто і без помилок.

## Лабораторія 3: Моделювання пошкодження розмірних пулів пам'яті (Sized Deallocation)

Щоб наочно побачити, як невіртуальний деструктор пошкоджує пам'ять без множинного успадкування в стандарті C++14/17, створимо модель ізольованого пулу пам'яті (*size-segregated memory pool*).

```cpp
#include <iostream>
#include <cstddef>
#include <vector>
#include <cassert>

// Модель пулу пам'яті з корзинами для різних розмірів
class SimpleSegregatedAllocator {
    static constexpr std::size_t BIN_SMALL = 8;
    static constexpr std::size_t BIN_LARGE = 128;

    std::vector<void*> free_list_small;
    std::vector<void*> free_list_large;

public:
    void* allocate(std::size_t size) {
        if (size <= BIN_SMALL) {
            std::cout << "[ALLOC] Виділено з пулу SMALL (" << size << " байтів)\n";
            return ::operator new(BIN_SMALL);
        }
        std::cout << "[ALLOC] Виділено з пулу LARGE (" << size << " байтів)\n";
        return ::operator new(BIN_LARGE);
    }

    void deallocate(void* ptr, std::size_t size) {
        if (size <= BIN_SMALL) {
            std::cout << "[FREE]  Повернено в пул SMALL (" << size << " байтів) <-- ПОМИЛКА ДЕАЛОКАЦІЇ!\n";
            free_list_small.push_back(ptr);
        } else {
            std::cout << "[FREE]  Повернено в пул LARGE (" << size << " байтів)\n";
            free_list_large.push_back(ptr);
        }
    }
};

static SimpleSegregatedAllocator g_pool;

struct BaseNode {
    // Невіртуальний деструктор
    ~BaseNode() = default;

    static void* operator new(std::size_t sz) {
        return g_pool.allocate(sz);
    }
    static void operator delete(void* ptr, std::size_t sz) noexcept {
        g_pool.deallocate(ptr, sz);
    }
};

struct BigDataNode : public BaseNode {
    char raw_payload[120]{}; // Робить об'єкт великим (120 байтів)
    ~BigDataNode() = default;
};

int main() {
    std::cout << "=== Тест деалокації з точним розміром ===\n";
    std::cout << "sizeof(BaseNode):    " << sizeof(BaseNode) << " байтів\n";
    std::cout << "sizeof(BigDataNode): " << sizeof(BigDataNode) << " байтів\n\n";

    BaseNode* node = new BigDataNode();
    delete node; // Поліморфне видалення

    return 0;
}
```

### Аналіз консольного виводу

```text
=== Тест деалокації з точним розміром ===
sizeof(BaseNode):    1 байтів
sizeof(BigDataNode): 120 байтів

[ALLOC] Виділено з пулу LARGE (120 байтів)
[FREE]  Повернено в пул SMALL (1 байтів) <-- ПОМИЛКА ДЕАЛОКАЦІЇ!
```

Цей експеримент показує прихований механізм катастрофи:
1. Під час створення `new BigDataNode()` алокатор отримав реальний розмір об'єкта (120 байтів) і виділив блок із пулу великих об'єктів `LARGE`.
2. Під час видалення `delete node;`, оскільки `BaseNode` має невіртуальний деструктор, компілятор статично передав у функцію деалокації `sizeof(BaseNode)` (1 байт).
3. Алокатор помилково повернув 120-байтовий блок у пул 8-байтових об'єктів `SMALL`.
4. Наступний виклик `new SmallNode()` у програмі отримає цей блок і запише туди маленькі дані. Проте система керування великими блоками вважатиме цей блок або втраченим, або повторно використає його під інший великий об'єкт, що спричинить взаємне перетирання пам'яті (*use-after-free* / *memory aliasing*).

Оголошення деструктора віртуальним змушує компілятор згенерувати деструктор видалення `D0`, який передає в `operator delete` точний розмір 120 байтів, зберігаючи цілісність пулів пам'яті.

## Лабораторія 4: Нульові накладні витрати зі статичним поліморфізмом (CRTP)

Коли об'єкт не призначений для динамічного поліморфного видалення через покажчик на базу, використання `virtual` є невиправданою витратою пам'яті та швидкодії процесора. Реалізуємо безпечну домішку на основі шаблону CRTP (*Curiously Recurring Template Pattern*) із захищеним деструктором.

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <chrono>

// Шаблонний базовий клас CRTP
template <typename Derived>
class ObservableMixin {
protected:
    // Захищений невіртуальний деструктор блокує небезпечне видалення
    ~ObservableMixin() = default;

public:
    void emit_event(const std::string& msg) {
        // Статична диспетчеризація часу компіляції (inline)
        static_cast<Derived*>(this)->handle_event(msg);
    }
};

// Конкретний сервіс
class TelemetryManager : public ObservableMixin<TelemetryManager> {
    int counter{0};
public:
    void handle_event(const std::string& msg) {
        ++counter;
        std::cout << "[Event #" << counter << "] " << msg << "\n";
    }

    ~TelemetryManager() {
        std::cout << "[~] TelemetryManager успішно очищено\n";
    }
};

int main() {
    std::cout << "=== Статичний поліморфізм CRTP ===\n";
    
    // 1. Створення на стеку
    {
        TelemetryManager manager;
        manager.emit_event("Ініціалізація датчиків");
    }

    // 2. Створення в купі через покажчик на конкретний тип
    {
        auto dynamic_mgr = std::make_unique<TelemetryManager>();
        dynamic_mgr->emit_event("Отримано кадр телеметрії");
    }

    // 3. Перевірка безпеки компіляції:
    /*
    ObservableMixin<TelemetryManager>* unsafe_ptr = new TelemetryManager();
    delete unsafe_ptr; // ПОМИЛКА КОМПІЛЯЦІЇ: деструктор захищений!
    */

    std::cout << "Розмір TelemetryManager: " << sizeof(TelemetryManager) << " байтів\n";
    return 0;
}
```

### Переваги захищеного деструктора

1. **Повна безпека на етапі компіляції:** розробник фізично не може випадково викликати `delete` через вказівник на базову домішку. Будь-яка спроба призводить до зрозумілої помилки трансляції `error: '~ObservableMixin' is protected within this context`.
2. **Нуль байтів накладних витрат:** розмір об'єкта `TelemetryManager` становить лише 4 байти (одне поле `int`), оскільки клас не містить покажчика `vptr` на таблицю методів.
3. **Пряме вбудовування коду:** виклики методів та деструктора повністю оптимізуються компілятором без жодного непрямого переходу через пам'ять, забезпечуючи максимальну продуктивність на апаратному рівні.
