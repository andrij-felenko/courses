# ⚙️ Реалізація безпечного рушія Metadata-Driven UI

Клієнтський рушій Metadata-Driven UI перетворює декларативне синтаксичне дерево (AST) у працюючий нативний інтерфейс. Головний інженерний виклик полягає у забезпеченні динамічної поведінки — умовного відображення полів, реактивної валідації та міжпольових залежностей — без компрометації безпеки виконання.

Використання вбудованого інтерпретатора JavaScript (`eval()` або `new Function()`) для обчислення серверних виразів відкриває критичні вразливості до віддаленого виконання коду (Remote Code Execution, RCE) та прямо порушує правила публікації мобільних застосунків в Apple App Store (пункт 2.5.2) та Google Play Store. Надійний клієнтський рушій реалізує **ізольований Тюрінг-неповний обчислювач AST-виразів**, поєднаний з реактивним сховищем стану та реєстром компонентів.

## Архітектурний контур та розподіл обов'язків

Рушій будується на базі чотирьох взаємопов'язаних підсистем, кожна з яких відповідає за ізольовану фазу обробки метаданих:

1. **Сховище стану (Form State Store):** ієрархічний реактивний контейнер даних із підтримкою адресації шляхів за стандартом JSON Pointer (наприклад, `/billing/card/number`) та оповіщення підписників про локальні мутації.
2. **Безпечний обчислювач виразів (Safe AST Evaluator):** рекурсивний інтерпретатор логічних та порівняльних операцій. Він виконує обхід дерева виразу в глибину (depth-first post-order traversal), маючи доступ виключно до переданого контексту стану форми, і повністю ізольований від системних функцій платформи, пам'яті процесу чи мережевого сокета.
3. **Декларативний валідатор (Validation Engine):** механізм перевірки інваріантів введення зі збереженням карти помилок і підтримкою умовних перевірок (`when`), що активуються лише в заданих станах інтерфейсу.
4. **Реєстр та рендерер компонентів (Component Registry & Tree Dispatcher):** словник відображення строкових міток типів на нативні фабрики віджетів з автоматичною деградацією (Fallback) при виявленні невідомих вузлів.

---

## Реалізація рушія

