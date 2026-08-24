# ⚙️ Розплутати клас: від захованих смиків до чесного конструктора

Порада «тягни залежності конструктором» вимовляється за секунду, а виконується місяцями. Бо в живому застосунку клас, який смикає служби з глобала, ніколи не стоїть сам: його створюють у сорока місцях, половина з них — чужі, на нього спираються тести, які самі готують той глобал, а всередині він майструє інші класи, що смикають так само. Переписати це одним рухом не вийде — а якщо вийде, то це вже не рефакторинг, а [переписування](book:programming/rewrite-vs-refactor) з усіма його ризиками.

Отже, задача формулюється точно. Є клас `OrderService`, що бере служби з `Locator`. Треба довести його до стану, коли всі залежності стоять у сигнатурі конструктора, а слова `Locator` у файлі немає. Умови: застосунок мусить збиратися після **кожного** кроку, тести мусять бути зелені після **кожного** кроку, і кожен крок мусить їхати окремим комітом, який не страшно злити в п'ятницю ввечері.

## Ідея: смик не зникає — він переїжджає

Уся хитрість в одному спостереженні. Смик не можна «прибрати» — залежність-бо справжня, вона нікуди не дінеться. Але його можна **пересунути на один крок назовні**, і так кілька разів поспіль:

```
тіло методу → конструктор → типове значення параметра → композиційний корінь → нема
```

Кожна стрілка тут — окрема, дрібна, зворотно-сумісна правка. Смик лишається смиком доти, доки не доїде до кореня, де він перестає бути смиком і стає звичайним створенням об'єкта. Саме тому процедура безпечна: ти ніколи не робиш стрибка «було глобально — стало впорснуто», ти щоразу пересуваєш ту саму залежність на один сантиметр ближче до виходу.

![Чотири стани того самого класу зліва направо: смики розсипані по тілу методів при порожньому конструкторі; ті самі смики зібрані в конструктор; конструктор із типовими значеннями, де смик лишився запасним ходом, а композиційний корінь уже подає залежності ззовні; чесний конструктор із повним списком параметрів, локатора вже нема](img/untangle-arc.svg)

*Той самий клас у чотири моменти рефакторингу. Смик не зникає раптом: він переїжджає з тіла в конструктор, звідти в типове значення параметра, і аж тоді — геть, у корінь. Між станами застосунок збирається, а тести зелені, тому кожен переїзд їде своїм комітом.*

Далі — сама процедура, крок за кроком, на живому вузлі.

## Крок 1. З'ясувати справжній список

Починати доводиться з розвідки, і причина в цьому одна: **конструктор бреше**, а отже, список залежностей класу ніде не записаний. Його нема ні в сигнатурі, ні в імпортах — він розмазаний по тілу. Поки ти його не знаєш, планувати нема чого.

Ось вузол, який дістався у спадок:

:::tabs
```ts
class ReceiptBuilder {
  build(order: Order, chargeId: string): string {
    const t = Locator.get<TemplateStore>("templates");     // смик усередині дитини
    return t.render("receipt", { order: order.id, charge: chargeId });
  }
}

class OrderService {
  checkout(order: Order): string {
    const gateway = Locator.get<PaymentGateway>("gateway");   // смик 1
    const clock = Locator.get<Clock>("clock");                // смик 2
    const chargeId = gateway.charge(order.total());
    const receipt = new ReceiptBuilder().build(order, chargeId);
    this.audit(order, chargeId, clock);
    return receipt;
  }
  private audit(order: Order, chargeId: string, clock: Clock): void {
    Locator.get<AuditLog>("audit")                             // смик 3, у надрах
      .write(`${clock.now()} order=${order.id} charge=${chargeId}`);
  }
}
```
```py
class ReceiptBuilder:
    def build(self, order, charge_id):
        templates = Locator.get("templates")          # смик усередині дитини
        return templates.render("receipt", order=order.id, charge=charge_id)


class OrderService:
    def checkout(self, order):
        gateway = Locator.get("gateway")              # смик 1
        clock = Locator.get("clock")                  # смик 2
        charge_id = gateway.charge(order.total())
        receipt = ReceiptBuilder().build(order, charge_id)
        self._audit(order, charge_id, clock)
        return receipt

    def _audit(self, order, charge_id, clock):
        log = Locator.get("audit")                    # смик 3, у надрах
        log.write(f"{clock.now()} order={order.id} charge={charge_id}")
```
:::

