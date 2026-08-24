# ⚙️ Реалізація стійкого оркестратора Саги: журнал станів, ідемпотентні кроки та каскад компенсацій

Головна небезпека при побудові розподілених бізнес-процесів — перетворення коду на некерований набір розрізнених обробників подій або беззахисних RPC-викликів. Якщо під час виконання чергового кроку падає мережа або перезавантажується сам сервер-координатор, система без збереженого журналу назавжди втрачає інформацію про те, які дії вже зафіксовані в базах даних, а які потребують компенсації.

Розглянемо повноцінну реалізацію рушія оркестрації Саги (*Saga Execution Coordinator*, SEC). Архітектура спирається на три непорушні принципи:
1. **Незмінний журнал станів (SEC Log):** кожна зміна фази саги та кожен результат кроку скидається у стійке сховище до надсилання мережевої команди.
2. **Ідемпотентність операцій:** кожен виклик несе унікальний ідентифікатор саги та номер кроку, захищаючи сервіси від подвійного списання при повторах.
3. **Класифікація кроків:** розділення дій на компенсовні (*compensable*), точку неповернення (*pivot*) та повторювані (*retryable*).

![Життєвий цикл оркестратора саги: ведення журналу, пряме виконання та компенсаційний відкат](img/orchestration-vs-choreography.svg)
*Архітектура координатора: центральний автомат станів відправляє команди кроків, записує переходи у журнал та розгортає зворотний стек компенсацій при збоях.*

## Задача: Оформлення розподіленого замовлення

Бізнес-сценарій складається з трьох послідовних етапів:
* **Крок 1 (Payment):** списання 1500 грн з рахунку користувача. Компенсовна дія: повернення коштів.
* **Крок 2 (Inventory):** резервування товару на складі. Поворотна дія (*Pivot*): після успіху склад зафіксовано. При відмові: повертаємо гроші кроку 1.
* **Крок 3 (Notification):** відправка електронного листа з чеком. Повторювана дія (*Retryable*): гарантована відправка з повторами при таймаутах.

## Анатомія журналу виконання саги (SEC Log)

Журнал координатора — це журнал випереджального запису (*Write-Ahead Log*), адаптований для розподілених середовищ. До того як надіслати мережевий виклик до віддаленого сервісу платежів чи складу, координатор зобов'язаний зберегти запис `EXECUTING` у локальній базі даних.

Схема типового рядка в таблиці журналу саги:
* `saga_id` (UUIDv4) — глобальний ідентифікатор екземпляра саги.
* `step_index` (int) — порядковий номер кроку (0, 1, 2...).
* `step_name` (varchar) — назва кроку для трасування (`Payment`, `Inventory`).
* `state` (enum) — поточний стан (`EXECUTING`, `COMPLETED`, `FAILED`, `COMPENSATING`, `COMPENSATED`).
* `payload` (JSON/Protobuf) — параметри вхідних даних та контекст виконання.
* `updated_at` (timestamp) — позначка часу останньої мутації для детекції завислих процесів.

Якщо сервер-координатор зазнає апаратного перезапуску, під час старту фоновий воркер виконує процедуру відновлення (*Recovery Scan*):
1. Вибирає всі саги, які перебувають у проміжних станах (`EXECUTING` або `COMPENSATING`).
2. Для саг у стані `EXECUTING` перевіряє час останнього оновлення. Якщо таймаут минув, координатор повторює запит до сервісу (використовуючи ключ ідемпотентності) або ініціює компенсаційний відкат.
3. Для саг у стані `COMPENSATING` координатор продовжує розгортання стека компенсацій у зворотному порядку, починаючи з останнього незавершеного кроку.

## Робочий код: Двигун оркестрації з журналом відновлення

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <optional>
#include <chrono>
#include <thread>
#include <sstream>

enum class StepKind {
    Compensable,
    Pivot,
    Retryable
};

enum class StepState {
    NotStarted,
    Executing,
    Completed,
    Failed,
    Compensating,
    Compensated
};

struct StepContext {
    std::string saga_id;
    std::string payload;
    bool simulate_failure = false;
};

