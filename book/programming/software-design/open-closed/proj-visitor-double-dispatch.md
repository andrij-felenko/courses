# ⚙️ Відвідувач із подвійною диспетчеризацією: коли закрити треба операції

Віртуальний метод — звичний спосіб закрити код проти нових **типів**. Інтерфейс `Shape` з методом `area()`, під ним `Circle`, `Rect`, `Triangle`; додаєш фігуру — пишеш новий клас, і код, що підсумовує площі, не змінюється жодним символом. Але придивися, що цей самий прийом лишає **відкритим**. Додати фігуру дешево — а додати нову **операцію**: периметр, малювання, серіалізацію? Тоді доводиться відкрити сам інтерфейс `Shape` і дописати метод у **кожен** наявний клас. Те, що віртуальні методи закрили по одній осі, вони навстіж лишили по другій.

Патерн «Відвідувач» (англ. *Visitor*) перевертає цей вибір: він закриває код проти нових **операцій** — ціною відкритості проти нових типів. Механізм, яким він це робить, зветься **подвійна диспетчеризація** (англ. *double dispatch*), і саме її ми зберемо руками на невеликому дереві, щоб побачити на власні очі, як два звичайні віртуальні виклики поспіль дають те, чого один дати не може.

## Задача: дерево виразу, над яким наростають проходи

Візьмемо крихітну мову арифметики — дерево виразу. Три види вузлів: число `Num`, сума `Add`, добуток `Mul`. Вузол `Add` тримає два піддерева, `Mul` — теж, `Num` — лист без дітей. Це [Компонувальник](book:programming/composite): листки й композити за спільним інтерфейсом, де композит рекурсивно містить дітей того самого типу. Вираз `(2 + 3) * 4` — це дерево `Mul(Add(Num(2), Num(3)), Num(4))`.

Тепер найважливіше — про **домен**. Видів вузлів мало, і вони стабільні: число, сума, добуток — набір, що майже не росте. А от **операцій** над деревом весь час більшає. Спершу треба порахувати значення. Потім — надрукувати вираз у дужках. Далі — вивести у зворотному польському записі для стекової машини, порахувати глибину дерева, згорнути сталі підвирази, перевірити типи, згенерувати машинний код. Це рівно ситуація компілятора: **дерево розбору стабільне, а проходів над ним — десятки, і вони додаються без кінця**. Осі зростання тут дзеркальні до задачі про фігури — росте не набір типів, а набір операцій.

Зроби це віртуальними методами — і одразу видно, куди вдарить.

:::tabs
```ts
interface Expr {
  eval(): number;
  print(): string;   // щоб додати друк, довелося ВІДКРИТИ інтерфейс…
}

class Num implements Expr {
  constructor(readonly value: number) {}
  eval(): number { return this.value; }
  print(): string { return String(this.value); }        // …і КОЖЕН клас
}
class Add implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  eval(): number { return this.left.eval() + this.right.eval(); }
  print(): string { return `(${this.left.print()} + ${this.right.print()})`; }
}
class Mul implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  eval(): number { return this.left.eval() * this.right.eval(); }
  print(): string { return `(${this.left.print()} * ${this.right.print()})`; }
}
```
```cpp
// Кожна операція — метод у контракті.
struct Expr {
    virtual ~Expr() = default;
    virtual int eval() const = 0;
    virtual std::string print() const = 0;   // щоб додати друк, довелося ВІДКРИТИ інтерфейс…
};

struct Num : Expr {
    int value;
    explicit Num(int value) : value(value) {}
    int eval() const override { return value; }
    std::string print() const override { return std::to_string(value); }   // …і КОЖЕН клас
};
struct Add : Expr {
    const Expr *left, *right;
    Add(const Expr* left, const Expr* right) : left(left), right(right) {}
    int eval() const override { return left->eval() + right->eval(); }
    std::string print() const override { return "(" + left->print() + " + " + right->print() + ")"; }
};
struct Mul : Expr {
    const Expr *left, *right;
    Mul(const Expr* left, const Expr* right) : left(left), right(right) {}
    int eval() const override { return left->eval() * right->eval(); }
    std::string print() const override { return "(" + left->print() + " * " + right->print() + ")"; }
};
```
```java
interface Expr {
    int eval();
    String print();   // щоб додати друк, довелося ВІДКРИТИ інтерфейс…
}

final class Num implements Expr {
    final int value;
    Num(int value) { this.value = value; }
    public int eval() { return value; }
    public String print() { return Integer.toString(value); }   // …і КОЖЕН клас
}
final class Add implements Expr {
    final Expr left, right;
    Add(Expr left, Expr right) { this.left = left; this.right = right; }
    public int eval() { return left.eval() + right.eval(); }
    public String print() { return "(" + left.print() + " + " + right.print() + ")"; }
}
final class Mul implements Expr {
    final Expr left, right;
    Mul(Expr left, Expr right) { this.left = left; this.right = right; }
    public int eval() { return left.eval() * right.eval(); }
    public String print() { return "(" + left.print() + " * " + right.print() + ")"; }
}
```
:::

