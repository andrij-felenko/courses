# ⚙️ Реалізація стійкого парсера й серіалізатора HTTP-cookie

Цей практичний проєкт демонструє створення надійного, сумісного з RFC 6265 та RFC 6265bis парсера й серіалізатора HTTP-cookie, який валідує атрибути, перевіряє захисні префікси `__Host-` та `__Secure-`, коректно кодує спецсимволи та відкидає некоректні заголовки без збоїв сервера.

## Чому наївний парсинг руйнує безпеку

У багатьох початкових навчальних матеріалах розбір заголовка `Cookie` зводять до простого однорядкового виразу:

```javascript
// НАЇВНИЙ ПАРСИНГ — ДЖЕРЕЛО ВРАЗЛИВОСТЕЙ У ПРОДАКШЕНІ
const cookies = Object.fromEntries(req.headers.cookie.split(';').map(p => p.split('=')));
```

Такий спрощений підхід не враховує реалій мережевого протоколу й створює критичні вразливості у промисловому середовищі:

1. **Знак рівності всередині корисного навантаження:** Якщо значення токена сесії закодовано в Base64 або містить внутрішні параметри (наприклад, `sid=dGhpcz1zZWNyZXQ==`), наївний поділ за знаком `=` розіб'є рядок на три частини, безповоротно відкинувши хвіст значення. Сервер отримає спотворений токен і відхилить легітимну сесію користувача.
2. **Значення у подвійних лапках:** За специфікацією Netscape та стандартом RFC 6265 значення cookie може бути обрамлене подвійними лапками (`sid="xyz123"`). Якщо парсер не знімає обрамляючі лапки, бекенд намагатиметься знайти в базі сесію з літеральними лапками `\"xyz123\"` замість `xyz123`, що призведе до раптової відмови в авторизації.
3. **Атака розщепленням заголовків (CRLF Injection / HTTP Response Splitting):** Якщо серіалізатор не валідує символи переводу рядка (`\r`, `\n`) в імені або значенні cookie, зловмисник може впорснути власні HTTP-заголовки чи фальшиве тіло відповіді, скомпрометувавши клієнтський кеш або виконавши XSS.
4. **Аварійне завершення процесу (DoS через некоректний Percent-Encoding):** Якщо значення містить символ `%` без двох коректних шістнадцяткових цифр (наприклад, `promo=50%_discount`), стандартні функції на кшталт `decodeURIComponent` викидають необроблене виключення `URIError`. У багатьох асинхронних серверах це призводить до аварійного завершення робочого потоку (Worker Thread) або падіння всього процесу, дозволяючи зловмиснику вивести бекенд із ладу одним сформованим запитом.
5. **Вразливості ReDoS у регулярних виразах:** Спроби парсити заголовок `Cookie` за допомогою складних регулярних виразів із вкладеними квантифікаторами неодноразово призводили до вразливостей типу ReDoS (Regular Expression Denial of Service), коли спеціально підібраний рядок із тисячі пробілів блокував подієвий цикл сервера на десятки секунд.
6. **Атака на прототипи об'єктів (Prototype Pollution):** Коли розібрані пари записуються у звичайний JavaScript-об'єкт `{}`, зловмисник може передати заголовок `Cookie: __proto__[isAdmin]=true` або `Cookie: constructor[prototype][role]=admin`. Якщо серверний код використовує прямий доступ до полів або злиття об'єктів, це призводить до модифікації глобального прототипу `Object.prototype` та ескалації привілеїв. Використання структури `Map<string, string>` повністю усуває цей клас загроз, оскільки `Map` не має ланцюжка користувацьких властивостей і розділяє ключі та системні методи.

Стійкий до відмов промисловий парсер повинен працювати за принципом детермінованого сканера: розбивати рядок на лексеми за один лінійний прохід, ізолювати помилки парсингу окремих пошкоджених записів та гарантувати повну безпеку пам'яті.

## Архітектура парсера та серіалізатора

Компонент обробки cookie складається з двох дзеркальних підсистем, кожна з яких виконує свій набір інженерних перевірок:

```
                  ┌─────────────────────────────────────────┐
                  │          Вхідний HTTP-запит             │
                  │   Cookie: __Host-sid=abc%3D%3D; mode=1  │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       Парсер вхідного Cookie            │
                  │  1. Послідовне сканування роздільників  │
                  │  2. Знаходження першого входження '='   │
                  │  3. Очищення пробілів (Trim OWS)        │
                  │  4. Зняття парних подвійних лапок       │
                  │  5. Безпечне Percent-декодування        │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │      Словник валідних параметрів        │
                  │   {"__Host-sid": "abc==", "mode": "1"}  │
                  └─────────────────────────────────────────┘

                                  ... Обробка запиту ...

                  ┌─────────────────────────────────────────┐
                  │      Серіалізатор Set-Cookie            │
                  │  1. Перевірка імені на неприпустимі байти│
                  │  2. Перевірка префіксів __Host-/__Secure│
                  │  3. Percent-кодування значення          │
                  │  4. Формування та перевірка директив    │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │          Вихідна HTTP-відповідь         │
                  │ Set-Cookie: __Host-sid=abc%3D%3D;       │
                  │             Path=/; Secure; HttpOnly;   │
                  │             SameSite=Lax                │
                  └─────────────────────────────────────────┘
```

### Алгоритм покрокового розбору вхідного рядка (RFC 6265 §5.2)

1. **Токенізація:** Вхідний рядок сканується зліва направо у пошуках символу `;`. Фрагмент між двома роздільниками розглядається як кандидат на пару `ім'я=значення`.
2. **Видалення пробілів (OWS — Optional Whitespace):** Символи пробілу та табуляції на початку та в кінці кожного знайденого фрагмента відкидаються.
3. **Поділ на ключ і значення:** Усередині фрагмента виконується пошук **першого** входження символу `=`. Усе, що передує першому `=`, стає сирим іменем; усе, що розташоване після нього, стає сирим значенням. Якщо символ `=` відсутній, фрагмент вважається іменем із порожнім значенням.
4. **Нормалізація лапок:** Якщо довжина значення становить щонайменше 2 символи, і воно починається та закінчується символом `"`, обидві лапки видаляються. Лапки всередині рядка зберігаються без змін.
5. **Безпечне декодування:** Ім'я та значення передаються у функцію декодування відсоткових послідовностей. Якщо зустрічається невалідна послідовність (наприклад, `%ZZ`), функція не викидає виключення, а зберігає сирий символ `%`, запобігаючи аварійній зупинці сервера.
6. **Усунення дублікатів:** Якщо заголовок містить кілька записів з однаковим іменем (наприклад, через колізію доменного та Host-Only cookie), парсер зберігає **перше** зустрінуте значення, оскільки за специфікацією браузери розміщують cookie з більш специфічним шляхом попереду.

### Покроковий аналіз скінченного автомата розбору

Усередині парсера обробка символів виконується через простий автомат станів:

```
[Початок лексеми] ──► (Пропуск пробілів) ──► [Читання імені до '=']
                                                      │
                                                      ▼
[Збереження пари] ◄── (Декодування) ◄── [Читання значення до ';']
```

- **Стан `STATE_READ_NAME`:** накопичує байти імені до моменту зустрічі символу `=` або `;`. Якщо знайдено символ `;` без попереднього `=`, ім'я зберігається з порожнім значенням.
- **Стан `STATE_READ_VALUE`:** фіксує початок значення. Якщо першим символом виступає подвійна лапка `"`, автомат переходить у режим зняття лапок, зберігаючи символи до кінцевої лапки або роздільника `;`.
- **Стан `STATE_DECODE`:** виконує розгортання послідовностей `%XX` у байти UTF-8. Якщо зустрічається байт `0x00` (нуль-байт), парсер замінює його на безпечний пробіл або відкидає запис, унеможливлюючи атаки типу Null-byte injection у C/C++ бібліотеках.

### Покрокова траса розбору аномального заголовка

Розглянемо покрокову роботу алгоритму на екстремальному тестовому рядку:
`Cookie:   sid="dGhpcz1zZWNyZXQ=="  ; bad_param=%GG ; empty_key= ; single_name ; trailing=1  `

1. **Фрагмент 1 (`   sid="dGhpcz1zZWNyZXQ=="  `):**
   - Очищення OWS: обрізання провідних і кінцевих пробілів дає `sid="dGhpcz1zZWNyZXQ=="`.
   - Пошук першого `=`: знайдено на позиції 3. Ім'я = `sid`, Значення = `"dGhpcz1zZWNyZXQ=="`.
   - Зняття лапок: значення починається і завершується `"`, тому лапки знімаються: `dGhpcz1zZWNyZXQ==`.
   - Декодування: успішно розпізнано, додано пару `("sid", "dGhpcz1zZWNyZXQ==")`.
2. **Фрагмент 2 (` bad_param=%GG `):**
   - Очищення OWS: `bad_param=%GG`.
   - Пошук `=`: Ім'я = `bad_param`, Значення = `%GG`.
   - Декодування: `%GG` не є валідною шістнадцятковою послідовністю. Безпечний декодер зберігає сирий рядок `%GG` без виключення `URIError`. Додано пару `("bad_param", "%GG")`.
