# ⚙️ Зібрати ACL і довести його непроникність

Одну річ легко проголосити й важко втримати: «жодне чуже поняття не просочується в домен». Проголосити — це намалювати рамку шару на дошці. Втримати — це зробити так, щоб через рік, коли над кодом попрацювало п'ятеро людей поспіху, рамка все ще тримала. Різниця між цими двома станами — не старанність, а **автоматична перевірка**. Правило, яке нема чим перевірити, — це не правило, а побажання; його зламають, і ніхто не помітить, доки не стане дорого.

Тож розберемо ACL до останнього гвинтика: з чого він складається, як зібрати всі частини докупи — і, головне, як **машиною довести**, що оборона справді непроникна. Задача навмисне вужча за «намалювати архітектуру»: узяти конкретний стик «чужий CRM → чистий контекст складу» і зробити його так, щоб протікання чужого поняття всередину домену стало не «поганим стилем, який на код-рев'ю попросять переписати», а **зламаним тестом, який не пускає код у гілку**.

## Задача

Склад приймає замовлення зі старого CRM. CRM віддає рядок `SKU` виду `"ART-00417/RED/XL"` (колір і розмір зашиті рисками), поле `qty`, де від'ємне число означає повернення, магічний `status_code` (число `7` в їхній документації значить «частково зарезервовано на іншому складі»), і `client_ref` виду `"CL:88213"`. Наша модель складу нічого з цього не знає: у ній є `Order`, `Product` з окремими артикулом/кольором/розміром, `ClientId`, а понять «повернення з CRM» чи «резерв деінде» просто нема.

Треба:

1. Зібрати повний ACL із чотирьох частин — **фасад** (ховає незручний API CRM за одним зрозумілим викликом), **перекладач-translator** (перетворює чужі поняття на наші), **обробку чужого без відповідника** (відбиває зрозумілою помилкою, а не мовчки протягує), і **точку збірки** (де все це з'єднується з доменом).
2. Написати **тест на непроникність**, який автоматично доводить дві речі: (а) доменний шар не імпортує жодного типу CRM; (б) перекладач відбиває непідтримуване чуже поняття, а не пропускає його всередину.

Мова прикладу — TypeScript і Python вкладками: стик двох бекендів — рівно та задача, де обидві лягають ідіоматично, тож показуємо кожну по-своєму.

> 🔧 **Навіщо це.** Архітектурне правило без автоматичної перевірки живе рівно до першого «та тут швидше було просто взяти `dto.sku` прямо в сервісі». Одне таке протікання саме по собі нешкідливе; проблема в тому, що воно **знімає табу**. Раз можна тут — можна й там, і за пів року знання про формат CRM знову розмазане по домену, а шар стоїть декоративною ширмою. Тест на непроникність повертає правилу зуби: протікання перестає бути питанням смаку й дисципліни й стає механічним фактом, який видно на CI. Дешевше зловити його червоним тестом за секунди, ніж археологією через рік.

## Ідея: чотири частини й один шов

ACL зсередини — не одна каша, а чотири ролі, кожна з вузькою відповідальністю. Розділити їх варто не заради краси, а тому, що кожну хочеться **міняти й тестувати окремо**.

**Фасад** розмовляє з реальним CRM: тримає з'єднання, знає ендпойнти, розгортає посторінкову видачу, ретрайне мережеві збої. Його єдина мета — сховати незручність доступу за одним чесним викликом «дай наступний сирий запис». Фасад усе ще працює в **чужих типах** — він повертає `CrmOrderDto`, бо його робота дістати дані, а не перекласти їх.

**Перекладач (translator)** бере сирий `CrmOrderDto` і **народжує з нього** `Order` нашої моделі — розбирає `SKU`, тлумачить `qty`, звіряє статус. Він не знає ні про мережу, ні про сторінки; він знає лише про два словники — чужий і наш — і про правила перекладу між ними. Це єдине місце в усій системі, де слова CRM зустрічаються зі словами складу.

**Обробка чужого без відповідника** — не окремий клас, а **свідоме рішення перекладача** на кожному понятті, якому в нашій моделі пари немає. Повернення? Наша модель приймання їх не знає — відбій. Статус `7`? Відповідника нема — відбій. Відбій — це кинута доменна помилка `UnsupportedByModel`, зрозуміла людині й ловна кодом. Ключове: непідтримуване поняття **не доходить** до домену навіть у скаліченому вигляді — воно зупиняється на порозі.

**Точка збірки** з'єднує все з доменом через **порт** — інтерфейс, який оголошує домен своєю мовою (`OrderSource`: «дай наступне замовлення як НАШ об'єкт»). Домен залежить лише від порту. Конкретна реалізація порту — це фасад + перекладач, склеєні в точці збірки (composition root). Домен її не бачить і не імпортує.

