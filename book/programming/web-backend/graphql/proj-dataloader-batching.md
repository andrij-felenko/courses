# ⚙️ Розв'язання проблеми N+1 через патерн DataLoader

У типовому вебінтерфейсі сутності рідко існують ізольовано: користувачі публікують статті, статті містять коментарі, коментарі посилаються на авторів, а автори належать до організацій та мають індивідуальні ролі. Коли клієнт надсилає GraphQL-запит на отримання списку публікацій разом із даними їхніх авторів, незалежні функції-резолвери кожного поля стикаються з класичною пасткою продуктивності — **проблемою N+1 запитів до бази даних**.

Цей проєкт демонструє покрокову анатомію виникнення проблеми N+1 у дереві резолверів, математику навантаження на систему введення-виведення (I/O), детальне простеження черги мікротасок у часі, роботу зі зв'язками один-до-багатьох, складеними ключами, поліморфними сутностями, інтеграцію в мікросервіси, дворівневе кешування з Redis, тонкощі багатопотоковості в C++, стратегії тестування та повну виробничу реалізацію патерну DataLoader мовами TypeScript та C++.

---

### 1. Анатомія проблеми N+1 у графі резолверів

Розглянемо GraphQL-запит, що завантажує стрічку з 20 останніх публікацій та інформацію про автора для кожної з них:

```graphql
query GetFeedWithAuthors {
  feed(limit: 20) {
    id
    title
    author {
      id
      name
      avatarUrl
    }
  }
}
```

У наївній реалізації серверний рушій виконує резолвери зверху вниз за ієрархією графа:

1. Спочатку викликається кореневий резолвер `Query.feed`:
   ```sql
   SELECT id, title, author_id FROM posts ORDER BY created_at DESC LIMIT 20;
   ```
2. Сервер отримує масив із 20 об'єктів публікацій.
3. Для кожного елемента масиву рушій паралельно запускає резолвер дочірнього поля `Post.author`:
   ```typescript
   // Наївний резолвер поля Post.author
   const resolvers = {
     Post: {
       author: async (post, args, context) => {
         return await context.db.query(
           "SELECT id, name, avatar_url FROM users WHERE id = ?",
           [post.author_id]
         );
       }
     }
   };
   ```

Оскільки резолвер `Post.author` є повністю ізольованою функцією, яка знає лише про свій поточний батьківський об'єкт `post`, він змушений виконати окремий мережевий запит до бази даних для кожного рядка.

**Підсумок наївного виконання:**
- 1 запит для отримання списку публікацій.
- 20 окремих запитів для отримання авторів.
- Разом: `1 + 20 = 21` запит до сховища.

Якщо кожна з 20 публікацій містить ще й список із 5 коментарів, а кожен коментар резолвить свого автора, кількість запитів зростає лавиноподібно:
```
1 (пости) + 20 (автори постів) + 20 (списки коментарів) + 100 (автори коментарів) = 141 запит до БД!
```

Навіть якщо 10 публікацій написані одним і тим самим користувачем (наприклад, автором із `id: "42"`), наївний код виконає абсолютно ідентичний SQL-запит `SELECT ... WHERE id = 42` десять разів поспіль. База даних отримує масований сплеск однакових операцій читання, пул мережевих з'єднань блокується, а час відповіді сервера (latency) зростає пропорційно до розміру стрічки.

---

### 2. Принцип роботи DataLoader: коалесценція та мемоізація

Патерн **DataLoader** розв'язує проблему N+1 за допомогою поєднання двох взаємопов'язаних механізмів:

1. **Коалесценція ключів і батчинг (Batching / Key Coalescing):** Коли резолвер викликає метод `load(key)`, DataLoader не надсилає запит до бази даних негайно. Замість цього він зберігає ідентифікатор у черзі поточного пакета і планує виконання запиту на наступному мікротакті циклу подій (Microtask Queue у JavaScript або відкладена черга в C++). Усі виклики `load()`, зроблені резолверами одного рівня дерева під час поточного синхронного обходу, об'єднуються в єдиний масив унікальних ключів `[id1, id2, ..., idN]`. Потім виконується один груповий SQL-запит:
   ```sql
   SELECT id, name, avatar_url FROM users WHERE id IN (10, 11, 42, 99);
   ```
