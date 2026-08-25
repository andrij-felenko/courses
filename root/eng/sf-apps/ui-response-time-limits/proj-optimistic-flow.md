# ⚙️ Реалізація оптимістичного оновлення зі стійким відкатом

Коли мережева операція збереження на сервері займає від 300 до 1500 мс (сумарний мережевий RTT плюс транзакція в базі даних), песимістичне очікування з блокуванням кнопки або крутінням спінера грубо порушує поріг прямої маніпуляції 100 мс. Інтерфейс виглядає повільним і «задумливим», а безперервний потік дій користувача розривається на кожному кліку.

Оптимістичний патерн (*Optimistic UI*) розв'язує цю архітектурну суперечність: клієнтський стан оновлюється **синхронно за <16–30 мс**, а мережевий запит виконується асинхронно у фоні. Якщо сервер повертає помилку або мережевий запит переривається за таймаутом, система автоматично відновлює попередній підтверджений стан та показує користувачеві ненав'язливе сповіщення про збій.

## Архітектура сховища з чергою мутацій

Стійка реалізація оптимістичного інтерфейсу базується на принципі двох шарів стану з чергою відкладених операцій:

1. **Підтверджений стан (`committedState`):** канонічна копія стану, підтверджена сервером. Вона змінюється виключно тоді, коли з бекенду приходить успішна відповідь з кодом `200 OK`.
2. **Оптимістичний стан (`optimisticState`):** робочий стан, який безпосередньо відображається у компонентах інтерфейсу. Він миттєво мутує при будь-якій дії користувача.
3. **Черга незавершених мутацій (`pendingMutations`):** впорядкований список активних операцій, які зараз летять мережею. Кожна мутація інкапсулює унікальний ідентифікатор транзакції, функцію прямої зміни (`apply`), функцію інверсії (`rollback`) та асинхронну дію виконання (`execute`).
4. **Механізм перебазування (`rebase`):** якщо одна з проміжних мутацій зазнає невдачі, стан не можна просто «відкотити на один крок назад», оскільки користувач міг устигнути зробити наступні дії поверх неї. Сховище скидає `optimisticState` до рівня `committedState`, вилучає зі списку дефектну мутацію та послідовно перезастосовує всі інші активні операції.

## Реалізація на TypeScript та Modern C++

У наведених нижче прикладах реалізовано повноцінне оптимістичне сховище списку задач. Обидва варіанти гарантують синхронний час реакції `<1 мс` для підписників інтерфейсу, зберігаючи повну безпеку відновлення при помилках мережі.

:::tabs
```ts
// TypeScript: Оптимістичне сховище з чергою мутацій та стійким перебазуванням

export interface Task {
  readonly id: string;
  readonly title: string;
  readonly completed: boolean;
}

export interface AppState {
  readonly tasks: readonly Task[];
}

export interface Mutation<T> {
  readonly id: string;
  readonly apply: (state: T) => T;
  readonly rollback: (state: T) => T;
  readonly execute: () => Promise<void>;
}

export class OptimisticStore<T> {
  private committedState: T;
  private optimisticState: T;
  private pendingMutations: Mutation<T>[] = [];
  private listeners: Set<(state: T) => void> = new Set();

  constructor(initialState: T) {
    this.committedState = initialState;
    this.optimisticState = initialState;
  }

  public getState(): T {
    return this.optimisticState;
  }

  public subscribe(listener: (state: T) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    for (const listener of this.listeners) {
      listener(this.optimisticState);
    }
  }

  /**
   * Застосовує мутацію оптимістично та запускає фонове збереження
   */
  public async dispatch(mutation: Mutation<T>): Promise<boolean> {
    // 1. Миттєве оновлення інтерфейсу (виконується за <1 мс, гарантує поріг 100 мс)
    this.pendingMutations.push(mutation);
    this.optimisticState = mutation.apply(this.optimisticState);
    this.notify();

    // 2. Фонова передача на сервер
    try {
      await mutation.execute();

      // 3. Успіх: фіксуємо мутацію у підтвердженому стані
      this.committedState = mutation.apply(this.committedState);
      this.pendingMutations = this.pendingMutations.filter((m) => m.id !== mutation.id);
      return true;
    } catch (error) {
      // 4. Помилка: відкат та перебазування решти активних мутацій
      this.pendingMutations = this.pendingMutations.filter((m) => m.id !== mutation.id);
      this.rebase();
      this.notify();
      return false;
    }
  }

  /**
   * Перебазування: повторне застосування всіх активних мутацій поверх останнього committed стану
   */
  private rebase(): void {
    let state = this.committedState;
    for (const pending of this.pendingMutations) {
      state = pending.apply(state);
    }
    this.optimisticState = state;
  }
}
```
```cpp
// C++20: Оптимістичне сховище стану клієнта з механізмом відкату (Rollback & Rebase)

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <future>
#include <algorithm>
#include <expected>

struct Task {
    std::string id;
    std::string title;
    bool completed{false};
};

struct AppState {
    std::vector<Task> tasks;
};

template <typename State>
struct Mutation {
    std::string id;
    std::function<State(const State&)> apply;
    std::function<State(const State&)> rollback;
    std::function<std::expected<void, std::string>()> execute;
};

template <typename State>
class OptimisticStore {
public:
    explicit OptimisticStore(State initial)
        : committedState_(std::move(initial)), optimisticState_(committedState_) {}

    const State& getState() const noexcept {
        return optimisticState_;
    }

    void subscribe(std::function<void(const State&)> listener) {
        listeners_.push_back(std::move(listener));
    }

    // Синхронно мутує оптимістичний стан (<1 мс) та повертає результат асинхронного комміту
    std::future<bool> dispatch(Mutation<State> mutation) {
        // 1. Миттєве локальне оновлення
        optimisticState_ = mutation.apply(optimisticState_);
        pendingMutations_.push_back(mutation);
        notify();

        // 2. Асинхронний комміт на сервер
        return std::async(std::launch::async, [this, id = mutation.id]() {
            // Знаходимо мутацію за ідентифікатором
            auto it = std::find_if(pendingMutations_.begin(), pendingMutations_.end(),
                                   [&](const auto& m) { return m.id == id; });
            if (it == pendingMutations_.end()) {
                return false;
            }
            auto currentMutation = *it;

            auto result = currentMutation.execute();
            if (result.has_value()) {
                // Успіх: фіксуємо в підтвердженому стані
                committedState_ = currentMutation.apply(committedState_);
                removeMutation(id);
                return true;
            } else {
                // Помилка: вилучаємо з черги та виконуємо rebase
                removeMutation(id);
                rebase();
                notify();
                return false;
            }
        });
    }

private:
    void notify() {
        for (const auto& listener : listeners_) {
            listener(optimisticState_);
        }
    }

    void removeMutation(const std::string& id) {
        pendingMutations_.erase(
            std::remove_if(pendingMutations_.begin(), pendingMutations_.end(),
                           [&](const auto& m) { return m.id == id; }),
            pendingMutations_.end()
        );
    }

    void rebase() {
        State state = committedState_;
        for (const auto& pending : pendingMutations_) {
            state = pending.apply(state);
        }
        optimisticState_ = std::move(state);
    }

    State committedState_;
    State optimisticState_;
    std::vector<Mutation<State>> pendingMutations_;
    std::vector<std::function<void(const State&)>> listeners_;
};
```
:::

