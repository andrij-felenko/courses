# 📋 Специфікація середовища Edge Runtime: стандартизований контракт FetchEvent та Web API

Цей довідник містить повну структурну та описову специфікацію програмного інтерфейсу (API) стандартизованого середовища виконання крайових функцій (Edge Runtime) згідно зі стандартами робочої групи WinterCG та консорціуму W3C. Довідник охоплює всі системні контракти, типи даних, сигнатури методів, модель життєвого циклу обробки подій `FetchEvent`, інтерфейси потокової обробки даних `TransformStream`, асинхронні криптографічні примітиви `SubtleCrypto`, прямі зв'язки між сервісами (Service Bindings / RPC), а також взаємодію з крайовим HTTP-кешем, розподіленим сховищем ключ-значення (Edge KV), потоковим парсером `HTMLRewriter` та транзакційними стійкими об'єктами (Durable Objects).

Документ призначений для інженерів, які розробляють кросплатформні крайові мікросервіси, інтелектуальні API-шлюзи, проксі-сервери перехоплення трафіку, модулі динамічної автентифікації та системи потокової модифікації контенту. Дотримання цієї специфікації гарантує сумісність і переносимість вихідного коду між платформами Cloudflare Workers, Fastly Compute, Deno Deploy, Vercel Edge Runtime, Netlify Edge та локальними середовищами тестування на базі Node.js або workerd.

```
Ієрархія інтерфейсів Edge Runtime:
FetchEvent ──► Request ──► ExecutionContext (waitUntil / passThroughOnException)
    │
    ├──► Response ──► ReadableStream / TransformStream / HTMLRewriter (Потокове тіло)
    ├──► Cache API (caches.default: match / put / delete)
    ├──► Crypto API (crypto.subtle: importKey / sign / verify / digest)
    ├──► Edge KV Binding (get / put / delete / list)
    ├──► Service Bindings / Worker RPC (Прямий міжсервісний виклик у пам'яті)
    └──► Durable Objects / Transactional Storage / WebSockets
```

---

## 1. Архітектура обробника запитів, життєвий цикл FetchEvent та ExecutionContext

Крайове середовище функціонує в парадигмі реактивного циклу подій (англ. *Event Loop*), де один системний потік може одночасно обслуговувати тисячі паралельних з'єднань, ізольованих одне від одного на рівні контекстів пам'яті. Точкою входу в програму виступає експортований модуль із методом `fetch`, що приймає вхідний HTTP-запит, змінні оточення та контекст виконання.

```ts
interface ExportedHandler<Env = unknown> {
  fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> | Response;
}
```

### Механіка життєвого циклу запиту

Обробка запиту проходить три послідовні фази:
1. **Фаза ініціалізації та диспетчеризації**: крайовий проксі отримує вхідні байти TCP/TLS від клієнта, розбирає HTTP-заголовки, створює екземпляр класу `Request` та передає його в ізолят V8 як подію виклику.
2. **Фаза формування відповіді**: функція виконує синхронну та асинхронну бізнес-логіку і повертає об'єкт `Response` (або проміс, що розкривається у відповідь). Щойно об'єкт `Response` повернено хостовому процесу, перші байти HTTP-заголовків та статус негайно відправляються клієнту через мережевий сокет. Це забезпечує мінімальний час до першого байта (TTFB).
3. **Фаза фонової післяобробки (Drain Phase)**: клієнт уже отримав відповідь, але ізолят продовжує жити для виконання завдань, зареєстрованих через метод `ctx.waitUntil()`.

### Специфікація інтерфейсу `ExecutionContext`

Інтерфейс контексту виконання слугує мостом між пісочницею функції та хостовим процесом CDN, дозволяючи керувати життєвим циклом без блокування клієнтського потоку даних.

```ts
interface ExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
  passThroughOnException(): void;
}
```

#### Метод `waitUntil(promise)`
Метод приймає проміс довільного типу і повідомляє планувальнику середовища, що виконання не можна переривати до повного завершення цього промісу, навіть якщо клієнтське з'єднання вже повністю закрите.
- **Призначення**: асинхронна відправка аналітики та структурованих логів у черги, прогрів і запис важких об'єктів у розподілений кеш, оновлення лічильників відвідуваності в базі даних.
- **Поведінка у разі відхилення промісу (Promise Rejection)**: якщо проміс, переданий у `waitUntil`, викидає неперехоплену помилку, вона фіксується у внутрішньому системному журналі аудиту платформи, але жодним чином не впливає на відповідь, яку вже отримав користувач.
- **Ліміти часу**: середовище гарантує виконання фонових промісів протягом фіксованого вікна (зазвичай до 30 секунд після повернення відповіді). Якщо фонове завдання не завершується в межах цього ліміту, воно примусово анулюється планувальником.

