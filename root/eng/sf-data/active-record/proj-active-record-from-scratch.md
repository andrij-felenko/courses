# ⚙️ Робочий Active Record на півтори сотні рядків

Клас на три десятки рядків, який сам себе знаходить і сам себе зберігає, вже працює — але бібліотекою він ще не є. Між ним і тим, що стоїть під Rails чи Django, лежать три речі, і жодна з них не виглядає складною:

- `save()` пише **всі** колонки, навіть ті, яких ніхто не торкався;
- поля класу перелічені руками, хоч база й так знає їхній перелік напам'ять;
- два одночасні збереження одного рядка мовчки затирають одне одного.

Кожну полагодимо окремо, на живому коді, який запускається. Основа — SQLite: він лежить у стандартній поставці і Python (`sqlite3`), і Node (`node:sqlite`), тож жодної зовнішньої залежності не треба, а патерн видно без прошарку фреймворку. Таблиця всюди та сама:

```sql
CREATE TABLE orders (
  id           INTEGER PRIMARY KEY,
  customer_id  TEXT,
  total        REAL    NOT NULL DEFAULT 0,
  status       TEXT    NOT NULL DEFAULT 'new',
  lock_version INTEGER NOT NULL DEFAULT 0
)
```

Найцікавіше почнеться не тоді, коли всі три кроки запрацюють, а коли вони зустрінуться між собою: кожен щось купує — і мовчки щось продає. Ціну видно лише на зібраному коді, тож спершу зберімо.

## Крок 1. Писати лише те, що змінилося

Присвоїли `order.status = "shipped"` — змінилася одна колонка з чотирьох, а `UPDATE` несе в базу всі чотири. Здається, дрібниця: рядок короткий, мережа швидка. Але щоб покласти в `UPDATE` колонку `total`, її треба **мати** — тобто прочитати всі колонки, навіть коли потрібен був самий статус. І щоб записати `total`, треба бути певним, що твоє значення свіже. Одна зайва колонка в `SET` — це мовчазне твердження «я знаю поточне значення `total`, і воно моє». Твердження, за яке рано чи пізно доведеться відповідати.

Тож завдання: `save()` мусить сам знати, що саме змінилося з моменту читання. Знати це можна лише з одного місця — з дороги, якою значення потрапляє в об'єкт. У Python така дорога єдина: будь-яке `x.поле = значення` проходить крізь `__setattr__`. Станьмо на ній.

```py
def __setattr__(self, name, value):
    if name not in type(self).columns():        # не колонка — звичайний атрибут
        object.__setattr__(self, name, value)
        return
    if self._data.get(name, _UNSET) != value:   # те саме значення не бруднить
        self._dirty.add(name)
    self._data[name] = value
```

Колонки більше не живуть в `__dict__` об'єкта — вони переїхали у власний словник `_data`, а поруч став `_dirty`: набір імен, які чіпали після читання з бази. Звідси `_update()` бере рівно те, що треба:

```py
cols = [c for c in cls.columns()
        if c in self._dirty and c != cls.pk and c != cls.version]
if not cols:
    return 0                                # нічого не змінилося — жодного запиту
```

Три наслідки випливають один із одного. `UPDATE` тепер несе одну колонку замість чотирьох. `save()` на об'єкті, якого не міняли, не робить **взагалі жодного запиту** — не порожній `UPDATE`, а тиша. І присвоєння того самого значення (`status = "shipped"` там, де вже `"shipped"`) не бруднить поля, бо звіряємо не факт присвоєння, а значення. Rails зве це `partial_updates` і тримає ввімкненим за замовчуванням; Django не робить так ніколи — його `save()` пише всі поля, поки не попросиш `update_fields` руками.

> 🔧 **Навіщо це.** Порахуй на екрані-списку, де користувач правив одну галочку в рядку з сорока колонками. Без брудного набору кожен `save()` — це сорок значень у `SET`, сорок значень у мережу й повний перезапис рядка, а на широких таблицях ще й перезапис індексів по колонках, які ніхто не міняв. З брудним набором — одна колонка. Але справжня плата не в байтах: повний `UPDATE` мовчки заявляє, що ти знаєш **усі сорок** поточних значень. Ти їх не знаєш — ти їх читав секунду тому.

## Крок 2. Клас, який не оголошує полів

Тепер `__setattr__` мусить відрізняти колонку від звичайного атрибута — а для цього треба знати перелік колонок. Оголошувати його в класі руками означає списати з таблиці те, що таблиця про себе й так знає. Тож спитаймо базу:

