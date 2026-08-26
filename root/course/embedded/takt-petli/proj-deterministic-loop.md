# ⚙️ Детермінований контур керування: таймер, АЦП та ШІМ без блокувань

Цей проєкт демонструє повну практичну реалізацію високочастотного (20 кГц) контуру керування струмом і швидкістю електромеханічного приводу без участі операційної системи RTOS у критичному шляху: апаратний запуск АЦП за подією таймера TRGO, обчислення дискретного ПІД-регулятора в перериванні без блокувань та передача телеметрії у фоновий потік через неблокуючий lock-free буфер.

---

### Архітектура конвеєра з нульовим джитером

Щоб повністю усунути програмний джитер і мінімізувати затримку транспорту, тракт керування розбивається на чотири строго синхронізовані апаратні етапи:

```
[Таймер TIM1: Center-Aligned PWM] 
       │ (подія TRGO на верхівці рахунку)
       ▼
[АЦП Dual SAR: Одночасна вибірка фазних струмів]
       │ (переривання EOC через 1.2 мкс)
       ▼
[Обробник ISR: Розрахунок ПІД + Clamping Anti-Windup]
       │ (запис у тіньовий регістр TIM1->CCR1)
       ▼
[Оновлення ШІМ на дні рахунку лічильника]
```

1. **Тактовий генератор контуру (Master Timer):** Таймер `TIM1` працює в режимі симетричного ШІМ (Center-Aligned PWM Mode 1) на частоті 20 кГц (`Ts = 50 мкс`). Під час проходження лічильника через нуль або верхівку таймер генерує імпульс `TRGO` (Trigger Output). Цей сигнал поширюється внутрішньою матрицею периферії без залучення ядра CPU.
2. **Апаратна вибірка (Hardware-Triggered Sampling):** Подія `TRGO` безпосередньо запускає регулярне перетворення двох незалежних блоків АЦП (`ADC1` та `ADC2`). Обидва канали одночасно захоплюють напругу з вимірювальних шунтів фаз двигуна. Процесор у цей час може виконувати фонові задачі або перебувати в режимі енергозбереження.
3. **Обчислення в прецизійному ISR (Zero-Jitter Control):** Завершення конверсії активує переривання `ADC_IRQHandler` із найвищим пріоритетом NVIC 0. Обробник зчитує 12-бітні значення, розраховує дискретний ПІД із фільтром D-складової та захистом від інтегрального насичення (anti-windup clamping) і оновлює буферизований регістр порівняння `TIM1->CCR1`.
4. **Неблокуюча телеметрія (Lock-Free Telemetry):** Зріз поточного стану (уставка, виміряне значення, шпаруватість, часова мітка) записується в кільцеву безблокувальну чергу (SPSC Ring Buffer), яку вичитує низькопріоритетна задача FreeRTOS для логування по шинах CAN, UART або Ethernet.

---

### Детальна конфігурація периферії, імпеданс АЦП та часовий бюджет

#### 1. Розрахунок часу вибірки АЦП (Sample Time)
Вхідний каскад SAR-АЦП містить ключ комутації та внутрішню ємність пристрою вибірки-зберігання `C_sample ≈ 4..8 пФ`. Щоб напруга на конденсаторі встигла зарядитися до значення вхідного сигналу з точністю 12-бітного квантування (похибка менше `0.5 LSB` або `1 / 8192`), тривалість фази вибірки `T_sample` повинна задовольняти умову перехідного процесу RC-ланцюга:

```
T_sample ≥ (R_source + R_switch) · C_sample · ln(2^(N+1))
T_sample ≥ (R_source + R_switch) · C_sample · 9.01
```

Для вимірювального підсилювача з вихідним опором `R_source = 100 Ом` та опором ключа `R_switch = 1 кОм` мінімальний час вибірки становить:

```
T_sample_min = (100 + 1000) · 8·10^(−12) · 9.01 ≈ 79.3 нс
```

У конфігурації регістра `ADC_SMPR` встановлюється значення `3 cycles` при тактовій частоті АЦП 36 МГц (83.3 нс), що забезпечує максимальну швидкість без динамічної похибки вимірювання.

#### 2. Тіньові регістри таймера (Preload Registers)
У регістрі керування режимом захоплення-порівняння `TIM1->CCMR1` обов'язково встановлюється біт `OC1PE` (Output Compare 1 Preload Enable). Завдяки цьому нове значення шпаруватості завантажується в активний компаратор виключно під час настання події оновлення `UEV` (Update Event). Це запобігає виникненню асиметричних імпульсів та захищає силові MOSFET-транзистори від наскрізного струму.