Кожна операція — метод у контракті `Expr`. Додати `eval` було безкоштовно, поки він один. Але наступний прохід, `print`, змусив відкрити `interface Expr` і дописати тіло в `Num`, в `Add`, у `Mul`. Третій прохід (`rpn`) — знову відкрити всі три класи. Кожна нова операція розповзається по **всіх** наявних типах: вона — новий стовпець матриці, а віртуальні методи тримають код по рядках (клас = один тип із усіма своїми методами), тож новий стовпець ріже впоперек кожен рядок. Операційна вісь відкрита навстіж, і закрити її віртуальними методами не вийде — вони закривають рівно другу.

## Ідея: винести операцію назовні й диспетчеризувати двічі

Поверни думку на кут. Звичайний віртуальний виклик `x.f()` обирає тіло методу за **одним** типом — типом отримувача `x`, того, хто ліворуч від крапки. Це **одинарна диспетчеризація**: вона дає одну координату. А поведінка, яку ми хочемо, живе на перетині **двох** типів — який це вузол (`Num`/`Add`/`Mul`) і яка це операція (`eval`/`print`/`rpn`). Одна координата не адресує клітину; потрібні обидві. Ось у цьому корінь: одинарний виклик здатний закрити лише одну вісь саме тому, що дає лише одну координату.

Відвідувач добуває другу координату **другим** віртуальним викликом. Спершу винесемо кожну операцію з вузлів у власний об'єкт — **відвідувача** — з одним методом на кожен вид вузла: `visitNum`, `visitAdd`, `visitMul`. А в кожному вузлі лишимо один крихітний метод `accept(v)`, який лише кличе назад потрібний `visit`. Тоді виклик розкладається на два кроки:

- `expr.accept(v)` — отримувач тут **вузол**, тож віртуальна диспетчеризація обирає тіло за типом вузла. Це вибір **рядка** матриці: серед `Num`/`Add`/`Mul` спрацював, скажімо, `Add.accept`.
- Усередині нього — `v.visitAdd(this)`, де отримувач уже **відвідувач**, тож друга віртуальна диспетчеризація обирає тіло за типом відвідувача. Це вибір **стовпця**: серед `Eval`/`Print`/`Rpn` спрацював, скажімо, `Print.visitAdd`.

Рядок, потім стовпець — і разом вони вказують рівно одну клітину: `Print.visitAdd`. Два одинарні диспетчі, зчеплені один за одним, дають адресацію по двох осях. Звідси й ім'я — «подвійна».

![Виклик add.accept(printer) проходить два віртуальні диспетчі: перший за реальним типом елемента обирає рядок (Add), другий за реальним типом відвідувача обирає стовпець (Print); їх перетин — одне тіло методу, одна клітина матриці типи×операції.](/book/programming/software-design/open-closed/img/double-dispatch.svg)

*Подвійна диспетчеризація — це не якийсь особливий виклик, а два звичайні віртуальні виклики поспіль; перетин їхніх виборів і є клітина.*

> 🔧 **Навіщо це.** Уся хитрість — у крихітному відскоку `accept`. Здавалося б, навіщо він: чому не покликати `v.visitAdd(expr)` напряму? Бо тоді довелося б **самому** дізнатися, що `expr` — саме `Add`, тобто повернути `switch`/`instanceof`, який Відвідувач і прийшов прибрати. Відскок `accept` перекладає цю роботу на віртуальну диспетчеризацію: вузол сам знає свій тип і сам кличе відповідний `visit`. Без другого виклику лишилася б одна координата — і код знову закрив би тільки одну вісь.

## Робочий код: вузли, відвідувачі, два проходи