:::tabs
```ts
// TypeScript: Безпечний клієнтський рантайм Metadata-Driven UI

export type JsonValue = string | number | boolean | null | JsonObject | JsonArray;
export interface JsonObject { [key: string]: JsonValue; }
export interface JsonArray extends Array<JsonValue> {}

// 1. Граматика безпечних виразів (Safe Expression AST)
export type Expression =
  | boolean
  | number
  | string
  | { var: string }
  | { op: "==" | "!=" | ">" | ">=" | "<" | "<="; left: Expression; right: Expression }
  | { op: "and" | "or"; args: Expression[] }
  | { op: "not"; arg: Expression }
  | { op: "regex"; value: Expression; pattern: string };

// 2. Декларативні вузли інтерфейсу
export interface ValidationRule {
  rule: "required" | "min_length" | "pattern" | "range";
  params?: any;
  message: string;
  when?: Expression;
}

export interface Action {
  type: "SET_STATE" | "NAVIGATE" | "SUBMIT_FORM";
  payload: Record<string, any>;
}

export interface UINode {
  id: string;
  type: string;
  props?: Record<string, any>;
  bind?: { value?: string };
  visibility?: Expression;
  enabled?: Expression;
  validation?: ValidationRule[];
  actions?: Record<string, Action>;
  children?: UINode[];
  fallback?: UINode;
}

// 3. Реактивне сховище стану (State Store)
export class StateStore {
  private state: Record<string, any> = {};
  private listeners = new Set<(path: string, val: any) => void>();

  constructor(initialState: Record<string, any> = {}) {
    this.state = JSON.parse(JSON.stringify(initialState));
  }

  public get(path: string): any {
    if (!path) return undefined;
    const cleanPath = path.startsWith("/") ? path.slice(1) : path;
    const segments = cleanPath.split("/").filter(Boolean);
    let current: any = this.state;
    for (const seg of segments) {
      if (current === null || current === undefined) return undefined;
      current = current[seg];
    }
    return current;
  }

  public set(path: string, value: any): void {
    const cleanPath = path.startsWith("/") ? path.slice(1) : path;
    const segments = cleanPath.split("/").filter(Boolean);
    if (!segments.length) return;

    let current: any = this.state;
    for (let i = 0; i < segments.length - 1; i++) {
      const seg = segments[i];
      if (!(seg in current) || typeof current[seg] !== "object") {
        current[seg] = {};
      }
      current = current[seg];
    }
    current[segments[segments.length - 1]] = value;
    this.listeners.forEach((fn) => fn(path, value));
  }

  public subscribe(fn: (path: string, val: any) => void): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  public getAll(): Record<string, any> {
    return JSON.parse(JSON.stringify(this.state));
  }
}

// 4. Безпечний обчислювач виразів без eval()
export class SafeExpressionEvaluator {
  public static evaluate(expr: Expression | undefined, store: StateStore): boolean | number | string | null {
    if (expr === undefined || expr === null) return true;
    if (typeof expr === "boolean" || typeof expr === "number" || typeof expr === "string") {
      return expr;
    }

    if ("var" in expr) {
      const val = store.get(expr.var);
      return val !== undefined ? val : null;
    }

    if ("op" in expr) {
      switch (expr.op) {
        case "==":
          return this.evaluate(expr.left, store) === this.evaluate(expr.right, store);
        case "!=":
          return this.evaluate(expr.left, store) !== this.evaluate(expr.right, store);
        case ">":
          return Number(this.evaluate(expr.left, store)) > Number(this.evaluate(expr.right, store));
        case ">=":
          return Number(this.evaluate(expr.left, store)) >= Number(this.evaluate(expr.right, store));
        case "<":
          return Number(this.evaluate(expr.left, store)) < Number(this.evaluate(expr.right, store));
        case "<=":
          return Number(this.evaluate(expr.left, store)) <= Number(this.evaluate(expr.right, store));
        case "and":
          return expr.args.every((arg) => Boolean(this.evaluate(arg, store)));
        case "or":
          return expr.args.some((arg) => Boolean(this.evaluate(arg, store)));
        case "not":
          return !this.evaluate(expr.arg, store);
        case "regex": {
          const target = String(this.evaluate(expr.value, store) ?? "");
          try {
            const re = new RegExp(expr.pattern);
            return re.test(target);
          } catch {
            return false;
          }
        }
      }
    }
    return false;
  }
}

// 5. Рушій валідації (Validation Engine)
export class ValidationEngine {
  public static validateField(val: any, rules: ValidationRule[] | undefined, store: StateStore): string | null {
    if (!rules || !rules.length) return null;

    for (const r of rules) {
      if (r.when && !SafeExpressionEvaluator.evaluate(r.when, store)) {
        continue;
      }
      switch (r.rule) {
        case "required":
          if (val === null || val === undefined || String(val).trim() === "") {
            return r.message;
          }
          break;
        case "min_length":
          if (val && String(val).length < Number(r.params)) {
            return r.message;
          }
          break;
        case "pattern":
          if (val && !new RegExp(r.params).test(String(val))) {
            return r.message;
          }
          break;
        case "range":
          const num = Number(val);
          if (r.params?.min !== undefined && num < r.params.min) return r.message;
          if (r.params?.max !== undefined && num > r.params.max) return r.message;
          break;
      }
    }
    return null;
  }
}

// 6. Реєстр компонентів та диспетчеризація рендерингу
export type ComponentRenderer = (node: UINode, store: StateStore, engine: SDUIEngine) => any;

export class SDUIEngine {
  private registry = new Map<string, ComponentRenderer>();
  public store: StateStore;

  constructor(initialState: Record<string, any> = {}) {
    this.store = new StateStore(initialState);
  }

  public register(type: string, renderer: ComponentRenderer): void {
    this.registry.set(type, renderer);
  }

  public dispatchAction(action: Action): void {
    switch (action.type) {
      case "SET_STATE":
        if (action.payload.path) {
          this.store.set(action.payload.path, action.payload.value);
        }
        break;
      case "SUBMIT_FORM":
        console.log("Відправка форми:", this.store.getAll());
        break;
      case "NAVIGATE":
        console.log("Перехід на екран:", action.payload.screen_id);
        break;
    }
  }

  public renderNode(node: UINode): any {
    // 1. Перевірка видимості
    const isVisible = SafeExpressionEvaluator.evaluate(node.visibility, this.store);
    if (!isVisible) return null;

    // 2. Пошук рендерера в реєстрі
    const renderer = this.registry.get(node.type);
    if (renderer) {
      return renderer(node, this.store, this);
    }

    // 3. Граційна деградація (Fallback)
    if (node.fallback) {
      return this.renderNode(node.fallback);
    }

    // Ігнорування невідомого вузла без падіння процесу
    return null;
  }
}
```
```cpp
// C++20: Нативний рушій інтерпретації метаданих Metadata-Driven UI

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <variant>
#include <regex>
#include <functional>

// 1. Представлення універсального JSON-значення
struct Value;
using Object = std::unordered_map<std::string, Value>;
using Array = std::vector<Value>;

struct Value {
    std::variant<std::nullptr_t, bool, double, std::string, Object, Array> data;

    Value() : data(nullptr) {}
    Value(bool b) : data(b) {}
    Value(double d) : data(d) {}
    Value(std::string s) : data(std::move(s)) {}
    Value(const char* s) : data(std::string(s)) {}
    Value(Object o) : data(std::move(o)) {}
    Value(Array a) : data(std::move(a)) {}

    bool as_bool() const {
        if (auto p = std::get_if<bool>(&data)) return *p;
        if (auto p = std::get_if<double>(&data)) return *p != 0.0;
        if (auto p = std::get_if<std::string>(&data)) return !p->empty();
        return false;
    }

    std::string as_string() const {
        if (auto p = std::get_if<std::string>(&data)) return *p;
        if (auto p = std::get_if<double>(&data)) return std::to_string(*p);
        if (auto p = std::get_if<bool>(&data)) return *p ? "true" : "false";
        return "";
    }
};

// 2. Реактивне сховище стану
class StateStore {
public:
    explicit StateStore(Object initial) : state_(std::move(initial)) {}

    Value get(std::string_view path) const {
        if (path.empty()) return Value();
        std::string p(path.starts_with('/') ? path.substr(1) : path);
        size_t start = 0;
        const Object* cur = &state_;

        while (start < p.size()) {
            size_t end = p.find('/', start);
            std::string key = (end == std::string::npos) ? p.substr(start) : p.substr(start, end - start);
            auto it = cur->find(key);
            if (it == cur->end()) return Value();

            if (end == std::string::npos) {
                return it->second;
            }
            if (auto obj = std::get_if<Object>(&it->second.data)) {
                cur = obj;
            } else {
                return Value();
            }
            start = end + 1;
        }
        return Value();
    }

    void set(std::string_view path, Value val) {
        std::string p(path.starts_with('/') ? path.substr(1) : path);
        state_[p] = std::move(val);
        for (auto& cb : listeners_) cb(p);
    }

    void subscribe(std::function<void(const std::string&)> cb) {
        listeners_.push_back(std::move(cb));
    }

private:
    Object state_;
    std::vector<std::function<void(const std::string&)>> listeners_;
};

// 3. Безпечний обчислювач логічних виразів AST
struct ExprNode;
using ExprPtr = std::shared_ptr<ExprNode>;

struct ExprNode {
    enum class Type { Literal, Var, Equal, NotEqual, And, Or, Not, Regex } type;
    Value literal_val;
    std::string var_path;
    std::string pattern;
    std::vector<ExprPtr> children;
};

class SafeEvaluator {
public:
    static Value evaluate(const ExprPtr& expr, const StateStore& store) {
        if (!expr) return Value(true);

        switch (expr->type) {
            case ExprNode::Type::Literal:
                return expr->literal_val;
            case ExprNode::Type::Var:
                return store.get(expr->var_path);
            case ExprNode::Type::Equal: {
                if (expr->children.size() < 2) return Value(false);
                auto l = evaluate(expr->children[0], store);
                auto r = evaluate(expr->children[1], store);
                return Value(l.as_string() == r.as_string());
            }
            case ExprNode::Type::NotEqual: {
                if (expr->children.size() < 2) return Value(false);
                auto l = evaluate(expr->children[0], store);
                auto r = evaluate(expr->children[1], store);
                return Value(l.as_string() != r.as_string());
            }
            case ExprNode::Type::And: {
                for (const auto& child : expr->children) {
                    if (!evaluate(child, store).as_bool()) return Value(false);
                }
                return Value(true);
            }
            case ExprNode::Type::Or: {
                for (const auto& child : expr->children) {
                    if (evaluate(child, store).as_bool()) return Value(true);
                }
                return Value(false);
            }
            case ExprNode::Type::Not: {
                if (expr->children.empty()) return Value(false);
                return Value(!evaluate(expr->children[0], store).as_bool());
            }
            case ExprNode::Type::Regex: {
                if (expr->children.empty()) return Value(false);
                std::string target = evaluate(expr->children[0], store).as_string();
                try {
                    std::regex re(expr->pattern);
                    return Value(std::regex_search(target, re));
                } catch (...) {
                    return Value(false);
                }
            }
        }
        return Value(false);
    }
};

// 4. Структура візуального вузла та реєстр рендерерів
struct UINode {
    std::string id;
    std::string type;
    std::unordered_map<std::string, std::string> props;
    std::string bind_path;
    ExprPtr visibility;
    std::vector<std::unique_ptr<UINode>> children;
    std::unique_ptr<UINode> fallback;
};

class SDUIEngine {
public:
    using Renderer = std::function<void(const UINode&, const StateStore&, SDUIEngine&)>;

    explicit SDUIEngine(Object init_state) : store_(std::move(init_state)) {}

    void register_component(const std::string& type, Renderer r) {
        registry_[type] = std::move(r);
    }

    void render_tree(const UINode& node) {
        // 1. Перевірка видимості
        if (node.visibility && !SafeEvaluator::evaluate(node.visibility, store_).as_bool()) {
            return;
        }

        // 2. Диспетчеризація за типом
        auto it = registry_.find(node.type);
        if (it != registry_.end()) {
            it->second(node, store_, *this);
            return;
        }

        // 3. Fallback-деградація
        if (node.fallback) {
            render_tree(*node.fallback);
        }
    }

    StateStore& store() { return store_; }

private:
    StateStore store_;
    std::unordered_map<std::string, Renderer> registry_;
};
```
:::