// Інтерфейс стійкого журналу виконання саги (Saga Execution Coordinator Log)
class ISagaLog {
public:
    virtual ~ISagaLog() = default;
    virtual void log_state(const std::string& saga_id, size_t step_idx, const std::string& step_name, StepState state) = 0;
};

class ConsoleSagaLog : public ISagaLog {
public:
    void log_state(const std::string& saga_id, size_t step_idx, const std::string& step_name, StepState state) override {
        const char* state_str = "UNKNOWN";
        switch (state) {
            case StepState::Executing:    state_str = "EXECUTING"; break;
            case StepState::Completed:    state_str = "COMPLETED"; break;
            case StepState::Failed:       state_str = "FAILED"; break;
            case StepState::Compensating: state_str = "COMPENSATING"; break;
            case StepState::Compensated:  state_str = "COMPENSATED"; break;
            default: break;
        }
        std::cout << " [SEC-LOG] Saga=" << saga_id << " Step[" << step_idx << "]=" 
                  << step_name << " -> State=" << state_str << "\n";
    }
};

// Визначення окремого кроку саги
class SagaStep {
public:
    std::string name;
    StepKind kind;
    std::function<bool(StepContext&)> action;
    std::function<bool(StepContext&)> compensate;

    SagaStep(std::string n, StepKind k,
             std::function<bool(StepContext&)> act,
             std::function<bool(StepContext&)> comp = nullptr)
        : name(std::move(n)), kind(k), action(std::move(act)), compensate(std::move(comp)) {}
};

// Оркестратор саги
class SagaOrchestrator {
private:
    std::string saga_id_;
    std::vector<SagaStep> steps_;
    std::shared_ptr<ISagaLog> log_;

public:
    SagaOrchestrator(std::string id, std::shared_ptr<ISagaLog> log)
        : saga_id_(std::move(id)), log_(std::move(log)) {}

    void add_step(SagaStep step) {
        steps_.push_back(std::move(step));
    }

    bool execute(StepContext& ctx) {
        std::cout << "\n=== Запуск Саги: " << saga_id_ << " ===\n";
        ctx.saga_id = saga_id_;
        size_t last_executed = 0;
        bool forward_success = true;

        // 1. Прямий хід (Forward execution)
        for (size_t i = 0; i < steps_.size(); ++i) {
            auto& step = steps_[i];
            log_->log_state(saga_id_, i, step.name, StepState::Executing);

            bool success = false;
            int retries = 0;
            const int max_retries = (step.kind == StepKind::Retryable) ? 3 : 1;

            while (!success && retries < max_retries) {
                if (retries > 0) {
                    std::cout << "  -> Повтор кроку " << step.name << " (спроба " << retries + 1 << ")...\n";
                    std::this_thread::sleep_for(std::chrono::milliseconds(50));
                }
                success = step.action(ctx);
                retries++;
            }

            if (success) {
                log_->log_state(saga_id_, i, step.name, StepState::Completed);
                last_executed = i;
            } else {
                log_->log_state(saga_id_, i, step.name, StepState::Failed);
                std::cout << " [ERROR] Крок " << step.name << " завершився фатальною помилкою!\n";
                forward_success = false;
                break;
            }
        }

        if (forward_success) {
            std::cout << "=== Сага " << saga_id_ << " успішно завершена ===\n";
            return true;
        }

        // 2. Зворотний хід (Backward compensation)
        std::cout << "\n--- Запуск каскаду компенсацій для Саги " << saga_id_ << " ---\n";
        for (int i = static_cast<int>(last_executed); i >= 0; --i) {
            auto& step = steps_[i];
            if (step.compensate) {
                log_->log_state(saga_id_, i, step.name, StepState::Compensating);
                bool comp_ok = false;
                int retries = 0;
                while (!comp_ok && retries < 5) {
                    comp_ok = step.compensate(ctx);
                    if (!comp_ok) {
                        std::cout << "  [WARN] Збій компенсації " << step.name << ", повтор...\n";
                        std::this_thread::sleep_for(std::chrono::milliseconds(50));
                    }
                    retries++;
                }
                log_->log_state(saga_id_, i, step.name, StepState::Compensated);
            }
        }

        std::cout << "=== Сага " << saga_id_ << " компенсована (стан узгоджено) ===\n";
        return false;
    }
};