Зберемо рушій цілком. Спершу — **контракт**: вузли вміють лише «прийняти відвідувача», а відвідувач має по методу на кожен вид вузла. Обидва інтерфейси параметризуємо типом результату `R` — щоб `Eval` повертав число, `Print` — рядок, і все це без жодного зведення типів:

:::tabs
```ts
// Вузли дерева — кожен уміє тільки прийняти відвідувача й покликати свій visit.
interface Expr {
  accept<R>(v: Visitor<R>): R;
}

class Num implements Expr {
  constructor(readonly value: number) {}
  accept<R>(v: Visitor<R>): R { return v.visitNum(this); }
}
class Add implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  accept<R>(v: Visitor<R>): R { return v.visitAdd(this); }
}
class Mul implements Expr {
  constructor(readonly left: Expr, readonly right: Expr) {}
  accept<R>(v: Visitor<R>): R { return v.visitMul(this); }
}

// Операція — окремий об'єкт. Один метод на кожен вид вузла.
interface Visitor<R> {
  visitNum(n: Num): R;
  visitAdd(a: Add): R;
  visitMul(m: Mul): R;
}

// Прохід 1: обчислити значення (R = number).
class Eval implements Visitor<number> {
  visitNum(n: Num): number { return n.value; }
  visitAdd(a: Add): number { return a.left.accept(this) + a.right.accept(this); }
  visitMul(m: Mul): number { return m.left.accept(this) * m.right.accept(this); }
}

// Прохід 2: надрукувати у дужках (R = string).
class Print implements Visitor<string> {
  visitNum(n: Num): string { return String(n.value); }
  visitAdd(a: Add): string { return `(${a.left.accept(this)} + ${a.right.accept(this)})`; }
  visitMul(m: Mul): string { return `(${m.left.accept(this)} * ${m.right.accept(this)})`; }
}
```
```cpp
struct Num; struct Add; struct Mul;          // попереднє оголошення вузлів

// Операція — окремий об'єкт. Один метод на кожен вид вузла.
struct Visitor {
    virtual ~Visitor() = default;
    virtual void visitNum(const Num& n) = 0;
    virtual void visitAdd(const Add& a) = 0;
    virtual void visitMul(const Mul& m) = 0;
};

// Вузли дерева — кожен уміє тільки прийняти відвідувача й покликати свій visit.
struct Expr {
    virtual ~Expr() = default;
    virtual void accept(Visitor& v) const = 0;
};

struct Num : Expr {
    int value;
    explicit Num(int value) : value(value) {}
    void accept(Visitor& v) const override { v.visitNum(*this); }
};
struct Add : Expr {
    const Expr *left, *right;
    Add(const Expr* left, const Expr* right) : left(left), right(right) {}
    void accept(Visitor& v) const override { v.visitAdd(*this); }
};
struct Mul : Expr {
    const Expr *left, *right;
    Mul(const Expr* left, const Expr* right) : left(left), right(right) {}
    void accept(Visitor& v) const override { v.visitMul(*this); }
};

// Прохід 1: обчислити значення. Кожен відвідувач несе свій типізований результат (int).
struct Eval : Visitor {
    int result = 0;
    int run(const Expr& e) { e.accept(*this); return result; }
    void visitNum(const Num& n) override { result = n.value; }
    void visitAdd(const Add& a) override { result = run(*a.left) + run(*a.right); }
    void visitMul(const Mul& m) override { result = run(*m.left) * run(*m.right); }
};

// Прохід 2: надрукувати у дужках (тут результат — std::string).
struct Print : Visitor {
    std::string result;
    std::string run(const Expr& e) { e.accept(*this); return result; }
    void visitNum(const Num& n) override { result = std::to_string(n.value); }
    void visitAdd(const Add& a) override { result = "(" + run(*a.left) + " + " + run(*a.right) + ")"; }
    void visitMul(const Mul& m) override { result = "(" + run(*m.left) + " * " + run(*m.right) + ")"; }
};
```
```java
// Вузли дерева — кожен уміє тільки прийняти відвідувача й покликати свій visit.
interface Expr {
    <R> R accept(Visitor<R> v);
}

final class Num implements Expr {
    final int value;
    Num(int value) { this.value = value; }
    public <R> R accept(Visitor<R> v) { return v.visitNum(this); }
}
final class Add implements Expr {
    final Expr left, right;
    Add(Expr left, Expr right) { this.left = left; this.right = right; }
    public <R> R accept(Visitor<R> v) { return v.visitAdd(this); }
}
final class Mul implements Expr {
    final Expr left, right;
    Mul(Expr left, Expr right) { this.left = left; this.right = right; }
    public <R> R accept(Visitor<R> v) { return v.visitMul(this); }
}

// Операція — окремий об'єкт. Один метод на кожен вид вузла.
interface Visitor<R> {
    R visitNum(Num n);
    R visitAdd(Add a);
    R visitMul(Mul m);
}

// Прохід 1: обчислити значення (R = Integer).
final class Eval implements Visitor<Integer> {
    public Integer visitNum(Num n) { return n.value; }
    public Integer visitAdd(Add a) { return a.left.accept(this) + a.right.accept(this); }
    public Integer visitMul(Mul m) { return m.left.accept(this) * m.right.accept(this); }
}

// Прохід 2: надрукувати у дужках (R = String).
final class Print implements Visitor<String> {
    public String visitNum(Num n) { return Integer.toString(n.value); }
    public String visitAdd(Add a) { return "(" + a.left.accept(this) + " + " + a.right.accept(this) + ")"; }
    public String visitMul(Mul m) { return "(" + m.left.accept(this) + " * " + m.right.accept(this) + ")"; }
}
```
:::

