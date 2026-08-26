# ⚙️ Емуляція апаратного автомата: повентильна перевірка на C та C++

Збирання цифрового автомата на дискретній логіці 74-ї серії без попередньої верифікації — надійний спосіб витратити години на пошук помилково підключеного виводу, переплутаної інверсії або непоміченого статичного ризику на макетній платі. На відміну від мікроконтролера, де помилку в алгоритмі виправляють зміною рядка коду й новим прошиванням, у залізній схемі будь-який промах у рівняннях збудження вимагає перепаювання дротів, заміни корпусів мікросхем чи навіть повторного виготовлення друкованої плати.

Програмна емуляція дискретного автомата дає змогу перевірити логічні рівняння збудження тригерів на всіх можливих комбінаціях входів і станів ще до того, як буде ввімкнено паяльник чи нарізано перемички для безпайкової макетної плати. 

У цій практичній роботі до статті [Логіка без процесора: збираємо автомат](root:embedded/lohika-bez-protsesora) реалізовано повноцінну дворівневу модель верифікації чотирифазного контролера безпеки пальника:
1. **Еталонний алгоритмічний автомат (Golden Model)** — високорівнева модель поведінки на базі станів переліку `enum`, яка реалізує чистий алгоритм роботи системи за стандартом безпеки.
2. **Повентильний емулятор схеми (Gate-Level Netlist)** — точне моделювання булевих рівнянь входів `D1`, `D0` тригерів 74HC74 та комбінаційних виходів Мура (`Fan`, `Valve`, `Spark`, `Ok`), синтезованих через карти Карно.

Емулятор генерує послідовність випробувальних тестових векторів, моделює дискретні тактові фронти годинника `CLK` і здійснює такт за тактом строгу перевірку тверджень (`assert`), контролюючи повний збіг внутрішніх станів та вихідних керувальних ліній.

### Принцип дворівневої верифікації та моделювання дискретного часу

У цифровій схемотехніці перевірка логіки через «золоту модель» є стандартом індустрії (як при проектуванні ASIC, так і при складанні дискретних плат). Процес моделювання розбивається на дві фази всередині кожного тактового циклу:

* **Фаза 1: Комбінаційне розповсюдження (Propagation Phase)**.
  На основі поточних виходів тригерів `Q1`, `Q0` та зовнішніх вхідних ліній (`Start`, `Done`, `Flame`, `Abort`) обчислюються значення булевих функцій наступного стану `D1`, `D0` та виходів Мура. У реальному залізі цей процес займає час затримки поширення сигналу крізь вентилі `t_pd` (близько 15–25 нс для суми двох рівнів логіки 74HC08 та 74HC32). У коді це відповідає обчисленню булевих виразів без зміни поточного стану тригерів.
* **Фаза 2: Тактовий фронт і фіксація (Clock Edge & Latch)**.
  На активному (додатному) фронті тактового сигналу `CLK` обчислені значення `D1` та `D0` записуються в бістабільні комірки D-тригерів 74HC74. Значення `Q1` та `Q0` оновлюються, стаючи вихідними даними для наступного такту.

Такий поділ усуває ефект гонки сигналів у симуляторі: значення наступного стану обчислюються строго на базі старого стану до того, як тригери змінять свої виходи.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

/* Кодування станів автомата */
typedef enum {
    STATE_IDLE   = 0, /* 00: Очікування */
    STATE_PURGE  = 1, /* 01: Продування камери */
    STATE_IGNITE = 2, /* 10: Розпал та перевірка полум'я */
    STATE_RUN    = 3  /* 11: Штатна робота */
} fsm_state_t;

/* Вхідні сигнали автомата */
typedef struct {
    bool start; /* Кнопка пуску */
    bool done;  /* Сигнал завершення продувки від таймера */
    bool flame; /* Оптичний давач наявності полум'я */
    bool abort; /* Аварійний стоп / скидання */
} fsm_inputs_t;

/* Вихідні силові сигнали моделі Мура */
typedef struct {
    bool fan;   /* Вентилятор примусової тяги */
    bool valve; /* Електромагнітний клапан газу */
    bool spark; /* Високовольтний запальник */
    bool ok;    /* Індикатор нормальної роботи */
} fsm_outputs_t;

/* -------------------------------------------------------------
 * 1. Високорівнева еталонна модель (Golden Model)
 * ------------------------------------------------------------- */
typedef struct {
    fsm_state_t state;
} golden_fsm_t;

