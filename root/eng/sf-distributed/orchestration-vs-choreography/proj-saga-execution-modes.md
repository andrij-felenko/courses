# ⚙️ Реалізація рушіїв саги: централізований оркестратор зі стеком відкату та реактивна хореографія на шині подій

Багатокроковий розподілений процес оформлення замовлення вимагає чіткого механізму координації кроків: резервування товару на складі, списання коштів із платіжної картки та бронювання кур'єрської доставки. Якщо на третьому кроці стається аварія, система зобов'язана гарантовано повернути гроші клієнту та зняти резерв зі складу.

Головна складність полягає в тому, що кожен крок виконує незалежну локальну транзакцію у власній базі даних. Зворотний рух не є класичним SQL `ROLLBACK`, який просто скидає незбережені сторінки пам'яті. Компенсація — це нова пряма семантична дія (`Compensating Transaction`), яка нівелює бізнес-ефект попередньої успішної дії: замість скасування запису про оплату створюється новий запис про повернення коштів (Refund), а замість видалення рядка резерву виконується операція повернення товару на доступний баланс складу.

Нижче наведено дві повноцінні моделі реалізації цього процесу:
1. **Оркестратор саги (Orchestration):** централізований диспетчер послідовно викликає кроки, реєструє компенсаційні дії у стеку `LIFO` (Last-In, First-Out) і при виникненні збою детерміновано розмотує стек у зворотному напрямку.
2. **Реактивна хореографія (Choreography):** автономні обробники підписуються на доменні події через шину, виконують локальну роботу й публікують результати або події збою, самостійно реагуючи на зворотні компенсаційні сигнали.

---

## 1. Програмний код: Порівняння моделей мовами C та C++

У реалізації на мові C використано сувору структуру з покажчиками на функції прямих дій та компенсацій, статичний масив стека відкату та детермінований цикл виконання.

У реалізації на мові C++ використано сучасні ідіоми стандарту C++23: `std::expected` для явної типізації помилок без використання важких винятків, функціональні об'єкти `std::function`, динамічний вектор компенсаційного стека з використанням зворотних ітераторів та форматований вивід `std::format`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_STEPS 8
#define MAX_PAYLOAD 128

typedef enum {
    STATUS_SUCCESS = 0,
    STATUS_FAILED = 1
} StepStatus;

typedef struct {
    char order_id[32];
    double amount;
    bool simulate_delivery_failure;
} OrderContext;

/* Сигнатури прямого кроку та компенсаційної дії */
typedef StepStatus (*ForwardAction)(OrderContext *ctx);
typedef void (*CompensateAction)(OrderContext *ctx);

typedef struct {
    const char *name;
    ForwardAction forward;
    CompensateAction compensate;
} SagaStep;

/* ── Доменні функції активностей ── */

StepStatus step_reserve_inventory(OrderContext *ctx) {
    printf("[Склад] Резервування товару для замовлення %s... [УСПІХ]\n", ctx->order_id);
    return STATUS_SUCCESS;
}

void compensate_release_inventory(OrderContext *ctx) {
    printf("[Склад] КОМПЕНСАЦІЯ: Зняття резерву товару для %s.\n", ctx->order_id);
}

StepStatus step_charge_payment(OrderContext *ctx) {
    printf("[Оплата] Списання %.2f грн для замовлення %s... [УСПІХ]\n", ctx->amount, ctx->order_id);
    return STATUS_SUCCESS;
}

void compensate_refund_payment(OrderContext *ctx) {
    printf("[Оплата] КОМПЕНСАЦІЯ: Повернення %.2f грн на картку для %s.\n", ctx->amount, ctx->order_id);
}

StepStatus step_book_delivery(OrderContext *ctx) {
    printf("[Доставка] Спроба призначення кур'єра для %s...\n", ctx->order_id);
    if (ctx->simulate_delivery_failure) {
        printf("[Доставка] ПОМИЛКА: Немає вільних кур'єрів (HTTP 503).\n");
        return STATUS_FAILED;
    }
    printf("[Доставка] Кур'єра призначено успішно.\n");
    return STATUS_SUCCESS;
}

void compensate_cancel_delivery(OrderContext *ctx) {
    printf("[Доставка] КОМПЕНСАЦІЯ: Скасування виклику кур'єра для %s.\n", ctx->order_id);
}

/* ── Рушій оркестрації зі стеком LIFO ── */

typedef struct {
    SagaStep steps[MAX_STEPS];
    size_t step_count;
    CompensateAction rollback_stack[MAX_STEPS];
    size_t stack_top;
} SagaOrchestrator;

void saga_init(SagaOrchestrator *orch) {
    orch->step_count = 0;
    orch->stack_top = 0;
}

void saga_add_step(SagaOrchestrator *orch, const char *name, ForwardAction fwd, CompensateAction comp) {
    if (orch->step_count < MAX_STEPS) {
        orch->steps[orch->step_count].name = name;
        orch->steps[orch->step_count].forward = fwd;
        orch->steps[orch->step_count].compensate = comp;
        orch->step_count++;
    }
}