```py
@classmethod
def columns(cls):
    if "_columns" not in cls.__dict__:          # кеш саме цього класу
        info = cls.db.execute(f'PRAGMA table_info("{cls.table}")').fetchall()
        if not info:
            raise LookupError(f'таблиці "{cls.table}" немає')
        cls._columns = tuple(row[1] for row in info)
    return cls._columns
```

`PRAGMA table_info` — SQLite-ів спосіб показати схему таблиці; в інших базах те саме дає `information_schema.columns`. Перевірка `"_columns" not in cls.__dict__` замість звичного `cls._columns is None` тут не примха: інакше підклас побачив би кеш батька й вирішив, що його колонки — то колонки чужої таблиці.

Тепер придивімося до рядка, який виглядає як недбалість: ім'я таблиці вставлене в SQL конкатенацією, а не параметром. Це не лінощі — так **доводиться**. Прив'язати параметром (`?`) можна лише значення; ідентифікатор — ім'я таблиці чи колонки — параметром прив'язати не можна в жодній базі, бо параметр підставляється вже після того, як запит розібрано на частини, а ім'я колонки визначає сам розбір. Тому кожна без винятку бібліотека Active Record будує SQL склеюванням рядків. Питання лише в тому, звідки беруться склеювані імена.

І ось де крок 2 повертає борг: після нього імена приходять **із самої схеми**. Не від користувача, не з параметра запиту — з `PRAGMA`, тобто від бази, яку й питаємо. Ось звідки береться ця перевірка в `where()`:

```py
for c in cond:
    if c not in cls.columns():              # у SQL іде лише те, що дала схема
        raise LookupError(f'колонки "{c}" в "{cls.table}" немає')
```

Схема тут працює білим списком: усе, що не збіглося з іменем справжньої колонки, до склеювання не доживає. Конкатенація лишається, а діри немає — бо склеюємо лише те, що база щойно сама й назвала.

Той самий крок пояснює механіку, від якої страждають усі: **об'єкт цього класу не існує без бази**. Не тому, що комусь так схотілося, а тому, що `__setattr__` не може відповісти на питання «це колонка?», не сходивши по схему. `Order(customer_id="c-19")` без живого з'єднання падає ще до першого запису — конструктор кличе `columns()`. Rails поводиться точнісінько так само й з тієї ж причини.

Мовам зі статичними типами цей крок дається дорожче, і варто побачити, чому саме. У Python поля з'являються самі: `__getattr__` віддасть будь-що з `_data`. Компілятор TypeScript про `PRAGMA` не знає нічого — до запуску схеми немає. Тому полям доводиться оголоситися вдруге, вже для нього:

```ts
// Полів у класі немає — вони приїдуть зі схеми. Але компілятору про них треба сказати окремо.
interface Order {
  id: number | null;
  customer_id: string;
  total: number;
  status: string;
  lock_version: number;
}
class Order extends Model {
  static table = "orders";
  static version = "lock_version";
  static db = db;

  canCancel(): boolean {
    return this.status === "new" || this.status === "paid";
  }
}
```

Клас і однойменний інтерфейс зливаються в один тип: інтерфейс описує поля для компілятора, посередник підставляє їх на виконанні. Задум кроку 2 — прибрати опис, який дублює схему, — на виконанні здійснено повністю, а на рівні типів дублювання повернулося тим самим списком, з якого ми й тікали. Саме тому в TypeScript-світі перемогли не самоглядні бібліотеки, а генератори: Prisma, Drizzle, Kysely читають схему **до** запуску й породжують ці описи кодом. Дублювання нікуди не поділося — його просто перестали писати руками.

## Крок 3. Лічильник версій

Крок 1 виглядав як економія байтів, але тихо змінив дещо серйозніше. Двоє правлять одне замовлення: один пише `status`, другий — `total`. Повний `UPDATE` віддав би перемогу тому, хто зберігся другим: він переписав би обидві колонки, включно з чужою, значенням, яке прочитав до чужої правки. З брудним набором ці двоє **просто не зустрічаються**: у їхніх `UPDATE` різні колонки в `SET`, і обидві правки доїжджають. Крок 1 полагодив цілий клас гонок, навіть не ставлячи собі такої мети.

Але лише той клас, де колонки різні. Хай тепер обидва міняють `total`:

