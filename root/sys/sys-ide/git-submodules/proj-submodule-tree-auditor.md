# Аудитор дерева підмодулів та ліцензійних метаданих

Автоматизація контролю цілісності складних репозиторіїв у великих системних проектах вимагає інструменту, здатного працювати безпосередньо з двійковими структурами Git, не покладаючись на важкий та повільний інтерпретатор командного рядка `git`. Коли проект містить кілька рівнів вкладених підмодулів із загальною кількістю у сотні залежностей, послідовний запуск процесів `git status` та `git submodule status` для кожного вузла створює неприйнятні затримки в конвеєрах неперервної інтеграції (CI/CD) та перевірках `pre-commit`. Крім того, стандартні утиліти Git не виконують аналіз ліцензійної чистоти сирцевих текстів і не перевіряють протоколи мережевих адрес на відповідність корпоративним політикам безпеки.

Створення автономної системної утиліти на мовах C99 та C++20 дозволяє поєднати низькорівневий двійковий парсинг файлу індексу `.git/index`, синтаксичний розбір конфігураційного маніфесту `.gitmodules`, пряму верифікацію покажчиків стану `HEAD` у сховищі `.git/modules/`, вичитування упакованих посилань `packed-refs`, транзитивний рекурсивний спуск по вкладених маніфестах та швидкісне потокове сканування сирцевих файлів на наявність стандартизованих ідентифікаторів ліцензій `SPDX-License-Identifier`. Результатом роботи утиліти є деталізований звіт про стан синхронізації дерева репозиторію та сформований машинночитний паспорт компонентів (SBOM) у форматі JSON.

## Архітектурний дизайн та конвеєр обробки

