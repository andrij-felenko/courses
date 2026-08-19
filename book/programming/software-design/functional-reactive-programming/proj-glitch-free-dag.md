# ⚙️ Реалізація реактивного графа без глітчів: push-pull топологія

Коли розробник намагається самостійно написати реактивну систему на основі класичного патерна «Спостерігач» (*Observer*), перша ж розгалужена структура залежностей стикається з проблемою **ромбоподібної залежності** (англ. *Diamond Dependency Problem*).

Уявімо типову ситуацію в архітектурі інтерфейсу або розрахункового рушія. У нас є базове джерело `A` (наприклад, курс валюти або ширина контейнера). Від цього джерела залежать два проміжні обчислювані значення: `B = f(A)` (ціна у валюті з урахуванням податку) та `C = g(A)` (знижка клієнта у тій самій валюті). Кінцевий вузол `D = h(B, C)` формує підсумковий чек, додаючи значення `B` та `C`. Граф залежностей утворює форму ромба: `A` розгалужується на `B` та `C`, які потім знову сходяться у `D`.

Якщо реактивна система побудована на наївному синхронному сповіщенні підписників (*naive push*), зміна значення в джерелі `A` викликає ланцюгову реакцію викликів функцій у випадковому порядку підписки. Якщо гілка `B` обробляється першою, вона негайно викликає оновлення вузла `D`. У цей момент вузол `D` починає перерахунок: він бере свіже, щойно оновлене значення з `B`, але з вузла `C` зчитує застаріле значення, оскільки сповіщення до гілки `C` ще фізично не дійшло по стеку викликів. 

У результаті вузол `D` на короткий проміжок часу переходить у хибний, математично неможливий стан. Через частку мілісекунди сповіщення доходить до `C`, `C` оновлюється і смикає `D` вдруге. Вузол `D` нарешті стає коректним, але шкоди вже завдано: якщо `D` був прив'язаний до виклику мережевого запиту, відмальовки пікселів на екрані або розрахунку фізики, користувач бачить миготіння (*glitch*), система відправляє некоректний дублюючий запит на сервер або падає через проміжне ділення на нуль.

У цій практичній вставці ми реалізуємо повноцінний мінімальний реактивний рушій на основі **двоетапного алгоритму Push-Pull із динамічним відстеженням залежностей, автоматичним очищенням старих підписок та пакетуванням транзакцій** двома мовами: **TypeScript** (для веб- та прикладних систем) та **C++20** (для системного та високопродуктивного програмування).

## Чому наївний підхід ламається: детальний розбір викликів

Погляньмо, як розгортається стек викликів у наївній системі на основі звичайних масивів слухачів `listeners.forEach(fn => fn())`:

```
1. Користувач викликає: A.set(2)  [початковий стан: A=1, B=2, C=2, D=4]
2. Джерело A сповіщає підписника B:
   → B обчислює B = 2 + 1 = 3
   → B одразу сповіщає свого підписника D
     → D обчислює D = B.get() + C.get()
     → D бачить: B = 3 (нове!), але C = 2 (старе!)
     → D отримує тимчасове значення 5 (ГЛІТЧ!)
     → D запускає зовнішній ефект із числом 5
3. Джерело A повертається до свого циклу і сповіщає підписника C:
   → C обчислює C = 2 * 2 = 4
   → C сповіщає підписника D
     → D обчислює D = B.get() + C.get()
     → D бачить: B = 3, C = 4
     → D отримує коректне фінальне значення 7
     → D запускає зовнішній ефект удруге з числом 7
```

Проблема полягає у змішуванні двох різних відповідальностей в один синхронний прохід: **сповіщення про факт зміни** та **безпосереднього обчислення нових значень**.

## Архітектура рішення: Двоетапний Push-Pull граф

Щоб гарантувати строгу транзакційність і повну відсутність глітчів (*Glitch Freedom*), сучасні реактивні архітектури (від дослідницької системи Flapjax до SolidJS та Preact Signals) розділяють реакцію на дві чіткі фази:

### Фаза 1: Push (Поширення міток застарілості)