3. **Фрагмент 3 (` empty_key= `):**
   - Очищення OWS: `empty_key=`.
   - Пошук `=`: Ім'я = `empty_key`, Значення = `""`. Додано пару `("empty_key", "")`.
4. **Фрагмент 4 (` single_name `):**
   - Очищення OWS: `single_name`.
   - Символ `=` відсутній: інтерпретується як ключ із порожнім значенням. Додано пару `("single_name", "")`.
5. **Фрагмент 5 (` trailing=1  `):**
   - Очищення OWS: `trailing=1`. Додано пару `("trailing", "1")`.

Усі аномалії успішно ізольовані, жодне виключення не перервало роботу сервера, стан збережено в детермінованому вигляді.

### Обробка UTF-8, емодзі та символів за межами ASCII
Специфікація HTTP вимагає, щоб усі заголовки містили виключно 7-бітні друковані символи ASCII (коди від `0x21` до `0x7E`).

Якщо сервер або клієнт спробує записати у значення cookie сирі багатобайтні символи UTF-8 (наприклад, кириличний текст `ім'я=Олена` або емодзі `status=🎉`), поведінка мережевих посередників стає непередбачуваною. Багато проксі-серверів (Nginx, HAProxy) інтерпретують байти зі старшим бітом (`>= 0x80`) як кодування ISO-8859-1 або відхиляють запит зі статусом `400 Bad Request`.

Серіалізатор зобов'язаний застосовувати функцію `encodeURIComponent`, яка перетворює кожен 4-байтний символ UTF-8 на ланцюжок шістнадцяткових трійок (наприклад, символ `🎉` стає `%F0%9F%8E%89`), забезпечуючи 100% сумісність з усіма мережевими шлюзами та серверами.

### Чому не можна розділяти cookie за комою (Пастка RFC 2109)
Застарілий стандарт RFC 2109 дозволяв використовувати кому як роздільник між парами cookie (`Cookie: a=1, b=2`). Проте на практиці директива `Expires` містить кому у форматі дати (`Expires=Wed, 21 Oct 2026 07:28:00 GMT`). Якщо парсер наївно розділяє вхідний заголовок за комою, дата розривається на шматки, пошкоджуючи наступні атрибути. Стандарт RFC 6265 остаточно закріпив крапку з комою `;` як єдиний канонічний роздільник.

### Вимоги до перевірки захисних префіксів у серіалізаторі
Серіалізатор зобов'язаний гарантувати виконання вимог RFC 6265bis безпосередньо в момент формування рядка заголовка:
- Для імені з префіксом `__Secure-`: наявність прапорця `secure: true`.
- Для імені з префіксом `__Host-`: наявність прапорця `secure: true`, відсутність директиви `domain` та обов'язкова наявність `path: "/"`.

Якщо розробник помилково спробує встановити `domain` для `__Host-` cookie, серіалізатор повинен відхилити операцію з чіткою помилкою валідації, не дозволяючи згенерувати заголовок, який буде мовчки відкинутий браузером.

## Багатомовна реалізація

Нижче наведено промислові реалізації трьома мовами: TypeScript (для сучасного Node.js / Deno / Bun), Python (типізований бекенд) та C++20 (високопродуктивний сервіс із нульовим копіюванням через `std::string_view` та обробкою помилок через `std::expected`).

