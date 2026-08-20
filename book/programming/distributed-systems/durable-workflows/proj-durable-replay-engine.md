# ⚙️ Реалізація рушія детермінованого відтворення та незнищенного виконання

Створення розподілених бізнес-процесів вимагає залізобетонної гарантії: після аварійного падіння сервера, втрати живлення чи перезапуску контейнера виконання коду не повинно починатися спочатку з дублюванням фінансових транзакцій чи надсиланням повторних листів клієнту. Код має відновитися рівно з тієї точки, де стався збій, зберігаючи всі значення локальних змінних, лічильників циклів та стек викликів.

Для розуміння внутрішньої механіки платформ довговічного виконання (Durable Execution) розглянемо побудову мінімального рушія на базі детермінованого відтворення (Deterministic Replay Engine). Цей механізм лежить в основі таких промислових систем, як Temporal, Cadence та Azure Durable Task Framework.

## Архітектурна модель: як працює перехоплювач подій

Рушій довговічного виконання не намагається робити періодичні «дампи» оперативної пам'яті процесу на диск. Спроба зберегти весь образ віртуальної пам'яті (memory dump) була б надзвичайно повільною, непереносною між різними версіями операційної системи й несумісною з оновленням коду.

Замість цього застосовується модель подієвого сорсингу (Event Sourcing). Рушій складається з трьох ключових архітектурних ланок:

1. **Журнал історії (Event History):** незмінний впорядкований список подій, що послідовно фіксує кожен зовнішній ефект. У ньому зберігаються лише результати взаємодії із зовнішнім світом: вхідні аргументи процесу (`WorkflowStarted`), реєстрація задачі в черзі (`ActivityScheduled`), успішний фінал задачі з поверненими даними (`ActivityCompleted`) та спрацьовування таймерів (`TimerFired`).
2. **Контекст виконання (Workflow Context):** обгортка, яка перехоплює будь-які зовнішні виклики всередині бізнес-функції. Замість безпосереднього виконання мережевого запиту (I/O) контекст перевіряє поточний покажчик у журналі історії:
   * Якщо на поточному кроці в історії вже є збережений результат (`ActivityCompleted`), рушій миттєво повертає його значення у функцію без реального мережевого виклику.
   * Якщо запису про завершення немає, рушій фіксує намір виконати операцію (`ActivityScheduled`) та призупиняє виконання поточної ітерації процесу за допомогою механізму переривання (виняток, генератор або корутина).
   * Якщо тип або параметри запланованої операції не збігаються із записом в історії, фіксується фатальна помилка недетермінізму (*Non-determinism error*).
3. **Диспетчер виконання (Replay Worker):** фоновий компонент, що отримує нові результати з черги задач та запускає функцію процесу від самого початку (`main`), проганяючи збережені події до досягнення нового незвіданого кроку.

## Реалізація рушія: C++ та Go

Розглянемо повноцінну реалізацію мінімального рушія, який підтримує детерміноване виконання асинхронних активностей, збереження історії, виявлення розбіжностей у коді та відновлення після аварійного падіння вузла.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <variant>
#include <memory>
#include <stdexcept>
#include <optional>
#include <functional>

// ── Типи подій у незмінному журналі історії ──────────────────────────────
struct WorkflowStartedEvent {
    std::string workflow_id;
    std::string input_data;
};

struct ActivityScheduledEvent {
    std::string activity_name;
    std::string input;
};

struct ActivityCompletedEvent {
    std::string activity_name;
    std::string result;
};

struct TimerFiredEvent {
    int duration_ms;
};

using WorkflowEvent = std::variant<
    WorkflowStartedEvent,
    ActivityScheduledEvent,
    ActivityCompletedEvent,
    TimerFiredEvent
>;

// ── Виняток для призупинення виконання при очікуванні результату ─────────
class ExecutionYieldedException : public std::exception {
public:
    const char* what() const noexcept override {
        return "Workflow execution yielded awaiting external event";
    }
};

// ── Виняток порушення детермінізму коду ──────────────────────────────────
class NonDeterminismException : public std::runtime_error {
public:
    explicit NonDeterminismException(const std::string& msg)
        : std::runtime_error("Non-determinism detected: " + msg) {}
};