Коли значення в базовому джерелі змінюється, система **не викликає жодних користувацьких обчислень чи формул**. Натомість джерело лише виставляє бітовий прапорець `isDirty = true` усім своїм прямим нащадкам. Нащадки рекурсивно передають цей прапорець далі вниз за графом усім своїм споживачам.

Ця фаза є надзвичайно дешевою: вона виконує виключно прохід по графу зі встановленням булевих прапорців або зміною числових станів. Жодна складна функція, фільтрація масиву чи відмальовка інтерфейсу на цьому кроці не запускається. Усі залежні вузли тепер просто знають: «мої вхідні дані змінилися, моє поточне закешоване значення більше не є дійсним».

### Фаза 2: Pull (Топологічне або ліниве чисте зчитування)

Коли кінцевий споживач (користувацький інтерфейс, фоновий процес або реактивний ефект) потребує актуального значення:

1. Він звертається до вузла через метод зчитування (`get()`).
2. Вузол перевіряє свій прапорець `isDirty`. Якщо вузол чистий (`isDirty == false`), він миттєво повертає вже збережене значення з кешу без жодних розрахунків.
3. Якщо вузол брудний (`isDirty == true`), він **спочатку рекурсивно вимагає оновлення від усіх своїх батьківських вузлів**.
4. Оскільки оновлення батьківських вузлів відбувається до того, як поточний вузол запустить власну формулу, на момент виконання формули **всі входи гарантовано мають найсвіжіші, узгоджені значення з однієї і тієї самої транзакції**.
5. Вузол обчислює своє значення рівно один раз, записує результат у кеш і скидає свій прапорець `isDirty = false`.

Якщо обчислене значення вузла виявилося ідентичним до попереднього (наприклад, `Math.floor(x)` дало те саме ціле число), система може взагалі зупинити подальше поширення оновлення вниз по гілці (*pruning*).

## Динамічне відстеження залежностей і запобігання витокам

Справжній реактивний граф не є статичним. Розглянемо вираз з умовним тернарним оператором:

```ts
const dynamicMsg = createComputed(() => {
  return showDetails() ? detailedInfo() : summaryInfo();
});
```

Коли `showDetails()` дорівнює `false`, вузол `dynamicMsg` взагалі не повинен слухати зміни в `detailedInfo()`. Якщо `detailedInfo()` оновлюватиметься тисячу разів на секунду, `dynamicMsg` не має витрачати такти на перерахунок. Ба більше, якщо `detailedInfo` триматиме посилання на `dynamicMsg` у своєму списку підписників, виникає класичний **витік пам'яті застарілого слухача** (*lapsed listener problem*).

Для вирішення цієї проблеми рушій реалізує **автоматичне динамічне відстеження**:

- Перед виконанням функції формули активний вузол встановлюється в глобальний контекстний стек (`activeSubscriber`).
- Під час обчислення кожен викликаний `get()` джерела автоматично реєструє пару «джерело ↔ споживач».
- Старий набір підписок порівнюється з новим, і вузол автоматично відписується від тих джерел, які більше не брали участі в останньому проході обчислення.

## Пакетування транзакцій (Batching)

Якщо програма послідовно змінює три пов'язані сигнали:

```ts
setFirstName("Тарас");
setLastName("Шевченко");
setAge(47);
```

Ми не хочемо, щоб кінцевий ефект (наприклад, генерація HTML-картки) запускався тричі. Функція `batch(fn)` призупиняє запуск другої фази (Pull/Run) доти, доки всі зміни всередині синхронного блоку не завершаться, після чого виконує єдине топологічно узгоджене оновлення.

## Робоча реалізація двома мовами

Нижче наведено повні, повністю функціональні реалізації реактивного рушія з підтримкою `Signal`, `Computed`, `Effect`, динамічного відстеження та `batch`.

