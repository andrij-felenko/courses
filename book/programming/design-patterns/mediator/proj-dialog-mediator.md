# ⚙️ Вікно реєстрації: посередник, який не розповзається

Маленьке вікно на три елементи — прапорець, поле, кнопка — тримається на посереднику легко: його `notify` читається за десять секунд. Але справжні форми не такі. Візьмімо вікно реєстрації з доставкою — десяток полів, що чіпляються одне за одне, — і проведімо його через ту саму ідею. Тут посередник або лишається найяснішим місцем коду, або тихо перероджується в монстра, якого страшно чіпати. Різниця не в патерні, а в трьох дисциплінах, які ми зараз і випишемо кодом.

## Повніше вікно: хто на кого впливає

Поля такі:

- **пошта** — обов'язкова, має бути схожа на адресу;
- **пароль** і **повтор пароля** — другий мусить збігатися з першим;
- **країна** — випадний список; від неї залежить список **областей** (інша країна — інші області, а для декого їх узагалі нема);
- **область** — список, наповнення якого диктує країна;
- **«доставка збігається з оплатою»** — прапорець; коли ввімкнений, поле **адреси доставки** гасне й очищається;
- **адреса доставки** — обов'язкова, поки прапорець не стоїть;
- **промокод** — необов'язковий; чинний код запалює позначку знижки;
- **згода з умовами** — прапорець, обов'язковий;
- **кнопка «Зареєструватися»** — активна лише коли все правильно.

Уже з опису проступає павутина: країна смикає область, прапорець доставки смикає адресу, пароль смикає повтор, а кнопка залежить майже від усіх. Порахуймо це чесно, перш ніж чіпати посередник.

## Скільки зв'язків без посередника

Якщо зшити вікно «в лоб» — хай кожен віджет сам смикає тих, кого зачіпає, — постане ось такий список прямих посилань:

```
хто → кого           навіщо
country  → region     перезавантажити список областей
country  → submit     валідність могла змінитись
shipSame → shipping   увімкнути/вимкнути й очистити
shipSame → submit     валідність
shipping → submit     валідність
password → confirm    звірити збіг
password → submit     валідність
confirm  → submit     валідність
email    → submit     валідність
region   → submit     валідність
promo    → discount   показати/сховати знижку
terms    → submit     валідність
                      ────
разом                 12 прямих посилань між віджетами
```

Дванадцять ниток на дев'ять полів. Гляньмо на них уважніше — біда не лише в числі. По-перше, **кнопка — вузол-хаб**: на неї показують вісім різних віджетів, бо кожне обов'язкове поле впливає на її стан. По-друге, щоб порахувати той стан, треба **прочитати сім полів разом** (пошту, обидва паролі, країну, область, адресу, згоду) — отже логіка «чи можна тиснути» зчеплена одразу з усіма сімома, і хтось мусить її тримати. По-третє, ця логіка **смикається з восьми місць** — з кожного `onChange`, — тож або її дублюють, або виносять у спільний метод, який знову-таки знає про всіх. Оце і є [високе зчеплення](book:programming/coupling-cohesion): вузли переплетені так, що жоден не витягнеш і жодного правила не зміниш локально.

## Перший посередник: зірка замість павутини

Заведімо посередник і домовмося звично: жоден віджет не смикає сусіда — кожен лише каже посередникові «зі мною сталося ось що». Спершу колеги. Три різновиди: текстове поле, прапорець і список (поле з набором варіантів).

