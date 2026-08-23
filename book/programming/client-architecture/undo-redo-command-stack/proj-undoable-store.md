# ⚙️ Сховище документа з історією: збираємо цілком

Тут в один робочий шматок коду зібрано те, що зазвичай пояснюють частинами: сховище стану клієнта, у якому крок назад коштує **одне присвоєння вказівника**, межа кроку збігається з межею людського наміру, курсор після відкату стоїть там, де людина діяла, зірочка «незбережено» не бреше — а історія має стелю в байтах і, впершись у неї, справді віддає пам'ять назад. Основна мова — C++ (вузли на `std::shared_ptr`, точне звільнення), друга вкладка кожного блоку — TypeScript, де ті самі обіцянки тримаються інакше.

## Умова: п'ять обіцянок одночасно

Кожна з них поодинці робиться за годину. Разом вони тягнуть за собою цілком певну будову — і в цьому вся задача.

**Відкат не залежить від розміру документа.** У книжці на двадцять мегабайтів «назад» мусить спрацювати так само швидко, як у порожньому файлі, — бо людина тисне цю клавішу серіями, не чекаючи.

**Один намір — один крок.** Перетягування — це сотні проміжних позицій, оформлення абзацу — три різні поля. У меню «Скасувати» має стояти «перетягування», а не «зсув на піксель».

**Крок повертає й увагу.** Відкат, що відновив комірку за три екрани звідси, формально правильний і по відчуттю зламаний: людина не бачить, що змінилося, і тисне ще раз.

**«Змінено» — правда.** Якщо після збереження зробити зміну й скасувати її, документ побайтно дорівнює файлу — і зірочка мусить згаснути.

**Пам'ять історії обмежена й справді звільняється.** Сховище, що за день роботи виростає до трьох гігабайтів, не має історії — воно має витік із гарним інтерфейсом.

## Одна ідея, з якої випливає решта

Зробимо модель документа [незмінною](book:programming/immutability) — такою, що після народження її не правлять на місці, а заміняють новою. Тоді зміна не руйнує нічого: народжується **нова версія**, а стара лишається живою, поки на неї хтось дивиться. У сховищі з'являється рівно одна змінна комірка — **вказівник на поточний корінь**, а вся історія стає списком старих коренів.

Звідси одразу випливає головна обіцянка. Відкат — це присвоїти комірці старий вказівник. Розмір документа в цьому не бере участі: хоч сторінка, хоч книжка — одне присвоєння.

Наївне заперечення «нова версія на кожну літеру — це копія документа на кожну літеру» знімає **копіювання лише шляху**: нова версія перебудовує тільки вузли на дорозі від кореня до зміни, а всі бічні піддерева обидві версії ділять фізично тим самим шматком пам'яті. Механізм, його вартість і те, чому балансування тут не прикраса, розібрано окремо — [на незмінному дереві з path copying](book:programming/immutability/proj-persistent-structures.md); а простіший родич цього прийому, [копіювання при записі](book:algorithms/copy-on-write-structures), відрізняється тим, що платить повною копією за перший же запис у спільні дані. Нам звідти потрібен лише результат: одна правка коштує стільки нових вузлів, яка глибина дерева.

## Модель: вузол, що знає свою вагу

Вузол зберігає дві заздалегідь пораховані величини: `own` — вагу себе самого, і `bytes` — вагу всього піддерева. Друга потрібна не для звітності. Коли крок вилучить піддерево, ми муситимемо миттєво сказати, скільки байтів історія тепер тримає живими замість людини, — і кешоване поле дає це за одну дію замість обходу.

