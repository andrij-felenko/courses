# 📋 Специфікація та контракти Remote Execution API (REAPI v2)

Протокол **Remote Execution API (REAPI v2)** — це відкритий індустріальний стандарт взаємодії між герметичними системами збірки (Bazel, Buck2, Pants, Reclient) та розподіленими кластерами віддаленого кешування й виконання дій (Buildbarn, BuildGrid, EngFlow, BuildBuddy). Протокол стандартизовано під егідою Linux Foundation та Google на базі технологій gRPC та Protocol Buffers (proto3).

Усі транзакції та структури даних у REAPI побудовані на парадигмі криптографічних дайджестів фіксованої довжини (SHA-256) та контентно-адресованого сховища (CAS).

## Архітектурні принципи протоколу

Специфікація REAPI спирається на чотири базові інженерні принципи:

1. **Контентна адресація (Content Addressing)**: будь-який об'єкт (сирцевий файл, скомпільований бінарник, метадані каталогу чи опис команди) ідентифікується виключно криптографічним гешем свого двійкового вмісту.
2. **Абстракція Merkle-дерев**: файлова структура робочого простору проєкту моделюється як ациклічний граф вузлів `Directory` та `FileNode`. Зміна одного байта в одному файлі змінює лише дайджести його батьківських каталогів, залишаючи решту графа незмінною.
3. **Розділення кешу результатів та сховища файлів**: індекс відповідності задач (`Action Cache`) та фактичне сховище бінарних блоків (`CAS`) розділені на незалежні gRPC-сервіси, що дозволяє масштабувати їх окремо.
4. **Легковажні клієнти (Remote Builds without the Bytes)**: клієнт не зобов'язаний завантажувати проміжні об'єктні файли `.o` на свій локальний диск; він оперує дайджестами, а проміжні результати залишаються всередині хмарного сховища CAS.

## Базові структури даних (Protobuf Schema)

Усі повідомлення протоколу використовують уніфіковані типи даних, визначені у пакеті `build.bazel.remote.execution.v2`.

### 1. Ідентифікатор вмісту: `Digest`

Структура `Digest` є універсальним покажчиком на будь-який бінарний фрагмент (блоб) у системі.

```protobuf
syntax = "proto3";
package build.bazel.remote.execution.v2;

message Digest {
  // Шістнадцятковий рядок SHA-256 гешу вмісту (рівно 64 символи в нижньому регістрі)
  string hash = 1;

  // Точний розмір бінарного навантаження у байтах
  int64 size_bytes = 2;
}
```

*Контрактні вимоги:*
- Поле `hash` зобов'язане містити валідний шістнадцятковий SHA-256 геш. Порожній файл завжди має геш `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` та `size_bytes = 0`.
- Поле `size_bytes` є обов'язковим. Воно дозволяє серверу заздалегідь перевіряти наявність вільного місця на диску та виділяти точні буфери в пам'яті до початку отримання байтів.

---

### 2. Опис виконання: `Action`

Повідомлення `Action` описує повну замкнену задачу компіляції чи тестування.

```protobuf
message Action {
  // Посилання на повідомлення Command у сховищі CAS
  Digest command_digest = 1;

  // Посилання на кореневе повідомлення Directory вхідного дерева файлів у CAS
  Digest input_root_digest = 2;

  // Максимальний час виконання команди на віддаленому воркері
  google.protobuf.Duration timeout = 6;

  // Чи заборонено зберігати результат в Action Cache (true для нестабільних тестів)
  bool do_not_cache = 7;

  // Платформні вимоги до ізольованого середовища виконання
  Platform platform = 8;
}
```

*Ключові поля та семантика:*
- `command_digest`: вказує на точну команду, прапорці компіляції та змінні середовища.
- `input_root_digest`: кореневий вузол Merkle-дерева, що містить усі необхідні для цієї дії файли сирців та заголовків.
- `platform`: словник властивостей цільового середовища (наприклад, `OSFamily=linux`, `ISA=x86_64`, `container-image=docker://...`). Планувальник кластера використовує ці властивості для вибору відповідного пулу воркерів з необхідною апаратною архітектурою чи версією ядра Linux.

---

### 3. Команда та оточення: `Command`

Повідомлення `Command` містить аргументи командного рядка та специфікацію очікуваних виходів.

```protobuf
message Command {
  // Вектор аргументів командного рядка (argv[0], argv[1], ...)
  repeated string arguments = 1;

  // Список очищених змінних середовища, відсортованих за назвою
  repeated EnvironmentVariable environment_variables = 2;

  // Шляхи очікуваних вихідних файлів відносно робочого каталогу
  repeated string output_files = 3;

  // Шляхи очікуваних вихідних каталогів
  repeated string output_directories = 4;

  // Робочий підкаталог для запуску (якщо порожній — корінь пісочниці)
  string working_directory = 5;

  message EnvironmentVariable {
    string name = 1;
    string value = 2;
  }
}
```