![Горизонтальний конвеєр зліва направо. Ліворуч блок «Чужий CRM» червоним. Стрілка веде до блоку «Фасад» синім з підписом «мережа, сторінки, ретрай; повертає CrmOrderDto». Наступна стрілка з підписом «сирий CrmOrderDto» веде до блоку «Перекладач» синім з підписом «SKU→Product, qty, статус». Від перекладача вниз відходить коротка червона стрілка до маленького блоку «UnsupportedByModel — відбій» з підписом «чуже без пари не йде далі». Основна стрілка з підписом «чистий Order» від перекладача веде до пунктирної вертикальної лінії-межі домену, за якою зелений блок «Домен: OrderService». Уся трійця фасад-перекладач-відбій обведена рамкою з підписом «Антикорупційний шар». Домен за межею підписаний «залежить лише від порту OrderSource»](img/acl-pipeline.svg)

*Чотири ролі на одному конвеєрі. Фасад дістає сирі дані в чужих типах; перекладач народжує з них наш `Order`; чуже без відповідника відбивається вниз помилкою й не доходить до межі; за межею домен бачить лише чистий об'єкт через порт. Знання про CRM живе ліворуч від пунктиру й ніколи не перетинає його.*

Тепер зберемо це в код, частину за частиною, а тоді — найцікавіше — доведемо, що пунктир на малюнку справді непрохідний.

## Крок 1. Чужі типи й доменні типи — по різні боки

Спершу зафіксуємо два світи як окремі модулі. Це не формальність: **фізична межа файлів** — половина оборони. Якщо типи CRM лежать в окремому модулі, стає можливим механічно спитати «хто його імпортує?» — і саме на цьому питанні триматиметься весь тест непроникності.

Чужий бік — типи CRM. Вони існують рівно для того, щоб перекладач мав що читати, і **більше ніхто** не має права їх бачити.

:::tabs
```ts
// crm/dto.ts — ЧУЖИЙ світ. Тільки перекладач має право це імпортувати.
export interface CrmOrderDto {
  sku: string;         // "ART-00417/RED/XL"
  qty: number;         // від'ємне → повернення
  status_code: number; // 7 = "зарезервовано деінде" тощо
  client_ref: string;  // "CL:88213"
}
```
```python
# crm/dto.py — ЧУЖИЙ світ. Тільки перекладач має право це імпортувати.
from dataclasses import dataclass

@dataclass(frozen=True)
class CrmOrderDto:
    sku: str          # "ART-00417/RED/XL"
    qty: int          # від'ємне → повернення
    status_code: int  # 7 = "зарезервовано деінде" тощо
    client_ref: str   # "CL:88213"
```
:::

Наш бік — доменні типи. Чиста мова складу, [незмінні значення](root:sf-apps/immutability) там, де їм місце. Жодного натяку на CRM.

:::tabs
```ts
// domain/order.ts — НАШ світ. Мова складу. Про CRM не чув.
export class Article { constructor(readonly code: string) {} }
export class Color   { static parse(s: string) { return new Color(s); }
                       private constructor(readonly name: string) {} }
export class Size    { static parse(s: string) { return new Size(s); }
                       private constructor(readonly label: string) {} }
export class ClientId { constructor(readonly value: string) {} }

export class Product {
  constructor(
    readonly article: Article,
    readonly color: Color,
    readonly size: Size,
  ) {}
}

export class Order {
  constructor(
    readonly client: ClientId,
    readonly product: Product,
    readonly quantity: number,  // завжди > 0 — модель від'ємних не знає
  ) {}
  reserve(): void { /* чисте доменне правило складу */ }
}

// Порт: що домен ВИМАГАЄ. Оголошено нашою мовою.
export interface OrderSource {
  next(): Order | null;
}
```
```python
# domain/order.py — НАШ світ. Мова складу. Про CRM не чув.
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class Article: code: str

@dataclass(frozen=True)
class Color:
    name: str
    @staticmethod
    def parse(s: str) -> "Color": return Color(s)

@dataclass(frozen=True)
class Size:
    label: str
    @staticmethod
    def parse(s: str) -> "Size": return Size(s)

@dataclass(frozen=True)
class ClientId: value: str

@dataclass(frozen=True)
class Product:
    article: Article
    color: Color
    size: Size

@dataclass(frozen=True)
class Order:
    client: ClientId
    product: Product
    quantity: int  # завжди > 0 — модель від'ємних не знає
    def reserve(self) -> None: ...  # чисте доменне правило складу

# Порт: що домен ВИМАГАЄ. Оголошено нашою мовою.
class OrderSource(ABC):
    @abstractmethod
    def next(self) -> Order | None: ...
```
:::

