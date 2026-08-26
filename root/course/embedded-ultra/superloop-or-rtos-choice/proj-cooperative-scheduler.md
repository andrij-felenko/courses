# ⚙️ Кооперативний планувальник завдань на мікроконтролері

Цей проєкт демонструє побудову детерміністичного диспетчера періодичних задач для систем із жорстким бюджетом оперативної пам'яті, де накладні витрати витісняльної операційної системи реального часу є неприпустимими.

У керуванні безпілотними апаратами та швидкісними приводами часто постає завдання: виконувати стабілізаційний контур із фіксованою частотою (наприклад, 1 кГц або 8 кГц), паралельно обслуговуючи повільні фонові задачі (обробку телеметрії на 50 Гц, опитування барометра на 20 Гц та моніторинг напруги акумулятора на 10 Гц). Класичний неорганізований суперцикл перетворюється на заплутаний лабіринт лічильників і прапорців, а витісняльна RTOS вимагає виділення кілобайтів пам'яті під окремі стеки кожної нитки.

Кооперативний планувальник (Cooperative Scheduler) розв'язує цю дилему: усі задачі виконуються в єдиному контексті головного циклу зі спільним стеком, проте отримують суворий часовий розклад на основі мікросекундного таймера та статичних пріоритетів.

## Архітектурний задум

Планувальник оперує масивом дескрипторів задач. Кожна задача описується покажчиком на функцію, періодом виклику, часовою міткою наступного очікуваного запуску, пріоритетом та динамічною статистикою виконання.

```
+-------------------------------------------------------------+
|               Головний цикл (Super-loop)                    |
|                                                             |
|   1. Отримати поточний час: now = micros()                  |
|   2. Знайти готову задачу з найвищим пріоритетом:           |
|      (int32_t)(now - next_execution_us) >= 0                |
|   3. Виконати задачу: task->callback()                      |
|   4. Оновити таймінг: next_execution_us += period_us        |
|   5. Якщо жодна задача не готова -> перейти в режим сну WFI |
+-------------------------------------------------------------+
```

Ключовий математичний нюанс полягає в оновленні часу наступного запуску. Якщо додавати період до поточного часу `micros()`, виникає систематичний часовий дрейф (Phase Drift), оскільки тривалість виконання самої задачі щоразу зміщуватиме фазу:

```
next_execution_us = now + period_us             [помилково: накопичує дрейф]
next_execution_us = next_execution_us + period_us [правильно: фіксована часова сітка]
```

Другий важливий аспект — захист від переповнення апаратного 32-бітного мікросекундного лічильника. Значення `uint32_t` переповнюється кожні 71.58 хвилини (`2³² - 1` мікросекунд). Пряме порівняння `now >= next_execution_us` у момент переходу через нуль дає хибний результат. Натомість операція віднімання цілих беззнакових чисел `(int32_t)(now - next_execution_us) >= 0` коректно працює навіть під час переповнення за умови, що затримка не перевищує `2³¹ - 1` мікросекунд (понад 35 хвилин).

## Прецизійне профілювання через DWT-лічильник та розрахунок завантаження CPU

Для прецизійного вимірювання часу виконання окремих задач на ядрах ARM Cortex-M3/M4/M7 замість системного таймера з мікросекундною роздільною здатністю використовують апаратний лічильник тактів DWT (Data Watchpoint and Trace, регістр `DWT->CYCCNT`).

На процесорі з тактовою частотою 168 МГц один такт лічильника DWT дорівнює:

```
t_tick = 1 / 168 000 000 = 5.95 наносекунди
```

Це дозволяє фіксувати тривалість виконання коротких функцій фільтрації з точністю до окремих інструкцій.

Загальне завантаження процесора (CPU Load) розраховується за ковзним вікном спостереження тривалістю 1 секунда:

```
CPU_Load = (∑ T_exec_task[i] / T_window) × 1000 ‰
```

Значення у проміле (десятих частках відсотка) передається в телеметричний потік польотного контролера. Якщо сумарне завантаження перевищує 850 ‰ (85%), планувальник генерує попередження про наближення до межі пропускної здатності.

