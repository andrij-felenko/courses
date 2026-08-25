# ⚙️ Реалізація рушія узгодження вмісту за RFC 9110

Розробка надійного та швидкого диспетчера узгодження вмісту для високонавантаженого веб-сервера або API-шлюзу вимагає значно більшого, ніж простий пошук підрядка чи виклик стандартних функцій поділу рядків. Протокол HTTP (RFC 9110) вимагає коректного розбору складних заголовків із якісними коефіцієнтами, точного обчислення специфічності виразів, підтримки підстановочних знаків, ієрархічного відкату мовних локалей за стандартом BCP 47 та автоматичного формування заголовка `Vary`.

Цей проєкт демонструє побудову завершеного, потокобезпечного та оптимізованого модуля узгодження вмісту, спроєктованого для роботи у складі проміжного програмного забезпечення (middleware) або зворотного проксі-сервера.

---

## 1. Архітектура та математика зіставлення

Процес прийняття рішення про віддачу того чи іншого представлення складається з п'яти послідовних фаз, кожна з яких ізольована у відповідних структурах даних.

```
Вхідний запит: Accept, Accept-Language
        │
        ▼
[Фаза 1: Токенізація та парсинг ABNF]
  • Розділення списку за комами (з урахуванням лапок)
  • Виділення типу, підтипу, параметрів та коефіцієнта q
        │
        ▼
[Фаза 2: Обчислення ваги та специфічності]
  • Розрахунок рангу (0..3) за структурою MIME-типу
  • Валідація діапазону q ∈ [0.000, 1.000]
        │
        ▼
[Фаза 3: Зіставлення з можливостями сервера]
  • Порівняння кожного серверного варіанта з клієнтськими фільтрами
  • Виключення заборонених форматів (q = 0)
        │
        ▼
[Фаза 4: Ранжування та вирішення колізій]
  • Сортування за кортежем (q DESC, specificity DESC, server_order ASC)
        │
        ▼
[Фаза 5: Формування результату та метаданих]
  • Вибір переможця або повернення статусу 406
  • Генерація списку полів для заголовка Vary
```

### Математична модель ранжування

Нехай `S = {s₁, s₂, ..., sₙ}` — впорядкована множина представлень, які сервер здатен згенерувати для цього ресурсу (порядок елементів відображає внутрішній пріоритет бекенду).

Нехай `C = {c₁, c₂, ..., cₘ}` — множина правил, витягнутих із клієнтського заголовка `Accept`. Кожне правило `c` характеризується вектором властивостей:

```
c = ( type, subtype, params, q, specificity, client_index )
```

Правило `c` покриває серверний варіант `s` (позначається `c ⊳ s`), якщо виконуються три умови:
1. `c.type == "*"` або `c.type == s.type`;
2. `c.subtype == "*"` або `c.subtype == s.subtype`;
3. Усі додаткові параметри, вказані в `c.params` (крім `q`), присутні в `s.params` з ідентичними значеннями.

Для кожної пари `(c, s)`, де `c ⊳ s` і `c.q > 0`, обчислюється векторний ранг сумісності:

```
Rank(c, s) = ⟨ c.q,  c.specificity,  −Index(s, S),  −c.client_index ⟩
```

Порівняння двох кандидатів здійснюється лексикографічно за координатами вектора `Rank`:
- **Координата 1 (`c.q`)**: Перевага клієнта. Кандидат із більшим `q` завжди виграє.
- **Координата 2 (`c.specificity`)**: Рівень точності правила за стандартом RFC 9110:
  - `3` — точний тип із параметрами (наприклад, `application/json; version=2`);
  - `2` — точний тип без параметрів (наприклад, `application/json`);
  - `1` — родина підтипів (наприклад, `text/*`);
  - `0` — глобальний підстановочний знак (`*/*`).