2. **Мемоізація в межах одного запиту (Per-Request Caching):** DataLoader зберігає створений проміс у локальній хеш-таблиці `Map`. Якщо в межах одного HTTP-запиту метод `load(42)` викликається повторно (наприклад, у різних гілках дерева резолверів), DataLoader негайно повертає вже наявний проміс без додавання дубльованого ключа в чергу пакета.

```
Резолвери Post.author (20 паралельних викликів):
loader.load(10) ──┐
loader.load(42) ──┼──► [ Черга ключів: {10, 42, 15} ] ──► SELECT * FROM users
loader.load(42) ──┤          (усунено дублікати)            WHERE id IN (10, 42, 15)
loader.load(15) ──┘                   │                                │
                                      ▼                                ▼
                         Розподіл результатів за Promise ◄── Масив значень [U10, U42, U15]
```

---

### 3. Простеження життєвого циклу запиту в часі

Щоб зрозуміти, чому DataLoader спрацьовує автоматично без явного очікування, простежимо покроковий хронометраж виконання в циклі подій (Event Loop):

- **Момент `t0`:** Кореневий резолвер `Query.feed` завершує асинхронний запит до таблиці публікацій і повертає масив із 20 об'єктів `Post`.
- **Момент `t1`:** Рушій GraphQL запускає синхронний цикл обчислення дочірніх полів першого рівня. Викликається перший резолвер `Post[0].author`. Він викликає `userLoader.load(10)`.
- **Момент `t2`:** Метод `load(10)` створює новий об'єкт `Promise`, додає ключ `10` у внутрішню чергу `queue` і викликає `queueMicrotask(dispatchQueue)`. Планувальник черги мікротасок запам'ятовує функцію `dispatchQueue`, але ще не виконує її, оскільки поточний синхронний стек зайнятий.
- **Момент `t3`:** Рушій GraphQL переходить до наступних елементів `Post[1]...Post[19]`. Усі відповідні резолвери синхронно викликають `userLoader.load(id)`. Кожен виклик додає свій ключ у масив `queue` і повертає нерозв'язаний `Promise`. Оскільки планування мікротаски вже відбулося (`batchScheduled = true`), нові мікротаски не створюються.
- **Момент `t4`:** Синхронний прохід рушія по всіх 20 резолверах завершено. Поточний стек викликів звільняється.
- **Момент `t5`:** Двигун JavaScript (V8) переходить до виконання накопиченої черги мікротасок. Викликається функція `dispatchQueue()`.
- **Момент `t6`:** Функція `dispatchQueue()` забирає всі накопичені 20 ключів із черги, формує масив унікальних ідентифікаторів і викликає користувацьку пакетну функцію `batchGetUsersByIds([10, 42, ...])`.
- **Момент `t7`:** Виконується один SQL-запит `WHERE id IN (...)`. Отримані з бази рядки перевпорядковуються у відповідність до вихідного порядку ключів.
- **Момент `t8`:** DataLoader послідовно викликає `resolve(user)` для кожного з 20 промісів, які очікували в резолверах. Усі 20 резолверів одночасно отримують свої дані й повертають значення рушію GraphQL.

Замість 20 послідовних або розрізнених звернень до бази даних система виконала рівно один пакетний запит.

---

### 4. Суворий контракт пакетної функції (Batch Function Contract)

Пакетна функція користувача приймає масив ключів `keys: K[]` і повертає масив результатів `Promise<(V | Error)[]>`.

Специфікація DataLoader висуває три обов'язкові інваріанти:

1. **Ідентична довжина масиву:** Довжина повернутого масиву результатів повинна суворо дорівнювати довжині вхідного масиву ключів:
   ```
   keys.length === results.length
   ```
