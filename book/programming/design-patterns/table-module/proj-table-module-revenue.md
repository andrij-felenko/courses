# ⚙️ Модуль таблиці, що працює: набір рядків з індексом і визнання виторгу

Тут патерн зібрано цілком і в робочому вигляді: власний набір рядків із типізованими колонками, індексом за первинним ключем і міткою стану на кожному рядку; два модулі над ним, що розмовляють між собою ключами; підсумок «визнано на дату» як операція над набором; і дорога накопичених змін назад у базу — одним рухом і в одній транзакції. Дивитися на це варто заради двох речей, яких з опису патерну не видно: чому індекс тут не оптимізація, а умова, без якої все розсипається, і в яких саме місцях конструкція починає тріщати.

## Задача

Продаємо три товари: текстовий редактор, табличний процесор і базу даних. Контракт фіксує один товар, суму й дату підписання. Виторг визнається за розкладом, що залежить від типу товару: за редактор і за базу — увесь у день підписання; за табличний процесор — трьома рівними частками: у день підписання, через 60 і через 90 днів.

Треба вміти три речі:

1. за контрактом розкласти виторг на визнання;
2. відповісти, скільки визнано станом на дату;
3. дати підсумок за всім набором — скільки визнано на дату в розрізі типу товару.

Дані приходять трьома таблицями і в такому самому вигляді йдуть на екран, у звіт і назад у базу:

```
products      (id, kind)
contracts     (id, product_id, revenue, signed_on)
recognitions  (id, contract_id, amount, recognized_on)
```

Це той випадок, для якого патерн і придумано: [набір рядків](book:programming/record-set) — таблицеподібна копія результату запиту, з тими самими колонками, — ходить системою наскрізь, і нічого перекладати в об'єкти й назад не треба.

## Що всередині набору рядків

Набір рядків має вміти чотири речі, і кожна з них потім проступить у коді модуля.

**Колонки з типами.** Рядок плаский: значення за іменем колонки, а не поля об'єкта з поведінкою. Тип потрібен, щоб порівняння дат було порівнянням дат, а додавання грошей — додаванням, а не склеюванням тексту.

**Індекс за первинним ключем.** Модуль не має тотожності: він не знає, «про кого» зараз розмова, тому кожен виклик починається з пошуку рядка за ключем. Якщо цей пошук — прохід по таблиці, то будь-яка масова операція стає квадратичною.

**Вторинний індекс за чужим ключем.** Питання «усі визнання контракту 17» виникає на кожному виклику, і відповідати на нього перебором усієї таблиці визнань так само згубно.

**Мітку стану на кожному рядку.** Набір живе відірваним від бази: правки накопичуються в пам'яті, а поїдуть одним рухом. Щоб було що надсилати, треба знати, який рядок додано, який змінено, який вилучено — і які були вихідні значення, якщо доведеться вертати назад.

![Що всередині набору рядків. Угорі ліворуч зелена рамка індекс за id зі списком 17 стрілка слот 0, 18 стрілка слот 1, 19 стрілка слот 2 і підписами хеш-таблиця та пошук приблизно O(1); від неї стрілка вправо до таблиці contracts з колонками id, product_id, revenue, signed_on, стан, під іменами колонок курсивом типи int64, int64, копійки int64, доба int32, мітка, і трьома рядками: 17, 3, 100000, 20522, без змін; 18, 4, 60000, 20531, змінено; 19, 3, 90000, 20540, додано; праворуч підпис колонка стану — не дані, а мітка, що саме поїде в базу. Унизу ліворуч зелена рамка вторинний індекс за contract_id зі списком 17 стрілка список слотів 0, 1, 2 та 18 стрілка список слота 3 і підписом усі рядки контракту без обходу таблиці; від неї стрілка вправо до таблиці recognitions з колонками id, contract_id, amount, recognized_on, стан і чотирма рядками визнань, три з яких належать контракту 17; праворуч червоний підпис без цього індексу визнано на дату перебирає всі визнання. Унизу через усю ширину напис модуль не тримає ні рядка, ні покажчика на нього: між викликами живе тільки ключ, а нижче курсивом покажчик у C++ дійсний лише до наступної вставки, тому його не зберігають](img/recordset-inside.svg)