#### Метод `passThroughOnException()`
Метод змінює стандартну поведінку аварійного завершення функції.
- **Стандартна поведінка**: у разі виникнення неперехопленого винятку в тілі обробника функція падає, а клієнт отримує від CDN службову сторінку з кодом стану HTTP `500 Internal Server Error` або `1101 Worker Threw Exception`.
- **Поведінка з `passThroughOnException()`**: хостовий процес CDN перехоплює аварійне завершення функції, повністю ігнорує збій та автоматично перенаправляє оригінальний вхідний запит на центральний Origin-сервер так, ніби крайової функції взагалі не існувало. Це критично важливо для шлюзів A/B-тестування та систем збору метрик, де збій експериментального коду не повинен переривати обслуговування користувачів.

---

## 2. Специфікація інтерфейсів `Request`, `Headers` та геометаданих

Об'єкт `Request` інкапсулює всі параметри вхідного HTTP-повідомлення, включаючи метод, URL-адресу, заголовки, потокове тіло та специфічні крайові метадані підключення.

```ts
interface Request {
  readonly method: string;
  readonly url: string;
  readonly headers: Headers;
  readonly body: ReadableStream<Uint8Array> | null;
  readonly bodyUsed: boolean;
  readonly redirect: RequestRedirect;
  readonly signal: AbortSignal;
  readonly cf?: IncomingRequestCfProperties;

  clone(): Request;
  arrayBuffer(): Promise<ArrayBuffer>;
  blob(): Promise<Blob>;
  json<T = unknown>(): Promise<T>;
  text(): Promise<string>;
}
```

### Особливості поведінки та методи класу `Request`

- **Незмінність (Immutability)**: вхідний об'єкт `request`, наданий середовищем, є доступним лише для читання. Спроба безпосередньо змінити його властивості (наприклад, `request.url = '...'` або `request.method = 'POST'`) викидає помилку типу `TypeError`. Для модифікації запиту необхідно створити новий екземпляр за допомогою конструктора `new Request(input, init)`.
- **Одноразове читання тіла (`bodyUsed`)**: властивість `body` є об'єктом `ReadableStream`. Після виклику методів зчитування (`.text()`, `.json()`, `.arrayBuffer()`) прапорець `bodyUsed` стає рівним `true`, а потік переходить у стан заблокованого (locked). Будь-яка наступна спроба прочитати потік або передати його у виклик `fetch()` викличе помилку `TypeError: Body has already been consumed`.
- **Клонування (`clone()`)**: створює точну копію запиту, використовуючи механізм роздвоєння потоку (Stream Teeing). Обидва екземпляри можуть бути прочитані незалежно, проте слід пам'ятати, що роздвоєння потоку збільшує навантаження на оперативну пам'ять, оскільки рантайм змушений буферизувати незчитані чанки у внутрішньому кільцевому буфері.

### Клас `Headers`: правила нормалізації та згортання

Клас `Headers` забезпечує роботу з заголовками протоколу HTTP згідно зі стандартом RFC 9110.

```ts
interface Headers {
  append(name: string, value: string): void;
  delete(name: string): void;
  get(name: string): string | null;
  has(name: string): boolean;
  set(name: string, value: string): void;
  forEach(callback: (value: string, name: string) => void): void;
  entries(): IterableIterator<[string, string]>;
  keys(): IterableIterator<string>;
  values(): IterableIterator<string>;
}
```

#### Правила роботи з заголовками в Edge Runtime
1. **Регістронезалежність імен**: усі імена заголовків автоматично нормалізуються до нижнього регістру (lowercase). Виклики `headers.get('Content-Type')` та `headers.get('content-type')` повертають ідентичний результат.
2. **Згортання повторюваних заголовків (Header Folding)**: якщо запит містить кілька однойменних заголовків, метод `headers.get(name)` повертає їхні значення, об'єднані через кому та пробіл (наприклад, `"gzip, deflate, br"`).
3. **Виняток для `Set-Cookie`**: заголовок `Set-Cookie` не може бути згорнутий через кому, оскільки дати в полі `Expires` самі містять коми. У сучасному стандарті для читання масиву окремих cookies використовується спеціалізований метод `headers.getSetCookie()`, що повертає масив незгорнутих рядків `string[]`.