void golden_fsm_init(golden_fsm_t *fsm) {
    fsm->state = STATE_IDLE;
}

fsm_outputs_t golden_fsm_get_outputs(const golden_fsm_t *fsm) {
    fsm_outputs_t out = {0};
    switch (fsm->state) {
        case STATE_IDLE:
            out.fan = false; out.valve = false; out.spark = false; out.ok = false;
            break;
        case STATE_PURGE:
            out.fan = true;  out.valve = false; out.spark = false; out.ok = false;
            break;
        case STATE_IGNITE:
            out.fan = true;  out.valve = true;  out.spark = true;  out.ok = false;
            break;
        case STATE_RUN:
            out.fan = true;  out.valve = true;  out.spark = false; out.ok = true;
            break;
    }
    return out;
}

void golden_fsm_tick(golden_fsm_t *fsm, fsm_inputs_t in) {
    if (in.abort) {
        fsm->state = STATE_IDLE;
        return;
    }
    switch (fsm->state) {
        case STATE_IDLE:
            if (in.start) fsm->state = STATE_PURGE;
            break;
        case STATE_PURGE:
            if (in.done) fsm->state = STATE_IGNITE;
            break;
        case STATE_IGNITE:
            if (in.flame) fsm->state = STATE_RUN;
            else fsm->state = STATE_IDLE; /* Зрив запалювання */
            break;
        case STATE_RUN:
            if (!in.flame) fsm->state = STATE_IDLE; /* Згасання полум'я */
            break;
    }
}

/* -------------------------------------------------------------
 * 2. Повентильний емулятор дискретної схеми 74HC
 * ------------------------------------------------------------- */
typedef struct {
    bool q1; /* Старший D-тригер (IC1B) */
    bool q0; /* Молодший D-тригер (IC1A) */
} discrete_fsm_t;

void discrete_fsm_init(discrete_fsm_t *fsm) {
    fsm->q1 = false;
    fsm->q0 = false;
}

fsm_outputs_t discrete_fsm_get_outputs(const discrete_fsm_t *fsm) {
    fsm_outputs_t out;
    /* Дешифратор виходів Мура на вентилях:
     * Fan   = Q1 OR Q0
     * Valve = Q1
     * Spark = Q1 AND NOT(Q0)
     * Ok    = Q1 AND Q0
     */
    out.fan   = fsm->q1 || fsm->q0;
    out.valve = fsm->q1;
    out.spark = fsm->q1 && !fsm->q0;
    out.ok    = fsm->q1 && fsm->q0;
    return out;
}

void discrete_fsm_tick(discrete_fsm_t *fsm, fsm_inputs_t in) {
    bool q1 = fsm->q1;
    bool q0 = fsm->q0;

    /* Рівняння комбінаційної логіки наступного стану:
     * D1 = (NOT(Q1) AND Q0 AND Done) OR (Q1 AND Flame AND NOT(Abort))
     * D0 = (NOT(Q1) AND NOT(Q0) AND Start AND NOT(Abort)) OR
     *      (NOT(Q1) AND Q0 AND NOT(Done) AND NOT(Abort)) OR
     *      (Q1 AND NOT(Q0) AND Flame AND NOT(Abort))
     */
    bool d1 = (!q1 && q0 && in.done && !in.abort) ||
              (q1 && in.flame && !in.abort);

    bool d0 = (!q1 && !q0 && in.start && !in.abort) ||
              (!q1 && q0 && !in.done && !in.abort) ||
              (q1 && !q0 && in.flame && !in.abort);

    /* Тактовий фронт: засувка в D-тригери 74HC74 */
    fsm->q1 = d1;
    fsm->q0 = d0;
}

/* -------------------------------------------------------------
 * 3. Тестова верифікація та порівняння такт за тактом
 * ------------------------------------------------------------- */