*Набір рядків — це не «масив структур». Це рядки плюс мітки стану плюс індекси, і кожна з трьох частин відповідає за свою потребу патерну: індекс за первинним ключем — за дешеве звертання по ключу, індекс за чужим ключем — за питання «усі рядки цього контракту», мітки — за одну поїздку в базу замість багатьох.*

У C# ця структура вже написана — це `DataSet`, і всі чотири речі в ньому вбудовані, крім вторинного індексу, який заводять руками. У C++ її пишемо самі, і саме тому видно, з чого вона складається.

:::tabs
```cpp
#include <cstdint>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using Id    = std::int64_t;
using Money = std::int64_t;   // гроші — цілі копійки, ніяких double
using Day   = std::int32_t;   // дата — номер доби від епохи

enum class RowState : std::uint8_t { Unchanged, Added, Modified, Deleted };

// Таблиця набору рядків: рядки + мітка стану на кожен + два індекси.
// Від Row вимагається одне поле — Id id, це первинний ключ.
template <class Row>
class Table {
public:
    struct Change { RowState state; const Row* row; };

    void load(Row r)   { add(std::move(r), RowState::Unchanged); }  // приїхало з бази
    void insert(Row r) { add(std::move(r), RowState::Added); }      // народилося тут

    const Row* find(Id id) const {                   // ← це місце вирішує все
        auto it = index_.find(id);
        return it == index_.end() ? nullptr : &rows_[it->second];
    }

    Row* modify(Id id) {                             // те саме, але з міткою «змінено»
        auto it = index_.find(id);
        if (it == index_.end()) return nullptr;
        touch(it->second);
        return &rows_[it->second];
    }

    void erase(Id id) {
        auto it = index_.find(id);
        if (it == index_.end()) return;
        touch(it->second);
        state_[it->second] = RowState::Deleted;      // не викидаємо: базі ще треба сказати
    }

    std::size_t size() const               { return rows_.size(); }
    const Row&  at(std::size_t i) const    { return rows_[i]; }
    bool        alive(std::size_t i) const { return state_[i] != RowState::Deleted; }

    void indexBy(Id Row::* column) { column_ = column; rebuild(); }   // вторинний індекс

    const std::vector<std::size_t>& rowsWith(Id key) const {
        static const std::vector<std::size_t> none;
        auto it = secondary_.find(key);
        return it == secondary_.end() ? none : it->second;
    }

    std::vector<Change> changes() const {
        std::vector<Change> out;
        for (std::size_t i = 0; i < rows_.size(); ++i)
            if (state_[i] != RowState::Unchanged) out.push_back({state_[i], &rows_[i]});
        return out;
    }

    void accept() {                                  // база прийняла все
        std::vector<Row> kept;
        kept.reserve(rows_.size());
        for (std::size_t i = 0; i < rows_.size(); ++i)
            if (state_[i] != RowState::Deleted) kept.push_back(std::move(rows_[i]));
        settle(std::move(kept));
    }

    void reject() {                                  // назад до вихідних значень
        std::vector<Row> kept;
        for (std::size_t i = 0; i < rows_.size(); ++i) {
            if (state_[i] == RowState::Added) continue;          // доданого не було
            auto o = original_.find(rows_[i].id);
            kept.push_back(o == original_.end() ? std::move(rows_[i]) : std::move(o->second));
        }
        settle(std::move(kept));
    }

private:
    void add(Row r, RowState st) {
        if (index_.count(r.id)) throw std::logic_error("дубль первинного ключа");
        const std::size_t slot = rows_.size();
        index_.emplace(r.id, slot);
        if (column_) secondary_[r.*column_].push_back(slot);
        rows_.push_back(std::move(r));
        state_.push_back(st);
    }

    void touch(std::size_t i) {
        if (state_[i] == RowState::Unchanged) {
            original_.emplace(rows_[i].id, rows_[i]);   // копія вихідного — щоб було що вертати
            state_[i] = RowState::Modified;
        }
    }

    void settle(std::vector<Row> kept) {
        rows_ = std::move(kept);
        state_.assign(rows_.size(), RowState::Unchanged);
        original_.clear();
        rebuild();
    }

    void rebuild() {                                 // слоти зсунулися — індекси наново
        index_.clear();
        secondary_.clear();
        for (std::size_t i = 0; i < rows_.size(); ++i) {
            index_[rows_[i].id] = i;
            if (column_) secondary_[rows_[i].*column_].push_back(i);
        }
    }

    std::vector<Row>      rows_;     // колонки — поля структури, перевірені компілятором
    std::vector<RowState> state_;    // мітка на кожен рядок, паралельним масивом
    std::unordered_map<Id, std::size_t>              index_;      // id → слот
    std::unordered_map<Id, std::vector<std::size_t>> secondary_;  // чужий ключ → слоти
    std::unordered_map<Id, Row>                      original_;   // вихідні значення змінених
    Id Row::* column_ = nullptr;
};

struct Product     { Id id; std::string kind; };
struct Contract    { Id id; Id productId; Money revenue; Day signedOn; };
struct Recognition { Id id; Id contractId; Money amount; Day on; };

struct SalesData {                                   // це і є набір рядків застосунку
    Table<Product>     products;
    Table<Contract>    contracts;
    Table<Recognition> recognitions;
    Id nextTempId = -1;        // тимчасові ключі від'ємні: справжні роздасть база
};

inline SalesData makeSalesData() {
    SalesData d;
    d.recognitions.indexBy(&Recognition::contractId);   // без цього «усі рядки контракту»
    return d;                                           // тихо стає перебором
}
```
```cs
using System;
using System.Data;

// У .NET набір рядків уже написаний. Типи колонок, індекс за первинним ключем
// і стан рядка вбудовані; вторинний індекс доводиться заводити руками.
public static DataSet MakeSalesData()
{
    var data = new DataSet("sales");

    DataTable products = data.Tables.Add("products");
    products.Columns.Add("id", typeof(long));
    products.Columns.Add("kind", typeof(string));
    products.PrimaryKey = new[] { products.Columns["id"] };

    DataTable contracts = data.Tables.Add("contracts");
    contracts.Columns.Add("id", typeof(long));
    contracts.Columns.Add("product_id", typeof(long));
    contracts.Columns.Add("revenue", typeof(decimal));       // гроші — decimal, не double
    contracts.Columns.Add("signed_on", typeof(DateTime));
    contracts.PrimaryKey = new[] { contracts.Columns["id"] }; // ← індекс, яким живе Rows.Find

    DataTable recognitions = data.Tables.Add("recognitions");
    DataColumn rid = recognitions.Columns.Add("id", typeof(long));
    rid.AutoIncrement = true;
    rid.AutoIncrementSeed = -1;      // тимчасові ключі від'ємні: справжні роздасть база
    rid.AutoIncrementStep = -1;
    recognitions.Columns.Add("contract_id", typeof(long));
    recognitions.Columns.Add("amount", typeof(decimal));
    recognitions.Columns.Add("recognized_on", typeof(DateTime));
    recognitions.PrimaryKey = new[] { recognitions.Columns["id"] };

    return data;
}

// Мітка стану вже є на кожному рядку: row.RowState ∈ { Unchanged, Added, Modified, Deleted },
// а row["revenue", DataRowVersion.Original] віддасть значення, яке було до правки.
// Вторинний індекс за чужим ключем — це DataView із заданим Sort:
//     var byContract = new DataView(recognitions) { Sort = "contract_id" };
// Такий DataView будує індекс за колонкою, і FindRows шукає ним, а не перебором.
```
:::