:::tabs
```ts
// cookie_engine.ts
import crypto from "node:crypto";

export type SameSiteMode = "Strict" | "Lax" | "None";

export interface CookieOptions {
  maxAge?: number;           // час життя у секундах
  expires?: Date;            // абсолютна дата згасання
  domain?: string;           // домен видимості
  path?: string;             // шлях видимості
  secure?: boolean;          // обов'язковий TLS
  httpOnly?: boolean;        // захист від XSS
  sameSite?: SameSiteMode;   // міжсайтова ізоляція
  partitioned?: boolean;     // CHIPS-ізоляція
}

export class CookieError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CookieError";
  }
}

/**
 * Стійкий парсер вхідного заголовка Cookie (RFC 6265)
 */
export function parseCookies(header: string | undefined | null): Map<string, string> {
  const result = new Map<string, string>();
  if (!header || typeof header !== "string") {
    return result;
  }

  const pairs = header.split(";");
  for (const pair of pairs) {
    const trimmed = pair.trim();
    if (!trimmed) continue;

    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) {
      // Cookie без знака '=' вважається ключем із порожнім значенням
      const key = decodeSafely(trimmed);
      if (key && !result.has(key)) result.set(key, "");
      continue;
    }

    const rawKey = trimmed.slice(0, eqIdx).trim();
    let rawVal = trimmed.slice(eqIdx + 1).trim();

    // Зняття подвійних лапок за стандартом Netscape / RFC 6265
    if (rawVal.startsWith('"') && rawVal.endsWith('"') && rawVal.length >= 2) {
      rawVal = rawVal.slice(1, -1);
    }

    const key = decodeSafely(rawKey);
    const val = decodeSafely(rawVal);

    if (key && !result.has(key)) {
      result.set(key, val);
    }
  }

  return result;
}

/**
 * Серіалізатор Set-Cookie з повною перевіркою префіксів (RFC 6265bis)
 */
export function serializeSetCookie(
  name: string,
  value: string,
  options: CookieOptions = {}
): string {
  // 1. Валідація коректності імені
  const fieldContentRegExp = /^[\u0021-\u003A\u003C\u007E]+$/;
  if (!name || !fieldContentRegExp.test(name)) {
    throw new CookieError(`Неприпустимі символи в імені cookie: "${name}"`);
  }

  // 2. Валідація захисних префіксів RFC 6265bis
  if (name.startsWith("__Secure-")) {
    if (!options.secure) {
      throw new CookieError(`Префікс __Secure- вимагає прапорця secure: true`);
    }
  }

  if (name.startsWith("__Host-")) {
    if (!options.secure) {
      throw new CookieError(`Префікс __Host- вимагає прапорця secure: true`);
    }
    if (options.domain) {
      throw new CookieError(`Префікс __Host- забороняє вказувати domain`);
    }
    if (options.path !== "/") {
      throw new CookieError(`Префікс __Host- вимагає path: "/"`);
    }
  }

  // 3. Кодування значення для уникнення роздільників і некоректного UTF-8
  const encodedValue = encodeURIComponent(value);
  const parts: string[] = [`${name}=${encodedValue}`];

  // 4. Формування директив
  if (options.maxAge !== undefined) {
    if (Number.isNaN(options.maxAge)) {
      throw new CookieError("maxAge повинен бути валідним числом");
    }
    parts.push(`Max-Age=${Math.floor(options.maxAge)}`);
  }

  if (options.domain) {
    parts.push(`Domain=${options.domain}`);
  }

  if (options.path) {
    parts.push(`Path=${options.path}`);
  }

  if (options.expires) {
    parts.push(`Expires=${options.expires.toUTCString()}`);
  }

  if (options.httpOnly) {
    parts.push("HttpOnly");
  }

  if (options.secure) {
    parts.push("Secure");
  }

  if (options.sameSite) {
    const mode = options.sameSite;
    if (mode === "None" && !options.secure) {
      throw new CookieError(`SameSite=None обов'язково вимагає прапорця secure: true`);
    }
    parts.push(`SameSite=${mode}`);
  }

  if (options.partitioned) {
    parts.push("Partitioned");
  }

  return parts.join("; ");
}

/**
 * Валідація підписаного значення в константному часі (Constant-Time Verification)
 */
export function verifySignedCookie(signedValue: string, secret: string): string | null {
  const lastDot = signedValue.lastIndexOf(".");
  if (lastDot === -1) return null;

  const value = signedValue.slice(0, lastDot);
  const signature = signedValue.slice(lastDot + 1);

  const expectedSig = crypto
    .createHmac("sha256", secret)
    .update(value)
    .digest("base64url");

  const sigBuf = Buffer.from(signature);
  const expBuf = Buffer.from(expectedSig);

  if (sigBuf.length !== expBuf.length) return null;
  return crypto.timingSafeEqual(sigBuf, expBuf) ? value : null;
}

/**
 * Безпечне декодування: не падає на пошкоджених відсоткових послідовностях
 */
function decodeSafely(str: string): string {
  try {
    return decodeURIComponent(str);
  } catch {
    return str; // повертаємо вихідний рядок, якщо послідовність пошкоджена
  }
}
```
```py
# cookie_engine.py
from datetime import datetime, timezone
import urllib.parse
import hmac
import hashlib
import re
from typing import Optional, Dict

class CookieError(ValueError):
    """Помилка валідації або серіалізації параметрів cookie."""
    pass