:::tabs
```ts
type FieldId =
  | "email" | "password" | "confirm" | "country" | "region"
  | "shipSame" | "shipping" | "promo" | "terms";

interface Mediator {
  notify(sender: FieldId, event: string): void;   // НАЇВНО: подія — рядок
}

class Field {                          // текстове поле-колега
  value = ""; enabled = true; error = "";
  constructor(readonly id: FieldId, private m: Mediator) {}
  setValue(v: string) { this.value = v; this.m.notify(this.id, "changed"); }
}

class Check {                          // прапорець-колега
  checked = false;
  constructor(readonly id: FieldId, private m: Mediator) {}
  toggle() { this.checked = !this.checked; this.m.notify(this.id, "toggled"); }
}

class Select extends Field {           // список — поле плюс набір варіантів
  options: string[] = [];
  setOptions(o: string[]) {
    this.options = o;
    if (!o.includes(this.value)) this.value = "";   // старий вибір більше не чинний
  }
}
```
```py
from typing import Protocol

class Mediator(Protocol):
    def notify(self, sender: str, event: str) -> None: ...   # НАЇВНО: рядок

class Field:                            # текстове поле-колега
    def __init__(self, id: str, m: Mediator) -> None:
        self.id, self._m = id, m
        self.value, self.enabled, self.error = "", True, ""
    def set_value(self, v: str) -> None:
        self.value = v
        self._m.notify(self.id, "changed")

class Check:                            # прапорець-колега
    def __init__(self, id: str, m: Mediator) -> None:
        self.id, self._m = id, m
        self.checked = False
    def toggle(self) -> None:
        self.checked = not self.checked
        self._m.notify(self.id, "toggled")

class Select(Field):                    # список — поле плюс набір варіантів
    def __init__(self, id: str, m: Mediator) -> None:
        super().__init__(id, m)
        self.options: list[str] = []
    def set_options(self, o: list[str]) -> None:
        self.options = o
        if self.value not in o:
            self.value = ""             # старий вибір більше не чинний
```
:::

Кожен колега знає лише посередника й уміє одне: змінившись, крикнути йому. Тепер серце — конкретний посередник. Він тримає всіх, а в одному методі описує **всю поведінку вікна**:

:::tabs
```ts
const REGIONS: Record<string, string[]> = {
  "Україна": ["Київська", "Львівська", "Одеська"],
  "Польща":  ["Мазовецьке", "Малопольське"],
  "США":     [],            // штат вводять окремо — список порожній
};
const PROMO: Record<string, number> = { WELCOME: 10, BOOK5: 5 };
const EMAIL_RE = /\S+@\S+\.\S+/;

class RegistrationDialog implements Mediator {
  email    = new Field("email", this);
  password = new Field("password", this);
  confirm  = new Field("confirm", this);
  country  = new Select("country", this);
  region   = new Select("region", this);
  shipSame = new Check("shipSame", this);
  shipping = new Field("shipping", this);
  promo    = new Field("promo", this);
  terms    = new Check("terms", this);
  submit   = { enabled: false };
  discount = 0;

  notify(sender: FieldId, _event: string) {      // УСЯ поведінка вікна — тут
    if (sender === "country")
      this.region.setOptions(REGIONS[this.country.value] ?? []);
    if (sender === "shipSame") {
      this.shipping.enabled = !this.shipSame.checked;
      if (this.shipSame.checked) this.shipping.value = "";
    }
    if (sender === "promo")
      this.discount = PROMO[this.promo.value.trim()] ?? 0;
    this.revalidate();
  }

  private revalidate() {
    const filled = (f: Field) => f.value.trim() !== "";
    const regionOk = this.region.options.length === 0 || filled(this.region);
    const shipOk   = this.shipSame.checked || filled(this.shipping);
    this.submit.enabled =
      EMAIL_RE.test(this.email.value) &&
      this.password.value.length >= 8 &&
      this.confirm.value === this.password.value &&
      filled(this.country) && regionOk && shipOk && this.terms.checked;
  }
}
```
```py
import re

REGIONS = {
    "Україна": ["Київська", "Львівська", "Одеська"],
    "Польща":  ["Мазовецьке", "Малопольське"],
    "США":     [],            # штат вводять окремо — список порожній
}
PROMO = {"WELCOME": 10, "BOOK5": 5}
EMAIL_RE = re.compile(r"\S+@\S+\.\S+")

class RegistrationDialog:
    def __init__(self) -> None:
        self.email     = Field("email", self)
        self.password  = Field("password", self)
        self.confirm   = Field("confirm", self)
        self.country   = Select("country", self)
        self.region    = Select("region", self)
        self.ship_same = Check("shipSame", self)
        self.shipping  = Field("shipping", self)
        self.promo     = Field("promo", self)
        self.terms     = Check("terms", self)
        self.submit_enabled = False
        self.discount = 0

    def notify(self, sender: str, event: str) -> None:   # УСЯ поведінка — тут
        if sender == "country":
            self.region.set_options(REGIONS.get(self.country.value, []))
        if sender == "shipSame":
            self.shipping.enabled = not self.ship_same.checked
            if self.ship_same.checked:
                self.shipping.value = ""
        if sender == "promo":
            self.discount = PROMO.get(self.promo.value.strip(), 0)
        self._revalidate()

    def _revalidate(self) -> None:
        filled = lambda f: f.value.strip() != ""
        region_ok = len(self.region.options) == 0 or filled(self.region)
        ship_ok   = self.ship_same.checked or filled(self.shipping)
        self.submit_enabled = bool(
            EMAIL_RE.match(self.email.value)
            and len(self.password.value) >= 8
            and self.confirm.value == self.password.value
            and filled(self.country) and region_ok and ship_ok
            and self.terms.checked)
```
:::