Двома мовами однаково видно чотири частини, але місце перевірки типів у них різне. У `DataSet` значення лежить як `object`, а тип колонки оголошено під час виконання — тому той самий екземпляр здатний прийняти схему, яку віддасть база, і показати будь-який запит у сітці, нічого не перекомпільовуючи. У C++ колонки — це поля структури, і компілятор ловить `contract["revenu"]` ще до запуску, зате схема мусить бути відома під час компіляції. Патерн виріс на першому варіанті не випадково: там, де набір рядків справді спільна мова застосунку, схема часто приходить разом із даними.

## Модулі: правило живе тут

Модуль — це поведінка без власних даних. Набір йому дають ззовні, рядок називають ключем у виклику, а сусідній модуль питають так само — ключем, а не посиланням.

Одну річ варто зробити інакше, ніж у найпростішому варіанті, і зробити одразу: розклад визнання не пишемо ланцюжком `if`, а кладемо **таблицею** — тип товару відображаємо в перелік зсувів у днях. Розклад «увесь у день підписання» стає списком з одного нуля, «трьома частками» — списком `{0, 60, 90}`, і обидва проходять тим самим кодом.

:::tabs
```cpp
#include <map>

// Розклад визнання: правило таблицею. Ключ — тип товару,
// значення — зсуви часток у днях від дати підписання.
inline const std::unordered_map<std::string, std::vector<int>>& schedules() {
    static const std::unordered_map<std::string, std::vector<int>> table = {
        {"word-processor", {0}},
        {"database",       {0}},
        {"spreadsheet",    {0, 60, 90}},
    };
    return table;
}

// Ділення з округленням донизу — щоб залишок ніколи не був від'ємним.
inline Money floorDiv(Money a, Money b) {
    Money q = a / b;                                    // у C++ ділення цілих усікає до нуля
    if (a % b != 0 && ((a < 0) != (b < 0))) --q;
    return q;
}

// Ділимо суму на n часток так, щоб їхня сума ТОЧНО дорівнювала цілому.
// Залишок (менший за n копійок) роздаємо в останні частки.
inline std::vector<Money> splitEvenly(Money total, std::size_t n) {
    if (n == 0) throw std::logic_error("порожній розклад");
    const Money base = floorDiv(total, static_cast<Money>(n));
    Money rest = total - base * static_cast<Money>(n);  // 0 ≤ rest < n
    std::vector<Money> parts(n, base);
    for (std::size_t i = n; rest > 0; --rest) parts[--i] += 1;
    return parts;
}

class ProductModule {
public:
    explicit ProductModule(const SalesData& d) : d_(d) {}

    const std::string& kindOf(Id productId) const {
        const Product* p = d_.products.find(productId);
        if (!p) throw std::logic_error("немає товару " + std::to_string(productId));
        return p->kind;
    }
private:
    const SalesData& d_;
};

class ContractModule {
public:
    explicit ContractModule(SalesData& d) : d_(d) {}

    void calculateRecognitions(Id contractId) {
        const Contract* c = d_.contracts.find(contractId);   // один доступ, не перебір
        if (!c) throw std::logic_error("немає контракту " + std::to_string(contractId));
        const Money revenue = c->revenue;         // значення забираємо ЗАРАЗ: покажчик
        const Day   signedOn = c->signedOn;       // дійсний лише до наступної вставки
        const std::string kind = ProductModule(d_).kindOf(c->productId);

        auto it = schedules().find(kind);
        if (it == schedules().end()) throw std::logic_error("немає розкладу: " + kind);
        const std::vector<int>& offsets = it->second;

        dropRecognitions(contractId);             // повторний виклик не подвоює рядки
        const std::vector<Money> parts = splitEvenly(revenue, offsets.size());
        for (std::size_t i = 0; i < offsets.size(); ++i)
            d_.recognitions.insert(Recognition{d_.nextTempId--, contractId,
                                               parts[i], signedOn + offsets[i]});
    }

    Money recognizedAsOf(Id contractId, Day asOf) const {
        Money sum = 0;
        for (std::size_t i : d_.recognitions.rowsWith(contractId)) {   // тільки свої рядки
            if (!d_.recognitions.alive(i)) continue;
            const Recognition& r = d_.recognitions.at(i);
            if (r.on <= asOf) sum += r.amount;
        }
        return sum;
    }

    // Підсумок за НАБОРОМ: один прохід по визнаннях, решта — доступи за ключем.
    std::map<std::string, Money> recognizedByKind(Day asOf) const {
        std::map<std::string, Money> total;
        ProductModule products(d_);
        for (std::size_t i = 0; i < d_.recognitions.size(); ++i) {
            if (!d_.recognitions.alive(i)) continue;
            const Recognition& r = d_.recognitions.at(i);
            if (r.on > asOf) continue;
            const Contract* c = d_.contracts.find(r.contractId);
            if (!c) continue;                       // осиротіле визнання — не наша справа
            total[products.kindOf(c->productId)] += r.amount;
        }
        return total;
    }

private:
    void dropRecognitions(Id contractId) {
        for (std::size_t i : d_.recognitions.rowsWith(contractId))
            if (d_.recognitions.alive(i)) d_.recognitions.erase(d_.recognitions.at(i).id);
    }

    SalesData& d_;
};
```
```cs
using System;
using System.Collections.Generic;
using System.Data;

public sealed class ProductModule
{
    private readonly DataSet _data;
    public ProductModule(DataSet data) => _data = data;

    public string KindOf(long productId)
    {
        DataRow row = _data.Tables["products"].Rows.Find(productId)
                      ?? throw new InvalidOperationException($"немає товару {productId}");
        return (string)row["kind"];
    }
}

public sealed class ContractModule
{
    // Розклад визнання: правило таблицею. Ключ — тип товару,
    // значення — зсуви часток у днях від дати підписання.
    private static readonly Dictionary<string, int[]> Schedules = new()
    {
        ["word-processor"] = new[] { 0 },
        ["database"]       = new[] { 0 },
        ["spreadsheet"]    = new[] { 0, 60, 90 },
    };

    private readonly DataSet _data;
    private readonly DataView _byContract;      // вторинний індекс за чужим ключем

    public ContractModule(DataSet data)
    {
        _data = data;
        _byContract = new DataView(data.Tables["recognitions"]) { Sort = "contract_id" };
    }

    public void CalculateRecognitions(long contractId)
    {
        DataRow contract = _data.Tables["contracts"].Rows.Find(contractId)   // індексом за PK
                           ?? throw new InvalidOperationException($"немає контракту {contractId}");
        decimal revenue = (decimal)contract["revenue"];
        DateTime signed = (DateTime)contract["signed_on"];
        string kind = new ProductModule(_data).KindOf((long)contract["product_id"]);

        if (!Schedules.TryGetValue(kind, out int[] offsets))
            throw new InvalidOperationException($"немає розкладу: {kind}");

        DropRecognitions(contractId);           // повторний виклик не подвоює рядки
        decimal[] parts = SplitEvenly(revenue, offsets.Length);
        DataTable table = _data.Tables["recognitions"];
        for (int i = 0; i < offsets.Length; i++)
        {
            DataRow row = table.NewRow();
            row["contract_id"] = contractId;
            row["amount"] = parts[i];
            row["recognized_on"] = signed.AddDays(offsets[i]);
            table.Rows.Add(row);                // рядок одразу стає Added
        }
    }

    public decimal RecognizedAsOf(long contractId, DateTime asOf)
    {
        decimal sum = 0m;
        foreach (DataRowView v in _byContract.FindRows(contractId))   // індексом, не перебором
            if ((DateTime)v["recognized_on"] <= asOf) sum += (decimal)v["amount"];
        return sum;
    }

    // Підсумок за НАБОРОМ: один прохід по визнаннях, решта — доступи за ключем.
    public IDictionary<string, decimal> RecognizedByKind(DateTime asOf)
    {
        var total = new SortedDictionary<string, decimal>();
        var products = new ProductModule(_data);
        DataTable contracts = _data.Tables["contracts"];
        foreach (DataRow r in _data.Tables["recognitions"].Rows)
        {
            if (r.RowState == DataRowState.Deleted) continue;   // до вилученого не дотягнешся
            if ((DateTime)r["recognized_on"] > asOf) continue;
            DataRow c = contracts.Rows.Find((long)r["contract_id"]);
            if (c == null) continue;                        // осиротіле визнання
            string kind = products.KindOf((long)c["product_id"]);
            total.TryGetValue(kind, out decimal had);
            total[kind] = had + (decimal)r["amount"];
        }
        return total;
    }

    // Ділимо так, щоб сума часток ТОЧНО дорівнювала цілому:
    // кожну — вниз до копійки, залишок — в останні частки.
    private static decimal[] SplitEvenly(decimal total, int n)
    {
        const decimal cent = 0.01m;
        decimal each = decimal.Floor(total / n / cent) * cent;
        int rest = (int)((total - each * n) / cent);            // 0 ≤ rest < n
        decimal[] parts = new decimal[n];
        for (int i = 0; i < n; i++) parts[i] = each;
        for (int i = n; rest > 0; rest--) parts[--i] += cent;
        return parts;
    }

    private void DropRecognitions(long contractId)
    {
        foreach (DataRowView v in _byContract.FindRows(contractId))
            v.Row.Delete();      // рядок лишається в наборі з міткою Deleted
    }
}
```
:::