*Контрактні вимоги:*
- Список `environment_variables` повинен бути лексикографічно відсортований за полем `name`. Недотримання порядку змінює криптографічний геш повідомлення `Command` і призводить до промаху кешу.
- Списки `output_files` та `output_directories` вказують системі, які саме створені файли воркер зобов'язаний зберегти в CAS після завершення процесу. Будь-які інші файли, створені процесом під час роботи, безповоротно знищуються разом із пісочницею.

---

### 4. Структура вхідного дерева: `Directory` та `FileNode`

Файлова структура робочого каталогу транслюється у граф повідомлень `Directory`.

```protobuf
message Directory {
  // Список звичайних файлів у цьому каталозі (відсортований за name)
  repeated FileNode files = 1;

  // Список підкаталогів (відсортований за name)
  repeated DirectoryNode directories = 2;

  // Список символічних посилань
  repeated SymlinkNode symlinks = 3;
}

message FileNode {
  // Ім'я файлу всередині каталогу (без символу '/')
  string name = 1;

  // Посилання на бінарний вміст файлу в CAS
  Digest digest = 2;

  // Атрибут прав доступу (true відповідає прапорцю chmod +x)
  bool is_executable = 3;
}

message DirectoryNode {
  // Ім'я підкаталогу
  string name = 1;

  // Посилання на серіалізоване повідомлення Directory цього підкаталогу в CAS
  Digest digest = 2;
}

message SymlinkNode {
  string name = 1;
  string target = 2;
}
```

*Канонізація Merkle-дерева:*
Згідно зі специфікацією REAPI, масиви `files`, `directories` та `symlinks` усередині повідомлення `Directory` зобов'язані бути відсортовані за алфавітом за полем `name`. Це гарантує, що однаковий набір файлів на диску завжди генерує єдиний, наперед визначений `input_root_digest`.

---

### 5. Результат виконання: `ActionResult`

Після виконання дії воркер формує звіт про результати роботи процесу.

```protobuf
message ActionResult {
  // Список згенерованих вихідних файлів та їхніх дайджестів у CAS
  repeated OutputFile output_files = 2;

  // Список згенерованих вихідних каталогів
  repeated OutputDirectory output_directories = 3;

  // Код завершення процесу (0 відповідає успіху)
  int32 exit_code = 4;

  // Посилання на захоплений потік stdout у CAS
  Digest stdout_digest = 5;

  // Посилання на захоплений потік stderr у CAS
  Digest stderr_digest = 6;

  // Метрики виконання дії
  ExecutedActionMetadata execution_metadata = 7;
}

message OutputFile {
  string path = 1;
  Digest digest = 2;
  bool is_executable = 3;
}

message OutputDirectory {
  string path = 1;
  Digest tree_digest = 2;
}

message ExecutedActionMetadata {
  string worker = 1;
  google.protobuf.Timestamp queued_timestamp = 2;
  google.protobuf.Timestamp worker_start_timestamp = 3;
  google.protobuf.Timestamp worker_completed_timestamp = 4;
  google.protobuf.Timestamp input_fetch_completed_timestamp = 5;
  google.protobuf.Timestamp execution_completed_timestamp = 6;
  google.protobuf.Timestamp output_upload_completed_timestamp = 7;
}
```

---

## gRPC Сервіси REAPI

Протокол визначає чотири базові сервіси, які взаємодіють між клієнтом збірки та кластером.

```protobuf
// Сервіс виконання дій
service Execution {
  // Запуск виконання дії в асинхронному режимі з потоком статусів
  rpc Execute(ExecuteRequest) returns (stream google.longrunning.Operation);

  // Очікування завершення раніше запущеної тривалої операції
  rpc WaitExecution(WaitExecutionRequest) returns (stream google.longrunning.Operation);
}

// Сервіс кешування результатів (Action Cache)
service ActionCache {
  // Отримання готового результату за дайджестом дії
  rpc GetActionResult(GetActionResultRequest) returns (ActionResult);

  // Оновлення запису кешу
  rpc UpdateActionResult(UpdateActionResultRequest) returns (ActionResult);
}

// Контентно-адресоване сховище (CAS)
service ContentAddressableStorage {
  // Перевірка наявності списку дайджестів у сховищі
  rpc FindMissingBlobs(FindMissingBlobsRequest) returns (FindMissingBlobsResponse);

  // Пакетне завантаження невеликих блобів (до кількох мегабайтів)
  rpc BatchUpdateBlobs(BatchUpdateBlobsRequest) returns (BatchUpdateBlobsResponse);

  // Пакетне читання невеликих блобів
  rpc BatchReadBlobs(BatchReadBlobsRequest) returns (BatchReadBlobsResponse);

  // Отримання повного піддерева каталогів (Tree)
  rpc GetTree(GetTreeRequest) returns (stream GetTreeResponse);
}

// Потокове передавання великих файлів (Google ByteStream API)
service ByteStream {
  // Потокове читання блобу частинами (чанками)
  rpc Read(ReadRequest) returns (stream ReadResponse);

  // Потоковий запис блобу частинами
  rpc Write(stream WriteRequest) returns (WriteResponse);
}
```