Читати такий клас очима — марна праця: у справжньому проєкті це не двадцять рядків, а двісті, і смик ховається в приватному методі, який кличе інший приватний метод. Але робота ця механічна, тож її робить [статичний аналіз](book:programming/static-analysis) — тридцять рядків на стандартному `ast`, без жодної бібліотеки:

```py
# pulls.py — інвентаризація смиків: хто з локатора що бере
import ast, os, sys, collections

def pulls_in(path):
    """(клас, метод, ключ, рядок) для кожного Locator.get(...) у файлі."""
    tree = ast.parse(open(path, encoding='utf-8').read(), path)
    found = []
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        for fn in [n for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)]:
            for call in [n for n in ast.walk(fn) if isinstance(n, ast.Call)]:
                f = call.func
                if isinstance(f, ast.Attribute) and f.attr == 'get' \
                   and isinstance(f.value, ast.Name) and f.value.id == 'Locator':
                    arg = call.args[0] if call.args else None
                    key = arg.value if isinstance(arg, ast.Constant) else '<ОБЧИСЛЕНИЙ>'
                    found.append((cls.name, fn.name, key, call.lineno))
    return found

def scan(root):
    out = collections.defaultdict(list)
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if fname.endswith('.py'):
                p = os.path.join(dirpath, fname)
                for cls, fn, key, ln in pulls_in(p):
                    out[cls].append((fn, key, os.path.basename(p), ln))
    return out

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')          # щоб «→» не спіткнувся на консолі
    for cls, rows in sorted(scan(sys.argv[1]).items()):
        print(f"{cls}: справжній список залежностей = {sorted({k for _, k, _, _ in rows})}")
        for fn, key, f, ln in rows:
            print(f"    {f}:{ln}  {fn}()  →  '{key}'")
```

На нашому вузлі він друкує те, чого не видно в жодній сигнатурі:

```
OrderService: справжній список залежностей = ['audit', 'clock', 'gateway']
    orders.py:11  checkout()  →  'gateway'
    orders.py:12  checkout()  →  'clock'
    orders.py:18  _audit()  →  'audit'
ReceiptBuilder: справжній список залежностей = ['templates']
    orders.py:6  build()  →  'templates'
```

Придивися до цього виводу уважно, бо він каже більше, ніж здається. `OrderService` показує три ключі — але це його **власні** смики. Четверта залежність, `templates`, у нього теж є, тільки живе вона поверхом нижче: `OrderService` майструє `ReceiptBuilder`, а той смикає шаблони. Тобто справжній список верхнього класу — це не рядок таблиці, а **сума по всьому піддереву**, яке він створює. Ця дрібниця вирішить далі порядок роботи.

> 🔧 **Навіщо це.** Інвентаризація — не бюрократія, а єдиний спосіб оцінити роботу до того, як у неї вліз. Таблиця смиків одразу каже три речі: скільки залежностей насправді має клас (і чи не забагато — вісім ключів у списку означають, що розплутувати треба не смики, а [сам клас](book:programming/single-responsibility)), де вони сидять (смик у приватному методі переїде важче за смик у `checkout`) і які класи тягнуться слідом. Без таблиці ти оцінюєш рефакторинг на око й помиляєшся втричі.

## Крок 2. Сітка безпеки — тест-зліпок

Перед тим як рухати бодай рядок, треба мати чим ловити падіння. І тут є халепа, гідна уваги: **клас не тестується — саме тому ми його й чіпаємо**. Замкнене коло.

Розмикається воно неприємно, зате чесно: перший тест пишуть **з локатором**, а не проти нього. Ти тимчасово приймаєш правила гри — готуєш глобальний реєстр, підсовуєш підробки, викликаєш метод і записуєш у тест те, що він **насправді** робить сьогодні:

:::tabs
```ts
function fill(): { gw: FakeGateway; log: FakeLog } {
  const gw = new FakeGateway(), log = new FakeLog();
  Locator.reset();
  Locator.register("gateway", gw);
  Locator.register("clock", new FakeClock());
  Locator.register("audit", log);
  Locator.register("templates", new TemplateStore());
  return { gw, log };
}

test("checkout — зліпок сьогоднішньої поведінки", () => {
  const { gw, log } = fill();
  const receipt = new OrderService().checkout(new Order("A-1", 1999));
  expect(receipt).toBe("[receipt] charge=ch_1 order=A-1");
  expect(gw.charges).toEqual([1999]);
  expect(log.lines).toEqual(["2026-07-16T10:00:00Z order=A-1 charge=ch_1"]);
});
```
```py
def fill():
    gw, log = FakeGateway(), FakeLog()
    Locator.reset()
    Locator.register("gateway", gw)
    Locator.register("clock", FakeClock())
    Locator.register("audit", log)
    Locator.register("templates", TemplateStore())
    return gw, log


def test_checkout_characterization():        # зліпок сьогоднішньої поведінки
    gw, log = fill()
    receipt = OrderService().checkout(Order("A-1", 1999))
    assert receipt == "[receipt] charge=ch_1 order=A-1"
    assert gw.charges == [1999]
    assert log.lines == ["2026-07-16T10:00:00Z order=A-1 charge=ch_1"]
```
:::