Дві дрібниці в цьому коді варті окремої уваги, бо вони не про синтаксис.

Перша: `const Contract* c` живе рівно до наступної вставки в ту саму таблицю — далі `std::vector` може переїхати в іншу пам'ять, і покажчик стане недійсним. Тому значення з рядка забирають одразу, а потім користуються ключем. Це не C++-специфічна пересторога, а той самий факт із іншого боку: у модуля немає тотожності, і єдина довговічна ручка на рядок — його ключ. У `DataSet` покажчиків немає, зате є дзеркальна пастка: `DataRow` після `Delete()` стає недоторканним, і звертання до колонки кине виняток — тому мітку перевіряють перед читанням.

Друга: обидва варіанти рахують останню частку не як третину, а як залишок. Округли кожну частку окремо — і сума часток розійдеться з виторгом.

**Контракт 17: табличний процесор, виторг 1000.00, підписано 2026-03-10.**

```
виторг       = 100000 копійок
розклад      = "spreadsheet" → зсуви 0, 60, 90 днів, тобто 3 частки

base         = floorDiv(100000, 3)   = 33333
rest         = 100000 − 33333 · 3    = 1

частка 1     = 33333                 → 333.33   на 2026-03-10
частка 2     = 33333                 → 333.33   на 2026-05-09
частка 3     = 33333 + 1 = 33334     → 333.34   на 2026-06-08
сума часток  = 100000 = виторг ✔

визнано на 2026-05-31 = 33333 + 33333 = 66666 → 666.66
```