#### 3. Часовий бюджет обробника переривання
При тактовій частоті ядра мікроконтролера 168 МГц повний такт `Ts = 50 мкс` містить 8400 тактів CPU. Виконання апаратного входу в ISR на ядрі ARM Cortex-M4 (апаратне збереження регістрів `r0-r3, r12, lr, pc, xPSR`) займає рівно 12 тактів. Розрахунок алгоритму ПІД з плаваючою комою займає близько 300 тактів (менше 1.8 мкс), що складає лише 3.6% процесорного часу. Решта 96.4% бюджету залишаються доступними для задач операційної системи, обміну даними та призначеного для користувача інтерфейсу.

---

### Методика налагодження та вимірювання затримки осцилографом

Для фізичної верифікації детермінізму контуру на платі виділяються два діагностичні виводи GPIO:
1. **Пін `DEBUG_PIN_SAMPLE`:** Перемикається в логічну одиницю на початку обробника переривання `ADC_IRQHandler` і скидається в нуль перед виходом. Тривалість імпульсу на екрані осцилографа точно показує час виконання алгоритму `T_calc`.
2. **Пін `DEBUG_PIN_PWM_SYNC`:** Підключається до каналу синхронізації осцилографа для вимірювання інтервалу між фронтом TRGO та фактичним оновленням вихідного ШІМ-сигналу.

Якщо на осцилографі в режимі накопичення люмінофора (Infinite Persistence) спостерігається ідеально тонка лінія імпульсів без розмиття фронтів, часовий джитер контуру гарантовано дорівнює нулю.

---

### Реалізація прошивки

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define LOOP_FREQ_HZ       20000.0f
#define LOOP_DT_S          (1.0f / LOOP_FREQ_HZ)
#define SPSC_QUEUE_SIZE    64

/* Регістри та апаратні структури периферії */
typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
    volatile uint32_t RCR;
    volatile uint32_t CCR1;
    volatile uint32_t CCR2;
    volatile uint32_t CCR3;
    volatile uint32_t CCR4;
    volatile uint32_t BDTR;
} HwTimerRegisters;

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMPR1;
    volatile uint32_t SMPR2;
    volatile uint32_t DR;
} HwAdcRegisters;

/* Конфігурація та стан ПІД-регулятора */
typedef struct {
    float kp;
    float ki;
    float kd;
    float tf_d;             /* Постійна часу фільтра низьких частот для D-складової */
    float out_min;
    float out_max;

    /* Внутрішній стан накопичувачів */
    float integrator;
    float prev_meas;
    float d_filtered;
} DeterministicPid;

typedef struct {
    float target;
    float measured;
    float output;
    uint32_t timestamp_us;
} TelemetryItem;

/* Кільцевий буфер SPSC (Single-Producer Single-Consumer) */
typedef struct {
    TelemetryItem buffer[SPSC_QUEUE_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} SpscQueue;

/* Глобальні статичні екземпляри */
static DeterministicPid g_current_pid;
static SpscQueue g_telemetry_queue;

static inline void spsc_init(SpscQueue *q) {
    q->head = 0;
    q->tail = 0;
}

static inline bool spsc_push(SpscQueue *q, const TelemetryItem *item) {
    uint32_t next_head = (q->head + 1) & (SPSC_QUEUE_SIZE - 1);
    if (next_head == q->tail) {
        return false; /* Буфер заповнений, викидаємо телеметрію без блокування */
    }
    q->buffer[q->head] = *item;
    __sync_synchronize(); /* Memory barrier */
    q->head = next_head;
    return true;
}

bool spsc_pop(SpscQueue *q, TelemetryItem *item) {
    if (q->head == q->tail) {
        return false; /* Черга порожня */
    }
    *item = q->buffer[q->tail];
    __sync_synchronize();
    q->tail = (q->tail + 1) & (SPSC_QUEUE_SIZE - 1);
    return true;
}

void pid_init(DeterministicPid *pid, float kp, float ki, float kd, float tf_d, float min_val, float max_val) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->tf_d = tf_d;
    pid->out_min = min_val;
    pid->out_max = max_val;
    pid->integrator = 0.0f;
    pid->prev_meas = 0.0f;
    pid->d_filtered = 0.0f;
}

