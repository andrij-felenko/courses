# 📋 Довідник заголовків CORS: запити, відповіді та правила взаємодії

Цей довідник містить повну специфікацію HTTP-заголовків механізму Cross-Origin Resource Sharing (CORS), визначену стандартами W3C та WHATWG Fetch Standard. Тут зведено синтаксис, допустимі значення, обмеження браузерів, взаємні несумісності директив, коди стану попередніх запитів та розширення безпеки приватних мереж (Private Network Access).

---

## Заголовки клієнтського запиту

Усі заголовки запиту CORS формуються та контролюються виключно мережевим стеком браузера (User Agent). Вони належать до категорії *Forbidden Header Names* — спроба модифікувати або встановити їх вручну через клієнтський JavaScript за допомогою `fetch()` або `XMLHttpRequest.setRequestHeader()` автоматично ігнорується рушієм або завершується винятком `TypeError`.

| Заголовок | Де надсилається | Опис та допустимі значення | Приклад |
|---|---|---|---|
| `Origin` | Усі запити CORS (прості, preflight, credentialed) | Вказує схему, хост та номер порту клієнтської сторінки, яка ініціювала виклик. Формат: `<scheme> "://" <host> [ ":" <port> ]` або літерал `null`. | `Origin: https://app.example.com:8443` |
| `Access-Control-Request-Method` | Тільки у попередньому запиті `OPTIONS` (Preflight) | Повідомляє серверу, який саме HTTP-метод клієнтський додаток планує викликати у наступному фактичному запиті. | `Access-Control-Request-Method: DELETE` |
| `Access-Control-Request-Headers` | Тільки у `OPTIONS` (Preflight), якщо є нестандартні заголовки | Список розділених комами назв HTTP-заголовків, які клієнт планує додати до фактичного запиту. | `Access-Control-Request-Headers: authorization, x-api-key` |
| `Access-Control-Request-Private-Network` | У `OPTIONS` при звертанні з публічного інтернету до локальної мережі | Частина специфікації Private Network Access (PNA). Встановлюється в `true`, коли публічна сторінка викликає `localhost` або приватні IP (RFC 1918). | `Access-Control-Request-Private-Network: true` |

---

## Заголовки серверної відповіді

Сервер повертає ці заголовки, щоб інструктувати браузер щодо дозволених міжсайтових операцій. Якщо заголовок відсутній, містить синтаксичну помилку або не збігається з параметрами клієнтського запиту, браузер відхиляє операцію та приховує відповідь від скрипту.

### 1. `Access-Control-Allow-Origin` (ACAO)
Визначає, яким зовнішнім походженням дозволено читати ресурси сервера.

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Origin: null
```

- `*` (Wildcard) — дозволяє доступ будь-якому походженню у світі. **Категорично несумісний** із запитами, що передають облікові дані (`Access-Control-Allow-Credentials: true`).
- `<origin>` — фіксоване джерело (схема + FQDN + порт). Заголовок може містити **лише одне** походження; передача кількох значень через кому (`https://a.com, https://b.com`) заборонена стандартом і призводить до відхилення запиту браузером.
- `null` — дозволяє доступ запитам без явного мережевого походження (локальні файли `file://`, пісочниці `iframe sandbox`). Використання на робочих серверах є критичною вразливістю.

---

### 2. `Access-Control-Allow-Methods` (ACAM)
Визначає перелік дозволених HTTP-методів для доступу до ресурсу у відповідь на `OPTIONS`.

```http
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
Access-Control-Allow-Methods: *
```

- Значення — перелік методів через кому або `*`. Символ `*` у заголовку методів дозволяє всі методи запиту за винятком `AUTHENTICATE` або специфічних системних команд.

---

### 3. `Access-Control-Allow-Headers` (ACAH)
Визначає перелік HTTP-заголовків, які клієнт має право передати у фактичному запиті.

```http
Access-Control-Allow-Headers: Content-Type, Authorization, X-Request-ID, X-Custom-Token
Access-Control-Allow-Headers: *
```

- Імена заголовків нечутливі до регістру символів (case-insensitive).
- Заголовки з білого списку безпечних (Safelisted) вказувати необов'язково.

---