2. **Точна відповідність індексів:** Елемент `results[i]` зобов'язаний відповідати ключу `keys[i]`. Якщо база даних повернула записи в довільному порядку (що є стандартною поведінкою оператора `WHERE id IN (...)`), пакетна функція зобов'язана самостійно перевпорядкувати результати відповідно до вихідного масиву `keys`.
3. **Обробка відсутніх значень:** Якщо для певного ключа запис у базі відсутній, на відповідній позиції має стояти `null` (або екземпляр `Error`). Пропускати індекс категорично заборонено, інакше всі наступні значення змістяться і потраплять до чужих резолверів.

---

### 5. Повна реалізація патерну DataLoader мовами TypeScript та C++

Нижче наведено повноцінні виробничі реалізації мінімального рушія DataLoader мовами TypeScript та C++.

:::tabs
```ts
// TypeScript: Ідіоматична реалізація DataLoader з чергою мікротасок

type BatchFunction<K, V> = (keys: ReadonlyArray<K>) => Promise<Array<V | Error>>;

interface DataLoaderOptions<K> {
  maxBatchSize?: number;
  cache?: boolean;
  cacheKeyFn?: (key: K) => string;
}

export class DataLoader<K, V> {
  private readonly batchFn: BatchFunction<K, V>;
  private readonly maxBatchSize: number;
  private readonly useCache: boolean;
  private readonly cacheKeyFn: (key: K) => any;
  
  // Черга ключів та відповідних їм Promise triggers для поточного пакета
  private queue: Array<{
    key: K;
    resolve: (value: V) => void;
    reject: (error: Error) => void;
  }> = [];
  
  // Локальний мемоізаційний кеш у межах одного екземпляра
  private cacheMap: Map<any, Promise<V>> = new Map();
  private batchScheduled: boolean = false;

  constructor(batchFn: BatchFunction<K, V>, options: DataLoaderOptions<K> = {}) {
    this.batchFn = batchFn;
    this.maxBatchSize = options.maxBatchSize ?? 1000;
    this.useCache = options.cache ?? true;
    this.cacheKeyFn = options.cacheKeyFn ?? ((k: K) => k);
  }

  public load(key: K): Promise<V> {
    const cacheKey = this.cacheKeyFn(key);

    // 1. Якщо увімкнено кеш і ключ уже запитувався — повертаємо готовий Promise
    if (this.useCache) {
      const cached = this.cacheMap.get(cacheKey);
      if (cached !== undefined) {
        return cached;
      }
    }

    // 2. Створюємо новий Promise і додаємо його в чергу відкладеного виконання
    const promise = new Promise<V>((resolve, reject) => {
      this.queue.push({ key, resolve, reject });

      // Якщо черга досягла максимального розміру — скидаємо негайно
      if (this.queue.length >= this.maxBatchSize) {
        this.dispatchQueue();
      } else if (!this.batchScheduled) {
        // Плануємо скидання черги на наступний такт мікротасок
        this.batchScheduled = true;
        queueMicrotask(() => this.dispatchQueue());
      }
    });

    if (this.useCache) {
      this.cacheMap.set(cacheKey, promise);
    }

    return promise;
  }

  public loadMany(keys: ReadonlyArray<K>): Promise<Array<V | Error>> {
    return Promise.all(
      keys.map((key) => this.load(key).catch((err: Error) => err))
    );
  }

  public clear(key: K): this {
    const cacheKey = this.cacheKeyFn(key);
    this.cacheMap.delete(cacheKey);
    return this;
  }

  public clearAll(): this {
    this.cacheMap.clear();
    return this;
  }

  public prime(key: K, value: V | Error): this {
    const cacheKey = this.cacheKeyFn(key);
    if (!this.cacheMap.has(cacheKey)) {
      const promise = value instanceof Error 
        ? Promise.reject(value) 
        : Promise.resolve(value);
      // Запобігаємо unhandled rejection для помилок у кеші
      promise.catch(() => {});
      this.cacheMap.set(cacheKey, promise);
    }
    return this;
  }

  private async dispatchQueue(): Promise<void> {
    this.batchScheduled = false;
    const currentQueue = this.queue;
    this.queue = [];

    if (currentQueue.length === 0) return;

    const keys = currentQueue.map((item) => item.key);

    try {
      // Викликаємо користувацьку пакетну функцію
      const values = await this.batchFn(keys);

      // Перевіряємо суворий інваріант контракту DataLoader
      if (values.length !== keys.length) {
        throw new TypeError(
          `DataLoader batch function must return array of length ${keys.length}, but got ${values.length}`
        );
      }

      // Розподіляємо значення по індивідуальних промісах
      for (let i = 0; i < currentQueue.length; i++) {
        const result = values[i];
        if (result instanceof Error) {
          currentQueue[i].reject(result);
        } else {
          currentQueue[i].resolve(result);
        }
      }
    } catch (error) {
      // Якщо впала вся пакетна функція — відхиляємо всі проміси поточного пакета
      const err = error instanceof Error ? error : new Error(String(error));
      for (const item of currentQueue) {
        item.reject(err);
      }
    }
  }
}
```
```cpp
// C++: Ідіоматична потокобезпечна реалізація DataLoader на базі std::future та RAII

#include <iostream>
#include <vector>
#include <unordered_map>
#include <memory>
#include <future>
#include <functional>
#include <mutex>
#include <stdexcept>
#include <string>

template <typename Key, typename Value>
class DataLoader {
public:
    using BatchFunction = std::function<std::vector<Value>(const std::vector<Key>&)>;

    explicit DataLoader(BatchFunction batchFn, size_t maxBatchSize = 1000)
        : batchFn_(std::move(batchFn)), maxBatchSize_(maxBatchSize) {}

    // Метод load реєструє ключ і повертає std::shared_future на майбутній результат
    std::shared_future<Value> load(const Key& key) {
        std::lock_guard<std::mutex> lock(mutex_);

        // 1. Перевіряємо наявність у кеші
        auto it = cache_.find(key);
        if (it != cache_.end()) {
            return it->second;
        }

        // 2. Створюємо новий promise для асинхронного результату
        auto promisePtr = std::make_shared<std::promise<Value>>();
        std::shared_future<Value> future = promisePtr->get_future().share();
        cache_.emplace(key, future);

        queue_.push_back({key, promisePtr});

        return future;
    }

    // Скидання черги: виконання пакетного запиту для всіх накопичених ключів
    void dispatch() {
        std::vector<QueueItem> currentQueue;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (queue_.empty()) return;
            currentQueue = std::move(queue_);
            queue_.clear();
        }

        std::vector<Key> keys;
        keys.reserve(currentQueue.size());
        for (const auto& item : currentQueue) {
            keys.push_back(item.key);
        }

        try {
            // Виклик користувацької пакетної функції
            std::vector<Value> results = batchFn_(keys);

            if (results.size() != keys.size()) {
                throw std::runtime_error(
                    "DataLoader batch function returned vector of incorrect size: expected " +
                    std::to_string(keys.size()) + ", got " + std::to_string(results.size())
                );
            }

            // Розподіл результатів по promise
            for (size_t i = 0; i < currentQueue.size(); ++i) {
                currentQueue[i].promise->set_value(results[i]);
            }
        } catch (...) {
            auto ex = std::current_exception();
            for (auto& item : currentQueue) {
                item.promise->set_exception(ex);
            }
        }
    }

    void clear(const Key& key) {
        std::lock_guard<std::mutex> lock(mutex_);
        cache_.erase(key);
    }

    void clearAll() {
        std::lock_guard<std::mutex> lock(mutex_);
        cache_.clear();
    }

private:
    struct QueueItem {
        Key key;
        std::shared_ptr<std::promise<Value>> promise;
    };

    BatchFunction batchFn_;
    size_t maxBatchSize_;
    std::mutex mutex_;
    std::vector<QueueItem> queue_;
    std::unordered_map<Key, std::shared_future<Value>> cache_;
};
```
:::