/* Швидкий неблокуючий розрахунок ПІД за фіксований крок dt */
float pid_update(DeterministicPid *pid, float setpoint, float measured, float dt) {
    float error = setpoint - measured;

    /* 1. Пропорційна складова */
    float p_term = pid->kp * error;

    /* 2. Диференційна складова від вимірюваної величини з ФНЧ (Derivative on Measurement) */
    float d_meas = (measured - pid->prev_meas) / dt;
    pid->prev_meas = measured;

    /* Фільтр першого порядку: d_filtered = d_filtered + alpha * (d_meas - d_filtered) */
    float alpha = dt / (pid->tf_d + dt);
    pid->d_filtered += alpha * (d_meas - pid->d_filtered);
    float d_term = -pid->kd * pid->d_filtered;

    /* 3. Попередній ненасичений вихід для anti-windup */
    float unsaturated_out = p_term + pid->integrator + d_term;

    /* 4. Обмеження виходу (Saturation) */
    float output = unsaturated_out;
    if (output > pid->out_max) {
        output = pid->out_max;
    } else if (output < pid->out_min) {
        output = pid->out_min;
    }

    /* 5. Умовне інтегрування (Clamping Anti-Windup) */
    bool is_saturated = (unsaturated_out != output);
    bool same_direction = ((error > 0.0f && unsaturated_out > pid->out_max) ||
                           (error < 0.0f && unsaturated_out < pid->out_min));

    if (!is_saturated || !same_direction) {
        pid->integrator += pid->ki * error * dt;
    }

    return output;
}

/* Обробник апаратного переривання АЦП найвищого пріоритету (Zero Jitter) */
void ADC1_2_IRQHandler(void) {
    HwTimerRegisters *tim1 = (HwTimerRegisters *)0x40012C00;
    HwAdcRegisters   *adc1 = (HwAdcRegisters *)0x40012000;

    /* Очищення прапорця завершення перетворення (EOC) */
    adc1->SR &= ~0x02;

    /* Зчитування 12-бітного результату струму шунта */
    uint16_t raw_adc = (uint16_t)(adc1->DR & 0x0FFF);
    float current_amps = ((float)raw_adc - 2048.0f) * (3.3f / 4096.0f) * 10.0f; /* 10 А/В */

    /* Цільовий струм із глобальної уставки */
    float target_amps = 2.5f;

    /* Обчислення регулятора (час виконання ≈ 1.8 мкс на Cortex-M4F 168 МГц) */
    float duty_cycle = pid_update(&g_current_pid, target_amps, current_amps, LOOP_DT_S);

    /* Оновлення тіньового регістра порівняння таймера ШІМ (Shadow / Preload) */
    uint32_t arr = tim1->ARR;
    uint32_t ccr_val = (uint32_t)(duty_cycle * (float)arr);
    if (ccr_val > arr) ccr_val = arr;
    tim1->CCR1 = ccr_val;

    /* Відправка телеметрії в lock-free чергу */
    TelemetryItem telem = {
        .target = target_amps,
        .measured = current_amps,
        .output = duty_cycle,
        .timestamp_us = tim1->CNT
    };
    spsc_push(&g_telemetry_queue, &telem);
}
```
```cpp
#include <cstdint>
#include <array>
#include <atomic>
#include <algorithm>
#include <span>

namespace control {

constexpr float kLoopFreqHz = 20000.0f;
constexpr float kLoopDtSec  = 1.0f / kLoopFreqHz;
constexpr size_t kQueueSize = 64;

struct TelemetryItem {
    float target{0.0f};
    float measured{0.0f};
    float output{0.0f};
    uint32_t timestamp_cnt{0};
};

template <typename T, size_t Size>
class SpscRingBuffer {
    static_assert((Size & (Size - 1)) == 0, "Розмір буфера мусить бути степенем двійки!");
public:
    constexpr SpscRingBuffer() noexcept : head_(0), tail_(0) {}

    bool push(const T& item) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t next_head = (current_head + 1) & (Size - 1);
        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; /* Буфер переповнений */
        }
        buffer_[current_head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    bool pop(T& item) noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return false; /* Черга порожня */
        }
        item = buffer_[current_tail];
        tail_.store((current_tail + 1) & (Size - 1), std::memory_order_release);
        return true;
    }

private:
    std::array<T, Size> buffer_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
};

class DeterministicPidController {
public:
    struct Config {
        float kp{1.0f};
        float ki{0.0f};
        float kd{0.0f};
        float filter_time_const{0.0005f};
        float out_min{0.0f};
        float out_max{1.0f};
    };

    explicit constexpr DeterministicPidController(const Config& cfg) noexcept
        : cfg_(cfg) {}

    void reset() noexcept {
        integrator_ = 0.0f;
        prev_meas_ = 0.0f;
        d_filtered_ = 0.0f;
    }