- **Координата 3 (`−Index(s, S)`)**: Якщо клієнтські коефіцієнти якості та специфічність однакові, перемагає той серверний формат, який розробники розмістили раніше у внутрішній конфігурації.
- **Координата 4 (`−c.client_index`)**: Якщо все попереднє рівне, зберігається початковий порядок у заголовку клієнта.

---

## 2. Мовне узгодження за RFC 4647 (Matching of Language Tags)

Окрім форматів медіа, промисловий диспетчер зобов'язаний узгоджувати природні мови згідно зі стандартом RFC 4647 («Matching of Language Tags»). Мовні діапазони мають ієрархічну природу:

- **Алгоритм пошуку (Lookup Algorithm)**: Клієнтський запит `uk-UA` (українська мова в Україні) спершу шукає точний збіг `uk-UA`. Якщо такого перекладу немає, алгоритм відкидає правий субтег регіону і виконує пошук за первинним префіксом `uk`.
- **Підстановочний знак `*`**: Збігається з будь-якою мовою, яка ще не була явно зазначена в інших елементах заголовка.

---

## 3. Реалізація узгоджувача

Нижче наведено дві повноцінні та ідіоматичні реалізації алгоритму: мовою TypeScript для середовищ Node.js/Bun/Deno та мовою C++20 для високонавантажених шлюзів і мережевих проксі.