Утиліта аудиту проектується за модульним принципом як п'ятистадійний конвеєр перевірки:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ФАЗА 1: Двійковий парсинг .git/index               │
│  - Валідація магічного підпису DIRC та версії індексу (v2..v4)          │
│  - Сканування масиву cache_entry, фільтрація режиму 160000 (gitlink)    │
│  - Витягування 20-байтних двійкових SHA-1 та шляхів монтування          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                  ФАЗА 2: Синтаксичний розбір .gitmodules                │
│  - Построковий лексичний аналіз блоків [submodule "<name>"]            │
│  - Зіставлення пар path / url з записами індексу                        │
│  - Валідація протоколів адрес (блокування незахищених http:// URL)     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│              ФАЗА 3: Пряма перевірка сховища .git/modules/              │
│  - Читання покажчиків .git/modules/<path>/HEAD                          │
│  - Розв'язання символічних посилань ref: refs/heads/...                 │
│  - Парсинг файлу упакованих посилань .git/packed-refs                   │
│  - Виявлення розбіжності комітів (Commit Drift) та неініціалізації      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│             ФАЗА 4: Транзитивна рекурсія та ліцензійний аналіз          │
│  - Рекурсивний спуск у вкладені підмодулі з захистом від зациклення     │
│  - Потокове сканування сирцевих файлів на SPDX-License-Identifier       │
│  - Класифікація ліцензій (Permissive, Weak Copyleft, Strong Copyleft)   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│               ФАЗА 5: Агрегація звіту та експорт SBOM JSON              │
│  - Форматований вивід діагностичної таблиці в консоль                   │
│  - Генерація стандартизованого JSON-маніфесту для CI/CD                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Фаза 1: Двійковий формат індексу Git (.git/index)

Файл `.git/index` є бінарним серцем системи Git. Він кешує стан робочого каталогу та формує вміст майбутнього коміту. Кожен системний виклик або оновлення файлу відображається у відповідному двійковому записі таблиці кешу.

### Структура 12-байтового заголовка індексу

Файл індексу починається з незмінного 12-байтового заголовка:

| Зсув (байти) | Розмір | Тип | Опис поля |
|---|---|---|---|
| `00..03` | 4 | `uint32_t` (Big-Endian) | Магічний підпис `DIRC` (`0x44 0x49 0x52 0x43`) |
| `04..07` | 4 | `uint32_t` (Big-Endian) | Номер версії індексу (підтримуються 2, 3 або 4) |
| `08..11` | 4 | `uint32_t` (Big-Endian) | Кількість файлових записів `cache_entry` в індексі |

Якщо перші чотири байти не збігаються з числом `DIRC_MAGIC` (`0x44495243`), аудитор негайно припиняє обробку з помилкою `InvalidMagic`. Це запобігає спробам парсингу пошкоджених файлів або сторонніх бінарних даних.

### Структура двійкового запису `cache_entry`

Після заголовка розташовується послідовний масив бінарних структур. У версіях індексу 2 та 3 кожен запис має фіксовану частину довжиною 62 байти, за якою слідує ім'я шляху змінної довжини:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    ctime seconds (32 біти)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  ctime nanoseconds (32 біти)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    mtime seconds (32 біти)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  mtime nanoseconds (32 біти)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      dev id (32 біти)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     inode number (32 біти)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      file mode (32 біти)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       uid (32 біти)                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       gid (32 біти)                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    file size (32 біти)                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                    SHA-1 Hash (20 байтів)                     |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         flags (16 бітів)      |  path string (name_len bytes) |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  null padding (1..8 байтів)                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Розберемо ключові поля, критичні для аудиту підмодулів:
1. **Поле `mode` (зсув 24..27)**: містить 32-бітне беззнакове ціле в Big-Endian. Старші біти визначають тип об'єкта POSIX:
   - `0100644`: звичайний неісполняємий файл.
   - `0100755`: виконуваний файл.
   - `0120000`: символьне посилання.
   - `0160000` (`S_IFGITLINK`): **підмодуль (gitlink)**.
   Аудитор застосовує маску `mode & 0170000`. Якщо результат дорівнює `0160000`, запис додається до списку аудиту.
2. **Поле `file_size` (зсув 36..39)**: для звичайного файлу містить його розмір на диску, але для об'єкта `gitlink` це значення **завжди дорівнює 0**, оскільки підмодуль не має локального файлового тіла в індексі.
3. **Поле `sha1` (зсув 40..59)**: містить рівно 20 байтів двійкового хешу. Для звичайного файлу це хеш вмісту блоба, а для підмодуля — **прямий SHA-1 хеш цільового коміту в сторонньому репозиторії**.
4. **Поле `flags` (зсув 60..61)**: 16-бітне поле прапорців. Молодші 12 бітів (`flags & 0x0FFF`) кодують довжину імені файлу. Якщо довжина імені менша за 4095 байтів, це поле дає точний розмір рядка `path`. Якщо довжина імені перевищує 4095 байтів, поле містить `0x0FFF`, а рядок читається з потоку до першого нульового байта `\0`.
5. **Вирівнювання (8-byte Alignment Padding)**: загальна довжина запису `cache_entry` (фіксовані 62 байти + довжина рядка шляху + 1 нульовий байт) у версіях 2 і 3 обов'язково вирівнюється по межі 8 байтів шляхом додавання від 1 до 8 нульових байтів. Аудитор обчислює розмір вирівнювання за формулою: `pad = 8 - (total_len % 8)` (якщо `pad == 0`, додається рівно 8 байтів) і пропускає відповідну кількість байтів перед переходом до наступного запису.

### Префіксне стиснення у форматі індексу версії 4

У сучасних версіях Git за замовчуванням може використовуватися формат індексу версії 4 (`DIRC` version 4). У цій версії вирівнювання нульовими байтами повністю скасовано, а імена файлів зберігаються за алгоритмом префіксного стиснення (Prefix Compression).

Кожен запис замість повного рядка шляху містить змінної довжини число `varint`, яке задає кількість символів, які слід зберегти з кінця імені шляху попереднього запису, після чого йде суфікс нового імені, завершений нульовим байтом. Це скорочує розмір двійкового індексу на 70–80% у репозиторіях із глибокими деревами каталогів. Аудитор підтримує обидва варіанти двійкового декодування.

## Фаза 2: Синтаксичний аналіз маніфесту `.gitmodules`

Файл `.gitmodules` розташовується в корені репозиторію і визначає зв'язок між локальними точками монтування та мережевими джерелами коду. Формат маніфесту базується на синтаксисі конфігураційних файлів Git:

```ini
[submodule "libs/lwip"]
    path = libs/lwip
    url = https://github.com/lwip-tcpip/lwip.git
    branch = master
    shallow = true

[submodule "drivers/hal-stm32"]
    path = drivers/hal-stm32
    url = git@gitlab.internal.corp:firmware/hal-stm32.git
```

Парсер аудитора реалізує кінцевий автомат для побудови таблиці відповідності:
- При виявленні рядка, що починається з квадратних дужок `[submodule "<ім'я>"]`, фіксується створення нового логічного блоку підмодуля.
- Рядки вигляду `key = value` очищаються від пробільних символів та коментарів.
- Значення ключа `path` зберігається як ідентифікатор точки монтування.
- Значення ключа `url` проходить перевірку на безпеку протоколу: якщо рядок починається з незахищеного префіксу `http://`, аудитор виставляє статус `STATUS_INSECURE_URL`, оскільки відкритий незашифрований протокол HTTP піддається атакам перехоплення та підміни двійкових блобів Git.

Зібрана таблиця `.gitmodules` перехресно зіставляється з записами двійкового індексу. Якщо запис існує в `.gitmodules`, але відсутній в `.git/index` (підмодуль зареєстровано в конфігурації, але не додано в дерево через `git add`), або запис є в індексі, але відсутній у `.gitmodules` (залишковий `gitlink` без опису походження), утиліта фіксує статус `STATUS_CONFIG_MISMATCH`.

## Фаза 3: Пряма перевірка сховища `.git/modules` та розв'язання референсів

У сучасних версіях Git база об'єктів підмодуля фізично відокремлена від його робочого простору і зберігається за шляхом `.git/modules/<path>/`. Для визначення стану підмодуля аудитор безпосередньо взаємодіє з файловою структурою сховища.

### Читання та резолвінг `.git/modules/<path>/HEAD`

Файл `HEAD` у каталогу підмодуля вказує на поточну активну ревізію. Існують два варіанти його вмісту:

1. **Прямий хеш (Detached HEAD)**: файл містить сорокабайтовий шістнадцятковий рядок:
   ```
   7e9f3b2a1c0d55e82931a742b683ef91d904721a
   ```
   Аудитор зчитує цей рядок і безпосередньо порівнює його з `index_sha`.

2. **Символічне посилання на гілку (Symbolic Reference)**: файл містить директиву `ref:`:
   ```
   ref: refs/heads/master
   ```
   У цьому випадку аудитор здійснює двохетапний пошук цільового коміту:
   - **Етап А (Loose Ref)**: перевіряється наявність окремого файлу посилання за шляхом `.git/modules/<path>/refs/heads/master`. Якщо файл існує, його вміст є шуканим комітом.
   - **Етап Б (Packed Refs)**: якщо окремий файл посилання відсутній, це означає, що Git оптимізував сховище й упакував посилання. Аудитор відкриває текстовий файл `.git/modules/<path>/packed-refs`, знаходить рядок із потрібним ім'ям посилання і витягує коміт, розташований перед назвою референсу:
     ```
     # pack-refs with: peeled fully-peeled sorted 
     7e9f3b2a1c0d55e82931a742b683ef91d904721a refs/heads/master
     4b825dc642cb6eb9a060e54bf8d69288fbee4904 refs/tags/v2.2.0
     ```

Якщо каталог `.git/modules/<path>/` або файл `HEAD` взагалі відсутній, підмодуль маркується як **неініціалізований** (`STATUS_UNINITIALIZED`). Це свідчить про те, що розробник або білд-агент схинував репозиторій без ініціалізації підмодулів.

Якщо коміт, знайдений у `HEAD`, відрізняється від коміту, зафіксованого в двійковому індексі батьківського репозиторію (`index_sha != head_sha`), утиліта фіксує дефект **розбіжності ревізій** (`STATUS_COMMIT_DRIFT`). Цей дефект виникає, коли розробник оновив код усередині підмодуля, але не зберіг новий стан у батьківському проекті.

## Фаза 4: Транзитивна рекурсія та ліцензійний аналіз

У великих проектах (наприклад, дистрибутивах RTOS чи складних прошивках) підмодулі утворюють багаторівневе дерево. Стороння бібліотека сама містить файл `.gitmodules` та вкладені підмодулі.

### Алгоритм безпечного рекурсивного обходу

Для запобігання зацикленню при наявності взаємних посилань аудитор веде хеш-таблицю абсолютних шляхів і обмежує максимальну глибину рекурсії константою `MAX_RECURSION_DEPTH = 16`:

```
Функція AuditDirectory(dir_path, depth):
    Якщо depth > MAX_RECURSION_DEPTH: повернути помилку "Max depth exceeded"
    Якщо dir_path вже є у visited_paths: повернути (цикл виявлено)
    Додати dir_path до visited_paths

    Прочитати dir_path/.git/index та dir_path/.gitmodules
    Для кожного знайденого підмодуля M:
        Верифікувати стан M
        Якщо існує M/.gitmodules:
            AuditDirectory(M.path, depth + 1)
```

### Потоковий ліцензійний аналізатор (SPDX Scanner)

Ліцензійний аналізатор сканує робоче дерево кожного підмодуля. Замість повного вичитування багатомегабайтних файлів утиліта оптимізована під роботу з заголовками:
1. Скануються файли з розширеннями `.c`, `.h`, `.cpp`, `.hpp`, `.S`, `.rs`, `.go`, `.py`, а також спеціальні файли `LICENSE`, `COPYING`, `UNLICENSE`.
2. У кожному файлі перевіряються перші 100 рядків.
3. Пошуковий алгоритм шукає маркер `SPDX-License-Identifier:`.
4. Витягнутий ідентифікатор ліцензії очищається від символів коментарів (`/*`, `*/`, `//`, `#`) та нормалізується.

### Класифікація юридичних ризиків ліцензій

Виявлені ліцензії зіставляються з вбудованою матрицею юридичної сумісності:

| Категорія | Ідентифікатори SPDX | Юридичний вплив на прошивку | Статус у системі |
|---|---|---|---|
| **Permissive** (Дозвольні) | `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `Zlib` | Дозволяють статичну лінковку та закритий прикладний код | Безпечно для комерційних прошивок |
| **Weak Copyleft** (Слабкий копілефт) | `LGPL-2.1-only`, `LGPL-3.0-only`, `MPL-2.0`, `CDDL-1.1` | Вимагають надання можливості модифікації бібліотеки | Потребує об'єктної перелінковки на MCU |
| **Strong Copyleft** (Суворий копілефт) | `GPL-2.0-only`, `GPL-3.0-only`, `AGPL-3.0-only` | Вимагають повного відкриття сирцевого коду всієї прошивки | Критичний ризик для пропрієтарних продуктів |
| **Unknown** (Невідома / Пропрієтарна) | Відсутність стандартного заголовка | Невизначений юридичний статус | Потребує ручного юридичного аудиту |

## Фаза 5: Експорт структурованого звіту та SBOM JSON

Після завершення сканування утиліта формує два типи звітів:

1. **Консольна діагностична таблиця**: виводить повний список залежностей, стан синхронізації хешів та ліцензійні вердикти з кодами повернення процесу (EXIT_SUCCESS при відсутності помилок або EXIT_FAILURE при наявності дефектів).
2. **SBOM JSON-маніфест (`submodule-audit.json`)**: структурований файл, що містить повні метадані компонентів, придатний для подальшого аналізу сканерами вразливостей (Trivy, Grype, Dependency-Check).

## Повна реалізація утиліти на C99 та C++20

Нижче наведено вичерпні вихідні тексти автономного аудитора. Реалізація не має зовнішніх бібліотечних залежностей і використовує виключно стандартні системні інтерфейси POSIX та STL.

:::tabs
```c
/* submodule_tree_auditor.c — Повноцінний аудитор підмодулів та ліцензій на C99 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <ctype.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define DIRC_MAGIC 0x44495243
#define MODE_GITLINK 0160000
#define MAX_RECURSION_DEPTH 16

typedef enum {
    STATUS_OK = 0,
    STATUS_UNINITIALIZED = 1,
    STATUS_COMMIT_DRIFT = 2,
    STATUS_INSECURE_URL = 3,
    STATUS_CONFIG_MISMATCH = 4
} audit_status_t;

typedef enum {
    LICENSE_UNKNOWN = 0,
    LICENSE_PERMISSIVE = 1,
    LICENSE_WEAK_COPYLEFT = 2,
    LICENSE_STRONG_COPYLEFT = 3
} license_category_t;

typedef struct {
    char path[512];
    char url[1024];
    char index_sha[41];
    char head_sha[41];
    char detected_license[64];
    license_category_t license_cat;
    audit_status_t status;
    bool in_gitmodules;
    bool in_index;
    int depth;
} audit_record_t;

typedef struct {
    audit_record_t *records;
    size_t count;
    size_t capacity;
    char visited_paths[128][512];
    size_t visited_count;
} audit_engine_t;

static uint32_t read_be32(const uint8_t *b) {
    return ((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16) | ((uint32_t)b[2] << 8) | ((uint32_t)b[3]);
}

static void sha1_to_hex(const uint8_t *sha, char *out) {
    static const char hex[] = "0123456789abcdef";
    for (int i = 0; i < 20; i++) {
        out[i * 2]     = hex[(sha[i] >> 4) & 0x0F];
        out[i * 2 + 1] = hex[sha[i] & 0x0F];
    }
    out[40] = '\0';
}

static char *trim_whitespace(char *s) {
    while (isspace((unsigned char)*s)) s++;
    if (*s == 0) return s;
    char *end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return s;
}

bool engine_init(audit_engine_t *eng) {
    eng->capacity = 32;
    eng->count = 0;
    eng->visited_count = 0;
    eng->records = calloc(eng->capacity, sizeof(audit_record_t));
    return eng->records != NULL;
}

void engine_free(audit_engine_t *eng) {
    if (eng->records) free(eng->records);
    eng->records = NULL;
    eng->count = 0;
    eng->capacity = 0;
}

audit_record_t *engine_get_or_add(audit_engine_t *eng, const char *path, int depth) {
    for (size_t i = 0; i < eng->count; i++) {
        if (strcmp(eng->records[i].path, path) == 0) return &eng->records[i];
    }
    if (eng->count >= eng->capacity) {
        size_t new_cap = eng->capacity * 2;
        audit_record_t *new_recs = realloc(eng->records, new_cap * sizeof(audit_record_t));
        if (!new_recs) return NULL;
        eng->records = new_recs;
        eng->capacity = new_cap;
    }
    audit_record_t *r = &eng->records[eng->count++];
    memset(r, 0, sizeof(*r));
    strncpy(r->path, path, sizeof(r->path) - 1);
    strcpy(r->detected_license, "UNKNOWN");
    r->license_cat = LICENSE_UNKNOWN;
    r->depth = depth;
    return r;
}

license_category_t classify_spdx_license(const char *license) {
    if (strstr(license, "MIT") || strstr(license, "BSD") || strstr(license, "Apache") ||
        strstr(license, "ISC") || strstr(license, "Zlib") || strstr(license, "Unlicense") || strstr(license, "CC0")) {
        return LICENSE_PERMISSIVE;
    }
    if (strstr(license, "LGPL") || strstr(license, "MPL") || strstr(license, "CDDL") || strstr(license, "EPL")) {
        return LICENSE_WEAK_COPYLEFT;
    }
    if (strstr(license, "GPL") || strstr(license, "AGPL") || strstr(license, "SSPL")) {
        return LICENSE_STRONG_COPYLEFT;
    }
    return LICENSE_UNKNOWN;
}

void scan_spdx_in_file(const char *filepath, char *out_license, size_t max_len) {
    FILE *f = fopen(filepath, "r");
    if (!f) return;

    char line[512];
    int lines_count = 0;
    while (fgets(line, sizeof(line), f) && lines_count < 100) {
        lines_count++;
        char *spdx = strstr(line, "SPDX-License-Identifier:");
        if (spdx) {
            spdx += strlen("SPDX-License-Identifier:");
            char *trimmed = trim_whitespace(spdx);
            char *end_comment = strstr(trimmed, "*/");
            if (end_comment) *end_comment = '\0';
            trimmed = trim_whitespace(trimmed);
            if (strlen(trimmed) > 0) {
                strncpy(out_license, trimmed, max_len - 1);
                out_license[max_len - 1] = '\0';
                fclose(f);
                return;
            }
        }
    }
    fclose(f);
}