![Дві панелі. Угорі без лічильника: клієнти A і B по черзі читають рядок orders id 42 і бачать total 100, потім A пише UPDATE total 110 WHERE id 42 і дістає один рядок, за ним B пише UPDATE total 120 з тим самим WHERE і теж дістає один рядок; підсумок — у базі 120, робота A зникла. Унизу з лічильником: обидва читають total 100 і lock_version 0, A пише UPDATE з SET lock_version 1 і WHERE id 42 AND lock_version 0 та дістає один рядок, а B із тим самим WHERE дістає нуль рядків і StaleObject; підсумок — у базі 110, B мусить перечитати](img/ar-lost-update.svg)

*Обидва прочитали сотню, обидва порахували від неї — і обидва мали рацію в момент читання. Верхній `UPDATE` не бреше й не помиляється: він робить рівно те, що просили. Просто ніхто не спитав, чи та сотня ще на місці.*

Це **втрачене оновлення**: не збій, не помилка запиту, а два коректні записи, з яких другий стер перший. Пастка в тому, що `WHERE id = 42` — надто слабка умова. Вона питає «чи існує рядок 42», а спитати треба інше: «чи це **той самий** рядок 42, який я читав». Донесімо цю різницю до бази — додаймо в `WHERE` версію, яку бачили:

```py
if cls.version:
    seen = self._data[cls.version] or 0
    sets.append(f'"{cls.version}" = ?')
    args.append(seen + 1)
    where += f' AND "{cls.version}" = ?'    # рядок мусить бути тим, що ми читали
    wargs.append(seen)
cur = cls.db.execute(
    f'UPDATE "{cls.table}" SET {", ".join(sets)} WHERE {where}', args + wargs)
if cur.rowcount != 1:                       # 0 рядків → версія вже не наша
    raise StaleObject(f'{cls.__name__} {self._data[cls.pk]}: рядок змінили')
```

Уся вигадка — в тому, що перевірку робить не програма, а сама база, тим самим запитом, що й запис. Прочитати версію, порівняти й записати окремими кроками не можна: між порівнянням і записом устигне вклинитися чужий запис — рівно та гонка, яку ловимо. А `UPDATE` із версією в `WHERE` — одна атомарна дія: або рядок і досі той, який читали, і його змінено, або він уже не той, і не змінено нічого.

Відповідь бази — не помилка, а **кількість змінених рядків**. Нуль означає, що рядок із такою версією не знайшовся: хтось уже підняв лічильник. Тому `rowcount != 1` — це не перевірка «чи вдалося», а весь механізм цілком.