:::tabs
```ts
// TypeScript: Повноцінний реактивний граф без глітчів із динамічними залежностями та batch

export interface Subscriber {
  markDirty(): void;
  run(): void;
}

export interface Dependency {
  removeSubscriber(sub: Subscriber): void;
}

// ── Глобальний контекст виконання ────────────────────────────────────────────
let activeSubscriber: (Subscriber & { addDependency(dep: Dependency): void }) | null = null;
const subscriberStack: typeof activeSubscriber[] = [];

let batchDepth = 0;
const pendingEffects = new Set<Subscriber>();

export function pushContext(sub: typeof activeSubscriber): void {
  subscriberStack.push(activeSubscriber);
  activeSubscriber = sub;
}

export function popContext(): void {
  activeSubscriber = subscriberStack.pop() ?? null;
}

export function batch<T>(fn: () => T): T {
  batchDepth++;
  try {
    return fn();
  } finally {
    batchDepth--;
    if (batchDepth === 0) {
      // Виконуємо всі відкладені ефекти після завершення пакета
      const effectsToRun = Array.from(pendingEffects);
      pendingEffects.clear();
      for (const effect of effectsToRun) {
        effect.run();
      }
    }
  }
}

// ── 1. Signal (Джерело первинного стану) ──────────────────────────────────────
export class Signal<T> implements Dependency {
  private value: T;
  private subscribers = new Set<Subscriber>();

  constructor(initialValue: T) {
    this.value = initialValue;
  }

  get(): T {
    if (activeSubscriber) {
      this.subscribers.add(activeSubscriber);
      activeSubscriber.addDependency(this);
    }
    return this.value;
  }

  set(newValue: T): void {
    if (Object.is(this.value, newValue)) return;
    this.value = newValue;

    // Фаза 1: Push (позначаємо залежні вузли брудними)
    const subs = Array.from(this.subscribers);
    for (const sub of subs) {
      sub.markDirty();
    }

    // Фаза 2: Запуск споживачів (або відкладення при batch)
    for (const sub of subs) {
      if (batchDepth > 0) {
        pendingEffects.add(sub);
      } else {
        sub.run();
      }
    }
  }

  removeSubscriber(sub: Subscriber): void {
    this.subscribers.delete(sub);
  }
}

export function createSignal<T>(initial: T): [() => T, (val: T) => void] {
  const s = new Signal(initial);
  return [() => s.get(), (val: T) => s.set(val)];
}

// ── 2. Computed (Мемоізоване похідне обчислення) ─────────────────────────────
export class Computed<T> implements Subscriber, Dependency {
  private fn: () => T;
  private cachedValue!: T;
  private isDirty = true;
  private isEvaluating = false;
  private subscribers = new Set<Subscriber>();
  private dependencies = new Set<Dependency>();

  constructor(fn: () => T) {
    this.fn = fn;
  }

  addDependency(dep: Dependency): void {
    this.dependencies.add(dep);
  }

  removeSubscriber(sub: Subscriber): void {
    this.subscribers.delete(sub);
  }

  markDirty(): void {
    if (!this.isDirty) {
      this.isDirty = true;
      for (const sub of this.subscribers) {
        sub.markDirty();
      }
    }
  }

  run(): void {
    // Computed оновлюється ліниво при get(), але сповіщає своїх підписників
    for (const sub of Array.from(this.subscribers)) {
      if (batchDepth > 0) {
        pendingEffects.add(sub);
      } else {
        sub.run();
      }
    }
  }

  get(): T {
    if (this.isEvaluating) {
      throw new Error("Виявлено циклічну залежність у графі обчислень!");
    }

    if (activeSubscriber) {
      this.subscribers.add(activeSubscriber);
      activeSubscriber.addDependency(this);
    }

    if (this.isDirty) {
      // Очищаємо старі залежності перед новим виконанням формули
      for (const dep of this.dependencies) {
        dep.removeSubscriber(this);
      }
      this.dependencies.clear();

      this.isEvaluating = true;
      pushContext(this);
      try {
        const newValue = this.fn();
        this.cachedValue = newValue;
        this.isDirty = false;
      } finally {
        popContext();
        this.isEvaluating = false;
      }
    }

    return this.cachedValue;
  }
}

export function createComputed<T>(fn: () => T): () => T {
  const c = new Computed(fn);
  return () => c.get();
}

// ── 3. Effect (Кінцевий споживач / Ефект) ─────────────────────────────────────
export class Effect implements Subscriber {
  private fn: () => void;
  private isDirty = true;
  private isRunning = false;
  private dependencies = new Set<Dependency>();

  constructor(fn: () => void) {
    this.fn = fn;
    this.run();
  }

  addDependency(dep: Dependency): void {
    this.dependencies.add(dep);
  }

  markDirty(): void {
    this.isDirty = true;
  }

  run(): void {
    if (!this.isDirty || this.isRunning) return;

    // Очищаємо підписки попереднього запуску
    for (const dep of this.dependencies) {
      dep.removeSubscriber(this);
    }
    this.dependencies.clear();

    this.isDirty = false;
    this.isRunning = true;
    pushContext(this);
    try {
      this.fn();
    } finally {
      popContext();
      this.isRunning = false;
    }
  }

  dispose(): void {
    for (const dep of this.dependencies) {
      dep.removeSubscriber(this);
    }
    this.dependencies.clear();
  }
}

export function createEffect(fn: () => void): () => void {
  const e = new Effect(fn);
  return () => e.dispose();
}

// ── Демонстрація перевірки на відсутність глітчів ────────────────────────────
const [a, setA] = createSignal(1);

const b = createComputed(() => {
  const v = a();
  console.log(`  [Обчислення B] a + 1 = ${v + 1}`);
  return v + 1;
});

const c = createComputed(() => {
  const v = a();
  console.log(`  [Обчислення C] a * 2 = ${v * 2}`);
  return v * 2;
});

const d = createComputed(() => {
  const bVal = b();
  const cVal = c();
  console.log(`  [Обчислення D] B(${bVal}) + C(${cVal}) = ${bVal + cVal}`);
  return bVal + cVal;
});

console.log("=== Початкове створення Effect ===");
createEffect(() => {
  console.log(`-> ГОЛОВНИЙ РЕЗУЛЬТАТ D = ${d()}`);
});

console.log("\n=== Зміна a: 1 -> 2 (без глітчів) ===");
setA(2);

console.log("\n=== Пакетна зміна (batch) ===");
batch(() => {
  setA(3);
  setA(5);
});
```
```cpp
// C++20: Типобезпечний двоетапний реактивний граф без глітчів із RAII та batch

#include <iostream>
#include <memory>
#include <vector>
#include <functional>
#include <unordered_set>
#include <stdexcept>
#include <cassert>

class IDependency;

class ISubscriber {
public:
    virtual ~ISubscriber() = default;
    virtual void mark_dirty() = 0;
    virtual void run() = 0;
    virtual void add_dependency(std::shared_ptr<IDependency> dep) = 0;
};

class IDependency {
public:
    virtual ~IDependency() = default;
    virtual void remove_subscriber(ISubscriber* sub) = 0;
};

// ── Глобальний контекст активного підписника ──────────────────────────────────
inline ISubscriber* g_active_subscriber = nullptr;
inline int g_batch_depth = 0;
inline std::unordered_set<ISubscriber*> g_pending_effects;

struct ContextGuard {
    ISubscriber* prev;
    explicit ContextGuard(ISubscriber* next) : prev(g_active_subscriber) {
        g_active_subscriber = next;
    }
    ~ContextGuard() {
        g_active_subscriber = prev;
    }
};

template <typename Func>
auto batch(Func&& fn) {
    g_batch_depth++;
    try {
        if constexpr (std::is_void_v<std::invoke_result_t<Func>>) {
            fn();
            g_batch_depth--;
            if (g_batch_depth == 0) {
                auto effects = g_pending_effects;
                g_pending_effects.clear();
                for (auto* eff : effects) {
                    eff->run();
                }
            }
        } else {
            auto res = fn();
            g_batch_depth--;
            if (g_batch_depth == 0) {
                auto effects = g_pending_effects;
                g_pending_effects.clear();
                for (auto* eff : effects) {
                    eff->run();
                }
            }
            return res;
        }
    } catch (...) {
        g_batch_depth--;
        throw;
    }
}

// ── 1. Signal (Джерело даних) ────────────────────────────────────────────────
template <typename T>
class Signal : public IDependency, public std::enable_shared_from_this<Signal<T>> {
private:
    T value_;
    std::unordered_set<ISubscriber*> subscribers_;

public:
    explicit Signal(T initial) : value_(std::move(initial)) {}

    const T& get() {
        if (g_active_subscriber) {
            subscribers_.insert(g_active_subscriber);
            g_active_subscriber->add_dependency(this->shared_from_this());
        }
        return value_;
    }

    void set(T new_value) {
        if (value_ == new_value) return;
        value_ = std::move(new_value);

        auto subs = subscribers_;
        // Фаза 1: Push Dirty
        for (auto* sub : subs) {
            sub->mark_dirty();
        }
        // Фаза 2: Pull / Run
        for (auto* sub : subs) {
            if (g_batch_depth > 0) {
                g_pending_effects.insert(sub);
            } else {
                sub->run();
            }
        }
    }

    void remove_subscriber(ISubscriber* sub) override {
        subscribers_.erase(sub);
    }
};

// ── 2. Computed (Мемоізоване похідне обчислення) ─────────────────────────────
template <typename T>
class Computed : public ISubscriber, public IDependency, public std::enable_shared_from_this<Computed<T>> {
private:
    std::function<T()> fn_;
    T cached_value_{};
    bool is_dirty_{true};
    bool is_evaluating_{false};
    std::unordered_set<ISubscriber*> subscribers_;
    std::unordered_set<std::shared_ptr<IDependency>> dependencies_;

public:
    explicit Computed(std::function<T()> fn) : fn_(std::move(fn)) {}

    void add_dependency(std::shared_ptr<IDependency> dep) override {
        dependencies_.insert(std::move(dep));
    }

    void remove_subscriber(ISubscriber* sub) override {
        subscribers_.erase(sub);
    }

    void mark_dirty() override {
        if (!is_dirty_) {
            is_dirty_ = true;
            for (auto* sub : subscribers_) {
                sub->mark_dirty();
            }
        }
    }

    void run() override {
        auto subs = subscribers_;
        for (auto* sub : subs) {
            if (g_batch_depth > 0) {
                g_pending_effects.insert(sub);
            } else {
                sub->run();
            }
        }
    }

    const T& get() {
        if (is_evaluating_) {
            throw std::runtime_error("Виявлено циклічну залежність у реактивному графі!");
        }

        if (g_active_subscriber) {
            subscribers_.insert(g_active_subscriber);
            g_active_subscriber->add_dependency(this->shared_from_this());
        }

        if (is_dirty_) {
            // Очищення старих залежностей перед перерахунком
            for (auto& dep : dependencies_) {
                dep->remove_subscriber(this);
            }
            dependencies_.clear();

            is_evaluating_ = true;
            ContextGuard guard(this);
            try {
                cached_value_ = fn_();
                is_dirty_ = false;
                is_evaluating_ = false;
            } catch (...) {
                is_evaluating_ = false;
                throw;
            }
        }
        return cached_value_;
    }
};

// ── 3. Effect (Кінцевий споживач) ────────────────────────────────────────────
class Effect : public ISubscriber {
private:
    std::function<void()> fn_;
    bool is_dirty_{true};
    bool is_running_{false};
    std::unordered_set<std::shared_ptr<IDependency>> dependencies_;

public:
    explicit Effect(std::function<void()> fn) : fn_(std::move(fn)) {
        run();
    }

    ~Effect() override {
        dispose();
    }

    void add_dependency(std::shared_ptr<IDependency> dep) override {
        dependencies_.insert(std::move(dep));
    }

    void mark_dirty() override {
        is_dirty_ = true;
    }

    void run() override {
        if (!is_dirty_ || is_running_) return;

        for (auto& dep : dependencies_) {
            dep->remove_subscriber(this);
        }
        dependencies_.clear();

        is_dirty_ = false;
        is_running_ = true;
        ContextGuard guard(this);
        try {
            fn_();
            is_running_ = false;
        } catch (...) {
            is_running_ = false;
            throw;
        }
    }

    void dispose() {
        for (auto& dep : dependencies_) {
            dep->remove_subscriber(this);
        }
        dependencies_.clear();
    }
};

// ── Демонстрація роботи ──────────────────────────────────────────────────────
int main() {
    auto a = std::make_shared<Signal<int>>(1);

    auto b = std::make_shared<Computed<int>>([a]() {
        int v = a->get();
        std::cout << "  [C++ B] a + 1 = " << (v + 1) << "\n";
        return v + 1;
    });

    auto c = std::make_shared<Computed<int>>([a]() {
        int v = a->get();
        std::cout << "  [C++ C] a * 2 = " << (v * 2) << "\n";
        return v * 2;
    });

    auto d = std::make_shared<Computed<int>>([b, c]() {
        int bv = b->get();
        int cv = c->get();
        std::cout << "  [C++ D] B(" << bv << ") + C(" << cv << ") = " << (bv + cv) << "\n";
        return bv + cv;
    });

    std::cout << "=== Створення Effect ===\n";
    auto effect = std::make_unique<Effect>([d]() {
        std::cout << "-> ГОЛОВНИЙ РЕЗУЛЬТАТ D = " << d->get() << "\n";
    });

    std::cout << "\n=== Зміна a: 1 -> 2 (без глітчів) ===\n";
    a->set(2);

    std::cout << "\n=== Пакетне оновлення (batch) ===\n";
    batch([&]() {
        a->set(3);
        a->set(5);
    });

    return 0;
}
```
:::

