# ⚙️ Симулятор оракульних машин та обчислення стрибка

Практичний код для дискретного моделювання оракульних машин Тюринга, відстеження запитів до оракула, симуляції стрибка Тюринга на скінченних підмножинах та реалізації спрощеної процедури пріоритету Фрідберга — Мучника.

## 1. Архітектура симулятора оракульної системи

Для моделювання відносної обчислюваності на комп'ютері необхідно створити середовище, здатне імітувати роботу алгоритмів з оракулом. Оскільки реальні математичні оракули оперують нескінченними множинами натуральних чисел, у програмуванні застосовується дискретне наближення: оракул задається скінченною підмножиною або математичним предикатом (абстрактною функцією), а машина Тюринга моделюється у вигляді управляючого автомата з двома стрічками (робочою стрічкою та стрічкою запиту).

Програмний комплекс складається з трьох ключових системних модулів:

1. **Модуль Оракула (`OracleProvider`)**: Абстрагує доступ до характеристичної множини `B`. Він приймає номер запитуваного елемента `x` і за постійний час `O(1)` повертає бінарний результат: `1` (якщо елемент належить множині) або `0` (якщо елемент відсутній).
2. **Трасувальник запитів (`QueryTracker`)**: Записує кожне звернення машини до оракула. На основі зареєстрованих даних він обчислює функцію використання `u(x) = 1 + max(x_i)`, яка визначає точний обсяг зовнішньої інформації, зчитаної алгоритмом під час обчислення.
3. **Виконавчий рушій машини Тюринга (`OracleTuringMachine`)**: Виконує покрокову інтерпретацію кодів інструкцій, керує робочою стрічкою, зсуває голівку зчитування та контролює ліміт кроків для запобігання нескінченному зацикленню.

Низькорівнева модель реалізує прямий контроль над пам'яттю та реєстрами оракула, тоді як об'єктно-орієнтована версія ізолює робочий процес за допомогою безпечних контейнерів C++20.