bool saga_execute(SagaOrchestrator *orch, OrderContext *ctx) {
    printf("\n=== ЗАПУСК ОРКЕСТРАЦІЇ САГИ: %s ===\n", ctx->order_id);
    orch->stack_top = 0;

    for (size_t i = 0; i < orch->step_count; ++i) {
        SagaStep *step = &orch->steps[i];
        printf("-> Оркестратор викликає крок %zu: %s\n", i + 1, step->name);
        
        StepStatus status = step->forward(ctx);
        if (status == STATUS_SUCCESS) {
            /* Якщо крок успішний — реєструємо компенсацію у стеку LIFO */
            if (step->compensate) {
                orch->rollback_stack[orch->stack_top++] = step->compensate;
            }
        } else {
            printf("\n[!] ЗБІЙ на кроці %s. Оркестратор ініціює LIFO відкат!\n", step->name);
            while (orch->stack_top > 0) {
                CompensateAction comp = orch->rollback_stack[--orch->stack_top];
                comp(ctx);
            }
            printf("=== ОРКЕСТРАЦІЮ ЗАВЕРШЕНО З ВІДКАТОМ ===\n");
            return false;
        }
    }

    printf("=== ОРКЕСТРАЦІЮ УСПІШНО ЗАВЕРШЕНО ===\n");
    return true;
}