// ── Контекст детермінованого робочого процесу ────────────────────────────
class WorkflowContext {
private:
    const std::vector<WorkflowEvent>& history_;
    std::vector<WorkflowEvent> new_events_;
    size_t replay_index_{0};
    bool is_replaying_{true};

public:
    explicit WorkflowContext(const std::vector<WorkflowEvent>& history)
        : history_(history) {}

    // Метод виклику activity з підтримкою відтворення з історії
    std::string execute_activity(const std::string& name, const std::string& input) {
        if (replay_index_ < history_.size()) {
            const auto& event = history_[replay_index_];
            
            // Якщо наступна подія — завершення цієї активності, повертаємо записаний результат
            if (auto completed = std::get_if<ActivityCompletedEvent>(&event)) {
                if (completed->activity_name != name) {
                    throw NonDeterminismException(
                        "Expected activity '" + completed->activity_name + 
                        "', but workflow requested '" + name + "'"
                    );
                }
                replay_index_++;
                return completed->result;
            }
            
            // Якщо подія в історії є плануванням, ми все ще чекаємо на її результат
            if (auto scheduled = std::get_if<ActivityScheduledEvent>(&event)) {
                if (scheduled->activity_name != name) {
                    throw NonDeterminismException("History mismatch on scheduled activity: " + name);
                }
                replay_index_++;
                throw ExecutionYieldedException();
            }
        }

        // Подій в історії більше немає: плануємо нову активність
        is_replaying_ = false;
        new_events_.push_back(ActivityScheduledEvent{name, input});
        throw ExecutionYieldedException();
    }

    bool is_replaying() const noexcept {
        return is_replaying_ && (replay_index_ < history_.size());
    }

    const std::vector<WorkflowEvent>& get_new_events() const noexcept {
        return new_events_;
    }
};

// ── Функція бізнес-процесу (Workflow Definition) ─────────────────────────
// Код пишеться як звичайна послідовна функція без ручних state-машин
std::string order_fulfillment_workflow(WorkflowContext& ctx, const std::string& order_id) {
    // Крок 1: Списання коштів
    std::string payment_res = ctx.execute_activity("ProcessPayment", order_id + ":amount=500");

    // Крок 2: Резервування товару на складі
    std::string inventory_res = ctx.execute_activity("ReserveInventory", order_id + ":item=SKU-99");

    // Крок 3: Створення накладної доставки
    std::string shipping_res = ctx.execute_activity("CreateShippingLabel", order_id + ":addr=Kyiv");

    return "Order " + order_id + " completed: " + payment_res + " | " + inventory_res + " | " + shipping_res;
}
```
```go
package main

import (
	"errors"
	"fmt"
)

// Типи подій в історії
type EventType int

const (
	EventWorkflowStarted EventType = iota
	EventActivityScheduled
	EventActivityCompleted
)

type WorkflowEvent struct {
	Type         EventType
	ActivityName string
	Input        string
	Result       string
}

var ErrYield = errors.New("execution yielded")

// WorkflowContext керує детермінованим відтворенням
type WorkflowContext struct {
	history     []WorkflowEvent
	newEvents   []WorkflowEvent
	replayIndex int
}

func NewWorkflowContext(history []WorkflowEvent) *WorkflowContext {
	return &WorkflowContext{history: history}
}

// ExecuteActivity перевіряє історію перед реальним виконанням
func (ctx *WorkflowContext) ExecuteActivity(name, input string) (string, error) {
	if ctx.replayIndex < len(ctx.history) {
		event := ctx.history[ctx.replayIndex]
		if event.Type == EventActivityCompleted {
			if event.ActivityName != name {
				return "", fmt.Errorf("non-determinism: expected %s, got %s", event.ActivityName, name)
			}
			ctx.replayIndex++
			return event.Result, nil
		}
		if event.Type == EventActivityScheduled {
			ctx.replayIndex++
			return "", ErrYield
		}
	}

	ctx.newEvents = append(ctx.newEvents, WorkflowEvent{
		Type:         EventActivityScheduled,
		ActivityName: name,
		Input:        input,
	})
	return "", ErrYield
}