---

### 6. Багатопотоковість і модель пам'яті в C++

Реалізація DataLoader у мовах із підтримкою справжньої багатопотоковості (C++, Rust) має принципові відмінності від однопотокової моделі циклу подій JavaScript:

1. **Чому `std::shared_future`, а не `std::future`:**
   Стандартний `std::future` у C++ є типом, який можна лише переміщувати (`move-only`), а його метод `get()` можна викликати лише один раз для вилучення значення. Якщо кілька паралельних резолверів запитують одного й того самого автора (наприклад, пости 1 і 5 належать користувачу 42), виклик `get()` на другому потоці призведе до викидання фатального винятку `std::future_error` із кодом `no_state`.
   Використання `std::shared_future` дозволяє безпечно копіювати дескриптор майбутнього результату та викликати метод `get()` довільну кількість разів із різних потоків виконання.
2. **Захист стану через RAII:**
   Оскільки паралельні резолвери можуть одночасно викликати `load()` з різних потоків робочого пулу, доступ до внутрішнього контейнера `queue_` та таблиці `cache_` захищений блокуванням `std::lock_guard<std::mutex>`.
3. **Відокремлення черги під час `dispatch()`:**
   У методі `dispatch()` черга `queue_` миттєво переміщується у локальний вектор під коротким блокуванням м'ютекса, після чого м'ютекс звільняється. Важка операція введення-виведення (SQL-запит або мережевий RPC-виклик) виконується **поза критичною секцією блокування**. Це дозволяє іншим потокам безперешкодно продовжувати реєстрацію нових ключів для наступного пакета без взаємних блокувань.

