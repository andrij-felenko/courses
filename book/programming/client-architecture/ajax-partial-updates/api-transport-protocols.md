# 📋 Протоколи та інтерфейси фонового обміну: XHR, Fetch, SSE, WebSocket і RSC

Клієнтська архітектура сучасного вебу спирається на п'ять базових мережевих контрактів для виконання фонового обміну даними без перезавантаження документа. Кожен інтерфейс має власну модель життєвого циклу, протокольний оверхед, семантику підключення, гарантії доставки та підтримку потокового читання байтів.

Вибір відповідного протоколу визначається співвідношенням частоти подій, вимог до затримки (*latency*), необхідності двосторонньої передачі та сумісності з проміжними проксі-серверами й балансувальниками навантаження.

## Зведена матриця мережевих контрактів

| Критерій | `XMLHttpRequest` | `Fetch API + Streams` | `Server-Sent Events` | `WebSocket` | `RSC Wire Format` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Рік стандартизації** | 1999 / 2006 | 2015 | 2009 | 2011 (RFC 6455) | 2020+ |
| **Базовий транспорт** | HTTP/1.1, HTTP/2 | HTTP/1.1, HTTP/2, HTTP/3 | HTTP/1.1, HTTP/2, HTTP/3 | TCP-сокети (RFC 6455) | HTTP/2, HTTP/3 |
| **Напрямок потоку** | Запит ⇄ Відповідь | Запит ⇄ Відповідь | Сервер → Клієнт (Simplex) | Дуплекс (Full Duplex) | Сервер → Клієнт (Simplex) |
| **Модель API** | Callbacks / Events | Promises / Streams | Events (`EventSource`) | EventTarget (`ws.onmessage`)| React Runtime / Stream |
| **Потокове читання** | Частково (`readyState 3`)| Повне (`ReadableStream`)| Порядкове (`data: ...`) | Пофреймове (Binary/Text)| Порядкове (Flight JSON)|
| **Авто-перепідключення**| Відсутнє | Відсутнє | Вбудоване у рантайм | Ручне (потрібен код)| Вбудоване в роутер |
| **Підтримка бінарних даних**| `ArrayBuffer`, `Blob` | `ArrayBuffer`, `Blob`, `Uint8Array` | Лише UTF-8 текст | `ArrayBuffer`, `Blob` | JSON + TypedArray slots |
| **Скасування операції**| `xhr.abort()` | `AbortController` / Signal | `eventSource.close()` | `ws.close(code, reason)` | `AbortSignal` |

---

## 1. XMLHttpRequest (XHR)

Об'єкт подійного зв'язку зі станами скінченного автомата `readyState`. Хоча в новому коді перевага надається `Fetch API`, XHR залишається єдиним стандартизованим способом відстежувати прогрес завантаження бінарних файлів на сервер у реальному часі через інтерфейс `xhr.upload.onprogress`.

### Життєвий цикл станів (`readyState`)

Скінченний автомат XHR переходить між п'ятьма фіксованими числовими фазами:

```
UNSENT (0) ──open()──> OPENED (1) ──send()──> HEADERS_RECEIVED (2)
                                                     │
                                                     ▼
DONE (4) <──(кінцевий байт)── LOADING (3, часткові байти)
```

* `0 (UNSENT)`: Об'єкт інстанційовано конструктором `new XMLHttpRequest()`, метод `open()` ще не викликано.
* `1 (OPENED)`: Метод `open()` виконано; налаштовано цільовий URL, HTTP-метод та режим асинхронності. На цьому етапі дозволено встановлювати користувацькі заголовки через `setRequestHeader()`.
* `2 (HEADERS_RECEIVED)`: Отримано перший байт відповіді, код HTTP-статусу та заголовки сервера. Стають доступними методи `getResponseHeader()` та `getAllResponseHeaders()`.
* `3 (LOADING)`: Завантаження тіла відповіді; властивість `responseText` містить накопичений частковий текст, проте спроба розпарсити його як цілісний JSON на цьому етапі викличе синтаксичну помилку через незавершеність структури документа.
* `4 (DONE)`: Мережеву транзакцію повністю завершено, з'єднання закрито або перервано внутрішньою помилкою чи явним викликом `abort()`.

### Сигнатура ключових методів та подій