## Подієве розширення: міст між перериваннями та планувальником

Періодичний запуск вирішує більшість завдань опитування, але реакція на зовнішні апаратні події (завершення прийому кадру UART по DMA, готовність даних на ніжці DRDY гіроскопа) потребує подієвого тригера (Event-driven trigger).

Вводити блокуюче очікування прапорця в планувальнику заборонено. Замість цього дескриптор задачі розширюється бітовою маскою динамічних подій. Обробник переривання ISR виконує мінімальну дію — атомарно встановлює біт події у бітовій масці за допомогою апаратних інструкцій або критичної секції, а диспетчер під час чергового сканування масиву негайно запускає відповідну задачу, навіть якщо її періодичний час ще не настав.

Такий гібридний підхід усуває необхідність постійного опитування периферії (Polling) та гарантує запуск обробника події одразу після завершення поточної виконуваної задачі.

## Реалізація диспетчера завдань

Нижче наведено повну виробничу реалізацію планувальника двома мовами: чистим C для мікроконтролерів Cortex-M та ідіоматичним C++20 з використанням статичних масивів, шаблонних параметрів і лямбда-функцій без динамічного виділення пам'яті.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define SCHEDULER_MAX_TASKS 8

typedef void (*task_fn_t)(uint32_t current_time_us);

typedef enum {
    TASK_PRIORITY_LOW    = 0,
    TASK_PRIORITY_MEDIUM = 1,
    TASK_PRIORITY_HIGH   = 2,
    TASK_PRIORITY_REALTIME = 3
} task_priority_t;

typedef struct {
    task_fn_t callback;
    uint32_t period_us;
    uint32_t next_execution_us;
    uint32_t max_exec_time_us;
    uint32_t total_exec_time_us;
    uint32_t execution_count;
    task_priority_t priority;
    volatile uint8_t event_flags;
    bool enabled;
} task_descriptor_t;

typedef struct {
    task_descriptor_t tasks[SCHEDULER_MAX_TASKS];
    uint8_t task_count;
    uint32_t total_overruns;
    uint32_t cpu_load_permille; /* Завантаження CPU у проміле (0.1%) */
} scheduler_t;

/* Системна функція отримання монотонного часу в мікросекундах */
extern uint32_t platform_micros(void);

/* Переведення процесора в режим низького енергоспоживання до переривання */
extern void platform_sleep_wfi(void);

void scheduler_init(scheduler_t *sched) {
    sched->task_count = 0;
    sched->total_overruns = 0;
    sched->cpu_load_permille = 0;
    for (uint8_t i = 0; i < SCHEDULER_MAX_TASKS; ++i) {
        sched->tasks[i].enabled = false;
        sched->tasks[i].event_flags = 0;
    }
}

bool scheduler_add_task(scheduler_t *sched, task_fn_t fn, uint32_t period_us, task_priority_t priority) {
    if (sched->task_count >= SCHEDULER_MAX_TASKS || fn == NULL) {
        return false;
    }

    uint8_t idx = sched->task_count++;
    uint32_t now = platform_micros();

    sched->tasks[idx].callback = fn;
    sched->tasks[idx].period_us = period_us;
    sched->tasks[idx].next_execution_us = now + period_us;
    sched->tasks[idx].max_exec_time_us = 0;
    sched->tasks[idx].total_exec_time_us = 0;
    sched->tasks[idx].execution_count = 0;
    sched->tasks[idx].priority = priority;
    sched->tasks[idx].event_flags = 0;
    sched->tasks[idx].enabled = true;

    return true;
}

void scheduler_trigger_event(scheduler_t *sched, uint8_t task_id, uint8_t flag) {
    if (task_id < sched->task_count) {
        sched->tasks[task_id].event_flags |= flag;
    }
}

