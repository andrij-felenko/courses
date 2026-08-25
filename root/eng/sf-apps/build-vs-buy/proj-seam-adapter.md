# ⚙️ Порт і два адаптери: шов, за яким сидить постачальник

Задача звучить буденно, аж поки не візьмешся її кодувати. Застосунок доставки їжі мусить сповіщати клієнта: замовлення виїхало, кур'єр за п'ять хвилин, доставлено. Сьогодні листи розсилає готовий SaaS — HTTP-API постачальника (візьмімо для конкретності SendGrid). Усе працює. Але подивімося на рік уперед: ціна підписки може вирости втричі, постачальник — закритися, служба безпеки — зажадати слати через **власний** поштовий сервер по SMTP, маркетинг — захотіти іншого вендора з кращою аналітикою. Жоден із цих поворотів не фантастика; принаймні один майже напевно станеться.

Отже справжнє питання не «яким сервісом слати» — на нього відповідь є вже сьогодні. Питання таке: **як написати код так, щоб заміна постачальника була заміною одного файлу, а не розкопками по всій системі**. Це і є задача про шов — тонку перегородку, за якою конкретний постачальник захований і замінний. Далі — робочий приклад цієї перегородки: доменний порт, два адаптери до геть різних постачальників, збірка через впровадження залежностей, підміна в тестах, а тоді — найпповчальніше — як той самий шов зробити **дірявим** так, що він лише вдає захист, і коли його взагалі не варто ставити.