Зверни увагу на дрібницю, яка потім зіграє велику роль: `Order.quantity` тут **завжди додатне**. Модель складу поняття «мінус три штуки» не має. Це не випадковість і не строгість заради строгості — це те саме табу, яке шар мусить стерегти. Від'ємне число з CRM не має права стати `quantity`; воно або перекладається в інше наше поняття, або відбивається. Тип домену вже кодує це правило, і перекладачеві доведеться його поважати.

## Крок 2. Фасад — сховати незручність доступу

Фасад стоїть упритул до CRM. Він розгортає посторінкову видачу, тримає буфер, за потреби ретрайне — уся ця морока замкнена тут, за одним чесним викликом `fetchNext()`, що віддає сирий `CrmOrderDto` або `null`, коли записи скінчились. Фасад **навмисно** лишається в чужих типах: перекласти — не його робота.

:::tabs
```ts
// acl/crmFacade.ts — ховає незручний доступ. Усе ще в ЧУЖИХ типах.
import { CrmOrderDto } from "../crm/dto";
import { CrmHttpClient } from "../crm/httpClient"; // сира HTTP-обгортка CRM

export class CrmOrderFacade {
  private buffer: CrmOrderDto[] = [];
  private page = 0;
  private exhausted = false;

  constructor(private http: CrmHttpClient) {}

  // Один чесний виклик замість пагінації, ретраїв і формату відповіді.
  async fetchNext(): Promise<CrmOrderDto | null> {
    if (this.buffer.length === 0 && !this.exhausted) {
      await this.loadPage();
    }
    return this.buffer.shift() ?? null;
  }

  private async loadPage(): Promise<void> {
    const resp = await this.retry(() =>
      this.http.get(`/orders?page=${this.page}&size=100`));
    this.buffer = resp.items;          // сирі CrmOrderDto
    this.exhausted = resp.items.length === 0;
    this.page += 1;
  }

  private async retry<T>(fn: () => Promise<T>, tries = 3): Promise<T> {
    for (let i = 0; ; i++) {
      try { return await fn(); }
      catch (e) { if (i >= tries - 1) throw e; }
    }
  }
}
```
```python
# acl/crm_facade.py — ховає незручний доступ. Усе ще в ЧУЖИХ типах.
from collections import deque
from crm.dto import CrmOrderDto
from crm.http_client import CrmHttpClient  # сира HTTP-обгортка CRM

class CrmOrderFacade:
    def __init__(self, http: CrmHttpClient):
        self._http = http
        self._buffer: deque[CrmOrderDto] = deque()
        self._page = 0
        self._exhausted = False

    # Один чесний виклик замість пагінації, ретраїв і формату відповіді.
    def fetch_next(self) -> CrmOrderDto | None:
        if not self._buffer and not self._exhausted:
            self._load_page()
        return self._buffer.popleft() if self._buffer else None

    def _load_page(self) -> None:
        resp = self._retry(
            lambda: self._http.get(f"/orders?page={self._page}&size=100"))
        self._buffer = deque(resp.items)      # сирі CrmOrderDto
        self._exhausted = not resp.items
        self._page += 1

    def _retry(self, fn, tries=3):
        for i in range(tries):
            try:
                return fn()
            except Exception:
                if i >= tries - 1:
                    raise
```
:::

Фасад — це той шар, який хочеться підмінити в тесті: реальний ходить у мережу, а тестовий віддає підготовлені записи з пам'яті. Тому фасад теж корисно сховати за вузьким інтерфейсом «джерело сирих записів». Але поки що важливіше інше — перекладач, бо саме він тримає межу.