void scheduler_dispatch(scheduler_t *sched) {
    uint32_t now = platform_micros();
    int16_t selected_task_idx = -1;
    task_priority_t highest_priority = TASK_PRIORITY_LOW;
    int32_t max_time_overdue = 0;
    bool is_event_triggered = false;

    /* Пошук найбільш пріоритетної готової задачі */
    for (uint8_t i = 0; i < sched->task_count; ++i) {
        task_descriptor_t *t = &sched->tasks[i];
        if (!t->enabled) continue;

        /* Перевірка наявності асинхронної події від ISR */
        if (t->event_flags != 0) {
            selected_task_idx = i;
            highest_priority = t->priority;
            is_event_triggered = true;
            break;
        }

        int32_t delta = (int32_t)(now - t->next_execution_us);
        if (delta >= 0) {
            if (selected_task_idx == -1 || t->priority > highest_priority ||
               (t->priority == highest_priority && delta > max_time_overdue)) {
                selected_task_idx = i;
                highest_priority = t->priority;
                max_time_overdue = delta;
            }
        }
    }

    if (selected_task_idx != -1) {
        task_descriptor_t *task = &sched->tasks[selected_task_idx];
        uint32_t start_us = platform_micros();

        if (is_event_triggered) {
            task->event_flags = 0; /* Очищення прапорців події */
        }

        /* Виклик тіла задачі */
        task->callback(start_us);

        uint32_t exec_duration = platform_micros() - start_us;
        task->total_exec_time_us += exec_duration;
        task->execution_count++;
        if (exec_duration > task->max_exec_time_us) {
            task->max_exec_time_us = exec_duration;
        }

        /* Оновлення сітки часу для періодичних задач */
        if (task->period_us > 0) {
            task->next_execution_us += task->period_us;

            /* Детекція катастрофічного перевантаження */
            now = platform_micros();
            if ((int32_t)(now - task->next_execution_us) >= (int32_t)task->period_us) {
                sched->total_overruns++;
                task->next_execution_us = now + task->period_us;
            }
        }
    } else {
        /* Якщо жодна задача не готова, переводимо ядро в режим низького струму */
        platform_sleep_wfi();
    }
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <functional>
#include <algorithm>

enum class TaskPriority : uint8_t {
    Low = 0,
    Medium = 1,
    High = 2,
    Realtime = 3
};

struct TaskMetrics {
    uint32_t max_duration_us{0};
    uint32_t total_duration_us{0};
    uint32_t execution_count{0};
    uint32_t overrun_count{0};
};

template <size_t MaxTasks>
class CooperativeScheduler {
public:
    using TaskCallback = void (*)(uint32_t now_us);

    struct Task {
        TaskCallback callback{nullptr};
        uint32_t period_us{0};
        uint32_t next_execution_us{0};
        TaskPriority priority{TaskPriority::Low};
        volatile uint8_t event_flags{0};
        bool enabled{false};
        TaskMetrics metrics{};
    };

    constexpr CooperativeScheduler() = default;

    bool add_task(TaskCallback fn, uint32_t period_us, TaskPriority priority = TaskPriority::Medium) noexcept {
        if (task_count_ >= MaxTasks || fn == nullptr) {
            return false;
        }

        const uint32_t now = get_platform_micros();
        tasks_[task_count_] = Task{
            .callback = fn,
            .period_us = period_us,
            .next_execution_us = now + period_us,
            .priority = priority,
            .event_flags = 0,
            .enabled = true,
            .metrics = {}
        };
        ++task_count_;
        return true;
    }

    void trigger_event(size_t task_index, uint8_t flag) noexcept {
        if (task_index < task_count_) {
            tasks_[task_index].event_flags |= flag;
        }
    }

    void dispatch() noexcept {
        const uint32_t now = get_platform_micros();
        int32_t best_index = -1;
        TaskPriority highest_priority = TaskPriority::Low;
        int32_t max_overdue = 0;
        bool event_active = false;

        for (size_t i = 0; i < task_count_; ++i) {
            auto& t = tasks_[i];
            if (!t.enabled) continue;

            if (t.event_flags != 0) {
                best_index = static_cast<int32_t>(i);
                highest_priority = t.priority;
                event_active = true;
                break;
            }

            const int32_t delta = static_cast<int32_t>(now - t.next_execution_us);
            if (delta >= 0) {
                if (best_index == -1 || t.priority > highest_priority ||
                   (t.priority == highest_priority && delta > max_overdue)) {
                    best_index = static_cast<int32_t>(i);
                    highest_priority = t.priority;
                    max_overdue = delta;
                }
            }
        }

        if (best_index >= 0) {
            auto& task = tasks_[static_cast<size_t>(best_index)];
            const uint32_t start_us = get_platform_micros();

            if (event_active) {
                task.event_flags = 0;
            }

            task.callback(start_us);

            const uint32_t duration_us = get_platform_micros() - start_us;
            task.metrics.total_duration_us += duration_us;
            task.metrics.max_duration_us = std::max(task.metrics.max_duration_us, duration_us);
            ++task.metrics.execution_count;

            if (task.period_us > 0) {
                task.next_execution_us += task.period_us;

                const uint32_t post_exec_now = get_platform_micros();
                if (static_cast<int32_t>(post_exec_now - task.next_execution_us) >= static_cast<int32_t>(task.period_us)) {
                    ++task.metrics.overrun_count;
                    ++global_overruns_;
                    task.next_execution_us = post_exec_now + task.period_us;
                }
            }
        } else {
            enter_sleep_mode();
        }
    }

    [[nodiscard]] std::span<const Task> tasks() const noexcept {
        return std::span<const Task>(tasks_.data(), task_count_);
    }

    [[nodiscard]] uint32_t total_overruns() const noexcept {
        return global_overruns_;
    }

private:
    static uint32_t get_platform_micros() noexcept;
    static void enter_sleep_mode() noexcept;

    std::array<Task, MaxTasks> tasks_{};
    size_t task_count_{0};
    uint32_t global_overruns_{0};
};
```
:::

## Інженерні пастки та їх подолання

1. **Блокуючі операції всередині задачі.** Якщо будь-яка задача викличе блокуючу затримку на зразок `delay_ms(10)` або зависне в очікуванні прапорця апаратного регістра UART, весь розклад заблокується на цей час. Усі задачі мусять проєктуватися як неблокуючі кінцеві автомати (FSM), що повертають керування менш ніж за 50–100 мікросекунд.

2. **Лавинне наздоганяння (Overrun Cascading).** Коли важка задача перевищує свій бюджет і затримує інші періодичні задачі, наївний алгоритм намагатиметься виконати пропущені ітерації поспіль без пауз. Захисний блок `(now - task->next_execution_us) >= task->period_us` виявляє цей стан, фіксує переповнення лічильника `overrun_count` і переносить час запуску на наступний інтервал, запобігаючи зупинці системи.

3. **Спільний стек і локальні змінні.** Оскільки всі задачі виконуються в єдиному контексті, великі буфери (наприклад, кадр пакету телеметрії на 512 байтів) не можна розміщувати в локальному стеку всередині функцій, оскільки це збільшує загальні вимоги до стека. Їх слід оголошувати як статичні змінні модуля або виділяти в глобальній області `.bss`.

4. **Атомарність викликів із переривань.** Прапорець `event_flags` модифікується з обробників ISR та скидається всередині планувальника. Для запобігання втрати подій (Race Condition) операції читання та запису прапорців на 8-бітних або 32-бітних регістрах мають бути атомарними або захищеними маскуванням переривань `__disable_irq()` / `__enable_irq()`.

5. **Кеш-когерентність на ARM Cortex-M7.** На чипах STM32F7 / STM32H7 увімкнений кеш даних L1 D-Cache може призвести до того, що оновлений обробником DMA дескриптор задачі в оперативній пам'яті не буде помічений ядром CPU через застарілі дані в рядку кешу. У таких конфігураціях масив дескрипторів або розміщують у некешованій пам'яті через налаштування MPU (Memory Protection Unit), або виконують інвалідацію кешу `SCB_InvalidateDCache_by_Addr()`.