Приклад — код звичайного бекенду, не заліза, тож він однаково природний кількома мовами стеку. Показую трьома, кожна ідіоматична сама по собі: **TypeScript** (типізовані інтерфейси й розмічені об'єднання роблять протікання видимим у типах), **Python** (`Protocol` і датакласи — структурна типізація без церемоній) і **Go** (маленькі інтерфейси й помилки-значення — рідна стихія цього прийому). Перемикайте вкладки: це не переклад слово-в-слово, а той самий задум мовою кожної.

## Порт: гніздо, назване вашою потребою

Почнімо з головного рішення, від якого залежить усе інше, — **як назвати інтерфейс**. Спокуса одна: зазирнути в документацію SendGrid і зробити метод «схожий на те, що вміє постачальник». Це фатальна помилка, і причину варто відчути одразу, ще до коду. Якщо інтерфейс описано в термінах постачальника, то постачальник уже **всередині** інтерфейсу — а отже всередині всього, що цей інтерфейс уживає, тобто всередині ядра. Перейменувати метод замало: якщо він приймає чужий об'єкт і повертає чужий код, чужа модель протекла крізь нього, хай як його назви.

Тому порт описує не те, що **вміє постачальник**, а те, що **потрібно домену**. Домену потрібно рівно одне: сповістити отримувача про подію. Отже й порт — про це: `notify(отримувач, подія)`. Жодного постачальника в сигнатурі. Типи навколо — теж ваші: `отримувач` знає лише те, що знає ваш продукт (адреса, ім'я, мова листа), а `подія` — це словник **вашого** домену (замовлення виїхало, кур'єр поруч), а не поля чужого запиту.

Є ще тонкість, яку легко проґавити: **наслідок** спроби теж мусить бути доменним. Постачальник поверне вам «202» або «429» або «550» — але ядру не можна бачити цих чисел, бо в різних постачальників вони різні. Ядру треба знати одне з трьох у **його** термінах: доставлено (`delivered`), варто повторити пізніше (`retryable`), відхилено остаточно (`rejected`). Це доменне рішення — «чи є сенс повторювати» — і саме адаптер зобов'язаний перекласти будь-який чужий код у цю трійку. Кожна мова виражає такий наслідок ідіоматично: TypeScript і Python повертають об'єкт-наслідок, Go — помилку-значення, де `nil` означає «доставлено».

:::tabs
```ts
// domain/notifications.ts — усе у ВАШИХ термінах. Постачальника тут нема й близько.

export interface Recipient {
  email: string;
  name: string;
  locale: "uk" | "en";     // якою мовою слати — знає домен, не вендор
}

// Подія домену — те, ПРО ЩО сповіщаємо, мовою вашого продукту.
export type DomainEvent =
  | { kind: "order_shipped"; orderId: string; etaMinutes: number }
  | { kind: "courier_near"; orderId: string; minutesAway: number }
  | { kind: "order_delivered"; orderId: string };

// Наслідок спроби — теж доменний: доставлено / варто повторити / марно.
export type NotifyOutcome =
  | { status: "delivered" }
  | { status: "retryable"; reason: string }
  | { status: "rejected"; reason: string };

// Порт: одне гніздо, назване вашою ПОТРЕБОЮ.
export interface Notifier {
  notify(to: Recipient, event: DomainEvent): Promise<NotifyOutcome>;
}
```
```py
# domain/notifications.py — усе у ВАШИХ термінах.
from dataclasses import dataclass
from typing import Literal, Protocol, Union

@dataclass(frozen=True)
class Recipient:
    email: str
    name: str
    locale: Literal["uk", "en"]      # мову листа знає домен, не вендор

# Події домену — те, ПРО ЩО сповіщаємо, мовою вашого продукту.
@dataclass(frozen=True)
class OrderShipped:
    order_id: str
    eta_minutes: int

@dataclass(frozen=True)
class CourierNear:
    order_id: str
    minutes_away: int

@dataclass(frozen=True)
class OrderDelivered:
    order_id: str

DomainEvent = Union[OrderShipped, CourierNear, OrderDelivered]

# Наслідок спроби — теж доменний: доставлено / варто повторити / марно.
@dataclass(frozen=True)
class NotifyOutcome:
    status: Literal["delivered", "retryable", "rejected"]
    reason: str = ""

    @classmethod
    def delivered(cls) -> "NotifyOutcome":
        return cls("delivered")
    @classmethod
    def retryable(cls, reason: str) -> "NotifyOutcome":
        return cls("retryable", reason)
    @classmethod
    def rejected(cls, reason: str) -> "NotifyOutcome":
        return cls("rejected", reason)

# Порт: одне гніздо, назване вашою ПОТРЕБОЮ (структурний інтерфейс).
class Notifier(Protocol):
    def notify(self, to: Recipient, event: DomainEvent) -> NotifyOutcome: ...
```
```go
// domain/notify.go — усе у ВАШИХ термінах.
package domain

import "errors"

type Recipient struct {
    Email  string
    Name   string
    Locale string // "uk" | "en" — мову листа знає домен
}

// Подія домену — те, ПРО ЩО сповіщаємо (замкнене об'єднання).
type Event interface{ isEvent() }

type OrderShipped struct {
    OrderID    string
    ETAMinutes int
}
type CourierNear struct {
    OrderID     string
    MinutesAway int
}
type OrderDelivered struct{ OrderID string }

func (OrderShipped) isEvent()   {}
func (CourierNear) isEvent()    {}
func (OrderDelivered) isEvent() {}

// Наслідок домену виражений ідіоматично — помилкою. nil = доставлено;
// обгортка над цими двома = варто повторити / відхилено остаточно.
var (
    ErrRetryable = errors.New("notify: retryable")
    ErrRejected  = errors.New("notify: rejected")
)

// Порт: маленький інтерфейс, названий вашою потребою.
type Notifier interface {
    Notify(to Recipient, event Event) error
}
```
:::

> 🔧 **Навіщо це.** Прочитайте сигнатуру порту вголос: «сповісти цього отримувача про цю подію, і скажи — доставлено, повторити чи марно». У цьому реченні немає слова «SendGrid», немає «HTTP», немає «429». Саме тому воно переживе будь-яку зміну постачальника: ядро просить те, що йому справді треба, а **як** це зробити — клопіт того одного файлу, що зветься адаптером. Якби в сигнатурі стояло `sendViaSendGrid`, ви б уже програли — про це нижче.

## Адаптер перший: постачальник через HTTP-API

Тепер — єдине місце у всій системі, якому дозволено знати слово «SendGrid». Адаптер реалізує порт `Notifier` і робить рівно три переклади: **домен → чужий формат запиту** (зібрати тіло, яке хоче їхній HTTP-API), відправлення, і — найважливіше — **чужі коди → доменний наслідок**. У SendGrid успіх Mail Send — це `202 Accepted` (запит прийнято до відправлення), перевищення ліміту — `429 Too Many Requests`, а решта 4xx — відмова. *(Статус: усталено — коди з чинної документації Twilio SendGrid.)* Адаптер ловить кожен із них і віддає назовні лише `delivered` / `retryable` / `rejected`. Число `429` не виходить за поріг адаптера ніколи.

Зверніть увагу на одну межу відповідальності: **текст** листа (тема, тіло, потрібною мовою) вирішує домен — це його політика, а не транспорт. Тому адаптер кличе доменну `renderEvent(подія, мова)`, отримує готові тему й HTML, і лише **пакує** їх у чужий конверт. Якщо цю логіку затягти в адаптер, вона загубиться при заміні постачальника — а вона доменна, губити її не можна.

:::tabs
```ts
// adapters/sendgrid-notifier.ts — ЄДИНЕ місце зі словом "SendGrid".
import { Notifier, Recipient, DomainEvent, NotifyOutcome } from "../domain/notifications";
import { renderEvent } from "../domain/render";   // ТЕКСТ листа — рішення домену

const ENDPOINT = "https://api.sendgrid.com/v3/mail/send";

export class SendGridNotifier implements Notifier {
  constructor(private apiKey: string, private from: string) {}

  async notify(to: Recipient, event: DomainEvent): Promise<NotifyOutcome> {
    const { subject, html } = renderEvent(event, to.locale);

    // Переклад ДОМЕН → чужий формат тіла живе тут і тільки тут.
    const body = {
      personalizations: [{ to: [{ email: to.email, name: to.name }] }],
      from: { email: this.from },
      subject,
      content: [{ type: "text/html", value: html }],
    };

    let resp: Response;
    try {
      resp = await fetch(ENDPOINT, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });
    } catch (e) {
      // навіть збій мережі НЕ протікає як є — це доменний "варто повторити"
      return { status: "retryable", reason: `network: ${(e as Error).message}` };
    }

    // Переклад чужих КОДІВ → доменний наслідок. 202/429/5xx назовні не йдуть.
    if (resp.status === 202) return { status: "delivered" };
    if (resp.status === 429 || resp.status >= 500)
      return { status: "retryable", reason: `sendgrid ${resp.status}` };
    return { status: "rejected", reason: `sendgrid ${resp.status}` };
  }
}
```
```py
# adapters/sendgrid_notifier.py — єдине місце зі словом "SendGrid".
import json
import urllib.error
import urllib.request

from domain.notifications import Notifier, Recipient, DomainEvent, NotifyOutcome
from domain.render import render_event      # ТЕКСТ листа — рішення домену

ENDPOINT = "https://api.sendgrid.com/v3/mail/send"

class SendGridNotifier:                      # структурно реалізує Notifier (Protocol)
    def __init__(self, api_key: str, sender: str) -> None:
        self._api_key = api_key
        self._from = sender

    def notify(self, to: Recipient, event: DomainEvent) -> NotifyOutcome:
        subject, html = render_event(event, to.locale)

        # Переклад ДОМЕН → чужий формат тіла живе тут і тільки тут.
        body = {
            "personalizations": [{"to": [{"email": to.email, "name": to.name}]}],
            "from": {"email": self._from},
            "subject": subject,
            "content": [{"type": "text/html", "value": html}],
        }
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code                    # 4xx/5xx приходять сюди
        except urllib.error.URLError as e:
            return NotifyOutcome.retryable(f"network: {e.reason}")

        # Переклад чужих КОДІВ → доменний наслідок. 202/429/5xx назовні не йдуть.
        if code == 202:
            return NotifyOutcome.delivered()
        if code == 429 or code >= 500:
            return NotifyOutcome.retryable(f"sendgrid {code}")
        return NotifyOutcome.rejected(f"sendgrid {code}")
```
```go
// adapters/sendgrid.go — єдине місце зі словом "SendGrid".
package adapters

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"

    "example.com/app/domain"
)

const sendGridEndpoint = "https://api.sendgrid.com/v3/mail/send"

type SendGrid struct {
    APIKey string
    From   string
    HTTP   *http.Client
}

func (s SendGrid) Notify(to domain.Recipient, event domain.Event) error {
    subject, html := domain.RenderEvent(event, to.Locale) // ТЕКСТ — рішення домену

    // Переклад ДОМЕН → чужий формат тіла живе тут і тільки тут.
    payload := map[string]any{
        "personalizations": []any{map[string]any{
            "to": []any{map[string]string{"email": to.Email, "name": to.Name}},
        }},
        "from":    map[string]string{"email": s.From},
        "subject": subject,
        "content": []any{map[string]string{"type": "text/html", "value": html}},
    }
    buf, _ := json.Marshal(payload)

    req, _ := http.NewRequest(http.MethodPost, sendGridEndpoint, bytes.NewReader(buf))
    req.Header.Set("Authorization", "Bearer "+s.APIKey)
    req.Header.Set("Content-Type", "application/json")

    resp, err := s.HTTP.Do(req)
    if err != nil {
        return fmt.Errorf("network: %v: %w", err, domain.ErrRetryable)
    }
    defer resp.Body.Close()

    // Переклад чужих КОДІВ → доменний наслідок. 202/429/5xx назовні не йдуть.
    switch {
    case resp.StatusCode == 202:
        return nil // доставлено
    case resp.StatusCode == 429, resp.StatusCode >= 500:
        return fmt.Errorf("sendgrid %d: %w", resp.StatusCode, domain.ErrRetryable)
    default:
        return fmt.Errorf("sendgrid %d: %w", resp.StatusCode, domain.ErrRejected)
    }
}
```
:::

## Адаптер другий: той самий порт, зовсім інший постачальник

Тепер найпереконливіший доказ, що шов справжній, а не намальований: другий адаптер до постачальника, який **нічого спільного** не має з першим. SMTP — це не HTTP-API, у нього інший протокол, інша бібліотека, і головне — **інший словник помилок**. Замість `202` він каже `250` (прийнято), замість `429` — `421` (сервіс тимчасово недоступний) чи `450`/`452` (тимчасова відмова), а остаточну відмову позначає `550`. *(Статус: усталено — коди відповідей SMTP за RFC 5321.)*

І ось у чому вся сіль. Ці числа **зовсім інші**, ніж у SendGrid, — але вони перекладаються в **ту саму** доменну трійку. `421` і `429` — різні коди різних протоколів, а обидва означають доменне «варто повторити». Ядро ніколи не дізнається, який саме код прийшов; воно бачить лише `retryable`. Оце і є працюючий антикорупційний шар: два постачальники з несумісними моделями помилок, зведені до одного доменного наслідку, і ядро, яке говорить лише своєю мовою.

:::tabs
```ts
// adapters/smtp-notifier.ts — інший постачальник, ТОЙ САМИЙ порт.
import { Transporter } from "nodemailer";
import { Notifier, Recipient, DomainEvent, NotifyOutcome } from "../domain/notifications";
import { renderEvent } from "../domain/render";

export class SmtpNotifier implements Notifier {
  constructor(private tx: Transporter, private from: string) {}

  async notify(to: Recipient, event: DomainEvent): Promise<NotifyOutcome> {
    const { subject, html } = renderEvent(event, to.locale);
    try {
      await this.tx.sendMail({
        from: this.from,
        to: `${to.name} <${to.email}>`,
        subject,
        html,
      });
      return { status: "delivered" };
    } catch (err: any) {
      const code: number | undefined = err.responseCode;   // код відповіді SMTP
      if (code === undefined) return { status: "retryable", reason: `smtp io: ${err.code}` };
      // 4xx SMTP → тимчасово; 5xx → остаточно. Ті самі два кошики домену.
      if (code >= 400 && code < 500) return { status: "retryable", reason: `smtp ${code}` };
      return { status: "rejected", reason: `smtp ${code}` };
    }
  }
}
```
```py
# adapters/smtp_notifier.py — інший постачальник, ТОЙ САМИЙ порт.
import smtplib
from email.message import EmailMessage

from domain.notifications import Recipient, DomainEvent, NotifyOutcome
from domain.render import render_event

class SmtpNotifier:
    def __init__(self, host: str, port: int, sender: str) -> None:
        self._host, self._port, self._from = host, port, sender

    def notify(self, to: Recipient, event: DomainEvent) -> NotifyOutcome:
        subject, html = render_event(event, to.locale)

        msg = EmailMessage()
        msg["From"] = self._from
        msg["To"] = f"{to.name} <{to.email}>"
        msg["Subject"] = subject
        msg.set_content(html, subtype="html")

        try:
            with smtplib.SMTP(self._host, self._port, timeout=10) as smtp:
                smtp.send_message(msg)
            return NotifyOutcome.delivered()
        except smtplib.SMTPRecipientsRefused as e:       # усіх отримувачів відхилено
            code = max(c for c, _ in e.recipients.values())
            return _classify(code)
        except smtplib.SMTPResponseException as e:       # несе .smtp_code
            return _classify(e.smtp_code)
        except OSError as e:                             # мережа / з'єднання
            return NotifyOutcome.retryable(f"smtp io: {e}")

def _classify(code: int) -> NotifyOutcome:
    # 4xx SMTP → тимчасово; 5xx → остаточно. Ті самі два кошики домену.
    if 400 <= code < 500:
        return NotifyOutcome.retryable(f"smtp {code}")
    return NotifyOutcome.rejected(f"smtp {code}")
```
```go
// adapters/smtp.go — інший постачальник, ТОЙ САМИЙ порт.
package adapters

import (
    "errors"
    "fmt"
    "net/smtp"
    "net/textproto"

    "example.com/app/domain"
)

type SMTP struct {
    Addr string // "mail.example.com:587"
    From string
    Auth smtp.Auth
}

func (m SMTP) Notify(to domain.Recipient, event domain.Event) error {
    subject, html := domain.RenderEvent(event, to.Locale)

    msg := "From: " + m.From + "\r\n" +
        fmt.Sprintf("To: %s <%s>\r\n", to.Name, to.Email) +
        "Subject: " + subject + "\r\n" +
        "MIME-Version: 1.0\r\n" +
        "Content-Type: text/html; charset=UTF-8\r\n\r\n" + html

    err := smtp.SendMail(m.Addr, m.Auth, m.From, []string{to.Email}, []byte(msg))
    if err == nil {
        return nil // доставлено
    }

    // Чужі коди SMTP перекладаємо в доменний наслідок — назовні йде лише він.
    var proto *textproto.Error
    if errors.As(err, &proto) {
        // 4xx SMTP → тимчасово; 5xx → остаточно. Ті самі два кошики домену.
        if proto.Code >= 400 && proto.Code < 500 {
            return fmt.Errorf("smtp %d: %w", proto.Code, domain.ErrRetryable)
        }
        return fmt.Errorf("smtp %d: %w", proto.Code, domain.ErrRejected)
    }
    return fmt.Errorf("smtp io: %v: %w", err, domain.ErrRetryable) // мережа
}
```
:::

## Збірка на краю: впровадження залежностей

Порт і два адаптери самі себе не з'єднають. Хтось має вирішити, який саме адаптер отримає ядро, — і вся вправність тут у тому, **де** це рішення живе. Правило залізне: ядро **не створює** адаптер і навіть не знає його імені; воно приймає готовий `Notifier` ззовні, через конструктор. Це і є [впровадження залежностей](root:sf-apps/dependency-injection) — коли залежність передають об'єкту, а не він її сам добуває; завдяки цьому ядро залежить лише від порту-абстракції, а не від конкретики. А єдине місце, що обирає постачальника, — **композиційний корінь** (`main`), зовнішній край застосунку, де все збирають докупи. Заміна постачальника — це зміна одного рядка тут, і ніде більше.

:::tabs
```ts
// domain/dispatch.ts — ЯДРО. Знає лише порт Notifier, жодного постачальника.
export class OrderDispatch {
  constructor(private notifier: Notifier) {}    // впровадження залежності

  async onCourierAssigned(order: Order, customer: Recipient): Promise<void> {
    const outcome = await this.notifier.notify(customer, {
      kind: "courier_near",
      orderId: order.id,
      minutesAway: order.etaMinutes,
    });
    // рішення домену — БЕЗ знання про 429 чи 421
    if (outcome.status === "retryable") this.scheduleRetry(order);
  }
}

// main.ts — КОМПОЗИЦІЙНИЙ КОРІНЬ: єдиний рядок вибору постачальника.
const notifier: Notifier =
  process.env.MAIL === "smtp"
    ? new SmtpNotifier(makeTransport(), "no-reply@food.app")
    : new SendGridNotifier(process.env.SENDGRID_KEY!, "no-reply@food.app");

const dispatch = new OrderDispatch(notifier);  // ядро дістає порт, не знаючи, який адаптер
```
```py
# domain/dispatch.py — ЯДРО. Знає лише порт Notifier.
class OrderDispatch:
    def __init__(self, notifier: Notifier) -> None:    # впровадження залежності
        self._notifier = notifier

    def on_courier_assigned(self, order: Order, customer: Recipient) -> None:
        outcome = self._notifier.notify(
            customer, CourierNear(order_id=order.id, minutes_away=order.eta_minutes)
        )
        # рішення домену — без знання про 429 чи 421
        if outcome.status == "retryable":
            self._schedule_retry(order)

# main.py — КОМПОЗИЦІЙНИЙ КОРІНЬ: єдине місце вибору постачальника.
def build_notifier() -> Notifier:
    if os.environ.get("MAIL") == "smtp":
        return SmtpNotifier("mail.example.com", 587, "no-reply@food.app")
    return SendGridNotifier(os.environ["SENDGRID_KEY"], "no-reply@food.app")

dispatch = OrderDispatch(build_notifier())     # ядро дістає порт, не знаючи, який адаптер
```
```go
// domain/dispatch.go — ЯДРО. Приймає інтерфейс Notifier ("accept interfaces").
package domain

import "errors"

type Dispatch struct {
    Notifier Notifier // впровадження залежності — інтерфейс, не конкретика
}

func (d Dispatch) OnCourierAssigned(order Order, customer Recipient) {
    err := d.Notifier.Notify(customer, CourierNear{
        OrderID: order.ID, MinutesAway: order.ETAMinutes,
    })
    // рішення домену — без знання, це 429 чи 421
    if errors.Is(err, ErrRetryable) {
        d.scheduleRetry(order)
    }
}

// main.go — КОМПОЗИЦІЙНИЙ КОРІНЬ: єдине місце вибору постачальника.
func main() {
    var notifier domain.Notifier
    if os.Getenv("MAIL") == "smtp" {
        notifier = adapters.SMTP{Addr: "mail.example.com:587", From: "no-reply@food.app"}
    } else {
        notifier = adapters.SendGrid{
            APIKey: os.Getenv("SENDGRID_KEY"), From: "no-reply@food.app", HTTP: http.DefaultClient,
        }
    }
    dispatch := domain.Dispatch{Notifier: notifier} // ядро дістає порт, не знаючи адаптера
    _ = dispatch
}
```
:::

Загальну форму цього прийому — власний інтерфейс («порт») на краю ядра, за яким ховається все зовнішнє через змінні «адаптери», — називають [портами й адаптерами](root:sf-apps/hexagonal-architecture) (термін Алістера Кокберна, 2005). Суть її саме в напрямі залежності: не ядро тягнеться до постачальника, а адаптер тягнеться до ядра, реалізуючи його порт. Тому конкретний вендор завжди на **краю**, ніколи в **серці**.

## Підміна в тестах: чому чистий порт робить тести тривіальними

Ось де чистий порт окупається негайно, ще до всяких змін постачальника. Щоб перевірити логіку ядра — «на `retryable` призначаю повтор» — не треба ні мережі, ні ключа SendGrid, ні живого поштового сервера. Треба підмінити порт **підробкою**: об'єктом, що реалізує той самий `Notifier`, запам'ятовує виклики й повертає заздалегідь заданий наслідок. Ядро не відрізнить її від справжнього адаптера — і в цьому весь сенс.

І зверніть увагу, **чому** підробка така крихітна. Бо порт — доменний. Треба повернути `retryable` — повертаєш `retryable`, один рядок. Якби порт протікав постачальником, підробці довелося б вдавати цілий `SendGridResponse` із його полями й кодами — і тест став би крихким та прив'язаним до чужої форми. Чистий порт робить тест ядра **швидким, детермінованим і офлайновим**; це та сама причина, з якої заміна постачальника дешева, лише повернута іншим боком.

:::tabs
```ts
// tests/dispatch.test.ts — ядро перевіряємо БЕЗ мережі, підмінивши порт.
class FakeNotifier implements Notifier {
  public calls: { to: Recipient; event: DomainEvent }[] = [];
  constructor(private outcome: NotifyOutcome = { status: "delivered" }) {}
  async notify(to: Recipient, event: DomainEvent): Promise<NotifyOutcome> {
    this.calls.push({ to, event });
    return this.outcome;
  }
}

test("на retryable ядро призначає повтор", async () => {
  const fake = new FakeNotifier({ status: "retryable", reason: "test" });
  const dispatch = new OrderDispatch(fake);

  await dispatch.onCourierAssigned(order, customer);

  expect(fake.calls).toHaveLength(1);
  expect(fake.calls[0].event.kind).toBe("courier_near");
  expect(dispatch.pendingRetries).toContain(order.id);
});
```
```py
# tests/test_dispatch.py — ядро без мережі, підмінивши порт.
class FakeNotifier:                          # реалізує Notifier структурно
    def __init__(self, outcome: NotifyOutcome = NotifyOutcome.delivered()) -> None:
        self.calls: list[tuple[Recipient, DomainEvent]] = []
        self._outcome = outcome
    def notify(self, to: Recipient, event: DomainEvent) -> NotifyOutcome:
        self.calls.append((to, event))
        return self._outcome

def test_retry_scheduled_on_retryable():
    fake = FakeNotifier(NotifyOutcome.retryable("test"))
    dispatch = OrderDispatch(fake)

    dispatch.on_courier_assigned(order, customer)

    assert len(fake.calls) == 1
    assert isinstance(fake.calls[0][1], CourierNear)
    assert order.id in dispatch.pending_retries
```
```go
// dispatch_test.go — ядро без мережі, підмінивши порт.
type fakeNotifier struct {
    calls   []domain.Event
    outcome error
}

func (f *fakeNotifier) Notify(to domain.Recipient, e domain.Event) error {
    f.calls = append(f.calls, e)
    return f.outcome
}

func TestRetryScheduledOnRetryable(t *testing.T) {
    fake := &fakeNotifier{outcome: fmt.Errorf("test: %w", domain.ErrRetryable)}
    d := domain.Dispatch{Notifier: fake}

    d.OnCourierAssigned(order, customer)

    if len(fake.calls) != 1 {
        t.Fatalf("очікували 1 виклик, отримали %d", len(fake.calls))
    }
    if _, ok := fake.calls[0].(domain.CourierNear); !ok {
        t.Errorf("очікували подію CourierNear")
    }
}
```
:::

## Анти-патерн: протікаюча обгортка

Тепер найважливіший контраст усього прикладу, бо саме на ньому команди й спотикаються. Можна побудувати «шов», який нічого не ізолює, — і зовні він виглядатиме як шов. Це **протікаюча обгортка** (leaky wrapper): інтерфейс, що дзеркалить API постачальника один-в-один. Метод зветься, як у нього; приймає його об'єкт; повертає його відповідь. Формально шар є — а насправді чужа модель протекла крізь нього, як крізь друшляк.

```ts
// АНТИ-ПАТЕРН: порт-обгортка дзеркалить SendGrid. Чужі типи вже В ІНТЕРФЕЙСІ.
interface MailGateway {
  send(msg: SendGridMessage): Promise<SendGridResponse>;   // ← постачальник у сигнатурі
}
```

Слово «SendGrid» тут уже в **інтерфейсі** — тобто в ядрі, бо інтерфейс належить ядру. А отже воно розповзеться скрізь, де інтерфейс уживають:

```ts
// ...і ось як протікання розтікається ядром:
const resp = await gateway.send(toSendGridMessage(order)); // ядро БУДУЄ чужий об'єкт
if (resp.statusCode === 429) scheduleRetry(order);         // ядро ЧИТАЄ чужі коди
if (resp.statusCode === 202) markSent(order);
// а таких місць — десятки. Приходить SMTP, у якого НЕ буває 429 (є 421),
// і кожен цей "if" тихо бреше. Заміна постачальника = переписати ядро.
```

Різницю видно як на долоні. У чистому порті слово «SendGrid» жило **рівно в одному файлі** — адаптері, і заміна була локальна. У протікаючій обгортці воно живе **скрізь**, куди дотягнувся інтерфейс: ядро власноруч будує `SendGridMessage`, власноруч читає `statusCode === 429`, власноруч знає форму чужої відповіді. Такий «шов» коштує стільки ж, скільки чистий, а рятує рівно від нічого — навпаки, дає **оманливе відчуття захисту**, і це гірше, ніж узагалі без шва, бо без шва хоч ілюзій немає.

І протікати чуже вміє не лише через типи в сигнатурі — стережіться трьох тонших шпарин. Через **виняток**: якщо дати винятку `SendGridError` вилетіти з адаптера назовні, ядро мусить його ловити — і знову знає постачальника. Через **повернене значення**: якщо порт віддає чужий ідентифікатор листа як «доказ відправлення», ядро прив'язується до формату вендора. Через **семантику коду**: якщо повертати сирий `statusCode` замість доменного наслідку, ядро змушене тлумачити чужі числа. Правильний адаптер глушить усі три: перекладає винятки в доменний наслідок, не пропускає чужих ідентифікаторів у доменну модель, зводить будь-який код у трійку `delivered`/`retryable`/`rejected`.

> 🔧 **Навіщо це.** Тест на протікання простий: подивіться, чи згадується ім'я постачальника (тип, код помилки, виняток, поле відповіді) **деінде, крім тіла адаптера**. Знайшли `SendGridResponse` в ядрі, `statusCode === 429` у бізнес-логіці, `import { SendGridMessage }` у доменному файлі — шов діряний, і заміна постачальника буде переписуванням, хоч «інтерфейс же є». Чистий шов проходить тест мовчки: за межами одного файла постачальника не видно взагалі.

Цей прийом — не пускати чужу модель псувати вашу — має точну назву: [антикорупційний шар](root:sf-apps/anti-corruption-layer) (термін Еріка Еванса з «Domain-Driven Design», 2003). «Корупція», від якої він боронить, — це саме тихе просякання чужих понять у ваше ядро, аж поки ваша модель не стає викривленою тінню вендорської. Адаптер, що чесно перекладає в обидва боки, і є цей шар у дії.

## Коли шов не вартий заходу

Було б спокусливо вивести звідси правило «ховай усе чуже за портом» — і це була б протилежна помилка, теж дорога. Шов не безкоштовний: це зайвий шар, зайвий код, зайвий стрибок при читанні. Платити за нього варто лише там, де він щось дає, а дає він **право передумати** — опціон на заміну. Отже питання суто економічне, і його можна записати нерівністю:

```
став шов  ⟺  вартість_шва  <  ймовірність_зміни · вартість_зміни_без_шва
```

Права частина — це очікувана шкода від того, що передумати доведеться, а шва нема. Якщо вона більша за ціну шва — шов окупається; якщо менша — це витрачені гроші за опціон, яким ви не скористаєтесь. Прогляньмо кути цієї нерівності, бо вони дають чіткі «ні».

**Стандартна бібліотека мови.** Ви не зміните вбудований `JSON`, `fmt`, масив, HTTP-клієнт стандартної бібліотеки — ймовірність тут практично нуль, тож права частина ≈ 0, і будь-яка ціна шва програє. Обгортати стандартну бібліотеку у власний інтерфейс «про всяк випадок» — це купувати опціон, який ніколи не виконають. Просто вживайте її прямо.

**Ваше власне ядро.** Його ви теж не збираєтеся ні на що міняти — у тім і суть, що це ваша перевага, і вона лишається вашою. Шов «раптом замінимо свій рушій маршрутизації на чужий» суперечить самому рішенню, що маршрутизація — ядро. А якщо ви й справді допускаєте таку заміну — значить, це був не ядро, а фон, і питання не про шов, а про класифікацію.

**Дешева заміна навіть без шва.** Буває, що постачальника цілком імовірно зміните (права ймовірність висока), але заміна дешева й так — залежність дрібна, викликів мало, зібрати заново — година. Тоді права частина мала не через ймовірність, а через малу вартість зміни, і шов знову радше зайвий: він рятує від клопоту, якого й так майже нема.

Куди шов лягає — це **чужий фон, який імовірно зміниться і дорого коштуватиме міняти без нього**: SaaS-розсилка, платіжний шлюз, сховище файлів, зовнішня аналітика. Тут обидва множники великі — і постачальник цілком може розчарувати (ціна, закриття, розбіжність напряму), і без шва його виклики проростуть у сотні місць. Один шов там коштує кількох годин на старті й рятує місяці потім. Шов усюди — коштує місяців і не рятує нічого; ба більше, надлишок обгорток плодить діряві абстракції, що лише вдають ізоляцію, і код стає важчим читати без жодної вигоди.

## Пастки, що роблять шов діряним

Навіть узявшись за шов там, де треба, його легко зіпсувати так, що він тектиме. Кілька місць, де це стається найчастіше, — кожне з механізмом, а не просто пересторогою.

**Порт, спроєктований від вендора, а не від домену.** Найглибша пастка, бо непомітна. Якщо ви пишете інтерфейс, дивлячись у документацію постачальника, ви заб'єте його форму в порт, хоч би як гарно перейменували методи. Ліки — питати не «що вміє вендор», а «що потрібно **моєму домену**», і виводити сигнатуру звідти. Порт має читатися так, ніби постачальника не існує зовсім.

**Найменший спільний знаменник.** Коли постачальників двоє й більше, тягне звузити порт до того, що вміють **усі** — до перетину можливостей. Це псує домен заради адаптерів. Проєктуйте порт від того, що треба **домену**; якщо котрийсь вендор чогось не вміє — це клопіт його адаптера (емулювати або чесно повернути доменну відмову), а не привід калічити інтерфейс. Домен хоче лист потрібною мовою — SMTP-адаптер зверстає його локально, SendGrid-адаптер може вжити свої шаблони; порт від цього не міняється.

**Переклад помилок «за одним винятком».** Класифікація `retryable`/`rejected` — доменна, і кожен чужий код мусить у неї лягти. Спокуса пропустити «лише цей один» сирий код назовні — це тріщина, крізь яку чужа модель заллється назад. Або перекладаєте **все**, або шва нема.

**Ідемпотентність не в порті.** Реальна розсилка на повторі не сміє слати двічі — але «надіслати рівно раз» це доменна вимога, а не деталь вендора. Отже ключ ідемпотентності породжує домен і передає крізь порт, а кожен адаптер зобов'язується його шанувати. Сховаєте ідемпотентність в адаптер — вона загубиться при заміні постачальника.

**Підробка, що не тримає контракту.** Якщо тестова підробка поводиться інакше, ніж справжній адаптер, зелені тести брешуть: підробка пройшла, живий адаптер упаде. Тому контракт порту варто перевіряти **одним** набором тестів, ганяючи його і по підробці, і — в інтеграційних — по справжньому адаптеру.

**Бізнес-логіка, що заповзла в адаптер.** Який шаблон для якої події, якою мовою, кому не слати вночі — це доменна політика, і живе вона в домені (`renderEvent`), а не в адаптері. Адаптер лише переносить байти до постачальника. Заповзе політика в адаптер — при заміні вендора ви її втратите разом зі старим файлом.

**Розбухлий порт.** Інтерфейс із десятьма методами важко реалізувати кожному адаптеру й важко підмінити в тесті. `Notifier` має рівно один метод — і це не випадковість, а мета: маленький порт легко і реалізувати, і підробити. Коли порт розростається, це майже завжди знак, що в нього просочилися чужі можливості, яких домен не просив.

Складіть це докупи — і шов перестає бути магією й стає дешевою, зрозумілою механікою: один доменний порт, по адаптеру на постачальника, вибір на краю, підробка в тестах, і жодної згадки вендора поза єдиним файлом. Це коштує кількох годин уваги на старті. А повертає воно те єдине, чого не купиш потім за жодні гроші, коли постачальник підняв ціну втричі чи зник, — право спокійно поміняти адаптер за тиждень, поки решта системи навіть не помічає, що під нею щось змінилося.
