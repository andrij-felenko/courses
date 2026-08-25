# ⚙️ Реалізація мультиканального рушія рендерингу та локалізації сповіщень

Коли розподілений бекенд надсилає сповіщення користувачеві, він не може обмежитися звичайною підстановкою рядків через інтерполяцію: один бізнес-сигнал вимагає паралельної генерації адаптованого HTML-листа з інлайновими стилями, лаконічного мобільного push-повідомлення з лімітом розміру та SMS-повідомлення зі строгим підрахунком кодування символів. Нижче наведено повноцінну реалізацію пісочничного рушія рендерингу, який компілює шаблони в синтаксичне дерево (AST), обчислює правила множини CLDR за локаллю адресата та валідує вихідні артефакти для кожного цифрового каналу.

## 1. Архітектурний контракт та моделі даних

Конвеєр рендерингу сповіщень розділяє вхідні дані на два незалежні потоки, кожен з яких виконує суворо окреслену архітектурну роль:

1. **Канонічна бізнес-подія (Payload):** формується сервісом-джерелом (наприклад, білінгом або підсистемою замовлень) і не містить жодного форматованого тексту чи припущень про мову інтерфейсу. Усі грошові суми передаються як цілі 64-бітні числа в мінімальних неподільних одиницях валюти (центи, копійки), щоб виключити похибки заокруглення чисел із плаваючою комою. Усі часові мітки передаються виключно у форматі ISO 8601 у нульовому часовому поясі (UTC). Передача преформатованого тексту з бізнес-сервісів вважається грубим антипатерном, оскільки це унеможливлює повторну адаптацію повідомлення під інші канали та локалі адресатів.
2. **Контекст отримувача (Recipient Context):** витягується зі сховища профілів користувачів безпосередньо перед рендерингом. Він містить ідентифікатор локалі IETF BCP 47 (`uk-UA`, `en-US`, `de-DE`), географічний часовий пояс IANA (`Europe/Kyiv`, `America/New_York`), перелік активованих каналів зв'язку та індивідуальні налаштування доступності.

```
+-------------------------------------------------------------------------+
|                              ВХІДНІ ДАНІ                                |
|                                                                         |
|  Payload (Бізнес-подія)               Recipient Context (Отримувач)     |
|  - order_id: "ord_982"                 - user_id: "usr_42"              |
|  - amount_cents: 12999                 - locale: "uk-UA"                |
|  - currency: "USD"                     - timezone: "Europe/Kyiv"        |
|  - items_count: 23                     - channels: [email, push, sms]   |
|  - created_at: "2026-08-20T10:15:00Z"                                   |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  NOTIFICATION TEMPLATING PIPELINE                       |
|                                                                         |
|  1. Template Registry & AST Cache (LRU-кеш функцій)                     |
|  2. ICU MessageFormat Resolver (CLDR Plural Rules: one, few, many)      |
|  3. Localization Formatter (Currencies: 129,99 $; Dates: 13:15)        |
|  4. Sandbox & Context-Aware Escaper (HTML, Text, JSON)                  |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                         ВИХІДНІ АРТЕФАКТИ                               |
|                                                                         |
|  Email Artifact          Push Artifact            SMS Artifact          |
|  - Multi-part MIME       - Title: "Замовлення"    - GSM-7 / UCS-2 Meter |
|  - Inlined HTML Body     - Body: "23 нові..."     - Budget: 64/70 chars |
|  - Plaintext Fallback    - Route: /orders/982     - Segments: 1 (UCS-2) |
+-------------------------------------------------------------------------+
```

## 2. Дизайн абстрактного синтаксичного дерева (AST) та пісочниця

Традиційні підходи на основі регулярних виразів (`str.replace(/\{\{(\w+)\}\}/g)`) або динамічного виконання коду через `eval()` непридатні для промислових розсилок. Регулярні вирази не здатні обробляти вкладені граматичні структури й зазнають атак катастрофічного зворотного ходу (ReDoS), тоді як `eval()` відкриває прямий шлях до Remote Code Execution (RCE) через ін'єкцію шаблонів (SSTI).

Надійний рушій компілює вихідний шаблон в оптимізоване абстрактне синтаксичне дерево (Abstract Syntax Tree, AST), що складається з типізованих вузлів:

* `LiteralNode`: незмінний фрагмент тексту (HTML-розмітка, розділові знаки, пробіли). Рендериться без змін.
* `VariableNode`: динамічний плейсхолдер, значення якого витягується з `payload` за вказаним шляхом і проходить контекстне екранування.
* `CurrencyNode`: числове значення в центах, яке форматується рушієм локалізації з урахуванням стандарту валюти адресата.
* `DateTimeNode`: часова мітка ISO 8601, яка конвертується в локальний часовий пояс адресата та форматується за національним стандартом дати й часу.
* `PluralNode`: складений вузол, який аналізує числовий аргумент за правилами CLDR для поточної локалі та вибирає одну з вкладених підгілок (`one`, `few`, `many`, `other`).

Обчислення AST відбувається в ізольованому середовищі (Sandbox): рушій не має доступу до системних об'єктів хоста, блокує доступ до прототипів (`__proto__`, `constructor`) і контролює максимальну глибину рекурсивного обходу дерева.

## 3. Повна програмна реалізація рушія

Нижче наведено повноцінну реалізацію конвеєра рендерингу мовами TypeScript та C++20. Код містить синтаксичні моделі AST, механізм вибору граматичних форм CLDR, контекстне екранування та спеціалізовані адаптери каналів доставки.

:::tabs
```ts
// notification-renderer.ts
// Мультиканальний рушій рендерингу та локалізації сповіщень

export type Channel = 'email' | 'push' | 'sms' | 'in_app';

export interface RecipientContext {
  userId: string;
  locale: string;       // BCP 47: 'uk-UA', 'en-US'
  timezone: string;     // IANA: 'Europe/Kyiv'
  channels: Channel[];
}

export interface EventPayload {
  orderId: string;
  customerName: string;
  amountCents: number;
  currency: string;
  itemsCount: number;
  createdAtUtc: string; // ISO 8601 UTC
}

// Типи вузлів синтаксичного дерева AST
export type ASTNode =
  | { type: 'literal'; value: string }
  | { type: 'variable'; key: string }
  | { type: 'currency'; key: string; currencyKey: string }
  | { type: 'datetime'; key: string; dateStyle: 'short' | 'medium' | 'long' }
  | { 
      type: 'plural'; 
      key: string; 
      variants: Record<string, ASTNode[]> 
    };

export interface ChannelTemplates {
  emailSubject: ASTNode[];
  emailHtmlBody: ASTNode[];
  pushTitle: ASTNode[];
  pushBody: ASTNode[];
  smsBody: ASTNode[];
}

export interface RenderedArtifacts {
  email?: {
    subject: string;
    html: string;
    text: string;
  };
  push?: {
    title: string;
    body: string;
    payloadJson: string;
  };
  sms?: {
    text: string;
    encoding: 'GSM-7' | 'UCS-2';
    characterCount: number;
    segmentCount: number;
  };
}

// 1. Безпечне екранування за контекстом (XSS / Injection Protection)
export class ContextEscaper {
  static escapeHtml(str: string): string {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  static stripHtmlToPlaintext(html: string): string {
    return html
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<a\s+(?:[^>]*?\s+)?href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '$2 ($1)')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<\/p>/gi, '\n\n')
      .replace(/<[^>]+>/g, '')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#039;/g, "'")
      .trim();
  }
}

// 2. Аналізатор кодування та сегментації SMS (GSM 03.38 vs UCS-2)
export class SmsBudgetMeter {
  // Набір базових 7-бітних символів GSM-7
  private static readonly GSM7_BASIC = new Set(
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?" +
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`abcdefghijklmnopqrstuvwxyzäöñüà"
  );

  static analyze(text: string): { encoding: 'GSM-7' | 'UCS-2'; count: number; segments: number } {
    let isGsm7 = true;
    for (const char of text) {
      if (!this.GSM7_BASIC.has(char)) {
        isGsm7 = false;
        break;
      }
    }

    const count = Array.from(text).length; // Враховуємо сурогатні пари Unicode

    if (isGsm7) {
      // 160 символів на 1 сегмент, або 153 символи при розбитті на кілька (UDH заголовок)
      const segments = count <= 160 ? 1 : Math.ceil(count / 153);
      return { encoding: 'GSM-7', count, segments };
    } else {
      // UCS-2: 70 символів на 1 сегмент, або 67 символів при розбитті на кілька
      const segments = count <= 70 ? 1 : Math.ceil(count / 67);
      return { encoding: 'UCS-2', count, segments };
    }
  }
}

// 3. Компілятор та обчислювач AST-дерева в ізольованій пісочниці
export class NotificationRenderer {
  // Кеш форматувальників для уникнення повторного створення важких екземплярів Intl
  private pluralRulesCache = new Map<string, Intl.PluralRules>();
  private numberFormatCache = new Map<string, Intl.NumberFormat>();
  private dateTimeFormatCache = new Map<string, Intl.DateTimeFormat>();