:::tabs
```cpp
#include <memory>
#include <string>
#include <vector>

struct Node;
using NodeP = std::shared_ptr<const Node>;   // const у самому типі: вузол не міняють ніколи

// Скільки байтів вузлів народилося. Модель живе на одному потоці — на потоці
// інтерфейсу, — тож звичайний лічильник, без атомарності.
inline thread_local std::size_t g_born = 0;

struct Node {
    const std::string        id;      // стабільний; переживає всі версії документа
    const std::string        text;
    const std::vector<NodeP> kids;
    const std::size_t        own;     // вага САМОГО вузла
    const std::size_t        bytes;   // вага піддерева: own + сума bytes дітей

    Node(std::string i, std::string t, std::vector<NodeP> k)
        : id(std::move(i)), text(std::move(t)), kids(std::move(k)),
          own(sizeof(Node) + 24 /* керувальний блок shared_ptr */
              + id.capacity() + text.capacity() + kids.size() * sizeof(NodeP)),
          bytes(own + sumKids(kids))
    {
        g_born += own;
    }

    static std::size_t sumKids(const std::vector<NodeP>& v) {
        std::size_t s = 0;
        for (const auto& k : v) s += k->bytes;   // діти вже знають свою вагу — це O(1) на дитину
        return s;
    }
};

inline NodeP mk(std::string id, std::string text, std::vector<NodeP> kids = {}) {
    return std::make_shared<const Node>(std::move(id), std::move(text), std::move(kids));
}

// Замінити вузол із заданим id. Нові вузли — ЛИШЕ на дорозі від кореня до цілі;
// бічні піддерева нова версія бере тим самим вказівником, вони спільні.
NodeP replaceById(const NodeP& n, const std::string& id, const NodeP& repl) {
    if (n->id == id) return repl;
    for (std::size_t i = 0; i < n->kids.size(); ++i) {
        NodeP nk = replaceById(n->kids[i], id, repl);
        if (nk != n->kids[i]) {                    // ціль знайшлася в цій гілці
            std::vector<NodeP> kids = n->kids;     // копія масиву ВКАЗІВНИКІВ, не піддерев
            kids[i] = std::move(nk);
            return mk(n->id, n->text, std::move(kids));
        }
    }
    return n;                                      // тут цілі немає — вузол лишається спільним
}

// Вилучити вузол; заразом кажемо, скільки байтів пішло з дерева.
NodeP removeById(const NodeP& n, const std::string& id, std::size_t& removed) {
    for (std::size_t i = 0; i < n->kids.size(); ++i) {
        if (n->kids[i]->id == id) {
            removed += n->kids[i]->bytes;          // ← O(1): вага піддерева вже порахована
            std::vector<NodeP> kids = n->kids;
            kids.erase(kids.begin() + i);
            return mk(n->id, n->text, std::move(kids));
        }
        NodeP nk = removeById(n->kids[i], id, removed);
        if (nk != n->kids[i]) {
            std::vector<NodeP> kids = n->kids;
            kids[i] = std::move(nk);
            return mk(n->id, n->text, std::move(kids));
        }
    }
    return n;
}
```
```ts
type Res = { release(): void };          // зовнішній ресурс: Blob URL, текстура, файл

type Node = Readonly<{
  id: string;                            // стабільний; переживає всі версії документа
  text: string;
  kids: readonly Node[];
  own: number;                           // вага самого вузла
  bytes: number;                         // вага піддерева
  res?: Res;
}>;

let born = 0;                            // оцінка народжених байтів, не бухгалтерія

export function mk(id: string, text: string,
                   kids: readonly Node[] = [], res?: Res): Node {
  const own = 72 + 2 * (id.length + text.length) + 8 * kids.length;  // рядки в UTF-16
  born += own;
  return Object.freeze({                 // freeze робить незмінність помилкою, а не домовленістю
    id, text, kids, own, res,
    bytes: own + kids.reduce((s, k) => s + k.bytes, 0),
  });
}

export function replaceById(n: Node, id: string, repl: Node): Node {
  if (n.id === id) return repl;
  for (let i = 0; i < n.kids.length; i++) {
    const nk = replaceById(n.kids[i], id, repl);
    if (nk !== n.kids[i]) {               // ціль знайшлася в цій гілці
      const kids = n.kids.slice();        // копія масиву ПОСИЛАНЬ, не піддерев
      kids[i] = nk;
      return mk(n.id, n.text, kids);
    }
  }
  return n;                               // тут цілі немає — вузол лишається спільним
}

export function removeById(n: Node, id: string): { root: Node; removed: number; dropped: Node[] } {
  for (let i = 0; i < n.kids.length; i++) {
    if (n.kids[i].id === id) {
      const kids = n.kids.slice();
      const [gone] = kids.splice(i, 1);
      // dropped збираємо тільки з вузлів із зовнішнім ресурсом — саме їх доведеться
      // віддавати руками, бо збирач сміття цього не зробить
      return { root: mk(n.id, n.text, kids), removed: gone.bytes, dropped: withRes(gone) };
    }
    const r = removeById(n.kids[i], id);
    if (r.root !== n.kids[i]) {
      const kids = n.kids.slice();
      kids[i] = r.root;
      return { root: mk(n.id, n.text, kids), removed: r.removed, dropped: r.dropped };
    }
  }
  return { root: n, removed: 0, dropped: [] };
}

function withRes(n: Node, out: Node[] = []): Node[] {
  if (n.res) out.push(n);
  for (const k of n.kids) withRes(k, out);
  return out;
}
```
:::

> 🔧 **Навіщо це.** Кешована вага піддерева — не мікрооптимізація, а те, без чого бюджет історії сліпий. Найдорожчий крок у житті редактора — **вилучення**: воно народжує кілька вузлів дороги й більше нічого, тобто за лічильником нових байтів важить майже нуль, а тримає живими двісті мегабайтів картинки. Дізнатися вагу вилученого треба саме в мить вилучення й за одну дію — обходити щойно відрізане піддерево на кожен `Delete` ніхто не буде.

## Крок історії: два вказівники, а не дві копії

Крок зберігає **два кореня** — стан до й стан після. Це два вказівники по вісім-шістнадцять байтів, а не дві копії документа: обидві версії й так живуть у пам'яті, ділячи майже все.

Виділення теж лежить у кроці двічі — «до» і «після». Причина в тому, що відкат і повтор ведуть людину в різні місця: після `Ctrl+Z` вона має опинитися там, де діяла (перед дією), після `Ctrl+Y` — там, куди дія її привела. І адресується виділення **стабільним ідентифікатором вузла**, а не позицією в масиві: після відкоту сусіди могли з'явитися й зникнути, тож «третій елемент згори» вкаже кудись не туди, а `id` показує на той самий абзац завжди.