---

## Детальний розбір механізмів та трасування

Щоб зрозуміти, як поводяться компоненти під час взаємодії користувача, простежимо покроковий ланцюжок дій при зміні вибору у випадаючому списку форми.

### Крок 1. Мутація значення та сповіщення сховища
Користувач перемикає спосіб оплати з банківської картки на безготівковий розрахунок за реквізитами (`payment_method = "invoice"`). Віджет генерує подію `on_change`, яка викликає метод `store.set("/payment_method", "invoice")`. Сховище оновлює внутрішнє дерево об'єктів і викликає зареєстровані функції зворотного виклику підписників.

### Крок 2. Перерахунок дерева умовних виразів
Усі вузли інтерфейсу, що містять предикати видимості (`visibility`) або доступності (`enabled`), проганяють свої AST-дерева через `SafeExpressionEvaluator`. Наприклад, вузол із полем вводу коду ЄДРПОУ містить правило:

```json
{
  "visibility": {
    "op": "==",
    "left": { "var": "/payment_method" },
    "right": "invoice"
  }
}
```

Обчислювач читає поточне значення `/payment_method` зі сховища (отримує `"invoice"`), порівнює його з `"invoice"` і повертає `true`. Вузол негайно змінює свій статус з прихованого на видимий.

### Крок 3. Рекурсивна диспетчеризація рендерингу
Рушій `SDUIEngine` обходить дерево зверху вниз. Для кореневого контейнера `Stack` викликається відповідний рендерер, який ітерує список дочірніх елементів `children`. Коли обхід доходить до вузла ЄДРПОУ, реєстр знаходить прив'язаний нативний компонент `TextInputRenderer`, передає йому конфігурацію пропсів, початкове значення зі сховища та обробники дій.