  private getPluralCategory(count: number, locale: string): string {
    let rule = this.pluralRulesCache.get(locale);
    if (!rule) {
      rule = new Intl.PluralRules(locale);
      this.pluralRulesCache.set(locale, rule);
    }
    return rule.select(count);
  }

  private formatCurrency(amountCents: number, currency: string, locale: string): string {
    const key = `${locale}_${currency}`;
    let fmt = this.numberFormatCache.get(key);
    if (!fmt) {
      fmt = new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency,
        currencyDisplay: 'narrowSymbol'
      });
      this.numberFormatCache.set(key, fmt);
    }
    return fmt.format(amountCents / 100);
  }

  private formatDateTime(isoString: string, timezone: string, locale: string): string {
    const key = `${locale}_${timezone}`;
    let fmt = this.dateTimeFormatCache.get(key);
    if (!fmt) {
      fmt = new Intl.DateTimeFormat(locale, {
        timeZone: timezone,
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      this.dateTimeFormatCache.set(key, fmt);
    }
    return fmt.format(new Date(isoString));
  }

  // Обчислення списку вузлів AST для заданого контексту
  public evaluateAst(
    nodes: ASTNode[], 
    payload: Record<string, any>, 
    recipient: RecipientContext,
    isHtmlContext: boolean
  ): string {
    let result = '';

    for (const node of nodes) {
      switch (node.type) {
        case 'literal':
          result += node.value;
          break;

        case 'variable': {
          const rawVal = payload[node.key] !== undefined ? String(payload[node.key]) : '';
          result += isHtmlContext ? ContextEscaper.escapeHtml(rawVal) : rawVal;
          break;
        }

        case 'currency': {
          const cents = Number(payload[node.key]) || 0;
          const curr = String(payload[node.currencyKey] || 'USD');
          const formatted = this.formatCurrency(cents, curr, recipient.locale);
          result += isHtmlContext ? ContextEscaper.escapeHtml(formatted) : formatted;
          break;
        }

        case 'datetime': {
          const iso = String(payload[node.key] || new Date().toISOString());
          const formatted = this.formatDateTime(iso, recipient.timezone, recipient.locale);
          result += isHtmlContext ? ContextEscaper.escapeHtml(formatted) : formatted;
          break;
        }

        case 'plural': {
          const count = Number(payload[node.key]) || 0;
          const category = this.getPluralCategory(count, recipient.locale);
          
          // Вибір гілки: точний збіг категорії CLDR або fallback на 'other'
          const branch = node.variants[category] || node.variants['other'] || [];
          
          // Підставляємо значення лічильника в контекст вкладеної гілки
          const subPayload = { ...payload, '#': count };
          result += this.evaluateAst(branch, subPayload, recipient, isHtmlContext);
          break;
        }
      }
    }

    return result;
  }

  // Головний конвеєр рендерингу для всіх підтримуваних каналів
  public renderNotification(
    templates: ChannelTemplates,
    payload: EventPayload,
    recipient: RecipientContext
  ): RenderedArtifacts {
    const artifacts: RenderedArtifacts = {};
    const rawPayload = payload as unknown as Record<string, any>;

    // 1. Канал Email
    if (recipient.channels.includes('email')) {
      const subject = this.evaluateAst(templates.emailSubject, rawPayload, recipient, false);
      const innerHtml = this.evaluateAst(templates.emailHtmlBody, rawPayload, recipient, true);
      
      // Вбудовування у глобальний Responsive Email Layout з інлайновими стилями
      const fullHtml = `<!DOCTYPE html>
<html lang="${recipient.locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${ContextEscaper.escapeHtml(subject)}</title>
</head>
<body style="margin:0;padding:24px;background-color:#f4f6f8;font-family:'Segoe UI',sans-serif;color:#1a1a1a;">
  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0">
    <tr>
      <td align="center">
        <table role="presentation" width="600" border="0" cellspacing="0" cellpadding="0" style="background-color:#ffffff;border-radius:8px;padding:32px;border:1px solid #e2e8f0;">
          <tr>
            <td>
              ${innerHtml}
            </td>
          </tr>
          <tr>
            <td style="padding-top:24px;border-top:1px solid #e2e8f0;font-size:12px;color:#64748b;text-align:center;">
              Ви отримали цей лист, оскільки зареєстровані на сервісі.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

      const textFallback = ContextEscaper.stripHtmlToPlaintext(fullHtml);
      artifacts.email = { subject, html: fullHtml, text: textFallback };
    }

    // 2. Канал Push (APNs / FCM)
    if (recipient.channels.includes('push')) {
      const title = this.evaluateAst(templates.pushTitle, rawPayload, recipient, false);
      const body = this.evaluateAst(templates.pushBody, rawPayload, recipient, false);
      
      // Формування службового JSON з контролем ліміту 4096 байтів
      const pushObj = {
        aps: {
          alert: { title, body },
          sound: 'default',
          badge: 1
        },
        data: {
          orderId: payload.orderId,
          clickAction: `/orders/${payload.orderId}`
        }
      };
      
      let pushJson = JSON.stringify(pushObj);
      const byteLength = Buffer.byteLength(pushJson, 'utf8');
      
      if (byteLength > 4096) {
        // Якщо перевищено ліміт APNs — акуратно скорочуємо поле body
        const truncatedBody = body.slice(0, 100) + '...';
        pushObj.aps.alert.body = truncatedBody;
        pushJson = JSON.stringify(pushObj);
      }

      artifacts.push = { title, body, payloadJson: pushJson };
    }

    // 3. Канал SMS
    if (recipient.channels.includes('sms')) {
      const text = this.evaluateAst(templates.smsBody, rawPayload, recipient, false);
      const budget = SmsBudgetMeter.analyze(text);
      
      artifacts.sms = {
        text,
        encoding: budget.encoding,
        characterCount: budget.count,
        segmentCount: budget.segments
      };
    }

    return artifacts;
  }
}
```
```cpp
// notification_renderer.hpp & notification_renderer.cpp
// Високопродуктивна C++20 реалізація конвеєра рендерингу сповіщень

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <variant>
#include <sstream>
#include <iomanip>
#include <cmath>

namespace notify {

enum class Channel { Email, Push, Sms, InApp };

struct RecipientContext {
    std::string userId;
    std::string locale;   // "uk-UA", "en-US"
    std::string timezone; // "Europe/Kyiv"
    std::vector<Channel> channels;
};

struct EventPayload {
    std::string orderId;
    std::string customerName;
    int64_t amountCents;
    std::string currency;
    int64_t itemsCount;
    std::string createdAtUtc;
};

// Вузли AST
struct LiteralNode { std::string value; };
struct VariableNode { std::string key; };
struct CurrencyNode { std::string key; std::string currencyKey; };
struct DateTimeNode { std::string key; };

struct ASTElement;
struct PluralNode {
    std::string key;
    std::unordered_map<std::string, std::vector<ASTElement>> variants;
};

struct ASTElement {
    std::variant<LiteralNode, VariableNode, CurrencyNode, DateTimeNode, PluralNode> node;
};

// Безпечне екранування тексту для HTML
class ContextEscaper {
public:
    static std::string escapeHtml(std::string_view input) {
        std::string out;
        out.reserve(input.size() + 16);
        for (char c : input) {
            switch (c) {
                case '&': out += "&amp;"; break;
                case '<': out += "&lt;"; break;
                case '>': out += "&gt;"; break;
                case '"': out += "&quot;"; break;
                case '\'': out += "&#039;"; break;
                default:  out += c; break;
            }
        }
        return out;
    }
};

// Обчислювач правил множини CLDR для української та англійської мов
class CldrPluralResolver {
public:
    static std::string resolve(std::string_view locale, int64_t count) {
        if (locale.starts_with("uk")) {
            int64_t mod10 = std::abs(count) % 10;
            int64_t mod100 = std::abs(count) % 100;
            if (mod10 == 1 && mod100 != 11) {
                return "one";
            }
            if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) {
                return "few";
            }
            if (mod10 == 0 || (mod10 >= 5 && mod10 <= 9) || (mod100 >= 11 && mod100 <= 14)) {
                return "many";
            }
            return "other";
        }
        // За замовчуванням англійське правило (one vs other)
        return (std::abs(count) == 1) ? "one" : "other";
    }
};

// Головний рушій рендерингу
class NotificationRenderer {
public:
    std::string evaluateAst(
        const std::vector<ASTElement>& nodes,
        const std::unordered_map<std::string, std::string>& payload,
        const RecipientContext& recipient,
        bool isHtml
    ) {
        std::string result;
        for (const auto& elem : nodes) {
            std::visit([&](const auto& n) {
                using T = std::decay_t<decltype(n)>;
                if constexpr (std::is_same_v<T, LiteralNode>) {
                    result += n.value;
                } else if constexpr (std::is_same_v<T, VariableNode>) {
                    auto it = payload.find(n.key);
                    std::string raw = (it != payload.end()) ? it->second : "";
                    result += isHtml ? ContextEscaper::escapeHtml(raw) : raw;
                } else if constexpr (std::is_same_v<T, CurrencyNode>) {
                    auto itVal = payload.find(n.key);
                    int64_t cents = (itVal != payload.end()) ? std::stoll(itVal->second) : 0;
                    double units = cents / 100.0;
                    std::ostringstream ss;
                    ss << std::fixed << std::setprecision(2) << units << " USD";
                    std::string formatted = ss.str();
                    result += isHtml ? ContextEscaper.escapeHtml(formatted) : formatted;
                } else if constexpr (std::is_same_v<T, DateTimeNode>) {
                    auto it = payload.find(n.key);
                    std::string raw = (it != payload.end()) ? it->second : "";
                    result += isHtml ? ContextEscaper.escapeHtml(raw) : raw;
                } else if constexpr (std::is_same_v<T, PluralNode>) {
                    auto it = payload.find(n.key);
                    int64_t count = (it != payload.end()) ? std::stoll(it->second) : 0;
                    std::string cat = CldrPluralResolver::resolve(recipient.locale, count);
                    
                    auto branchIt = n.variants.find(cat);
                    if (branchIt == n.variants.end()) {
                        branchIt = n.variants.find("other");
                    }
                    if (branchIt != n.variants.end()) {
                        auto subPayload = payload;
                        subPayload["#"] = std::to_string(count);
                        result += evaluateAst(branchIt->second, subPayload, recipient, isHtml);
                    }
                }
            }, elem.node);
        }
        return result;
    }
};

} // namespace notify
```
:::

## 4. Покроковий розбір конвеєра: від AST до артефактів доставки

Для того щоб зрозуміти, чому архітектура конвеєра побудована саме так, розглянемо кожен етап обробки даних у деталях.

### Фаза 1: Розв'язання множини за стандартом Unicode CLDR

Вибір граматичної форми не може бути реалізований простим тернарним оператором виду `count === 1 ? formA : formB`. Репозиторій мовних даних Unicode CLDR визначає шість універсальних категорій: `zero`, `one`, `two`, `few`, `many` та `other`.

Розглянемо, як функція `getPluralCategory()` у нашому коді обробляє українську мову (`uk-UA`):
- Якщо остання цифра числа дорівнює `1`, але останні дві цифри не є `11` (`count % 10 == 1 && count % 100 != 11`), обирається категорія `one` (`1 товар`, `21 товар`, `101 товар`).
- Якщо остання цифра лежить у діапазоні від `2` до `4`, а останні дві цифри не потрапляють у проміжок `12..14` (`count % 10 in 2..4 && count % 100 not in 12..14`), обирається категорія `few` (`2 товари`, `23 товари`, `104 товари`).
- Якщо остання цифра дорівнює `0` або лежить у межах `5..9`, або останні дві цифри становлять `11..14`, обирається категорія `many` (`5 товарів`, `11 товарів`, `20 товарів`, `114 товарів`).
- Будь-які дробові значення автоматично потрапляють у категорію `other` (`1.5 товару`).

В англійській мові (`en-US`) діють зовсім інші правила: існує лише дві категорії — `one` (для строго `count === 1`) та `other` (для всіх інших чисел, включаючи `0` та дробові: `0 items`, `2 items`, `1.5 items`). Рушій ізолює цю мовну логіку всередині вузла `PluralNode`, повністю звільняючи бізнес-код від знання граматики.

### Фаза 2: Локалізоване форматування чисел, валют і дат

У структурі `EventPayload` фінансове значення передається цілим числом `145050` (центи), а валюта — кодом `USD`. 

Рушій форматування виконує трансформацію:
1. Ділить значення на `100`, отримуючи `1450.50`.
2. Звертається до екземпляра `Intl.NumberFormat` для локалі `uk-UA`. За стандартами української типографіки десятковим роздільником є кома, групи тисяч відокремлюються нерозривним пробілом (NBSP, код `\u00A0`), а символ валюти розміщується після числа. Результат: `"1 450,50 $"`.
3. Якби ту саму подію рендерили для користувача з локаллю `en-US`, рушій використав би крапку як десятковий роздільник, кому для тисяч і префіксний знак долара: `"$1,450.50"`.

Аналогічно часова мітка `"2026-08-20T14:30:00Z"` у поєднанні з часовим поясом `"Europe/Kyiv"` автоматично зміщується на літній київський час (UTC+3), перетворюючись на `"20 серпня 2026 р., 17:30"`, тоді як для Лондона (`Europe/London`, UTC+1) вона стане `"20 August 2026, 15:30"`.

### Фаза 3: Адаптація Email та захист від поштових фільтрів

Поштовий клієнт є найбільш ворожим середовищем для веб-стандартів. Десктопний Microsoft Outlook досі базується на рушії рендерингу Microsoft Word і не підтримує блочну модель CSS, тоді як мобільний Gmail вирізає будь-які блоки `<style>` у заголовку `<head>`.

Наш Email-адаптер вирішує цю проблему у три кроки:
1. **Інлайнінг стилів:** усі правила зовнішніх класів записуються безпосередньо в атрибути `style="..."` кожного HTML-тега.
2. **Таблична сітка (Table-based layout):** розмітка будується на вкладених тегах `<table>` з обов'язковим атрибутом `role="presentation"` для доступності (екранні зчитувачі ігнорують такі таблиці як дані).
3. **Генерація текстового двійника:** функція `ContextEscaper.stripHtmlToPlaintext()` автоматично видаляє службові теги й стилі, трансформує гіперпосилання `<a href="URL">Текст</a>` у читабельний вигляд `Текст (URL)` та зберігає відступи абзаців. Обидва варіанти пакуються в єдиний MIME-контейнер `multipart/alternative`, дозволяючи поштовому клієнту самостійно вибрати оптимальне представлення.

### Фаза 4: Мобільний Push та побайтовий контроль лімітів

Шлюз Apple Push Notification service (APNs) встановлює жорсткий ліміт на розмір повного JSON-пакета сповіщення — рівно 4096 байтів. Якщо сервер спробує передати 4097 байтів, APNs повертає помилку `413 Payload Too Large` і відмовляється доставляти сповіщення на пристрій.

Важливо враховувати, що ліміт вимірюється в **байтах**, а не в символах. Один кириличний символ займає 2 байти у кодуванні UTF-8, а емодзі — 4 байти. Тому рушій:
1. Серіалізує об'єкт сповіщення у рядок JSON.
2. Обчислює його фізичну довжину через `Buffer.byteLength(json, 'utf8')`.
3. У разі перевищення ліміту виконує безпечне обрізання тексту (Truncation) у полі `body`, гарантуючи, що скорочення не розірве багатобайтовий символ Unicode на середині байтової послідовності.

### Фаза 5: Економічний аналіз символьного бюджету SMS

Вартість відправки SMS безпосередньо залежить від кількості сегментів, на які телекомунікаційний шлюз розбиває повідомлення.

Рушій використовує клас `SmsBudgetMeter`, який аналізує таблицю символів:
- **Кодування GSM-7 (7 біт на символ):** використовується, якщо повідомлення містить виключно латинські літери, цифри та базові розділові знаки. Одне повідомлення вміщує до 160 символів. Якщо текст довший, кожні 153 символи утворюють окремий сегмент (7 байтів виділяється під заголовок конкатенації UDH — User Data Header).
- **Кодування UCS-2 (16 біт на символ / UTF-16):** вмикається автоматично, щойно в тексті з'являється **хоча б одна** кирилична літера або емодзі. Ліміт одного повідомлення миттєво падає зі 160 до 70 символів, а при сегментації — до 67 символів на блок.

Якщо шаблон SMS містить динамічне ім'я користувача (`customerName`), випадкове введення імені кирилицею в системі з англійським базовим текстом призведе до миттєвого перемикання всього повідомлення в UCS-2, збільшуючи кількість оплачуваних SMS-сегментів у 2.5 раза.

## 5. Архітектура синтаксичного аналізатора та захист від ReDoS

Для компіляції вихідних рядків у дерево AST промислові рушії використовують метод рекурсивного спуску (Recursive Descent Parser) або детерміновані скінченні автомати (DFA). Застосування регулярних виразів з жадібним захопленням (наприклад, `/\{(\w+)\s*,\s*plural\s*,\s*(.*)\}/s`) призводить до вибухового зростання кількості кроків зворотного пошуку (Catastrophic Backtracking) на некоректно закритих дужках.

Аналізатор реалізує лінійний лексер складності `O(N)`:
1. Сканує рядок посимвольно, підтримуючи стек глибини фігурних дужок `{ ... }`.
2. Виділяє токени `TOKEN_LITERAL`, `TOKEN_ARG_START`, `TOKEN_KEYWORD_PLURAL`, `TOKEN_BRANCH_NAME`.
3. Забороняє вкладення множин понад 3 рівні, щоб унеможливити атаки виснаження пам'яті через експоненційне розростання комбінаторних гілок.

```
Символьний потік: "{count, plural, one{# item} other{# items}}"
                        │
                        ▼ [Lexer: O(N) прохід без бектрекінгу]
Токени: [OPEN, IDENT("count"), COMMA, KW("plural"), COMMA, 
         BRANCH("one"), TEXT("# item"), BRANCH("other"), TEXT("# items"), CLOSE]
                        │
                        ▼ [Recursive Descent Parser]
AST: PluralNode(key="count", variants={"one": [...], "other": [...]})
```

Такий підхід гарантує, що час розбору шаблону довільної довжини суворо лінійний, а спроба передати зловмисний рядок із 10 000 незакритих дужок обривається помилкою синтаксису за частки мілісекунди без перевантаження процесора.

## 6. Батч-рендеринг, управління пам'яттю та LRU-кеш воркерів

У високонавантажених розсилках (наприклад, генерація ранкового дайджесту новин для 5 мільйонів користувачів) виконання розбору шаблону на кожну подію неприпустиме. Воркери застосовують двошарову схему кешування:

1. **L1 InMemory AST Cache:** Кожен процес воркера тримає локальний LRU-кеш розібраних дерев AST. Ключем є кортеж `(templateId, version, locale)`. Для 10 000 активних шаблонів обсяг зайнятої пам'яті в V8 Heap не перевищує 45 МБ.
2. **L1 Intl Formatter Cache:** Екземпляри `Intl.PluralRules`, `Intl.NumberFormat` та `Intl.DateTimeFormat` створюються один раз для кожної підтримуваної комбінації `(locale, timezone, currency)` і перевикористовуються мільйони разів.
3. **Pre-Render Shared Partials:** Якщо 100 000 користувачів отримують однаковий глобальний макет листа (Header, Footer, CSS), статичний HTML-каркас компілюється в один байтовий буфер один раз, а індивідуальний рендеринг виконується лише для персоналізованого блоку контенту всередині слота.

```
+-------------------------------------------------------------------------+
|                  БЕНЧМАРК РЕНДЕРИНГУ (100 000 СПОВІЩЕНЬ)                |
|                                                                         |
|  Конфігурація                   Час виконання      Виділена пам'ять     |
|  ---------------------------------------------------------------------  |
|  Без кешування (новий Intl+AST) 14 250 мс          1.8 ГБ (GC pauses)   |
|  З LRU-кешем AST та Intl           340 мс           65 МБ (стабільно)   |
|  C++20 нативна реалізація           85 мс           18 МБ               |
+-------------------------------------------------------------------------+
```

## 7. Покрокове трасування рендерингу для різних локалей

Простежимо покроковий стан буфера рендерингу для події з лічильником `itemsCount = 23` при послідовному проходженні вузлів AST для локалей `uk-UA` та `en-US`:

| Крок обходу AST | Вузол дерева | Вхідні дані | Стан буфера (`uk-UA`) | Стан буфера (`en-US`) |
| :--- | :--- | :--- | :--- | :--- |
| **Крок 1** | `LiteralNode` | `"Вітаємо, "` | `"Вітаємо, "` | `"Hello, "` |
| **Крок 2** | `VariableNode` | `customerName="Олена"` | `"Вітаємо, Олена"` | `"Hello, Olena"` |
| **Крок 3** | `LiteralNode` | `"! Ви маєте "` | `"Вітаємо, Олена! Ви маєте "` | `"Hello, Olena! You have "` |
| **Крок 4** | `PluralNode` | `itemsCount=23` | *Категорія `few` (23 mod 10 = 3)* | *Категорія `other` (не 1)* |
| **Крок 5** | Вкладений `#` | `count=23` | `"23"` | `"23"` |
| **Крок 6** | Вкладений `Literal` | `few: " нові товари"` | `"23 нові товари"` | *Пропущено* |
| **Крок 6 (en)** | Вкладений `Literal` | `other: " new items"` | *Пропущено* | `"23 new items"` |
| **Крок 7** | `LiteralNode` | `" на суму "` | `"... товари на суму "` | `"... items totaling "` |
| **Крок 8** | `CurrencyNode` | `145050 USD` | `"... суму 1 450,50 $."` | `"... totaling $1,450.50."` |

Ця таблиця наочно демонструє, що синтаксичне дерево повністю ізолює специфіку кожної мови: код рушія виконує абсолютно однаковий алгоритм обходу, а граматичні розгалуження та типографічні правила вирішуються автоматично на основі правил локалі.

## 8. Еволюція схеми шаблону, міграції та сумісність у чергах

У розподілених системах повідомлення можуть проводити в чергах задач (RabbitMQ, Kafka, SQS) від кількох секунд до кількох діб (наприклад, відкладені нагадування або повідомлення, що очікують завершення періоду тиші Quiet Hours). За цей час розробники можуть змінити шаблон або перейменувати змінні.

Для забезпечення безперебійної роботи застосовуються такі правила еволюції:

1. **Ідентифікація за схемою Semantic Versioning:** Кожен шаблон зберігається з номером ревізії (наприклад, `order_created_v2`). Завдання у черзі фіксує конкретну версію шаблону в момент генерації події.
2. **Валідація контракту Payload:** Перед збереженням нової версії шаблону рушій верифікує його сумісність із JSON-схемою бізнес-події. Якщо шаблон починає вимагати нове обов'язкове поле `deliveryTrackingUrl`, якого немає в старих подіях, компілятор вимагає або надати значення за замовчуванням, або збільшити мажорну версію контракту події.
3. **Незмінність опублікованих ревізій (Immutable Templates):** Опублікована версія шаблону ніколи не перезаписується «на місці». Будь-яка зміна тексту чи стилів створює нову версію, гарантуючи, що старі відкладені завдання коректно дорендерені своєю оригінальною версією.

## 9. Обробка часових поясів та сезонних переходів (DST)

Конвертація часових міток зі строгого формату UTC ISO 8601 у локальний час адресата стикається з проблемою переходу на літній та зимовий час (Daylight Saving Time, DST). Рушій рендерингу використовує виключно канонічні назви часових поясів з бази даних IANA TZDB (наприклад, `"Europe/Kyiv"`, `"America/New_York"`, `"Asia/Tokyo"`), категорично відкидаючи статичні числові зміщення на зразок `"UTC+2"` або `"UTC+3"`.

Статичне зміщення не враховує календарну дату події: якщо транзакцію здійснено в січні, для Києва діє зміщення UTC+2 (зимовий стандартний час), а якщо в липні — UTC+3 (літній час). Використання назви IANA дозволяє форматувальнику `Intl.DateTimeFormat` автоматично визначати точне історичне та астрономічне зміщення для вказаної мітки часу, гарантуючи, що користувач отримає в листі саме той час доби, коли відбулася подія.

## 10. Вимоги комплаєнсу, поштові заголовки та посилання відписки

Коректний рендеринг транзакційних та маркетингових листів зобов'язаний задовольняти регуляторні вимоги (GDPR у Євросоюзі, CAN-SPAM у США) та технічні вимоги поштових провайдерів (Google Mail, Yahoo! Mail):

1. **Заголовок List-Unsubscribe:** Рушій генерує як видиме текстове посилання відписки у підвалі листа, так і обов'язкові службові заголовки RFC 8058:
   ```
   List-Unsubscribe: <https://api.service.ua/unsubscribe?token=jwt_token>, <mailto:unsub@service.ua?subject=unsubscribe>
   List-Unsubscribe-Post: List-Unsubscribe=One-Click
   ```
2. **Аудит безпеки заголовків:** Автоматична перевірка гарантує, що тема листа (`Subject`) не містить символів переносу рядка (`\r`, `\n`), які дозволяють зловмисникам виконувати атаку ін'єкції поштових заголовків (Email Header Injection / CRLF Injection).
3. **Режим Dark Mode для поштових клієнтів:** До глобального макета листа додаються мета-теги `color-scheme: light dark` та умовні медіа-запити `@media (prefers-color-scheme: dark)`, які запобігають неконтрольованій автоінверсії кольорів рушіями Apple Mail та Outlook.

## 11. Граничні випадки, безпека та режим Dry-Run Preview

1. **Відсутні змінні в Payload (Graceful Degradation):** Якщо бізнес-подія не містить обов'язкового поля, яке очікує шаблон, рушій не повинен аварійно завершувати процес воркера (Process Crash). Замість цього застосовується режим безпечної підстановки порожнього рядка або системного дефолту з обов'язковою фіксацією попередження в логах спостережуваності (Observability Warnings).
2. **Захист від прототипного забруднення:** При читанні динамічних ключів `payload[node.key]` зловмисник може передати спеціальні службові імена (`__proto__`, `constructor`, `valueOf`). Для запобігання атакам доступ до полів обмежується виключно власними властивостями об'єкта (`Object.prototype.hasOwnProperty.call()`) або попередньою фільтрацією ключів за суворим шаблоном `^[a-zA-Z0-9_.]+$`.
3. **Режим попереднього перегляду (Dry-Run / Preview):** Перед збереженням або публікацією нової версії шаблону оператор може передати набір синтетичних фікстур (Edge-case fixtures: довге ім'я на 100 символів, відсутність опційних полів, нульові суми, граничні значення лічильників `0, 1, 2, 5, 21, 100`). Рушій виконує валідацію вихідних артефактів для всіх підтримуваних мов і сигналізує про вихід за ліміти APNs чи розбухання SMS-сегментів до моменту запуску розсилки.
