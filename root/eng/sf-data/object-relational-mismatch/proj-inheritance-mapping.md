# ⚙️ Три способи покласти ієрархію в таблиці

У пам'яті ця задача — не задача. Є абстрактний `Payment`, є два його різновиди: `CardPayment` (оплата карткою — останні чотири цифри, код авторизації) і `BankTransfer` (банківський переказ — IBAN, призначення). Спільне в них — сума й дата. Хочеш «усі платежі за сьогодні» — береш список `Payment[]`, кличеш на кожному `settle()`, і [поліморфізм](root:sf-lang/polymorphism) сам добере, чий метод виконати; тобі байдуже, який конкретний різновид у руці.

База даних цього фокусу не вміє. У [реляційній моделі](root:sf-data/relational-model) немає поняття «таблиця Y — різновид таблиці X»; [спадкування](root:sf-lang/inheritance) там відсутнє як сама ідея. Тож ієрархію доводиться сплющити в таблиці руками, і зробити це можна рівно трьома способами. Це не хтось вигадав на ходу: Мартін Фаулер назвав і розібрав усі три в «Patterns of Enterprise Application Architecture» (2002) — Single Table, Class Table, Concrete Table Inheritance, — а специфікація JPA потім вкарбувала їх у анотацію `@Inheritance` як `SINGLE_TABLE`, `JOINED` і `TABLE_PER_CLASS`. Показова дрібниця: перші дві будь-який JPA-рушій зобов'язаний підтримувати, а третя — необов'язкова. Уже з цього видно, котра з трьох найдужче свариться з реляційною моделлю.

Розберімо кожну на тому самому прикладі: робоча схема, мапер, що кладе об'єкт у рядок і піднімає назад у правильний підтип, поліморфний запит «усі платежі» з чесно порахованою ціною — і пастки, яких не видно, доки не наступиш.

Спершу — об'єктний бік, спільний для всіх трьох. Гроші тримаємо парою «сума в найдрібнішій одиниці + валюта», щоб не тягти сюди ще й окремий тип грошей:

:::tabs
```ts
class Money { constructor(readonly cents: number, readonly ccy: string) {} }

abstract class Payment {
  constructor(readonly id: number, readonly amount: Money, readonly createdAt: Date) {}
  abstract settle(): void;
}
class CardPayment extends Payment {
  constructor(id: number, amount: Money, createdAt: Date,
              readonly cardLast4: string, readonly authCode: string) {
    super(id, amount, createdAt);
  }
  settle() { /* провести через платіжний шлюз */ }
}
class BankTransfer extends Payment {
  constructor(id: number, amount: Money, createdAt: Date,
              readonly iban: string, readonly reference: string) {
    super(id, amount, createdAt);
  }
  settle() { /* звірити з банківською випискою */ }
}
```
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Money:
    cents: int
    ccy: str

@dataclass(frozen=True)
class Payment:
    id: int
    amount: Money
    created_at: datetime
    def settle(self) -> None: ...

@dataclass(frozen=True)
class CardPayment(Payment):
    card_last4: str
    auth_code: str
    def settle(self) -> None: ...      # провести через платіжний шлюз

@dataclass(frozen=True)
class BankTransfer(Payment):
    iban: str
    reference: str
    def settle(self) -> None: ...      # звірити з банківською випискою