## Аналіз складності та інваріантів

Порівняємо характеристики трьох архітектур реактивного оновлення:

| Підхід | Складність оновлення | Захист від глітчів | Зайві обчислення неактивних гілок |
| :--- | :--- | :--- | :--- |
| **Наївний Push (Observer)** | `O(|E|)` | ❌ Немає (виникають глітчі) | ❌ Так (обчислює все поспіль) |
| **Чистий Pull (Повне опитування)** | `O(|V| + |E|)` | ✅ Є | ❌ Так (опитує навіть незмінені гілки) |
| **Двоетапний Push-Pull (Signals)** | `O(|E_dirty|) + O(|V_used|)` | ✅ Повна транзакційність | ✅ Ні (обчислює тільки змінене й затребуване) |

## Топологічні ранги проти рекурсивного Push-Pull: дві школи реалізації

У практиці побудови реактивних бібліотек існують два основні способи гарантування властивості Glitch Freedom:

### 1. Рекурсивний Push-Pull (підхід SolidJS, Preact Signals)

Саме цей підхід ми реалізували вище. Його перевага — мінімальне споживання оперативної пам'яті та природна робота з динамічними графами, які змінюють свою форму під час виконання. Вузлу не потрібно зберігати глобальний номер рангу або підтримувати масив рівнів. Позначення `isDirty` спускається вниз рекурсивно, а зчитування підтягує актуальний стан батьків перед обчисленням формули.