І короткий прогін — жоден віджет не торкається іншого, усе тече крізь центр:

:::tabs
```ts
const dlg = new RegistrationDialog();
dlg.country.setValue("Україна");     // → області: Київська/Львівська/Одеська
dlg.email.setValue("a@b.co");
dlg.password.setValue("secret12");
dlg.confirm.setValue("secret12");
dlg.region.setValue("Львівська");
dlg.shipping.setValue("вул. Січова, 3");
dlg.terms.toggle();                  // → submit.enabled === true
dlg.shipSame.toggle();               // доставка = оплата: адреса гасне, кнопка лишається активною
```
```py
dlg = RegistrationDialog()
dlg.country.set_value("Україна")     # → області: Київська/Львівська/Одеська
dlg.email.set_value("a@b.co")
dlg.password.set_value("secret12")
dlg.confirm.set_value("secret12")
dlg.region.set_value("Львівська")
dlg.shipping.set_value("вул. Січова, 3")
dlg.terms.toggle()                   # → submit_enabled == True
dlg.ship_same.toggle()               # доставка = оплата: адреса гасне, кнопка активна
```
:::

Що сталося зі зчепленням? Дванадцять ниток між віджетами перетворилися на **нуль**: жодне поле не назве жодного іншого. Кожен колега тримає рівно одне посилання — на посередник, — і всі дев'ять цих посилань дивляться в **один вузький інтерфейс** `notify`.

```
                     колега ↔ колега    колега → посередник
до посередника       12 ниток           —
після посередника    0                  9 (усі на один інтерфейс)
```

Правила нікуди не зникли — дванадцять взаємодій тепер живуть гілками в одному `notify`. Але граф зв'язків згорнувся в зірку: щоб зрозуміти «чому згасла кнопка», більше не треба обходити дев'ять класів — відповідь уся в `revalidate`. Оце і є виграш. А тепер — три способи, якими цей самий посередник псується, і дисципліна проти кожного.

## Спосіб перший, яким він гниє: рядкові події

Проблема захована в підписі `notify(sender, event: string)` — точніше, у тому, що `event` це голий рядок. Три діри:

- **Одрук компілюється.** Напишеш у гілці `sender === "contry"` — жодної помилки, гілка просто ніколи не спрацює, і область тихо перестане оновлюватися. Баг знайдеш руками, у проді.
- **Немає вичерпності.** Додаси десяте поле — компілятор не нагадає, що для нього треба гілка. `notify` мовчки не обробить новачка.
- **Пари «хто + що» не перевіряються.** `notify("country", "toggled")` — нісенітниця (список не клацають), але типи це пропустять.