Зверни увагу, хто веде рекурсію. Тіло `visitAdd` саме кличе `a.left.accept(this)` і `a.right.accept(this)` — тобто **відвідувач** обходить піддерева, передаючи `this` (себе) далі вглиб. Це навмисно: різні проходи хочуть різного порядку. `Print` спускається зліва направо й обгортає в дужки; `Eval` — так само, але множить; майбутній прохід «глибина» захоче взяти максимум по дітях, а не суму. Рекурсію тримає той, хто знає, як саме йому обходити, — сам відвідувач.

Запустимо:

:::tabs
```ts
// (2 + 3) * 4
const tree: Expr = new Mul(new Add(new Num(2), new Num(3)), new Num(4));

tree.accept(new Eval());    // 20
tree.accept(new Print());   // "((2 + 3) * 4)"
```
```cpp
// (2 + 3) * 4
Num n2{2}, n3{3}, n4{4};
Add inner{&n2, &n3};
Mul tree{&inner, &n4};

Eval{}.run(tree);    // 20
Print{}.run(tree);   // "((2 + 3) * 4)"
```
```java
// (2 + 3) * 4
Expr tree = new Mul(new Add(new Num(2), new Num(3)), new Num(4));

tree.accept(new Eval());    // 20
tree.accept(new Print());   // "((2 + 3) * 4)"
```
:::

Прослідкуй `tree.accept(new Print())` крок за кроком, і подвійна диспетчеризація перестане бути абстракцією. `tree` — це `Mul`, тож перший диспетч веде в `Mul.accept`, а той кличе `printer.visitMul(this)` — другий диспетч веде в `Print.visitMul`. Той кличе `accept` на лівому піддереві (`Add`) і на правому (`Num`), і на кожному кроці пара «тип вузла × тип відвідувача» знову добирає рівно одну клітину. Дерево обходиться, клітини складаються в рядок `((2 + 3) * 4)`.

## Обидві осі в дії: нова операція дешева, новий тип — дорогий

Тепер найцікавіше — заради чого Відвідувача й затіяно. Додамо **нову операцію**: зворотний польський запис. Ось повний обсяг правок:

:::tabs
```ts
// Нова операція — НОВИЙ клас. Жоден вузол не відкрито.
class Rpn implements Visitor<string> {
  visitNum(n: Num): string { return String(n.value); }
  visitAdd(a: Add): string { return `${a.left.accept(this)} ${a.right.accept(this)} +`; }
  visitMul(m: Mul): string { return `${m.left.accept(this)} ${m.right.accept(this)} *`; }
}

tree.accept(new Rpn());   // "2 3 + 4 *"
```
```cpp
// Нова операція — НОВИЙ клас. Жоден вузол не відкрито.
struct Rpn : Visitor {
    std::string result;
    std::string run(const Expr& e) { e.accept(*this); return result; }
    void visitNum(const Num& n) override { result = std::to_string(n.value); }
    void visitAdd(const Add& a) override { result = run(*a.left) + " " + run(*a.right) + " +"; }
    void visitMul(const Mul& m) override { result = run(*m.left) + " " + run(*m.right) + " *"; }
};

Rpn{}.run(tree);   // "2 3 + 4 *"
```
```java
// Нова операція — НОВИЙ клас. Жоден вузол не відкрито.
final class Rpn implements Visitor<String> {
    public String visitNum(Num n) { return Integer.toString(n.value); }
    public String visitAdd(Add a) { return a.left.accept(this) + " " + a.right.accept(this) + " +"; }
    public String visitMul(Mul m) { return m.left.accept(this) + " " + m.right.accept(this) + " *"; }
}

tree.accept(new Rpn());   // "2 3 + 4 *"
```
:::