## Крок 3. Перекладач — народити наше з чужого, чуже без пари відбити

Ось серце шару. Перекладач бере `CrmOrderDto` і повертає `Order`. На кожному полі він робить свідомий вибір: **перекласти** (є відповідник) або **відбити** (відповідника нема). Третього — «протягнути як є» — у нього нема за задумом.

Спершу доменна помилка відбою. Вона мусить бути **нашим** типом (живе в домені, бо це доменне рішення «наша модель такого не приймає»), нести зрозумілу людині причину й бути ловною кодом на межі.

:::tabs
```ts
// domain/errors.ts — доменна помилка: "наша модель це поняття не приймає".
export class UnsupportedByModel extends Error {
  constructor(readonly reason: string) {
    super(`Модель складу не приймає: ${reason}`);
    this.name = "UnsupportedByModel";
  }
}
```
```python
# domain/errors.py — доменна помилка: "наша модель це поняття не приймає".
class UnsupportedByModel(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Модель складу не приймає: {reason}")
```
:::

Тепер сам перекладач. Це чиста функція над даними — жодної мережі, жодного стану; лише два словники й правила між ними. Тому його так легко тестувати: подав `CrmOrderDto` — дістав або `Order`, або `UnsupportedByModel`.

:::tabs
```ts
// acl/orderTranslator.ts — ЄДИНЕ місце, де мови CRM і складу зустрічаються.
import { CrmOrderDto } from "../crm/dto";
import { Order, Product, Article, Color, Size, ClientId } from "../domain/order";
import { UnsupportedByModel } from "../domain/errors";

const KNOWN_STATUS = new Set([1, 2, 3]); // статуси, що мають відповідник у нас

export function translateOrder(dto: CrmOrderDto): Order {
  // --- чуже без пари: відбій на порозі ---
  if (dto.qty < 0)
    throw new UnsupportedByModel("повернення (від'ємна кількість) з CRM");
  if (dto.qty === 0)
    throw new UnsupportedByModel("нульова кількість");
  if (!KNOWN_STATUS.has(dto.status_code))
    throw new UnsupportedByModel(`статус ${dto.status_code} без відповідника`);

  // --- переклад: народжуємо наші поняття ---
  const product = parseSku(dto.sku);
  const client  = parseClient(dto.client_ref);
  return new Order(client, product, dto.qty);
}

function parseSku(sku: string): Product {
  const parts = sku.split("/");
  if (parts.length !== 3)
    throw new UnsupportedByModel(`SKU не розкладається на 3 частини: "${sku}"`);
  const [article, color, size] = parts;
  return new Product(new Article(article), Color.parse(color), Size.parse(size));
}

function parseClient(ref: string): ClientId {
  if (!ref.startsWith("CL:"))
    throw new UnsupportedByModel(`client_ref без префікса "CL:": "${ref}"`);
  return new ClientId(ref.slice(3));
}
```
```python
# acl/order_translator.py — ЄДИНЕ місце, де мови CRM і складу зустрічаються.
from crm.dto import CrmOrderDto
from domain.order import Order, Product, Article, Color, Size, ClientId
from domain.errors import UnsupportedByModel

KNOWN_STATUS = {1, 2, 3}  # статуси, що мають відповідник у нас

def translate_order(dto: CrmOrderDto) -> Order:
    # --- чуже без пари: відбій на порозі ---
    if dto.qty < 0:
        raise UnsupportedByModel("повернення (від'ємна кількість) з CRM")
    if dto.qty == 0:
        raise UnsupportedByModel("нульова кількість")
    if dto.status_code not in KNOWN_STATUS:
        raise UnsupportedByModel(f"статус {dto.status_code} без відповідника")

    # --- переклад: народжуємо наші поняття ---
    product = _parse_sku(dto.sku)
    client  = _parse_client(dto.client_ref)
    return Order(client, product, dto.qty)

def _parse_sku(sku: str) -> Product:
    parts = sku.split("/")
    if len(parts) != 3:
        raise UnsupportedByModel(f'SKU не розкладається на 3 частини: "{sku}"')
    article, color, size = parts
    return Product(Article(article), Color.parse(color), Size.parse(size))

def _parse_client(ref: str) -> ClientId:
    if not ref.startswith("CL:"):
        raise UnsupportedByModel(f'client_ref без префікса "CL:": "{ref}"')
    return ClientId(ref[3:])
```
:::