Це **тест-зліпок** (characterization test) — термін і прийом Майкла Фезерса з «Working Effectively with Legacy Code» (Prentice Hall, 2004; усталений факт). Суть у назві: він не описує, як має бути, — він знімає зліпок із того, як **є**, разом із дивацтвами й вадами. Якщо `checkout` сьогодні пише в журнал криво — записуй криво. Твоє завдання зараз не полагодити поведінку, а **прибити її цвяхом**, щоб під час переїзду смиків будь-яка зміна одразу закричала. Полагодиш потім, окремим комітом, коли клас уже буде під тестами.

Тест цей потворний: він знає про глобал, готує його й прибирає за собою. Так і має бути — це риштування, і воно приречене. Наприкінці рецепту ти його викинеш і перепишеш начисто, бо клас нарешті прийматиме підробки крізь парадні двері. А поки що це єдина сітка, яка в тебе є.

## Крок 3. Зібрати смики докупи

Тепер перша справжня правка — і навмисно найдрібніша з можливих. Смики не чіпаємо по суті, а лише **зсуваємо в одне місце й один момент**: із тіл методів у конструктор.

:::tabs
```ts
class OrderService {
  private gateway = Locator.get<PaymentGateway>("gateway");
  private clock = Locator.get<Clock>("clock");
  private log = Locator.get<AuditLog>("audit");
  private receipts = new ReceiptBuilder();

  checkout(order: Order): string {
    const chargeId = this.gateway.charge(order.total());
    const receipt = this.receipts.build(order, chargeId);
    this.log.write(`${this.clock.now()} order=${order.id} charge=${chargeId}`);
    return receipt;
  }
}
```
```py
class OrderService:
    def __init__(self):
        self._gateway = Locator.get("gateway")
        self._clock = Locator.get("clock")
        self._log = Locator.get("audit")
        self._receipts = ReceiptBuilder()

    def checkout(self, order):
        charge_id = self._gateway.charge(order.total())
        receipt = self._receipts.build(order, charge_id)
        self._log.write(f"{self._clock.now()} order={order.id} charge={charge_id}")
        return receipt
```
:::

Зовні виграш ніби копійчаний: смиків стільки ж, глобал на місці, тест-зліпок зелений і навіть не помітив правки. Але вигода тут не в кількості, а в **геометрії**. По-перше, тепер усі залежності класу зібрані в одному вікні екрана — конструктор нарешті каже правду, хай і пошепки. По-друге — і це головне — смик тепер стається **раз, при народженні**, а не щоразу посеред виклику. А раз він відбувається в конструкторі, то це вже майже параметр: між `Locator.get("gateway")` у конструкторі й `gateway` у його сигнатурі лишився один крок.

Одна засторога, яку варто зробити свідомо: цим переїздом ти міняєш **момент** смику. Раніше служба бралася під час виклику `checkout`, тепер — під час `new OrderService()`. Якщо десь у коді хтось створює сервіс до того, як реєстр наповнили, він упаде — і впаде раніше, ніж падав досі. Це майже завжди на краще (збій переїхав ближче до причини), але саме ця правка може підсвітити порядок запуску, про який ти не знав.

## Крок 4. Відчинити двері, не ламаючи стіни

Тепер найцікавіший хід усього рецепту. Конструктор має **почати приймати** залежності — але сорок місць, що кличуть `new OrderService()` без аргументів, мусять і далі працювати. Розв'язок — параметр із типовим значенням, у якому сидить старий смик:

:::tabs
```ts
class ReceiptBuilder {
  constructor(private templates: TemplateStore = Locator.get<TemplateStore>("templates")) {}

  build(order: Order, chargeId: string): string {
    return this.templates.render("receipt", { order: order.id, charge: chargeId });
  }
}

class OrderService {
  constructor(
    private gateway: PaymentGateway = Locator.get<PaymentGateway>("gateway"),
    private clock: Clock = Locator.get<Clock>("clock"),
    private log: AuditLog = Locator.get<AuditLog>("audit"),
    private receipts: ReceiptBuilder = new ReceiptBuilder(),
  ) {}

  checkout(order: Order): string {
    const chargeId = this.gateway.charge(order.total());
    const receipt = this.receipts.build(order, chargeId);
    this.log.write(`${this.clock.now()} order=${order.id} charge=${chargeId}`);
    return receipt;
  }
}
```
```py
class ReceiptBuilder:
    def __init__(self, templates=None):
        # сентинел None, а НЕ typedefault=Locator.get(...) — чому, див. нижче
        self._templates = templates if templates is not None else Locator.get("templates")

    def build(self, order, charge_id):
        return self._templates.render("receipt", order=order.id, charge=charge_id)


class OrderService:
    def __init__(self, gateway=None, clock=None, log=None, receipts=None):
        self._gateway = gateway if gateway is not None else Locator.get("gateway")
        self._clock = clock if clock is not None else Locator.get("clock")
        self._log = log if log is not None else Locator.get("audit")
        self._receipts = receipts if receipts is not None else ReceiptBuilder()

    def checkout(self, order):
        charge_id = self._gateway.charge(order.total())
        receipt = self._receipts.build(order, charge_id)
        self._log.write(f"{self._clock.now()} order={order.id} charge={charge_id}")
        return receipt
```
:::

Клас щойно роздвоївся, і це навмисне. Старий виклик `new OrderService()` живий — типове значення тихо смикне з глобала, як і раніше. Новий виклик `new OrderService(gw, clock, log, receipts)` уже подає все ззовні й глобала не торкається зовсім. Тобто **шов з'явився, а жоден із сорока викликів не зламався** — і саме тому правку можна злити сьогодні, а мігрувати виклики хоч місяць.

І перше, що варто зробити з новими дверима, — переписати начисто той потворний тест-зліпок:

:::tabs
```ts
test("checkout — тепер без жодного глобала", () => {
  Locator.reset();                                  // реєстр порожній — і не потрібен
  const gw = new FakeGateway(), log = new FakeLog();
  const svc = new OrderService(gw, new FakeClock(), log,
                               new ReceiptBuilder(new TemplateStore()));
  expect(svc.checkout(new Order("A-1", 1999))).toBe("[receipt] charge=ch_1 order=A-1");
  expect(log.lines).toEqual(["2026-07-16T10:00:00Z order=A-1 charge=ch_1"]);
});
```
```py
def test_checkout_without_globals():             # тепер без жодного глобала
    Locator.reset()                              # реєстр порожній — і не потрібен
    gw, log = FakeGateway(), FakeLog()
    svc = OrderService(gw, FakeClock(), log, ReceiptBuilder(TemplateStore()))
    assert svc.checkout(Order("A-1", 1999)) == "[receipt] charge=ch_1 order=A-1"
    assert log.lines == ["2026-07-16T10:00:00Z order=A-1 charge=ch_1"]
```
:::

Різниця між цим тестом і зліпком із кроку 2 — і є вся вигода рефакторингу, стисла в кілька рядків. Ніякого `fill()`, ніякого прибирання за собою, ніякої війни паралельних тестів за спільний реєстр: усе, що потрібно класові, стоїть у виклику конструктора.

## Крок 5. Перенести виклики й забрати драбину

Двері відчинені — тепер треба провести крізь них сорок викликів. Робота нудна, зате безпечна: береш місце, де стоїть `new OrderService()`, і питаєш, звідки **там** узяти залежності. Відповідь майже завжди одна: не створювати їх на місці, а попросити на поверх вище — тобто повторити той самий хід із кроку 4 для класу-власника. Так рішення «саме Stripe» повзе вгору, від виклику до виклику, поки не впреться в `main`.

Коли останній виклик подає все явно, настає найприємніший коміт усього рецепту — **прибрати типове значення**:

:::tabs
```ts
class OrderService {
  constructor(
    private gateway: PaymentGateway,      // ніяких типових значень
    private clock: Clock,
    private log: AuditLog,
    private receipts: ReceiptBuilder,
  ) {}
  // ...
}
```
```py
class OrderService:
    def __init__(self, gateway, clock, log, receipts):   # ніяких None-заглушок
        self._gateway, self._clock = gateway, clock
        self._log, self._receipts = log, receipts
```
:::

Разом із типовим значенням із файлу зникає імпорт `Locator` — і це той момент, заради якого все затівалося. Компілятор тепер сам стереже: забув аргумент — не збереться. Конструктор перестав бути таємницею й став **описом**: чотири параметри — чотири залежності, більше нема чого шукати в тілі.