Єдине обмеження рекурсивного підходу — глибина графа. Якщо ланцюг залежностей налічує тисячі послідовних вузлів `A₁ → A₂ → ... → A₁₀₀₀₀`, глибока рекурсія у фазі читання може призвести до вичерпання стека викликів (*call stack overflow*). У таких випадках рекурсію замінюють ітеративним обходом за допомогою внутрішнього стека вузлів.

### 2. Черга пріоритетів на основі топологічних рангів (підхід MobX, Flapjax)

У цій моделі кожен вузол має цілочисельний ранг `rank`, який дорівнює максимальному рангу його предків плюс один: `rank(v) = 1 + max(rank(u))`. 

Коли джерело змінюється, усі залежні вузли додаються не у звичайний масив сповіщень, а в **двійкову купу або масив списків за рангами** (*priority queue by rank*). Планувальник завжди витягує з черги вузол із найменшим рангом. Оскільки будь-який предок `u` гарантовано має `rank(u) < rank(v)`, на момент вилучення вузла `v` з черги всі його предки вже гарантовано обчислені й мають актуальні значення.

Перевага підходу з рангами полягає у строго ітеративному виконанні без рекурсії та можливості оптимального планування черг виконання у фонових потоках. Недоліком є необхідність перераховувати ранги підграфа (*rank rebalancing*), коли динамічний вираз `if-else` підключає нову, глибшу гілку залежностей.