## Стратегії передавання даних та політики розміру блобів

Під час передавання даних між клієнтом та CAS сховищем протокол застосовує два взаємодоповнюючі канали:
1. **Пакетний канал (`BatchUpdateBlobs` / `BatchReadBlobs`)**: оптимізований для великої кількості дрібних файлів (заголовки `.h`, невеликі сирці, серіалізовані вузли `Directory` та `Command`). Повідомлення упаковуються в один gRPC-запит, якщо їхній сумарний розмір не перевищує ліміт gRPC-фрейму (зазвичай 4 МБ).
2. **Потоковий канал (`ByteStream API`)**: використовується для важких бінарних блобів (великі бібліотеки `.a`, скомпільовані бінарники, образи компіляторів та sysroot-архіви). Дані передаються чанками фіксованого розміру (наприклад, по 64 КБ або 1 МБ) без завантаження всього файлу в оперативну пам'ять клієнта чи сервера.
3. **Стиснення трафіку**: сучасні сервери REAPI підтримують прозоре стиснення потоків за алгоритмами zstd або Snappy на рівні транспортного рівня gRPC, що додатково скорочує використання пропускної здатності корпоративної мережі на 60–80%.

## Життєвий цикл виконання дії та обробка помилок

Повна взаємодія між клієнтом та RBE-сервером проходить п'ять послідовних етапів:

```text
Клієнт (Bazel / Buck2)                                   RBE Кластер (AC / CAS / Worker)
      │                                                                  │
      │── 1. ActionCache.GetActionResult(ActionDigest) ─────────────────>│
      │<── 2. NOT_FOUND (Промах кешу) ───────────────────────────────────│
      │                                                                  │
      │── 3. CAS.FindMissingBlobs([InputDigest1, InputDigest2...]) ─────>│
      │<── 4. MissingBlobsResponse([InputDigest2]) ──────────────────────│
      │                                                                  │
      │── 5. ByteStream.Write(InputDigest2, payload) ───────────────────>│
      │<── 6. WriteResponse(committed_size) ─────────────────────────────│
      │                                                                  │
      │── 7. Execution.Execute(ActionDigest) ───────────────────────────>│
      │<── 8. stream Operation (stage: EXECUTING, worker: node-42) ──────│
      │<── 9. Operation.done = true, response = ActionResult ────────────│
      │                                                                  │
      │── 10. ByteStream.Read(OutputFileDigest) ────────────────────────>│
      │<── 11. Бінарний потік скомпільованого артефакту ─────────────────│
```

### Стандартні коди помилок gRPC у REAPI:

- **`NOT_FOUND`**:
  - При виклику `GetActionResult`: означає відсутність готового результату в кеші (Cache Miss). Клієнт переходить до фази завантаження входів та віддаленого виконання.
  - При виклику `Execute`: означає, що воркер під час створення пісочниці виявив відсутність одного з вхідних блобів у CAS (наприклад, видаленого збирачем сміття). Клієнт повторно завантажує відсутні блоби через `ByteStream` і перезапускає дію.
- **`RESOURCE_EXHAUSTED`**:
  Черга віддалених воркерів переповнена або вичерпано дискову квоту в CAS. Клієнт зобов'язаний застосувати експоненційну затримку повторних спроб (англ. *exponential backoff*).
- **`DEADLINE_EXCEEDED`**:
  Тривалість виконання дії перевищила ліміт, вказаний у полі `timeout` структури `Action`. Сервер примусово надсилає сигнал `SIGKILL` процесу у пісочниці та повертає помилку клієнту.
- **`UNAVAILABLE`**:
  Тимчасовий збій мережевого з'єднання або перезавантаження балансувальника навантаження. Клієнт автоматично повторює запит через інший доступний gRPC-канал.
- **`FAILED_PRECONDITION`**:
  Вказані у повідомленні `Platform` вимоги не підтримуються жодним пулом воркерів у кластері (наприклад, запит на збірку під macOS на суто Linux-кластері).