:::tabs
```cpp
#include <deque>
#include <optional>
#include <functional>
#include <chrono>

struct Selection {                 // де стояла увага людини
    std::string nodeId;            // ЩО виділено — стабільний id, а не «третій згори»
    int from = 0, to = 0;          // діапазон усередині тексту вузла
};

// Результат правки: нова версія + скільки байтів правка ВИЛУЧИЛА з дерева.
struct EditResult { NodeP root; std::size_t removed = 0; };
using Edit = std::function<EditResult(const NodeP&)>;   // чиста функція: стара версія → нова

struct Step {
    NodeP       before, after;      // два кореня — два вказівники, не дві копії
    Selection   selBefore, selAfter;
    std::string label;              // «набір тексту» — те, що стане в меню «Скасувати …»
    std::string mergeKey;           // порожній ⇒ із сусіднім кроком не зливати
    std::size_t weight = 0;         // додане + вилучене цим кроком, у байтах
    std::chrono::steady_clock::time_point at;
};

class Store {
public:
    Store(NodeP root, std::size_t budget, std::function<void()> onChange)
        : root_(std::move(root)), budget_(budget), notify_(std::move(onChange)) {}

    const NodeP&     doc()       const { return root_; }
    const Selection& selection() const { return sel_; }

    void apply(const Edit& edit, Selection selAfter);        // ЄДИНА точка зміни моделі
    void begin(std::string label, std::string mergeKey = {});
    void commit();
    void rollback() noexcept;

    bool undo();
    bool redo();
    void markSaved()      { saved_ = static_cast<long long>(index_); }
    bool isDirty()  const { return saved_ != static_cast<long long>(index_); }

private:
    struct Open {                       // відкрита транзакція
        NodeP       base;               // корінь на початку наміру
        Selection   selBefore;
        std::string label, mergeKey;
        std::size_t born0 = 0;          // g_born на початку
        std::size_t removed = 0;
    };
    void pushStep(Step st);
    void trim();
    void retire(Step dead);             // віддати мертвий крок прибиральникові

    NodeP                 root_;        // ← ЄДИНА змінна комірка в усьому сховищі
    Selection             sel_;
    std::deque<Step>      steps_;       // deque: викидаємо і з кінця, і з ДНА
    std::size_t           index_ = 0;   // скільки кроків застосовано (курсор на лінії)
    long long             saved_ = 0;   // −1 ⇒ збережений стан недосяжний
    std::size_t           bytes_ = 0;   // Σ ваг кроків
    std::size_t           budget_;
    std::optional<Open>   open_;
    std::function<void()> notify_;
    Disposer              disposer_;    // фоновий прибиральник; його визначення — наприкінці
};
```
```ts
export type Selection = { nodeId: string; from: number; to: number };

export type EditResult = {
  root: Node;
  removed: number;        // байти, що пішли з дерева
  dropped: Node[];        // вилучені носії ресурсів — помруть із кроком на дні
  added: Node[];          // додані носії ресурсів — помруть, коли зріжуть гілку повтору
};
export type Edit = (root: Node) => EditResult;

export type Step = {
  before: Node; after: Node;
  selBefore: Selection; selAfter: Selection;
  label: string; mergeKey: string;
  weight: number;
  dropped: Node[]; added: Node[];
  at: number;
};

export class Store {
  private root: Node;                       // ← єдина змінна комірка
  private sel: Selection = { nodeId: "", from: 0, to: 0 };
  private steps: Step[] = [];
  private index = 0;                        // курсор на лінії історії
  private saved = 0;                        // −1 ⇒ збережений стан недосяжний
  private bytes = 0;
  private open: {
    base: Node; selBefore: Selection; label: string; mergeKey: string;
    born0: number; removed: number; dropped: Node[]; added: Node[];
  } | null = null;

  constructor(root: Node,
              private budget: number,
              private notify: () => void) { this.root = root; }

  doc(): Node { return this.root; }
  selection(): Selection { return this.sel; }
  markSaved(): void { this.saved = this.index; }
  isDirty(): boolean { return this.saved !== this.index; }
}
```
:::

## Єдина точка: усе, що міняє модель, іде крізь `apply`

Історія відтворює минуле лише з того, що встигла записати. Тому в сховищі є рівно одна функція, яка чіпає `root_`, — і другого шляху немає ні для обробника кнопки, ні для відповіді сервера, ні для таймера.

Сама правка приходить сюди **чистою функцією** «стара версія → нова». Вона нічого не міняє й не знає ні про історію, ні про подання: її можна викликати в тесті, повторити двічі, порівняти результати. Усе, що може піти не так — перевірка, розбір, звернення до чужих даних, — стається всередині неї, **до** того, як хтось торкнувся `root_`.