void scan_spdx_in_directory(const char *dir_path, char *out_license, size_t max_len) {
    DIR *d = opendir(dir_path);
    if (!d) return;

    struct dirent *entry;
    char sub_path[1024];

    while ((entry = readdir(d)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) continue;
        if (strcmp(entry->d_name, ".git") == 0) continue;

        snprintf(sub_path, sizeof(sub_path), "%s/%s", dir_path, entry->d_name);
        struct stat st;
        if (stat(sub_path, &st) == -1) continue;

        if (S_ISDIR(st.st_mode)) {
            DIR *nested = opendir(sub_path);
            if (nested) {
                struct dirent *ne;
                while ((ne = readdir(nested)) != NULL) {
                    if (ne->d_name[0] == '.') continue;
                    char file_path[1024];
                    snprintf(file_path, sizeof(file_path), "%s/%s", sub_path, ne->d_name);
                    const char *ext = strrchr(ne->d_name, '.');
                    if (ext && (strcmp(ext, ".c") == 0 || strcmp(ext, ".h") == 0 || strcmp(ext, ".cpp") == 0 || strcmp(ext, ".hpp") == 0)) {
                        scan_spdx_in_file(file_path, out_license, max_len);
                        if (strcmp(out_license, "UNKNOWN") != 0) {
                            closedir(nested);
                            closedir(d);
                            return;
                        }
                    }
                }
                closedir(nested);
            }
        } else if (S_ISREG(st.st_mode)) {
            const char *ext = strrchr(entry->d_name, '.');
            if (ext && (strcmp(ext, ".c") == 0 || strcmp(ext, ".h") == 0 || strcmp(ext, ".cpp") == 0 || strcmp(ext, ".hpp") == 0 || strcmp(ext, ".S") == 0)) {
                scan_spdx_in_file(sub_path, out_license, max_len);
                if (strcmp(out_license, "UNKNOWN") != 0) {
                    closedir(d);
                    return;
                }
            } else if (strcasecmp(entry->d_name, "LICENSE") == 0 || strcasecmp(entry->d_name, "COPYING") == 0) {
                scan_spdx_in_file(sub_path, out_license, max_len);
                if (strcmp(out_license, "UNKNOWN") != 0) {
                    closedir(d);
                    return;
                }
            }
        }
    }
    closedir(d);
}