Придивись до порядку всередині `translateOrder`: спершу **всі відбої**, і лише потім **переклад**. Це не косметика. Перекладач — вартовий, і вартовий спершу перевіряє перепустку, а тоді пускає. Якби ми спершу розібрали `SKU`, а вже потім спохопились про від'ємне `qty`, ми б витратили роботу на дані, які й так не мали права зайти. Гірше — легше було б випадково повернути напівзібраний `Order` десь у середині. Політика «нема пари — відбій негайно» тримає інваріант простим: **або на виході коректний `Order`, або помилка; проміжного стану не буває**.

## Крок 4. Точка збірки — з'єднати з доменом через порт

Фасад дає сирі записи, перекладач їх перекладає. З'єднати їх у реалізацію порту `OrderSource` — робота точки збірки. Саме тут, і лише тут, фасад зустрічається з перекладачем; домен цієї зустрічі не бачить.

:::tabs
```ts
// acl/crmOrderSource.ts — реалізація ПОРТУ. Склеює фасад + перекладач.
import { OrderSource, Order } from "../domain/order";
import { CrmOrderFacade } from "./crmFacade";
import { translateOrder } from "./orderTranslator";

export class CrmOrderSource implements OrderSource {
  constructor(private facade: CrmOrderFacade) {}

  // Порт синхронний (як оголосив домен); async-фасад мостимо буфером —
  // деталі мосту опущено, суть тут — склейка фасаду з перекладачем.
  next(): Order | null {
    const dto = this.facade.nextBuffered();   // сирий CrmOrderDto або null
    return dto === null ? null : translateOrder(dto);
  }
}
```
```python
# acl/crm_order_source.py — реалізація ПОРТУ. Склеює фасад + перекладач.
from domain.order import OrderSource, Order
from acl.crm_facade import CrmOrderFacade
from acl.order_translator import translate_order

class CrmOrderSource(OrderSource):
    def __init__(self, facade: CrmOrderFacade):
        self._facade = facade

    def next(self) -> Order | None:
        dto = self._facade.fetch_next()
        return None if dto is None else translate_order(dto)
```
:::

І composition root — місце, де все стягується докупи й передається в домен. Це єдине місце в програмі, яке одночасно «бачить» і CRM-фасад, і доменний сервіс. Воно **навмисно тонке** й **навмисно поза доменом**: домен отримує вже готовий `OrderSource` і не знає, звідки той узявся.

:::tabs
```ts
// main.ts — composition root. Поза доменом. Єдине місце, що бачить обидва світи.
import { CrmHttpClient } from "./crm/httpClient";
import { CrmOrderFacade } from "./acl/crmFacade";
import { CrmOrderSource } from "./acl/crmOrderSource";
import { OrderService } from "./domain/orderService";

const http   = new CrmHttpClient(process.env.CRM_URL!);
const facade = new CrmOrderFacade(http);
const source = new CrmOrderSource(facade);   // ← ось де CRM стає OrderSource
const service = new OrderService(source);    // домен бачить лише порт

service.processBatch();
```
```python
# main.py — composition root. Поза доменом. Єдине місце, що бачить обидва світи.
import os
from crm.http_client import CrmHttpClient
from acl.crm_facade import CrmOrderFacade
from acl.crm_order_source import CrmOrderSource
from domain.order_service import OrderService

http    = CrmHttpClient(os.environ["CRM_URL"])
facade  = CrmOrderFacade(http)
source  = CrmOrderSource(facade)    # ← ось де CRM стає OrderSource
service = OrderService(source)      # домен бачить лише порт

service.process_batch()
```
:::

Тепер уся конструкція стоїть. Але поки що її непроникність тримається **лише на нашій добрій волі**: ніщо, крім домовленості, не заважає завтра комусь написати в доменному сервісі `import { CrmOrderDto }` і почати колупати `dto.sku` прямо там. Час зробити так, щоб заважало.

## Крок 5. Тест на непроникність — головне

Оборона, яку тримає тільки дисципліна, — це оборона, яку одного разу неодмінно проб'ють. Тому непроникність треба перетворити з «ми домовились» на **зламаний тест, що не пускає код далі**. Є два різні протікання, і кожне ловиться своїм тестом — вони перевіряють різні речі й не замінюють одне одного.