Ліки — зробити подію **закритим типом**, а не рядком. У TypeScript це розмічене об'єднання: подія «змінив значення» несе будь-яке поле, а подія «клацнув» — лише прапорець. Тоді хибну пару відкидає вже компілятор. Це той самий хід, що й [зробити нелегальні стани невиразними через типи](book:programming/type-driven-design): множину дозволених подій задає система типів, а не домовленість у голові.

:::tabs
```ts
type DialogEvent =
  | { kind: "changed"; field: FieldId }               // значення оновилось
  | { kind: "toggled"; field: "shipSame" | "terms" }; // клацнути можна ЛИШЕ прапорці

interface Mediator { notify(e: DialogEvent): void; }

// у посереднику — розбір, який компілятор перевіряє на вичерпність:
notify(e: DialogEvent) {
  switch (e.field) {
    case "country":  this.region.setOptions(REGIONS[this.country.value] ?? []); break;
    case "shipSame": this.shipping.enabled = !this.shipSame.checked;
                     if (this.shipSame.checked) this.shipping.value = ""; break;
    case "promo":    this.discount = PROMO[this.promo.value.trim()] ?? 0; break;
    case "email": case "password": case "confirm":
    case "region": case "shipping": case "terms": break;   // лише ревалідація
    default: assertNever(e.field);   // забув гілку для нового поля → помилка КОМПІЛЯЦІЇ
  }
  this.revalidate();
}

function assertNever(x: never): never { throw new Error("незакрите поле: " + x); }
```
```py
from enum import Enum
from dataclasses import dataclass
from typing import assert_never

class F(Enum):                          # закритий перелік полів
    EMAIL = "email";   PASSWORD = "password"; CONFIRM = "confirm"
    COUNTRY = "country"; REGION = "region";   SHIP_SAME = "shipSame"
    SHIPPING = "shipping"; PROMO = "promo";   TERMS = "terms"

@dataclass(frozen=True)
class Changed: field: F
@dataclass(frozen=True)
class Toggled: field: F                 # у реальному коді — звузити до прапорців
DialogEvent = Changed | Toggled

def notify(self, e: DialogEvent) -> None:
    match e.field:
        case F.COUNTRY:  self.region.set_options(REGIONS.get(self.country.value, []))
        case F.SHIP_SAME:
            self.shipping.enabled = not self.ship_same.checked
            if self.ship_same.checked: self.shipping.value = ""
        case F.PROMO:    self.discount = PROMO.get(self.promo.value.strip(), 0)
        case F.EMAIL | F.PASSWORD | F.CONFIRM | F.REGION | F.SHIPPING | F.TERMS:
            pass                        # лише ревалідація
        case other:
            assert_never(other)         # новий F без гілки → перевіряч типів підкреслить
    self._revalidate()
```
:::

Тепер одрук `F.CONFRIM` — миттєва помилка (такого члена в переліку нема), а не тиха мертва гілка. Забудеш гілку для нового поля — `assertNever`/`assert_never` не пройде перевірку типів. І `notify({ kind: "toggled", field: "country" })` навіть не збереться: `country` не входить до дозволених для `toggled`. Рядок був домовленістю, про яку легко забути; типізована подія — домовленість, яку тримає компілятор.

## Спосіб другий: один notify на все

Технічно все у `notify` — законно. Але шість правил сьогодні стають двадцятьма за півроку, і метод, що був окрасою, стає полотном, крізь яке доводиться продиратися очима. Ліки — не пхати всю форму в один посередник, а розбити її на **групи полів за зв'язністю** й дати кожній свій маленький посередник, лишивши зверху тонкого координатора.