:::tabs
```cpp
void Store::begin(std::string label, std::string mergeKey) {
    if (open_)
        throw std::logic_error("вкладені транзакції заборонені: намір не буває всередині наміру");
    open_ = Open{ root_, sel_, std::move(label), std::move(mergeKey), g_born, 0 };
}

// Уся модель міняється ТІЛЬКИ тут. Немає другого шляху — і саме тому історія повна.
void Store::apply(const Edit& edit, Selection selAfter) {
    const bool implicit = !open_;             // проста дія — сама собі транзакція
    if (implicit) begin("зміна");
    try {
        EditResult r = edit(root_);           // ← усе, що здатне впасти, падає ТУТ
        root_ = std::move(r.root);            // ← присвоєння вказівника: не кине ніколи
        sel_  = selAfter;
        open_->removed += r.removed;
    } catch (...) {
        rollback();                           // намір не відбувся — стан на початок кроку
        throw;
    }
    notify_();                                // подання перемальовується вже зараз
    if (implicit) commit();
}

void Store::rollback() noexcept {
    if (!open_) return;
    root_ = open_->base;      // одне присвоєння — і все, що встигли побудувати, стає сміттям
    sel_  = open_->selBefore;
    open_.reset();
    notify_();                // ⚠ цей виклик мусить бути noexcept: виняток із відкату вб'є процес
}
```
```ts
  begin(label: string, mergeKey = ""): void {
    if (this.open) throw new Error("вкладені транзакції заборонені: намір не буває всередині наміру");
    this.open = { base: this.root, selBefore: this.sel, label, mergeKey,
                  born0: born, removed: 0, dropped: [], added: [] };
  }

  // Уся модель міняється ТІЛЬКИ тут.
  apply(edit: Edit, selAfter: Selection): void {
    const implicit = !this.open;
    if (implicit) this.begin("зміна");
    try {
      const r = edit(this.root);       // ← усе, що здатне кинути, кидає ТУТ
      this.root = r.root;              // ← присвоєння посилання: не кине ніколи
      this.sel = selAfter;
      this.open!.removed += r.removed;
      this.open!.dropped.push(...r.dropped);
      this.open!.added.push(...r.added);
    } catch (e) {
      this.rollback();
      throw e;
    }
    this.notify();
    if (implicit) this.commit();
  }

  rollback(): void {
    if (!this.open) return;
    this.root = this.open.base;        // одне присвоєння — усе побудоване стає сміттям
    this.sel = this.open.selBefore;
    this.open = null;
    this.notify();
  }
```
:::

Порядок рядків в `apply` — не смак, а вся гарантія цілості. Модель незмінна, тож єдина мутація в цій функції — присвоєння `root_`, і воно стоїть **після** всього, що здатне впасти. Якщо правка кине на середині, `root_` ще дорівнює тому, чим був: стан або став новим цілком, або лишився старим цілком, третього немає. Це та сама сувора гарантія цілості при винятку, якої в змінюваній моделі доводиться домагатися працею [ручного відкоту напівзроблених правок](book:programming/exception-safety), — а тут вона виходить із будови даром.

## Транзакція — це межа наміру

Одна дія людини майже ніколи не дорівнює одній зміні моделі. Перетягування — сотні позицій, оформлення абзацу — три поля, набір слова — сім літер. Транзакція збирає їх в один запис історії, і межу їй ставить не код, а намір: доки намір триває, `root_` міняється (людина мусить бачити, як фігура їде), а історія мовчить.

![Ліворуч намір дійшов до кінця: ланцюжок версій r₀ → r₁ → r₂ → r₃, кожна правка одразу видна на екрані, а в історію лягає один крок із before = r₀ і after = r₃. Праворуч намір урвався: ланцюжок r₀ → r₁ → r₂ обривається червоним хрестом «перевірка не пропустила», довга червона стрілка повертає корінь на r₀ одним присвоєнням, і в історію не лягає нічого](/book/programming/client-architecture/undo-redo-command-stack/img/transaction-boundary.svg)

*Проміжні версії живуть рівно доти, доки на них дивиться екран; в історію потрапляє тільки завершений намір — або не потрапляє нічого.*