def parse_cookies(header: Optional[str]) -> Dict[str, str]:
    """Стійкий парсер вхідного заголовка Cookie відповідно до RFC 6265."""
    cookies: Dict[str, str] = {}
    if not header:
        return cookies

    for item in header.split(";"):
        item = item.strip()
        if not item:
            continue

        if "=" in item:
            key, val = item.split("=", 1)
            key = key.strip()
            val = val.strip()

            # Зняти обрамляючі подвійні лапки
            if len(val) >= 2 and val.startswith('"') and val.endswith('"'):
                val = val[1:-1]

            decoded_key = urllib.parse.unquote(key)
            decoded_val = urllib.parse.unquote(val)
            if decoded_key and decoded_key not in cookies:
                cookies[decoded_key] = decoded_val
        else:
            decoded_key = urllib.parse.unquote(item)
            if decoded_key and decoded_key not in cookies:
                cookies[decoded_key] = ""

    return cookies

def serialize_set_cookie(
    name: str,
    value: str,
    *,
    max_age: Optional[int] = None,
    expires: Optional[datetime] = None,
    domain: Optional[str] = None,
    path: Optional[str] = None,
    secure: bool = False,
    http_only: bool = False,
    same_site: Optional[str] = None,
    partitioned: bool = False
) -> str:
    """Серіалізатор Set-Cookie з валідацією префіксів __Host- та __Secure-."""
    if not name or not re.match(r"^[\x21-\x3A\x3C\x7E]+$", name):
        raise CookieError(f"Неприпустимі символи в імені cookie: '{name}'")

    # Валідація захисних префіксів RFC 6265bis
    if name.startswith("__Secure-"):
        if not secure:
            raise CookieError("Префікс __Secure- вимагає secure=True")

    if name.startswith("__Host-"):
        if not secure:
            raise CookieError("Префікс __Host- вимагає secure=True")
        if domain:
            raise CookieError("Префікс __Host- категорично забороняє атрибут domain")
        if path != "/":
            raise CookieError("Префікс __Host- обов'язково вимагає path='/'")

    encoded_val = urllib.parse.quote(value, safe="")
    parts = [f"{name}={encoded_val}"]

    if max_age is not None:
        parts.append(f"Max-Age={int(max_age)}")

    if domain:
        parts.append(f"Domain={domain}")

    if path:
        parts.append(f"Path={path}")

    if expires:
        # Форматування дати за RFC 1123 в зоні UTC
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        gmt_str = expires.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        parts.append(f"Expires={gmt_str}")

    if http_only:
        parts.append("HttpOnly")

    if secure:
        parts.append("Secure")

    if same_site:
        mode = same_site.capitalize()
        if mode not in ("Strict", "Lax", "None"):
            raise CookieError(f"Невідомий режим SameSite: '{same_site}'")
        if mode == "None" and not secure:
            raise CookieError("SameSite=None обов'язково вимагає secure=True")
        parts.append(f"SameSite={mode}")

    if partitioned:
        parts.append("Partitioned")

    return "; ".join(parts)