int main(void) {
    OrderContext ctx = {
        .amount = 45000.0,
        .simulate_delivery_failure = true
    };
    strncpy(ctx.order_id, "ORD-2026-X8", sizeof(ctx.order_id) - 1);

    SagaOrchestrator orch;
    saga_init(&orch);
    saga_add_step(&orch, "ReserveInventory", step_reserve_inventory, compensate_release_inventory);
    saga_add_step(&orch, "ChargePayment", step_charge_payment, compensate_refund_payment);
    saga_add_step(&orch, "BookDelivery", step_book_delivery, compensate_cancel_delivery);

    saga_execute(&orch, &ctx);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <functional>
#include <memory>
#include <expected>
#include <format>

struct OrderContext {
    std::string order_id;
    double amount{0.0};
    bool simulate_delivery_failure{false};
};

enum class StepError {
    InventoryOutOfStock,
    PaymentDeclined,
    DeliveryUnavailable,
    InternalTimeout
};

struct StepResult {
    bool success;
    std::string message;
};

/* Опис кроку саги */
struct SagaStep {
    std::string name;
    std::function<std::expected<StepResult, StepError>(OrderContext&)> forward;
    std::function<void(OrderContext&)> compensate;
};

class SagaOrchestrator {
public:
    void add_step(std::string name,
                  std::function<std::expected<StepResult, StepError>(OrderContext&)> forward,
                  std::function<void(OrderContext&)> compensate) {
        steps_.push_back(SagaStep{
            .name = std::move(name),
            .forward = std::move(forward),
            .compensate = std::move(compensate)
        });
    }

    std::expected<void, StepError> execute(OrderContext& ctx) {
        std::cout << std::format("\n=== ЗАПУСК C++ ОРКЕСТРАТОРА САГИ: {} ===\n", ctx.order_id);
        std::vector<std::function<void(OrderContext&)>> rollback_stack;

        for (size_t i = 0; i < steps_.size(); ++i) {
            const auto& step = steps_[i];
            std::cout << std::format("-> Оркестратор виконує крок {}: {}\n", i + 1, step.name);

            auto outcome = step.forward(ctx);
            if (outcome.has_value()) {
                if (step.compensate) {
                    rollback_stack.push_back(step.compensate);
                }
            } else {
                std::cout << std::format("\n[!] Збій на етапі {}. Початок LIFO розмотування компенсацій.\n", step.name);
                for (auto it = rollback_stack.rbegin(); it != rollback_stack.rend(); ++it) {
                    (*it)(ctx);
                }
                std::cout << "=== САГУ СКАСОВАНО ТА СТАБІЛІЗОВАНО ===\n";
                return std::unexpected(outcome.error());
            }
        }

        std::cout << "=== САГУ УСПІШНО ЗАВЕРШЕНО ===\n";
        return {};
    }

private:
    std::vector<SagaStep> steps_;
};

int main() {
    OrderContext ctx{
        .order_id = "ORD-CPP-2026",
        .amount = 45000.0,
        .simulate_delivery_failure = true
    };

    SagaOrchestrator orchestrator;

    orchestrator.add_step(
        "ReserveInventory",
        [](OrderContext& c) -> std::expected<StepResult, StepError> {
            std::cout << std::format("[Склад] Резервування для {}... [OK]\n", c.order_id);
            return StepResult{true, "Reserved"};
        },
        [](OrderContext& c) {
            std::cout << std::format("[Склад] КОМПЕНСАЦІЯ: Зняття резерву для {}.\n", c.order_id);
        }
    );

    orchestrator.add_step(
        "ChargePayment",
        [](OrderContext& c) -> std::expected<StepResult, StepError> {
            std::cout << std::format("[Оплата] Списання {:.2f} грн для {}... [OK]\n", c.amount, c.order_id);
            return StepResult{true, "Captured"};
        },
        [](OrderContext& c) {
            std::cout << std::format("[Оплата] КОМПЕНСАЦІЯ: Повернення {:.2f} грн для {}.\n", c.amount, c.order_id);
        }
    );

    orchestrator.add_step(
        "BookDelivery",
        [](OrderContext& c) -> std::expected<StepResult, StepError> {
            std::cout << std::format("[Доставка] Перевірка кур'єрів для {}...\n", c.order_id);
            if (c.simulate_delivery_failure) {
                std::cout << "[Доставка] ПОМИЛКА: Немає вільних авто (HTTP 503).\n";
                return std::unexpected(StepError::DeliveryUnavailable);
            }
            return StepResult{true, "Booked"};
        },
        [](OrderContext& c) {
            std::cout << std::format("[Доставка] КОМПЕНСАЦІЯ: Скасування кур'єра для {}.\n", c.order_id);
        }
    );

    auto res = orchestrator.execute(ctx);
    if (!res.has_value()) {
        std::cout << "Результат: Процес завершився з помилкою та повним відкатом.\n";
    }
    return 0;
}
```
:::

---

## 2. Глибокий аналіз архітектурної механіки відкату

Простежимо виконання кроків у наведеному прикладі, щоб зрозуміти, чому стек компенсацій є ключовим захистом від розсинхронізації:

### 1. Динамічне наповнення стека (Forward Phase)
Під час прямого виконання оркестратор додає покажчик на функцію компенсації у стек **лише після того, як пряма дія повернула успішний статус**:
* Крок 1 (`ReserveInventory`) повернув `STATUS_SUCCESS` → у стек покладено `compensate_release_inventory`.
* Крок 2 (`ChargePayment`) повернув `STATUS_SUCCESS` → у стек покладено `compensate_refund_payment`.

Це фундаментальна відмінність від наївних реалізацій, де список компенсацій жорстко зашитий наперед. Якщо б ми заздалегідь підготували список усіх трьох компенсацій і запустили його при збої на першому кроці, система спробувала б повернути гроші, які ще не списувалися, і скасувати доставку, якої не існувало.

### 2. Точка зламу та ізоляція невдалого кроку (Failure Point)
На кроці 3 (`BookDelivery`) стається збій (HTTP 503). Зверніть увагу: оскільки крок 3 завершився помилкою, функція `compensate_cancel_delivery` **не була додана у стек**. 

Якби ми викликали компенсацію для доставки, логістичний сервіс спробував би скасувати неіснуюче бронювання, що могло б призвести до фатальної помилки валідації (`BookingNotFoundException`) або блокування конвеєра відкату.

### 3. Детерміноване розмотування (LIFO Rollback Phase)
Оркестратор переходить у фазу відкату й розмотує стек у суворому порядку, зворотному до виконання:
1. Спочатку знімається `compensate_refund_payment` (останній успішний крок) — гроші повертаються на картку клієнта.
2. Потім знімається `compensate_release_inventory` (перший крок) — товар повертається у вільний продаж.

У хореографії досягнення такого суворого порядку вимагає складної передачі контексту через ланцюг топіків повідомлень, де кожен учасник має знати, хто стояв перед ним у черзі та чи потрібно передавати сигнал далі. Оркестратор робить цю логіку лінійною, прозорою та надійною.

---

## 3. Пам'ять, потокобезпека та крайові випадки

### Модель керування пам'яттю
У C-реалізації всі структури розміщуються у статичному пулі або на стеку виклику без динамічного виділення пам'яті через `malloc`, що унеможливлює витоки пам'яті (Memory Leaks) у високочастотних вбудованих диспетчерах. Статичний масив `rollback_stack[MAX_STEPS]` має фіксовану верхню межу, що виключає ризик неконтрольованого зростання динамічної купи.

У C++-версії ресурси керуються через семантику переміщення (`std::move`) та стандартні контейнери, забезпечуючи повне звільнення пам'яті за принципом RAII навіть при виникненні непередбачуваних виняткових ситуацій.

### Конкурентність та ізоляція стану
Сам об'єкт `SagaOrchestrator` опрацьовує конкретний `workflow_id` в межах одного логічного потоку виконання (State Machine Executor). Це гарантує відсутність гонок пам'яті (Data Races) при модифікації покажчика `stack_top`. 

Водночас окремі активності (`ForwardAction`) можуть виконуватися воркерами в різних потоках чи фізичних серверах, повертаючи результат асинхронно через механізм обіцянок (`Future` / `Promise`) або завершення довгого опитування черги gRPC.

### Поведінка при збої самої компенсації
Якщо під час фази розмотування стека функція `compensate_refund_payment` зазнає мережевого тайм-ауту при зверненні до банку, оркестратор не має права викинути задачу зі стека. Рушій зупиняє розмотування, запускає цикл повторів з експоненційним відкладенням і відновлює рух по стеку лише після гарантованого отримання підтвердження від платіжного шлюзу. Це виключає виникнення ситуацій, коли товар уже повернуто на склад, а гроші клієнта лишилися списаними.