Гляньмо, де зв'язки густі, а де рідкі. Пошта-пароль-повтор варяться разом (повтор звіряється з паролем) і майже не чіпають доставки. Країна-область-прапорець-адреса варяться разом (країна керує областю, прапорець — адресою) і майже не чіпають облікових даних. Дві щільні грудки, а між ними — тонка ниточка: обидві лише впливають на кнопку. Отже, дві групи:

- **облікові дані**: пошта, пароль, повтор;
- **доставка**: країна, область, прапорець-збіг, адреса.

А згода, промокод і кнопка лишаються нагорі. Кожна група стає посередником своїх полів **і водночас колегою** координатора — це складений посередник (той самий інтерфейс, вкладений сам у себе):

:::tabs
```ts
class CredentialsGroup implements Mediator {
  readonly id = "creds" as const;
  email    = new Field("email", this);
  password = new Field("password", this);
  confirm  = new Field("confirm", this);
  constructor(private parent: Mediator) {}

  notify(_sender: FieldId, _e: string) {          // як ПОСЕРЕДНИК своїх полів
    this.confirm.error =
      this.confirm.value && this.confirm.value !== this.password.value
        ? "паролі не збігаються" : "";
    this.parent.notify(this.id, "changed");       // як КОЛЕГА координатора
  }
  get valid() {
    return EMAIL_RE.test(this.email.value)
        && this.password.value.length >= 8
        && this.confirm.value === this.password.value;
  }
}

class RegistrationDialog implements Mediator {
  creds   = new CredentialsGroup(this);
  address = new AddressGroup(this);               // симетрична: country/region/shipSame/shipping
  terms   = new Check("terms", this);
  submit  = { enabled: false };

  notify(_sender: FieldId, _e: string) {          // ЖОДНОЇ польової логіки — сама координація
    this.submit.enabled = this.creds.valid && this.address.valid && this.terms.checked;
  }
}
```
```py
class CredentialsGroup:
    def __init__(self, parent) -> None:
        self.id, self._parent = "creds", parent
        self.email    = Field("email", self)
        self.password = Field("password", self)
        self.confirm  = Field("confirm", self)

    def notify(self, sender: str, e: str) -> None:      # як ПОСЕРЕДНИК полів
        self.confirm.error = ("паролі не збігаються"
            if self.confirm.value and self.confirm.value != self.password.value else "")
        self._parent.notify(self.id, "changed")         # як КОЛЕГА координатора

    @property
    def valid(self) -> bool:
        return bool(EMAIL_RE.match(self.email.value)
                    and len(self.password.value) >= 8
                    and self.confirm.value == self.password.value)

class RegistrationDialog:
    def __init__(self) -> None:
        self.creds   = CredentialsGroup(self)
        self.address = AddressGroup(self)               # симетрична група доставки
        self.terms   = Check("terms", self)
        self.submit_enabled = False

    def notify(self, sender: str, e: str) -> None:      # сама координація, без полів
        self.submit_enabled = (self.creds.valid and self.address.valid
                               and self.terms.checked)
```
:::

Тепер `notify` координатора — один рядок, а логіка збігу паролів схована в тій групі, якої вона стосується. Кожен метод малий і читається сам; додаси правило про паролі — чіпаєш `CredentialsGroup`, і доставка навіть не дізнається про це (`AddressGroup` — дзеркальна: тримає країну, область, прапорець і адресу зі своїми двома правилами; тут її опущено, бо вона симетрична). Головне — **різати за зв'язністю, а не навмання**: у групу йдуть поля, що густо взаємодіють між собою, а між групами лишається пара тонких зв'язків, які й тримає верхній посередник. Розріжеш абияк — і між групами протягнеться стільки ниток, скільки ти намагався прибрати.