І все. `Num`, `Add`, `Mul` не відкривали — вони як були перевірені, так і лишилися; `Eval` і `Print` не чіпали. Нова операція приїхала **одним новим класом в окремому файлі**. Це і є «закрито проти осі операцій»: скільки б проходів ти не додав — `Rpn`, `Depth`, `Optimize`, `Typecheck` — кожен це новий клас-відвідувач, новий стовпець матриці, а наявні вузли й наявні відвідувачі стоять недоторкані. Рівно ту вісь, яку віртуальні методи лишали відкритою, Відвідувач закрив.

За це заплачено дзеркальною монетою. Додамо тепер **новий тип вузла** — унарний мінус `Neg`:

:::tabs
```ts
class Neg implements Expr {
  constructor(readonly operand: Expr) {}
  accept<R>(v: Visitor<R>): R { return v.visitNeg(this); }
}
```
```cpp
struct Neg : Expr {
    const Expr* operand;
    explicit Neg(const Expr* operand) : operand(operand) {}
    void accept(Visitor& v) const override { v.visitNeg(*this); }
};
```
```java
final class Neg implements Expr {
    final Expr operand;
    Neg(Expr operand) { this.operand = operand; }
    public <R> R accept(Visitor<R> v) { return v.visitNeg(this); }
}
```
:::

Сам клас `Neg` написати легко. Але зверни увагу, що `accept` кличе `v.visitNeg(this)` — метод, якого в `Visitor` **ще немає**. Щоб код скомпілювався, доводиться:

:::tabs
```ts
interface Visitor<R> {
  visitNum(n: Num): R;
  visitAdd(a: Add): R;
  visitMul(m: Mul): R;
  visitNeg(x: Neg): R;    // ← новий рядок у контракті
}
```
```cpp
struct Visitor {
    virtual ~Visitor() = default;
    virtual void visitNum(const Num& n) = 0;
    virtual void visitAdd(const Add& a) = 0;
    virtual void visitMul(const Mul& m) = 0;
    virtual void visitNeg(const Neg& x) = 0;   // ← новий рядок у контракті
};
```
```java
interface Visitor<R> {
    R visitNum(Num n);
    R visitAdd(Add a);
    R visitMul(Mul m);
    R visitNeg(Neg x);    // ← новий рядок у контракті
}
```
:::

а слідом — дописати `visitNeg` у **кожен** наявний відвідувач: `Eval` (`return -x.operand.accept(this)`), `Print` (`return \`(-${x.operand.accept(this)})\``), `Rpn`, і в усі майбутні. Новий тип вузла — це новий **рядок** матриці, а Відвідувач тримає код по стовпцях (відвідувач = один прохід із усіма своїми `visit`), тож новий рядок ріже впоперек кожен стовпець. Точно та сама біда, що мучила віртуальні методи з новою операцією, лише повернута на 90°.

![Матриця типи×операції в аранжуванні Відвідувача: стовпець — це клас-відвідувач. Новий відвідувач (Depth) — це цілий новий стовпець в одному файлі, елементи недоторкані. Новий тип вузла (Neg) — це новий рядок, тобто метод visitNeg у кожен відвідувач.](/book/programming/software-design/open-closed/img/visitor-matrix.svg)

*Той самий поділ типи×операції, тільки згрупований за стовпцем: Відвідувач робить об'єктну програму такою, наче її писали процедурно — по операціях.*

Ось і вся дуальність, у коді: **Відвідувач і віртуальні методи — дзеркала**. Віртуальні методи групують код за рядком (клас тримає всі свої операції купно), тож новий **тип** дешевий, а нова **операція** розлазиться по всіх класах. Відвідувач групує код за стовпцем (відвідувач тримає всі типи для однієї операції), тож нова **операція** дешева, а новий **тип** розлазиться по всіх відвідувачах. Кожен закритий проти однієї осі рівно тому, що відкритий проти другої. Обрати між ними — це **зробити ставку**, що росте в твоєму домені: типи чи операції.