int main() {
    auto log = std::make_shared<ConsoleSagaLog>();

    // Сценарій 1: Успішне виконання
    {
        SagaOrchestrator saga("ORD-1001", log);
        saga.add_step(SagaStep("Payment", StepKind::Compensable,
            [](StepContext& ctx) {
                std::cout << "  [Billing] Списано 1500 грн для " << ctx.saga_id << "\n";
                return true;
            },
            [](StepContext& ctx) {
                std::cout << "  [Billing-Comp] Повернуто 1500 грн для " << ctx.saga_id << "\n";
                return true;
            }
        ));

        saga.add_step(SagaStep("Inventory", StepKind::Pivot,
            [](StepContext& ctx) {
                std::cout << "  [Warehouse] Товар зарезервовано на складі\n";
                return true;
            },
            [](StepContext& ctx) {
                std::cout << "  [Warehouse-Comp] Знято резерв товару\n";
                return true;
            }
        ));

        saga.add_step(SagaStep("Notification", StepKind::Retryable,
            [](StepContext& ctx) {
                std::cout << "  [Notifier] Чек надіслано покупцю\n";
                return true;
            }
        ));

        StepContext ctx{"", "order_data_ok", false};
        saga.execute(ctx);
    }

    // Сценарій 2: Збій на етапі складу з відкатом платежу
    {
        SagaOrchestrator saga("ORD-1002", log);
        saga.add_step(SagaStep("Payment", StepKind::Compensable,
            [](StepContext& ctx) {
                std::cout << "  [Billing] Списано 1500 грн для " << ctx.saga_id << "\n";
                return true;
            },
            [](StepContext& ctx) {
                std::cout << "  [Billing-Comp] Повернуто 1500 грн для " << ctx.saga_id << "\n";
                return true;
            }
        ));

        saga.add_step(SagaStep("Inventory", StepKind::Pivot,
            [](StepContext& ctx) {
                std::cout << "  [Warehouse] ПОМИЛКА: Товару немає на залишку!\n";
                return false;
            },
            [](StepContext& ctx) {
                std::cout << "  [Warehouse-Comp] Знято резерв товару\n";
                return true;
            }
        ));

        StepContext ctx{"", "order_data_fail", true};
        saga.execute(ctx);
    }

    return 0;
}
```
```go
package main

import (
	"context"
	"fmt"
	"time"
)

type StepKind int

const (
	Compensable StepKind = iota
	Pivot
	Retryable
)

type StepState string

const (
	StateExecuting    StepState = "EXECUTING"
	StateCompleted    StepState = "COMPLETED"
	StateFailed       StepState = "FAILED"
	StateCompensating StepState = "COMPENSATING"
	StateCompensated  StepState = "COMPENSATED"
)

type StepContext struct {
	SagaID  string
	Payload string
}

type ISagaLog interface {
	LogState(sagaID string, stepIdx int, stepName string, state StepState)
}

type ConsoleSagaLog struct{}

func (l *ConsoleSagaLog) LogState(sagaID string, stepIdx int, stepName string, state StepState) {
	fmt.Printf(" [SEC-LOG] Saga=%s Step[%d]=%s -> State=%s\n", sagaID, stepIdx, stepName, state)
}

type ActionFunc func(ctx context.Context, sCtx *StepContext) error

type SagaStep struct {
	Name       string
	Kind       StepKind
	Action     ActionFunc
	Compensate ActionFunc
}

type SagaOrchestrator struct {
	sagaID string
	steps  []SagaStep
	log    ISagaLog
}

func NewSagaOrchestrator(id string, log ISagaLog) *SagaOrchestrator {
	return &SagaOrchestrator{
		sagaID: id,
		steps:  make([]SagaStep, 0),
		log:    log,
	}
}

func (s *SagaOrchestrator) AddStep(step SagaStep) {
	s.steps = append(s.steps, step)
}