Прийом зветься [оптимістичне блокування](topic:sf-data/optimistic-locking): рядок не замикають наперед, а дають усім працювати вільно й ловлять конфлікт на записі — розрахунок на те, що зіткнення рідкі й дешевше зрідка перепитати, ніж завжди стояти в черзі. Rails робить буквально це: колонка `lock_version` (ім'я міняють через `self.locking_column`), `self[locking_column] += 1` перед записом, версія в `WHERE`, а далі — `if affected_rows != 1` і `ActiveRecord::StaleObjectError`. Півтори сотні наших рядків і промислова бібліотека тут збігаються не приблизно, а буквально.

Ловити `StaleObject` мусить той, хто кликав `save()`, і зробити з нього щось осмислене може тільки він: перечитати й повторити, показати користувачеві «поки ви думали, замовлення змінили», злити зміни. Бібліотека чесно каже, що не знає відповіді — бо відповідь предметна, а не технічна.

## Уся бібліотека

Сто десять рядків коду в Python, півтори сотні в TypeScript. Обидві вкладки — те саме: та сама таблиця, ті самі три кроки, той самий результат.

:::tabs
```py
import sqlite3

_UNSET = object()


class StaleObject(Exception):
    """Рядок змінив хтось інший, поки ми тримали цей об'єкт."""


class Record:
    table = ""            # ім'я таблиці
    pk = "id"             # первинний ключ
    version = None        # колонка-лічильник або None
    db = None             # sqlite3.Connection

    # ── схема: клас питає базу, які в нього поля ──
    @classmethod
    def columns(cls):
        if "_columns" not in cls.__dict__:          # кеш саме цього класу
            info = cls.db.execute(f'PRAGMA table_info("{cls.table}")').fetchall()
            if not info:
                raise LookupError(f'таблиці "{cls.table}" немає')
            cls._columns = tuple(row[1] for row in info)
        return cls._columns

    # ── брудний набір: перехоплюємо присвоєння ──
    def __init__(self, **fields):
        object.__setattr__(self, "_data", {c: None for c in type(self).columns()})
        object.__setattr__(self, "_dirty", set())
        for name, value in fields.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        if name not in type(self).columns():        # не колонка — звичайний атрибут
            object.__setattr__(self, name, value)
            return
        if self._data.get(name, _UNSET) != value:   # те саме значення не бруднить
            self._dirty.add(name)
        self._data[name] = value

    def __getattr__(self, name):                    # лише коли не знайшли інакше
        try:
            return self.__dict__["_data"][name]
        except KeyError:
            raise AttributeError(name) from None

    def changes(self):
        return {c: self._data[c] for c in sorted(self._dirty)}

    # ── читання ──
    @classmethod
    def _from_row(cls, row):
        obj = cls.__new__(cls)                      # __init__ не потрібен: рядок готовий
        object.__setattr__(obj, "_data", dict(zip(cls.columns(), row)))
        object.__setattr__(obj, "_dirty", set())    # щойно з бази → чистий
        return obj

    @classmethod
    def find(cls, key):
        names = ", ".join(f'"{c}"' for c in cls.columns())
        row = cls.db.execute(
            f'SELECT {names} FROM "{cls.table}" WHERE "{cls.pk}" = ?', (key,)
        ).fetchone()
        return cls._from_row(row) if row else None

    @classmethod
    def where(cls, **cond):
        for c in cond:
            if c not in cls.columns():              # у SQL іде лише те, що дала схема
                raise LookupError(f'колонки "{c}" в "{cls.table}" немає')
        names = ", ".join(f'"{c}"' for c in cls.columns())
        sql = f'SELECT {names} FROM "{cls.table}"'
        if cond:
            sql += " WHERE " + " AND ".join(f'"{c}" = ?' for c in cond)
        return [cls._from_row(r) for r in cls.db.execute(sql, tuple(cond.values()))]

    # ── запис ──
    def save(self):
        return self._insert() if self._data[type(self).pk] is None else self._update()

    def _insert(self):
        cls = type(self)
        if cls.version:
            self._data[cls.version] = 0
            self._dirty.add(cls.version)
        cols = [c for c in cls.columns() if c in self._dirty]
        if cols:
            names = ", ".join(f'"{c}"' for c in cols)
            marks = ", ".join("?" for _ in cols)
            cur = cls.db.execute(f'INSERT INTO "{cls.table}" ({names}) VALUES ({marks})',
                                 [self._data[c] for c in cols])
        else:
            cur = cls.db.execute(f'INSERT INTO "{cls.table}" DEFAULT VALUES')
        self._data[cls.pk] = cur.lastrowid
        self._dirty.clear()
        return 1

    def _update(self):
        cls = type(self)
        cols = [c for c in cls.columns()
                if c in self._dirty and c != cls.pk and c != cls.version]
        if not cols:
            return 0                                # нічого не змінилося — жодного запиту
        sets = [f'"{c}" = ?' for c in cols]
        args = [self._data[c] for c in cols]
        where, wargs = f'"{cls.pk}" = ?', [self._data[cls.pk]]
        if cls.version:
            seen = self._data[cls.version] or 0
            sets.append(f'"{cls.version}" = ?')
            args.append(seen + 1)
            where += f' AND "{cls.version}" = ?'    # рядок мусить бути тим, що ми читали
            wargs.append(seen)
        cur = cls.db.execute(
            f'UPDATE "{cls.table}" SET {", ".join(sets)} WHERE {where}', args + wargs)
        if cur.rowcount != 1:                       # 0 рядків → версія вже не наша
            raise StaleObject(f'{cls.__name__} {self._data[cls.pk]}: рядок змінили')
        if cls.version:
            self._data[cls.version] = seen + 1
        self._dirty.clear()
        return 1

    def delete(self):
        cls = type(self)
        key = self._data[cls.pk]
        if key is None:
            return 0
        cur = cls.db.execute(f'DELETE FROM "{cls.table}" WHERE "{cls.pk}" = ?', (key,))
        self._data[cls.pk] = None                   # ключа немає → рядка немає
        object.__setattr__(self, "_dirty", {c for c in cls.columns()
                                            if c != cls.pk and self._data[c] is not None})
        return cur.rowcount
```
```ts
import { DatabaseSync } from "node:sqlite";

export class StaleObject extends Error {}

type Row = Record<string, unknown>;
const q = (s: string) => `"${s.replace(/"/g, '""')}"`;