---

### 7. Робота зі зв'язками один-до-багатьох (1-to-Many Batching)

Особливий випадок пакетування виникає, коли кожне батьківське поле очікує не один об'єкт, а список сутностей (наприклад, резолвер `Post.comments` повертає масив `[Comment!]!`).

Якщо 20 постів запитують свої коментарі, наївний підхід виконає 20 окремих SQL-запитів `SELECT * FROM comments WHERE post_id = ?`.

Для пакетизації зв'язку один-до-багатьох створюється спеціалізований лоадер, пакетна функція якого групує рядки за зовнішнім ключем:

```typescript
// Пакетна функція для зв'язку 1-до-багатьох: Post -> Comments[]
async function batchGetCommentsByPostIds(
  postIds: ReadonlyArray<string>,
  db: DatabaseConnection
): Promise<Array<Comment[]>> {
  // 1. Отримуємо всі коментарі для всіх постів одним запитом
  const rows = await db.query<CommentRow>(
    "SELECT id, post_id, content, author_id FROM comments WHERE post_id IN (?)",
    [postIds]
  );

  // 2. Групуємо коментарі у словник за post_id
  const commentsByPostId = new Map<string, Comment[]>();
  for (const postId of postIds) {
    commentsByPostId.set(postId, []);
  }

  for (const row of rows) {
    const list = commentsByPostId.get(row.post_id);
    if (list !== undefined) {
      list.push({
        id: row.id,
        content: row.content,
        authorId: row.author_id
      });
    }
  }

  // 3. Повертаємо масив списків у ТОЧНОМУ порядку вихідних postIds
  return postIds.map((postId) => commentsByPostId.get(postId) ?? []);
}
```

Резолвер поля `Post.comments` набуває максимально компактного вигляду:

```typescript
const resolvers = {
  Post: {
    comments: (post, _args, context) => {
      return context.loaders.commentsByPostLoader.load(post.id);
    }
  }
};
```

---

### 8. Складені ключі та функція кешування (cacheKeyFn)

За замовчуванням `Map` у JavaScript порівнює ключі за посиланням (`===`). Якщо ключ є складним об'єктом (наприклад, пара `{ userId: "42", role: "ADMIN" }`), два однакових за значенням об'єкти вважатимуться різними ключами в кеші.

Параметр `cacheKeyFn` серіалізує складений об'єкт у детермінований строковий ключ, зберігаючи працездатність кешу:

```typescript
interface PermissionKey {
  userId: string;
  organizationId: string;
}

const permissionLoader = new DataLoader<PermissionKey, Permission[]>(
  async (keys) => batchFetchPermissions(keys),
  {
    cacheKeyFn: (key) => `${key.organizationId}:${key.userId}`
  }
);
```

---

### 9. Дворівневе кешування: поєднання L1 (Request Memory) та L2 (Shared Redis)

