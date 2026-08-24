# ⚙️ Колонковий набір рядків з обліком змін: працездатний код

Тут набір рядків доведено від оголошення типів до `COMMIT`: колонка — типізованим масивом, `NULL` — бітом у масці, рядок — спільним індексом у всіх масивах, а кожна правка лишає по собі тінь, з якої потім народжується `UPDATE` з умовою по початкових значеннях. Мова — C++, бо вся суть задачі в тому, ЯК саме байти лежать у пам'яті: середовище з прихованими заголовками об'єктів заховало б рівно те, що ми міряємо.

## Задача

Працюємо з однією таблицею, решта — те саме на більшій кількості колонок:

```sql
CREATE TABLE orders (
  id           bigserial   PRIMARY KEY,
  customer_id  text        NOT NULL,
  total_cents  bigint      NOT NULL,   -- гроші цілим числом копійок, не дробовим
  status       text        NOT NULL,
  updated_at   timestamptz NOT NULL
);
```

Потрібен клас, який:

1. **заповнюється** з результату запиту й одразу відпускає з'єднання;
2. дає **прочитати** комірку за номером колонки й за її іменем, не сплутавши `NULL` із нулем;
3. приймає **правки**, пам'ятаючи для кожної зачепленої комірки початкове значення;
4. знає **стан** кожного рядка: незмінений, змінений, доданий, вилучений;
5. **породжує** параметризовані `INSERT`/`UPDATE`/`DELETE` й розпізнає, що його випередили;
6. робить усе це так, щоб двісті тисяч рядків важили одиниці мегабайтів, а не десятки.

Останній пункт визначає все інше, тож із нього й почнемо.

## Колонка — масив, рядок — індекс

Наївний набір тримає рядок структурою, а комірку — окремим значенням із власним типом. У C++ це означає `std::vector<std::vector<std::variant<…>>>`: кожна комірка несе тег типу й вирівнювання під найширший варіант, а кожен рядок — ще й заголовок свого вектора. На п'ять колонок службових байтів виходить у кілька разів більше, ніж корисних.

Колонковий розклад прибирає службові байти цілком: тип відомий на всю колонку, тож тег не потрібен жодній комірці. Одна колонка — один щільний масив свого типу. Рядок при цьому перестає бути об'єктом і стає **числом**: рядок 3 — це третя комірка в кожному з масивів.

Лишається `NULL`. Обгортати кожну комірку в `std::optional<int64_t>` спокусливо, але дорого: до восьми байтів числа `optional` додає байт прапорця, а вирівнювання під восьмибайтове число доганяє розмір до **шістнадцяти**. Тобто вісім зайвих байтів на комірку рівно заради одного біта відомостей. Замість цього беремо окрему бітову маску: біт `j` каже, чи є значення в рядку `j`. Службова ціна падає з восьми байтів до 1/8 байта — у шістдесят чотири рази.

```cpp
#include <cstdint>
#include <functional>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <variant>
#include <vector>

enum class Type : uint8_t { Int64, Text };

struct Column {
    std::string              name;
    Type                     type;
    bool                     generated = false;  // ключ, який видає база
    bool                     key_ref   = false;  // ключ або посилання на ключ
    std::vector<int64_t>     i64;                // живий, якщо type == Int64
    std::vector<std::string> txt;                // живий, якщо type == Text
    std::vector<uint64_t>    valid;              // біт j: 1 — значення є, 0 — NULL
};
// колонка id у нашій таблиці несе ОБИДВА прапорці: її видає база (generated)
// і її значення проходить через книгу ключів (key_ref)

inline bool bit(const std::vector<uint64_t>& mask, size_t j) {
    return (mask[j >> 6] >> (j & 63)) & 1ull;
}

inline void set_bit(std::vector<uint64_t>& mask, size_t j, bool on) {
    uint64_t&      word = mask[j >> 6];
    const uint64_t b    = 1ull << (j & 63);
    word = on ? (word | b) : (word & ~b);
}
```

Два порожні вектори в кожній колонці — це 24 байти на **колонку**, а не на рядок, і за цю дрібницю ми купуємо код без жодного `std::visit`. Коли типів стане більше десятка, ця розкіш скінчиться й доведеться переходити на `std::variant` векторів або на власну арену байтів; на двох типах вона себе виправдовує.