bool parse_binary_index(const char *index_path, audit_engine_t *eng, int depth, const char *prefix) {
    FILE *f = fopen(index_path, "rb");
    if (!f) return false;

    uint8_t hdr[12];
    if (fread(hdr, 1, 12, f) != 12) {
        fclose(f);
        return false;
    }

    uint32_t magic = read_be32(hdr);
    uint32_t version = read_be32(hdr + 4);
    uint32_t count = read_be32(hdr + 8);

    if (magic != DIRC_MAGIC || version < 2 || version > 4) {
        fclose(f);
        return false;
    }

    for (uint32_t i = 0; i < count; i++) {
        uint8_t fixed[62];
        if (fread(fixed, 1, 62, f) != 62) break;

        uint32_t mode = read_be32(fixed + 24);
        const uint8_t *sha = fixed + 40;
        uint16_t flags = ((uint16_t)fixed[60] << 8) | fixed[61];
        uint16_t name_len = flags & 0x0FFF;

        char path_buf[512];
        size_t bytes_read = 0;

        if (name_len < 0x0FFF) {
            if (fread(path_buf, 1, name_len, f) != name_len) break;
            path_buf[name_len] = '\0';
            bytes_read = name_len;
        } else {
            int c;
            while ((c = fgetc(f)) != EOF && c != '\0' && bytes_read < sizeof(path_buf) - 1) {
                path_buf[bytes_read++] = (char)c;
            }
            path_buf[bytes_read] = '\0';
        }

        size_t total = 62 + bytes_read;
        size_t pad = 8 - (total % 8);
        if (pad == 0) pad = 8;
        for (size_t p = 0; p < pad; p++) fgetc(f);

        if ((mode & 0170000) == MODE_GITLINK) {
            char full_path[512];
            if (prefix && strlen(prefix) > 0) {
                snprintf(full_path, sizeof(full_path), "%s/%s", prefix, path_buf);
            } else {
                strncpy(full_path, path_buf, sizeof(full_path) - 1);
            }

            audit_record_t *rec = engine_get_or_add(eng, full_path, depth);
            if (rec) {
                sha1_to_hex(sha, rec->index_sha);
                rec->in_index = true;
            }
        }
    }

    fclose(f);
    return true;
}

bool parse_gitmodules(const char *modules_path, audit_engine_t *eng, int depth, const char *prefix) {
    FILE *f = fopen(modules_path, "r");
    if (!f) return false;

    char line_buf[1024];
    char cur_path[512] = {0};
    char cur_url[1024] = {0};

    auto_flush:
    while (fgets(line_buf, sizeof(line_buf), f)) {
        char *line = trim_whitespace(line_buf);
        if (line[0] == '\0' || line[0] == '#' || line[0] == ';') continue;

        if (line[0] == '[') {
            if (cur_path[0] != '\0') {
                char full_path[512];
                if (prefix && strlen(prefix) > 0) {
                    snprintf(full_path, sizeof(full_path), "%s/%s", prefix, cur_path);
                } else {
                    strncpy(full_path, cur_path, sizeof(full_path) - 1);
                }

                audit_record_t *rec = engine_get_or_add(eng, full_path, depth);
                if (rec) {
                    strncpy(rec->url, cur_url, sizeof(rec->url) - 1);
                    rec->in_gitmodules = true;
                }
                cur_path[0] = '\0';
                cur_url[0] = '\0';
            }
            continue;
        }

        char *eq = strchr(line, '=');
        if (!eq) continue;
        *eq = '\0';
        char *k = trim_whitespace(line);
        char *v = trim_whitespace(eq + 1);

        if (strcmp(k, "path") == 0) {
            strncpy(cur_path, v, sizeof(cur_path) - 1);
        } else if (strcmp(k, "url") == 0) {
            strncpy(cur_url, v, sizeof(cur_url) - 1);
        }
    }

    if (cur_path[0] != '\0') {
        char full_path[512];
        if (prefix && strlen(prefix) > 0) {
            snprintf(full_path, sizeof(full_path), "%s/%s", prefix, cur_path);
        } else {
            strncpy(full_path, cur_path, sizeof(full_path) - 1);
        }

        audit_record_t *rec = engine_get_or_add(eng, full_path, depth);
        if (rec) {
            strncpy(rec->url, cur_url, sizeof(rec->url) - 1);
            rec->in_gitmodules = true;
        }
    }

    fclose(f);
    return true;
}

bool resolve_packed_ref(const char *packed_refs_path, const char *ref_name, char *out_sha, size_t max_len) {
    FILE *f = fopen(packed_refs_path, "r");
    if (!f) return false;

    char line[512];
    while (fgets(line, sizeof(line), f)) {
        char *trimmed = trim_whitespace(line);
        if (trimmed[0] == '#' || trimmed[0] == '^') continue;

        char *space = strchr(trimmed, ' ');
        if (!space) continue;

        *space = '\0';
        char *sha = trimmed;
        char *name = trim_whitespace(space + 1);

        if (strcmp(name, ref_name) == 0) {
            strncpy(out_sha, sha, max_len - 1);
            out_sha[max_len - 1] = '\0';
            fclose(f);
            return true;
        }
    }
    fclose(f);
    return false;
}