### 4. `Access-Control-Expose-Headers` (ACEH)
Оголошує перелік заголовків відповіді, які клієнтський JavaScript має право прочитати через методи `response.headers.get()` у Fetch API або `xhr.getResponseHeader()`.

```http
Access-Control-Expose-Headers: X-Total-Count, X-RateLimit-Remaining, Content-Disposition
Access-Control-Expose-Headers: *
```

- За замовчуванням клієнтський скрипт бачить лише безпечні заголовки (CORS-safelisted response headers). Усі кастомні заголовки бекенду (пагінація, ліміти викликів, токени оновлення) без явної декларації в `ACEH` повертатимуть `null` у клієнтському додатку.

---

### 5. `Access-Control-Max-Age` (ACMA)
Задає тривалість кешування результату попередньої перевірки `OPTIONS` у внутрішньому сховищі браузера (у секундах).

```http
Access-Control-Max-Age: 86400
```

- Протягом цього інтервалу браузер не відправлятиме повторних запитів `OPTIONS` для ідентичної комбінації URL, методу та заголовків, а одразу виконуватиме основний запит.
- **Браузерні обмеження (Clamping):**
  - Chromium (Chrome, Edge): максимум 7200 секунд (2 години).
  - WebKit (Safari): максимум 600 секунд (10 хвилин).
  - Gecko (Firefox): максимум 86400 секунд (24 години).
  - Від'ємне значення або `0` повністю вимикає кешування preflight-запитів.

---

### 6. `Access-Control-Allow-Credentials` (ACAC)
Повідомляє браузеру, чи дозволено відкривати відповідь скрипту, якщо запит виконувався з обліковими даними (куки, HTTP-автентифікація або клієнтські TLS-сертифікати).

```http
Access-Control-Allow-Credentials: true
```

- Єдине допустиме значення за стандартом — строковий літерал `true` (виключно в нижньому регістрі). Будь-які інші значення (`false`, `1`, `yes`) інтерпретуються браузером як заборона доступу.

---

### 7. `Access-Control-Allow-Private-Network` (ACAPN)
Використовується в механізмі захисту локальних мереж від атак з публічного вебу (PNA).

```http
Access-Control-Allow-Private-Network: true
```

- Повертається локальним сервером (наприклад, IoT-пристроєм або локальним агентом розробника) на попередній запит `OPTIONS`, що містить `Access-Control-Request-Private-Network: true`. Без цього заголовка браузер блокує зв'язок між публічними сайтами та внутрішньою підмережею компанії чи користувача.

---

## Білі списки безпечних елементів (Safelists)

Запити, що використовують виключно елементи з білих списків, класифікуються як **прості запити (Simple Requests)** і надсилаються браузером негайно без попереднього `OPTIONS`.

### Безпечні методи запиту (CORS-safelisted methods)
- `GET`
- `HEAD`
- `POST`

### Безпечні заголовки запиту (CORS-safelisted request headers)
Браузер автоматично дозволяє такі заголовки без потреби попереднього узгодження:
- `Accept`
- `Accept-Language`
- `Content-Language`
- `Content-Type` — **виключно за наявності таких MIME-типів**:
  - `application/x-www-form-urlencoded`
  - `multipart/form-data`
  - `text/plain`
- `Range` (якщо задано просте однозначне значення інтервалу байтів).

Будь-який інший заголовок (`Authorization`, `X-Api-Key`, `X-Request-Id`) або тип вмісту `application/json` негайно перетворює запит на **складний (Preflighted)** і змушує браузер виконати попередня перевірку через `OPTIONS`.

### Безпечні заголовки відповіді (CORS-safelisted response headers)
Заголовки, які JavaScript може прочитати без встановлення `Access-Control-Expose-Headers`:
- `Cache-Control`
- `Content-Language`
- `Content-Length`
- `Content-Type`
- `Expires`
- `Last-Modified`
- `Pragma`

---

## Статуси відповіді на запит Preflight (OPTIONS)

При обробці попереднього запиту `OPTIONS` сервер зобов'язаний повернути успішний статус із відповідними заголовками `Access-Control-Allow-*`.