// Функція бізнес-процесу
func OrderFulfillmentWorkflow(ctx *WorkflowContext, orderID string) (string, error) {
	payRes, err := ctx.ExecuteActivity("ProcessPayment", orderID+":amount=500")
	if err != nil {
		return "", err
	}

	invRes, err := ctx.ExecuteActivity("ReserveInventory", orderID+":item=SKU-99")
	if err != nil {
		return "", err
	}

	shipRes, err := ctx.ExecuteActivity("CreateShippingLabel", orderID+":addr=Kyiv")
	if err != nil {
		return "", err
	}

	return fmt.Sprintf("Order %s done: %s, %s, %s", orderID, payRes, invRes, shipRes), nil
}
```
:::

## Покрокова симуляція аварії та відновлення

Для демонстрації незнищенності процесу змоделюємо повний життєвий цикл виконання з аварійним падінням сервера після успішної фіксації кроку 1.

:::tabs
```cpp
// ── Диспетчер тестування та емулятор середовища ─────────────────────────
int main() {
    std::cout << "=== СТАРТ НОВОГО РОБОЧОГО ПРОЦЕСУ ===" << std::endl;
    std::vector<WorkflowEvent> history;
    history.push_back(WorkflowStartedEvent{"order-101", "user=Andrii"});

    // ── Ітерація 1: Перший запуск на новому вузлі ────────────────────────
    std::cout << "\n[Вузол 1] Запуск виконання workflow..." << std::endl;
    {
        WorkflowContext ctx(history);
        try {
            order_fulfillment_workflow(ctx, "order-101");
        } catch (const ExecutionYieldedException&) {
            std::cout << "[Вузол 1] Процес призупинено. Заплановано нові події:" << std::endl;
            for (const auto& ev : ctx.get_new_events()) {
                if (auto sched = std::get_if<ActivityScheduledEvent>(&ev)) {
                    std::cout << "  -> Scheduled Activity: " << sched->activity_name 
                              << " (Input: " << sched->input << ")" << std::endl;
                    // В реальності диспетчер відправляє задачу у чергу
                    history.push_back(ev);
                }
            }
        }
    }

    // ── Емуляція виконання Activity воркером та збереження результату ──────
    std::cout << "\n[Activity Worker] Виконано ProcessPayment -> повернено 'PAYMENT_OK_#9981'" << std::endl;
    history.push_back(ActivityCompletedEvent{"ProcessPayment", "PAYMENT_OK_#9981"});

    // ── АВАРІЯ СЕРВЕРА: Вузол 1 згорів, пам'ять стерто! ──────────────────
    std::cout << "\n!!! АВАРІЯ: Сервер Вузол 1 впав. Локальний стан знищено. Перезапуск на Вузлі 2..." << std::endl;

    // ── Ітерація 2: Відновлення на Вузлі 2 через Replay ───────────────────
    std::cout << "\n[Вузол 2] Підхоплення задачі з історії (Replay). Розмір історії: " 
              << history.size() << " подій." << std::endl;
    {
        WorkflowContext ctx(history);
        try {
            order_fulfillment_workflow(ctx, "order-101");
        } catch (const ExecutionYieldedException&) {
            std::cout << "[Вузол 2] Replay успішно відновив крок 1 без повторного виклику платежу!" << std::endl;
            std::cout << "[Вузол 2] Заплановано наступний крок:" << std::endl;
            for (const auto& ev : ctx.get_new_events()) {
                if (auto sched = std::get_if<ActivityScheduledEvent>(&ev)) {
                    std::cout << "  -> Scheduled Activity: " << sched->activity_name 
                              << " (Input: " << sched->input << ")" << std::endl;
                    history.push_back(ev);
                }
            }
        }
    }

    // ── Завершення решти кроків ──────────────────────────────────────────
    history.push_back(ActivityCompletedEvent{"ReserveInventory", "INVENTORY_RESERVED"});
    history.push_back(ActivityCompletedEvent{"CreateShippingLabel", "TRACKING_UA_12345"});

    std::cout << "\n[Вузол 2] Фінальний запуск (всі кроки виконано)..." << std::endl;
    {
        WorkflowContext ctx(history);
        std::string final_result = order_fulfillment_workflow(ctx, "order-101");
        std::cout << "[Вузол 2] Результат завершення: " << final_result << std::endl;
    }

    return 0;
}
```
```go
func main() {
	fmt.Println("=== СТАРТ РОБОЧОГО ПРОЦЕСУ ===")
	history := []WorkflowEvent{
		{Type: EventWorkflowStarted, Input: "user=Andrii"},
	}

	// Ітерація 1: Перший запуск
	ctx1 := NewWorkflowContext(history)
	_, err := OrderFulfillmentWorkflow(ctx1, "order-101")
	if errors.Is(err, ErrYield) {
		fmt.Println("[Вузол 1] Заплановано активність:", ctx1.newEvents[0].ActivityName)
		history = append(history, ctx1.newEvents...)
	}

	// Емуляція виконання активності
	fmt.Println("[Worker] Виконано ProcessPayment -> OK")
	history = append(history, WorkflowEvent{
		Type:         EventActivityCompleted,
		ActivityName: "ProcessPayment",
		Result:       "PAYMENT_OK_#9981",
	})

	// Аварія та Replay на Вузлі 2
	fmt.Println("\n!!! Аварія Вузла 1 -> Replay на Вузлі 2")
	ctx2 := NewWorkflowContext(history)
	_, err = OrderFulfillmentWorkflow(ctx2, "order-101")
	if errors.Is(err, ErrYield) {
		fmt.Println("[Вузол 2] Replay пройшов! Наступна активність:", ctx2.newEvents[0].ActivityName)
		history = append(history, ctx2.newEvents...)
	}
}
```
:::

## Глибокий аналіз механіки Replay та крайових випадків

Розглянута мінімальна реалізація розкриває кілька критично важливих принципів функціонування розподілених незнищенних систем:

### 1. Механіка призупинення: чому застосовано виняток Yield

У нашому C++ прикладі для призупинення виконання використано `ExecutionYieldedException`. Коли код процесу викликає `execute_activity`, для якої ще немає результату в історії, продовжувати виконання поточного потоку синхронно неможливо: результат операції буде відомий лише через кілька секунд чи діб.

Викидання контрольованого винятку дозволяє миттєво згорнути стек викликів (`unwind stack`), повернути керування у диспетчер воркера та зберегти всі заплановані команди (`new_events_`) у транзакційне сховище. У повнофункціональних SDK промислових рушіїв замість винятків використовуються:
* **Зелені потоки (Green Threads / Coroutines):** у мовах Go та Python SDK запускає функцію процесу в ізольованій горутині чи корутині, блокуючи її на каналі до отримання результату з історії.
* **Асинхронні генератори та проміси:** у TypeScript та C# використовується компіляторний механізм `async/await`, де кожен виклик активності повертає спеціальний `DurablePromise`, стан якого контролюється рушієм.

### 2. Виявлення розбіжностей історії (Non-determinism Detection)

Зверніть увагу на перевірку всередині методу `execute_activity`:
```cpp
if (completed->activity_name != name) {
    throw NonDeterminismException(...);
}
```
Якщо розробник змінить код працюючого процесу — наприклад, поміняє місцями кроки `ProcessPayment` та `ReserveInventory` — новий воркер під час replay отримає команду виконати `ReserveInventory`, тоді як перший запис в історії свідчить про `ProcessPayment`. 

Рушій миттєво фіксує розбіжність і блокує процес. Це фундаментальна гарантія безпеки: рушій ніколи не дозволить коду піти іншим шляхом над уже зафіксованою історією, запобігаючи незворотному пошкодженню бізнес-даних.

### 3. Оптимізація продуктивності: кешування стану проти Replay

У наївній реалізації кожна нова подія змушує воркер перечитувати історію з бази даних і проганяти функцію від початку. Якщо процес містить 50 кроків, для 50-го кроку воркер виконає 50 ітерацій replay.

Для усунення цих накладних витрат промислові платформи застосовують **кешування стеків у пам'яті (Sticky Execution / Worker Cache)**:
* Доки воркер живий і має вільну пам'ять, він утримує призупинену корутину процесу в оперативній пам'яті.
* Коли приходить результат нової активності, воркер не перезапускає процес з нуля, а просто розблоковує потік і передає результат у точку очікування.
* Повний Replay виконується **лише тоді**, коли воркер зазнав аварії, задача мігрувала на інший сервер або процес було витіснено з кешу через брак пам'яті (LRU eviction).

Завдяки цьому середня латентність кроку в гарячому стані вимірюється частками мілісекунди, а надійність зберігається на рівні розподіленої бази даних.