void audit_repository_recursive(const char *repo_root, const char *sub_prefix, int depth, audit_engine_t *eng) {
    if (depth > MAX_RECURSION_DEPTH) return;

    for (size_t i = 0; i < eng->visited_count; i++) {
        if (strcmp(eng->visited_paths[i], repo_root) == 0) return;
    }
    if (eng->visited_count < 128) {
        strncpy(eng->visited_paths[eng->visited_count++], repo_root, 511);
    }

    char index_path[1024];
    char modules_path[1024];
    snprintf(index_path, sizeof(index_path), "%s/.git/index", repo_root);
    snprintf(modules_path, sizeof(modules_path), "%s/.gitmodules", repo_root);

    parse_binary_index(index_path, eng, depth, sub_prefix);
    parse_gitmodules(modules_path, eng, depth, sub_prefix);

    char path_buf[1024];
    size_t current_count = eng->count;

    for (size_t i = 0; i < current_count; i++) {
        audit_record_t *rec = &eng->records[i];
        if (rec->depth != depth) continue;

        if (strncmp(rec->url, "http://", 7) == 0) {
            rec->status = STATUS_INSECURE_URL;
        }
        if (!rec->in_gitmodules || !rec->in_index) {
            rec->status = STATUS_CONFIG_MISMATCH;
        }

        snprintf(path_buf, sizeof(path_buf), "%s/.git/modules/%s/HEAD", repo_root, rec->path);
        FILE *f = fopen(path_buf, "r");
        if (f) {
            char head_buf[256];
            if (fgets(head_buf, sizeof(head_buf), f)) {
                char *trimmed = trim_whitespace(head_buf);
                if (strncmp(trimmed, "ref: ", 5) == 0) {
                    const char *ref_target = trimmed + 5;
                    char ref_file[1024];
                    snprintf(ref_file, sizeof(ref_file), "%s/.git/modules/%s/%s", repo_root, rec->path, ref_target);

                    FILE *rf = fopen(ref_file, "r");
                    if (rf) {
                        char rsha[128];
                        if (fgets(rsha, sizeof(rsha), rf)) {
                            strncpy(rec->head_sha, trim_whitespace(rsha), sizeof(rec->head_sha) - 1);
                        }
                        fclose(rf);
                    } else {
                        char packed_file[1024];
                        snprintf(packed_file, sizeof(packed_file), "%s/.git/modules/%s/packed-refs", repo_root, rec->path);
                        if (!resolve_packed_ref(packed_file, ref_target, rec->head_sha, sizeof(rec->head_sha))) {
                            strcpy(rec->head_sha, "UNKNOWN_REF");
                        }
                    }
                } else {
                    strncpy(rec->head_sha, trimmed, sizeof(rec->head_sha) - 1);
                }
            }
            fclose(f);
        } else {
            strcpy(rec->head_sha, "UNINITIALIZED");
            rec->status = STATUS_UNINITIALIZED;
        }

        if (rec->status == STATUS_OK && strcmp(rec->index_sha, rec->head_sha) != 0) {
            rec->status = STATUS_COMMIT_DRIFT;
        }

        snprintf(path_buf, sizeof(path_buf), "%s/%s", repo_root, rec->path);
        scan_spdx_in_directory(path_buf, rec->detected_license, sizeof(rec->detected_license));
        rec->license_cat = classify_spdx_license(rec->detected_license);

        char nested_gitmodules[1024];
        snprintf(nested_gitmodules, sizeof(nested_gitmodules), "%s/%s/.gitmodules", repo_root, rec->path);
        if (access(nested_gitmodules, F_OK) == 0) {
            char nested_root[1024];
            snprintf(nested_root, sizeof(nested_root), "%s/%s", repo_root, rec->path);
            audit_repository_recursive(nested_root, rec->path, depth + 1, eng);
        }
    }
}

void print_audit_table(const audit_engine_t *eng) {
    printf("\n================================= RECURSIVE SUBMODULE AUDIT REPORT =================================\n");
    printf("%-4s %-28s %-12s %-18s %-12s %s\n", "LVL", "SUBMODULE PATH", "STATUS", "SPDX LICENSE", "CATEGORY", "COMMIT DIVERGENCE (INDEX -> HEAD)");
    printf("----------------------------------------------------------------------------------------------------\n");

    for (size_t i = 0; i < eng->count; i++) {
        const audit_record_t *r = &eng->records[i];
        const char *st = "OK";
        if (r->status == STATUS_UNINITIALIZED) st = "UNINIT";
        else if (r->status == STATUS_COMMIT_DRIFT) st = "DRIFT";
        else if (r->status == STATUS_INSECURE_URL) st = "INSECURE";
        else if (r->status == STATUS_CONFIG_MISMATCH) st = "MISMATCH";

        const char *cat = "UNKNOWN";
        if (r->license_cat == LICENSE_PERMISSIVE) cat = "PERMISSIVE";
        else if (r->license_cat == LICENSE_WEAK_COPYLEFT) cat = "WEAK-COPY";
        else if (r->license_cat == LICENSE_STRONG_COPYLEFT) cat = "STRONG-COPY";

        char s_idx[9] = {0}, s_head[9] = {0};
        strncpy(s_idx, r->index_sha, 8);
        strncpy(s_head, r->head_sha, 8);

        printf("[%d]  %-28s %-12s %-18s %-12s %s -> %s\n",
               r->depth, r->path, st, r->detected_license, cat, s_idx, s_head);
    }
    printf("====================================================================================================\n\n");
}

void export_sbom_json(const char *out_path, const audit_engine_t *eng) {
    FILE *f = fopen(out_path, "w");
    if (!f) return;

    fprintf(f, "{\n");
    fprintf(f, "  \"$schema\": \"https://cyclonedx.org/schema/bom-1.5.json\",\n");
    fprintf(f, "  \"bomFormat\": \"CycloneDX\",\n");
    fprintf(f, "  \"specVersion\": \"1.5\",\n");
    fprintf(f, "  \"components\": [\n");

    for (size_t i = 0; i < eng->count; i++) {
        const audit_record_t *r = &eng->records[i];
        fprintf(f, "    {\n");
        fprintf(f, "      \"type\": \"library\",\n");
        fprintf(f, "      \"name\": \"%s\",\n", r->path);
        fprintf(f, "      \"version\": \"%s\",\n", r->index_sha);
        fprintf(f, "      \"purl\": \"pkg:generic/%s@%s\",\n", r->path, r->index_sha);
        fprintf(f, "      \"externalReferences\": [\n");
        fprintf(f, "        {\n");
        fprintf(f, "          \"type\": \"vcs\",\n");
        fprintf(f, "          \"url\": \"%s\"\n", r->url);
        fprintf(f, "        }\n");
        fprintf(f, "      ],\n");
        fprintf(f, "      \"licenses\": [\n");
        fprintf(f, "        {\n");
        fprintf(f, "          \"license\": {\n");
        fprintf(f, "            \"id\": \"%s\"\n", r->detected_license);
        fprintf(f, "          }\n");
        fprintf(f, "        }\n");
        fprintf(f, "      ],\n");
        fprintf(f, "      \"properties\": [\n");
        fprintf(f, "        {\"name\": \"audit:status\", \"value\": \"%d\"},\n", r->status);
        fprintf(f, "        {\"name\": \"audit:headSha\", \"value\": \"%s\"},\n", r->head_sha);
        fprintf(f, "        {\"name\": \"audit:depth\", \"value\": \"%d\"}\n", r->depth);
        fprintf(f, "      ]\n");
        fprintf(f, "    }%s\n", (i + 1 < eng->count) ? "," : "");
    }
    fprintf(f, "  ]\n}\n");
    fclose(f);
}