```
:::

Об'єктна форма однакова завжди. Розходяться три способи в тому, у скільки таблиць і як саме її розкласти.

![Три схеми однієї ієрархії. Угорі одна широка таблиця payments з колонкою-розрізнювачем kind і колонками всіх підтипів підряд, де карткові поля порожні в банківських рядках і навпаки. Посередині корінь payments зі спільними колонками і дві підтаблиці card_payments та bank_transfers, чий первинний ключ є зовнішнім ключем на корінь. Унизу дві самодостатні таблиці зі спільними колонками, дубльованими в кожній, і без жодної кореневої таблиці payments — тож зовнішньому ключу на «будь-який платіж» нема на що показати](img/inherit-shapes.svg)

*Три форми однієї ієрархії Payment ← CardPayment, BankTransfer. Одна широка таблиця з розрізнювачем; корінь плюс листки, зшиті спільним id; або дві самодостатні таблиці без кореня — і тоді зовнішньому ключу на «платіж» нема на що показати.*

## Одна таблиця на всю ієрархію

**Ідея.** Всю ієрархію — в одну таблицю. Одна колонка-**розрізнювач** (англ. *discriminator*) каже, який різновид у цьому рядку; далі йдуть спільні колонки, а за ними — колонки геть усіх підтипів підряд. Рядок картки заповнює свої колонки, а «чужі» (банківські) лишає порожніми, і навпаки.

```sql
CREATE TABLE payments (
  id           BIGINT      PRIMARY KEY,
  kind         VARCHAR(16) NOT NULL,          -- розрізнювач: 'card' | 'bank'
  amount_cents BIGINT      NOT NULL,
  currency     CHAR(3)     NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL,
  -- поля CardPayment (NULL у банківських рядках)
  card_last4   CHAR(4),
  auth_code    VARCHAR(32),
  -- поля BankTransfer (NULL у карткових рядках)
  iban         VARCHAR(34),
  reference    VARCHAR(64),
  CHECK (kind IN ('card', 'bank'))
);
```

Мапер простий, і вся його суть — у розгалуженні за `kind`. Прочитавши рядок, він дивиться на розрізнювач і будує потрібний підтип:

:::tabs
```ts
type Row = {
  id: number; kind: 'card' | 'bank'; amount_cents: number; currency: string;
  created_at: string; card_last4: string | null; auth_code: string | null;
  iban: string | null; reference: string | null;
};

function fromRow(r: Row): Payment {
  const amount = new Money(r.amount_cents, r.currency);
  const at = new Date(r.created_at);
  switch (r.kind) {
    case 'card': return new CardPayment(r.id, amount, at, r.card_last4!, r.auth_code!);
    case 'bank': return new BankTransfer(r.id, amount, at, r.iban!, r.reference!);
  }
}
```
```python
def from_row(r: dict) -> Payment:
    amount = Money(r["amount_cents"], r["currency"])
    at = r["created_at"]
    if r["kind"] == "card":
        return CardPayment(r["id"], amount, at, r["card_last4"], r["auth_code"])
    if r["kind"] == "bank":
        return BankTransfer(r["id"], amount, at, r["iban"], r["reference"])
    raise ValueError(f"невідомий різновид платежу: {r['kind']!r}")
```
:::

Ті знаки оклику в TypeScript — `r.card_last4!` — не косметика. Тип каже, що колонка `string | null`, бо в банківських рядках вона таки NULL. Ти ж, знаючи `kind === 'card'`, стверджуєш: «тут не NULL». Компілятор цього довести не може — і саме тому мусиш присягнутися за нього. Ця присяга — перший симптом того, що зараз опишу.

**Поліморфний запит.** Ось де ця стратегія блищить. «Усі платежі» — це буквально одна таблиця:

```sql
SELECT * FROM payments ORDER BY created_at DESC;
```

Нуль `JOIN`, один прохід по одній таблиці. Дешевше не буває — і читання одного платежу за `id` так само коштує нуль з'єднань. Якщо застосунок здебільшого питає «дай усі платежі впереміш», кращого за це немає.

**Пастки.** За дешевину читання платиш цілісністю. `card_last4` не можна оголосити `NOT NULL`: банківські рядки законно тримають там NULL, і рушій відхилив би вставку. Отже, правило «у картки МУСЯТЬ бути останні цифри» база більше не стереже — воно випало зі схеми. Повернути його можна лише умовним обмеженням, прив'язаним до розрізнювача:

```sql
ALTER TABLE payments ADD CONSTRAINT card_fields_present
  CHECK (kind <> 'card' OR (card_last4 IS NOT NULL AND auth_code IS NOT NULL));