| HTTP-код відповіді | Інтерпретація браузером | Практична рекомендація |
|---|---|---|
| `204 No Content` | **Успіх**: попередню перевірку пройдено, тіло відповіді порожнє. | **Найкраща практика**: мінімальний оверхед трафіку, ідеально для OPTIONS. |
| `200 OK` | **Успіх**: попередню перевірку пройдено (якщо присутні всі потрібні заголовки). | Допустимо, але передача зайвого тіла витрачає ресурси мережі. |
| `400 Bad Request` | **Помилка**: попередню перевірку відхилено. | Браузер скасовує надсилання фактичного запиту. |
| `403 Forbidden` | **Помилка**: доступ для цього Origin або методу суворо заборонено. | Браузер перериває операцію і генерує CORS error у консолі. |
| `404 Not Found` | **Помилка**: роут для OPTIONS не зареєстровано на бекенді. | Типова помилка розробки, коли роутер не обробляє метод OPTIONS. |
| `405 Method Not Allowed` | **Помилка**: сервер забороняє метод OPTIONS на цьому URL. | Браузер не виконує фактичний запит і завершує виклик збоєм. |

---

## Матриця комбінацій заголовків безпеки

| `Access-Control-Allow-Origin` | `Access-Control-Allow-Credentials` | Клієнтський виклик | Результат у браузері |
|---|---|---|---|
| `*` | Відсутній | `fetch(url)` (без credentials) | **Успіх**: відповідь передається в JS |
| `*` | `true` | `fetch(url, {credentials: 'include'})` | **ПОМИЛКА**: блокування через несумісність `*` та credentials |
| `https://app.com` | `true` | `fetch(url, {credentials: 'include'})` | **Успіх**: відповідь та куки доступні коду |
| `https://app.com` | Відсутній | `fetch(url, {credentials: 'include'})` | **ПОМИЛКА**: куки відправлено, але результат приховано |
| `null` | `true` | `fetch(url, {credentials: 'include'})` | **Успіх**: критична загроза витоку даних через пісочниці |

---

## Обов'язкова взаємодія з кешем: заголовок Vary: Origin

Коли бекенд формує заголовок `Access-Control-Allow-Origin` динамічно (підставляючи дозволений домен зі списку клієнтів), відповідь обов'язково повинна містити директиву:

```http
Vary: Origin
```

Цей заголовок інструктує проміжні кешувальні сервери (CDN, Cloudflare, Fastly, проксі Nginx та локальний кеш браузера), що ключ кешування ресурсу повинен враховувати не лише URL, а й точне значення заголовка `Origin` у запиті. Якщо опустити `Vary: Origin`, відповідь із заголовком `Access-Control-Allow-Origin: https://trusted-a.com` буде збережена в CDN і віддана клієнту з `https://trusted-b.com`, що спричинить неочікувану помилку `CORS policy: The 'Access-Control-Allow-Origin' header has a value that is not equal to the supplied origin`.

---

## Класифікація помилок CORS у консолі браузера

Браузери не надають детальної інформації про помилки CORS у клієнтський JavaScript (метод `fetch()` повертає неінформативний `TypeError: Failed to fetch` заради захисту від сканування внутрішньої топології мережі). Діагностика здійснюється через повідомлення DevTools:

1. **`No 'Access-Control-Allow-Origin' header is present on the requested resource`** — сервер не додав заголовок ACAO до відповіді (або впав із необробленим винятком до виклику CORS-middleware).
2. **`The 'Access-Control-Allow-Origin' header contains multiple values 'a.com, b.com', but only one is allowed`** — сервер помилково об'єднав кілька походжень через кому замість повернення єдиного поточного Origin.
3. **`The value of the 'Access-Control-Allow-Origin' header in the response must not be the wildcard '*' when the request's credentials mode is 'include'`** — конфлікт між режимом передачі кук/токенів та зірочкою у конфігурації сервера.
4. **`Method <METHOD> is not allowed by Access-Control-Allow-Methods in preflight response`** — серверний обробник OPTIONS не включив запитуваний метод (наприклад, PATCH чи DELETE) до списку дозволених методів.
5. **`Request header field <header> is not allowed by Access-Control-Allow-Headers in preflight response`** — клієнт передав нестандартний службовий заголовок (наприклад, `X-Correlation-ID`), відсутній у списку ACAH сервера.
6. **`Response to preflight request doesn't pass access control check: It does not have HTTP ok status`** — ендпоінт відповів на `OPTIONS` статусом помилки (404, 500, 401 або 405) замість 204 чи 200.