Драбину прибирають одразу після того, як злізли: поки типове значення стоїть, воно люб'язно рятує кожного, хто забув подати залежність, — а отже, тихо пускає смик назад. Пів року такої люб'язності, і в тебе знову сорок місць із `new OrderService()`.

## Крок 6. Листя першим

Лишилася четверта залежність — `templates`, що ховається під `ReceiptBuilder`. І тут порядок роботи вирішує все.

Спокуса така: почати згори, з головного класу, бо він важливіший. Спробуй — і застрягнеш. `OrderService` прийме свої три залежності й здаватиметься чесним, але всередині він і далі майструє `ReceiptBuilder`, а той далі смикає шаблони з глобала. Тест `OrderService` **усе одно** муситиме готувати реєстр. Батько не буває чесним, поки бреше дитина: його сигнатура — це обіцянка про **все піддерево**, а не про власний рядок коду.

![Вгорі спроба згори вниз: OrderService уже приймає три залежності й виглядає чесним, але створює всередині ReceiptBuilder, а той смикає templates із глобала, тож список залежностей батька все одно неповний. Внизу порядок від листя вгору: спершу чесним стає ReceiptBuilder, тоді потреба виринає в OrderService, а звідти піднімається в композиційний корінь, де все й створюють](img/leaf-first.svg)

*Згори вниз рефакторинг застрягає: батько вже приймає своє, а дитина всередині смикає далі — отже, сигнатура батька досі бреше, і тест досі мусить готувати глобал. Від листя вгору кожен крок завершений: листок стає чесним, його потреба виринає в батька, батькова — в корінь, де її нарешті створюють.*

Тому йдемо навпаки — **від листя**. Спершу чесним стає `ReceiptBuilder`, у якого залежність одна. Щойно це сталося, `OrderService` більше не може написати `new ReceiptBuilder()` — і його власна потреба спливає на видноту. Дивна річ трапляється на цьому кроці: список залежностей батька **тимчасово росте**, бо тепер він мусить десь узяти ще й `templates`. Це не регрес — це зчеплення, яке весь час було, просто ховалося за смиком дитини. Локатор його не прибирав, лише малював невидимим.

Далі, після інвентаризації, граф уже видно, і порядок складання читається з нього однозначно:

```
Залежності (з таблиці смиків):

  ReceiptBuilder ← templates
  OrderService   ← gateway, clock, audit, receipts

Топологічний порядок (листя першими):

  1. TemplateStore                    ← нічого не потребує
  2. ReceiptBuilder(TemplateStore)    ← шар 1
  3. StripeGateway, SystemClock, FileLog
  4. OrderService(3, ReceiptBuilder)  ← шари 1–3

Глибина ланцюга = 3 → стільки шарів створення буде в корені.
```

Якщо на цьому кроці батько роздувся до восьми параметрів, з яких половину він лише **передає далі**, не вживаючи сам, — це сигнал, а не привід страждати. Наскрізні аргументи означають, що клас складає чуже піддерево; тоді розумніше впровадити не п'ять залежностей `ReceiptBuilder`, а [фабрику](book:programming/factory-method) `ReceiptBuilderFactory`, яка вміє його зробити. Батько тримає одну залежність замість п'яти й нічого не знає про нутрощі дитини.

## Крок 7. Реєстр стає коренем

Тепер найкорисніша думка всього рефакторингу — і вона лишається непоміченою, якщо не сказати її вголос. Ось як виглядав файл реєстрації локатора:

:::tabs
```ts
// registry.ts — те, що виконувалося на старті застосунку
Locator.register("templates", new TemplateStore());
Locator.register("gateway", new StripeGateway(process.env.STRIPE_KEY!));
Locator.register("clock", new SystemClock());
Locator.register("audit", new FileLog("/var/log/orders.log"));
```
```py
# registry.py — те, що виконувалося на старті застосунку
Locator.register("templates", TemplateStore())
Locator.register("gateway", StripeGateway(os.environ["STRIPE_KEY"]))
Locator.register("clock", SystemClock())
Locator.register("audit", FileLog("/var/log/orders.log"))
```
:::

А ось композиційний корінь, що його замінює:

:::tabs
```ts
function main(): void {
  const templates = new TemplateStore();
  const gateway = new StripeGateway(process.env.STRIPE_KEY!);
  const clock = new SystemClock();
  const audit = new FileLog("/var/log/orders.log");
  const service = new OrderService(gateway, clock, audit, new ReceiptBuilder(templates));
  runApp(service);
}
```
```py
def main():
    templates = TemplateStore()
    gateway = StripeGateway(os.environ["STRIPE_KEY"])
    clock = SystemClock()
    audit = FileLog("/var/log/orders.log")
    service = OrderService(gateway, clock, audit, ReceiptBuilder(templates))
    run_app(service)
```
:::