## Скільки це коштує

Тепер видно, чому пошук за ключем у цьому патерні — не деталь.

Візьмімо ніч кінця кварталу: перерахувати визнання за всіма контрактами. Це виклик `calculateRecognitions` на кожен контракт, а всередині кожного — знайти контракт, знайти товар, прибрати старі визнання.

```
n = 50 000    контрактів
m = 150 000   визнань (у середньому k = 3 на контракт)
p = 200       товарів

без індексів   n · (n + p + m) = 50 000 · (50 000 + 200 + 150 000)
                               ≈ 1.0 · 10¹⁰ звірянь
з індексами    n · (1 + 1 + k) = 50 000 · 5
                               = 2.5 · 10⁵ звірянь
різниця        ≈ 40 000 разів

на машині, що робить 10⁸ простих звірянь за секунду:
   ≈ 100 с   проти   ≈ 2.5 мс
```

Ця різниця не в тому, що перебір «повільніший». Вона в порядку зростання: без індексу вартість нічного перерахунку росте як квадрат кількості контрактів, тож база, що виросла вдесятеро, дає стократ довшу ніч. З індексом вартість лінійна, і зростання бази підіймає час рівно настільки, наскільки зросла база.

Хеш-індекс дає доступ за сталий час у середньому: ключ перетворюють на число, число — на номер комірки, а збіги комірок розв'язують на місці — про це докладно в статті про [хеш-таблицю](book:algorithms/hash-table), там-таки й про те, коли «в середньому» перестає бути правдою. У `DataSet` індекс за первинним ключем упорядкований, а не хешований, тому `Rows.Find` — це двійковий пошук, O(log n): для п'ятдесяти тисяч рядків близько шістнадцяти звірянь замість одного. Різниця з хешем тут не принципова; принципова різниця — з n.