    [[nodiscard]] float update(float setpoint, float measured, float dt) noexcept {
        const float error = setpoint - measured;

        /* Пропорційна ланка */
        const float p_term = cfg_.kp * error;

        /* Диференційна ланка від виміру (Derivative on Measurement) */
        const float d_meas = (measured - prev_meas_) / dt;
        prev_meas_ = measured;

        const float alpha = dt / (cfg_.filter_time_const + dt);
        d_filtered_ += alpha * (d_meas - d_filtered_);
        const float d_term = -cfg_.kd * d_filtered_;

        const float unsaturated_output = p_term + integrator_ + d_term;
        const float output = std::clamp(unsaturated_output, cfg_.out_min, cfg_.out_max);

        /* Anti-windup clamping */
        const bool is_saturated = (unsaturated_output != output);
        const bool same_direction = ((error > 0.0f && unsaturated_output > cfg_.out_max) ||
                                     (error < 0.0f && unsaturated_output < cfg_.out_min));

        if (!is_saturated || !same_direction) {
            integrator_ += cfg_.ki * error * dt;
        }

        return output;
    }

private:
    Config cfg_;
    float integrator_{0.0f};
    float prev_meas_{0.0f};
    float d_filtered_{0.0f};
};

} // namespace control

/* Статичні екземпляри без динамічної пам'яті */
static control::DeterministicPidController g_current_controller({
    .kp = 0.45f,
    .ki = 120.0f,
    .kd = 0.0015f,
    .filter_time_const = 0.0002f,
    .out_min = 0.0f,
    .out_max = 0.98f
});

static control::SpscRingBuffer<control::TelemetryItem, control::kQueueSize> g_telem_queue;

extern "C" void ADC1_2_IRQHandler() {
    volatile auto* const tim1_ccr1 = reinterpret_cast<volatile uint32_t*>(0x40012C34);
    volatile auto* const tim1_arr  = reinterpret_cast<volatile uint32_t*>(0x40012C2C);
    volatile auto* const tim1_cnt  = reinterpret_cast<volatile uint32_t*>(0x40012C24);
    volatile auto* const adc1_sr   = reinterpret_cast<volatile uint32_t*>(0x40012000);
    volatile auto* const adc1_dr   = reinterpret_cast<volatile uint32_t*>(0x4001204C);

    *adc1_sr &= ~0x02; /* Очищення прапорця EOC */

    const uint16_t raw_adc = static_cast<uint16_t>(*adc1_dr & 0x0FFF);
    const float current_amps = (static_cast<float>(raw_adc) - 2048.0f) * (3.3f / 4096.0f) * 10.0f;
    constexpr float target_amps = 2.5f;

    const float duty = g_current_controller.update(target_amps, current_amps, control::kLoopDtSec);

    const uint32_t arr = *tim1_arr;
    *tim1_ccr1 = std::min(static_cast<uint32_t>(duty * static_cast<float>(arr)), arr);

    g_telem_queue.push({
        .target = target_amps,
        .measured = current_amps,
        .output = duty,
        .timestamp_cnt = *tim1_cnt
    });
}
```
:::

---

### Пастки та інженерні тонкощі

1. **Тіньові регістри ШІМ (Preload Register):** Якщо біт `TIM_OC1PE` (Preload Enable) вимкнено, зміна значення `TIM1->CCR1` відбувається негайно в середині циклу рахунку. Якщо лічильник таймера вже проскочив нове значення `CCR1`, компаратор пропустить подію порівняння, і вихідний ШІМ зависне в одиниці на весь наступний період — це спричиняє раптовий струмовий удар та пробій силових MOSFET-ключів. Завжди вмикайте буферизацію `OCxPE`.
2. **Апаратне множення з плаваючою комою (FPU):** На процесорах ARM Cortex-M4F/M7 в ISR обов'язково має використовуватися одинарна точність `float` (32 біти). Випадкове використання константи `1.0` замість `1.0f` змушує комп'ютер викликати софтверну бібліотеку подвійної точності `double`, що роздуває час виконання ISR з 2 мкс до 45 мкс і зриває наступний такт переривання.
3. **Пріоритети переривань:** Переривання контуру керування повинно мати пріоритет NVIC вищий, ніж системний таймер RTOS (`SysTick`), переривання зв'язку (UART, SPI, USB) та стек FreeRTOS. Будь-яке блокування критичних секцій усередині RTOS (`taskENTER_CRITICAL`) не повинно маскувати виклики апаратного контуру.
4. **Кореляція пам'яті (Memory Fences):** У lock-free буферах перестановка інструкцій компілятором або процесором (out-of-order execution) може призвести до того, що споживач прочитає заголовок до запису тіла зразка. Використання атоміків з семантикою `std::memory_order_release` та `acquire` або бар'єрів `__sync_synchronize()` є обов'язковим.