:::tabs
```ts
// content_negotiator.ts — Промисловий рушій узгодження вмісту за RFC 9110
export interface MediaRange {
  type: string;
  subtype: string;
  params: Record<string, string>;
  q: number;
  specificity: number;
  clientIndex: number;
}

export interface LanguageRange {
  tag: string;
  primary: string;
  region?: string;
  q: number;
  clientIndex: number;
}

export interface MatchResult {
  selectedType: string;
  q: number;
  vary: string[];
}

export interface LanguageMatchResult {
  selectedLanguage: string;
  q: number;
  vary: string[];
}

export class ContentNegotiator {
  private readonly availableTypes: string[];
  private readonly availableLanguages: string[];

  constructor(availableTypes: string[], availableLanguages: string[] = []) {
    if (!availableTypes || availableTypes.length === 0) {
      throw new Error("ContentNegotiator вимагає щонайменше одного доступного типу сервера");
    }
    this.availableTypes = availableTypes.map((t) => t.toLowerCase().trim());
    this.availableLanguages = availableLanguages.map((l) => l.toLowerCase().trim());
  }

  /**
   * Розбір заголовка Accept у структурований та впорядкований список діапазонів
   */
  public parseAccept(header?: string | null): MediaRange[] {
    if (!header || !header.trim()) {
      return [{
        type: "*",
        subtype: "*",
        params: {},
        q: 1.0,
        specificity: 0,
        clientIndex: 0,
      }];
    }

    const ranges: MediaRange[] = [];
    const entries = this.splitHeaderEntries(header);

    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i].trim();
      if (!entry) continue;

      const segments = entry.split(";").map((s) => s.trim());
      const mimePart = segments[0].toLowerCase();
      const slashIndex = mimePart.indexOf("/");

      if (slashIndex === -1) continue;

      const type = mimePart.slice(0, slashIndex).trim();
      const subtype = mimePart.slice(slashIndex + 1).trim();

      if (!type || !subtype) continue;

      let q = 1.0;
      const params: Record<string, string> = {};

      for (let j = 1; j < segments.length; j++) {
        const paramPart = segments[j];
        const eqIndex = paramPart.indexOf("=");
        if (eqIndex === -1) continue;

        const key = paramPart.slice(0, eqIndex).trim().toLowerCase();
        let val = paramPart.slice(eqIndex + 1).trim();

        if (val.length >= 2 && val.startsWith('"') && val.endsWith('"')) {
          val = val.slice(1, -1);
        }

        if (key === "q") {
          const parsed = parseFloat(val);
          q = isNaN(parsed) ? 1.0 : Math.max(0, Math.min(1, parsed));
        } else {
          params[key] = val;
        }
      }

      let specificity = 0;
      if (type !== "*") {
        if (subtype !== "*") {
          specificity = Object.keys(params).length > 0 ? 3 : 2;
        } else {
          specificity = 1;
        }
      }

      ranges.push({
        type,
        subtype,
        params,
        q,
        specificity,
        clientIndex: i,
      });
    }

    ranges.sort((a, b) => {
      if (b.q !== a.q) return b.q - a.q;
      if (b.specificity !== a.specificity) return b.specificity - a.specificity;
      return a.clientIndex - b.clientIndex;
    });

    return ranges;
  }

  /**
   * Розбір заголовка Accept-Language за стандартом BCP 47
   */
  public parseAcceptLanguage(header?: string | null): LanguageRange[] {
    if (!header || !header.trim()) {
      return [{
        tag: "*",
        primary: "*",
        q: 1.0,
        clientIndex: 0,
      }];
    }

    const ranges: LanguageRange[] = [];
    const entries = this.splitHeaderEntries(header);

    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i].trim();
      if (!entry) continue;

      const segments = entry.split(";").map((s) => s.trim());
      const rawTag = segments[0].toLowerCase();
      if (!rawTag) continue;

      let q = 1.0;
      for (let j = 1; j < segments.length; j++) {
        const param = segments[j];
        const eqIdx = param.indexOf("=");
        if (eqIdx !== -1 && param.slice(0, eqIdx).trim().toLowerCase() === "q") {
          const parsed = parseFloat(param.slice(eqIdx + 1).trim());
          q = isNaN(parsed) ? 1.0 : Math.max(0, Math.min(1, parsed));
        }
      }

      const dashIdx = rawTag.indexOf("-");
      const primary = dashIdx === -1 ? rawTag : rawTag.slice(0, dashIdx);
      const region = dashIdx === -1 ? undefined : rawTag.slice(dashIdx + 1);

      ranges.push({
        tag: rawTag,
        primary,
        region,
        q,
        clientIndex: i,
      });
    }

    ranges.sort((a, b) => {
      if (b.q !== a.q) return b.q - a.q;
      return a.clientIndex - b.clientIndex;
    });

    return ranges;
  }

  /**
   * Селекція типу носія
   */
  public negotiate(acceptHeader?: string | null): MatchResult | null {
    const ranges = this.parseAccept(acceptHeader);

    for (const range of ranges) {
      if (range.q === 0) continue;

      for (const serverType of this.availableTypes) {
        const slashIdx = serverType.indexOf("/");
        const sType = serverType.slice(0, slashIdx);
        const sSubtype = serverType.slice(slashIdx + 1);

        const typeMatches = range.type === "*" || range.type === sType;
        const subtypeMatches = range.subtype === "*" || range.subtype === sSubtype;

        if (typeMatches && subtypeMatches) {
          return {
            selectedType: serverType,
            q: range.q,
            vary: ["Accept"],
          };
        }
      }
    }

    return null;
  }

  /**
   * Селекція мовної локалі за алгоритмом префіксного пошуку
   */
  public negotiateLanguage(acceptLanguageHeader?: string | null): LanguageMatchResult | null {
    if (this.availableLanguages.length === 0) return null;

    const ranges = this.parseAcceptLanguage(acceptLanguageHeader);

    for (const range of ranges) {
      if (range.q === 0) continue;

      // 1. Точний збіг повного мовного тегу (наприклад, uk-ua)
      for (const lang of this.availableLanguages) {
        if (range.tag === "*" || lang === range.tag) {
          return { selectedLanguage: lang, q: range.q, vary: ["Accept-Language"] };
        }
      }

      // 2. Префіксний збіг (наприклад, uk-ua зіставляється з uk)
      for (const lang of this.availableLanguages) {
        const sDash = lang.indexOf("-");
        const sPrimary = sDash === -1 ? lang : lang.slice(0, sDash);
        if (range.primary === sPrimary) {
          return { selectedLanguage: lang, q: range.q, vary: ["Accept-Language"] };
        }
      }
    }

    // За замовчуванням повертаємо першу мову сервера
    return {
      selectedLanguage: this.availableLanguages[0],
      q: 1.0,
      vary: ["Accept-Language"],
    };
  }

  private splitHeaderEntries(header: string): string[] {
    const results: string[] = [];
    let start = 0;
    let inQuotes = false;

    for (let i = 0; i < header.length; i++) {
      const char = header[i];
      if (char === '"' && (i === 0 || header[i - 1] !== "\\")) {
        inQuotes = !inQuotes;
      } else if (char === "," && !inQuotes) {
        results.push(header.slice(start, i));
        start = i + 1;
      }
    }

    if (start < header.length) {
      results.push(header.slice(start));
    }

    return results;
  }
}
```
```cpp
// content_negotiator.hpp — Високопродуктивний рушій C++20 без динамічних алокацій у гарячому циклі
#pragma once
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <optional>
#include <algorithm>
#include <charconv>

struct MediaRange {
    std::string type;
    std::string subtype;
    std::map<std::string, std::string> params;
    double q = 1.0;
    int specificity = 0;
    std::size_t clientIndex = 0;
};

struct LanguageRange {
    std::string tag;
    std::string primary;
    double q = 1.0;
    std::size_t clientIndex = 0;
};

struct MatchResult {
    std::string selectedType;
    double q = 1.0;
    std::vector<std::string> vary;
};

struct LanguageMatchResult {
    std::string selectedLanguage;
    double q = 1.0;
    std::vector<std::string> vary;
};

class ContentNegotiator {
public:
    explicit ContentNegotiator(std::vector<std::string> availableTypes,
                               std::vector<std::string> availableLanguages = {})
        : m_availableTypes(std::move(availableTypes)),
          m_availableLanguages(std::move(availableLanguages)) {
        for (auto& t : m_availableTypes) {
            std::transform(t.begin(), t.end(), t.begin(), [](unsigned char c) {
                return static_cast<char>(std::tolower(c));
            });
        }
        for (auto& l : m_availableLanguages) {
            std::transform(l.begin(), l.end(), l.begin(), [](unsigned char c) {
                return static_cast<char>(std::tolower(c));
            });
        }
    }

    std::vector<MediaRange> parseAccept(std::string_view header) const {
        if (header.empty()) {
            return { MediaRange{ "*", "*", {}, 1.0, 0, 0 } };
        }

        std::vector<MediaRange> ranges;
        std::size_t clientIdx = 0;
        std::size_t pos = 0;

        while (pos < header.size()) {
            std::size_t commaPos = findNextComma(header, pos);
            std::string_view entry = trim(header.substr(pos, commaPos - pos));
            pos = (commaPos == std::string_view::npos) ? header.size() : commaPos + 1;

            if (entry.empty()) continue;

            MediaRange range;
            range.clientIndex = clientIdx++;
            range.q = 1.0;

            std::size_t pStart = 0;
            bool isMimePart = true;

            while (pStart < entry.size()) {
                auto pEnd = entry.find(';', pStart);
                if (pEnd == std::string_view::npos) pEnd = entry.size();

                std::string_view part = trim(entry.substr(pStart, pEnd - pStart));
                pStart = pEnd + 1;

                if (part.empty()) continue;

                if (isMimePart) {
                    auto slash = part.find('/');
                    if (slash != std::string_view::npos) {
                        range.type = toLower(trim(part.substr(0, slash)));
                        range.subtype = toLower(trim(part.substr(slash + 1)));
                    }
                    isMimePart = false;
                } else {
                    auto eq = part.find('=');
                    if (eq != std::string_view::npos) {
                        std::string key = toLower(trim(part.substr(0, eq)));
                        std::string_view val = trim(part.substr(eq + 1));

                        if (val.size() >= 2 && val.front() == '"' && val.back() == '"') {
                            val = val.substr(1, val.size() - 2);
                        }

                        if (key == "q") {
                            double parsedQ = 1.0;
                            auto [ptr, ec] = std::from_chars(val.data(), val.data() + val.size(), parsedQ);
                            if (ec == std::errc()) {
                                range.q = std::clamp(parsedQ, 0.0, 1.0);
                            }
                        } else {
                            range.params[key] = std::string(val);
                        }
                    }
                }
            }

            if (range.type.empty() || range.subtype.empty()) continue;

            if (range.type == "*") {
                range.specificity = 0;
            } else if (range.subtype == "*") {
                range.specificity = 1;
            } else {
                range.specificity = range.params.empty() ? 2 : 3;
            }

            ranges.push_back(std::move(range));
        }

        std::sort(ranges.begin(), ranges.end(), [](const MediaRange& a, const MediaRange& b) {
            if (a.q != b.q) return a.q > b.q;
            if (a.specificity != b.specificity) return a.specificity > b.specificity;
            return a.clientIndex < b.clientIndex;
        });

        return ranges;
    }

    std::vector<LanguageRange> parseAcceptLanguage(std::string_view header) const {
        if (header.empty()) {
            return { LanguageRange{ "*", "*", 1.0, 0 } };
        }

        std::vector<LanguageRange> ranges;
        std::size_t clientIdx = 0;
        std::size_t pos = 0;

        while (pos < header.size()) {
            std::size_t commaPos = findNextComma(header, pos);
            std::string_view entry = trim(header.substr(pos, commaPos - pos));
            pos = (commaPos == std::string_view::npos) ? header.size() : commaPos + 1;

            if (entry.empty()) continue;

            LanguageRange range;
            range.clientIndex = clientIdx++;
            range.q = 1.0;

            auto semicolon = entry.find(';');
            std::string_view tagPart = trim(entry.substr(0, semicolon));
            range.tag = toLower(tagPart);

            auto dash = range.tag.find('-');
            range.primary = (dash == std::string::npos) ? range.tag : range.tag.substr(0, dash);

            if (semicolon != std::string_view::npos) {
                std::string_view paramPart = trim(entry.substr(semicolon + 1));
                auto eq = paramPart.find('=');
                if (eq != std::string_view::npos && toLower(trim(paramPart.substr(0, eq))) == "q") {
                    std::string_view val = trim(paramPart.substr(eq + 1));
                    double parsedQ = 1.0;
                    auto [ptr, ec] = std::from_chars(val.data(), val.data() + val.size(), parsedQ);
                    if (ec == std::errc()) {
                        range.q = std::clamp(parsedQ, 0.0, 1.0);
                    }
                }
            }

            ranges.push_back(std::move(range));
        }

        std::sort(ranges.begin(), ranges.end(), [](const LanguageRange& a, const LanguageRange& b) {
            if (a.q != b.q) return a.q > b.q;
            return a.clientIndex < b.clientIndex;
        });

        return ranges;
    }

    std::optional<MatchResult> negotiate(std::string_view acceptHeader) const {
        auto ranges = parseAccept(acceptHeader);

        for (const auto& range : ranges) {
            if (range.q <= 0.0) continue;

            for (const auto& serverType : m_availableTypes) {
                auto slash = serverType.find('/');
                if (slash == std::string::npos) continue;

                std::string_view sType(serverType.data(), slash);
                std::string_view sSubtype(serverType.data() + slash + 1, serverType.size() - slash - 1);

                bool typeMatch = (range.type == "*" || range.type == sType);
                bool subtypeMatch = (range.subtype == "*" || range.subtype == sSubtype);

                if (typeMatch && subtypeMatch) {
                    return MatchResult{
                        .selectedType = serverType,
                        .q = range.q,
                        .vary = { "Accept" }
                    };
                }
            }
        }

        return std::nullopt;
    }

    std::optional<LanguageMatchResult> negotiateLanguage(std::string_view acceptLanguageHeader) const {
        if (m_availableLanguages.empty()) return std::nullopt;

        auto ranges = parseAcceptLanguage(acceptLanguageHeader);

        for (const auto& range : ranges) {
            if (range.q <= 0.0) continue;

            for (const auto& lang : m_availableLanguages) {
                if (range.tag == "*" || lang == range.tag) {
                    return LanguageMatchResult{
                        .selectedLanguage = lang,
                        .q = range.q,
                        .vary = { "Accept-Language" }
                    };
                }
            }

            for (const auto& lang : m_availableLanguages) {
                auto dash = lang.find('-');
                std::string_view sPrimary = (dash == std::string::npos) ? std::string_view(lang) : std::string_view(lang.data(), dash);
                if (range.primary == sPrimary) {
                    return LanguageMatchResult{
                        .selectedLanguage = lang,
                        .q = range.q,
                        .vary = { "Accept-Language" }
                    };
                }
            }
        }

        return LanguageMatchResult{
            .selectedLanguage = m_availableLanguages.front(),
            .q = 1.0,
            .vary = { "Accept-Language" }
        };
    }

private:
    std::vector<std::string> m_availableTypes;
    std::vector<std::string> m_availableLanguages;

    static std::size_t findNextComma(std::string_view str, std::size_t start) {
        bool inQuotes = false;
        for (std::size_t i = start; i < str.size(); ++i) {
            if (str[i] == '"' && (i == 0 || str[i - 1] != '\\')) {
                inQuotes = !inQuotes;
            } else if (str[i] == ',' && !inQuotes) {
                return i;
            }
        }
        return std::string_view::npos;
    }

    static std::string_view trim(std::string_view s) {
        while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) s.remove_prefix(1);
        while (!s.empty() && (s.back() == ' ' || s.back() == '\t')) s.remove_suffix(1);
        return s;
    }

    static std::string toLower(std::string_view s) {
        std::string res(s);
        std::transform(res.begin(), res.end(), res.begin(), [](unsigned char c) {
            return static_cast<char>(std::tolower(c));
        });
        return res;
    }
};
```
:::