### Крайові метадані підключення (`IncomingRequestCfProperties`)

У крайових середовищах об'єкт `Request` автоматично збагачується метаданими фізичного мережевого рівня:

| Поле | Тип | Семантичний зміст та приклад використання |
| :--- | :--- | :--- |
| `country` | `string` | Двозначний код країни згідно з ISO 3166-1 alpha-2 (наприклад, `"UA"` або `"PL"`). Використовується для геоблокування та вибору мови інтерфейсу. |
| `city` | `string` | Назва міста клієнта на основі бази BGP GeoIP (наприклад, `"Kyiv"` або `"Berlin"`). |
| `colo` | `string` | Трилітерний код найближчого аеропорту дата-центру CDN, який обробив запит (наприклад, `"KBP"`, `"FRA"`, `"WAW"`). Дозволяє точно діагностувати маршрутизацію трафіку. |
| `asn` | `number` | Номер автономної системи інтернет-провайдера клієнта (наприклад, `13335`). Допомагає виявляти трафік із центрів обробки даних або підозрілих хостингів. |
| `tlsVersion` | `string` | Версія використаного протоколу безпеки (наприклад, `"TLSv1.3"`). Дозволяє відхиляти застарілі та небезпечні клієнтські з'єднання. |
| `clientTcpRtt` | `number` | Виміряний час зворотного зв'язку TCP (RTT) між клієнтом і крайовим сервером у мілісекундах. Дозволяє оптимізувати якість стримінгу контенту. |

---

## 3. Специфікація інтерфейсу `Response`, Streams API та потокового парсера `HTMLRewriter`

Об'єкт `Response` інкапсулює HTTP-відповідь, що передається клієнту або надходить від бекенду під час виконання підзапиту.

```ts
interface ResponseInit {
  status?: number;
  statusText?: string;
  headers?: HeadersInit;
}

interface Response {
  readonly status: number;
  readonly statusText: string;
  readonly ok: boolean;
  readonly headers: Headers;
  readonly body: ReadableStream<Uint8Array> | null;
  readonly bodyUsed: boolean;

  clone(): Response;
  arrayBuffer(): Promise<ArrayBuffer>;
  json<T = unknown>(): Promise<T>;
  text(): Promise<string>;
}
```

### Потокова обробка: класи `ReadableStream`, `WritableStream` та `TransformStream`

У крайових середовищах із лімітом пам'яті 128 МБ категорично заборонено повністю вичитувати в пам'ять великі файли, відеопотоки або довгі HTML-документи. Будь-яка масштабована модифікація вмісту має виконуватися потоково за допомогою інтерфейсу `TransformStream`.

```ts
interface TransformStream<I = Uint8Array, O = Uint8Array> {
  readonly readable: ReadableStream<O>;
  readonly writable: WritableStream<I>;
}

interface Transformer<I, O> {
  start?(controller: TransformStreamDefaultController<O>): void;
  transform?(chunk: I, controller: TransformStreamDefaultController<O>): void | Promise<void>;
  flush?(controller: TransformStreamDefaultController<O>): void | Promise<void>;
}
```

### Механіка зворотного тиску (Backpressure)

Потокова модель Edge Runtime підтримує автоматичне керування зворотним тиском (англ. *Backpressure*):
- Якщо клієнт підключений через повільний мобільний зв'язок 3G і не встигає зчитувати байти з сокета, внутрішній буфер `TransformStream` заповнюється до встановленої верхньої межі (англ. *High Water Mark*, за замовчуванням кілька чанків);
- Щойно ліміт буфера досягнуто, метод `controller.enqueue()` призупиняє виконання методу `transform()`, а рантайм припиняє вичитування байтів із сокета Origin-сервера;
- Це унеможливлює неконтрольоване зростання споживання пам'яті в ізоляті незалежно від загального розміру переданого файлу (навіть для файлів обсягом 100 ГБ пам'ять ізоляту залишається стабільною на рівні 2–4 МБ).

### Потокова модифікація HTML: інтерфейс `HTMLRewriter`

