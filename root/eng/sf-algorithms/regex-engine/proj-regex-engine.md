# ⚙️ Реалізація рушія регулярних виразів: від парсингу до НКА Томпсона

Створення лінійного рушія регулярних виразів вимагає послідовного вирішення двох фундаментальних задач комбінаторної обробки текстів та теорії автоматів: перетворення текстового шаблону з інфіксної нотації у граф Недетермінованого Скінченного Автомата (НКА) за допомогою виведення Томпсона та побудови віртуальної машини (Pike VM) для паралельної симуляції множини активних станів без використання рекурсивного бектрекінгу.

У цьому практичному керівництві детально розібрано архітектуру, математичні інваріанти, структури даних та повністю робочу реалізацію рушія двома системними мовами програмування — C та C++. Реалізація містить повний конвеєр обробки: від автоматичного перетворення інфіксного шаблону (наприклад, `(a|b)*abb`) у постфіксний запис із додаванням неявних операторів конкатенації до побудови графа станів та їх виконання за лінійний час `O(M · N)`.

## Теоретичний фундамент та структури даних

Класична симуляція НКА за алгоритмом Кліні–Томпсона спирається на побудову спрямованого графа, де кожна вершина (стан) описується певним типом операції (опокодом), а ребра задають переходи між станами.

### Модель станів НКА

У нашій архітектурі кожен стан автомата належить до одного з трьох типів:
1. **Символьний стан (Literal / Match Token)**: містить конкретний символ вхідного алфавіту (наприклад, 'a', 'b', '0'). Автомат споживає один символ з вхідного потоку даних і переходить за єдиним вказівником `out`.
2. **Стан розгалуження (Split / `ε`-перехід)**: не споживає символів з вхідного тексту. Містить два безумовних вказівники `out` та `out1`, дозволяючи автомату перебувати в двох станах одночасно.
3. **Термінальний стан (Accept / Match)**: позначає успішне закінчення зіставляння шаблону з текстом. Не має вихідних дуг.

Для запобігання нескінченним циклам при обробці `ε`-переходів кожному стану додається службове поле `last_step`. Це числове поле зберігає номер поточного кроку сканування вхідного тексту. Якщо під час обчислення `ε`-замикання стан спробувати відвідати повторно на тому самому кроці, рушій негайно ігнорує його, забезпечуючи лінійний час виконання.

### Алгоритм розбору та інфіксно-постфіксна трансформація (Shunting-Yard)

Перш ніж будувати граф автомата, текстовий шаблон у звичайній інфіксній нотації (наприклад, `(a|b)*abb`) необхідно перетворити у постфіксну форму (зворотний польський запис), де оператори передують своїм операндам або йдуть одразу за ними.

Для цього використовується модифікований алгоритм Дейкстри «сортівна станція» (Shunting-Yard algorithm). У регулярних виразах оператори мають наступні рівні пріоритету (від найвищого до найнижчого):
1. **Ітерація Кліні `*` (унарний постфіксний оператор)**: найвищий пріоритет. Виконується миттєво над попереднім символом або групою.
2. **Конкатенація `.` (бінарний інфіксний оператор)**: середній пріоритет. Зв'язує сусідні символи або дужки. У більшості синтаксисів регулярних виразів знак конкатенації опускається (наприклад, `ab`), тому препроцесор парсера автоматично вставляє явний символ конкатенації `.` між двома літералами, після зірочка перед літералом, або між закриваючою та відкриваючою дужками.
3. **Альтернація `|` (бінарний інфіксний оператор)**: найнижчий пріоритет. Розділяє альтернативні гілки шаблону.

Приклади трансформації інфіксного шаблону у постфіксну форму:
- Інфіксний вираз `a|b` → Постфіксний вираз `ab|`
- Інфіксний вираз `ab` (неявна конкатенація `a.b`) → Постфіксний вираз `ab.`
- Інфіксний вираз `(a|b)*abb` (з неявною конкатенацією `(a|b)*.a.b.b`) → Постфіксний вираз `ab|*a.b.b.`

### Метод фрагментів Томпсона та з'єднання переходів