ALTER TABLE payments ADD CONSTRAINT bank_fields_present
  CHECK (kind <> 'bank' OR (iban IS NOT NULL AND reference IS NOT NULL));
```

Читається як «якщо це картка, то поля картки не NULL». Працює — але це вже не проста колонка `NOT NULL`, а окреме правило на кожен підтип, яке легко забути дописати. І що більше різновидів, то ширша таблиця з дедалі більшою часткою порожнеч: десять підтипів по три поля — і кожен рядок несе під тридцять здебільшого NULL-колонок.

Розрізнювач `kind` — теж вразливе місце. Він несе на собі всю логіку відновлення типу, тож NULL або друкарська помилка в ньому — і мапер не знає, що будувати. Тому він обов'язково `NOT NULL` і під `CHECK`-списком дозволених значень; інакше одного кривого рядка досить, щоб завалити читання всієї таблиці.

## Таблиця на клас: збірка через JOIN

**Ідея.** Дати кожному класу ієрархії власну таблицю. Спільне (`id`, сума, дата) живе в кореневій `payments`; кожен підтип — окрема таблиця тільки зі своїми полями, і її первинний ключ водночас є зовнішнім ключем на корінь. Один платіж — це рядок у базовій таблиці плюс рядок в одній підтабличній, склеєні спільним `id`.

```sql
CREATE TABLE payments (                        -- спільний корінь
  id           BIGINT      PRIMARY KEY,
  kind         VARCHAR(16) NOT NULL,
  amount_cents BIGINT      NOT NULL,
  currency     CHAR(3)     NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL,
  CHECK (kind IN ('card', 'bank'))
);
CREATE TABLE card_payments (
  id         BIGINT      PRIMARY KEY REFERENCES payments(id) ON DELETE CASCADE,
  card_last4 CHAR(4)     NOT NULL,              -- NOT NULL повернувся!
  auth_code  VARCHAR(32) NOT NULL
);
CREATE TABLE bank_transfers (
  id        BIGINT      PRIMARY KEY REFERENCES payments(id) ON DELETE CASCADE,
  iban      VARCHAR(34) NOT NULL,
  reference VARCHAR(64) NOT NULL
);
```

Одразу видно виграш: `card_last4 NOT NULL` тепер законне, бо в цій таблиці немає жодного банківського рядка, якому та колонка була б чужа. Цілісність, що випала в попередній схемі, повернулася сама собою.

Запис коштує двох вставок — у базу й у підтаблицю, — і робити їх треба разом: якщо друга впаде, перша має відкотитися, інакше в базі лишиться «платіж без різновиду». Тому обидві йдуть однією [транзакцією](root:sf-data/transactions-acid):

:::tabs
```ts
async function insert(p: Payment, tx: Tx): Promise<void> {
  const kind = p instanceof CardPayment ? 'card' : 'bank';
  await tx.query(
    `INSERT INTO payments(id, kind, amount_cents, currency, created_at)
     VALUES ($1, $2, $3, $4, $5)`,
    [p.id, kind, p.amount.cents, p.amount.ccy, p.createdAt]);
  if (p instanceof CardPayment)
    await tx.query(
      `INSERT INTO card_payments(id, card_last4, auth_code) VALUES ($1, $2, $3)`,
      [p.id, p.cardLast4, p.authCode]);
  else if (p instanceof BankTransfer)
    await tx.query(
      `INSERT INTO bank_transfers(id, iban, reference) VALUES ($1, $2, $3)`,
      [p.id, p.iban, p.reference]);
}
```
```python
def insert(p: Payment, tx) -> None:
    kind = "card" if isinstance(p, CardPayment) else "bank"
    tx.execute(
        "INSERT INTO payments(id, kind, amount_cents, currency, created_at)"
        " VALUES (%s, %s, %s, %s, %s)",
        (p.id, kind, p.amount.cents, p.amount.ccy, p.created_at))
    if isinstance(p, CardPayment):
        tx.execute(
            "INSERT INTO card_payments(id, card_last4, auth_code) VALUES (%s, %s, %s)",
            (p.id, p.card_last4, p.auth_code))
    elif isinstance(p, BankTransfer):
        tx.execute(
            "INSERT INTO bank_transfers(id, iban, reference) VALUES (%s, %s, %s)",
            (p.id, p.iban, p.reference))