```ts
interface XMLHttpRequest extends XMLHttpRequestEventTarget {
  open(method: string, url: string, async?: boolean, user?: string, password?: string): void;
  setRequestHeader(name: string, value: string): void;
  send(body?: Document | XMLHttpRequestBodyInit | null): void;
  abort(): void;

  readonly readyState: number;
  readonly status: number;
  readonly statusText: string;
  readonly responseText: string;
  readonly responseXML: Document | null;
  responseType: XMLHttpRequestResponseType; // "" | "arraybuffer" | "blob" | "document" | "json" | "text"

  readonly upload: XMLHttpRequestUpload; // Надає події progress, load, error для тіла POST-запиту

  onreadystatechange: ((this: XMLHttpRequest, ev: Event) => any) | null;
  onload: ((this: XMLHttpRequest, ev: ProgressEvent) => any) | null;
  onerror: ((this: XMLHttpRequest, ev: ProgressEvent) => any) | null;
  onprogress: ((this: XMLHttpRequest, ev: ProgressEvent) => any) | null;
  ontimeout: ((this: XMLHttpRequest, ev: ProgressEvent) => any) | null;
}
```

---

## 2. Fetch API та ReadableStream

Сучасний стандарт неблоківного мережевого обміну на основі промісів і потоків даних (WHATWG Streams API). Головна архітектурна відмінність від XHR полягає у відокремленні фази отримання заголовків від фази зчитування тіла: виклик `fetch()` переходить у стан `fulfilled`, щойно надійшли HTTP-заголовки, не чекаючи завантаження всього масиву байтів.

### Базова сигнатура виклику

```ts
function fetch(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response>;

interface RequestInit {
  method?: string;
  headers?: HeadersInit;
  body?: BodyInit | null;
  mode?: "cors" | "no-cors" | "same-origin" | "navigate";
  credentials?: "omit" | "same-origin" | "include";
  cache?: "default" | "no-store" | "reload" | "no-cache" | "force-cache" | "only-if-cached";
  redirect?: "follow" | "error" | "manual";
  signal?: AbortSignal | null;
  keepalive?: boolean;
}
```

### Читання потокового тіла відповіді (`ReadableStream`)

Потокове читання дозволяє уникнути виділення монолітного буфера пам'яті під великі відповіді. Байти обробляються чанками (*chunks*) у міру їхнього надходження через мережевий сокет:

```ts
const response = await fetch("/api/stream", { signal: abortController.signal });

if (!response.ok) {
  throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
}

const reader = response.body?.getReader();
const decoder = new TextDecoder("utf-8");

while (reader) {
  const { value, done } = await reader.read();
  if (done) break;
  // value є типізованим масивом Uint8Array
  const chunkText = decoder.decode(value, { stream: true });
  processChunkIncremental(chunkText);
}
```

---

## 3. Server-Sent Events (SSE / EventSource)

Односпрямований постійний потік текстових повідомлень від сервера до клієнта через звичайне HTTP-з'єднання. Протокол ідеально підходить для новинних стрічок, систем моніторингу метрик, сповіщень та потокового виведення відповідей мовних моделей, оскільки не вимагає оверхеду на відкриття окремих TCP-портів і бездоганно проходить крізь корпоративні фаєрволи та HTTP-проксі.

### Формат кадрування (`Content-Type: text/event-stream`)

Сервер передає блоки тексту у кодуванні UTF-8, де окремі поля починаються з ключових слів, а кожне повідомлення завершується подвійним переведенням рядка `\n\n`:

```http
event: message
id: 1042
retry: 5000
data: {"type": "PRICE_UPDATE", "symbol": "AAPL", "price": 182.45}

event: user_alert
id: 1043
data: Вашу підписку успішно оновлено.

: це рядок коментаря (використовується для запобігання тайм-аутам проксі)
```

* `event:` тип події; якщо поле відсутнє, спрацьовує стандартний обробник `onmessage`.
* `id:` ідентифікатор події. Браузер автоматично зберігає це значення й передає його у заголовку `Last-Event-ID` під час повторного підключення після обриву мережі.
* `retry:` інтервал у мілісекундах, який клієнт має зачекати перед спробою відновлення розірваного з'єднання.
* `data:` корисне навантаження; якщо рядок містить кілька префіксів `data:`, браузер автоматично склеює їх через символ `\n`.

### Клієнтський інтерфейс `EventSource`

```ts
const sse = new EventSource("/api/live-feed", { withCredentials: true });

// Обробка стандартних подій без зазначеного типу
sse.onmessage = (event: MessageEvent) => {
  const payload = JSON.parse(event.data);
  console.log("Отримано базове повідомлення:", payload);
};

// Підписка на кастомний тип події (поле event: user_alert)
sse.addEventListener("user_alert", (event: MessageEvent) => {
  displayAlertBanner(event.data);
});

// Обробка стану з'єднання та помилок
sse.onerror = (err) => {
  if (sse.readyState === EventSource.CLOSED) {
    console.error("З'єднання остаточно закрито сервером");
  } else if (sse.readyState === EventSource.CONNECTING) {
    console.warn("Тимчасовий обрив; браузер виконує автоматичний reconnect");
  }
};
```