---

## 4. Покроковий розбір складних сценаріїв

Протестуємо поведінку реалізованого класу `ContentNegotiator` на конфігурації сервера, який підтримує такі формати та мови:

```
Серверний пул типів = [ "application/json", "text/html", "application/xml" ]
Серверний пул мов  = [ "uk", "en-us", "de" ]
```

### Сценарій 1: Реальний заголовок сучасного браузера

Клієнт надсилає стандартний складний рядок браузера Chrome/Firefox:

```http
Accept: text/html, application/xhtml+xml, application/xml;q=0.9, image/avif, image/webp, */*;q=0.8
```

1. **Фаза токенізації**: Заголовок розбивається на 6 діапазонів.
2. **Фаза ранжування**:
   - `text/html` → `q=1.0`, `specificity=2`, `index=0`
   - `application/xhtml+xml` → `q=1.0`, `specificity=2`, `index=1`
   - `image/avif` → `q=1.0`, `specificity=2`, `index=3`
   - `image/webp` → `q=1.0`, `specificity=2`, `index=4`
   - `application/xml` → `q=0.9`, `specificity=2`, `index=2`
   - `*/*` → `q=0.8`, `specificity=0`, `index=5`
3. **Зіставлення**: Першим серед доступних серверних форматів перевіряється `text/html`. Він має `q=1.0` і точний збіг.
4. **Результат**: Повертається `text/html`, `q=1.0`, `Vary: ["Accept"]`.