## Збереження черги на диск для стійкості до перезавантажень

Якщо користувач закриє вкладку браузера або застосунок буде завершено операційною системою під час польоту мережевого запиту, стан у оперативній пам'яті буде втрачено. 

Щоб оптимістичні зміни переживали перезапуск програми, черга незавершених операцій серіалізується у локальне енергонезалежне сховище (IndexedDB у браузері або SQLite на нативних платформах):

1. **Запис у журнал перед відправкою (Write-Ahead Log):** Мутація записується в локальну базу даних до виклику `fetch()` чи сокета.
2. **Відновлення під час старту:** При наступному запуску застосунок спочатку завантажує останній підтверджений знімок, накладає збережені в базі незавершені мутації та фоново відновлює їх відправку на сервер.
3. **Очищення журналу:** Запис видаляється з локальної бази тільки після отримання підтвердження від сервера.

## Сценарії паралельних змін та крайові випадки

Застосування оптимістичного шаблону породжує низку тонких інженерних крайових випадків, які необхідно враховувати в архітектурі:

### 1. Перегони послідовних мутацій (Race Conditions)

Найчастіший випадок: користувач двічі поспіль клікає по перемикачу статусу задачі (з `completed: false` на `true`, і майже одразу назад на `false`). 
- Обидва кліки миттєво відтворюються на екрані, створюючи ідеальне відчуття чуйності.
- Запити відправляються мережею паралельно. Якщо перший запит затримався, а другий прийшов на сервер раніше, на бекенді стан може зафіксуватися у неправильному порядку.
- **Розв'язання:** Використання монотонних версій записів (*version vectors*), векторних годинників або послідовної відправки мутацій з черги для однієї сутності (*per-entity serialization queue*).

### 2. Таймаути та адаптивні повтори (Retry with Exponential Backoff)

Мережеві з'єднання мобільних пристроїв часто втрачають пакети під час переходу між базовими станціями або в зонах слабкого сигналу. Якщо фоновий запит підвисає, клієнт не повинен залишати мутацію в невагомості на десятки секунд.
- Встановлюється жорсткий клієнтський таймаут (типово 5.0–8.0 секунд через `AbortController`).
- При тимчасовому мережевому збої (наприклад, втрата зв'язку або код `503 Service Unavailable`) система виконує 2–3 автоматичні повторні спроби з експоненційним зростанням інтервалу та випадковим тремтінням (*exponential backoff with jitter*).
- Кожен запит зобов'язаний містити унікальний заголовок ідемпотентності `X-Idempotency-Key: <mutation-uuid>`, щоб повторна відправка при обриві з'єднання не призвела до дублювання запису на сервері.

### 3. Межі застосування оптимістичного підходу

Оптимістичний інтерфейс базується на фундаментальному припущенні: **ймовірність успіху операції перевищує 99%**. Якщо операція часто зазнає невдачі через бізнес-правила або валідацію, користувач бачитиме постійне «сіпання» інтерфейсу (стан змінився і раптово стрибнув назад), що руйнує довіру до системи.

Оптимістичний підхід **заборонено застосовувати** для:
- Фінансових транзакцій і списання грошових коштів (платіж може бути відхилений банком через брак коштів на рахунку);
- Незворотного видалення великих обсягів даних чи критичних облікових записів;
- Дій, що вимагають складного серверного розрахунку ціни, динамічного бронювання останніх місць на авіарейс або перевірки суворих прав доступу в реальному часі.

Для таких операцій єдино правильним підходом залишається **песимістичний сценарій** із явною зміною стану кнопки на «Обробка...» та делікатним мікро-індикатором завантаження.