### 5.1. Структурний тест: домен не імпортує CRM

Перше протікання — **на рівні залежностей**: доменний файл починає імпортувати тип CRM. Це найпідступніше, бо на вигляд безневинне — «та я лише тип підтягнув». Але щойно домен імпортує `CrmOrderDto`, межа пробита: тепер зміна на боці CRM тягне перекомпіляцію й потенційний злам домену.

Ловиться це не звичайним юніт-тестом (він перевіряє поведінку, а тут ідеться про **структуру**), а [статичною перевіркою](root:sf-release/static-analysis) самих залежностей — читанням коду без запуску. Ідея проста: узяти всі файли домену й переконатися, що жоден не імпортує нічого з теки `crm/`. Це і є **архітектурна fitness-функція** — механізм, що дає об'єктивну оцінку архітектурної властивості. Термін увели Ніл Форд, Ребекка Парсонс і Патрік Куа в книжці «Building Evolutionary Architectures» (O'Reilly, 2017; у 2-му виданні співавтором доданий Прамод Садалаж), позичивши слово «fitness function» з еволюційних обчислень; означення там — «будь-який механізм, що дає об'єктивну оцінку інтегральності певної архітектурної характеристики». *(Статус: усталений термін індустрії, першоджерело — названа книжка.)*

У світі Java для цього є готовий інструмент ArchUnit, де правило пишеться майже словами: `noClasses().that().resideInAPackage("..domain..").should().dependOnClassesThat().resideInAPackage("..crm..")`. У TS і Python готове теж є (у TS — `dependency-cruiser` чи ESLint-правило `no-restricted-imports`; у Python — `import-linter`), але корисно раз побачити, що це не магія: під капотом — просто читання імпортів і перевірка, що заборонених серед них нема. Напишімо своїми руками, щоб було видно механізм.

:::tabs
```ts
// tests/impermeable.structure.test.ts
// Fitness-функція: жоден файл домену не сміє імпортувати нічого з crm/.
import { readFileSync } from "fs";
import { globSync } from "glob";

test("домен не імпортує CRM", () => {
  const domainFiles = globSync("src/domain/**/*.ts");
  const offenders: string[] = [];

  for (const file of domainFiles) {
    const src = readFileSync(file, "utf8");
    // будь-який import ... from "...crm..." — порушення
    const importsCrm = /import[^;]*from\s+["'][^"']*\/crm\/[^"']*["']/.test(src);
    if (importsCrm) offenders.push(file);
  }

  expect(offenders).toEqual([]); // жодного протікання на рівні залежностей
});
```
```python
# tests/test_impermeable_structure.py
# Fitness-функція: жоден модуль домену не сміє імпортувати нічого з crm.
import ast, pathlib

def test_domain_does_not_import_crm():
    domain_files = pathlib.Path("src/domain").rglob("*.py")
    offenders = []

    for file in domain_files:
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.Import):
                mod = ",".join(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
            if mod and "crm" in mod.split("."):
                offenders.append(f"{file}: {mod}")

    assert offenders == []  # жодного протікання на рівні залежностей
```
:::

Різниця в глибині між двома реалізаціями показова, і вона тут повчальна. Версія на Python розбирає файл у **синтаксичне дерево** (`ast`) і дивиться саме на вузли імпорту — це точно й не сплутає слово `crm` у коментарі з реальним імпортом. Версія на TS іде дешевшим шляхом — регулярним виразом по тексту, — і цього для гейта досить, але вона крихкіша: химерно записаний імпорт вона може проґавити, а `crm` у рядку-літералі — хибно звинуватити. Для промислового використання в TS беруть готовий `dependency-cruiser`, який теж будує справжній граф залежностей. Мораль одна: **точність перевірки має відповідати ціні протікання** — для твердої межі домену краще дерево, ніж регулярка.

> 🔧 **Навіщо це.** Структурний тест ловить протікання, якого **не видно в поведінці**. Код із `import CrmOrderDto` у домені може працювати ідеально — усі юніт-тести зелені, бо поведінка правильна. І саме тому дисциплінарний контроль тут безсилий: немає симптому, доки одного дня CRM не змінить `CrmOrderDto` і не покладе половину домену. Fitness-функція робить невидиму залежність **видимою на CI** — вона перетворює «хтось колись помітить на рев'ю» на «збірка червона за дві секунди».