Придивися: **це той самий список**. Ті самі чотири рядки створення, ті самі ключі з середовища, той самий порядок. Композиційний корінь не з'явився нізвідки — він увесь час був, під назвою «файл реєстрації», просто рішення в ньому не з'єднувалися одне з одним, а роз'їжджалися по глобальній таблиці, щоб зустрітися аж у рантаймі, за іменем-рядком.

Ось що ти насправді робив увесь цей час: не будував систему заново, а **підвищував реєстр у званні** — з пошуку за іменем під час роботи до звичайного складання під час запуску. Стрічка `Locator.register("gateway", …)` була обіцянкою «колись хтось попросить `"gateway"`, і я дам оце». Рядок `new OrderService(gateway, …)` — це та сама обіцянка, тільки виконана негайно, у видимому місці й під наглядом компілятора. Різниця між локатором і чесною збіркою — не в тому, **що** створюється, а в тому, **коли** й **чи видно**.

І ще одне: те, що корінь тепер довгий і нудний, — це нормально. Коли одноманітних рядків стає кількасот, їх доручають [контейнеру](book:programming/di-container), який обійде конструктори й складе граф сам. Але звертатися до контейнера є сенс аж тепер, коли конструктори чесні: контейнер уміє читати сигнатури, а не тіла методів. Розплутати смики — це передумова, без якої інструмент безсилий.

## Крок 8. Гейт від рецидиву

Останній крок — і без нього все попереднє протухне за квартал. Смик повертається природним шляхом: новачок побачить `Locator` у сусідньому файлі, скопіює рядок — і клас знову бреше. Тому останній коміт вішає замок:

```py
# test_no_locator.py — смик дозволено ЛИШЕ у складальних файлах
import ast, os, sys

ALLOWED = {"main.py", "composition_root.py"}     # тільки тут вільно смикати

def locator_users(root):
    bad = []
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if not fname.endswith(".py") or fname in ALLOWED:
                continue
            path = os.path.join(dirpath, fname)
            tree = ast.parse(open(path, encoding="utf-8").read(), path)
            for n in ast.walk(tree):
                if isinstance(n, ast.Attribute) and n.attr == "get" \
                   and isinstance(n.value, ast.Name) and n.value.id == "Locator":
                    bad.append(f"{fname}:{n.lineno}")
    return bad

def test_locator_lives_only_in_the_root():
    bad = locator_users("app")
    assert not bad, ("смик поза композиційним коренем: " + ", ".join(bad))
```

На вихідному вузлі він, як і належить, лається:

```
FAIL — смик поза композиційним коренем: dyn.py:7, dyn.py:9, orders.py:6, orders.py:11, orders.py:12, orders.py:18
```

а на розплутаному — мовчить. Зверни увагу на форму замка: він не забороняє локатор узагалі, а **прив'язує його до місця**. Це різниця між «так не можна» і «так можна ось тут» — перше правило обходять, друге пояснює, куди йти. Той самий гейт, до речі, стає твоїм лічильником прогресу посеред міграції: число в списку падає з кожним комітом, і видно, скільки лишилося.

## Складність і пастки

Рецепт вище виглядає рівним, і на дрібному класі він таким і буде. Але на живому коді він щоразу натикається на одні й ті самі місця, де здоровий глузд підводить.

**Типове значення в Python — не те, що в TypeScript.** Крок 4 в обох мовах виглядає однаково, а працює по-різному, і це коштує вечора налагодження. У TypeScript вираз типового значення обчислюється **при кожному виклику** — тому `= Locator.get("gateway")` у сигнатурі чесно смикає щоразу. У Python типове значення обчислюється **один раз, коли інтерпретатор читає `def`**, тобто на імпорті:

```py
Locator.register("rates", RateCache())      # кеш #1

class NaiveService:
    def __init__(self, rates=Locator.get("rates")):    # ← ПАСТКА
        self.rates = rates

Locator.register("rates", RateCache())      # перереєстрували на кеш #2
NaiveService().rates.id                     # → 1, а не 2
```

Смик застиг на кеші #1 назавжди — усі майбутні сервіси тримають об'єкт, який зареєстрували на мить імпорту. Гірше: якщо на момент імпорту модуля реєстр іще порожній, застосунок упаде **на імпорті**, і слід приведе не туди. Тому в Python двері відчиняють через сентинел `None`, як у коді кроку 4: `rates if rates is not None else Locator.get("rates")` — смик стається під час виклику, як і задумано. Той самий рядок, дві мови, протилежна семантика.