:::tabs
```cpp
void Store::commit() {
    if (!open_) return;
    Open op = std::move(*open_);
    open_.reset();
    if (root_ == op.base) return;                     // нічого не змінилося — кроку не буде

    const std::size_t w = (g_born - op.born0) + op.removed;   // додане + вилучене
    const auto now = std::chrono::steady_clock::now();
    using namespace std::chrono_literals;

    const bool canMerge =
        !op.mergeKey.empty() &&
        index_ == steps_.size() &&                    // ми на кінці лінії, гілки повтору немає
        index_ > 0 &&
        steps_.back().mergeKey == op.mergeKey &&      // той самий намір, що й у сусіда
        now - steps_.back().at < 700ms &&             // серія не переривалася паузою
        saved_ != static_cast<long long>(index_);     // ← на цьому кроці стоїть точка збереження

    if (canMerge) {                                   // серія триває — розтягуємо останній крок
        Step& last = steps_.back();
        last.after    = root_;
        last.selAfter = sel_;
        last.weight  += w;
        last.at       = now;
        bytes_ += w;
        trim();
        return;
    }
    pushStep(Step{ op.base, root_, op.selBefore, sel_, std::move(op.label),
                   std::move(op.mergeKey), w, now });
}

// Межа наміру як об'єкт: поки живий — крок відкритий. Вихід із області видимості
// будь-яким шляхом (return, break, виняток) без commit() означає відкат.
class Intent {
public:
    Intent(Store& s, std::string label, std::string mergeKey = {}) : s_(s) {
        s_.begin(std::move(label), std::move(mergeKey));
    }
    ~Intent() { if (!done_) s_.rollback(); }
    void commit() { s_.commit(); done_ = true; }
    Intent(const Intent&) = delete;
    Intent& operator=(const Intent&) = delete;
private:
    Store& s_;
    bool   done_ = false;
};

// Три зміни моделі — один крок історії.
void formatParagraph(Store& store, const std::string& id, const Style& st) {
    Intent step(store, "оформлення абзацу");
    store.apply(setBold  (id, st.bold),   keepSelection(store));
    store.apply(setIndent(id, st.indent), keepSelection(store));
    store.apply(setAlign (id, st.align),  keepSelection(store));  // ← кине — деструктор поверне все
    step.commit();
}
```
```ts
  commit(): void {
    if (!this.open) return;
    const op = this.open;
    this.open = null;
    if (this.root === op.base) return;               // нічого не змінилося — кроку не буде

    const w = (born - op.born0) + op.removed;        // додане + вилучене
    const now = performance.now();

    const canMerge =
      op.mergeKey !== "" &&
      this.index === this.steps.length &&            // ми на кінці лінії
      this.index > 0 &&
      this.steps[this.index - 1].mergeKey === op.mergeKey &&
      now - this.steps[this.index - 1].at < 700 &&
      this.saved !== this.index;                     // ← на цьому кроці стоїть точка збереження

    if (canMerge) {
      const last = this.steps[this.index - 1];
      last.after = this.root; last.selAfter = this.sel;
      last.weight += w; last.at = now;
      last.dropped.push(...op.dropped); last.added.push(...op.added);
      this.bytes += w;
      this.trim();
      return;
    }
    this.pushStep({ before: op.base, after: this.root,
                    selBefore: op.selBefore, selAfter: this.sel,
                    label: op.label, mergeKey: op.mergeKey, weight: w,
                    dropped: op.dropped, added: op.added, at: now });
  }

  // Межа наміру як область видимості: те саме, що робить деструктор у C++, тут робить finally.
  transact<T>(label: string, body: () => T, mergeKey = ""): T {
    this.begin(label, mergeKey);
    let ok = false;
    try { const out = body(); ok = true; this.commit(); return out; }
    finally { if (!ok) this.rollback(); }
  }
```
:::

У C++ межу наміру тримає час життя об'єкта: `Intent` відкриває крок у конструкторі й закриває в деструкторі, тож будь-який вихід із функції — навіть винятком — гарантовано щось зробить із транзакцією. Це [прив'язка ресурсу до часу життя](book:programming/raii) у чистому вигляді, тільки ресурс тут — не файл і не замок, а відкритий крок історії. У TypeScript тієї механіки немає, тож її роль виконує `finally`.

Рядок `saved_ != index_` у переліку умов злиття виглядає випадковим, а насправді лагодить тиху ваду. Якщо документ щойно записали у файл і людина далі набирає той самий текст, злиття дописало б нові літери **в той крок, який породжує збережений стан**. Позиція збереження лишилася б на місці, а стан у ній став би іншим — і зірочка гасла б на документі, який файлові вже не дорівнює.

## Відкат за одне присвоєння

![Лінія історії з семи кроків: чотири застосовані ліворуч, три бліді праворуч — гілка повтору. Знизу стрілка вказує на межу між четвертим і п'ятим: index = 4, стан, який людина бачить зараз; по цій же межі проходить червона пунктирна лінія зрізу. Згори стрілка вказує на межу після шостого кроку: saved = 6, тут документ записали у файл. Ліворуч синя стрілка виводить найстаріший крок за межу — з дна. Унизу дві панелі: випадає з дна — гине корінь «до» найстарішого кроку, звільняється те, що крок вилучив, saved з'їжджає вниз і під нулем стає мінус один; зрізається гілка повтору — гинуть корені «після» зрізаних кроків, звільняється те, що кроки додали, saved у зрізаному стає мінус один назавжди](/book/programming/client-architecture/undo-redo-command-stack/img/history-line.svg)

*Історія — це лінія з курсором, а не стос: із неї випадають кроки з двох кінців, і кінці ці поводяться по-різному.*