### 5.2. Поведінковий тест: перекладач відбиває непідтримуване

Друге протікання — **на рівні поведінки**: перекладач зустрів чуже поняття без відповідника й, замість відбити, тихо пропустив його — наприклад, підставив `qty = -3` у `Order` як є, або мовчки з'їв невідомий статус і повернув абияк зібраний об'єкт. Структурний тест такого не побачить (імпорти чисті!), бо тут ідеться не про залежності, а про **рішення на межі**.

Це вже звичайний юніт-тест, і перекладач ідеально для нього створений: чиста функція без стану. Перевіряємо обидва боки контракту — що добре пропускається, а погане відбивається саме `UnsupportedByModel`, а не якось інакше.

:::tabs
```ts
// tests/impermeable.behavior.test.ts
import { translateOrder } from "../src/acl/orderTranslator";
import { UnsupportedByModel } from "../src/domain/errors";
import { Order } from "../src/domain/order";

const good = {
  sku: "ART-00417/RED/XL", qty: 5, status_code: 2, client_ref: "CL:88213",
};

test("валідне замовлення перекладається в чистий Order", () => {
  const order = translateOrder(good);
  expect(order).toBeInstanceOf(Order);
  expect(order.quantity).toBe(5);
  expect(order.product.article.code).toBe("ART-00417");
  expect(order.client.value).toBe("88213");     // "CL:" зрізано
});

// Кожне чуже поняття без пари МУСИТЬ відбитися UnsupportedByModel.
test.each([
  ["повернення",        { ...good, qty: -3 }],
  ["нульова кількість", { ...good, qty: 0 }],
  ["невідомий статус",  { ...good, status_code: 7 }],
  ["кривий SKU",        { ...good, sku: "ART-00417-RED" }],
  ["client без CL:",    { ...good, client_ref: "88213" }],
])("відбиває: %s", (_name, dto) => {
  expect(() => translateOrder(dto)).toThrow(UnsupportedByModel);
});
```
```python
# tests/test_impermeable_behavior.py
import pytest
from acl.order_translator import translate_order
from domain.errors import UnsupportedByModel
from domain.order import Order
from crm.dto import CrmOrderDto

def good(**over) -> CrmOrderDto:
    base = dict(sku="ART-00417/RED/XL", qty=5,
                status_code=2, client_ref="CL:88213")
    base.update(over)
    return CrmOrderDto(**base)

def test_valid_order_translates_to_clean_order():
    order = translate_order(good())
    assert isinstance(order, Order)
    assert order.quantity == 5
    assert order.product.article.code == "ART-00417"
    assert order.client.value == "88213"          # "CL:" зрізано

# Кожне чуже поняття без пари МУСИТЬ відбитися UnsupportedByModel.
@pytest.mark.parametrize("name, dto", [
    ("повернення",        good(qty=-3)),
    ("нульова кількість", good(qty=0)),
    ("невідомий статус",  good(status_code=7)),
    ("кривий SKU",        good(sku="ART-00417-RED")),
    ("client без CL:",    good(client_ref="88213")),
])
def test_rejects_unsupported(name, dto):
    with pytest.raises(UnsupportedByModel):
        translate_order(dto)
```
:::

Ці два тести разом і є доказ непроникності — але доводять вони різне, і в цьому вся суть. Структурний каже: «чужий тип **фізично не дотягується** до домену». Поведінковий каже: «чуже поняття, навіть дотягнувшись до перекладача, **не проходить крізь нього** скаліченим — воно відбивається, а не мутує в кривий доменний об'єкт». Перший стереже двері, другий стереже вартового. Прибереш будь-який — і лишиться діра: без структурного хтось затягне DTO повз перекладач прямим імпортом; без поведінкового перекладач одного дня «на радощах» пропустить `qty = -3`, і від'ємна кількість оселиться в домені, який присягався її не знати.

## Складність і пастки

Зібрати ACL нескладно; складно **не дати йому непомітно протекти** попри всю конструкцію. Майже всі протікання — не через відсутність шару, а через тонкі діри в ньому, які структурний і поведінковий тести й покликані світити. Ось ті, що трапляються найчастіше.