### Сценарій 2: Колізія однакових коефіцієнтів і перемога специфічності

Клієнт надсилає рівнозначні вагові коефіцієнти для загального шаблону та конкретного типу:

```http
Accept: application/*; q=0.8, application/json; q=0.8
```

1. Обидва правила мають однакове значення `q = 0.8`.
2. Правило `application/json` має специфічність `2` (точний підтип).
3. Правило `application/*` має специфічність `1` (підстановочний знак у підтипі).
4. Рушій віддає пріоритет `application/json` завдяки вищій специфічності, уникаючи випадкового вибору `application/xml`.

### Сценарій 3: Категорична заборона формату (`q=0`)

Запит надходить від спеціалізованого бота, який не вміє розбирати HTML-верстку:

```http
Accept: text/html; q=0, */*; q=0.5
```

1. Навіть якщо `text/html` є дефолтним і стоїть першим у налаштуваннях сервера, правило `q=0` повністю виключає його з кандидатів.
2. Шаблон `*/*; q=0.5` зіставляється з наступним доступним варіантом — `application/json`.
3. Клієнт отримує чисті структуровані дані замість HTML-сторінки.

### Сценарій 4: Мовний відкат регіонального діалекту (Language Fallback)

Користувач надіслав мовний заголовок з регіональним субтегом:

```http
Accept-Language: uk-UA, en-US; q=0.8, en; q=0.7
```

1. Узгоджувач перевіряє точний збіг `uk-ua` серед мов сервера (`["uk", "en-us", "de"]`). Збігу немає.
2. Алгоритм відкидає субтег `-UA` і шукає базовий префікс `uk`.
3. Серверний пул містить мову `uk`. Збіг знайдено!
4. Повертається мова `uk` з коефіцієнтом `q=1.0` та заголовком `Vary: ["Accept-Language"]`.

### Сценарій 5: Повна несумісність форматів (Помилка 406)

Клієнт вимагає специфічний графічний або бінарний формат:

```http
Accept: image/png, application/x-protobuf
```

1. Жоден із зазначених типів не підтримується обробником даного ендпоінта.
2. Метод `negotiate()` повертає `null` (`std::nullopt`).
3. Бекенд надсилає клієнту стандартну відповідь `406 Not Acceptable` із тілом опису доступних форматів.

---

## 5. Пастки та оптимізація продуктивності

Під час інтеграції узгоджувача у виробничі веб-системи слід звернути увагу на такі інженерні аспекти:

1. **Неекрановані коми всередині лапок**:
   Значення параметрів можуть містити коми (наприклад, `application/json; schema="user,v2"`). Наївне розбиття рядка методом `split(',')` поламає синтаксичну структуру. Реалізований метод `splitHeaderEntries` коректно відстежує стан перебування всередині подвійних лапок.
2. **Локалезалежний парсинг чисел із плаваючою комою**:
   У C++ виклики `std::stod` або `atof` залежать від поточної локалі операційної системи (де десятковим роздільником може бути кома замість крапки). Використання функції `std::from_chars` (C++17/20) гарантує незалежність від системної локалі та максимальну швидкість парсингу без виділення пам'яті в купі.
3. **Нульове виділення пам'яті (Zero-Allocation Parsing)**:
   При обробці 100 000 запитів за секунду на один потік створення десятків тимчасових об'єктів `std::string` викликає фрагментацію пам'яті та навантаження на алокатор. Представлена реалізація C++20 оперує легковажними обрізками `std::string_view` під час токенізації, що дозволяє виконувати розбір заголовка повністю на стеку.
4. **Проблема кешування заголовка Vary**:
   Якщо диспетчер успішно обрав представлення на основі заголовка `Accept`, але middleware забув додати `Vary: Accept` до відповіді, проміжний кеш провайдера збереже JSON-відповідь для першого користувача і віддасть її браузеру наступного користувача, який очікував HTML. Завжди передавайте поле `vary` з результату узгодження безпосередньо у вихідні заголовки HTTP-відповіді.