> 🔧 **Навіщо це.** Коли доводиться читати чужий модуль таблиці, індекс — перше, що варто шукати, і найчастіша знахідка — його відсутність. Прикмета проста: метод бере ключ аргументом, а всередині має цикл по всій таблиці — `std::find_if`, `Rows.Cast<DataRow>().Where(...)`, `table.Select("id = " + id)`. На тестових двохстах рядках усе це літає, і саме тому доживає до бойових даних. Друга прикмета — той самий цикл, схований за зручним фасадом: `DataTable.Compute("sum(amount)", "contract_id = 17")` виглядає як запит до бази, а насправді читає кожен рядок таблиці. Індексом його не назвеш; індексом стане `DataView` із заданим `Sort`, і саме тому в коді вище підсумок іде через `FindRows`.

## Одним рухом назад у базу

Модуль правив рядки в пам'яті й до бази не звертався жодного разу. Тепер накопичені зміни треба надіслати — і саме тут набір рядків віддає те, заради чого його тримали: він **уже знає**, що змінилося. Обхід міток дає список правок, і цей список їде однією транзакцією. Готовий [облік змін одиницею роботи](book:programming/unit-of-work) — механізм, що збирає всі правки за операцію й записує їх разом, — тут не треба писати: він у структурі даних.

![Накопичені зміни й межа транзакції. Ліворуч рамка НАБІР РЯДКІВ зі списком рядок 17 без змін, рядок 18 змінено, рядок 19 додано, рядок 20 вилучено й підписом мітка — на кожному рядку; від неї стрілка вправо в синю пунктирну рамку з написом ОДНА ТРАНЗАКЦІЯ, усередині якої дві коробки: changes() з підписом тільки помічені рядки, решта не турбує базу, і ШЛЮЗ ТАБЛИЦІ з підписами INSERT, UPDATE, DELETE та тут і тільки тут — SQL. Знизу рамки лінія розгалужується на дві стрілки. Ліворуч зелена коробка commit вдався: accept() — мітки скинуто, вилучені рядки викинуто, набір і база кажуть те саме. Праворуч червона коробка commit упав, відкат: база незмінна, мітки лишилися, можна повторити або reject() до вихідних значень. Унизу широка червона рамка з попередженням: DataAdapter.Update сам кличе AcceptChanges на кожному вдалому рядку, тож після відкату транзакції набір уже вважає себе збереженим; лікує AcceptChangesDuringUpdate дорівнює false](img/change-boundary.svg)