## Ізоляція читання: оператор `untrack`

У практичних програмах часто виникає потреба зчитати поточне значення реактивного сигналу всередині `Effect` або `Computed` так, щоб **не створювати постійної підписки**.

Наприклад, якщо ми записуємо подію аналітики при натисканні кнопки, нам потрібне поточне значення лічильника, але ми не хочемо, щоб зміна лічильника сама по собі повторно відправляла подію в аналітику.

Для цього використовується оператор `untrack`:

```ts
export function untrack<T>(fn: () => T): T {
  pushContext(null); // Тимчасово очищаємо активного підписника
  try {
    return fn();
  } finally {
    popContext();    // Відновлюємо попередній контекст
  }
}
```

Будь-який виклик сигналу всередині `untrack(() => count())` прочитає його значення з внутрішнього поля `value`, але оскільки `activeSubscriber == null`, реєстрації в масиві `subscribers` не відбудеться.

## Управління життєвим циклом: Дерева власників (Owner Scopes)

У великих додатках ручне збереження функцій повернення `dispose()` для кожного створеного ефекту швидко стає незручним. Якщо компонент інтерфейсу створює 20 сигналів і 10 ефектів, при демонтуванні компонента розробник має не забути викликати всі 10 функцій очищення.

Для автоматизації цього процесу сучасні реактивні рушії використовують концепцію **Дерева власників** (англ. *Owner Tree* / *Disposal Scope*).