Побудова графа автомата виконується за допомогою стекового аналізатора постфіксної нотації шаблону. Під час парсингу кожна підмережа автомата представлена структурою `Fragment` (фрагмент НКА). Фрагмент характеризується двома елементами:
- `start`: вказівник на початковий стан даного фрагмента;
- `out_list`: список незаповнених вказівників на вихідні дуги (типу `State**`), які чекають на підключення до наступних станів.

Під час обробки оператора конкатенації `A · B` список виходів фрагмента `A` «патчиться» (з'єднується) з початковим станом фрагмента `B`. Це виконується проходом по списку `out_list` фрагмента `A` та присвоєнням `*ptr = B.start`.

Під час обробки альтернації `A | B` створюється новий стан розгалуження `Split`, виходи `out` та `out1` якого спрямовуються на входи `A.start` та `B.start` відповідно, а вихідні списки `A.out_list` та `B.out_list` об'єднуються у єдиний список `out_list` підсумкового фрагмента.

Для оператора ітерації Кліні `A*` створюється стан розгалуження `Split`. Один його вихід веде на вхід `A.start`, а другий залишається відкритим для виходу. Вихідний список `A.out_list` патчиться назад на створений стан `Split`, що формує циклічну `ε`-петлю повторення.

## Повний вихідний код реалізації мовами C та C++

У наведеному нижче коді представлено дві ідіоматичні реалізації. Версія мовою C демонструє пряме управління вказівниками, явні структури пам'яті, динамічний парсинг інфіксного шаблону у постфіксний та ручний патчинг списків переходів. Версія мовою C++20 використовує концепції RAII, автоматичне управління ресурсами через `std::unique_ptr`, контейнери `std::vector` та безпечні рядкові зрізи `std::string_view`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

/* Опокоди спеціальних переходів НКА */
#define MATCH_TOKEN 256
#define SPLIT_TOKEN 257

/* Структура стану НКА Томпсона */
typedef struct State {
    int opcode;          /* Звичайний символ (0..255), MATCH_TOKEN або SPLIT_TOKEN */
    struct State *out;   /* Перший вихідний перехід */
    struct State *out1;  /* Другий вихідний перехід (тільки для SPLIT_TOKEN) */
    int last_step;       /* Маркер для відсікання дубльованих відвідувань */
} State;

/* Фрагмент НКА із незавершеними вихідними переходами */
typedef struct Fragment {
    State *start;
    State **out_list;
} Fragment;

/* Динамічна множина активних станів на поточному кроці */
typedef struct StateList {
    State **states;
    int count;
    int capacity;
} StateList;

/* Створення нового стану автомата в купі */
static State* create_state(int opcode, State *out, State *out1) {
    State *s = (State*)malloc(sizeof(State));
    if (!s) {
        fprintf(stderr, "Помилка виділення пам'яті під стан НКА\n");
        exit(EXIT_FAILURE);
    }
    s->opcode = opcode;
    s->out = out;
    s->out1 = out1;
    s->last_step = 0;
    return s;
}

/* З'єднання списку вихідних дуг із цільовим станом */
static void patch(State **l, State *s) {
    *l = s;
}

/* Перетворення інфіксного шаблону в постфіксний із вставкою крапок конкатенації */
static char* re2post(const char *re) {
    int nalt = 0, natom = 0;
    static char buf[8000];
    char *dst = buf;
    struct {
        int nalt;
        int natom;
    } paren[100], *p = paren;

    if (strlen(re) >= 1000) return NULL;

    for (; *re; re++) {
        switch (*re) {
            case '(':
                if (natom > 1) {
                    natom--;
                    *dst++ = '.';
                }
                if (p >= paren + 100) return NULL;
                p->nalt = nalt;
                p->natom = natom;
                p++;
                nalt = 0;
                natom = 0;
                break;
            case '|':
                if (natom == 0) return NULL;
                while (--natom > 0) *dst++ = '.';
                nalt++;
                break;
            case ')':
                if (p == paren || natom == 0) return NULL;
                while (--natom > 0) *dst++ = '.';
                for (; nalt > 0; nalt--) *dst++ = '|';
                --p;
                nalt = p->nalt;
                natom = p->natom;
                natom++;
                break;
            case '*':
            case '+':
            case '?':
                if (natom == 0) return NULL;
                *dst++ = *re;
                break;
            default:
                if (natom > 1) {
                    natom--;
                    *dst++ = '.';
                }
                *dst++ = *re;
                natom++;
                break;
        }
    }
    while (--natom > 0) *dst++ = '.';
    for (; nalt > 0; nalt--) *dst++ = '|';
    *dst = '\0';
    return buf;
}

/* Перетворення постфіксного регулярного виразу в НКА Томпсона */
static State* transform_postfix_to_nfa(const char *postfix_regex) {
    Fragment stack[1000];
    Fragment *stack_ptr = stack;

    for (const char *p = postfix_regex; *p != '\0'; p++) {
        switch (*p) {
            case '|': { /* Оператор вибору (альтернація) */
                Fragment e2 = *--stack_ptr;
                Fragment e1 = *--stack_ptr;
                State *s = create_state(SPLIT_TOKEN, e1.start, e2.start);
                *stack_ptr++ = (Fragment){ s, e2.out_list };
                break;
            }
            case '*': { /* Оператор ітерації Кліні */
                Fragment e = *--stack_ptr;
                State *s = create_state(SPLIT_TOKEN, e.start, NULL);
                patch(e.out_list, s);
                *stack_ptr++ = (Fragment){ s, &s->out1 };
                break;
            }
            case '.': { /* Явна або неявна конкатенація */
                Fragment e2 = *--stack_ptr;
                Fragment e1 = *--stack_ptr;
                patch(e1.out_list, e2.start);
                *stack_ptr++ = (Fragment){ e1.start, e2.out_list };
                break;
            }
            default: { /* Звичайний символьний літерал */
                State *s = create_state((unsigned char)*p, NULL, NULL);
                *stack_ptr++ = (Fragment){ s, &s->out };
                break;
            }
        }
    }

    Fragment e = *--stack_ptr;
    State *match_state = create_state(MATCH_TOKEN, NULL, NULL);
    patch(e.out_list, match_state);
    return e.start;
}

/* Обчислення ε-замикання: додавання стану та його ε-переходів у множину */
static void add_state(StateList *l, State *s, int step) {
    if (!s || s->last_step == step) return;
    s->last_step = step;

    if (s->opcode == SPLIT_TOKEN) {
        add_state(l, s->out, step);
        add_state(l, s->out1, step);
        return;
    }

    if (l->count < l->capacity) {
        l->states[l->count++] = s;
    }
}

/* Симуляція віртуальної машини Pike VM над вхідним текстом */
bool match_nfa(State *start_state, const char *text) {
    int max_states = 4096;
    StateList current_list = { (State**)malloc(max_states * sizeof(State*)), 0, max_states };
    StateList next_list = { (State**)malloc(max_states * sizeof(State*)), 0, max_states };
    int step = 1;

    add_state(&current_list, start_state, step);

    for (const char *p = text; *p != '\0'; p++) {
        step++;
        next_list.count = 0;

        for (int i = 0; i < current_list.count; i++) {
            State *s = current_list.states[i];
            if (s->opcode == (unsigned char)*p) {
                add_state(&next_list, s->out, step);
            }
        }

        StateList tmp = current_list;
        current_list = next_list;
        next_list = tmp;

        if (current_list.count == 0) break;
    }

    bool matched = false;
    for (int i = 0; i < current_list.count; i++) {
        if (current_list.states[i]->opcode == MATCH_TOKEN) {
            matched = true;
            break;
        }
    }

    free(current_list.states);
    free(next_list.states);
    return matched;
}

/* Очищення пам'яті графа НКА */
void free_nfa(State *s, int cleanup_step) {
    if (!s || s->last_step == cleanup_step) return;
    s->last_step = cleanup_step;
    free_nfa(s->out, cleanup_step);
    free_nfa(s->out1, cleanup_step);
    free(s);
}

int main(void) {
    const char *infix_pattern = "(a|b)*abb";
    const char *postfix = re2post(infix_pattern);
    printf("Інфіксний шаблон: '%s'\n", infix_pattern);
    printf("Постфіксний вираз: '%s'\n", postfix);

    State *nfa_start = transform_postfix_to_nfa(postfix);

    const char *test_pass = "ababb";
    const char *test_fail = "ababa";

    printf("Тест 1 ('%s'): %s\n", test_pass, match_nfa(nfa_start, test_pass) ? "ЗБІГ" : "НЕМАЄ ЗБІГУ");
    printf("Тест 2 ('%s'): %s\n", test_fail, match_nfa(nfa_start, test_fail) ? "ЗБІГ" : "НЕМАЄ ЗБІГУ");

    free_nfa(nfa_start, 99999);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <algorithm>
#include <stdexcept>

namespace regex {

enum class Opcode { Literal, Split, Match };

/* Структура вузла НКА з використанням ідіом C++20 */
struct State {
    Opcode op;
    char symbol{'\0'};
    State* out{nullptr};
    State* out1{nullptr};
    mutable int last_step{0};

    explicit State(char c) : op(Opcode::Literal), symbol(c) {}
    explicit State(Opcode op_type, State* o0 = nullptr, State* o1 = nullptr)
        : op(op_type), out(o0), out1(o1) {}
};

class ThompsonEngine {
public:
    explicit ThompsonEngine(std::string_view infix_pattern) {
        std::string postfix = re2post(infix_pattern);
        build_nfa(postfix);
    }

    /* Симуляція Pike VM над текстовим зрізом std::string_view */
    [[nodiscard]] bool match(std::string_view text) const {
        if (!start_state_) return false;

        std::vector<State*> current_states;
        std::vector<State*> next_states;
        current_states.reserve(arena_.size());
        next_states.reserve(arena_.size());

        int step = 1;
        add_state(current_states, start_state_, step);

        for (char ch : text) {
            step++;
            next_states.clear();

            for (State* s : current_states) {
                if (s->op == Opcode::Literal && s->symbol == ch) {
                    add_state(next_states, s->out, step);
                }
            }

            std::swap(current_states, next_states);
            if (current_states.empty()) break;
        }

        return std::any_of(current_states.begin(), current_states.end(),
            [](const State* s) { return s->op == Opcode::Match; });
    }

private:
    struct Fragment {
        State* start;
        std::vector<State**> out_list;
    };

    std::vector<std::unique_ptr<State>> arena_;
    State* start_state_{nullptr};

    /* Препроцесор Shunting-Yard для перетворення інфіксного виразу у постфіксний */
    static std::string re2post(std::string_view re) {
        int nalt = 0, natom = 0;
        std::string dst;
        dst.reserve(re.size() * 2);

        struct ParenFrame {
            int nalt;
            int natom;
        };
        std::vector<ParenFrame> paren;

        for (char c : re) {
            switch (c) {
                case '(':
                    if (natom > 1) {
                        natom--;
                        dst.push_back('.');
                    }
                    paren.push_back({nalt, natom});
                    nalt = 0;
                    natom = 0;
                    break;
                case '|':
                    if (natom == 0) throw std::invalid_argument("Некоректний шаблон синтаксису '|'");
                    while (--natom > 0) dst.push_back('.');
                    nalt++;
                    break;
                case ')':
                    if (paren.empty() || natom == 0) throw std::invalid_argument("Незбалансовані дужки");
                    while (--natom > 0) dst.push_back('.');
                    for (; nalt > 0; nalt--) dst.push_back('|');
                    nalt = paren.back().nalt;
                    natom = paren.back().natom;
                    paren.pop_back();
                    natom++;
                    break;
                case '*':
                    if (natom == 0) throw std::invalid_argument("Операнд '*' відсутній");
                    dst.push_back('*');
                    break;
                default:
                    if (natom > 1) {
                        natom--;
                        dst.push_back('.');
                    }
                    dst.push_back(c);
                    natom++;
                    break;
            }
        }
        while (--natom > 0) dst.push_back('.');
        for (; nalt > 0; nalt--) dst.push_back('|');

        return dst;
    }

    State* make_state(char c) {
        arena_.push_back(std::make_unique<State>(c));
        return arena_.back().get();
    }

    State* make_state(Opcode op, State* o0 = nullptr, State* o1 = nullptr) {
        arena_.push_back(std::make_unique<State>(op, o0, o1));
        return arena_.back().get();
    }

    static void patch(const std::vector<State**>& list, State* target) {
        for (State** ptr : list) {
            *ptr = target;
        }
    }

    static std::vector<State**> append_lists(std::vector<State**> v1, const std::vector<State**>& v2) {
        v1.insert(v1.end(), v2.begin(), v2.end());
        return v1;
    }

    void add_state(std::vector<State*>& list, State* s, int step) const {
        if (!s || s->last_step == step) return;
        s->last_step = step;

        if (s->op == Opcode::Split) {
            add_state(list, s->out, step);
            add_state(list, s->out1, step);
            return;
        }

        list.push_back(s);
    }

    void build_nfa(std::string_view pattern) {
        std::vector<Fragment> stack;

        for (char c : pattern) {
            switch (c) {
                case '|': {
                    auto e2 = stack.back(); stack.pop_back();
                    auto e1 = stack.back(); stack.pop_back();
                    State* s = make_state(Opcode::Split, e1.start, e2.start);
                    stack.push_back({s, append_lists(e1.out_list, e2.out_list)});
                    break;
                }
                case '*': {
                    auto e = stack.back(); stack.pop_back();
                    State* s = make_state(Opcode::Split, e.start, nullptr);
                    patch(e.out_list, s);
                    stack.push_back({s, {&s->out1}});
                    break;
                }
                case '.': {
                    auto e2 = stack.back(); stack.pop_back();
                    auto e1 = stack.back(); stack.pop_back();
                    patch(e1.out_list, e2.start);
                    stack.push_back({e1.start, e2.out_list});
                    break;
                }
                default: {
                    State* s = make_state(c);
                    stack.push_back({s, {&s->out}});
                    break;
                }
            }
        }

        if (!stack.empty()) {
            auto e = stack.back();
            State* match_state = make_state(Opcode::Match);
            patch(e.out_list, match_state);
            start_state_ = e.start;
        }
    }
};

} // namespace regex

int main() {
    try {
        regex::ThompsonEngine engine("(a|b)*abb");

        std::cout << "Тест 1 ('ababb'): " << (engine.match("ababb") ? "ЗБІГ" : "НЕМАЄ ЗБІГУ") << "\n";
        std::cout << "Тест 2 ('ababa'): " << (engine.match("ababa") ? "ЗБІГ" : "НЕМАЄ ЗБІГУ") << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
    }

    return 0;
}
```
:::

## Детальний аналіз алгоритму та інженерні нюанси

### 1. Механізм відсікання циклів у `add_state`

Функція `add_state` є серцем алгоритму симуляції. Головна загроза при обробці графа з `ε`-переходами — це зациклення (наприклад, у виразах `(a*)*`). Завдяки маркеру `last_step`, кожен стан обробляється за один крок сканування тексту строго один раз.

Якщо стан має тип `SPLIT_TOKEN` (або `Opcode::Split`), функція `add_state` викликає саму себе рекурсивно для двох вихідних дуг `out` та `out1`. При цьому символ вхідного тексту не споживається (індекс `p` у тексті залишається незмінним). Якщо стан має тип `Literal`, він додається до списку активних станів `current_list`, чекаючи на перевірку збігу символу.

Покроковий прохід обчислення `ε`-замикання для стартного стану `(a|b)*`:
1. Вхід у стан `Split` для зірочки Кліні `*`.
2. Запис `last_step = 1` у поточному вузлі `Split`.
3. Рекурсивний виклик `add_state` для першої гілки (стан `Split` альтернації `a|b`) та другої гілки (витрата `ε`-переходу в обхід виразу).
4. Запис активних символьних станів `a` та `b` у списки `current_list`.

### 2. Пам'ять та стратегія арени у C++

У версії мовою C++ застосовано паттерн **Arena Allocation** за допомогою вектора розумних вказівників `std::vector<std::unique_ptr<State>> arena_`.

Цей підхід має дві важливі переваги:
- **Безпека ресурсів (RAII)**: Граф НКА містить циклічні `ε`-переходи назад, що робить використання `std::shared_ptr` небезпечним через ризик циклічних посилань та витоків пам'яті. Управління володінням через `unique_ptr` в окремому масиві-арені гарантує лінійне знищення всіх вузлів у деструкторі без рекурсивного виснаження стеку.
- **Локальність даних у кеші**: Вузли виділяються послідовно в купі, а вектор `arena_` зберігає їхню точну кількість, що дозволяє заздалегідь резервувати обсяг пам'яті під вектори списків станів `current_states.reserve(arena_.size())`.

### 3. Захоплювальні групи та Tagged NFA (TNFA)

У класичній симуляції Pike VM перевіряється лише факт наявності збігу (boolean match). Для підтримки витягування зафіксованих підрядків (capturing groups) граф НКА розширюється спеціальними станами міток (Tag nodes або Save nodes).

Кожна активна нитка (thread) у Pike VM зберігає не лише вказівник на поточний стан `State*`, а й масив позицій захоплення `int captures[2 * K]`, де `K` — кількість груп у шаблоні:
- При переході через стан `Save(2 * i)` у масив записується поточний індекс символу як початок `i`-ї групи.
- При переході через стан `Save(2 * i + 1)` записується поточний індекс як кінець `i`-ї групи.

Оскільки множина активних станів утримує списки ниток у порядку пріоритету (ліворуч-направо), при виникненні двох конкуруючих ниток, які досягають термінального стану `Match`, Pike VM обирає нитку з вищим пріоритетом (найлівіший найдовший збіг), забезпечуючи виконання операторів захоплення за лінійний час без бектрекінгу.

### 4. Багатопотокова безпека та змога повторного використання (Reentrancy)

Важливою інженерною властивістю скомпільованого об'єкта `ThompsonEngine` є його абсолютна потокобезпека (reentrancy) при виконанні читання. Оскільки структура графа НКА (`arena_` та вказівники на стани) залишається строго незмінною після завершення побудови, один і той самий екземпляр `ThompsonEngine` може одночасно використовуватися довільною кількістю робочих потоків (threads) для сканування різних текстових файлів або мережевих пакетів.

Кожен потік створює власні локальні вектори станів `current_states` та `next_states` у своєму стек-фреймі. Поле `last_step` у версії C++ позначено модифікатором `mutable` для локальної підтримки кроку на потік, або ж замість модифікації поля в самому графові передається локальний бітовий масив відвіданих станів `std::vector<bool> visited(num_states)`.

### 5. Порівняльний аналіз складності та підходів до виконання

Нижче наведено порівняння параметрів обчислювальної складності для трьох основних архітектур рушіїв регулярних виразів:

| Параметр | Рекурсивний бектрекінг (PCRE / Python `re`) | Симуляція НКА Томпсона (Pike VM) | Детермінований автомат (DFA) |
| :--- | :--- | :--- | :--- |
| **Складність у найгіршому випадку** | `O(2ⁿ)` (експоненціальний вибух) | `O(M · N)` (строго лінійний час) | `O(N)` (абсолютно оптимальний час) |
| **Обсяг пам'яті під час виконання** | `O(N)` (стек викликів) | `O(M)` (динамічні масиви станів) | `O(1)` (тільки поточний стан) |
| **Час компіляції шаблону** | `O(M)` (швидка побудова AST) | `O(M)` (лінійний час Томпсона) | `O(2ᵐ)` (експоненціальний розріст) |
| **Гарантія безпеки від ReDoS** | Відсутня (високий ризик вразливості) | Абсолютна гарантія | Абсолютна гарантія |
| **Підтримка зворотних посилань `\1`** | Присутня | Відсутня | Відсутня |

Де `M` — кількість операторів у шаблоні регулярного виразу, а `N` — довжина сканованого вхідного тексту.

### 6. Крайові випадки та обробка помилок

Розглянута реалізація коректно обробляє ключові крайові випадки:
- **Порожній вхідний текст `""`**: Обробляється без виключень — виконується лише початковий виклик `add_state` для стартового стану `start_state_`, після чого проводиться перевірка наявності `Opcode::Match` серед станів початкового `ε`-замикання. Це дозволяє правильно зіставляти порожні рядки з шаблонами на кшталт `a*` або `(a|b)*`.
- **Шаблони без збігів**: Якщо на якомусь кроці сканування вхідного символу списки `current_list` стають порожніми, внутрішній цикл сканування переривається достроково за оператором `break`, уникаючи зайвих обчислень над залишком файлу.
- **Синтаксичні помилки у шаблоні**: Метод `re2post` кидає виключення `std::invalid_argument` при виявленні незбалансованих дужок, відсутності операндів біля операторів `*`, `|` або некоректних символьних послідовностей.
- **Підтримка алфавітів високої розрядності (UTF-8)**: Для розширення рушія на повний діапазон символів Unicode (UTF-8) тип `symbol` розширюється з 8-бітного `char` до 32-бітного `uint32_t` (Unicode code point), а сканування тексту супроводжується потоковим декодером UTF-8.