export class Model {
  static table = "";
  static pk = "id";
  static version: string | null = null;
  static db: DatabaseSync;
  static _columns?: string[];

  // ── схема: клас питає базу, які в нього поля ──
  static columns(): string[] {
    if (!Object.hasOwn(this, "_columns")) {         // кеш саме цього класу
      const info = this.db
        .prepare(`PRAGMA table_info(${q(this.table)})`)
        .all() as { name: string }[];
      if (info.length === 0) throw new Error(`таблиці ${q(this.table)} немає`);
      this._columns = info.map((r) => r.name);
    }
    return this._columns!;
  }

  _data: Row = {};
  _dirty = new Set<string>();

  constructor(fields: Row = {}) {
    const cls = new.target as typeof Model;
    for (const c of cls.columns()) this._data[c] = null;
    const self = new Proxy(this, HANDLER);
    Object.assign(self, fields);
    return self;                                    // назовні віддаємо посередника
  }

  get changes(): Row {
    const out: Row = {};
    for (const c of [...this._dirty].sort()) out[c] = this._data[c];
    return out;
  }

  // ── читання ──
  static fromRow<T extends typeof Model>(this: T, row: Row): InstanceType<T> {
    const obj = Object.create(this.prototype) as Model;
    obj._data = { ...row };
    obj._dirty = new Set();                         // щойно з бази → чистий
    return new Proxy(obj, HANDLER) as InstanceType<T>;
  }

  static find<T extends typeof Model>(this: T, key: unknown): InstanceType<T> | null {
    const names = this.columns().map(q).join(", ");
    const row = this.db
      .prepare(`SELECT ${names} FROM ${q(this.table)} WHERE ${q(this.pk)} = ?`)
      .get(key as never) as Row | undefined;
    return row ? this.fromRow(row) : null;
  }

  static where<T extends typeof Model>(this: T, cond: Row = {}): InstanceType<T>[] {
    const keys = Object.keys(cond);
    for (const k of keys)
      if (!this.columns().includes(k))              // у SQL іде лише те, що дала схема
        throw new Error(`колонки ${q(k)} в ${this.table} немає`);
    const names = this.columns().map(q).join(", ");
    let sql = `SELECT ${names} FROM ${q(this.table)}`;
    if (keys.length) sql += " WHERE " + keys.map((k) => `${q(k)} = ?`).join(" AND ");
    const rows = this.db.prepare(sql).all(...(Object.values(cond) as never[])) as Row[];
    return rows.map((r) => this.fromRow(r));
  }

  // ── запис ──
  save(): number {
    const cls = this.constructor as typeof Model;
    return this._data[cls.pk] === null || this._data[cls.pk] === undefined
      ? this.insert()
      : this.update();
  }

  private insert(): number {
    const cls = this.constructor as typeof Model;
    if (cls.version) {
      this._data[cls.version] = 0;
      this._dirty.add(cls.version);
    }
    const cols = cls.columns().filter((c) => this._dirty.has(c));
    let info;
    if (cols.length) {
      const names = cols.map(q).join(", ");
      const marks = cols.map(() => "?").join(", ");
      info = cls.db
        .prepare(`INSERT INTO ${q(cls.table)} (${names}) VALUES (${marks})`)
        .run(...(cols.map((c) => this._data[c]) as never[]));
    } else {
      info = cls.db.prepare(`INSERT INTO ${q(cls.table)} DEFAULT VALUES`).run();
    }
    this._data[cls.pk] = Number(info.lastInsertRowid);
    this._dirty.clear();
    return 1;
  }

  private update(): number {
    const cls = this.constructor as typeof Model;
    const cols = cls
      .columns()
      .filter((c) => this._dirty.has(c) && c !== cls.pk && c !== cls.version);
    if (!cols.length) return 0;                     // нічого не змінилося — жодного запиту

    const sets = cols.map((c) => `${q(c)} = ?`);
    const args: unknown[] = cols.map((c) => this._data[c]);
    let where = `${q(cls.pk)} = ?`;
    const wargs: unknown[] = [this._data[cls.pk]];

    let seen = 0;
    if (cls.version) {
      seen = Number(this._data[cls.version] ?? 0);
      sets.push(`${q(cls.version)} = ?`);
      args.push(seen + 1);
      where += ` AND ${q(cls.version)} = ?`;        // рядок мусить бути тим, що ми читали
      wargs.push(seen);
    }
    const info = cls.db
      .prepare(`UPDATE ${q(cls.table)} SET ${sets.join(", ")} WHERE ${where}`)
      .run(...([...args, ...wargs] as never[]));
    if (Number(info.changes) !== 1)                 // 0 рядків → версія вже не наша
      throw new StaleObject(`${cls.name} ${this._data[cls.pk]}: рядок змінили`);
    if (cls.version) this._data[cls.version] = seen + 1;
    this._dirty.clear();
    return 1;
  }