**Скільки екземплярів було насправді.** Локатор мовчки роздавав **один** об'єкт на ключ: усі, хто просив `"rates"`, діставали ту саму скриньку. Коли смик переїжджає, ця обіцянка ніде не записана — і найприродніша правка «хай кожен майструє собі» тихо роздвоює спільний об'єкт:

```
локатор: три сервіси → кеш-екземплярів 1 | записав сервіс 1 → сервіс 3 бачить 42
недбало: три сервіси → кеш-екземплярів 3 | записав сервіс 1 → сервіс 3 бачить None
корінь:  три сервіси → кеш-екземплярів 1 | записав сервіс 1 → сервіс 3 бачить 42
```

![Три колонки. Ліворуч: три сервіси смикають з локатора і всі дістають один спільний RateCache — запис одного бачать усі. Посередині: після недбалої правки кожен сервіс майструє власний кеш, їх стало три, і запис одного не бачить ніхто. Праворуч: композиційний корінь створює один кеш і подає його всім трьом — кількість відтворено свідомо](img/lifetime-count.svg)

*Кількість екземплярів була частиною поведінки — просто ніде не записаною. Локатор роздавав один об'єкт на ключ; «хай кожен створить собі» непомітно розсипає кеш, пул з'єднань чи лічильник на три окремі. Код збереться, тести пройдуть, а поведінка зміниться — тому перед правкою полічи, скільки їх було, і відтвори це число в корені свідомо.*

Це найпідступніша пастка всього рецепту, бо вона не падає. Компілятор мовчить, тести зелені, а в проді кеш перестає влучати, лічильник рахує втричі менше, а пул з'єднань відкриває втричі більше сокетів. Правило просте: **перед переїздом кожного ключа спитай, скільки екземплярів було**, і відтвори це число в корені навмисне — один об'єкт, створений раз і поданий усім трьом, або три різних, якщо так і було.

**Цикл, який локатор ховав.** Іноді на кроці 5 граф просто не збирається: щоб створити `Billing`, потрібен `Notifier`, а щоб створити `Notifier` — потрібен `Billing`. Під локатором ця пара роками жила щасливо, бо смик стається **під час виклику**, коли обидва вже створені порожніми. Конструкторам так не можна: складання графа — це топологічний порядок, а в циклі його не існує.

```
Billing  ← Notifier
Notifier ← Billing
→ цикл довжини 2; топологічного порядку не існує → зібрати нема як
```

![Ліворуч під локатором: Billing і Notifier смикають одне одного з глобала, смик стається аж під час виклику, коли обидва вже створені порожніми, тож цикл живий і невидимий. Праворуч конструкторами: щоб створити одного, треба вже мати другого, топологічного порядку не існує і граф не збирається взагалі. Внизу два виходи: розірвати цикл, витягши спільне третє, або типізований постачальник у сигнатурі](img/cycle-topo.svg)

*Локатор терпів цикл, бо відкладав смик до виклику — і тим ховав справжню ваду будови. Конструктор вимагає порядку й тому робить цикл видимим: граф не збереться, поки його не розірвано. Постачальник у сигнатурі — чесніший компроміс за смик, але це компроміс, а не перемога.*

Ось чому це добра новина, хоч і схожа на біду: рефакторинг щойно **довів**, що твій граф залежностей має цикл — а цикл двох служб майже завжди означає, що між ними живе третє поняття, яке ніхто не виділив. Тому головний вихід — розірвати: витягти спільне в окремий клас, або пустити зв'язок назустріч подією замість прямого виклику. Коли ж інакше ніяк, лишається вузол розв'язати постачальником:

:::tabs
```ts
class Billing {
  constructor(private notify: () => Notifier) {}          // залежність видно в сигнатурі
  charge(x: string): string { return "b:" + this.notify().fmt(x); }
}
```
```py
class Billing:
    def __init__(self, notify_provider):                   # залежність видно в сигнатурі
        self._notify = notify_provider

    def charge(self, x):
        return "b:" + self._notify().fmt(x)
```
:::

Різниця з локатором тонка, але справжня: `() => Notifier` **задекларовано в конструкторі** — його видно, він типізований, у тест його подають так само, як усе інше. Це не глобальний реєстр, куди можна попросити будь-що на ім'я, а одна названа відкладена залежність. Смик відкладає **все й для всіх**; постачальник відкладає **одне, назване, вкидане**.

**Ключ, склеєний у рантаймі.** Твій скан із кроку 1 чесно позначив кілька рядків як `<ОБЧИСЛЕНИЙ>` — і це не вада скану:

```py
Locator.get("gateway." + self.region)     # ключа "gateway.eu" в коді просто нема
```

Такий смик не знайде жоден пошук по тексту, бо шуканого рядка не існує до запуску. Отже, статичний список залежностей у загальному випадку **недосяжний** — і це, як не дивно, найточніший вирок локатору: якщо машина з повним доступом до коду не може перелічити залежності класу, то й людина, читаючи, не зможе. Ловиться це лише в русі — обгорткою-дротиною на самому `Locator.get`, яка перед поверненням служби пише в журнал ключ і місце виклику:

```py
seen = []
_orig = Locator.get.__func__

def traced(cls, key):
    import traceback
    fr = traceback.extract_stack()[-2]
    seen.append((key, f"{fr.name}:{fr.lineno}"))
    return _orig(cls, key)

Locator.get = classmethod(traced)
# → [('gateway.eu', 'pay:124'), ('gateway.us', 'pay:124')]
```

Практика така: після переїзду **не видаляй локатор одразу**. Лиши його зареєстрованим, обвішаним дротиною, і потримай так у проді тиждень-два. Журнал скаже те, чого не знав жоден скан: хто ще смикає, звідки і як часто. Порожній журнал за два тижні живого навантаження — оце і є справжній дозвіл натиснути `Delete`, а не твоя впевненість, що ти все знайшов.

**Ліниве проти охочого.** Локатор створював службу тоді, коли її вперше попросили; корінь створює все на старті. Для дешевих об'єктів це дрібниця, для тих, що відкривають з'єднання чи читають файл, — зміна поведінки: старт довшає, а застосунок, якому бракує ключа доступу, тепер падає на запуску, а не на першому платежі за три години. Майже завжди це виграш — краще впасти голосно й одразу, ніж тихо й потім. Але це саме **зміна**, і краще внести її свідомо, ніж дізнатися з чергування. Якщо ж якийсь вузол справді дорогий і рідко потрібен, його [створення відкладають](book:programming/lazy-loading) тим самим постачальником — знову ж таки, названим у сигнатурі.

## Де смик лишається — і це чесно

Наприкінці рецепту знайдеться клас, у якому смик не прибрати ніяк: його створює каркас, і подати туди нічого — конструктор диктує чужий код. Це не поразка, а межа, і рецепт має відповідь саме на неї.

:::tabs
```ts
// Каркас створює ЦЕЙ клас сам — тут смикнути можна, бо іншого входу нема
class CheckoutController {
  private core = new OrderService(              // єдиний смик — на самій межі
    Locator.get<PaymentGateway>("gateway"),
    Locator.get<Clock>("clock"),
    Locator.get<AuditLog>("audit"),
    new ReceiptBuilder(Locator.get<TemplateStore>("templates")),
  );

  handle(req: Request): Response {
    return ok(this.core.checkout(toOrder(req)));   // уся логіка — у чесному ядрі
  }
}
```
```py
# Каркас створює ЦЕЙ клас сам — тут смикнути можна, бо іншого входу нема
class CheckoutController:
    def __init__(self):
        self._core = OrderService(                 # єдиний смик — на самій межі
            Locator.get("gateway"),
            Locator.get("clock"),
            Locator.get("audit"),
            ReceiptBuilder(Locator.get("templates")),
        )

    def handle(self, req):
        return ok(self._core.checkout(to_order(req)))   # уся логіка — у чесному ядрі
```
:::

Контролер тут — тонкий перехідник: він смикає **один раз, на межі**, збирає чесне ядро й одразу віддає йому роботу. Усередині `OrderService` жодного локатора немає, тестується він конструктором, і про існування каркаса не знає. Мета рефакторингу, отже, не «нуль смиків» — мета в тому, щоб смик лишився **тільки там, де ти справді не порядкуєш створенням**, і щоб таких місць було рівно стільки, скільки чужий код тобі нав'язав: два-три перехідники на всю систему замість двохсот класів, кожен із власним чорним ходом. Саме ця межа й відрізняє доречний реєстр від [локатора служб](book:programming/service-locator) як халепи — не сама наявність смику, а те, скільки коду він отруює.

Кількісно весь рецепт зводиться до одного числа — скільки файлів згадують `Locator`. На початку це число дорівнює числу класів, що смикають; наприкінці — числу місць, де створенням порядкує чужий код, тобто одиницям. Решта класів отримали чесні конструктори, а разом із ними — [шов](book:programming/testability-tactics), уздовж якого їх нарешті можна різати й перевіряти.