```
:::

**Поліморфний запит.** А ось де по рахунку. Щоб зібрати «усі платежі» повними об'єктами, спільна таблиця має знайти кожному рядкові його підтабличну половину. Способів два. Перший — один запит із `LEFT JOIN` до кожної підтаблиці:

```sql
SELECT p.id, p.kind, p.amount_cents, p.currency, p.created_at,
       c.card_last4, c.auth_code,
       b.iban, b.reference
FROM payments p
LEFT JOIN card_payments  c ON c.id = p.id
LEFT JOIN bank_transfers b ON b.id = p.id
ORDER BY p.created_at DESC;
```

Ціна прямо пропорційна числу підтипів: два різновиди — два `LEFT JOIN`, десять — десять з'єднань в одному операторі, і планувальник мусить зіставити базу з кожною підтабличкою. Кумедний поворот: NULL, від яких ми втекли у сховищі, повертаються в **результаті** — у кожному рядку половина підтабличних колонок порожня (банківському рядку нема чого класти в `card_last4`). Різниця в тому, що це NULL лише у відповіді на запит, а не в самій таблиці, тож `NOT NULL` там і далі чинний.

Другий спосіб — одним запитом узяти базу, а тоді догрузити підтипи пакетами: по одному дозапиту `WHERE id IN (…)` на кожну підтаблицю. Для двох різновидів це база + два дозапити. Саме так часто чинять ORM. Але зробиш це наївно — «на кожен базовий рядок окремо сходи по його підтип» — і отримаєш класичну зливу дрібних запитів (ту саму хворобу N+1); з'єднання чи пакетний дозапит існують якраз, щоб її уникнути.

**Пастки.** Головна — розподіл спільного `id`. Він мусить бути унікальним на всю ієрархію (два платежі не можуть мати `id = 5`, хай навіть різних різновидів), і видають його в базовій таблиці; підтаблиця лише переймає вже наявний. Тому й порядок вставок жорсткий: спершу база — там народжується `id`, — потім підтип. Забудеш транзакцію — і збій між двома вставками лишить у `payments` рядок-сироту, який твердить, що він платіж, але жодна підтаблиця його не визнає.

Друга пастка — сам факт, що схема цю сироту **дозволяє**. Правило «кожен рядок `payments` має рівно один відповідник у якійсь підтаблиці» реляційними засобами не виражається: зовнішній ключ дивиться від підтипу до бази, а не навпаки, тож база не змусить підтип існувати. Ловити напівпорожні ієрархії доводиться тригерами чи відкладеними перевірками — або мовчки терпіти.

Натомість те, що в одній таблиці було болем, тут — сила: зовнішній ключ на «будь-який платіж» ставиться природно. Таблиця повернень пише `payment_id BIGINT REFERENCES payments(id)`, і рушій стереже, що повернення не показує в порожнечу. Є на що послатися — бо є таблиця самого абстрактного поняття.

## Таблиця на конкретний клас: збірка через UNION

**Ідея.** Довести роздрібнення до кінця: таблиця на кожен *конкретний* різновид, і жодної спільної. `card_payments` і `bank_transfers` самодостатні — кожна містить і спільні колонки (сума, дата), і свої. Таблиці `payments` немає взагалі: абстрактний `Payment` живе поняттям лише в коді, а в схемі йому нічого не відповідає.

```sql
CREATE TABLE card_payments (
  id           BIGINT      PRIMARY KEY,
  amount_cents BIGINT      NOT NULL,           -- спільні колонки —
  currency     CHAR(3)     NOT NULL,           --   дубльовані в обох
  created_at   TIMESTAMPTZ NOT NULL,           --   таблицях
  card_last4   CHAR(4)     NOT NULL,
  auth_code    VARCHAR(32) NOT NULL
);
CREATE TABLE bank_transfers (
  id           BIGINT      PRIMARY KEY,
  amount_cents BIGINT      NOT NULL,
  currency     CHAR(3)     NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL,
  iban         VARCHAR(34) NOT NULL,
  reference    VARCHAR(64) NOT NULL
);
```

Мапер тут найпростіший: кожен різновид лягає у власну таблицю цілком, без розрізнювача й без з'єднань. Читання одного карткового платежу — `SELECT * FROM card_payments WHERE id = $1`, і ти вже знаєш його тип із самої назви таблиці. `NOT NULL` доступний на всьому — таблиця однорідна.

**Поліморфний запит.** Ось тут ховається вся ціна. «Усі платежі» більше нема звідки взяти однією таблицею — доводиться зшивати всі конкретні таблиці через `UNION`:

```sql
SELECT id, amount_cents, currency, created_at, 'card' AS kind FROM card_payments
UNION ALL
SELECT id, amount_cents, currency, created_at, 'bank' AS kind FROM bank_transfers
ORDER BY created_at DESC;
```

Два різновиди — `UNION` з двох гілок; кожна гілка — окремий прохід по своїй таблиці. Розрізнювача в схемі немає, тож його доводиться **вигадати на льоту** — рядковий літерал `'card'`/`'bank'`, щоб мапер знову міг розібрати, що будувати. Беремо `UNION ALL`, а не `UNION`: звичайний `UNION` ще й прибирає дублікати сортуванням, а дублікатів тут бути не може (ідентифікатори унікальні між таблицями), тож дедуплікація — чиста марна робота.

Помітно, що цей запит повертає лише спільні колонки. Захочеш у тому самому списку ще й поля підтипів — кожна гілка мусить видати однакову кількість колонок в однаковому порядку, а «чужі» забити типізованими заглушками:

```sql
SELECT id, amount_cents, currency, created_at, 'card' AS kind,
       card_last4, auth_code, NULL::varchar AS iban, NULL::varchar AS reference