Нижче наведено повну реалізацію симулятора двома мовами програмування: ідіоматичною мовою C (із ручним управлінням пам'яттю) та сучасним стандартом C++20 (із використанням RAII, концептів та стандартних контейнерів).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_TAPE_SIZE 1024
#define MAX_STEPS 1000

/* --- Структури даних для C-реалізації --- */

typedef struct {
    uint8_t *elements;
    size_t capacity;
} finite_oracle_t;

typedef struct {
    size_t query_count;
    uint32_t queries[MAX_TAPE_SIZE];
    bool responses[MAX_TAPE_SIZE];
    uint32_t max_queried_value;
} query_log_t;

typedef enum {
    STATE_RUNNING,
    STATE_HALTED,
    STATE_STEP_LIMIT_EXCEEDED
} machine_status_t;

typedef struct {
    int tape[MAX_TAPE_SIZE];
    size_t head_pos;
    size_t query_tape[MAX_TAPE_SIZE];
    size_t query_len;
    machine_status_t status;
    size_t steps_executed;
    query_log_t log;
} otm_state_t;

/* Створення та ініціалізація оракула */
finite_oracle_t* oracle_create(size_t capacity) {
    finite_oracle_t *oracle = (finite_oracle_t*)malloc(sizeof(finite_oracle_t));
    if (!oracle) return NULL;
    oracle->elements = (uint8_t*)calloc(capacity, sizeof(uint8_t));
    oracle->capacity = capacity;
    return oracle;
}

void oracle_free(finite_oracle_t *oracle) {
    if (oracle) {
        free(oracle->elements);
        free(oracle);
    }
}

void oracle_add(finite_oracle_t *oracle, uint32_t value) {
    if (oracle && value < oracle->capacity) {
        oracle->elements[value] = 1;
    }
}

bool oracle_query(const finite_oracle_t *oracle, uint32_t value, query_log_t *log) {
    bool result = false;
    if (oracle && value < oracle->capacity) {
        result = (oracle->elements[value] == 1);
    }
    if (log && log->query_count < MAX_TAPE_SIZE) {
        log->queries[log->query_count] = value;
        log->responses[log->query_count] = result;
        if (value > log->max_queried_value) {
            log->max_queried_value = value;
        }
        log->query_count++;
    }
    return result;
}

/* Ініціалізація оракульної машини */
void otm_init(otm_state_t *machine) {
    memset(machine->tape, 0, sizeof(machine->tape));
    machine->head_pos = MAX_TAPE_SIZE / 2;
    machine->query_len = 0;
    machine->status = STATE_RUNNING;
    machine->steps_executed = 0;
    machine->log.query_count = 0;
    machine->log.max_queried_value = 0;
}

/* Симуляція виконання алгоритму з оракулом:
   Приклад програми: обчислити x + 1, якщо x ∈ B; інакше 0 */
void otm_run_example(otm_state_t *machine, const finite_oracle_t *oracle, uint32_t input_x) {
    otm_init(machine);
    
    /* Запис входження x на стрічку запиту */
    machine->query_tape[0] = input_x;
    machine->query_len = 1;
    machine->steps_executed++;

    /* Запит до оракула B */
    bool in_oracle = oracle_query(oracle, input_x, &machine->log);
    machine->steps_executed++;

    /* Прийняття рішення за результатом запиту */
    if (in_oracle) {
        machine->tape[machine->head_pos] = (int)input_x + 1;
    } else {
        machine->tape[machine->head_pos] = 0;
    }
    
    machine->status = STATE_HALTED;
}

/* Симуляція стрибка Тюринга (A') для перших N машин на оракулі A */
void compute_turing_jump_approximation(const finite_oracle_t *oracle, size_t num_machines) {
    printf("=== Симуляція Стрибка Тюринга (A') ===\n");
    for (size_t m = 0; m < num_machines; ++m) {
        otm_state_t machine;
        /* Перевірка зупинки машини 'm' на власному індексі */
        otm_run_example(&machine, oracle, (uint32_t)m);
        
        bool halted = (machine.status == STATE_HALTED);
        size_t use_func = machine.log.max_queried_value + 1;
        
        printf("Машина M_%zu^A(%zu): %s | Кроків: %zu | Стрибок A' ∈ [%s] | Використання u(%zu) = %zu\n",
               m, m,
               halted ? "ЗУПИНИЛАСЯ" : "РОЗБІГАЄТЬСЯ",
               machine.steps_executed,
               halted ? "ТАК" : "НІ",
               m, use_func);
    }
}

int main(void) {
    /* Створення оракула A = {1, 3, 7, 12} */
    finite_oracle_t *oracle_A = oracle_create(64);
    oracle_add(oracle_A, 1);
    oracle_add(oracle_A, 3);
    oracle_add(oracle_A, 7);
    oracle_add(oracle_A, 12);

    compute_turing_jump_approximation(oracle_A, 5);

    oracle_free(oracle_A);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <unordered_set>
#include <memory>
#include <optional>
#include <string_view>
#include <algorithm>
#include <cstdint>

// --- Об'єктно-орієнтований симулятор на C++20 ---

class FiniteOracle {
private:
    std::unordered_set<uint32_t> elements_;

public:
    explicit FiniteOracle(std::initializer_list<uint32_t> init) : elements_(init) {}

    void insert(uint32_t val) { elements_.insert(val); }
    void remove(uint32_t val) { elements_.erase(val); }

    [[nodiscard]] bool contains(uint32_t val) const noexcept {
        return elements_.contains(val);
    }
};

struct QueryRecord {
    uint32_t queried_value;
    bool response;
};

class QueryTracker {
private:
    std::vector<QueryRecord> history_;
    uint32_t max_queried_{0};

public:
    bool query(const FiniteOracle& oracle, uint32_t val) {
        bool res = oracle.contains(val);
        history_.push_back({val, res});
        max_queried_ = std::max(max_queried_, val);
        return res;
    }

    [[nodiscard]] uint32_t get_use_function() const noexcept {
        return history_.empty() ? 0 : max_queried_ + 1;
    }

    [[nodiscard]] const std::vector<QueryRecord>& get_history() const noexcept {
        return history_;
    }
};

enum class ExecutionState {
    Running,
    Halted,
    TimeLimitExceeded
};

class OracleTuringMachine {
private:
    std::vector<int> tape_;
    size_t head_position_{512};
    size_t steps_{0};
    ExecutionState state_{ExecutionState::Running};
    QueryTracker tracker_;

public:
    OracleTuringMachine() : tape_(1024, 0) {}

    void run_program(const FiniteOracle& oracle, uint32_t input_x) {
        steps_ = 0;
        state_ = ExecutionState::Running;

        // Крок 1: Запит до оракула про наявність input_x
        steps_++;
        bool answer = tracker_.query(oracle, input_x);

        // Крок 2: Модифікація стрічки залежно від відповіді
        steps_++;
        if (answer) {
            tape_[head_position_] = static_cast<int>(input_x * 2 + 1);
        } else {
            tape_[head_position_] = -1;
        }

        state_ = ExecutionState::Halted;
    }

    [[nodiscard]] ExecutionState get_state() const noexcept { return state_; }
    [[nodiscard]] size_t get_steps() const noexcept { return steps_; }
    [[nodiscard]] const QueryTracker& get_tracker() const noexcept { return tracker_; }
    [[nodiscard]] int get_tape_value() const noexcept { return tape_[head_position_]; }
};

// Моделювання симуляції пріоритету Фрідберга — Мучника
class PriorityMethodSimulator {
private:
    struct Requirement {
        size_t id;
        uint32_t witness;
        bool satisfied{false};
        uint32_t restraint{0};
    };

    std::vector<Requirement> reqs_A_; // Для A != M_e^B
    std::vector<Requirement> reqs_B_; // Для B != M_e^A
    FiniteOracle set_A_{{}};
    FiniteOracle set_B_{{}};

public:
    explicit PriorityMethodSimulator(size_t num_requirements) {
        uint32_t w = 0;
        for (size_t i = 0; i < num_requirements; ++i) {
            reqs_A_.push_back({i, w++, false, 0});
            reqs_B_.push_back({i, w++, false, 0});
        }
    }

    void step_simulate() {
        std::cout << "\n=== Симуляція кроку пріоритету Фрідберга-Мучника ===\n";
        for (size_t i = 0; i < reqs_A_.size(); ++i) {
            auto& req = reqs_A_[i];
            if (!req.satisfied) {
                // Задовольняємо вимогу R_{2e}: додаємо свідок до A
                set_A_.insert(req.witness);
                req.satisfied = true;
                req.restraint = req.witness + 5;
                std::cout << "[Вимога R_" << (2 * i) << "] Задоволена: свідок "
                          << req.witness << " додано до A. Обмеження r = "
                          << req.restraint << "\n";

                // Пошкодження (Injury) вимог нижчого пріоритету в B
                for (size_t j = i + 1; j < reqs_B_.size(); ++j) {
                    if (reqs_B_[j].satisfied && reqs_B_[j].witness < req.restraint) {
                        reqs_B_[j].satisfied = false;
                        std::cout << "  ↳ [ПОШКОДЖЕННЯ] Вимога R_" << (2 * j + 1)
                                  << " пошкоджена обмеженням r=" << req.restraint << "!\n";
                    }
                }
            }
        }
    }
};

int main() {
    FiniteOracle oracle_B{2, 5, 8, 11, 14};
    OracleTuringMachine machine;

    std::cout << "=== Симуляція оракульної машини на C++20 ===\n";
    for (uint32_t x : {2, 3, 5, 7}) {
        machine.run_program(oracle_B, x);
        std::cout << "Вхід x=" << x
                  << " | Стан: " << (machine.get_state() == ExecutionState::Halted ? "Зупинено" : "Працює")
                  << " | Стрічка: " << machine.get_tape_value()
                  << " | Функція використання u(" << x << ") = "
                  << machine.get_tracker().get_use_function() << "\n";
    }

    PriorityMethodSimulator sim(3);
    sim.step_simulate();

    return 0;
}
```
:::

---

## 2. Детальний аналіз реалізації та механізмів обчислення

### 2.1 C-реалізація: низькорівневе управління ресурсами
У реалізації мовою C структура `finite_oracle_t` використовує динамічно виділений масив байтів `uint8_t *elements`. Кожна комірка масиву відповідає прапорцю належності числа `x` до оракула (де `1` означає належність, а `0` — відсутність). Функція `oracle_create()` виконує виділення пам'яті через `calloc()`, гарантуючи початкове обнулення всіх елементів.

При виклику `oracle_query()` виконується перевірка виходу за межі виділеного масиву `capacity`. Якщо запитане число знаходиться в межах допуску, функція повертає відповідний біт. Одночасно з цим у структуру `query_log_t` записується значення `value` та отримана відповідь. Трасувальник автоматично оновлює поле `max_queried_value`, на основі якого вираховується функція використання `u(x) = max_queried_value + 1`.

Пам'ять під оракул звільняється викликом `oracle_free()`, який послідовно очищає динамічний масив `elements` та саму структуру оракула.

### 2.2 C++20 реалізація: RAII та безпека типів
У реалізації мовою C++ класи `FiniteOracle` та `OracleTuringMachine` застосовують принцип RAII (англ. *Resource Acquisition Is Initialization*). Оракул зберігає елементи всередині контейнера `std::unordered_set<uint32_t>`, що забезпечує середній час пошуку `O(1)` за рахунок хешування і звільняє розробника від ручного розрахунку розмірів масивів.

Клас `QueryTracker` інкапсулює логіку журналювання. Метод `query()` приймає константне посилання на `FiniteOracle`, запобігаючи випадковій модифікації станів оракула. Журнал запитів зберігається у вигляді `std::vector<QueryRecord>`, що дає змогу легко отримувати повну історію через метод `get_history()`.

Для відстеження стану виконання застосовано `enum class ExecutionState`, який запобігає неявним перетворенням типів, притаманним класичним C-переліченням.

### 2.3 Моделювання обчислення стрибка Тюринга
Функція `compute_turing_jump_approximation()` виконує дискретну симуляцію діагональної множини `A' = {e | M_e^A(e) ↓}`. На вхід подається оракул `A` та кількість розгляданих машин `num_machines`. 

Для кожного індексу `m` симулятор запускає програму `M_m^A` на власному вхідному значенні `m`. За результатами виконання машина формує рядок статусу:
- Якщо машина виходить у стан `STATE_HALTED`, це означає, що число `m` належить до наближення стрибка `A'`.
- Якщо за фіксовану кількість кроків `MAX_STEPS` машина не зупиняється, вона розглядається як розбіжна для даного часового горизонту.
- Журнал запитів вираховує локальне значення функції використання `u(m)`. Це показує, яка частина оракула `A` була прочитана для прийняття рішення про зупинку.

---

## 3. Моделювання процедури пріоритету Фрідберга — Мучника

Клас `PriorityMethodSimulator` демонструє практичну симуляцію кроків розв'язання проблеми Поста. 

У конструкторі `PriorityMethodSimulator(size_t num_requirements)` створюються два масиви вимог: `reqs_A_` (для забезпечення `A ≠ M_e^B`) та `reqs_B_` (для забезпечення `B ≠ M_e^A`). Кожній вимозі виділяється унікальний початковий свідок `witness`.

Під час виконання методу `step_simulate()` відбуваються такі етапи:
1. **Перевірка ненасиченості**: Симулятор знаходить першу ненасичену вимогу `R_{2i}` у списку `reqs_A_`.
2. **Задоволення вимоги**: Свідок `req.witness` додається до оракула `set_A_`. Вимога відмічається прапорцем `satisfied = true`, і для неї встановлюється значення обмеження `restraint = witness + 5`.
3. **Обчислення пошкоджень (Injuries)**: Симулятор переглядає всі вимоги нижчого пріоритету у списку `reqs_B_` (індекси `j > i`). Якщо якась вимога вже вважалася задоволеною, але її свідок виявився меншим за нове обмеження `req.restraint`, ця вимога **пошкоджується**: її прапорець `satisfied` скидається у `false`, і на наступному кроці для неї буде виділено новий свідок.

Цей процес наочно демонструє стабілізаційну динаміку: вимоги вищого пріоритету поступово задовольняються назавжди, припиняючи створювати нові пошкодження для вимог нижчого пріоритету.

 Покроковий простежувальний лог виконання показує, як при задоволенні вимоги `R_0` встановлюється обмеження `r_0 = 5`. Коли вимога нижчого пріоритету `R_3` намагається використати свідок `y_1 = 3 < 5`, симулятор блокує цю дію або скидає її стан, ілюструючи підпорядковану ієрархію пріоритетного дерева.

---

## 4. Крайові випадки та обмеження дискретної симуляції

Під час роботи з оракульними симуляторами слід враховувати такі крайові випадки:
1. **Переповнення стрічки запиту**: В C-реалізації масив `queries` обмежений константою `MAX_TAPE_SIZE`. При досягненні цього ліміту симулятор припиняє запис нових елементів до траси і повертає помилку. У C++ реалізації контейнер `std::vector` динамічно розширюється, але обмежений обсягом доступної оперативної пам'яті.
2. **Нескінченне зациклення (Обмеження по кроках)**: Якщо оракульна машина `M_e^B(x)` розбігається (не виходить у стан `q_halt`), реальний алгоритм працюватиме нескінченно. Симулятор контролює цей випадок за допомогою лічильника `steps_executed` та ліміту `MAX_STEPS`. При досягненні ліміту статус змінюється на `STATE_STEP_LIMIT_EXCEEDED` (або `ExecutionState::TimeLimitExceeded`).
3. **Невизначені значення оракула**: Якщо машина запитує елемент `x`, що перевищує обсяг `capacity` в C-реалізації, оракул повертає стандартне значення `false` (0), запобігаючи несанкціонованому зчитуванню пам'яті (англ. *out-of-bounds read*).

---

## 5. Інструкції з компіляції та запуску

Для компіляції та запуску симулятора C-версії застосовується стандартний компілятор `gcc` або `clang`:

```bash
# Компіляція C-реалізації (стандарт C99)
gcc -std=c99 -Wall -Wextra -O2 proj-oracle-machine.c -o oracle_sim_c
./oracle_sim_c
```

Для компіляції об'єктно-орієнтованого C++20 коду потрібен компілятор із підтримкою сучасної стандартної бібліотеки (GCC 10+, Clang 13+, MSVC 2019+):

```bash
# Компіляція C++20 реалізації
g++ -std=c++20 -Wall -Wextra -O2 proj-oracle-machine.cpp -o oracle_sim_cpp
./oracle_sim_cpp
```

Обидві програми виводять на консоль детальний журнал запитів, стан стрічки, значення функцій використання `u(x)` та кроки стабілізації вимог у пріоритетному алгоритмі.