У високонавантажених системах виникає потреба кешувати сутності не лише в межах одного HTTP-запиту, а й між мільйонами різних користувачів через спільний Redis-кластер.

DataLoader стає координатором дворівневої стратегії кешування:
1. **Рівень L1 (In-Memory Request Cache):** Миттєво обслуговує запити одного графа GraphQL без мережевих затримок.
2. **Рівень L2 (Distributed Redis Cache):** Пакетна функція DataLoader перед зверненням до SQL виконує команду `MGET user:10 user:11 user:42`. Усі знайдені ключі беруться з Redis, а до первинної бази даних PostgreSQL надсилаються лише ті ідентифікатори, яких не було в кеші (`Cache Misses`).
3. Нові завантажені сутності записуються назад у Redis за допомогою пакетної команди `MSET` або конвеєра (Pipeline) з відповідним часом життя `TTL`.

Це поєднання зменшує навантаження на первинну реляційну базу на 90–98%, повністю зберігаючи переваги автоматичного батчингу.

---

### 10. DataLoader у мікросервісних архітектурах та gRPC

У сучасних розподілених системах дані публікацій та дані користувачів часто зберігаються не в одній базі даних, а в різних незалежних сервісах. У такому середовищі прямий SQL JOIN неможливий фізично.

DataLoader стає єдиним універсальним адаптером між графом GraphQL та зовнішніми мережевими RPC-викликами:
1. Замість SQL-запиту пакетна функція формує єдиний пакетний RPC-виклик:
   ```protobuf
   // gRPC Protobuf контракт
   message BatchUserRequest {
     repeated string user_ids = 1;
   }
   message BatchUserResponse {
     repeated User users = 1;
   }
   ```
2. DataLoader збирає 50 ідентифікаторів з різних резолверів, виконує один gRPC-виклик через протокол HTTP/2, отримує бінарну відповідь, розпаковує protobuf-повідомлення та розсилає результати відповідним промісам.
3. Мережеві накладні витрати на встановлення TCP-з'єднань, TLS-рукостискання та передачу HTTP-заголовків зменшуються на 95%.

---

### 11. Поліморфний DataLoader для глобальних вузлів Node(id)

У схемах, побудованих за специфікацією Relay Global Object Identification, клієнт може запитати список довільних поліморфних вузлів через єдиний корінь `nodes(ids: [ID!]!): [Node]`.

Ідентифікатор глобального вузла зазвичай містить закодований префікс типу: `"User:42"`, `"Post:101"`, `"Comment:500"`.

Поліморфний маршрутизатор DataLoader розбиває вхідний масив ключів за типами сутностей:

```typescript
async function polymorphicNodeBatchLoader(
  globalIds: ReadonlyArray<string>,
  context: ExecutionContext
): Promise<Array<Node | Error>> {
  // 1. Групуємо ключі за типом сутності
  const userIds: string[] = [];
  const postIds: string[] = [];
  const commentIds: string[] = [];

  for (const gid of globalIds) {
    const [type, rawId] = gid.split(":");
    if (type === "User") userIds.push(rawId);
    else if (type === "Post") postIds.push(rawId);
    else if (type === "Comment") commentIds.push(rawId);
  }

  // 2. Паралельно викликаємо спеціалізовані лоадери для кожного типу
  const [users, posts, comments] = await Promise.all([
    context.loaders.userLoader.loadMany(userIds),
    context.loaders.postLoader.loadMany(postIds),
    context.loaders.commentLoader.loadMany(commentIds)
  ]);

  // 3. Індексуємо знайдені сутності в єдиний Map
  const nodeMap = new Map<string, Node>();
  userIds.forEach((id, i) => {
    const u = users[i];
    if (!(u instanceof Error)) nodeMap.set(`User:${id}`, u);
  });
  postIds.forEach((id, i) => {
    const p = posts[i];
    if (!(p instanceof Error)) nodeMap.set(`Post:${id}`, p);
  });
  commentIds.forEach((id, i) => {
    const c = comments[i];
    if (!(c instanceof Error)) nodeMap.set(`Comment:${id}`, c);
  });

  // 4. Повертаємо результати у вихідному порядку вхідних globalIds
  return globalIds.map((gid) => nodeMap.get(gid) ?? new Error(`Вузол ${gid} не знайдено`));
}
```