- При створенні кореневого контексту (наприклад, через функцію `createRoot(fn)`) створюється вузол-власник `Owner`.
- Усі ефекти, створені всередині цієї функції, автоматично реєструються як дочірні вузли поточного активного власника.
- Коли батьківський компонент демонтується або знищується, викликається один метод `owner.dispose()`, який рекурсивно відписує всі дочірні ефекти від їхніх сигналів та звільняє пам'ять.

Це вирішує проблему «застарілих підписників» (*lapsed listeners*) на структурному рівні: реактивні зв'язки живуть рівно стільки, скільки живе екран або віджет, якому вони належать.

## Багатопотоковість та синхронізація у C++

Показана вище реалізація мовою C++ є однопотоковою і призначена для роботи в рамках одного циклу подій (*event loop*). Якщо реактивний граф використовується у багатопотоковому середовищі (наприклад, фоновий потік приймає телеметрію з сенсорів, а UI-потік рендерить графік), виникають додаткові вимоги до синхронізації:

1. **Захист множин підписників:** Додавання підписника під час читання та сповіщення під час запису мають синхронізуватися через `std::shared_mutex` (читачі беруть розділений лок `shared_lock`, запис бере ексклюзивний `unique_lock`).
2. **Атомарність транзакційного тіку:** Якщо два потоки одночасно змінюють два джерела `Signal A` та `Signal B`, оновлення графа має виконуватися в рамках глобального транзакційного замка (*transaction mutex*), інакше фази Push і Pull різних потоків можуть перемішатися, порушивши інваріант узгодженості станів.
3. **Ізоляція контексту потоку:** Глобальний вказівник на активного підписника `g_active_subscriber` у багатопотоковій системі обов'язково має бути позначений як `thread_local`, щоб обчислення в одному потоці не перехоплювали підписки паралельного потоку.

## Побудова користувацьких комбінаторів поверх сигналів

Маючи базові примітиви `Signal`, `Computed` та `Effect`, ми можемо виразити будь-які класичні оператори реактивного програмування без модифікації внутрішнього ядра рушія:

### 1. Комбінатор відображення (map / select)

Створює нове похідне обчислення, що застосовує функцію трансформації до джерела:

```ts
export function map<T, R>(source: () => T, transform: (val: T) => R): () => R {
  return createComputed(() => transform(source()));
}
```

### 2. Комбінатор фільтрації (filter / where)

Повертає значення, яке оновлюється лише тоді, коли нове значення джерела відповідає заданому предикату:

```ts
export function filter<T>(source: () => T, predicate: (val: T) => boolean, initial: T): () => T {
  let lastValid = initial;
  return createComputed(() => {
    const val = source();
    if (predicate(val)) {
      lastValid = val;
    }
    return lastValid;
  });
}
```

### 3. Комбінатор злиття (combineLatest)

Об'єднує кілька незалежних сигналів у єдиний кортеж або результат агрегації:

```ts
export function combine<T1, T2, R>(
  s1: () => T1,
  s2: () => T2,
  combiner: (v1: T1, v2: T2) => R
): () => R {
  return createComputed(() => combiner(s1(), s2()));
}
```