int main(void) {
    golden_fsm_t golden;
    discrete_fsm_t discrete;

    golden_fsm_init(&golden);
    discrete_fsm_init(&discrete);

    /* Тестовий сценарій: успішний пуск -> робота -> аварійний зрив полум'я */
    fsm_inputs_t test_vectors[] = {
        { .start = false, .done = false, .flame = false, .abort = false }, /* Такт 0: IDLE */
        { .start = true,  .done = false, .flame = false, .abort = false }, /* Такт 1: Пуск -> PURGE */
        { .start = false, .done = false, .flame = false, .abort = false }, /* Такт 2: Продувка триває */
        { .start = false, .done = true,  .flame = false, .abort = false }, /* Такт 3: Продувка завершена -> IGNITE */
        { .start = false, .done = false, .flame = true,  .abort = false }, /* Такт 4: Полум'я є -> RUN */
        { .start = false, .done = false, .flame = true,  .abort = false }, /* Такт 5: Стабільна робота */
        { .start = false, .done = false, .flame = false, .abort = false }, /* Такт 6: Згасання полум'я -> IDLE */
        { .start = false, .done = false, .flame = false, .abort = false }  /* Такт 7: Повернення в IDLE */
    };

    size_t num_steps = sizeof(test_vectors) / sizeof(test_vectors[0]);

    for (size_t step = 0; step < num_steps; ++step) {
        fsm_inputs_t in = test_vectors[step];

        fsm_outputs_t out_g = golden_fsm_get_outputs(&golden);
        fsm_outputs_t out_d = discrete_fsm_get_outputs(&discrete);

        uint8_t state_d = (discrete.q1 ? 2 : 0) | (discrete.q0 ? 1 : 0);

        /* Перевірка повної відповідності стану та виходів */
        assert((uint8_t)golden.state == state_d);
        assert(out_g.fan == out_d.fan);
        assert(out_g.valve == out_d.valve);
        assert(out_g.spark == out_d.spark);
        assert(out_g.ok == out_d.ok);

        /* Такт годинника */
        golden_fsm_tick(&golden, in);
        discrete_fsm_tick(&discrete, in);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <string_view>
#include <cstdint>
#include <cassert>

enum class FsmState : uint8_t {
    Idle   = 0b00,
    Purge  = 0b01,
    Ignite = 0b10,
    Run    = 0b11
};

struct FsmInputs {
    bool start{false};
    bool done{false};
    bool flame{false};
    bool abort{false};
};

struct FsmOutputs {
    bool fan{false};
    bool valve{false};
    bool spark{false};
    bool ok{false};

    [[nodiscard]] constexpr bool operator==(const FsmOutputs &other) const noexcept = default;
};

// -------------------------------------------------------------
// 1. Еталонна поведінкова модель (Golden Model)
// -------------------------------------------------------------
class GoldenFsm {
public:
    constexpr GoldenFsm() noexcept : state_{FsmState::Idle} {}

    [[nodiscard]] constexpr FsmState state() const noexcept { return state_; }

    [[nodiscard]] constexpr FsmOutputs outputs() const noexcept {
        switch (state_) {
            case FsmState::Idle:   return {.fan = false, .valve = false, .spark = false, .ok = false};
            case FsmState::Purge:  return {.fan = true,  .valve = false, .spark = false, .ok = false};
            case FsmState::Ignite: return {.fan = true,  .valve = true,  .spark = true,  .ok = false};
            case FsmState::Run:    return {.fan = true,  .valve = true,  .spark = false, .ok = true};
        }
        return {};
    }

    constexpr void tick(const FsmInputs &in) noexcept {
        if (in.abort) {
            state_ = FsmState::Idle;
            return;
        }
        switch (state_) {
            case FsmState::Idle:
                if (in.start) state_ = FsmState::Purge;
                break;
            case FsmState::Purge:
                if (in.done) state_ = FsmState::Ignite;
                break;
            case FsmState::Ignite:
                state_ = in.flame ? FsmState::Run : FsmState::Idle;
                break;
            case FsmState::Run:
                if (!in.flame) state_ = FsmState::Idle;
                break;
        }
    }

private:
    FsmState state_;
};

// -------------------------------------------------------------
// 2. Повентильний емулятор схеми 74HC
// -------------------------------------------------------------
class DiscreteLogicFsm {
public:
    constexpr DiscreteLogicFsm() noexcept : q1_{false}, q0_{false} {}

    [[nodiscard]] constexpr uint8_t raw_state() const noexcept {
        return static_cast<uint8_t>((q1_ ? 0b10 : 0b00) | (q0_ ? 0b01 : 0b00));
    }

    [[nodiscard]] constexpr FsmOutputs outputs() const noexcept {
        return {
            .fan   = q1_ || q0_,
            .valve = q1_,
            .spark = q1_ && !q0_,
            .ok    = q1_ && q0_
        };
    }

    constexpr void tick(const FsmInputs &in) noexcept {
        // Обчислення булевих функцій наступного стану
        const bool d1 = (!q1_ && q0_ && in.done && !in.abort) ||
                        (q1_ && in.flame && !in.abort);

        const bool d0 = (!q1_ && !q0_ && in.start && !in.abort) ||
                        (!q1_ && q0_ && !in.done && !in.abort) ||
                        (q1_ && !q0_ && in.flame && !in.abort);

        // Фіксація по тактовому фронту
        q1_ = d1;
        q0_ = d0;
    }

private:
    bool q1_;
    bool q0_;
};

// -------------------------------------------------------------
// 3. Тестова верифікація обох моделей
// -------------------------------------------------------------
int main() {
    GoldenFsm golden;
    DiscreteLogicFsm discrete;

    constexpr std::array<FsmInputs, 8> test_sequence{{
        {.start = false, .done = false, .flame = false, .abort = false},
        {.start = true,  .done = false, .flame = false, .abort = false},
        {.start = false, .done = false, .flame = false, .abort = false},
        {.start = false, .done = true,  .flame = false, .abort = false},
        {.start = false, .done = false, .flame = true,  .abort = false},
        {.start = false, .done = false, .flame = true,  .abort = false},
        {.start = false, .done = false, .flame = false, .abort = false},
        {.start = false, .done = false, .flame = false, .abort = false}
    }};

    for (const auto &inputs : test_sequence) {
        assert(static_cast<uint8_t>(golden.state()) == discrete.raw_state());
        assert(golden.outputs() == discrete.outputs());

        golden.tick(inputs);
        discrete.tick(inputs);
    }

    return 0;
}
```
:::

### Методика налагодження та перенесення на макетну плату

Коли програмна модель підтвердила коректність логічних рівнянь, переходять до складання макетного зразка на базі мікросхем серії 74HC. При цьому в лабораторії виникають типові розбіжності між ідеальною цифровою симуляцією та фізичною реальністю:

1. **Невикористані входи мікросхем КМОН (Floating Inputs)**:
   У симуляторі C/C++ неініціалізовані чи вільні змінні зануляються або набувають явного логічного значення. У реальних кремнієвих чипах 74HC ізольований затвор польового транзистора має ємність близько 3–5 пФ і опір витоку понад 1 тераом (`10¹² Ом`). Якщо вільний логічний елемент мікросхеми 74HC08 чи 74HC32 залишити у повітрі, він діє як антена: накопичує статичний заряд і плаває навколо порогу `VCC/2`. При цьому обидва транзистори інвертора відкриваються одночасно, породжуючи струм наскрізного пробою в кілька міліампер, що нагріває чип і вносить паразитні пульсації в шину живлення. **Правило:** усі вільні входи мікросхем 74HC обов'язково підключаються до `GND` або `VCC`.
2. **Антибрязкіт механічних контактів (Switch Debounce)**:
   У коді тестовий вектор змінює прапорець `start` з `false` на `true` за один крок дискретного часу. Фізична кнопка при замиканні вібрує протягом 5–20 мілісекунд, створюючи десятки мікроімпульсів. Якщо кнопку завести на схему без фільтра, автомат перестрибне зі стану `IDLE` у `PURGE`, а наступні відскоки кнопки можуть бути помилково інтерпретовані як інші сигнали. Тому на вході схеми обов'язково встановлюється інтегрувальний RC-ланцюг (`R = 10 кОм`, `C = 100 нФ`) із тригером Шмітта 74HC14.
3. **Локальне блокування живлення (Decoupling Capacitors)**:
   У момент зміни стану тригерів 74HC74 струм споживання мікросхеми підскакує на кілька десятків міліампер протягом 2–3 наносекунд. Індуктивність довгих з'єднувальних дротів макетної плати призводить до короткочасного просідання напруги на виводі живлення (англ. *VCC droop*). Це просідання може викликати спонтанне скидання сусіднього тригера. Для стабільної роботи безпосередньо біля кожного корпусу IC (між ніжками живлення та землі) встановлюється керамічний конденсатор ємністю 100 нФ.
4. **Покроковий ручний генератор такту для тестування**:
   Для перевірки роботи схеми на столі часто зручно замінити автоматичний генератор на 1 Гц ручною тактовою кнопкою «Step». У такому разі кнопка «Step» також обов'язково оснащується апаратною RS-засувкою на двох елементах 74HC00 або RC-фільтром з інвертором Шмітта 74HC14, щоб кожне натискання генерувало рівно один чистий тактовий фронт для тригерів 74HC74.