---

## 4. WebSocket (RFC 6455)

Повнодуплексний двосторонній транспорт поверх єдиного TCP-з'єднання. Після початкового HTTP-рукостискання клієнт і сервер переходять на бінарне фреймування. WebSocket незамінний у системах реального часу з високою частотою оновлень (онлайн-ігри, спільне редагування документів, фінансові біржі), де накладні витрати заголовків HTTP на кожен запит є неприпустимими.

### Процедура рукостискання (Handshake HTTP Upgrade)

Клієнт ініціює запит на підвищення протоколу:

```http
Клієнт -> Сервер:
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

Сервер -> Клієнт:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### Клієнтський API WebSocket

```ts
const ws = new WebSocket("wss://server.example.com/socket");
ws.binaryType = "arraybuffer";

ws.onopen = () => {
  // Відправлення текстового повідомлення
  ws.send(JSON.stringify({ action: "SUBSCRIBE", channel: "telemetry" }));
};

ws.onmessage = (event: MessageEvent) => {
  if (typeof event.data === "string") {
    const json = JSON.parse(event.data);
    handleTextMessage(json);
  } else if (event.data instanceof ArrayBuffer) {
    const view = new DataView(event.data);
    handleBinaryFrame(view);
  }
};

ws.onclose = (event: CloseEvent) => {
  console.log(`Сокет закрито: код=${event.code}, причина=${event.reason}, чисте=${event.wasClean}`);
};

ws.onerror = (event: Event) => {
  console.error("Помилка транспортного рівня WebSocket", event);
};
```

---

## 5. React Server Components Wire Format (RSC Flight)

Потоковий формат серіалізації дерев віртуальних вузлів (JSON-Lines / Flight Stream), що дозволяє клієнту вбудовувати серверні компоненти без завантаження їхнього коду JavaScript у клієнтський бандл. На відміну від звичайного HTML, формат Flight передає структурований граф компонентів, включно з даними пропсів, посиланнями на клієнтські острови (*Client Component References*) та слотами відкладених промісів `Suspense`.

### Структура кадру RSC

Кожен рядок потоку є самодостатнім JSON-дескриптором із числовим або літерним префіксом:

```
1:I["./src/CartButton.client.js",["client-bundle.js"],"default"]
2:{"title":"Кошик покупок","itemsCount":3}
0:["$","div",null,{"className":"cart-box","children":[["$","h2",null,{"children":"$2:title"}],["$","$L1",null,{"count":"$2:itemsCount"}]]}]
```

* `ID:I[...]`: Оголошення клієнтського компонента (Client Component Reference), який браузер повинен імпортувати динамічно через `import()`.
* `ID:{...}`: Слот серіалізованих даних моделі або проміса, розгорнутого на сервері.
* `0:[...]`: Кореневе дерево віртуального DOM, де символ `$` позначає дескриптор `React.createElement`, а `$L1` — підстановку клієнтського компонента за його ідентифікатором у поточному потоці.

---

## 6. Кешування, умовні запити та керування сесіями

Для мінімізації навантаження на мережу та бекенд фонові запити повинні ефективно використовувати протокольні механізми валідації кешу:

1. **Валідація через ETag та If-None-Match:** під час першого отримання фрагмента сервер повертає геш-заголовок `ETag: "w/3a5f8"`. Наступний фоновий `fetch()` автоматично передає `If-None-Match: "w/3a5f8"`. Якщо стан сутності не змінився, сервер повертає статус `HTTP 304 Not Modified` з нульовим розміром тіла, заощаджуючи обчислювальні ресурси та мобільний трафік.
2. **Директива Stale-While-Revalidate:** заголовок `Cache-Control: max-age=60, stale-while-revalidate=300` дозволяє клієнту миттєво відобразити збережену в локальному кеші версію, одночасно ініціюючи фоновий запит для тихого оновлення даних на наступний сеанс.
3. **Управління обліковими даними:** за замовчуванням `fetch()` у сучасних браузерах працює в режимі `credentials: 'same-origin'`. Для передачі авторизаційних кукі на крос-доменні API необхідно явно встановлювати опцію `credentials: 'include'`, а сервер повинен відповісти заголовком `Access-Control-Allow-Credentials: true` з точним зазначенням домену у виразі `Access-Control-Allow-Origin` (використання символу зірочки `*` разом із обліковими даними суворо заборонено специфікацією W3C).