Оскільки всі ці комбінатори розгортаються у вузли `Computed`, вони автоматично успадковують повну захищеність від глітчів, ліниве кешування та динамічне очищення залежностей.

## Профайлінг та діагностика надлишкових обчислень

Під час розробки складних реактивних систем типовою проблемою є **прихований оверхед** (*over-computation*): вузли перераховуються частіше, ніж очікує інженер.

Для моніторингу роботи рушія в налагоджувальному режимі впроваджують лічильники викликів:

1. **Лічильник звернень до `fn()`:** якщо на одну зміну джерела `Signal` функція `Computed.fn()` викликається більше одного разу, це пряма ознака порушення топологічного порядку або наявності неізольованих побічних ефектів.
2. **Лічильник перепідписок:** якщо розмір множини `dependencies` змінюється на кожному тіку, це свідчить про наявність динамічних умовних гілок. У високонавантажених циклах постійне створення і видалення об'єктів підписок створює тиск на збирач сміття (GC pressure). У критичних до продуктивності ділянках варто замінювати динамічні гілки статичними комбінаціями з булевими масками.
3. **Оцінка накладних витрат пам'яті:**
   - У JavaScript/TypeScript кожен реактивний вузол із двома множинами `Set` займає орієнтовно 120–200 байтів у купі.
   - У C++ оптимізована структура з фіксованими векторами `std::vector` займає лише 48–64 байти на вузол, що дозволяє тримати мільйони активних реактивних змінних у межах кількох десятків мегабайтів RAM.

## Автоматизоване тестування та фазинг реактивних графів

Для гарантування надійності реактивного рушія в умовах складних динамічних графів застосовують **тестування на основі властивостей** (*Property-Based Testing*):

1. **Генерація випадкових ациклічних графів:** генератор створює випадковий граф із сотень сигналів та похідних вузлів із випадковими арифметичними функціями (`+`, `-`, `*`, `min`, `max`, `if-else`).
2. **Порівняння з еталоном:** для кожної випадкової мутації джерел результат кінцевих вузлів обчислюється двома шляхами: через оптимізований реактивний граф та через «наївне повне переобчислення з нуля» (*ground truth reference*).
3. **Інваріант еквівалентності:** реактивний рушій вважається коректним, якщо для будь-якої послідовності з 10 000 випадкових транзакцій значення всіх кінцевих ефектів байт-у-байт збігаються з еталонним перерахунком, а кількість викликів проміжних формул не перевищує розміру активного зміненого підграфа.

## Підводні камені та типові пастки

1. **Мутація сигналів усередині `Computed`:**
   Спроба записати нове значення в `Signal` усередині тіла `Computed` є грубим порушенням принципу чистоти (*side effect inside pure computation*). Це призводить до нескінченних циклів або інвалідації графа посеред фази читання. Похідні обчислення мають бути чистими функціями, які лише трансформують дані.
2. **Втрата реактивності через деструктуризацію:**
   У TypeScript/JavaScript початківці часто пишуть `const { count } = props` або `const val = mySignal()`, зберігаючи примітивне число у локальну змінну. Після цього зв'язок із реактивним графом втрачається: щоб зберегти реактивність, передавати потрібно сам аксесор `() => mySignal()`, а не його разове числове значення.
3. **Порівняння значень за замовчуванням:**
   Якщо сигнал зберігає об'єкт або масив, наївне порівняння `Object.is(oldVal, newVal)` або `oldVal == newVal` порівнює вказівники на пам'ять. Якщо мутувати поля всередині того самого об'єкта, сигнал вважатиме, що значення не змінилося, і не запустить оновлення. Реактивні джерела вимагають або використання **незмінних структур даних** (*immutable data*), де кожна зміна створює новий об'єкт, або передачі кастомної функції порівняння (*custom equality function*).
4. **Непередбачені повторні підписки при винятках:**
   Якщо функція обчислення викидає виняток, важливо гарантувати відновлення глобального контексту `activeSubscriber` за допомогою блоку `finally` у TypeScript або RAII-вартового `ContextGuard` у C++. Інакше наступний звичайний виклик функції помилково підпишеться на зламаний вузол.