FROM card_payments
UNION ALL
SELECT id, amount_cents, currency, created_at, 'bank' AS kind,
       NULL::char(4), NULL::varchar, iban, reference
FROM bank_transfers;
```

І тут вилазить пастка `UNION`: гілки зшиваються лише за точним збігом кількості, порядку й сумісності типів колонок. Порожню заглушку доводиться прямо приводити до типу (`NULL::varchar`), бо голий `NULL` рушій вважає за `text`, і якщо у відповідній гілці колонка іншого типу, дістанеш `UNION types … cannot be matched`. Переплутаєш порядок — і `iban` мовчки ляже під колонку `card_last4`, бо `UNION` зіставляє за позицією, а не за назвою: помилки немає, дані поїхали.

**Пастки.** Найгостріша — та, що видно вже зі схеми: зовнішнього ключа на «будь-який платіж» поставити нема на що. Таблиці `payments` не існує, тож колонка `refunds.payment_id` не має цілі для `REFERENCES` — вона могла б показувати то в `card_payments`, то в `bank_transfers`, а зовнішній ключ націлюється рівно на одну таблицю. Цілісність посилання на абстрактний тип на рівні схеми недосяжна; лишається стерегти її кодом, що завжди слабше. Це найчастіша причина, чому цю стратегію відкидають: щойно на платіж хтось посилається — а на нього посилаються завжди, — вона починає текти.

Друга пастка — той самий унікальний `id`, але тепер без спільної таблиці, яка його роздавала. Наївний власний автолічильник у кожній таблиці окремо дасть `card_payments.id = 1` і `bank_transfers.id = 1` — два різні платежі з однаковим номером, і поліморфний список їх сплутає. Тож ідентифікатори треба брати зі **спільного джерела** — однієї послідовності на всі таблиці або UUID:

```sql
CREATE SEQUENCE payment_id_seq;
-- обидві таблиці черпають id з ОДНІЄЇ послідовності:
ALTER TABLE card_payments  ALTER COLUMN id SET DEFAULT nextval('payment_id_seq');
ALTER TABLE bank_transfers ALTER COLUMN id SET DEFAULT nextval('payment_id_seq');
```

Третя пастка — дублювання спільного. Колонки `amount_cents`, `currency`, `created_at` живуть у кожній таблиці своєю копією. Додати спільне поле (скажімо, `refunded_at`) — виправити КОЖНУ таблицю; зміниться правило для суми — правити його скрізь. А сам поліморфний `UNION` треба переписувати щоразу, як з'являється новий різновид: забудеш дописати гілку — і новий тип тихо випаде з «усіх платежів».

![Матриця: три стратегії (стовпці) проти семи вимірів (рядки) — усі платежі, один платіж, запис, NOT NULL на полях підтипу, зовнішній ключ на будь-який платіж, нова гілка чи спільна колонка, місце на диску. Клітини пофарбовані: зелене — виграш, жовте — помірна плата, червоне — програш. Одна таблиця виграє на читанні, але червона на NOT NULL. Таблиця на клас зелена на цілісності, жовта на вартості збірки. Конкретна таблиця червона на зовнішньому ключі та на новій гілці. Жодного суцільно зеленого стовпця немає](img/inherit-tradeoffs.svg)

*Та сама задача, три ціни в різних місцях. Зелене — де стратегія виграє, червоне — де програє, жовте — помірна плата. Суцільно зеленого стовпця немає й не буде: кожна щось віддає за те, що бере.*

## Що коли обирати

Тепер видно, що жодна стратегія не «правильна» — кожна ставить ціну в різне місце, і вибір диктує те, що для твоєї задачі найдорожче.

**Одна таблиця** — типовий і чесний вибір за замовчуванням. Бери її, коли ієрархія неглибока, полів у підтипів небагато, а головний запит — «усі платежі впереміш»: він виходить найдешевший з можливих, нуль з'єднань. Плата — розхитана цілісність (`NOT NULL` лише через `CHECK`) і ширшання таблиці з NULL; поки підтипів мало, ця плата дрібна. Недарма саме `SINGLE_TABLE` — стратегія за замовчуванням у JPA.

**Таблиця на клас** — коли цілісність дорожча за швидкість читання. Багато полів у підтипів, потрібні справжні `NOT NULL` і зовнішній ключ на «будь-який платіж» — бери її й плати з'єднаннями на кожну поліморфну збірку та двома вставками в транзакції на запис. Це найохайніша щодо цілісності стратегія; її обирають, коли схему бережуть суворо.

**Таблиця на конкретний клас** — рідкісний і вузький випадок. Вона виправдана, лише коли різновиди майже ніколи не питають разом, ніхто не посилається на абстрактний платіж зовнішнім ключем, а кожен підтип живе окремим життям. Щойно з'являється потреба в поліморфному запиті чи в посиланні на «будь-який платіж» — `UNION` по всіх таблицях і неможливість зовнішнього ключа роблять її найдорожчою. Не випадково саме `TABLE_PER_CLASS` специфікація JPA лишила необов'язковою: вона найдалі відходить від того, що реляційна модель уміє робити добре.

Спільний висновок один: перш ніж вибирати, спитай не «яка стратегія найкраща», а «який запит у мене найгарячіший і яку цілісність я не готовий втратити». Відповідь на це майже завжди називає стратегію сама.