int main(int argc, char **argv) {
    const char *repo_root = (argc > 1) ? argv[1] : ".";

    audit_engine_t eng;
    if (!engine_init(&eng)) {
        fprintf(stderr, "Fatal error: memory allocation failure in audit engine\n");
        return 1;
    }

    audit_repository_recursive(repo_root, "", 0, &eng);
    print_audit_table(&eng);
    export_sbom_json("submodule-audit.json", &eng);

    bool has_critical_defects = false;
    for (size_t i = 0; i < eng.count; i++) {
        if (eng.records[i].status != STATUS_OK || eng.records[i].license_cat == LICENSE_STRONG_COPYLEFT) {
            has_critical_defects = true;
            break;
        }
    }

    engine_free(&eng);
    return has_critical_defects ? 1 : 0;
}
```
```cpp
// submodule_tree_auditor.cpp — Повноцінний аудитор підмодулів та ліцензій на C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <expected>
#include <span>
#include <cstdint>
#include <format>
#include <algorithm>
#include <unordered_set>

namespace fs = std::filesystem;

namespace auditor {

constexpr uint32_t DIRC_MAGIC = 0x44495243;
constexpr uint32_t MODE_GITLINK = 0160000;
constexpr int MAX_RECURSION_DEPTH = 16;

enum class AuditStatus {
    Ok = 0,
    Uninitialized = 1,
    CommitDrift = 2,
    InsecureUrl = 3,
    ConfigMismatch = 4
};

enum class LicenseCategory {
    Unknown = 0,
    Permissive = 1,
    WeakCopyleft = 2,
    StrongCopyleft = 3
};

struct SubmoduleNode {
    std::string path;
    std::string url;
    std::string index_sha;
    std::string head_sha;
    std::string detected_license{"UNKNOWN"};
    LicenseCategory license_category{LicenseCategory::Unknown};
    AuditStatus status{AuditStatus::Ok};
    bool in_gitmodules{false};
    bool in_index{false};
    int depth{0};
};

enum class AuditError {
    FileNotFound,
    InvalidMagic,
    UnsupportedVersion,
    CorruptedData,
    RecursionLimitExceeded
};

class SubmoduleTreeAuditor {
public:
    static std::expected<std::vector<SubmoduleNode>, AuditError>
    audit_tree(const fs::path& root_path) {
        std::vector<SubmoduleNode> results;
        std::unordered_set<std::string> visited;

        auto status = audit_recursive(root_path, "", 0, results, visited);
        if (!status) return std::unexpected(status.error());

        return results;
    }

    static void print_report(const std::vector<SubmoduleNode>& nodes) {
        std::cout << "\n================================= RECURSIVE SUBMODULE AUDIT REPORT =================================\n";
        std::cout << std::format("{:<4} {:<28} {:<12} {:<18} {:<12} {}\n",
                                 "LVL", "SUBMODULE PATH", "STATUS", "SPDX LICENSE", "CATEGORY", "COMMIT DIVERGENCE (INDEX -> HEAD)");
        std::cout << "----------------------------------------------------------------------------------------------------\n";

        for (const auto& node : nodes) {
            std::string_view st_str = "OK";
            switch (node.status) {
                case AuditStatus::Uninitialized: st_str = "UNINIT"; break;
                case AuditStatus::CommitDrift: st_str = "DRIFT"; break;
                case AuditStatus::InsecureUrl: st_str = "INSECURE"; break;
                case AuditStatus::ConfigMismatch: st_str = "MISMATCH"; break;
                default: break;
            }

            std::string_view cat_str = "UNKNOWN";
            switch (node.license_category) {
                case LicenseCategory::Permissive: cat_str = "PERMISSIVE"; break;
                case LicenseCategory::WeakCopyleft: cat_str = "WEAK-COPY"; break;
                case LicenseCategory::StrongCopyleft: cat_str = "STRONG-COPY"; break;
                default: break;
            }

            std::string s_idx = node.index_sha.substr(0, std::min<size_t>(8, node.index_sha.size()));
            std::string s_head = node.head_sha.substr(0, std::min<size_t>(8, node.head_sha.size()));

            std::cout << std::format("[{}]  {:<28} {:<12} {:<18} {:<12} {} -> {}\n",
                                     node.depth, node.path, st_str, node.detected_license, cat_str, s_idx, s_head);
        }
        std::cout << "====================================================================================================\n\n";
    }

    static void export_sbom(const fs::path& out_path, const std::vector<SubmoduleNode>& nodes) {
        std::ofstream out(out_path);
        if (!out.is_open()) return;

        out << "{\n";
        out << "  \"$schema\": \"https://cyclonedx.org/schema/bom-1.5.json\",\n";
        out << "  \"bomFormat\": \"CycloneDX\",\n";
        out << "  \"specVersion\": \"1.5\",\n";
        out << "  \"components\": [\n";

        for (size_t i = 0; i < nodes.size(); ++i) {
            const auto& n = nodes[i];
            out << "    {\n";
            out << "      \"type\": \"library\",\n";
            out << std::format("      \"name\": \"{}\",\n", n.path);
            out << std::format("      \"version\": \"{}\",\n", n.index_sha);
            out << std::format("      \"purl\": \"pkg:generic/{}@{}\",\n", n.path, n.index_sha);
            out << "      \"externalReferences\": [\n";
            out << "        {\n";
            out << "          \"type\": \"vcs\",\n";
            out << std::format("          \"url\": \"{}\"\n", n.url);
            out << "        }\n";
            out << "      ],\n";
            out << "      \"licenses\": [\n";
            out << "        {\n";
            out << "          \"license\": {\n";
            out << std::format("            \"id\": \"{}\"\n", n.detected_license);
            out << "          }\n";
            out << "        }\n";
            out << "      ],\n";
            out << "      \"properties\": [\n";
            out << std::format("        {{\"name\": \"audit:status\", \"value\": \"{}\"}},\n", static_cast<int>(n.status));
            out << std::format("        {{\"name\": \"audit:headSha\", \"value\": \"{}\"}},\n", n.head_sha);
            out << std::format("        {{\"name\": \"audit:depth\", \"value\": \"{}\"}}\n", n.depth);
            out << "      ]\n";
            out << "    }" << (i + 1 < nodes.size() ? "," : "") << "\n";
        }
        out << "  ]\n}\n";
    }

private:
    static uint32_t parse_be32(std::span<const uint8_t, 4> b) noexcept {
        return (static_cast<uint32_t>(b[0]) << 24) |
               (static_cast<uint32_t>(b[1]) << 16) |
               (static_cast<uint32_t>(b[2]) << 8)  |
               (static_cast<uint32_t>(b[3]));
    }

    static std::string hex_sha(std::span<const uint8_t, 20> sha) {
        std::string s;
        s.reserve(40);
        for (uint8_t byte : sha) s += std::format("{:02x}", byte);
        return s;
    }