func (s *SagaOrchestrator) Execute(ctx context.Context, sCtx *StepContext) bool {
	fmt.Printf("\n=== Запуск Саги: %s ===\n", s.sagaID)
	sCtx.SagaID = s.sagaID
	lastExecuted := -1
	forwardSuccess := true

	// 1. Прямий хід
	for i, step := range s.steps {
		s.log.LogState(s.sagaID, i, step.Name, StateExecuting)
		var err error
		maxRetries := 1
		if step.Kind == Retryable {
			maxRetries = 3
		}

		for attempt := 1; attempt <= maxRetries; attempt++ {
			if attempt > 1 {
				fmt.Printf("  -> Повтор кроку %s (спроба %d)...\n", step.Name, attempt)
				time.Sleep(50 * time.Millisecond)
			}
			err = step.Action(ctx, sCtx)
			if err == nil {
				break
			}
		}

		if err == nil {
			s.log.LogState(s.sagaID, i, step.Name, StateCompleted)
			lastExecuted = i
		} else {
			s.log.LogState(s.sagaID, i, step.Name, StateFailed)
			fmt.Printf(" [ERROR] Крок %s завершився помилкою: %v\n", step.Name, err)
			forwardSuccess = false
			break
		}
	}

	if forwardSuccess {
		fmt.Printf("=== Сага %s успішно завершена ===\n", s.sagaID)
		return true
	}

	// 2. Зворотний хід (компенсація)
	fmt.Printf("\n--- Запуск каскаду компенсацій для Саги %s ---\n", s.sagaID)
	for i := lastExecuted; i >= 0; i-- {
		step := s.steps[i]
		if step.Compensate != nil {
			s.log.LogState(s.sagaID, i, step.Name, StateCompensating)
			for attempt := 1; attempt <= 5; attempt++ {
				cErr := step.Compensate(ctx, sCtx)
				if cErr == nil {
					break
				}
				fmt.Printf("  [WARN] Збій компенсації %s, спроба %d...\n", step.Name, attempt)
				time.Sleep(50 * time.Millisecond)
			}
			s.log.LogState(s.sagaID, i, step.Name, StateCompensated)
		}
	}

	fmt.Printf("=== Сага %s компенсована (стан узгоджено) ===\n", s.sagaID)
	return false
}