**Транзакція або `execSql` протекли в порт.** Найпідступніша пастка, бо маскується під невинність. Ти оголошуєш порт `OrderSource` — і в якийсь момент, «щоб було зручніше керувати транзакцією», додаєш у нього метод `beginTx()` чи параметр `connection`. Здавалося б, дрібниця — а насправді ти щойно протягнув у домен **поняття чужої інфраструктури**: домен тепер знає, що на тому боці є транзакції, з'єднання, SQL. Це те саме протікання, тільки не через тип DTO, а через **форму порту**. Правило-протиотрута: порт говорить **виключно доменними дієсловами** («дай наступне замовлення»), і жодне слово з нього не має видавати, що за ним — база, HTTP чи файл. Якщо в сигнатурі порту з'явилось `Transaction`, `Connection`, `Sql`, `Cursor` — межу вже пробито, хоч тести залежностей поки й зелені (бо ці типи можуть жити не в теці `crm/`). Тому структурний тест варто розширити й на інфраструктурні теки, не лише на `crm/`.

**Надто широкий порт.** Спокуса зробити порт «на всяк випадок» багатим: `next()`, `count()`, `rawStatusOf()`, `underlyingDto()`. Кожен зайвий метод — це запрошення чужому поняттю пролізти назад. Особливо `underlyingDto()` чи будь-що, що віддає домену сирий чужий об'єкт «якщо раптом знадобиться»: це прямий тунель під усією обороною — DTO офіційно, з парадного входу, потрапляє в домен. Порт має бути **рівно такий вузький**, як вимагає домен **сьогодні** — це прямий наказ [YAGNI](root:sf-apps/dry-kiss-yagni). Широкий порт — не гнучкість, а діра, яку ти сам прорубав і сам же завтра через неї протечеш.

**Переклад «на льоту» в кількох місцях.** Класика повільного гниття. Перекладач є, він гарний — але одного дня хтось «поспішав» і розібрав `SKU` через `split("/")` прямо в іншому сервісі, бо «там же той самий формат, навіщо тягти перекладач». Тепер знання про формат CRM живе у **двох** місцях, і структурний тест це може проґавити (якщо той сервіс формально не в теці `crm/`, а імпортує лише рядок). Протиотрута двояка: по-перше, залізне правило «переклад буває **рівно в одному** місці — у перекладачі», по-друге, підсилений структурний тест, який ловить не тільки імпорт DTO, а й **характерні операції над чужим форматом** поза шаром (розбір `SKU`, звірку зі `status_code`). Практично: якщо `split("/")` над артикулом чи літерал `"CL:"` трапляється деінде, крім `acl/`, — це порушення, і його варто внести окремим правилом. Один шов на кордоні — уся сила ACL; два шви — уже не кордон, а сито.

**Відбій, що тихо ковтає.** Буває, обробку чужого без відповідника пишуть як `catch` без діла або `return null` замість помилки — «щоб не падало». Це найгірше з можливого: непідтримуване поняття не протекло в домен, але й **не відбилося чесно** — воно просто зникло, і замовлення тихо загубилось. Оборона не в тому, щоб проковтнути чуже мовчки, а в тому, щоб **голосно відмовити**: кинути `UnsupportedByModel` із причиною, яку видно в логах і на яку є тест. Мовчазне ковтання — це діра, замаскована під порядок: тестів помилок нема, бо помилок «не буває», а дані тим часом течуть у нікуди.

Спільний корінь усіх чотирьох пасток той самий: **межа тримається рівно доти, доки її стереже машина, а не звичка.** Шар можна намалювати ідеально й за місяць продіряти в чотирьох місцях, жодного разу не зробивши нічого явно поганого — просто «зручніше було». Тому в ACL головний артефакт — не фасад і не перекладач, які пишуться за годину, а **пара тестів на непроникність**, які цю годину роботи стережуть роками. Структурний доводить, що чуже фізично не дотягується; поведінковий — що чуже, дотягнувшись, не проходить. Разом вони перетворюють «ми домовились тримати межу» на «межу тримає CI, і пробити її означає покласти збірку». Оце і є різниця між обороною, яку намалювали, і обороною, яка справді тримає.

Sources: [Building Evolutionary Architectures — Fitness Functions (O'Reilly)](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/ch02.html), [ArchUnit User Guide](https://www.archunit.org/userguide/html/000_Index.html)