> 🔧 **Навіщо це.** Ставку легко зробити не ту, і тоді завіса стоїть проти реальної осі — кожна дрібна зміна б'є по всьому коду. Компілятор: вузли дерева розбору стабільні, а проходів усе більше — Відвідувач лягає. Платіжна система: операцій мало (списати, повернути), а провайдерів усе більше — доречні, навпаки, віртуальні реалізації за інтерфейсом. Тому перш ніж тягти церемонію `accept`/`visit`, чесно спитай: у мене справді росте вісь **операцій**? Якщо ростуть типи — Відвідувач лише додасть роботи, бо кожен новий тип потягне правку в усі відвідувачі.

## Чому саме «accept»: перевантаження, статичні типи, типобезпека

Лишилося розібрати найтоншу деталь — чому відскок `accept` взагалі потрібен, і що дає система типів. Спокуса щоразу та сама: «навіщо два методи, зробімо один `visit`, що сам розбереться за типом аргумента». У мові зі статичними типами ця спроба розбивається об те, як обирається **перевантаження** (англ. *overload*):

```java
interface Visitor {
    void visit(Num n);
    void visit(Add a);
    void visit(Mul m);
}

Expr e = new Add(new Num(2), new Num(3));   // статичний тип змінної — Expr
visitor.visit(e);   // ✗ не компілюється: перевантаження visit(Expr) немає.
                    //   Java обирає перевантаження за СТАТИЧНИМ типом e (Expr),
                    //   а не за тим, що там Add у рантаймі.
```