func main() {
	log := &ConsoleSagaLog{}
	ctx := context.Background()

	// Сценарій 1: Успіх
	s1 := NewSagaOrchestrator("ORD-2001", log)
	s1.AddStep(SagaStep{
		Name: "Payment",
		Kind: Compensable,
		Action: func(c context.Context, sc *StepContext) error {
			fmt.Printf("  [Billing] Списано 1500 грн для %s\n", sc.SagaID)
			return nil
		},
		Compensate: func(c context.Context, sc *StepContext) error {
			fmt.Printf("  [Billing-Comp] Повернуто 1500 грн для %s\n", sc.SagaID)
			return nil
		},
	})
	s1.AddStep(SagaStep{
		Name: "Inventory",
		Kind: Pivot,
		Action: func(c context.Context, sc *StepContext) error {
			fmt.Println("  [Warehouse] Товар зарезервовано на складі")
			return nil
		},
	})
	s1.AddStep(SagaStep{
		Name: "Notification",
		Kind: Retryable,
		Action: func(c context.Context, sc *StepContext) error {
			fmt.Println("  [Notifier] Чек надіслано покупцю")
			return nil
		},
	})
	s1.Execute(ctx, &StepContext{Payload: "ok"})

	// Сценарій 2: Відмова складу
	s2 := NewSagaOrchestrator("ORD-2002", log)
	s2.AddStep(SagaStep{
		Name: "Payment",
		Kind: Compensable,
		Action: func(c context.Context, sc *StepContext) error {
			fmt.Printf("  [Billing] Списано 1500 грн для %s\n", sc.SagaID)
			return nil
		},
		Compensate: func(c context.Context, sc *StepContext) error {
			fmt.Printf("  [Billing-Comp] Повернуто 1500 грн для %s\n", sc.SagaID)
			return nil
		},
	})
	s2.AddStep(SagaStep{
		Name: "Inventory",
		Kind: Pivot,
		Action: func(c context.Context, sc *StepContext) error {
			return fmt.Errorf("товару немає в наявності")
		},
	})
	s2.Execute(ctx, &StepContext{Payload: "fail"})
}
```
:::

## Інженерні пастки реалізації

### 1. Падіння самого координатора під час компенсації
Якщо процес оркестратора гине посеред виконання кроку `C[2]`, під час рестарту сервіс зчитує `SEC-LOG` з диска або бази даних. Знайшовши сагу у стані `COMPENSATING`, координатор відновлює виконання строго з незавершеного кроку компенсації `C[2]`, а не з початку.

Для кластерних середовищ, де запущено кілька екземплярів оркестратора, відновлення координується через механізм розподіленого лізингу або лічильників епохи (*fencing tokens*): лише один вузол бере на себе обробку завислої саги, унеможливлюючи подвійне виконання паралельними воркерами.

### 2. Отруйна пігулка (*Poison Pill*) та ручне втручання
Якщо компенсаційна транзакція повертає фатальну помилку (наприклад, сторонній платіжний шлюз змінив формат підпису запиту або рахунок користувача заблоковано регулятором), нескінченні автоматичні повтори заблокують обробку.

У таких ситуаціях застосовується покрокова ескалація:
* Після 5 невдалих спроб з експоненційною затримкою (*exponential backoff with jitter*) сага переводиться у стан `MANUAL_RECONCILIATION_REQUIRED`.
* Повний контекст саги, включаючи історію спроб та тіла відповідей, відправляється у чергу мертвих повідомлень (*Dead Letter Queue*, DLQ).
* Оператор технічної підтримки через адмін-панель може вручну перевірити стан рахунку, виконати банківську проводку в ручному режимі та позначити крок як `COMPENSATED`, дозволивши оркестратору завершити решту компенсацій.

### 3. Гарантія обов'язкової ідемпотентності та Transactional Outbox
Компенсаційна транзакція `C[i]` може викликатися кілька разів через розриви мережевих з'єднань або таймаути. Якщо платіжний сервіс не підтримує таблицю ідемпотентності за ключем `saga_id + "_step_" + step_index + "_comp"`, повтор повернення коштів призведе до подвійного зарахування грошей клієнту.

Для відправки повідомлень між оркестратором та сервісами використовується патерн [Transactional outbox](topic:programming/outbox-pattern): запис про намір відправити команду вставляється в ту саму локальну транзакцію бази даних, що й зміна стану в `SEC-LOG`. Фоновий процес вичитує outbox-таблицю й гарантовано публікує повідомлення в брокер, усуваючи дуальний запис (*dual-write hazard*). На боці сервісу-отримувача працює [Inbox-патерн](topic:programming/inbox-pattern), який фільтрує дублікати перед виконанням бізнес-логіки.

### 4. Простеження виконання за журналом (Трасування)

Розглянемо трасу подій у консолі для другого сценарію (збій складу):
1. `Saga=ORD-1002 Step[0]=Payment -> State=EXECUTING` — оркестратор записує намір.
2. `[Billing] Списано 1500 грн для ORD-1002` — платіж зафіксовано в банку.
3. `Saga=ORD-1002 Step[0]=Payment -> State=COMPLETED` — підтвердження отримано.
4. `Saga=ORD-1002 Step[1]=Inventory -> State=EXECUTING` — спроба зарезервувати товар.
5. `[Warehouse] ПОМИЛКА: Товару немає на залишку!` — виявлено бізнес-відмову (поворотний крок не виконано).
6. `Saga=ORD-1002 Step[1]=Inventory -> State=FAILED` — фіксація збою.
7. `Saga=ORD-1002 Step[0]=Payment -> State=COMPENSATING` — запуск зворотної компенсації платежу.
8. `[Billing-Comp] Повернуто 1500 грн для ORD-1002` — кошти зараховано назад.
9. `Saga=ORD-1002 Step[0]=Payment -> State=COMPENSATED` — компенсація зафіксована.
10. `=== Сага ORD-1002 компенсована (стан узгоджено) ===` — фінальне сходження системи.

Усі гроші на місці, товари на складі не заблоковані, а клієнт отримує зрозумілу відповідь про відсутність товару без завислих ресурсів.