:::tabs
```cpp
void Store::pushStep(Step st) {
    // 1. Зріз гілки повтору: після нової дії старе майбутнє недосяжне
    while (steps_.size() > index_) {
        bytes_ -= steps_.back().weight;
        retire(std::move(steps_.back()));    // гине after зрізаних кроків → звільняється ДОДАНЕ
        steps_.pop_back();
    }
    if (saved_ > static_cast<long long>(index_))
        saved_ = -1;                         // точка збереження була в зрізаному — уже недосяжна

    // 2. Новий крок
    bytes_ += st.weight;
    steps_.push_back(std::move(st));
    ++index_;

    // 3. Бюджет
    trim();
}

bool Store::undo() {
    if (open_) return false;         // усередині незавершеного наміру відкочувати нема чого
    if (index_ == 0) return false;
    const Step& s = steps_[index_ - 1];
    root_ = s.before;                // ← ВЕСЬ відкат: одне присвоєння вказівника
    sel_  = s.selBefore;             // ← і людина опиняється там, де діяла
    --index_;
    notify_();
    return true;
}

bool Store::redo() {
    if (open_ || index_ >= steps_.size()) return false;
    const Step& s = steps_[index_];
    root_ = s.after;
    sel_  = s.selAfter;
    ++index_;
    notify_();
    return true;
}
```
```ts
  private pushStep(st: Step): void {
    // 1. Зріз гілки повтору
    while (this.steps.length > this.index) {
      const cut = this.steps.pop()!;
      this.bytes -= cut.weight;
      this.retire(cut, "top");          // гине after зрізаних кроків → звільняється ДОДАНЕ
    }
    if (this.saved > this.index) this.saved = -1;   // точка збереження була в зрізаному

    // 2. Новий крок
    this.bytes += st.weight;
    this.steps.push(st);
    this.index++;

    // 3. Бюджет
    this.trim();
  }

  undo(): boolean {
    if (this.open || this.index === 0) return false;
    const s = this.steps[this.index - 1];
    this.root = s.before;               // ← весь відкат: одне присвоєння посилання
    this.sel = s.selBefore;
    this.index--;
    this.notify();
    return true;
  }

  redo(): boolean {
    if (this.open || this.index >= this.steps.length) return false;
    const s = this.steps[this.index];
    this.root = s.after;
    this.sel = s.selAfter;
    this.index++;
    this.notify();
    return true;
  }
```
:::

Варто вгледіти, чому `undo` — це чесне O(1), а не «O(1) з раптовою паузою». Присвоєння `root_ = s.before` зменшує [лічильник посилань](book:programming/reference-counting) старого кореня — але не до нуля: той самий крок тримає його в полі `after`. Жодна лавина звільнення не запускається. Уся робота зі знищення відкладена до єдиної миті, коли крок справді випаде з історії, — і саме тому нею можна керувати.

## Точка збереження — це індекс, а не прапорець

`markSaved` запам'ятовує **позицію на лінії**, а `isDirty` порівнює її з поточною. Прапорець `dirty = true` на кожну зміну був би простішим і брехав би в найочевиднішому випадку: змінив — зберіг — змінив — скасував; документ дорівнює файлу, зірочка світить.