  delete(): number {
    const cls = this.constructor as typeof Model;
    const key = this._data[cls.pk];
    if (key === null || key === undefined) return 0;
    const info = cls.db
      .prepare(`DELETE FROM ${q(cls.table)} WHERE ${q(cls.pk)} = ?`)
      .run(key as never);
    this._data[cls.pk] = null;                      // ключа немає → рядка немає
    this._dirty = new Set(
      cls.columns().filter((c) => c !== cls.pk && this._data[c] !== null),
    );
    return Number(info.changes);
  }
}

const HANDLER: ProxyHandler<Model> = {
  get(t, k, recv) {
    // hasOwn, а не `in`: інакше "constructor" знайдеться в прототипі _data
    if (typeof k === "string" && Object.hasOwn(t._data, k)) return t._data[k];
    return Reflect.get(t, k, recv);
  },
  set(t, k, v) {
    const cls = t.constructor as typeof Model;
    if (typeof k === "string" && cls.columns().includes(k)) {
      if (t._data[k] !== v) t._dirty.add(k);        // те саме значення не бруднить
      t._data[k] = v;
      return true;
    }
    return Reflect.set(t, k, v);
  },
};
```
:::

Роль `__setattr__` у TypeScript грає [проксі](topic:sf-apps/proxy) — об'єкт-посередник, що стоїть перед справжнім і перехоплює звертання до нього: `get` віддає колонку з `_data`, `set` бруднить її й кладе назад. Конструктор віддає назовні саме посередника (`return self`) — інакше перехоплювати було б нічого. Одну помилку тут видно вже на другому запуску: якщо в пастці `get` написати звичне `k in t._data`, то `this.constructor` знайде `constructor` у прототипі порожнього об'єкта й поверне `Object`. Звідси `Object.hasOwn` — і це не причепка стилю, а різниця між робочим кодом і мовчазною поламкою.

## Що вона вміє

Модель — це те, з чого починалося: ім'я таблиці, ім'я колонки-лічильника й предметне правило. Полів не оголошено.

```py
class Order(Record):
    table = "orders"
    version = "lock_version"
    db = db

    def can_cancel(self):
        return self.status in ("new", "paid")
```

Далі — справжній вивід справжнього прогону; SQL показує сам SQLite через `db.set_trace_callback`, тож це не переказ, а те, що поїхало в базу:

```
полів у класі не оголошено, а вони є:
   SQL: PRAGMA table_info("orders")
   ('id', 'customer_id', 'total', 'status', 'lock_version')

створюємо:
   SQL: INSERT INTO "orders" ("customer_id", "total", "status", "lock_version")
        VALUES ('c-19', 1200.0, 'paid', 0)
   id = 1 | lock_version = 0 | can_cancel() = True

міняємо ОДНУ колонку:
   SQL: SELECT "id", "customer_id", "total", "status", "lock_version"
        FROM "orders" WHERE "id" = 1
   changes() = {'status': 'shipped'}
   SQL: UPDATE "orders" SET "status" = 'shipped', "lock_version" = 1
        WHERE "id" = 1 AND "lock_version" = 0

save() без жодної зміни:
   рядків змінено: 0 — бо запиту не було

двоє правлять ту саму колонку:
   SQL: SELECT ... FROM "orders" WHERE "id" = 1
   SQL: SELECT ... FROM "orders" WHERE "id" = 1
   SQL: UPDATE "orders" SET "total" = 10.0, "lock_version" = 2
        WHERE "id" = 1 AND "lock_version" = 1
   SQL: UPDATE "orders" SET "total" = 20.0, "lock_version" = 2
        WHERE "id" = 1 AND "lock_version" = 1
   StaleObject: Order 1: рядок змінили
   у базі total = 10.0 — двадцятку відхилено, а не втрачено