Ось де собака зарита. Перевантаження в Java (і в C++, і в C#) розв'язується на **компіляції**, за оголошеним типом виразу, а не за тим, що реально лежить в об'єкті під час виконання. `visitor.visit(e)`, де `e` оголошено як `Expr`, шукає `visit(Expr)` — і не знаходить. Відскок `accept` лагодить це елегантно: усередині `Add.accept` вказівник `this` має статичний тип `Add`, тож `v.visitAdd(this)` (чи `v.visit(this)` з перевантаженнями) компілятор розв'язує **точно**, а те, **котрий** `accept` спрацював, обрала віртуальна диспетчеризація в рантаймі. Перший виклик добуває рантайм-тип і робить його статично відомим; другий цим користується. Два диспетчі — це рантайм-вибір, помножений на компіляційний вибір перевантаження, і разом вони дають клітину без жодного `instanceof`.

Звідси й головний виграш у типобезпеці. Параметр `R` робить проходи типізованими наскрізь: `Eval` повертає `number`, `Print` — `string`, і компілятор це стереже — жодних зведень, жодного `any`. А коли додаєш новий тип вузла й дописуєш `visitNeg` у контракт `Visitor`, компілятор **сам перелічує** всі місця, які треба оновити: кожен відвідувач, що не отримав `visitNeg`, не збереться. Дорога правда (новий тип чіпає всі відвідувачі) лишається дорогою — але вона **безпечна**: не «десь тихо забув обробити `Neg`», а список помилок компіляції, який просто закриваєш пункт за пунктом. Система типів перетворює розсипану по стовпцях правку на перевірений нею ж контрольний список.

## Складність, ціна й пастки

Відвідувач не безкоштовний, і його церемонність — не дрібниця.

**Церемонія та громіздкість.** На `N` типів і `M` проходів маєш `N×M` методів `visit` плюс `N` методів `accept` — купа дрібного коду, і зв'язок «хто кого кличе» стрибає між класами. Для двох вузлів і двох проходів це надлишок: простий метод чи `switch` читалися б легше. Відвідувач окупається лише там, де операцій справді багато й вони справді ростуть, а типи стоять; на малому й стабільному він — складність без віддачі.

**Дзеркальна ціна реальна, а не теоретична.** Якщо набір вузлів усе-таки почне рости — щомісяця новий вид виразу, — кожен новий тип потягне правку в **усі** відвідувачі, і Відвідувач із рятівника стане тягарем. Це та сама «завіса не на тій осі», тільки для операційного боку.

**Циклічна залежність за побудовою.** `Visitor` мусить знати всі типи вузлів (`visitNum`, `visitAdd`, …), а кожен вузол мусить знати `Visitor` (щоб оголосити `accept`). Вони замкнені в кільце. Тому додавання типу вузла обов'язково торкає контракт `Visitor` — інакше й бути не може, це наслідок того, що операції винесені назовні.

**Стан у відвідувачі — це нормально, глобал — ні.** Відвідувач може накопичувати стан між вузлами: лічильник глибини, `StringBuilder`, список знайдених помилок. Це не гріх, а ідіома — **бо стан живе в екземплярі відвідувача й існує рівно один прохід**. Створив `new Print()`, обійшов дерево, викинув. Небезпечним стан робиться тільки тоді, коли він **спільний між проходами** — статичне поле, глобал, кеш, який ділять кілька відвідувачів: тоді два проходи зчіпляються невидимою ниткою, перестають додаватися незалежно, і закритість, яку дав патерн, дірявиться. Правило просте: стан — у полі екземпляра відвідувача, не в статиці.

**Хто веде обхід — і пастка «забув рекурсію».** Оскільки рекурсію тримає відвідувач, у кожному `visitAdd`/`visitMul` треба **не забути** покликати `accept` на дітях. Забудеш — прохід тихо обробить лише корінь і поверне неповний результат, без жодної помилки. Це плата за гнучкість (кожен прохід сам керує порядком): відповідальність за спуск лежить на авторі відвідувача.

**Пом'якшити дзеркальну ціну — базовим відвідувачем із типовим `visit`.** Якщо новий тип вузла не має ламати геть усі відвідувачі, дають базовий клас із типовим `visitNode`, який нові вузли викликають доти, доки конкретний прохід не перевизначить його. Але це той самий компроміс, що й «дірка в таблиці» диспетчеризації: ти виграєш те, що новий тип не валить збірку, і програєш те, що компілятор більше не перелічує пропущені місця — забутий випадок тихо йде в типову гілку. Обмінюєш повноту, яку стеріг компілятор, на м'якість додавання типів; знати, що саме віддаєш, тут важливіше за сам вибір.

## Коли Відвідувач лягає — і коли ні

Зведімо. Відвідувач — це віртуальні методи, вивернуті по осі закритості. Порівняння коротке й практичне:

- **Ростуть операції, типи стабільні** — Відвідувач. Класика: обхід дерева розбору в компіляторі чи лінтері, де вузлів AST скінченний набір, а проходів (перевірка типів, оптимізації, генерація коду, форматування) весь час більшає. Кожен прохід — новий відвідувач, дерево недоторкане.
- **Ростуть типи, операцій мало** — звичайні віртуальні методи. Новий тип — новий клас, наявний код закритий; саме те, що дає інтерфейс `Shape` з жменею стабільних операцій.
- **Плоский набір, ключований числом, у мові без класів або в гарячому шляху** — таблиця диспетчеризації на вказівниках на функції: там завіса стоїть на даних, а не на типах, і додавання виду — це рядок у масиві.

За цим вибором стоїть строгий факт. Спробуй закрити **обидві** осі одразу — щоб і новий тип, і нова операція додавалися, не чіпаючи наявного й зберігаючи статичну типобезпеку, — і побачиш, що базовими засобами ООП це неможливо: одинарна диспетчеризація дає одну координату й закриває одну вісь. Це **задача про вираз** (англ. *expression problem*), названа так Філіпом Вадлером (Philip Wadler) 1998 року в записці на розсилці про генерики Java (усталений факт; сам термін відтоді — стандартний орієнтир у теорії мов). Рядки — типи, стовпці — операції; в об'єктній мові легко додавати рядки, у процедурній — стовпці, а обидва разом — уже потребує сильніших механізмів (множинна диспетчеризація, класи типів, об'єктні алгебри), кожен зі своєю ціною. Відвідувач цю дилему не скасовує — він просто дає **обрати другий бік**: суто об'єктними засобами перенести закритість із осі типів на вісь операцій.

Сам патерн уперше каталогізовано в GoF-книзі *Design Patterns: Elements of Reusable Object-Oriented Software* (1994; Еріх Ґамма, Річард Гелм, Ральф Джонсон, Джон Вліссідес) з наміром, що читається як пряма формула OCP для операцій: «подати операцію над елементами структури об'єктів так, щоб можна було визначити нову операцію, не змінюючи класів елементів, над якими вона працює» (усталений факт). Ім'я «Відвідувач» — від образу об'єкта, що «ходить» структурою й на кожному вузлі робить своє; а рушій цього ходіння — дві диспетчеризації поспіль, які з двох звичайних віртуальних викликів складають одну клітину матриці типи×операції.