---

### 12. DataLoader проти SQL JOIN-компіляції (Lookahead / AST Inspection)

Альтернативним підходом до розв'язання проблеми N+1 є техніка **попереднього аналізу вибірки (Lookahead)** або використання спеціалізованих рушіїв (Hasura, PostGraphile), які транслюють увесь GraphQL-запит в один гігантський SQL-вираз із багатьма `LEFT JOIN` та агрегаціями `json_agg()`.

Порівняння архітектурних властивостей обох підходів:

| Критерій | Патерн DataLoader | SQL JOIN-компіляція (Lookahead) |
|---|---|---|
| **Джерела даних** | Повністю універсальний: об'єднує PostgreSQL, MongoDB, Redis, сторонні REST API та gRPC-мікросервіси в єдиному графі. | Обмежений виключно однією реляційною базою даних. Не працює для зовнішніх API та кешів. |
| **Ізоляція доменної логіки** | Кожен резолвер інкапсулює власні бізнес-правила, авторизацію та трансформацію сутностей. | Логіка авторизації та об'єднання вшита в генератор SQL або перевіряється на рівні рядків у БД (Row-Level Security). |
| **Навантаження на пам'ять БД** | Кілька простих запитів `WHERE id IN (...)` за індексом. Легко кешуються в Buffer Pool бази. | Складні багатотабличні JOIN-запити можуть викликати декартовий добуток рядків (Cartesian Explosion) при глибокій вкладеності списків. |
| **Складність кодової бази** | Прості, незалежні резолвери, що легко тестуються модульними тестами (Unit Tests). | Складний компілятор запитів, що вимагає глибокого парсингу `info.fieldNodes` та AST. |

DataLoader є золотим стандартом для сервісно-орієнтованих та мікросервісних архітектур, де різні типи даних фізично зберігаються в різних сховищах і мікросервісах.

---

### 13. Стратегія модульного тестування резолверів з DataLoader

Завдяки інкапсуляції пакетної функції, тестування GraphQL-резолверів стає простим і детермінованим. Для перевірки відсутності N+1 викликів не потрібно піднімати реальну базу даних: достатньо передати тестовий екземпляр лоадера з функцією-шпигуном (Spy):

```typescript
test("резолвер Post.author пакетує виклики і усуває N+1", async () => {
  let batchExecutionCount = 0;
  
  const mockBatchFn = async (ids: ReadonlyArray<string>) => {
    batchExecutionCount++;
    return ids.map((id) => ({ id, name: `User ${id}`, avatarUrl: "http://..." }));
  };

  const testLoader = new DataLoader(mockBatchFn);
  const context = { loaders: { userLoader: testLoader } };

  // Імітуємо виконання 10 резолверів для 10 постів (автори 1, 2, 1, 3, 2...)
  const promises = [
    resolvers.Post.author({ author_id: "1" }, {}, context),
    resolvers.Post.author({ author_id: "2" }, {}, context),
    resolvers.Post.author({ author_id: "1" }, {}, context),
    resolvers.Post.author({ author_id: "3" }, {}, context),
  ];

  const authors = await Promise.all(promises);

  // Перевіряємо результати
  expect(authors).toHaveLength(4);
  expect(authors[0].id).toBe("1");
  expect(authors[2].id).toBe("1");

  // КРИТИЧНА ПЕРЕВІРКА: пакетна функція викликалася РІВНО ОДИН РАЗ
  expect(batchExecutionCount).toBe(1);
});
```

---

### 14. Метрики та вимірювання продуктивності

Порівняння поведінки системи під навантаженням (запит списку з 50 публікацій, де кожен пост має автора, категорію та 3 коментарі):

1. **Без DataLoader (Наївні резолвери):**
   - Кількість викликів до БД: `1 + 50 (автори) + 50 (категорії) + 50 (коментарі) + 150 (автори коментарів) = 301 запит`.
   - Затримка відповіді (p99): `420 мс`.
   - Використання пулу з'єднань: вичерпання пулу (Connection Pool Starvation) при 50 одночасних користувачах.