```

Порожній клас, який знає свої поля, пише лише змінене й не дає себе тихо затерти. Рівно те, за що люблять справжні бібліотеки.

## Складність і пастки

Тепер найважливіше. Пастки, про які йтиметься, — не недоробки цієї бібліотеки. Кожна з них є в Rails, Django й Hibernate, і кожна росте з того самого кроку, який дав зручність. У малому коді їх просто видно цілком.

### Лічильник рахує рядок, а не колонку

Крок 1 тихо прибрав цілу гонку: двоє правлять різні колонки — обидва доїжджають. Крок 3 цей подарунок забирає назад. Версія одна на весь рядок, тож `WHERE lock_version = 0` не питає «чи чіпав хтось `total`» — він питає «чи чіпав хтось **рядок**». Двоє, що акуратно розійшлися по різних колонках, тепер конфліктують.

![Таблиця дві на два. Стовпці: A міняє status, B міняє total (різні колонки); обидва міняють total (та сама колонка). Рядки: save() пише лише змінені колонки; те саме плюс лічильник версій на рядок. Клітини: різні колонки без лічильника — обидва доїхали, різні UPDATE не зустрілися; та сама колонка без лічильника — тихо втрачене оновлення, у базі 20, десятку стерто; різні колонки з лічильником — хибний конфлікт, B відхилено, хоч воно не торкалося status; та сама колонка з лічильником — спіймано, нуль рядків, StaleObject. Унизу підпис: лічильник рахує рядок, а не колонку](img/ar-dirty-vs-version.svg)

*Чотири клітини, і двох галочок одночасно не буває. Вимкнеш лічильник — втратиш оновлення на спільній колонці; увімкнеш — платитимеш хибними конфліктами там, де їх не було.*

Напрошується розумніший хід: замість версії ставити в `WHERE` **старі значення** тих колонок, які пишемо (`WHERE id = 42 AND total = 100`). Тоді обидві галочки нібито сходяться: різні колонки не заважають одна одній, а та сама — ловиться. Це не вигадка — Hibernate дає рівно це: `OptimisticLockType.DIRTY` кладе у `WHERE` змінені поля, `ALL` — усі, а `VERSION` (як у нас) — лічильник.

Але спроба обійтися без версії ламається одразу в трьох місцях, і кожне варте того, щоб його побачити.

**Колонка була порожня.** `WHERE total = NULL` не збігається ніколи — навіть із рядком, де `total` таки `NULL`, бо порівняння з `NULL` дає не «істину», а «невідомо». Об'єкт, який заповнює порожнє поле, дістає `StaleObject` на рівному місці, без жодного суперника поруч.

**Значення повернулося.** Хтось змінив `total` зі 100 на 200, а тоді назад на 100. Старе значення на місці, `WHERE` збігається, запис проходить — хоча між нашим читанням і записом рядок жив своїм життям двічі. Лічильник таке ловить, бо рахує **події**, а не значення.

**Правило спиралося на колонку, якої ми не пишемо.** Прочитали `total = 100`, вирішили «відвантажувати можна» й пишемо `status = "shipped"`. Тим часом хтось підняв `total` до 5000. У `WHERE` стоїть лише `status` — запис проходить, і в базі опиняється відвантажене замовлення на п'ять тисяч, яке за правилом відвантажувати було не можна. Рішення ухвалили на даних, яких уже немає, а перевірка про ті дані не спитала.

Ось чому промислові бібліотеки за замовчуванням беруть грубий лічильник на рядок. Він **консервативний навмисне**: захищає не «колонку, яку я пишу», а «рядок, який я читав» — а саме на прочитаному рядку й будували рішення. Хибний конфлікт — не збій механізму, а його ціна: він каже «дані під тобою змінилися, перевір, чи твоє рішення ще чинне», і у випадку з відвантаженням має цілковиту рацію. Тонший `DIRTY` дешевший рівно тому, що питає менше, — і мовчить у випадках, де важливо було спитати.

### Брудний набір бачить лише присвоєння

`__setattr__` спрацьовує на `=`, і ні на чому іншому. Хай у колонці лежить JSON:

```py
note.tags.append("нове")   # присвоєння не було → __setattr__ не кликали
note.save()                # _dirty порожній → жодного запиту → зміна зникла
```

Жодної помилки, жодного попередження: `changes()` порожній, `save()` чесно вирішує, що робити нічого. Дані просто не доїхали. Ця пастка — пряма плата за крок 1: доти, доки `save()` писав усі колонки, зміна на місці доїжджала сама собою, бо колонку писали в будь-якому разі.

Ліки — не довіряти сетерам, а тримати знімок того, що прочитали, і звіряти з ним **у момент запису**, вже після перетворення значення на те, що поїде в базу. Rails робить саме це: `attribute_was` дістає `original_value` зі знімка, а на випадок зміни на місці є окрема перевірка `changed_in_place?`, яка порівнює серіалізовані форми старого й нового значення. Довгий шлейф багів Rails навколо `serialize`-колонок — про те, як дорого це дається насправді.

### Імена колонок живуть в одному просторі з методами

Об'єкт удає, що `order.total` — це поле, хоча воно приїхало зі схеми. Отже, імена колонок і імена методів діляться одним простором імен. Колонка `save`, `changes` чи `delete` — і модель зламана: у Python `__getattr__` навіть не покличеться, бо метод знайдеться раніше, а в TypeScript `Object.hasOwn` віддасть колонку замість методу.

Це не гіпотеза — рівно на цьому й спіткнувся код вище, коли `k in t._data` знайшов `constructor` у прототипі. Rails цю межу стереже явно: `dangerous_attribute_method?` перевіряє кожен атрибут проти власних методів `ActiveRecord::Base` і на збігу кидає `DangerousAttributeError` — краще відмовитися завести модель, ніж дати їй тихо поводитися дивно. Ціна кроку 2 у чистому вигляді: коли поля приходять із бази, база дістає право зламати клас іменем колонки.

### Обіцянка «лише змінене» дорожча на вставці, ніж на оновленні

Наш `_insert()` теж пише лише поставлені колонки — інші дістають замовчування з `CREATE TABLE`. Виглядає послідовно, але має неочевидний наслідок: об'єкт після `save()` **не дорівнює рядку**. У полі, якого не ставили, в об'єкті `None`, а в базі — `0` чи `'new'`, і об'єкт про це не знає, поки не перечитає. Rails прожив із цим дев'ять років, а у версії 7.0 вимкнув `partial_inserts` за замовчуванням: часткова вставка заважає безпечно прибирати замовчування колонок, а виграш на розмірі запиту виявився мізерним. Показово, що `partial_updates` при цьому лишили ввімкненим — на оновленні та сама ідея коштує менше, ніж дає.

### Чого тут немає — і чому це не дрібниці

Кожен `save()` — окрема дія. Зберегти замовлення разом із позиціями означає кілька незалежних записів: упаде другий — перший уже в базі. Щоб вони доїхали разом, потрібна [транзакція](topic:sf-data/transactions-acid) — межа, всередині якої або застосовуються всі зміни, або жодна; відкривати її доводиться зовні, руками, і жоден об'єкт про неї не знає. Систематична відповідь на це — [одиниця роботи](topic:sf-data/unit-of-work): накопичити всі зміни й записати одним махом в одній транзакції; тоді ж стає видно й порядок записів, і те, що `save()` посеред циклу — часто помилка.

Двічі покликаний `Order.find(1)` дає **два різні об'єкти** на один рядок — саме на цьому й тримається вся демонстрація гонки вище. У демонстрації це зручно, у застосунку — джерело загадкових багів: змінив в одному, зберіг другий. Лікує це [карта тотожності](topic:sf-data/identity-map) — реєстр «один рядок у межах роботи = один об'єкт у пам'яті», якого тут просто немає.

І врешті — те, чого лічильник не заміняє. Втрачене оновлення має ім'я не випадково: це класична аномалія, яку описують [рівні ізоляції](topic:sf-data/isolation-levels) — правила про те, наскільки транзакції бачать роботу одна одної. База вміє не допускати її сама, суворішою ізоляцією або блокуванням на читанні. Оптимістичний лічильник потрібен там, де ця дорога закрита: між читанням і записом користувач півгодини дивився на форму, транзакції давно немає, а зіткнення все одно треба спіймати. Він захищає не транзакцію, а **розмову** з користувачем.

Півтори сотні рядків не дають ані транзакцій, ані карти тотожності, ані зв'язків між таблицями — і саме тому в них так добре видно головне. Це не зменшена копія Rails, а його кістяк у натуральну величину: ті самі три кроки, ті самі місця, де вони труться одне об одне. Дописуючи решту, велика бібліотека не позбувається цих тертів — вона їх обростає. Тому й читати її потім легше, знаючи, що `partial_updates`, `lock_version` і `changed_in_place?` — не мудрація авторів, а три відповіді на три питання, які ставить собі кожен, хто дозволив об'єктові самому ходити в базу.