*Мітки — це не дані, а обіцянка базі. Поки транзакція не підтверджена, вони мусять лишатися на місці: скинути їх раніше означає стерти єдиний запис про те, що ще не збережено.*

:::tabs
```cpp
// Шлюз таблиці: ТУТ і тільки тут живе SQL. Модуль про базу не знає нічого.
template <class Row>
struct Gateway {
    virtual void insert(const Row&) = 0;
    virtual void update(const Row&) = 0;
    virtual void erase(Id) = 0;
    virtual ~Gateway() = default;
};

template <class Row>
void flush(const Table<Row>& t, Gateway<Row>& gw) {
    for (const auto& ch : t.changes())               // тільки помічені рядки
        switch (ch.state) {
            case RowState::Added:     gw.insert(*ch.row);      break;
            case RowState::Modified:  gw.update(*ch.row);      break;
            case RowState::Deleted:   gw.erase(ch.row->id);    break;
            case RowState::Unchanged: break;                   // сюди не потрапляє
        }
}

// Db і Transaction — тонкі обгортки застосунку над з'єднанням із базою.
// Межа транзакції — ТУТ, зовні модулів: модуль не знає, чи він
// єдиний учасник операції, тож і відкривати транзакцію не йому.
void save(SalesData& d, Db& db, Gateway<Contract>& gc, Gateway<Recognition>& gr) {
    Transaction tx(db);          // деструктор відкотить, якщо до commit не дійшло
    flush(d.contracts, gc);
    flush(d.recognitions, gr);
    tx.commit();

    d.contracts.accept();        // мітки знімаємо ЛИШЕ після успішного commit
    d.recognitions.accept();     // не дійшли сюди — набір лишився з мітками
}
```
```cs
using System.Data;
using Microsoft.Data.SqlClient;

public static void Save(DataSet data, SqlConnection cn,
                        SqlDataAdapter contracts, SqlDataAdapter recognitions)
{
    using SqlTransaction tx = cn.BeginTransaction();   // Dispose без Commit = відкат
    Enlist(contracts, tx);
    Enlist(recognitions, tx);

    // Update за замовчуванням сам кличе AcceptChanges на кожному вдалому рядку.
    // Тоді відкат транзакції прибере зміни в базі — але не в наборі, і той збреше.
    contracts.AcceptChangesDuringUpdate = false;
    recognitions.AcceptChangesDuringUpdate = false;

    contracts.Update(data, "contracts");               // поїдуть лише помічені рядки
    recognitions.Update(data, "recognitions");

    tx.Commit();
    data.AcceptChanges();                              // мітки скидаємо ЛИШЕ після commit
}

private static void Enlist(SqlDataAdapter a, SqlTransaction tx)
{
    foreach (SqlCommand cmd in new[] { a.InsertCommand, a.UpdateCommand, a.DeleteCommand })
        if (cmd != null) cmd.Transaction = tx;
}
```
:::

Порядок тут не декоративний. `accept()` каже наборові: усе, що ти пам'ятав як незбережене, тепер у базі — мітки геть, вихідні значення геть, вилучені рядки з пам'яті геть. Зробити це до підтвердження [транзакції](book:programming/transactions-acid) — операції, яка або застосовується цілком, або не застосовується зовсім — означає викинути єдиний слід того, що ще не збережено. Після невдалого запису набір із мітками ще можна врятувати: повторити спробу або відкотити правки до вихідних значень через `reject()`. Набір без міток не рятується ніяк — він переконаний, що збігається з базою.