---

## Інженерні пастки та крайові випадки

1. **Циклічні залежності у виразах (Circular Dependency Loops):**
   Якщо видимість поля `A` залежить від значення поля `B`, а видимість поля `B` — від значення поля `A`, наївний перерахунок під час мутації стану призведе до нескінченного циклу та переповнення стека викликів. Рушій зобов'язаний обмежувати максимальну глибину рекурсії обчислювача (наприклад, не більше 32 рівнів) або будувати спрямований ациклічний граф (DAG) залежностей перед рендерингом для топологічного обчислення станів.

2. **Вразливості регулярних виразів (ReDoS):**
   При валідації полів за серверними шаблонами регулярних виразів (`pattern`) шкідливий або некоректно складений шаблон із вкладеним квантифікатором може спричинити катастрофічне відкочування (catastrophic backtracking). Це блокує головний потік інтерфейсу на 100% процесорного часу. Обчислювач регулярних виразів повинен або застосовувати лінійні рушії без бектрекінгу (наприклад, Google RE2 або Rust regex engine), або обмежувати час виконання перевірки таймаутом у 10–15 мілісекунд з автоматичним скиданням у стан помилки валідації.

3. **Втрата фокусу та стрибки курсора (Focus Jitter):**
   Коли користувач швидко друкує текст у полі, що породжує безперервні оновлення стану, повна перебудова дерева екрана може призвести до демонтажу нативного віджета та скидання активного фокусу віртуальної клавіатури. Рушій повинен використовувати стабільні ідентифікатори вузлів (`id`) та узгоджувати віртуальне дерево (Reconciliation), змінюючи лише текстові властивості в існуючому нативному компоненті без його перестворення.

4. **Витік пам'яті в підписниках (Subscriber Memory Leaks):**
   Якщо динамічні вузли рендеpointються та знищуються під час перемикання вкладок, їхні анонімні підписки на `StateStore` можуть залишатися в пам'яті назавжди. Реалізація повинна гарантувати обов'язковий виклик функції `unsubscribe()` у хуках життєвого циклу демонтажу компонента або використовувати структури слабких посилань (WeakRef).

---

## Інваріанти тестування та верифікація схеми

Перед відправкою клієнтам серверні схеми проходять конвеєр автоматичної верифікації (Schema Linter). Тестовий стенд гарантує дотримання трьох обов'язкових інваріантів:
* **Цілісність графів прив'язки (Binding Integrity):** кожен шлях `bind.value` повинен існувати у структурі `initial_state` або створюватися гарантованою дією ініціалізації.
* **Досяжність дій (Action Reachability):** кожна дія `on_click` зобов'язана вказувати на валідний маршрут навігації або зареєстровану команду диспетчера дій.
* **Сумісність компонентів (Component Matrix):** схема не повинна містити нових типів вузлів без явно вказаного вузла `fallback`, якщо цільова версія клієнта нижча за реліз впровадження нового компонента.