Зверніть увагу на `j >> 6` і `j & 63`. Швидкості вони не додають: `j` беззнакове, тож `j / 64` і `j % 64` компілятор перепише в той самий зсув і ту саму маску сам. Вони стоять, щоб у коді було видно поділ індексу на дві частини — номер слова й номер біта всередині слова, — бо саме цей поділ і є всією конструкцією. Формати даних описують маску так само: [Apache Arrow](https://arrow.apache.org/docs/format/Columnar.html) кладе маску валідності 64-бітними словами, біт `1` означає «значення є», нумерація бітів у байті — від молодшого, а буфер рекомендують вирівнювати на 64 байти під ширину векторного регістра. Ми повторюємо ту саму домовленість, щоб набір можна було віддати назовні без перекладання.

![Схема того, що лежить у пам'яті колонкового набору. Угорі лінійка номерів рядків від нуля до семи. Нижче чотири блоки, у кожному ліворуч підпис із іменем і типом колонки, а праворуч смуга з восьми комірок значень і під нею смуга з восьми бітів: id int64 зі значеннями сорок один до сорок вісім і всіма бітами одиниця; customer_id text зі значеннями ACME, Borysfen, Cebra, Delta, Erid, Fenix, Grot, Hvylia і всіма бітами одиниця; total_cents int64, де третя комірка підсвічена рожевим зі знаком питання і її біт нуль, решта бітів одиниця; status text зі значеннями paid, review, paid, shipped, new, paid, paid, paid. Під ними смуга станів рядків: незмінений, змінений, незмінений, незмінений, незмінений, вилучений, незмінений, доданий. Праворуч три примітки зі стрілками до смуг: рядок це спільний індекс, рядок три стоїть третьою коміркою в кожному масиві; біт нуль означає комірку NULL, у масиві на цьому місці сміття і читати його не можна; вилучений рядок лишається на місці надгробком, інакше в базі не буде чого видаляти. Унизу два блоки поруч: ліворуч зелений, схема як дані, відображення імені в номер, id нуль, customer_id один, total_cents два, status три, виклик col від total_cents це один пошук у хеші і далі прямий доступ у масив; праворуч синій, початкові значення розріджено, лише правлені комірки, рядок один total_cents дорівнює 118000 і рядок один status дорівнює paid, тінь на весь набір подвоїла б пам'ять, у доданого рядка сім початкових значень немає взагалі. Найнижче примітка, що маска валідності це 64-бітні слова і на вісім рядків вистачає одного слова на колонку](img/record-set-in-memory.svg)

*Усе, що набір тримає в пам'яті: чотири щільні масиви, чотири бітові маски, один масив станів і розріджене сховище тіней. Рядок ніде не існує як об'єкт — він існує як число, спільне для всіх масивів.*

## Схема як дані й тіні як розріджене сховище

Схема — це самі описи колонок плюс відображення «ім'я → номер», побудоване раз при створенні набору. Тіні початкових значень — окрема мапа, і вона **розріджена**: у ній лежать лише ті комірки, яких справді торкнулися.

```cpp
enum class RowState : uint8_t {
    Unchanged,   // прочитаний і не чіпаний
    Modified,    // правлений; початкові значення лежать в orig_
    Added,       // доданий тут, у базі його ще немає
    Deleted,     // позначений вилученим, лишається на місці надгробком
    Discarded    // доданий і тут-таки вилучений — у базу не піде нічого
};

using Value = std::variant<std::monostate, int64_t, std::string>;  // monostate — це NULL

struct SvHash {                        // щоб пошук за string_view не створював std::string
    using is_transparent = void;
    size_t operator()(std::string_view s) const noexcept {
        return std::hash<std::string_view>{}(s);
    }
};

// рядок і колонка, склеєні в один ключ: до 65 536 колонок і до 2⁴⁸ рядків
inline uint64_t cell_key(size_t row, size_t colno) {
    return (static_cast<uint64_t>(row) << 16) | static_cast<uint64_t>(colno);
}

struct KeyBook {                       // тимчасовий ключ → справжній, виданий базою
    int64_t next_temp = -1;
    std::unordered_map<int64_t, int64_t> real;

    int64_t issue() { return next_temp--; }

    int64_t resolve(int64_t v) const {
        if (v >= 0) return v;                       // справжній ключ, нічого робити
        const auto it = real.find(v);
        if (it == real.end())
            throw std::logic_error("батьківський рядок ще не вставлено");
        return it->second;
    }
};

struct Statement;                      // оголошення наперед: тіла — далі за текстом
struct RowSource;
struct Op;
enum class Phase : uint8_t { Insert, Update, Delete };

class RecordSet {
public:
    RecordSet(std::string table, std::vector<Column> cols,
              std::vector<std::string> key, KeyBook& keys)
        : table_(std::move(table)), cols_(std::move(cols)),
          key_(std::move(key)), keys_(&keys) {
        for (size_t c = 0; c < cols_.size(); ++c) index_.emplace(cols_[c].name, c);
    }

    size_t rows() const noexcept { return nrows_; }

    size_t col(std::string_view name) const {
        const auto it = index_.find(name);
        if (it == index_.end())
            throw std::out_of_range("немає колонки " + std::string(name));
        return it->second;
    }

    void   reserve(size_t n);
    void   load(RowSource& src, size_t expect);

    bool                            is_null (size_t r, size_t c) const;
    std::optional<int64_t>          get_int (size_t r, size_t c) const;
    std::optional<std::string_view> get_text(size_t r, size_t c) const;

    void   set_int (size_t r, size_t c, std::optional<int64_t> v);
    void   set_text(size_t r, size_t c, std::optional<std::string> v);
    size_t append_row();
    void   erase_row(size_t r);

    void      collect(std::vector<Op>& plan, Phase phase);
    Statement make(size_t r, Phase phase) const;
    void      note_key(size_t r, const std::vector<Value>& returned);
    void      accept();

private:
    size_t      grow_one();
    Value       value_at(size_t r, size_t c) const;
    Value       param_at(size_t r, size_t c) const;
    Value       original_at(size_t r, size_t c) const;
    void        remember(size_t r, size_t c);
    std::string where_original(size_t r, std::vector<Value>& params) const;
    Statement   make_insert(size_t r) const;
    Statement   make_update(size_t r) const;
    Statement   make_delete(size_t r) const;
    void        compact();

    std::string                                                      table_;
    std::vector<Column>                                              cols_;
    std::vector<std::string>                                         key_;
    KeyBook*                                                         keys_;
    std::vector<RowState>                                            state_;
    std::unordered_map<std::string, size_t, SvHash, std::equal_to<>> index_;
    std::unordered_map<uint64_t, Value>                              orig_;
    size_t                                                           nrows_ = 0;
};
```

`is_transparent` у хешері — не прикраса. Без нього `index_.find("total_cents")` створює тимчасовий `std::string`, а для імені, довшого за п'ятнадцять символів, це ще й виділення пам'яті в купі. У циклі по двохстах тисячах рядків один недоданий рядок коду перетворює безкоштовний пошук на двісті тисяч виділень. Різнорідний пошук у неврегульованих контейнерах з'явився в C++20 — саме цей стандарт тут і мається на увазі.

Розрідженість тіней варта окремого рахунку. Повна тінь — це другий комплект масивів, тобто рівно подвоєна пам'ять, і платити її довелося б завжди, навіть коли користувач нічого не правив. Розріджена мапа коштує близько п'ятдесяти байтів на **змінену комірку**: вузол хеш-таблиці, ключ, варіант зі значенням. Діалоговий сеанс правки міняє десятки комірок; двісті тисяч рядків по п'ять колонок — це мільйон комірок. Різниця між «плюс кілька кілобайтів» і «плюс вісімнадцять мегабайтів» вирішує питання остаточно.

> 🔧 **Навіщо це.** Тінь потрібна не для «скасувати правку» — вона потрібна, щоб через десять хвилин після читання поставити базі питання «рядок ще такий, яким я його бачив?». Умова `WHERE` по початкових значеннях — це [оптимістичне блокування](book:programming/optimistic-locking), тобто спосіб не тримати блокування взагалі, а просто перевірити на записі, чи ніхто не втрутився; набір отримує його задарма, бо початкові значення в нього вже є.

## Заповнення: розібрати один раз

Драйвер віддає рядки по одному. Наше завдання — прогнати їх усі, розкласти по колонках і відпустити з'єднання.

```cpp
struct RowSource {                     // те, що вміє курсор драйвера
    virtual bool        next()                 = 0;
    virtual bool        is_null(size_t c) const = 0;
    virtual int64_t     as_int(size_t c) const = 0;
    virtual std::string as_text(size_t c) const = 0;
    virtual ~RowSource() = default;
};

void RecordSet::reserve(size_t n) {
    for (Column& k : cols_) {
        if (k.type == Type::Int64) k.i64.reserve(n); else k.txt.reserve(n);
        k.valid.reserve((n + 63) / 64);
    }
    state_.reserve(n);
}

size_t RecordSet::grow_one() {         // місце під новий рядок у ВСІХ масивах
    const size_t r = nrows_;
    for (Column& k : cols_) {
        if (k.type == Type::Int64) k.i64.emplace_back(); else k.txt.emplace_back();
        if ((r >> 6) >= k.valid.size()) k.valid.push_back(0);
        set_bit(k.valid, r, false);    // поки не записали — комірка порожня
    }
    state_.push_back(RowState::Unchanged);
    ++nrows_;
    return r;
}

void RecordSet::load(RowSource& src, size_t expect) {
    reserve(expect);
    while (src.next()) {
        const size_t r = grow_one();
        for (size_t c = 0; c < cols_.size(); ++c) {
            if (src.is_null(c)) continue;              // біт уже нульовий
            Column& k = cols_[c];
            if (k.type == Type::Int64) k.i64[r] = src.as_int(c);
            else                       k.txt[r] = src.as_text(c);
            set_bit(k.valid, r, true);
        }
    }
}
```

`reserve` тут не мікрооптимізація. Без нього п'ять масивів ростуть подвоєнням незалежно один від одного, і кожне подвоєння текстової колонки — це переміщення двохсот тисяч `std::string`. Кількість рядків зазвичай відома з `LIMIT` або з попереднього `COUNT`; коли невідома — кращий за ніщо навіть грубий здогад.

Розбір байтів у числа стається саме тут, один раз на комірку. Це і є головна відмінність набору від буфера сирих байтів: набір існує, щоб дані читали багато разів, тож розбір, віднесений на момент читання, помножився б на кількість читань.

## Читання: два шляхи й пастка з нулем

```cpp
bool RecordSet::is_null(size_t r, size_t c) const { return !bit(cols_[c].valid, r); }

std::optional<int64_t> RecordSet::get_int(size_t r, size_t c) const {
    const Column& k = cols_[c];
    if (!bit(k.valid, r)) return std::nullopt;
    return k.i64[r];
}

std::optional<std::string_view> RecordSet::get_text(size_t r, size_t c) const {
    const Column& k = cols_[c];
    if (!bit(k.valid, r)) return std::nullopt;
    return std::string_view(k.txt[r]);
}
```

Доступ за номером — перевірка біта й читання з масиву. Доступ за іменем — те саме плюс один пошук у хеші; ім'я стійкіше до перестановки колонок у `SELECT`, номер швидший у циклі. Практичний компроміс очевидний: номер беруть **перед** циклом, а всередині ходять уже за номером.

```cpp
const size_t c_total  = rs.col("total_cents");
const size_t c_status = rs.col("status");

int64_t sum = 0;
for (size_t r = 0; r < rs.rows(); ++r)
    if (const auto v = rs.get_int(r, c_total)) sum += *v;
```

Тепер про повернений тип. Спокуса написати `int64_t get_int(...)` й повертати нуль для порожньої комірки виглядає нешкідливо рівно доти, доки колонка не називається `discount_cents`. Знижка «не задана» й знижка «нуль» — різні речі, і `sum += get_int(r, c)`, яке мовчки додає нуль, дає ту саму суму, а от зворотний запис перетворює відсутню знижку на знижку нуль, і в базі з'являється те, чого людина не вводила. Тому повертати треба `std::optional`, і код, який хоче число, зобов'язаний сказати, що робити з порожнечею.

`get_text` повертає `std::string_view` у пам'ять колонки — і це друга пастка, суто C++. Додавання рядка кличе `push_back` у текстовий масив, той може перевиділити буфер, і всі раніше отримані `string_view` стають висячими. Правило коротке: `string_view` із набору живе до найближчої зміни розміру набору. Хочете пережити її — копіюйте в `std::string`.

## Правка: тінь лягає на першу зміну

```cpp
Value RecordSet::value_at(size_t r, size_t c) const {
    const Column& k = cols_[c];
    if (!bit(k.valid, r)) return std::monostate{};
    return (k.type == Type::Int64) ? Value{k.i64[r]} : Value{k.txt[r]};
}

void RecordSet::remember(size_t r, size_t c) {
    if (state_[r] == RowState::Added) return;      // початкових значень у нього немає
    const uint64_t key = cell_key(r, c);
    if (orig_.find(key) != orig_.end()) return;    // тінь кладемо лише на ПЕРШУ правку
    orig_.emplace(key, value_at(r, c));
}

void RecordSet::set_int(size_t r, size_t c, std::optional<int64_t> v) {
    remember(r, c);
    Column& k = cols_[c];
    if (v) k.i64[r] = *v;
    set_bit(k.valid, r, v.has_value());
    if (state_[r] == RowState::Unchanged) state_[r] = RowState::Modified;
}

void RecordSet::set_text(size_t r, size_t c, std::optional<std::string> v) {
    remember(r, c);
    Column& k = cols_[c];
    if (v) k.txt[r] = std::move(*v);
    set_bit(k.valid, r, v.has_value());
    if (state_[r] == RowState::Unchanged) state_[r] = RowState::Modified;
}

size_t RecordSet::append_row() {
    const size_t r = grow_one();
    state_[r] = RowState::Added;
    for (Column& k : cols_)
        if (k.generated && k.type == Type::Int64) {
            k.i64[r] = keys_->issue();             // від'ємний тимчасовий ключ
            set_bit(k.valid, r, true);
        }
    return r;
}

void RecordSet::erase_row(size_t r) {
    state_[r] = (state_[r] == RowState::Added) ? RowState::Discarded
                                               : RowState::Deleted;
}
```

Три рішення в цих тридцяти рядках варті слів.

**Тінь кладемо лише на першу правку.** Якщо користувач змінив статус тричі, у базу поїде остання версія, а порівнювати треба з тим, що прочитали з бази, — тобто з найпершою. Перевірка `orig_.find(key) != orig_.end()` і є цим правилом. Побічний ефект чесний і збігається з поведінкою класичних реалізацій: правка «туди й назад» лишається правкою, бо тінь уже лягла, а порівнювати значення на рівність набір не пробує.

**Вилучений рядок лишається на місці.** Це той самий [надгробок](book:programming/soft-delete-tombstones), що й у базах: позначка «цього більше немає» замість фізичного прибирання. Стерти рядок із масивів одразу означало б зсунути всі п'ять масивів і зіпсувати кожен номер рядка, який хтось десь запам'ятав, — включно з ключами в `orig_`. А ще з набору зникло б те, що треба видалити в базі, разом із початковими значеннями для умови.

**Доданий і тут-таки вилучений — окремий стан.** Рядка `Discarded` у базі ніколи не було, тож надсилати про нього нічого: ані `INSERT`, ані `DELETE`. Без п'ятого стану цей випадок або породив би `DELETE` неіснуючого рядка, або лишився б `Added` і вставив би те, що користувач передумав вставляти.

## Породження операторів

Кожен стан перетворюється на свій оператор. Значення в текст запиту не потрапляють: місце під них лишає позначка, а самі вони їдуть окремим списком — це [підготовлений вираз](book:programming/prepared-statements), і саме він робить неможливим перетворення даних на команду. Позначку кожен драйвер пише по-своєму (`$1` у PostgreSQL, `?` у SQLite та MySQL); беремо форму PostgreSQL.

```cpp
struct Statement {
    std::string        sql;
    std::vector<Value> params;
    size_t             returns_key_into = SIZE_MAX;   // рядок, чий ключ видасть база
};

Value RecordSet::param_at(size_t r, size_t c) const {
    Value v = value_at(r, c);
    if (cols_[c].key_ref)
        if (const int64_t* n = std::get_if<int64_t>(&v))
            v = keys_->resolve(*n);                   // тимчасовий ключ → справжній
    return v;
}

Value RecordSet::original_at(size_t r, size_t c) const {
    const auto it = orig_.find(cell_key(r, c));
    return (it == orig_.end()) ? value_at(r, c) : it->second;   // не правили — поточне і є початковим
}

std::string RecordSet::where_original(size_t r, std::vector<Value>& params) const {
    std::string w;
    for (size_t c = 0; c < cols_.size(); ++c) {
        if (!w.empty()) w += " AND ";
        const Value ov = original_at(r, c);
        if (std::holds_alternative<std::monostate>(ov)) {
            w += cols_[c].name + " IS NULL";          // «= NULL» не буває істинним НІКОЛИ
        } else {
            params.push_back(ov);
            w += cols_[c].name + " = $" + std::to_string(params.size());
        }
    }
    return w;
}

Statement RecordSet::make_update(size_t r) const {
    Statement st;
    std::string sets;
    for (size_t c = 0; c < cols_.size(); ++c) {
        if (orig_.find(cell_key(r, c)) == orig_.end()) continue;  // цю колонку не чіпали
        if (!sets.empty()) sets += ", ";
        st.params.push_back(param_at(r, c));                      // ПОТОЧНЕ значення
        sets += cols_[c].name + " = $" + std::to_string(st.params.size());
    }
    st.sql = "UPDATE " + table_ + " SET " + sets +
             " WHERE " + where_original(r, st.params);
    return st;
}

Statement RecordSet::make_delete(size_t r) const {
    Statement st;
    st.sql = "DELETE FROM " + table_ + " WHERE " + where_original(r, st.params);
    return st;
}

Statement RecordSet::make_insert(size_t r) const {
    Statement st;
    std::string names, marks;
    for (size_t c = 0; c < cols_.size(); ++c) {
        if (cols_[c].generated) continue;                         // ключ видасть база
        if (!names.empty()) { names += ", "; marks += ", "; }
        st.params.push_back(param_at(r, c));
        names += cols_[c].name;
        marks += "$" + std::to_string(st.params.size());
    }
    st.sql = "INSERT INTO " + table_ + " (" + names + ") VALUES (" + marks + ")";
    for (size_t i = 0; i < key_.size(); ++i)
        st.sql += (i ? ", " : " RETURNING ") + key_[i];
    st.returns_key_into = r;
    return st;
}
```

Порядок додавання параметрів і нумерація позначок зчеплені навмисно: номер рахується як `params.size()` **після** `push_back`, тож розсинхронізуватися вони не можуть у принципі. Це дрібний, але надійний прийом — у наборах, де текст і список параметрів збирають окремими проходами, зсув на одиницю є вічним джерелом помилок.

Тепер найтонше місце всієї вставки — гілка `IS NULL`. Написати `total_cents = $3` і підставити туди порожнє значення виглядає природно, а працює **ніколи**: у SQL порівняння з `NULL` дає не «хибно», а третє значення — «невідомо», і рядок за такою умовою не знайдеться навіть тоді, коли він насправді той самий. Умова мовчки не збігається, база повертає нуль змінених рядків, набір рапортує конфлікт, якого немає, і користувач бачить «вас випередили» на порожньому місці. Тому порожню комірку в умову вписують окремою формою `IS NULL`, а не параметром. [Тризначна логіка SQL](book:programming/sql-null-three-valued) — не примха стандарту, а прямий наслідок того, що `NULL` означає «значення невідоме», і два невідомих не зобов'язані бути рівними.

Умова по **всіх** початкових значеннях — найсуворіший варіант: конфліктом вважається будь-яка зміна рядка, хоч би й в іншій колонці. Він же й найдорожчий: у `WHERE` потрапляють усі текстові колонки, і база порівнює їх усі. Дешевша заміна відома — колонка версії: лічильник або мітка часу, яку база сама піднімає на кожному записі. Тоді в умові лишається ключ і версія, а `updated_at` у нашій таблиці саме для цього й стоїть. Вибір між двома формами — це вибір між «жодних припущень про схему» і «двома порівняннями замість п'яти».

## Порядок і межа підтвердження

Оператори не можна зліпити наперед і потім виконати списком. Дочірній рядок посилається на ключ батька, а ключ батька видає база — у мить його `INSERT`. Тому план містить не готові оператори, а **наміри**, і текст із параметрами будується безпосередньо перед виконанням, коли щойно виданий ключ уже лежить у книзі ключів.

```cpp
struct Op { RecordSet* set; size_t row; Phase phase; };

void RecordSet::collect(std::vector<Op>& plan, Phase phase) {
    for (size_t r = 0; r < nrows_; ++r) {
        const bool take =
            (state_[r] == RowState::Added    && phase == Phase::Insert) ||
            (state_[r] == RowState::Modified && phase == Phase::Update) ||
            (state_[r] == RowState::Deleted  && phase == Phase::Delete);
        if (take) plan.push_back(Op{this, r, phase});
        // Unchanged і Discarded не дають нічого в жодній фазі
    }
}

Statement RecordSet::make(size_t r, Phase phase) const {
    switch (phase) {
        case Phase::Insert: return make_insert(r);
        case Phase::Update: return make_update(r);
        default:            return make_delete(r);
    }
}

void RecordSet::note_key(size_t r, const std::vector<Value>& returned) {
    for (size_t i = 0; i < key_.size() && i < returned.size(); ++i) {
        const size_t c = col(key_[i]);
        const int64_t* issued = std::get_if<int64_t>(&returned[i]);
        if (issued && cols_[c].type == Type::Int64)
            keys_->real[cols_[c].i64[r]] = *issued;  // тимчасовий ключ рядка → справжній
    }
}
```

`note_key` навмисно **не** вписує справжній ключ у сам рядок, а лише реєструє відповідність у книзі. Доки транзакція не підтверджена, тимчасовий ключ у наборі лишається чинним, і відкат зводиться до одного `keys_->real.clear()`. Якби ми одразу підмінили значення в колонці, після відкату набір містив би ключі рядків, яких у базі немає, а відновити з них тимчасові було б уже нічим.

```cpp
struct Result { int64_t affected = 0; std::vector<Value> returned; };

struct Db {
    virtual void   begin()    = 0;
    virtual void   commit()   = 0;
    virtual void   rollback() = 0;
    virtual Result execute(const std::string& sql, const std::vector<Value>& params) = 0;
    virtual ~Db() = default;
};

struct Conflict : std::runtime_error {
    Conflict(const std::string& sql, int64_t affected)
        : std::runtime_error("змінено рядків: " + std::to_string(affected) + "; " + sql) {}
};

// sets подано в порядку залежності: батьки раніше за дітей
void apply_all(Db& db, KeyBook& keys, const std::vector<RecordSet*>& sets) {
    std::vector<Op> plan;
    for (RecordSet* rs : sets)  rs->collect(plan, Phase::Insert);   // батьки → діти
    for (RecordSet* rs : sets)  rs->collect(plan, Phase::Update);
    for (auto it = sets.rbegin(); it != sets.rend(); ++it)          // діти → батьки
        (*it)->collect(plan, Phase::Delete);

    db.begin();
    try {
        for (const Op& op : plan) {
            const Statement st = op.set->make(op.row, op.phase);    // будуємо ТУТ, не раніше
            const Result res = db.execute(st.sql, st.params);
            if (res.affected != 1)
                throw Conflict(st.sql, res.affected);               // 0 — нас випередили
            if (st.returns_key_into != SIZE_MAX)
                op.set->note_key(st.returns_key_into, res.returned);
        }
        db.commit();
    } catch (...) {
        db.rollback();
        keys.real.clear();          // видані ключі більше нічого не означають
        throw;                      // стани рядків НЕ чіпаємо: правки лишаються в наборі
    }
    for (RecordSet* rs : sets) rs->accept();   // і лише тепер, після успішного COMMIT
}
```

Три фази замість одного проходу — це і є розв'язок задачі порядку. Зовнішній ключ вимагає, щоб батько існував раніше за дитину й зникав пізніше за неї, тож вставки йдуть згори вниз по дереву зв'язків, а видалення — знизу вгору. Набір, який просто обходить власні рядки в порядку номерів, розіб'ється об обмеження цілісності на пів дорозі, і це не рідкісний випадок, а типовий: автоматичні генератори операторів у класичних реалізаціях будують команди для однієї таблиці, нічого не знаючи про зв'язки, і [документація Microsoft прямо попереджає](https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/generating-commands-with-commandbuilders), що через це запис може впасти на колонці, яка бере участь у зовнішньому ключі.

`res.affected != 1` — уся перевірка конфлікту. Нуль означає, що жоден рядок не задовольнив умову по початкових значеннях: між читанням і записом хтось інший змінив цей рядок або видалив його. Більше за одиницю означає, що ключ у наборі не унікальний — помилка вже не узгодження, а схеми, і мовчки її пропускати гірше, ніж упасти.

![Схема порядку запису й межі підтвердження. Ліворуч колонка з чотирьох блоків під заголовком порядок операторів: перший зелений, один INSERT, батьки раніше за дітей, customers переходить в orders і далі в order_lines, згенерований ключ батька повертає RETURNING і його вписують дітям перед їхньою вставкою; другий синій, два UPDATE, усередині одного рівня порядок довільний; третій рожевий, три DELETE, діти раніше за батьків, order_lines переходить в orders і далі в customers, інакше зовнішній ключ не дасть прибрати батька; четвертий сірий, набір що просто йде рядками згори вниз розіб'ється об обмеження цілісності на пів дорозі, порядок задає граф зв'язків а не номер рядка. Праворуч колонка під заголовком межа транзакції з чотирьох блоків, з'єднаних стрілками згори вниз: BEGIN; кожен оператор виконати й спитати скільки рядків він змінив, один означає далі, нуль означає нас випередили; COMMIT; accept, стани в незмінений, початкові значення стерти, надгробки прибрати. Нижче окремий рожевий блок, нуль змінених рядків веде до ROLLBACK і конфлікту, і вертикальна стрілка ліворуч від колонки веде до нього від блоку виконання. Унизу широкий рожевий блок на всю ширину: поміняти місцями два останні кроки і набір збреше сам собі, після відкату стани вже незмінений, початкові значення стерті, правки користувача зникли без сліду а в базі їх ніколи не було, приймати зміни можна лише після того як COMMIT повернувся успіхом](img/record-set-apply-order.svg)

*Порядок операторів диктує граф зовнішніх ключів, а не порядок рядків у наборі. Права колонка — межа, за якою набір має право повірити, що його правки вже в базі.*

## Прийняття змін і ущільнення

```cpp
void RecordSet::accept() {
    for (size_t r = 0; r < nrows_; ++r) {
        if (state_[r] != RowState::Added) continue;
        for (Column& k : cols_)                       // тимчасові ключі стають справжніми
            if (k.key_ref && k.type == Type::Int64 && bit(k.valid, r))
                k.i64[r] = keys_->resolve(k.i64[r]);
    }
    orig_.clear();
    for (RowState& s : state_)
        if (s != RowState::Deleted && s != RowState::Discarded) s = RowState::Unchanged;
    compact();
}

void RecordSet::compact() {
    std::vector<size_t> keep;
    keep.reserve(nrows_);
    for (size_t r = 0; r < nrows_; ++r)
        if (state_[r] != RowState::Deleted && state_[r] != RowState::Discarded)
            keep.push_back(r);
    if (keep.size() == nrows_) return;                // прибирати нема чого

    for (Column& k : cols_) {
        std::vector<uint64_t> nv((keep.size() + 63) / 64, 0);
        for (size_t i = 0; i < keep.size(); ++i) {
            const size_t src = keep[i];               // src >= i завжди, тож рух уперед безпечний
            if (k.type == Type::Int64) k.i64[i] = k.i64[src];
            else                       k.txt[i] = std::move(k.txt[src]);
            set_bit(nv, i, bit(k.valid, src));
        }
        if (k.type == Type::Int64) k.i64.resize(keep.size());
        else                       k.txt.resize(keep.size());
        k.valid.swap(nv);
    }
    for (size_t i = 0; i < keep.size(); ++i) state_[i] = state_[keep[i]];
    state_.resize(keep.size());
    nrows_ = keep.size();
}
```

`compact` живе всередині `accept` не випадково. Ущільнення пересуває рядки, а всі номери рядків, які хтось запам'ятав — ключі в `orig_`, індекси у в'ю над набором, посилання з таблиці на екрані, — після цього вказують на чужі дані. Викликати `compact` можна лише в мить, коли запам'ятовувати вже нічого: тіні щойно скинуто, транзакцію підтверджено, ніхто не тримає незакінченої правки. Ця залежність не виражається типами, тож `compact` тримають закритим, а зовнішній світ бачить лише `accept`.

Рух уперед у самому циклі безпечний з арифметичної причини: `keep[i] >= i` для всіх `i`, бо в `keep` індекси йдуть зростаючи й ми лише викидаємо частину. Тому запис у комірку `i` ніколи не затирає ще не прочитану комірку `keep[i]`.

## Що скільки коштує

Позначмо `n` — рядків, `C` — колонок, `m` — змінених рядків.

```
доступ за номером колонки     O(1)         перевірка біта + читання з масиву
доступ за іменем              O(1)         + один пошук у хеші
прохід колонкою               O(n)         щільно, 8 Б на рядок
додати рядок                  O(C) аморт.  C викликів emplace_back
позначити вилученим           O(1)         один запис у state_
правка комірки                O(1)         + одна вставка в orig_ на ПЕРШУ правку
породити оператори            O(m·C)       умова WHERE перебирає всі колонки
ущільнити                     O(n·C)       єдина дорога операція, раз після accept()
```

Найцікавіше — прохід колонкою, бо в ньому колонковий розклад і виграє. Процесор читає пам'ять не байтами, а лініями по 64 байти ([кеш](book:programming/cache) працює саме так), тож байти, які ви не використали, усе одно приїхали з пам'яті й посунули щось корисне.

**Скільки байтів прийде з пам'яті, щоб просумувати `total_cents` по 200 000 рядків?**

```
колонковий розклад:
  масив int64 підряд          200 000 · 8 Б      = 1.6 МБ
  корисних байтів у лінії     64 з 64            = 100 %

рядковий розклад (35 Б на рядок — рахунок нижче):
  крок між сусідніми total    35 Б
  лінія 64 Б накриває         64 / 35 ≈ 1.8 рядка
  тож із пам'яті прийде весь масив рядків        = 7.0 МБ
  корисних байтів у лінії     8 з 35             ≈ 23 %

  7.0 / 1.6                                      = 4.4 раза зайвого трафіку
```

Зворотний бік того самого — вставка. Додати рядок у колонковий набір означає торкнутися `C` різних масивів у `C` різних місцях пам'яті, і кожен із них колись перевиділиться окремо. Рядковому розкладу вистачає одного `push_back`. Саме тому набір для діалогового редагування історично рядковий, а колонковий розклад живе там, де рядки додають пачками й рідко, — у [стовпцевому зберіганні](book:programming/columnar-storage) аналітичних баз.

Тепер пам'ять. Порахуймо наш набір чесно, з реальними розмірами типів.

**Скільки важать 200 000 рядків по п'ять колонок?**

```
прямий розклад (текст — std::string):
  id, total_cents, updated_at    3 · 8 Б                = 24 Б
  customer_id, status            2 · 32 Б (libstdc++)   = 64 Б
  біти валідності                5 / 8                  ≈  1 Б
  стан рядка                     uint8                  =  1 Б
  разом на рядок                                        = 90 Б
  200 000 · 90 Б                                        ≈ 18.0 МБ
                       (+ купа під кожен текст, довший за 15 символів)

після двох правок розкладу:
  status → код у словнику        uint8                  =  1 Б   (було 32)
  customer_id → зсув в арені     uint64                 =  8 Б   (було 32 + купа)
  разом на рядок                                        = 35 Б
  200 000 · 35 Б                                        ≈  7.0 МБ

  18.0 / 7.0                                            ≈ 2.6 раза
```

Обидві правки — про те саме: `std::string` носить із собою 32 байти службової структури (24 в libc++) заради здатності бути будь-яким рядком, а колонка `status` має жменю різних значень на двісті тисяч рядків. Словник кодів робить із неї один байт; арена — суцільний буфер тексту плюс масив зсувів — прибирає окреме виділення на кожен рядок і, як побічний ефект, кладе весь текст колонки поруч у пам'яті.

## Три пастки, що лишилися

**Дві нитки в одному слові маски.** Розділити прохід між потоками спокусливо: перший бере рядки 0–99 999, другий — решту. Читати так можна, а писати — ні: біти рядків 99 998 і 100 001 лежать в **одному** 64-бітному слові, а запис біта — це читання слова, правка й запис назад. Дві нитки, що роблять це одночасно, гублять зміни одна одної. Це не [хибне спільне використання](book:programming/false-sharing), де дані різні, а лінія кеша спільна й страждає лише швидкість, — це справжня гонитва даних, від якої псуються значення. Ліки прості: межі діапазонів вирівнювати на 64 рядки, тобто на межу слова маски.

**Прийняти зміни до підтвердження.** Найдорожча помилка з усіх і найлегша для написання: `accept()` стоїть одразу після циклу операторів, а `commit()` — рядком нижче. Доки нічого не падає, різниці не видно. У день, коли транзакція відкотиться, набір уже вважатиме, що все записано: стани скинуті в «незмінений», тіні стерті, надгробки прибрані. Правок, які людина робила пів години, не існує ні в базі, ні в наборі. Порядок «спершу `COMMIT`, потім `accept`» — не стилістична вподоба, а єдина точка, у якій набір має право повірити базі; поки [транзакція](book:programming/transactions-acid) не підтверджена, її результат не існує ні для кого, включно з тим, хто її почав.

**Часткова невдача — це нормальний стан.** Коли дев'ятнадцятий оператор із двадцяти дав конфлікт, `apply_all` кидає виняток, база відкочується, а набір лишається точно таким, яким був: усі правки на місці, усі тіні цілі. Це правильно — користувачеві є що показати й що виправити. Спокуса «підчистити» набір у гілці `catch` виглядає охайно, а насправді знищує єдину копію даних, яку ще ніхто не бачив у базі.