Позиція має два способи стати недосяжною, і обидва в коді вище видно рядком. Перший — **зріз**: людина відкотилася на три кроки, зробила нову дію, і гілка повтору, у якій лежала точка збереження, зникла (`saved_ = -1` в `pushStep`). Другий — **дно**: бюджет вичерпався, і кроки під точкою збереження викинуто, тож той стан уже не відтворити (`saved_` з'їжджає вниз і, пішовши під нуль, стає −1). В обох випадках −1 означає «жодна позиція історії не дорівнює файлові», і документ чесно вважається зміненим, скільки б разів не тиснути «назад». Це не перестраховка: стану, що лежить у файлі, з цієї лінії справді більше не дістати.

Є й інший спосіб — тримати не індекс, а **сам вказівник** на збережений корінь і питати `root_ != savedRoot_`. У незмінній моделі тотожність вказівника означає тотожність вмісту, тож така перевірка теж O(1) і не боїться ні зрізу, ні обрізання дна. Ціна в неї своя, і чимала: збережений корінь **пришпилює** всю ту версію разом із тим, що з неї потім вилучили, тобто прямо воює з бюджетом історії. Індекс дешевший пам'яттю, вказівник — точніший; вибирають за тим, що дорожче в конкретному застосунку.

## Бюджет у байтах і те, що нарешті звільняється

Обмежувати історію кількістю кроків марно: один крок важить сорок байтів (набрана літера) або двісті мегабайтів (вилучена картинка). Тому стеля ставиться в байтах, а вага кроку рахується як **додане плюс вилучене** — і друга половина цієї суми найважливіша.

**Умова.** Дерево документа — 200 000 вузлів, гілкування ≈ 8, отже глибина h ≈ log₈(200 000) ≈ 6. Бюджет історії — 64 МБ.

```
вага одного вузла (own):
  sizeof(Node)                     ≈ 104 Б   (два std::string, вектор, два size_t)
  керувальний блок shared_ptr      ≈  24 Б
  масив дітей у купі (8 × 8 Б)     ≈  64 Б
  ─────────────────────────────────────────
  разом                            ≈ 192 Б

крок «натиснули клавішу» — копіюється лише дорога від кореня:
  нових вузлів  = h                = 6
  вага кроку    = 6 × 192 Б        ≈ 1.2 КБ
  кроків у бюджет: 64 МБ / 1.2 КБ  ≈ 55 000

крок «вилучили зображення на 8 МБ»:
  додане        = та сама дорога   ≈ 1.2 КБ
  вилучене      = вага піддерева   = 8 МБ
  вага кроку                       ≈ 8 МБ
  кроків у бюджет: 64 МБ / 8 МБ    = 8
```

Різниця між 55 000 і 8 — це відповідь на питання, чому ліміт «сто кроків» нічого не гарантує: сто кроків набору тексту важать 120 КБ, а сто кроків із вилученням картинок — вісімсот мегабайтів.

:::tabs
```cpp
void Store::trim() {
    // Курсор на дні (людина відкотилася в самий початок) — з дна брати нема чого:
    // там лежить теперішній стан. Тоді бюджет доводиться відбирати з іншого кінця,
    // зрізаючи найдальші кроки повтору, — і «вперед» перестане діставати до кінця.
    while (bytes_ > budget_ && steps_.size() > 1 && index_ > 0) {
        bytes_ -= steps_.front().weight;
        Step dead = std::move(steps_.front());
        steps_.pop_front();
        --index_;                                     // курсор з'їхав разом із дном
        if (saved_ >= 0) saved_ = (saved_ > 0 ? saved_ - 1 : -1);
        retire(std::move(dead));                      // ← тут «вилучене» нарешті помирає
    }
}

// Фоновий прибиральник. Крок, що випав із історії, — останній власник усього, що бачив
// лише він; його деструктор може звільняти сотні тисяч вузлів, а це помітна пауза.
// Вузли незмінні, лічильники shared_ptr атомарні — тож помирати в чужому потоці їм безпечно.
class Disposer {
public:
    Disposer() : th_([this] { loop(); }) {}
    ~Disposer() {
        { std::lock_guard lk(m_); stop_ = true; }
        cv_.notify_all();
        th_.join();
    }
    void post(Step dead) {
        { std::lock_guard lk(m_); q_.push_back(std::move(dead)); }
        cv_.notify_one();
    }
private:
    void loop() {
        for (;;) {
            std::deque<Step> batch;
            {
                std::unique_lock lk(m_);
                cv_.wait(lk, [this] { return stop_ || !q_.empty(); });
                if (stop_ && q_.empty()) return;
                batch.swap(q_);
            }
            batch.clear();     // ← ось тут і звільняються вузли, які тримала історія
        }
    }
    std::deque<Step>        q_;
    std::mutex              m_;
    std::condition_variable cv_;
    bool                    stop_ = false;
    std::thread             th_;
};

void Store::retire(Step dead) { disposer_.post(std::move(dead)); }
```
```ts
  private trim(): void {
    while (this.bytes > this.budget && this.steps.length > 1 && this.index > 0) {
      const dead = this.steps.shift()!;   // O(n) на масиві: для десятків тисяч кроків
      this.bytes -= dead.weight;          // беруть кільцевий буфер або зсув-основу
      this.index--;
      if (this.saved >= 0) this.saved = this.saved > 0 ? this.saved - 1 : -1;
      this.retire(dead, "bottom");
    }
  }

  // Пам'ять звільнить збирач сміття — сам і колись. Але жодного деструктора він не викличе:
  // URL.revokeObjectURL, texture.delete(), закриття файлу — це доводиться робити руками.
  // Тому крок і носить два списки: з дна помирає ВИЛУЧЕНЕ ним, зі зрізу — ДОДАНЕ ним.
  private retire(dead: Step, end: "bottom" | "top"): void {
    for (const n of end === "bottom" ? dead.dropped : dead.added) n.res?.release();
  }
```
:::

Дві половини вивільнення несиметричні, і плутати їх не можна. Коли крок випадає **з дна**, гине його корінь «до» — а він був останнім, хто тримав вилучене цим кроком: ось де через півгодини після натискання `Delete` справді звільняється зображення на двісті мегабайтів. Коли ж зрізається **гілка повтору**, гинуть корені «після» — і звільняється те, що ті кроки додали. Стерте піддерево при зрізі не чіпають узагалі: воно живе в теперішньому стані, бо його вилучення ще попереду.

У C++ обидва випадки закриває сам час життя: помер останній `shared_ptr` — спрацював деструктор вузла й віддав усе, чим той володів. Треба керувати лише тим, **коли й у якому потоці** це станеться. У TypeScript такої опори немає: [збирач сміття](book:programming/garbage-collection) поверне пам'ять, але не викличе нічого, тож зовнішній ресурс доводиться віддавати списком. На `FinalizationRegistry` тут покладатися не можна — специфікація прямо звільняє двигун від обов'язку: зворотний виклик може статися пізніше, ніж очікуєш, а може не статися взагалі, і при закритті вкладки його зазвичай не буде.

## Скільки коштує кожна операція

```
Операція                        Вартість
──────────────────────────────────────────────────────────────────────────────
mk (народження вузла)           O(1) — вага піддерева складається з готових ваг дітей
replaceById / removeById        O(h) нових вузлів на дорозі; пошук id без індексу — O(n)
apply                           вартість самої правки + O(h)
begin / commit                  O(1)
rollback                        O(1) — одне присвоєння кореня
undo / redo                     O(1) — присвоєння кореня; від розміру документа НЕ залежить
markSaved / isDirty             O(1)
pushStep зі зрізом гілки        O(k), k — довжина зрізаної гілки повтору
trim, один крок із дна          O(1) на облік + O(m) на звільнення m вузлів, що вмирають
пам'ять історії                 Σ weight ≤ бюджет
```

Ті самі числа варто закріпити переліком [інваріантів](book:programming/invariants) — умов, істинних до й після кожної операції; у зневаджувальній збірці їх перевіряють після кожного `commit`, і вони ловлять майже всі помилки обліку:

```
0 ≤ index_ ≤ steps_.size()
index_ > 0        ⟹  root_ == steps_[index_ − 1].after
index_ == 0       ⟹  root_ == steps_.front().before        (або історія порожня)
steps_[i].after   == steps_[i + 1].before                   (ланцюг без розривів)
saved_ == −1  або  0 ≤ saved_ ≤ steps_.size()
bytes_ == Σ steps_[i].weight
open_ != nullopt  ⟹  жоден крок не додано й не викинуто
```

## Пастки

**Зріз гілки повтору забирає точку збереження.** Найпоширеніша реалізація `push` просто відрізає хвіст і не чіпає `saved_` — і документ починає вважати себе збереженим у стані, якого вже не існує. Механізм видно на лінії: збереження стояло в тій частині майбутнього, яку щойно відрізали; жодна досяжна позиція йому більше не відповідає. Правильна відповідь — −1 і чесне «змінено» назавжди, а не спроба вгадати найближчу позицію.

**Напіврозпочатий крок в історії гірший за відсутність історії.** Якщо транзакція впала на третій зміні з п'яти, а в стек ліг крок із `after`, узятим на середині, то його відкат обертатиме на моделі, що вже пішла далі, — і зіпсує документ мовчки, без жодного повідомлення. Умова тут двоскладова: незмінна модель дає гарантію цілості (єдина мутація стоїть після всього, що падає), а `Intent`/`finally` — гарантію, що ніхто не забуде відкотитися. Ще одна дрібниця з цього ж боку: сповіщення подання всередині відкоту не має права кинути виняток — у C++ це `std::terminate` просто тому, що деструктор і `noexcept`-відкат винятків не пропускають.

**Історія роками тримає живими «видалені» об'єкти.** Це не витік, а плата за оборотність, але вона мусить бути керованою. Симптом упізнаваний: пам'ять росте цілий день і не спадає, хоч людина все повидаляла. Причина в тому, що бюджет міряє неправильну величину — лічильник **народжених** байтів сліпий саме до вилучення, бо `Delete` народжує тільки шість вузлів дороги. Лікує це доданок «вилучене» у вазі кроку, а щоб він був дешевим, вага піддерева має бути кешованою в самому вузлі.

**Переміщення — не вилучення.** Якщо правка переносить піддерево в інше місце тим самим кроком, вона не сміє звітувати про нього як про вилучене: вага кроку роздується вдвічі, а в TypeScript ще й спрацює `release()` на вузлі, який живий і видимий на екрані. Правило просте: вилучене — це те, чого немає в **остаточному** корені кроку, і стежить за цим сама правка.

**Виділення, записане позицією.** «Третій абзац згори» після відкоту може виявитися зовсім іншим абзацом, бо сусіди з'явилися й зникли. У кроці має лежати `id` вузла — той самий, що переживає всі версії. Із тієї ж причини прокрутку зазвичай не відновлюють дослівно: правильна поведінка — не «повернути екран, як стояв», а доскролити до місця зміни, якщо воно поза видимим.

**Лічильник міряє народжене, а не живе.** Коли серія літер зливається в один крок, проміжні версії викидаються одразу, а лічильник уже порахував їхні дороги. Вага злитого кроку виходить завищеною — і це правильна сторона помилки: бюджет тримається із запасом, а не з проваллям. Знати про це варто, коли дивуєшся, чому історія обрізається раніше, ніж малює арифметика.

**Пошук вузла за `id` — обхід дерева.** У показаному коді `replaceById` у гіршому разі проходить усе дерево, і на двохсоттисячному документі це помітно на кожній літері. Виправляють це не в історії, а поруч: сховище тримає покажчик `id → дорога від кореня`, і тоді правка одразу спускається куди треба, а вартість повертається до O(h). Для першої робочої версії обхід годиться; для другої — уже ні.

**Звільнення в потоці інтерфейсу.** Смерть кроку з великим піддеревом — це десятки тисяч атомарних зменшень лічильника й стільки ж викликів `delete`; у потоці, який малює кадри, це видима судома. Фоновий прибиральник її знімає, але вносить власне зауваження: ресурс, прив'язаний до свого потоку (текстура графічного контексту, дескриптор вікна), не можна звільняти будь-де — такий вузол мусить віддати ресурс назад у свій потік, а вже потім помирати. І окрема дрібниця для довгих ланцюгів: знищення однозв'язної структури йде рекурсією завглибшки в її довжину — [пастка, що переповнює стек на мільйоні вузлів](book:programming/immutability/proj-persistent-structures.md); дерево з логарифмічною глибиною від неї застраховане, довгий список — ні.