## Пастки

**Перебір замість індексу.** Мова не про повільність, а про порядок зростання: без індексу вартість масової операції квадратична, і вдесятеро більші дані дають стократну ніч. Прикмети описано вище; ліки — індекс за первинним ключем і вторинний індекс за кожним чужим ключем, яким справді питають.

**Округлення часток і залишок.** Пастка складається з двох. Перша — тип: число 0.01 не має точного двійкового зображення, тож у типі з рухомою комою сума ста таких часток не дає рівно одиниці; гроші тримають або в цілих копійках, або в десятковому типі на кшталт `decimal` — [фіксована кома](book:programming/fixed-point) саме про це. Друга — сам поділ: округлення кожної частки окремо ламає рівність «сума часток = ціле». Обидва варіанти вище рахують частки так, щоб рівність трималася за побудовою, і цю властивість варто закріпити тестом: для всіх сум від 1 до 100000 копійок і всіх n від 1 до 12 сума часток дорівнює цілому. Куди саме йде залишок — у першу частку, в останню чи по копійці на кожну — питання домовленості з бухгалтерією, і його треба зафіксувати явно, бо мовчазний вибір потім розходиться між звітами.

**Межа транзакції в чужих руках.** Модуль не знає, чи він єдиний учасник операції: сьогодні `calculateRecognitions` кличуть саму, завтра — разом зі зміною контракту й записом у журнал, і всі три мусять або пройти, або не пройти. Тому транзакцію відкриває той, хто знає межі операції, — зазвичай [сервісний шар](book:programming/service-layer). Модуль, що всередині відкриває власну транзакцію, робить спільну операцію неатомарною, і це непомітно рівно доти, доки нічого не падає. Друга частина цієї пастки — скидання міток раніше за підтвердження, і в .NET воно ввімкнене за замовчуванням: `DataAdapter.Update` кличе `AcceptChanges` на кожному вдалому рядку, тож після відкату транзакції база чиста, а набір уже вважає себе збереженим; вимикається властивістю `AcceptChangesDuringUpdate = false`. І третя: набір лежить відірваним від бази хвилини або години, і за цей час рядок міг змінити хтось інший — потрібна перевірка під час запису, [оптимістичне блокування](book:programming/optimistic-locking), яке звіряє версію рядка просто в умові `UPDATE` і відмовляє, якщо версії роз'їхалися.

**Розповзання `if` за колонкою типу.** Тип рядка тут — значення в колонці, а значення не вміє вибирати метод; вибір мусить зробити код. Поки такий вибір один, це чесна гілка. Небезпека в іншому: коли гілки за тим самим `kind` заводяться в кожному методі модуля, новий різновид товару означає обхід їх усіх, і забутий метод дає тиху помилку в звіті. Таблиця розкладу вище саме проти цього: додати базі даних власний розклад — це один рядок `{"database", {0, 30, 60}}`, а не ще одна гілка в кожному методі. Але межа в цього ходу є, і вона конкретна: таблиця працює, поки різновиди відрізняються **даними** — числами, зсувами, ставками. Щойно вони починають відрізнятися **обчисленням** — один тип рахує від суми, другий від суми без податку, третій дивиться на дату закриття, — таблиця перетворюється на реєстр функцій, тобто на [стратегію](book:programming/strategy), де кожен варіант поведінки винесено в окремий об'єкт зі спільним інтерфейсом. А коли й у стратегій починають бути власні дані та інваріанти, чесніше визнати, що рядки поводяться по-різному, і платити за [предметну модель](book:programming/domain-model).

**SQL і правила в одному класі.** Найдорожча з пасток, бо вона зростає повільно. Модуль, якому дозволено сходити в базу, рано чи пізно робить це всередині правила — а правило викликають у циклі по рядках, і замість одного запиту на набір виходить запит на кожен рядок. Це та сама лавина дрібних звертань, від якої модуль таблиці мав рятувати. Друга ціна — випробувати правило тепер можна тільки з базою. Тому доступ до бази лишається за окремою межею — це [шлюз таблиці даних](book:programming/table-data-gateway), об'єкт на таблицю, у якому немає жодного предметного правила, тільки її SQL. Злити ці дві ролі в один клас можна свідомо, і воно працює; біда починається тоді, коли злиття виходить ненавмисно — коли в клас, названий шлюзом, правила натекли по одному.