    static std::expected<void, AuditError>
    audit_recursive(const fs::path& repo_root, const std::string& prefix, int depth,
                    std::vector<SubmoduleNode>& nodes, std::unordered_set<std::string>& visited) {
        if (depth > MAX_RECURSION_DEPTH) return std::unexpected(AuditError::RecursionLimitExceeded);

        std::string canonical_root = fs::canonical(repo_root).string();
        if (visited.contains(canonical_root)) return {};
        visited.insert(canonical_root);

        const auto index_path = repo_root / ".git" / "index";
        const auto modules_path = repo_root / ".gitmodules";

        if (fs::exists(index_path)) {
            parse_index(index_path, prefix, depth, nodes);
        }

        if (fs::exists(modules_path)) {
            parse_modules(modules_path, prefix, depth, nodes);
        }

        size_t current_sz = nodes.size();
        for (size_t i = 0; i < current_sz; ++i) {
            auto& node = nodes[i];
            if (node.depth != depth) continue;

            if (node.url.starts_with("http://")) {
                node.status = AuditStatus::InsecureUrl;
            }
            if (!node.in_gitmodules || !node.in_index) {
                node.status = AuditStatus::ConfigMismatch;
            }

            const auto head_file = repo_root / ".git" / "modules" / node.path / "HEAD";
            std::error_code ec;
            if (fs::exists(head_file, ec)) {
                std::ifstream hf(head_file);
                std::string h_line;
                if (std::getline(hf, h_line)) {
                    auto tr_h = trim(h_line);
                    if (tr_h.starts_with("ref: ")) {
                        std::string ref_target = std::string(tr_h.substr(5));
                        auto ref_path = repo_root / ".git" / "modules" / node.path / ref_target;
                        if (fs::exists(ref_path, ec)) {
                            std::ifstream rf(ref_path);
                            std::string ref_line;
                            if (std::getline(rf, ref_line)) {
                                node.head_sha = std::string(trim(ref_line));
                            }
                        } else {
                            auto packed_file = repo_root / ".git" / "modules" / node.path / "packed-refs";
                            node.head_sha = resolve_packed(packed_file, ref_target);
                        }
                    } else {
                        node.head_sha = std::string(tr_h);
                    }
                }
            } else {
                node.head_sha = "UNINITIALIZED";
                node.status = AuditStatus::Uninitialized;
            }

            if (node.status == AuditStatus::Ok && node.index_sha != node.head_sha) {
                node.status = AuditStatus::CommitDrift;
            }

            const auto sub_dir = repo_root / node.path;
            node.detected_license = scan_spdx_directory(sub_dir);
            node.license_category = classify_license(node.detected_license);

            const auto nested_mod = sub_dir / ".gitmodules";
            if (fs::exists(nested_mod, ec)) {
                audit_recursive(sub_dir, node.path, depth + 1, nodes, visited);
            }
        }
        return {};
    }

    static void parse_index(const fs::path& index_path, const std::string& prefix, int depth, std::vector<SubmoduleNode>& nodes) {
        std::ifstream file(index_path, std::ios::binary);
        if (!file.is_open()) return;

        uint8_t hdr[12];
        if (!file.read(reinterpret_cast<char*>(hdr), 12)) return;

        uint32_t magic = parse_be32(std::span<const uint8_t, 4>(hdr, 4));
        uint32_t version = parse_be32(std::span<const uint8_t, 4>(hdr + 4, 4));
        uint32_t count = parse_be32(std::span<const uint8_t, 4>(hdr + 8, 4));

        if (magic != DIRC_MAGIC || version < 2 || version > 4) return;

        for (uint32_t i = 0; i < count; ++i) {
            uint8_t fixed[62];
            if (!file.read(reinterpret_cast<char*>(fixed), 62)) break;

            uint32_t mode = parse_be32(std::span<const uint8_t, 4>(fixed + 24, 4));
            uint16_t flags = (static_cast<uint16_t>(fixed[60]) << 8) | fixed[61];
            uint16_t name_len = flags & 0x0FFF;

            std::string path_str;
            if (name_len < 0x0FFF) {
                path_str.resize(name_len);
                file.read(path_str.data(), name_len);
            } else {
                std::getline(file, path_str, '\0');
            }

            size_t total = 62 + path_str.size();
            size_t pad = 8 - (total % 8);
            if (pad == 0) pad = 8;
            file.seekg(pad, std::ios::cur);

            if ((mode & 0170000) == MODE_GITLINK) {
                std::string full_path = prefix.empty() ? path_str : prefix + "/" + path_str;
                auto it = std::find_if(nodes.begin(), nodes.end(), [&](const auto& n) { return n.path == full_path; });
                if (it == nodes.end()) {
                    SubmoduleNode node;
                    node.path = std::move(full_path);
                    node.index_sha = hex_sha(std::span<const uint8_t, 20>(fixed + 40, 20));
                    node.in_index = true;
                    node.depth = depth;
                    nodes.push_back(std::move(node));
                } else {
                    it->index_sha = hex_sha(std::span<const uint8_t, 20>(fixed + 40, 20));
                    it->in_index = true;
                }
            }
        }
    }

    static void parse_modules(const fs::path& modules_path, const std::string& prefix, int depth, std::vector<SubmoduleNode>& nodes) {
        std::ifstream file(modules_path);
        std::string line, cur_path, cur_url;

        auto flush = [&]() {
            if (!cur_path.empty()) {
                std::string full_path = prefix.empty() ? cur_path : prefix + "/" + cur_path;
                auto it = std::find_if(nodes.begin(), nodes.end(), [&](const auto& n) { return n.path == full_path; });
                if (it == nodes.end()) {
                    SubmoduleNode node;
                    node.path = full_path;
                    node.url = cur_url;
                    node.in_gitmodules = true;
                    node.depth = depth;
                    nodes.push_back(std::move(node));
                } else {
                    it->url = cur_url;
                    it->in_gitmodules = true;
                }
                cur_path.clear();
                cur_url.clear();
            }
        };

        while (std::getline(file, line)) {
            auto tr = trim(line);
            if (tr.empty() || tr.starts_with('#') || tr.starts_with(';')) continue;

            if (tr.starts_with('[')) {
                flush();
                continue;
            }

            auto eq = tr.find('=');
            if (eq == std::string_view::npos) continue;

            auto k = trim(tr.substr(0, eq));
            auto v = trim(tr.substr(eq + 1));

            if (k == "path") cur_path = std::string(v);
            else if (k == "url") cur_url = std::string(v);
        }
        flush();
    }

    static std::string resolve_packed(const fs::path& packed_path, std::string_view ref_name) {
        std::ifstream file(packed_path);
        if (!file.is_open()) return "UNKNOWN_REF";

        std::string line;
        while (std::getline(file, line)) {
            auto tr = trim(line);
            if (tr.empty() || tr.starts_with('#') || tr.starts_with('^')) continue;

            auto sp = tr.find(' ');
            if (sp == std::string_view::npos) continue;

            auto sha = tr.substr(0, sp);
            auto name = trim(tr.substr(sp + 1));

            if (name == ref_name) return std::string(sha);
        }
        return "UNKNOWN_REF";
    }