![Ліворуч і праворуч — дві групи-посередники в рамках: CredentialsGroup (email, password, confirm; усередині зв'язок «пароль = повтор») і AddressGroup (country, region, shipSame, shipping; усередині «країна → області» й «прапорець гасить адресу»). Кожна група лінією «valid?» піднімається до тонкого координатора RegistrationDialog зверху, поряд із яким висить прапорець terms; notify координатора — один рядок submit = creds.valid && address.valid && terms](img/sub-mediators.svg)

*Складений посередник: дві щільні групи-посередники всередині, тонкий координатор зверху. Густі зв'язки замкнені в групі, а координатор бачить лише «група валідна чи ні» та згоду — його `notify` стискається до одного рядка.*

## Спосіб третій: посередник, що взявся працювати сам

Найтихіша згуба. У наївному `revalidate` уже сидить `EMAIL_RE.test(...)`, `length >= 8`, `PROMO[...]` — і це не координація, це **робота**. Сьогодні перевірка пошти — регулярка; завтра промокод перевіряють на сервері (`await fetch`), ціну форматують за локаллю, згоду звіряють із версією умов. Якщо все це тече в `notify`, посередник розбухає в [божественний об'єкт](book:programming/anti-patterns) — клас, що знає й робить усе, без якого нічого не працює і якого страшно чіпати.

Межа проста: посередник **вирішує, кого зачепити, і питає результат — але сам його не рахує**. Уся робота живе поза ним, у колегах або в окремих виконавцях, яких він лише кличе. Це пряме застосування [єдиного обов'язку](book:programming/single-responsibility): координація — один обов'язок, валідація пошти — інший, похід у мережу по промокод — третій; в одному класі їм тісно.

:::tabs
```ts
// РОБОТА виноситься геть від посередника:
class EmailField extends Field { get valid() { return EMAIL_RE.test(this.value); } }
class PasswordField extends Field { get valid() { return this.value.length >= 8; } }

class PromoService {                       // може ходити в мережу — посереднику байдуже
  check(code: string): number { return PROMO[code.trim()] ?? 0; }
}

// ПОСЕРЕДНИК лише координує: питає й вирішує, а не обчислює:
notify(e: DialogEvent) {
  if (e.field === "promo")   this.discount = this.promoSvc.check(this.promo.value);
  if (e.field === "country") this.region.setOptions(this.regions.of(this.country.value));
  this.submit.enabled =
    this.email.valid && this.password.valid &&        // ПИТАЄ поле, не рахує саме
    this.confirm.value === this.password.value &&
    this.address.valid && this.terms.checked;
}
```
```py
# РОБОТА виноситься геть від посередника:
class EmailField(Field):
    @property
    def valid(self) -> bool: return bool(EMAIL_RE.match(self.value))

class PasswordField(Field):
    @property
    def valid(self) -> bool: return len(self.value) >= 8

class PromoService:                        # може ходити в мережу — посереднику байдуже
    def check(self, code: str) -> int: return PROMO.get(code.strip(), 0)

# ПОСЕРЕДНИК лише координує: питає й вирішує, а не обчислює:
def notify(self, e) -> None:
    if e.field is F.PROMO:   self.discount = self.promo_svc.check(self.promo.value)
    if e.field is F.COUNTRY: self.region.set_options(self.regions.of(self.country.value))
    self.submit_enabled = (
        self.email.valid and self.password.valid          # ПИТАЄ поле, не рахує саме
        and self.confirm.value == self.password.value
        and self.address.valid and self.terms.checked)
```
:::

Робоче правило-запобіжник: якщо в `notify` завелася **регулярка, `await fetch`, форматування дати чи гілка бізнес-правила** — посередник узявся не за своє, винось. Лишай йому дієслова «спитати», «вирішити», «покликати», «увімкнути» — і жодного «обчислити».

![У центрі-ліворуч рамка «Посередник — лише координує» з переліком дій: маршрутизує подію, питає колегу valid?, вирішує кого ввімкнути, кличе виконавця. Праворуч три окремі рамки-виконавці, до яких ідуть стрілки «кличе»: Валідатори полів, PromoService (мережа), Форматувальник ціни. Унизу червона смуга «У notify НЕ місце — це вже робота» з переліком регулярка, await fetch, формат дати, бізнес-if і стрілкою до «божественний об'єкт»](img/coordinate-not-work.svg)

*Тонкий посередник лише маршрутизує події й питає колег про результат; уся робота — валідація, перевірка промокоду в мережі, форматування — живе в окремих виконавцях, яких він кличе. Щойно ця робота переповзає всередину `notify`, посередник стає божественним об'єктом.*

## Пастки, які легко не помітити

**Лавина сповіщень.** Посередник у `notify` міняє колегу — а якщо ця зміна сама кличе `notify`, дістаємо рекурсію або подвійні спрацювання. Дисципліна: посередник пише **похідний стан** колег (`enabled`, `options`, `error`) **напряму**, не через ту саму дію, якою користувач сповіщає його. Тобто `region.setOptions(...)` не має всередині смикати `notify`. Коли ж зворотний зв'язок неминучий — скажімо, посередник нормалізує введений промокод у верхній регістр і кладе назад у поле, а сеттер поля сповіщає, — постав **прапорець «я вже розсилаю»**, точно як у надійному [спостерігачі](book:programming/observer): вкладений виклик лише лишає мітку й виходить, а не пірнає в другий рівень.

**Колега тягнеться крізь посередник.** Спокуса: дати колезі посилання на посередник — і написати `this.m.submit.disable()`. Це вбиває всю ідею: зв'язок «колега → колега» повертається, лише завуальований через центр, і рветься [закон Деметри](book:programming/law-of-demeter) — не тягнися крізь сусіда до його нутрощів. Колега має право **лише сповіщати** посередник; читає й пише колег **тільки сам посередник**. Промінь зірки — односторонній сигнал угору, а не двері до всіх інших.

**Прихована залежність від порядку.** Усередині `notify` порядок дій значущий: спершу `country` наповнює `region.options`, і лише потім `revalidate` читає ці `options`, щоб вирішити, чи область обов'язкова. Переставиш два рядки — валідність порахується по застарілому списку, тихо, без жодної помилки. Порядок у `notify`, від якого щось залежить, вартий коментаря — щоб наступний, хто чіпатиме код, не переставив потрібне.

**Посередник, приклеєний до живого UI.** Велика прихована винагорода централізації — **тестованість**: усю поведінку вікна можна прогнати без жодного справжнього віджета. Створив діалог із порожніми полями, посмикав `setValue`/`toggle`, перевірив `submit.enabled` — і ти покрив логіку форми звичайним юніт-тестом, бо вона вся в одному місці. Пастка — втратити це: щойно `notify` полізе в `document.querySelector` чи справжній рендер, тестувати доведеться крізь браузер. Тримай `notify` над абстрактними колегами, а живі віджети хай будуть тонкими адаптерами над ними.

**Посередник там, де його не треба.** І дзеркальна засторога: якщо два поля пов'язані одним-єдиним сталим зв'язком — хай кличуть одне одного напряму. Посередник окупається на густій мінливій павутині; над парою полів він лише зайвий шлагбаум, крізь який тепер треба з'ясовувати, куди піде сигнал.

## Підсумок

Посередник не прибрав складність вікна реєстрації — він зібрав її в одне видиме місце й тим зробив дев'ять полів простими та замінними. Дванадцять ниток стали зіркою, «чому згасла кнопка» дістало одну адресу. Але та сама централізація — це і вся небезпека: варто дати рядковим подіям текти абияк, звалити все в один `notify` і почати рахувати роботу просто в ньому — і найясніше місце коду стає божественним об'єктом. Три дисципліни, якими ми провели вікно, — типізовані події, розбиття на групи за зв'язністю, тверда межа «координація, не робота» — це і є те, що тримає посередник тим, заради чого його брали: єдиним місцем, куди дивишся, щоб зрозуміти, як поводиться вікно.