Інтерфейс `HTMLRewriter` реалізує швидкий потоковий парсер на основі SAX-моделі (без побудови повного DOM-дерева в оперативній пам'яті). Він дозволяє перехоплювати HTML-теги за CSS-селекторами та модифікувати атрибути, вставляти фрагменти або змінювати текст прямо під час проходження потоку байтів до клієнта.

```ts
interface Element {
  readonly tagName: string;
  readonly attributes: IterableIterator<[string, string]>;
  readonly namespaceURI: string;
  getAttribute(name: string): string | null;
  hasAttribute(name: string): boolean;
  setAttribute(name: string, value: string): this;
  removeAttribute(name: string): this;
  before(content: string, options?: { html?: boolean }): this;
  after(content: string, options?: { html?: boolean }): this;
  prepend(content: string, options?: { html?: boolean }): this;
  append(content: string, options?: { html?: boolean }): this;
  setInnerContent(content: string, options?: { html?: boolean }): this;
  remove(): this;
  removeAndKeepContent(): this;
}

interface HTMLRewriter {
  on(selector: string, handlers: {
    element?(element: Element): void | Promise<void>;
    comments?(comment: unknown): void | Promise<void>;
    text?(text: unknown): void | Promise<void>;
  }): this;
  transform(response: Response): Response;
}
```

Використання `HTMLRewriter` забезпечує потокову динамічну персоналізацію HTML-сторінок (наприклад, підстановку імені користувача, CSRF-токенів чи локалізованих рядків) із затримкою обробки менше 1 мілісекунди та нульовою додатковою буферизацією.

---

## 4. Криптографічний інтерфейс: `crypto.subtle` (Web Crypto API)

Усі криптографічні операції на краю мережі виконуються через стандартизований неблокуючий інтерфейс `SubtleCrypto`, що забезпечує апаратне прискорення операцій безпосередньо в рушії V8.

```ts
interface SubtleCrypto {
  digest(algorithm: AlgorithmIdentifier, data: BufferSource): Promise<ArrayBuffer>;
  importKey(
    format: 'raw' | 'pkcs8' | 'spki' | 'jwk',
    keyData: BufferSource | JsonWebKey,
    algorithm: AlgorithmIdentifier | RsaHashedImportParams | HmacImportParams,
    extractable: boolean,
    keyUsages: KeyUsage[]
  ): Promise<CryptoKey>;
  sign(algorithm: AlgorithmIdentifier | HmacParams, key: CryptoKey, data: BufferSource): Promise<ArrayBuffer>;
  verify(algorithm: AlgorithmIdentifier | HmacParams, key: CryptoKey, signature: BufferSource, data: BufferSource): Promise<boolean>;
  encrypt(algorithm: AlgorithmIdentifier | AesGcmParams, key: CryptoKey, data: BufferSource): Promise<ArrayBuffer>;
  decrypt(algorithm: AlgorithmIdentifier | AesGcmParams, key: CryptoKey, data: BufferSource): Promise<ArrayBuffer>;
}
```

### Порівняльна характеристика криптографічних примітивів

1. **Симетричні підписи HMAC-SHA256**: ідеально підходять для валідації короткоживучих токенів сесій і підписаних URL-адрес. Час виконання операції перевірки становить менше 0.15 мс, що дозволяє валідувати кожен вхідний запит без зростання затримки.
2. **Асиметричні підписи RSA та ECDSA**: використовуються для перевірки відкритих ключів сторонніх провайдерів ідентифікації (Auth0, Firebase, Google Identity). Для мінімізації навантаження на CPU відкриті ключі JWKS повинні кешуватися в пам'яті ізоляту або в крайовому кеші з тривалим строком життя.
3. **Автентифіковане шифрування AES-256-GCM**: гарантує як конфіденційність, так і цілісність зашифрованих даних (захист від модифікації шифротексту). Використовується для безпечного збереження чутливих даних у незашифрованих сховищах клієнта (Cookies).

---

## 5. Інтерфейс крайового кешу: `Cache` та `caches.default`

Інтерфейс `Cache API` надає функціям пряме програмне керування локальним сховищем швидкого кешу на поточному PoP-вузлі.

```ts
interface Cache {
  match(request: RequestInfo, options?: { ignoreMethod?: boolean }): Promise<Response | undefined>;
  put(request: RequestInfo, response: Response): Promise<void>;
  delete(request: RequestInfo, options?: { ignoreMethod?: boolean }): Promise<boolean>;
}
```

### Життєвий цикл та правила взаємодії з кешем

1. **Формування ключа кешування (Cache Key)**: за замовчуванням ключем виступає повна канонічна URL-адреса запиту. Проте функція може створити власний кастомний ключ (Custom Cache Key), додавши в нього параметри заголовків (наприклад, тип пристрою або валюту користувача), використовуючи конструктор `new Request(customUrl)`.
2. **Ієрархія дворівневого кешування (Tiered Cache)**: у разі промаху на локальному PoP крайовий вузол може спочатку звернутися до регіонального верхнього рівня кешу (Upper-tier PoP), перш ніж надсилати запит на далекий Origin-сервер.
3. **Обробка `stale-while-revalidate`**: директива HTTP-заголовка `Cache-Control: max-age=60, stale-while-revalidate=300` дозволяє крайовому вузлу миттєво віддати клієнту трохи застарілу відповідь із кешу (у вікні до 300 секунд), одночасно запустивши у фоні через `ctx.waitUntil()` оновлення кешу з Origin-сервера.

---

## 6. Інтерфейс розподіленого сховища `KVNamespace`

Розподілене сховище ключ-значення реалізує модель високої доступності та низької затримки читання, жертвуючи строгою миттєвою узгодженістю запису на користь узгодженості в кінцевому підсумку (Eventual Consistency).

```ts
interface KVNamespace {
  get(key: string, options?: { cacheTtl?: number }): Promise<string | null>;
  get<T>(key: string, options: { type: 'json'; cacheTtl?: number }): Promise<T | null>;
  get(key: string, options: { type: 'arrayBuffer'; cacheTtl?: number }): Promise<ArrayBuffer | null>;
  get(key: string, options: { type: 'stream'; cacheTtl?: number }): Promise<ReadableStream | null>;

  getWithMetadata<T = unknown, M = unknown>(
    key: string,
    options?: { type: 'json'; cacheTtl?: number }
  ): Promise<{ value: T | null; metadata: M | null }>;

  put(
    key: string,
    value: string | ArrayBuffer | ReadableStream,
    options?: { expiration?: number; expirationTtl?: number; metadata?: unknown }
  ): Promise<void>;

  delete(key: string): Promise<void>;

  list<M = unknown>(options?: {
    prefix?: string;
    limit?: number;
    cursor?: string;
  }): Promise<{
    keys: Array<{ name: string; expiration?: number; metadata?: M }>;
    list_complete: boolean;
    cursor?: string;
  }>;
}
```

### Механізм локального кешування на PoP (`cacheTtl`)

Коли крайова функція зчитує значення через метод `kv.get(key, { cacheTtl: 300 })`:
- Під час першого читання значення завантажується з центрального розподіленого сховища й кешується безпосередньо в оперативній пам'яті або локальному сховищі поточного PoP на 300 секунд;
- Усі наступні запити з цього ж географічного регіону отримують значення за 1–2 мілісекунди без мережевих звернень до центрального кластера;
- Оновлення значення через `kv.put()` глобально реплікується по всіх PoP протягом 10–60 секунд.

---

## 7. Міжсервісна комунікація в пам'яті: Service Bindings та Worker RPC

У мікросервісних архітектурах на краю традиційні HTTP-підзапити через `fetch('https://auth-service.internal/...')` створюють зайві накладні витрати на серіалізацію HTTP-заголовків, проходження через віртуальний мережевий стек та повторне розпізнавання DNS.

Для усунення цих затримок стандарт Edge Runtime надає інтерфейс **Service Bindings** та систему прямого виклику віддалених процедур у пам'яті (**Worker RPC**).

```ts
interface Fetcher {
  fetch(input: RequestInfo, init?: RequestInit): Promise<Response>;
}

// Прямий виклик типізованого RPC-інтерфейсу суміжного воркера
interface AuthService {
  validateSession(token: string): Promise<{ userId: string; role: string }>;
  revokeToken(token: string): Promise<boolean>;
}

interface Env {
  AUTH_WORKER: Fetcher & AuthService;
}
```

### Механіка прямого виклику Service Binding
1. **Нульовий оверхед мережевого стека**: виклик `env.AUTH_WORKER.validateSession(token)` виконується як пряма передача повідомлення між двома ізолятами V8 у межах одного фізичного процесу хоста.
2. **Структурована серіалізація**: аргументи та повернені значення клонуються через алгоритм Structured Clone Algorithm (V8 Serializer), уникаючи текстової конвертації в JSON.
3. **Затримка виклику менше 0.05 мілісекунди**: прямий RPC-виклик працює на три порядки швидше за традиційний мережевий HTTP-запит.

---

## 8. Стійкі об'єкти з транзакційним станом: Durable Objects

Для завдань, що вимагають строгої послідовної узгодженості (Strong Consistency), координації між користувачами в реальному часі та двостороннього зв'язку через WebSockets, використовується інтерфейс **Durable Objects**.

Durable Object поєднує модель акторів (Actor Model) із транзакційним сховищем ключ-значення, гарантуючи, що для конкретного ідентифікатора у світі в будь-який момент часу існує рівно один активний екземпляр класу.

```ts
interface DurableObjectState {
  readonly id: DurableObjectId;
  readonly storage: DurableObjectStorage;
  waitUntil(promise: Promise<unknown>): void;
  acceptWebSocket(ws: WebSocket, tags?: string[]): void;
  getWebSockets(tag?: string): WebSocket[];
}

interface DurableObjectStorage {
  get<T = unknown>(key: string): Promise<T | undefined>;
  get<T = unknown>(keys: string[]): Promise<Map<string, T>>;
  put<T = unknown>(key: string, value: T): Promise<void>;
  put<T = unknown>(entries: Record<string, T>): Promise<void>;
  delete(key: string): Promise<boolean>;
  delete(keys: string[]): Promise<number>;
  deleteAll(): Promise<void>;
  list<T = unknown>(options?: { prefix?: string; start?: string; end?: string; limit?: number }): Promise<Map<string, T>>;
  transaction<T>(closure: (txn: DurableObjectTransaction) => Promise<T>): Promise<T>;
}

interface DurableObject {
  fetch(request: Request): Promise<Response> | Response;
}
```

### Механіка транзакцій та координації
- **Ізоляція та відсутність стану гонитви**: усі вхідні HTTP-запити та повідомлення WebSockets до одного екземпляра Durable Object обробляються послідовно в єдиному однопотоковому циклі подій. Це усуває потребу в розподілених блокуваннях (Distributed Locks) і м'ютексах;
- **Транзакційне сховище**: метод `storage.transaction()` гарантує виконання групи операцій запису за принципом атомарності ACID. Якщо під час транзакції виникає помилка, всі проміжні зміни автоматично відкочуються до попереднього стану.

---

## 9. Ліміти ресурсів, квоти та системні помилки

Крайові функції працюють під суворим контролем планувальника ресурсів хостової операційної системи.

| Категорія обмеження | Значення квоти | Поведінка системи у разі перевищення |
| :--- | :--- | :--- |
| **CPU Time (час процесора)** | 10–50 мс на виклик | Лічильник враховує лише активні інструкції CPU (без очікування I/O). При перевищенні ізолят примусово знищується з кодом `1102`. |
| **Wall-clock Time (астрономічний час)** | До 100 секунд | Враховує час очікування відповідей від зовнішніх API через мережеві сокети. |
| **Оперативна пам'ять (RAM)** | 128 МБ на ізолят | Виділяється під купу V8. При вичерпанні генерується помилка `1027 Out of Memory`. |
| **Кількість підзапитів (`fetch`)** | 50–1000 на запит | Запобігає створенню паразитного ампліфікованого трафіку та безкінечних рекурсивних викликів. |
| **Розмір ключа KV** | До 512 байт | Виняткова ситуація під час спроби збереження занадто довгого ключа. |
| **Розмір значення KV** | До 25 МБ | Для більших об'ємів даних необхідно використовувати спеціалізовані об'єктні сховища (R2/S3). |

### Таблиця діагностичних кодів помилок платформи

- **1015 (Rate Limited)**: спрацював алгоритм захисту від перевантаження (Leaky Bucket / Token Bucket). Потрібно збільшити ліміти або додати кешування.
- **1101 (Worker Threw Exception)**: у тілі функції стався необроблений виняток (наприклад, читання поля у `null`). Для усунення слід перевірити логи або скористатися методом `ctx.passThroughOnException()`.
- **1102 (CPU Time Limit Exceeded)**: алгоритм усередині функції (наприклад, складне регулярне вираження або парсинг масивного JSON) спожив забагато тактів процесора. Необхідно оптимізувати обчислювальний код або замінити його на WebAssembly модуль.
- **1042 (Subrequest Depth Limit)**: зафіксовано нескінченний цикл підзапитів, коли функція помилково викликає сама себе. Потрібно перевірити логіку визначення кінцевої точки Origin.