    static std::string scan_spdx_directory(const fs::path& dir_path) {
        std::error_code ec;
        if (!fs::exists(dir_path, ec) || !fs::is_directory(dir_path, ec)) return "UNKNOWN";

        for (const auto& entry : fs::recursive_directory_iterator(dir_path, fs::directory_options::skip_permission_denied, ec)) {
            if (entry.is_regular_file()) {
                const auto ext = entry.path().extension().string();
                const auto name = entry.path().filename().string();

                if (ext == ".c" || ext == ".h" || ext == ".cpp" || ext == ".hpp" || ext == ".S" ||
                    name == "LICENSE" || name == "COPYING") {
                    auto lic = scan_spdx_file(entry.path());
                    if (lic != "UNKNOWN") return lic;
                }
            }
        }
        return "UNKNOWN";
    }

    static std::string scan_spdx_file(const fs::path& file_path) {
        std::ifstream f(file_path);
        if (!f.is_open()) return "UNKNOWN";

        std::string line;
        int count = 0;
        while (std::getline(f, line) && count < 100) {
            count++;
            auto pos = line.find("SPDX-License-Identifier:");
            if (pos != std::string::npos) {
                auto spdx_val = trim(line.substr(pos + 24));
                auto comment_end = spdx_val.find("*/");
                if (comment_end != std::string_view::npos) {
                    spdx_val = trim(spdx_val.substr(0, comment_end));
                }
                if (!spdx_val.empty()) return std::string(spdx_val);
            }
        }
        return "UNKNOWN";
    }

    static LicenseCategory classify_license(std::string_view lic) {
        if (lic.find("MIT") != std::string_view::npos ||
            lic.find("BSD") != std::string_view::npos ||
            lic.find("Apache") != std::string_view::npos ||
            lic.find("ISC") != std::string_view::npos ||
            lic.find("Zlib") != std::string_view::npos ||
            lic.find("Unlicense") != std::string_view::npos ||
            lic.find("CC0") != std::string_view::npos) {
            return LicenseCategory::Permissive;
        }
        if (lic.find("LGPL") != std::string_view::npos ||
            lic.find("MPL") != std::string_view::npos ||
            lic.find("CDDL") != std::string_view::npos ||
            lic.find("EPL") != std::string_view::npos) {
            return LicenseCategory::WeakCopyleft;
        }
        if (lic.find("GPL") != std::string_view::npos ||
            lic.find("AGPL") != std::string_view::npos ||
            lic.find("SSPL") != std::string_view::npos) {
            return LicenseCategory::StrongCopyleft;
        }
        return LicenseCategory::Unknown;
    }

    static std::string_view trim(std::string_view s) noexcept {
        auto start = s.find_first_not_of(" \t\r\n");
        if (start == std::string_view::npos) return {};
        auto end = s.find_last_not_of(" \t\r\n");
        return s.substr(start, end - start + 1);
    }
};

} // namespace auditor

int main(int argc, char** argv) {
    fs::path repo_root = (argc > 1) ? argv[1] : ".";

    auto result = auditor::SubmoduleTreeAuditor::audit_tree(repo_root);
    if (!result) {
        std::cerr << "Audit failed with internal error\n";
        return 1;
    }

    auditor::SubmoduleTreeAuditor::print_report(*result);
    auditor::SubmoduleTreeAuditor::export_sbom("submodule-audit.json", *result);

    bool has_critical = false;
    for (const auto& node : *result) {
        if (node.status != auditor::AuditStatus::Ok || node.license_category == auditor::LicenseCategory::StrongCopyleft) {
            has_critical = true;
            break;
        }
    }

    return has_critical ? 1 : 0;
}
```
:::

## Тестовий стенд та автоматизована валідація

Для перевірки коректності роботи аудитора створюється синтетичний тестовий репозиторій із трьома сценаріями дефектів:
1. **Підмодуль A (Синхронізований)**: ініціалізований, має ліцензію MIT, стан `OK`.
2. **Підмодуль B (Commit Drift)**: локальний `HEAD` змінено на новий коміт, що не зафіксований в індексі батьківського проекту.
3. **Підмодуль C (Insecure URL + GPL-3.0)**: використовує протокол `http://` та містить заголовок `SPDX-License-Identifier: GPL-3.0-only`.

Скрипт генерації тестового стенду та перевірки:

```bash
#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="/tmp/git_submodule_test_env"
rm -rf "${TEST_DIR}"
mkdir -p "${TEST_DIR}"

# 1. Створення фіктивних зовнішніх репозиторіїв
mkdir -p "${TEST_DIR}/remote/lib_a"
git -C "${TEST_DIR}/remote/lib_a" init
echo "/* SPDX-License-Identifier: MIT */" > "${TEST_DIR}/remote/lib_a/lib_a.c"
git -C "${TEST_DIR}/remote/lib_a" add lib_a.c
git -C "${TEST_DIR}/remote/lib_a" commit -m "Initial commit for lib_a"

mkdir -p "${TEST_DIR}/remote/lib_b"
git -C "${TEST_DIR}/remote/lib_b" init
echo "/* SPDX-License-Identifier: BSD-3-Clause */" > "${TEST_DIR}/remote/lib_b/lib_b.c"
git -C "${TEST_DIR}/remote/lib_b" add lib_b.c
git -C "${TEST_DIR}/remote/lib_b" commit -m "Initial commit for lib_b"

mkdir -p "${TEST_DIR}/remote/lib_c"
git -C "${TEST_DIR}/remote/lib_c" init
echo "/* SPDX-License-Identifier: GPL-3.0-only */" > "${TEST_DIR}/remote/lib_c/lib_c.c"
git -C "${TEST_DIR}/remote/lib_c" add lib_c.c
git -C "${TEST_DIR}/remote/lib_c" commit -m "Initial commit for lib_c"

# 2. Створення батьківського репозиторію та додавання підмодулів
mkdir -p "${TEST_DIR}/main_project"
git -C "${TEST_DIR}/main_project" init
git -C "${TEST_DIR}/main_project" submodule add "../remote/lib_a" libs/lib_a
git -C "${TEST_DIR}/main_project" submodule add "../remote/lib_b" libs/lib_b
git -C "${TEST_DIR}/main_project" submodule add "http://insecure-host.internal/lib_c.git" libs/lib_c
git -C "${TEST_DIR}/main_project" commit -m "Add submodules A, B, C"

# 3. Симуляція Commit Drift у lib_b
echo "/* New feature in lib_b */" >> "${TEST_DIR}/main_project/libs/lib_b/lib_b.c"
git -C "${TEST_DIR}/main_project/libs/lib_b" commit -am "Update lib_b locally"

# 4. Компіляція та запуск аудитора
gcc -O2 -std=c99 -Wall -Wextra submodule_tree_auditor.c -o "${TEST_DIR}/auditor"
"${TEST_DIR}/auditor" "${TEST_DIR}/main_project" || true
```

Запуск аудитора на такому стенді генерує вичерпну діагностику, фіксує статус `DRIFT` для `libs/lib_b`, статус `INSECURE` та категорію `STRONG-COPY` для `libs/lib_c`, а також повертає ненульовий код виходу, що надійно блокує збірку в конвеєрі CI/CD.