2. **З DataLoader:**
   - Кількість викликів до БД: `1 (пости) + 1 (автори) + 1 (категорії) + 1 (коментарі) + 1 (автори коментарів) = 5 запитів`.
   - Затримка відповіді (p99): `18 мс` (прискорення в 23 рази).
   - Використання пулу з'єднань: стабільна робота під навантаженням у тисячі одночасних клієнтів.

Впровадження DataLoader перетворює рекурсивне дерево резолверів із некерованого джерела водоспадних I/O-запитів на ефективний, передбачуваний конвеєр із мінімальними накладними витратами.

---

### 15. Пастки та підводні камені у виробничих системах

#### Пастка 1: Глобальний екземпляр DataLoader замість контекстного (Витік пам'яті та безпеки)

Найнебезпечніша помилка — створення одного глобального екземпляра DataLoader на весь процес сервера (Singleton):
- **Порушення ізоляції користувачів:** Якщо Користувач А завантажив сутність, до якої він мав доступ, Користувач Б отримає її з кешу лоадера в обхід перевірок прав доступу (Security Leak).
- **Нескінченний витік пам'яті:** `cacheMap` накопичуватиме всі прочитані сутності, доки процес Node.js або C++ не вичерпає всю оперативну пам'ять (Out of Memory).
- **Неактуальні дані (Stale Data):** Зміни, зроблені через мутації в базі даних, ніколи не з'являться у відповідях наступних запитів, оскільки лоадер віддаватиме застарілий результат із глобального кешу.

*Правило:* Екземпляр DataLoader живе строго в межах одного HTTP-запиту всередині об'єкта `context` і знищується збирачем сміття (або деструктором C++) після завершення формування відповіді клієнту.

#### Пастка 2: Порушення порядку або довжини повернутого масиву в пакетній функції

Реляційні бази даних (PostgreSQL, MySQL) за замовчуванням **не гарантують збереження порядку записів** при використанні оператора `IN (...)`:
```sql
SELECT * FROM users WHERE id IN ('3', '1', '2');
-- База може повернути рядки за порядком первинного індексу: ['1', '2', '3']
```
Якщо пакетна функція поверне масив без явного перевпорядкування, пост із автором `'3'` помилково отримає дані користувача `'1'`. Використання внутрішньої хеш-таблиці `Map` для зіставлення `id -> Entity` усередині пакетної функції є критично обов'язковим.

#### Пастка 3: Робота з мутаціями та інвалідація кешу (Prime / Clear)

Якщо в межах одного складного GraphQL-запиту виконується мутація та подальше читання (наприклад, зміна імені автора й повернення оновленої сутності), DataLoader може повернути старе ім'я з кешу, якщо читання відбулося до мутації.

Для запобігання цій ситуації резолвер мутації зобов'язаний явно оновити або скинути кеш лоадера:
```typescript
const resolvers = {
  Mutation: {
    updateUserName: async (_parent, { id, newName }, context) => {
      const updatedUser = await context.db.updateUser(id, { name: newName });
      
      // 1. Скидаємо старе значення з кешу
      context.loaders.userLoader.clear(id);
      
      // 2. Або записуємо оновлене значення наперед (prime)
      context.loaders.userLoader.prime(id, updatedUser);
      
      return updatedUser;
    }
  }
};
```

#### Пастка 4: Ліміт розміру пакетного запиту (Max Batch Size)

Більшість СУБД мають жорсткі обмеження на кількість параметрів в одному SQL-виразі (наприклад, SQLite обмежує кількість змінних до 999, а PostgreSQL має ліміт на розмір буфера параметрів). Якщо в стрічці запитується 5000 елементів, один неконтрольований батч призведе до збою драйвера бази даних.

Параметр `maxBatchSize: 1000` автоматично розбиває надвеликі черги на кілька послідовних пакетів фіксованого розміру, гарантуючи стабільність роботи бази даних при будь-яких обсягах вибірки.