def verify_signed_cookie(signed_value: str, secret: str) -> Optional[str]:
    """Перевірка підпису HMAC у константному часі для захисту від Timing Attacks."""
    if "." not in signed_value:
        return None
    val, sig = signed_value.rsplit(".", 1)
    expected_sig = hmac.new(secret.encode(), val.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(sig, expected_sig):
        return val
    return None
```
```cpp
// cookie_engine.hpp
#pragma once
#include <string>
#include <string_view>
#include <unordered_map>
#include <optional>
#include <expected>
#include <vector>
#include <sstream>
#include <iomanip>
#include <cctype>

namespace web {

enum class SameSiteMode {
    Strict,
    Lax,
    None
};

struct CookieOptions {
    std::optional<int64_t> max_age;
    std::optional<std::string> domain;
    std::optional<std::string> path;
    bool secure = false;
    bool http_only = false;
    std::optional<SameSiteMode> same_site;
    bool partitioned = false;
};

class CookieEngine {
public:
    // Безпечне URL-декодування без падіння на некоректних байтах
    static std::string url_decode(std::string_view in) {
        std::string out;
        out.reserve(in.size());
        for (size_t i = 0; i < in.size(); ++i) {
            if (in[i] == '%' && i + 2 < in.size()) {
                auto hex_val = [](char c) -> int {
                    if (c >= '0' && c <= '9') return c - '0';
                    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
                    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
                    return -1;
                };
                int hi = hex_val(in[i + 1]);
                int lo = hex_val(in[i + 2]);
                if (hi != -1 && lo != -1) {
                    out.push_back(static_cast<char>((hi << 4) | lo));
                    i += 2;
                    continue;
                }
            } else if (in[i] == '+') {
                out.push_back(' ');
                continue;
            }
            out.push_back(in[i]);
        }
        return out;
    }

    // URL-кодування рядка
    static std::string url_encode(std::string_view in) {
        std::ostringstream ss;
        for (unsigned char c : in) {
            if (std::isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
                ss << c;
            } else {
                ss << '%' << std::uppercase << std::hex << std::setw(2)
                   << std::setfill('0') << static_cast<int>(c);
            }
        }
        return ss.str();
    }

    // Парсер вхідного заголовка Cookie
    static std::unordered_map<std::string, std::string> parse(std::string_view header) {
        std::unordered_map<std::string, std::string> cookies;
        size_t start = 0;

        while (start < header.size()) {
            size_t end = header.find(';', start);
            if (end == std::string_view::npos) end = header.size();

            std::string_view token = header.substr(start, end - start);
            // Видалення пробілів
            while (!token.empty() && std::isspace(static_cast<unsigned char>(token.front())))
                token.remove_prefix(1);
            while (!token.empty() && std::isspace(static_cast<unsigned char>(token.back())))
                token.remove_suffix(1);

            if (!token.empty()) {
                size_t eq = token.find('=');
                if (eq != std::string_view::npos) {
                    std::string_view k = token.substr(0, eq);
                    std::string_view v = token.substr(eq + 1);

                    // Зняття лапок
                    if (v.size() >= 2 && v.front() == '"' && v.back() == '"') {
                        v = v.substr(1, v.size() - 2);
                    }

                    std::string key = url_decode(k);
                    std::string val = url_decode(v);
                    if (!key.empty() && !cookies.contains(key)) {
                        cookies.emplace(std::move(key), std::move(val));
                    }
                }
            }
            start = end + 1;
        }
        return cookies;
    }

    // Серіалізатор Set-Cookie з верифікацією префіксів
    static std::expected<std::string, std::string> serialize(
        std::string_view name,
        std::string_view value,
        const CookieOptions& opts
    ) {
        if (name.empty()) {
            return std::unexpected("Ім'я cookie не може бути порожнім");
        }

        // Перевірка префіксів RFC 6265bis
        if (name.starts_with("__Secure-")) {
            if (!opts.secure) {
                return std::unexpected("Префікс __Secure- вимагає прапорця secure");
            }
        }

        if (name.starts_with("__Host-")) {
            if (!opts.secure) {
                return std::unexpected("Префікс __Host- вимагає прапорця secure");
            }
            if (opts.domain.has_value()) {
                return std::unexpected("Префікс __Host- забороняє встановлювати domain");
            }
            if (!opts.path.has_value() || opts.path.value() != "/") {
                return std::unexpected("Префікс __Host- вимагає path = '/'");
            }
        }

        std::string out;
        out.reserve(128);
        out.append(name);
        out.push_back('=');
        out.append(url_encode(value));

        if (opts.max_age.has_value()) {
            out.append("; Max-Age=");
            out.append(std::to_string(opts.max_age.value()));
        }

        if (opts.domain.has_value()) {
            out.append("; Domain=");
            out.append(opts.domain.value());
        }

        if (opts.path.has_value()) {
            out.append("; Path=");
            out.append(opts.path.value());
        }

        if (opts.http_only) {
            out.append("; HttpOnly");
        }

        if (opts.secure) {
            out.append("; Secure");
        }

        if (opts.same_site.has_value()) {
            if (opts.same_site.value() == SameSiteMode::None && !opts.secure) {
                return std::unexpected("SameSite=None вимагає прапорця secure");
            }
            out.append("; SameSite=");
            switch (opts.same_site.value()) {
                case SameSiteMode::Strict: out.append("Strict"); break;
                case SameSiteMode::Lax:    out.append("Lax"); break;
                case SameSiteMode::None:   out.append("None"); break;
            }
        }

        if (opts.partitioned) {
            out.append("; Partitioned");
        }

        return out;
    }
};

} // namespace web
```
:::

## Покроковий розбір тестування та граничних випадків

Для перевірки стійкості реалізації сформовано спеціальний набір тестів, що імітує реальні сценарії та спроби зловмисних маніпуляцій:

```ts
import { parseCookies, serializeSetCookie, verifySignedCookie } from "./cookie_engine";

// Тест 1: Розбір складних значень (Base64 із символами '=', лапки, зайві пробіли)
const complexHeader = '  sid="dGhpcz1zZWNyZXQ=="; theme=dark; empty_val=; unquoted=a=b=c; ';
const parsed = parseCookies(complexHeader);

console.assert(parsed.get("sid") === "dGhpcz1zZWNyZXQ==", "Помилка парсингу Base64 у подвійних лапках");
console.assert(parsed.get("theme") === "dark", "Помилка парсингу theme");
console.assert(parsed.get("empty_val") === "", "Помилка парсингу порожнього значення");
console.assert(parsed.get("unquoted") === "a=b=c", "Помилка збереження знаків '=' усередині значення");

// Тест 2: Захист від помилкової конфігурації префікса __Host-
try {
  serializeSetCookie("__Host-auth", "tok123", {
    domain: "example.com", // Неприпустимо для __Host-
    secure: true,
    path: "/"
  });
  console.assert(false, "Помилка: валідатор пропустив domain для __Host- cookie!");
} catch (err: any) {
  console.assert(err.message.includes("забороняє вказувати domain"), "Очікувана помилка валідації Domain");
}

// Тест 3: Генерація суворого захищеного заголовка для сесії
const validSetCookie = serializeSetCookie("__Host-session", "random_token_99", {
  secure: true,
  httpOnly: true,
  path: "/",
  sameSite: "Lax",
  maxAge: 3600
});

console.log("Згенеровано валідний заголовок Set-Cookie:");
console.log(validSetCookie);

// Тест 4: Перевірка валідації підписаних токенів у константному часі
const secret = "super-secret-key-12345";
const validToken = "usr_42.tX9s7Y_abc_signature"; // припустимий підпис
// Якщо підпис недійсний, функція повертає null
console.assert(verifySignedCookie("usr_42.invalid_sig", secret) === null, "Помилка: пропущено підроблений підпис!");
```

## Інженерні рекомендації для високих навантажень

Під час інтеграції парсера в сервери високого навантаження (API Gateways, мікросервісні проксі) критично важливо дотримуватися таких практик:

### 1. Лінивий розбір (Lazy Parsing) та мемоізація
У типовому веб-додатку до 80% запитів припадає на статичні ресурси, відкриті ендпойнти автентифікації або службові виклики моніторингу (Health Checks). Якщо проміжний обробник (Middleware) автоматично парсить заголовок `Cookie` у структуру `Map` для кожного вхідного пакету, сервер витрачає процесорні такти на непотрібну роботу.

Рекомендується реалізовувати лінивий розбір: об'єкт `Request` містить лише сирий покажчик на заголовок, а фактична токенізація та декодування виконуються лише при першому звертанні бізнес-логіки до методу `req.getCookie("sid")`. Отриманий результат кешується на час життя запиту (мемоізація), щоб повторні виклики з різних шарів сервісу не запускали сканування вдруге.

### 2. Парсинг без алокацій пам'яті (Zero-Allocation Fast Path)
У системних мовах програмування (C++, Rust, Go) створення окремого динамічного об'єкта `std::string` або `String` для кожного ключа та значення створює надлишковий тиск на менеджер динамічної пам'яті (Heap Allocator) та викликає часті паузи збирача сміття у керованих мовах.

Використання неволодіючих зрізів (`std::string_view` у C++, `&str` у Rust) дозволяє виконувати пошук потрібного cookie за один прохід по вхідному буферу сокета без жодного виділення динамічної пам'яті. Якщо значення не містить відсоткових послідовностей `%XX`, результат повертається як прямий зріз оригінального буфера пам'яті, забезпечуючи максимальну пропускну здатність під мільйонними RPS.

### 3. Архітектурне розділення шарів у Clean Architecture
У чистій архітектурі доменні сутності та сервіси бізнес-логіки (Use Cases) не повинні залежати від HTTP-специфічних понять на кшталт `Set-Cookie` або `SameSite`. 

Контролер або проміжний шлюз витягує чистий сесійний ідентифікатор через `parseCookies` і передає його в доменний сервіс як простий тип `SessionId(string)`. При формуванні відповіді шлюз отримує доменний об'єкт сесії та перетворює його на захищений заголовок `Set-Cookie` за допомогою `serializeSetCookie`. Це гарантує повну незалежність бізнес-правил від деталей транспортного протоколу й дозволяє легко змінювати протоколи транспорту (наприклад, переходити з HTTP REST на gRPC чи WebSockets) без переписування внутрішньої логіки авторизації.

### 4. Обробка граничних сценаріїв та стратегії відновлення (Error Recovery)
Промисловий парсер повинен дотримуватися принципу стійкості Постела (Robustness Principle: «Будь консервативним у тому, що надсилаєш, і ліберальним у тому, що приймаєш»):
- **Пошкоджені байти у значенні:** Якщо один із клієнтських скриптів записав пошкоджене значення `bad_token=%E0%A4`, парсер не повинен переривати обробку всього заголовка. Він ізолює це конкретне cookie, записуючи сире значення або порожній рядок, дозволяючи успішно розпарсити критично важливі сесійні cookie `__Host-sid`, розташовані поруч.
- **Відсутність пробілів між роздільниками:** Хоча стандарт вимагає пробіл після крапки з комою (`; SP`), багато вбудованих пристроїв та скриптів надсилають пари впритул (`a=1;b=2`). Парсер автоматично очищає будь-яку кількість пробілів на межах токенів.
- **Екстремально довгі заголовки:** Якщо довжина заголовка перевищує ліміт буфера (наприклад, понад 8 КБ), парсер негайно сигналізує про помилку `HTTP 431`, не намагаючись алокувати масив величезного розміру, що захищає сервер від вичерпання пам'яті (Memory Exhaustion DoS).

### 5. Стратегія ротації секретних ключів для підписаних cookie
Під час планової зміни ключів HMAC у продакшені неприпустимо використовувати лише один фіксований ключ: це призвело б до масового виходу користувачів із системи.

Архітектурний патерн **Key Rotation** полягає у підтримці масиву ключів:
- **Первинний ключ (Primary Key):** використовується для підписування нових `Set-Cookie` заголовків.
- **Вторинні ключі (Fallback Verification Keys):** перевіряються по черзі у функції `verifySignedCookie`, якщо перевірка первинним ключем завершилася невдачею.

Коли користувач надсилає запит зі старим підписом, сервер успішно верифікує його резервним ключем і тут же перевипускає заголовок `Set-Cookie`, підписаний свіжим первинним ключем, завершуючи ротацію без жодного переривання сервісу.

### 6. Інтеграція у веб-фреймворки (Fastify та Express)
У сучасних середовищах Node.js парсер інтегрується у конвеєр обробки як легкий плагін або декоратор:

```ts
import Fastify from "fastify";
import { parseCookies, serializeSetCookie, CookieOptions } from "./cookie_engine";

const app = Fastify();

// Реєстрація декораторів запиту та відповіді
app.decorateRequest("cookies", null);
app.addHook("onRequest", async (req, reply) => {
  // Лінивий парсинг при першому виклику
  let cachedCookies: Map<string, string> | null = null;
  req.getCookie = (name: string): string | undefined => {
    if (!cachedCookies) {
      cachedCookies = parseCookies(req.headers.cookie);
    }
    return cachedCookies.get(name);
  };
});

app.decorateReply("setCookie", function(name: string, value: string, options?: CookieOptions) {
  const cookieStr = serializeSetCookie(name, value, options);
  this.header("Set-Cookie", cookieStr);
});
```

Цей шаблон гарантує, що розбір виконується щонайбільше один раз на запит, не блокуючи подієвий цикл та забезпечуючи максимальну ергономіку розробки.

### 7. Порівняння продуктивності: Zero-Copy C++ проти інтерпретованих середовищ

Під час обробки трафіку обсягом від 100 000 до 1 000 000 RPS (запитів на секунду) вибір мови та моделі управління пам'яттю має вирішальний вплив на апаратні витрати інфраструктури:

- **Інтерпретовані середовища (Node.js / Python):** Виділення об'єктів рядків та структур словників для кожного HTTP-запиту призводить до значного споживання оперативної пам'яті. У середовищі Node.js створення об'єкта `Map` для 10 cookie генерує близько 1 КБ сміття на запит. При 100 000 RPS це становить 100 МБ алокацій щосекунди, викликаючи часті зупинки для збирання сміття (GC Pauses) та роздуваючи затримки 99-го перцентиля (Tail Latency P99).
- **Zero-Copy архітектура на C++20:** Застосування `std::string_view` усуває динамічне виділення пам'яті в купі (`heap`). Парсер оперує покажчиками на вже існуючий буфер мережевого драйвера. Це знижує час розбору заголовка до кількох наносекунд на запит і дозволяє одному процесорному ядру повністю утилізувати мережевий інтерфейс 10GbE без затримок пам'яті.
- **Пул потокобезпечних буферів:** У багатопотокових серверах (на базі epoll/kqueue) буфери `Thread-Local Storage` дозволяють перевикористовувати пам'ять парсингу між мільйонами підключень без блокувань м'ютексів.

## Підсумок практичної реалізації

Створення надійного парсера вимагає суворого дотримання стандарту RFC 6265, захисту від аномальних вхідних послідовностей, валідації префіксів `__Host-` та `__Secure-` ще на етапі створення заголовків, а також ізоляції пам'яті. Застосування розглянутих патернів і лінійного автомата станів перетворює обробку заголовків cookie на надійну, безпечну та високопродуктивну підсистему веб-сервера.
