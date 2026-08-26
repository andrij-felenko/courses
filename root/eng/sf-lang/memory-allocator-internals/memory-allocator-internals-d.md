# Внутрішня будова алокатора

<preknowlist>
- [Купа](root:sf-lang/heap-dynamic-memory) — інтерфейс динамічної пам'яті `malloc` і `free`, ручне керування часом життя об'єктів.
- [Адреси й покажчики](root:sf-lang/addresses-pointers) — пряма адресація пам'яті, вирівнювання даних та арифметика покажчиків.
- [Ілюзія власної пам'яті](root:unix/memory-illusion) — віртуальний адресний простір, сторінкова організація пам'яті ядра та системні виклики керування пам'яттю.
- [Фрагментація пам'яті: зовнішня і внутрішня](root:sf-lang/memory-fragmentation) — роздроблення суцільного адресного простору на дрібні уламки.
</preknowlist>

Виклик `malloc(24)` вимагає виділення двадцяти чотирьох байтів під вузол двозв'язного списку. Якщо звернутися за ними напряму до ядра операційної системи, процес змушений виконати системний виклик (англ. *system call*), що призведе до перемикання контексту процесора з користувацького простору в режим ядра, оновлення структур віртуальної пам'яті процесу та виділення щонайменше однієї цілої апаратної сторінки розміром 4096 байтів (4 КіБ). Отримання двадцяти чотирьох байтів ціною системного виклику у кілька сотень тактів і втрати 4072 байтів на невикористаний залишок сторінки зробило б дрібні алокації руйнівними як для швидкодії, так і для обсягу пам'яті.

Щоб подолати прірву між гранулярними, динамічними запитами програми та грубими сторінками операційної системи, у просторі користувача працює **алокатор пам'яті** (англ. *memory allocator*, від лат. *allocare* — «виділяти, розподіляти»). Алокатор бере в ядра великі суцільні області віртуальної пам'яті (від сотень кілобайтів до гігабайтів), організовує всередині них власну бухгалтерію, нарізає їх на блоки потрібного розміру за лічені наносекунди й склеює звільнені шматки назад, запобігаючи хаосу та вичерпанню адресного простору.

![Роль алокатора як посередника між дрібними запитами програми та сторінками операційної системи](/root/eng/sf-lang/memory-allocator-internals/img/allocator-role.svg)
*Алокатор простору користувача діє як високоефективний кешуючий шар: мільйони дрібних викликів `malloc`/`free` обслуговуються за 5–15 тактів процесора без системних викликів, тоді як ядро залучається лише рідко для отримання чи повернення великих блоків сторінок.*

## Системний інтерфейс: як алокатор отримує сиру пам'ять від ядра

Алокатор не створює пам'ять із повітря — він оперує віртуальним адресним простором, наданим ядром операційної системи через два фундаментальні механізми: зміну межі сегмента даних (`brk`/`sbrk`) та створення анонімних відображень (`mmap`).

### 1. Традиційний сегмент купи: `brk` та `sbrk`

Історично в середовищі Unix пам'ять процесу мала фіксовану структуру, де купа починалася одразу за неініціалізованими глобальними змінними (сегмент `.bss`) і зростала вгору в бік старших адрес. Поточну верхню межу цієї ділянки називають **точкою розриву програми** (англ. *program break*, або `brk`).

```
Нижні адреси                                                Верхні адреси
[ Текст коду (.text) ] [ Дані (.data) ] [ BSS ] [ Купа (Heap) ----> | brk ] ... [ Стек (Stack) <---- ]
```

Для зміни положення `brk` застосовують системні виклики:
- `int brk(void *addr)` — встановлює кінець сегмента даних за абсолютною адресою `addr`;
- `void *sbrk(intptr_t increment)` — зміщує поточний `brk` на відносну величину `increment` байтів і повертає попередню адресу розриву.

Коли алокатору потрібна пам'ять, він виконує `sbrk(131072)` (збільшення на 128 КіБ). Ядро розширює відповідну область віртуальної пам'яті (VMA), проте фізичні кадри оперативної пам'яті (DRAM) ще не виділяються: вони будуть прив'язані апаратурою сторінкового збою (*page fault*) лише в момент першого фактичного запису байта в цю сторінку.

Головна вада `brk` — **блокування верхівки** (англ. *head-of-line blocking*). Сегмент купи є неперервною лінійною смугою. Якщо програма виділила мільйон об'єктів, а потім звільнила 999 999 із них, але один живий об'єкт випадково опинився на самому кінці купи біля позначки `brk`, алокатор не має права знизити `brk` через `sbrk(-N)`. Усі гігабайти вільної пам'яті перед цим об'єктом виявляються замкненими у віртуальному адресному просторі процесу й не можуть бути повернуті системі.

### 2. Анонімні сторінкові відображення: `mmap`

Сучасні алокатори використовують системний виклик `mmap` із прапорцями `MAP_ANONYMOUS | MAP_PRIVATE`:

:::tabs
```c
#include <sys/mman.h>

void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE, 
                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
```
```cpp
#include <sys/mman.h>
#include <cstddef>

void *ptr = ::mmap(nullptr, size, PROT_READ | PROT_WRITE, 
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
```
:::

Слово «анонімне» означає, що пам'ять не прив'язана до жодного файлу на диску, а заповнена нулями. `mmap` виділяє незалежну ділянку в будь-якому вільному місці віртуального адресного простору з вирівнюванням на розмір сторінки (4 КіБ).

Переваги `mmap` над `brk`:
- **Повна незалежність ділянок:** будь-який блок, виділений через `mmap`, може бути миттєво повернутий ядру викликом `munmap(ptr, size)` у будь-який момент часу, незалежно від стану решти пам'яті програми.
- **Ізоляція багатопотокових арен:** кожен потік або кожне процесорне ядро може отримати окрему велику смугу пам'яті (наприклад, по 64 МіБ), виключаючи взаємне блокування при розширенні.
- **Пряме виділення гігантських блоків:** запити великого розміру (у glibc за замовчуванням понад 128 КіБ) спрямовуються напряму в `mmap`, уникаючи засмічення основної купи.

Отримавши від ядра масив сторінок через `brk` або `mmap`, алокатор повинен організувати внутрішню розмітку пам'яті.

## Анатомія чанка: заголовки, вирівнювання та кодування бітів

Одиницею внутрішнього обліку пам'яті є **чанк** (англ. *chunk* — «шматок, брила»). Чанк складається із службових метаданих (заголовка) та тіла, призначеного для збереження даних користувача (*payload*).

![Внутрішня структура зайнятого та вільного чанка пам'яті](/root/eng/sf-lang/memory-allocator-internals/img/chunk-layout.svg)
*Анатомія чанка: у зайнятому блоці заголовок містить розмір і 3 біти прапорців, а решта місця віддана користувачеві. У вільному блоці те саме тіло використовується алокатором для збереження покажчиків двозв'язного списку `fd`/`bk` та кінцевого тегу `prev_size`.*

### Вирівнювання та приховані біти

Усі сучасні 64-бітні процесори вимагають, щоб покажчики, які повертає `malloc`, були вирівняні щонайменше на 8 або 16 байтів (для коректної роботи векторних інструкцій SSE/AVX та атомарних операцій).

Якщо розмір будь-якого чанка в системі завжди кратний 16 байтам (`0x10`), то його числове значення у двійковій системі завжди закінчується на чотири нулі:

```
Розмір 32 байти   = 0b0000000000100000 (молодші 4 біти = 0000)
Розмір 64 байти   = 0b0000000001000000 (молодші 4 біти = 0000)
Розмір 128 байтів = 0b0000000010000000 (молодші 4 біти = 0000)
```

Три молодші біти 64-бітного поля `size` ніколи не несуть інформації про розмір. Цей факт дозволяє алокаторам застосувати класичну техніку **викрадення бітів** (англ. *bit-stealing*): використати три невикористовувані біти для збереження критично важливих прапорців статусу:

| Біт | Назва прапорця | Маска | Призначення |
|---|---|---|---|
| 0 | `PREV_INUSE` (P) | `0x1` | Показує, чи **зайнятий** фізично попередній сусідній чанк у пам'яті (`1` — зайнятий, `0` — вільний). |
| 1 | `IS_MMAPPED` (M) | `0x2` | Показує, чи був цей чанк виділений окремим викликом `mmap` (`1` — так, звільняти через `munmap`). |
| 2 | `NON_MAIN_ARENA` (A) | `0x4` | Показує, чи належить чанк до додаткової динамічної арени потоку (`1`), чи до головної купи `brk` (`0`). |

Щоб дізнатися справжній розмір чанка в байтах, алокатор просто скидає три молодші біти маскою `~0x7` (або `~0xF` при 16-байтному вирівнюванні):

:::tabs
```c
#include <stddef.h>
#include <stdbool.h>

size_t real_chunk_size = chunk_header->size & ~0x7;
bool is_prev_busy      = (chunk_header->size & 0x1) != 0;
bool is_from_mmap      = (chunk_header->size & 0x2) != 0;
```
```cpp
#include <cstddef>

const size_t real_chunk_size = chunk_header->size & ~0x7ULL;
const bool is_prev_busy      = (chunk_header->size & 0x1ULL) != 0;
const bool is_from_mmap      = (chunk_header->size & 0x2ULL) != 0;
```
:::

### Граничні теги Кнута (Boundary Tags)

Щоб звільнення блоку за адресою `free(ptr)` працювало швидко, алокатор повинен вміти за постійний час `O(1)` визначити:
1. Де закінчується поточний блок і починається наступний.
2. Де починається попередній фізичний блок у пам'яті.

Позиція наступного сусіда обчислюється тривіальним додаванням розміру до адреси поточного заголовка:

```
next_chunk_addr = current_chunk_addr + real_chunk_size
```

Але як знайти адресу *попереднього* сусіда, якщо блоки мають різну довжину? Дональд Кнут у 1968 році запропонував концепцію **граничних тегів** (англ. *boundary tags*): дублювати поле розміру не лише на початку блоку в заголовку (*header*), але й у його кінці — у футері (*footer*).

Тоді, перебуваючи на початку блоку `B`, алокатор може подивитися на 8 байтів назад (у футер блоку `A`), прочитати розмір `size_A` і миттєво обчислити початок `A`:

```
prev_chunk_addr = current_chunk_addr - size_A
```

#### Оптимізація dlmalloc: футер лише для вільних блоків
Якщо дублювати 8 байтів розміру у футері кожного зайнятого блоку, це створить значні накладні витрати пам'яті. Творець `dlmalloc` Дуг Лі запропонував геніальну оптимізацію: **футер зберігається лише тоді, коли блок вільний**.

Поки блок зайнятий, його останні 8 байтів віддані під корисні дані користувача. Але в заголовок *наступного* сусіда записується біт `PREV_INUSE = 1`. Коли блок звільняється, алокатор записує його розмір у його останні 8 байтів (поле `prev_size`) і скидає біт `PREV_INUSE = 0` у заголовку наступного чанка.

Тепер алгоритм перевірки попереднього сусіда виглядає так:
1. Поточний блок читає власний заголовок: якщо біт `PREV_INUSE == 1`, попередній сусід зайнятий — чіпати його заборонено.
2. Якщо біт `PREV_INUSE == 0`, попередній сусід гарантовано вільний. Його розмір лежить прямо перед нашим заголовком у полі `prev_size`. Ми відступаємо на `prev_size` байтів назад і отримуємо доступ до його заголовка.

Детальніше про те, як ці ідеї викристалізувалися в індустріальні стандарти, читайте в нарисі про [еволюцію алокаторів динамічної пам'яті](root:sf-lang/memory-allocator-internals/hist-allocator-evolution.md).

## Списки вільних блоків (Free Lists) та стратегії пошуку

Коли пам'ять звільняється через `free(p)`, алокатор не повертає її операційній системі негайно (оскільки системні виклики надто дорогі). Замість цього він зберігає вільні чанки у внутрішніх структурах даних для повторного використання під час наступних викликів `malloc`.

### 1. Неявний список (Implicit Free List)

У найпростішій схемі алокатор не створює окремих покажчиків між вільними блоками. Уся купа розглядається як неперервний ланцюг чанків, де кожен заголовок вказує на початок наступного.

Щоб знайти вільний блок під запит розміром `S`:
- Алокатор починає від старту купи й послідовно читає заголовки всіх блоків (як зайнятих, так і вільних).
- Перевіряє статус: якщо блок вільний і його розмір `size >= S`, блок обирається.

**Оцінка складності:** Пошук вимагає `O(N)` операцій, де `N` — загальна кількість усіх виділених блоків у програмі. На великих обсягах пам'яті лінійний перебір мільйонів зайнятих чанків призводить до катастрофічного падіння швидкодії та руйнує кеш процесора.

### 2. Явний список (Explicit Free List)

Щоб виключити зайняті блоки з пошуку, вільні чанки зшивають у явний зв'язний список.

Оскільки вільний чанк не містить даних користувача, його внутрішній простір (ті самі байти, де раніше лежали дані) використовується алокатором для збереження двох покажчиків:
- `fd` (*forward pointer*) — адреса наступного вільного чанка в списку;
- `bk` (*backward pointer*) — адреса попереднього вільного чанка в списку.

Ці покажчики займають `2 × 8 = 16` байтів, але вимагають **нуль байтів додаткової пам'яті**, оскільки розміщуються всередині вільного тіла. Єдине обмеження — мінімальний розмір чанка не може бути меншим за `24` або `32` байти (заголовок + два покажчики + вирівнювання).

### 3. Розділені списки та розмірні класи (Segregated Free Lists / Bins)

Один спільний явний список вільних блоків різного розміру все одно вимагає перебору `O(M)` вільних елементів. Щоб зробити виділення миттєвим, алокатори застосовують **розділені списки** (англ. *segregated fits*): пам'ять розбивають на масив незалежних кошиків (англ. *bins*), кожен із яких містить блоки лише певного калібру.

У класичній моделі `ptmalloc` / `dlmalloc` існує чотири категорії кошиків:

```
                                  [ Масив Bins ]
   ┌───────────────┬───────────────────┬───────────────────┬─────────────────────┐
   │ Fastbins (LIFO)│ Smallbins (FIFO)  │ Largebins (Sorted)│ Unsorted Bin (Cache)│
   │  16 B – 80 B  │   80 B – 1024 B   │   1024 B – 128 KiB│   Тимчасовий буфер  │
   │ O(1) lock-free│ O(1) точний розмір│ O(log N) діапазони│   для злиття/пошуку │
   └───────────────┴───────────────────┴───────────────────┴─────────────────────┘
```

#### Fastbins (Швидкі кошики)
- Обслуговують найдрібніші виділення (від 16 до 80 байтів із кроком 8 байтів).
- Організовані як однозв'язні LIFO-стеки (останнім прийшов — першим пішов).
- **Особливість:** при звільненні блоки у fastbins **не зливаються із сусідами негайно**. Це дозволяє повертати блок за одну операцію додавання в голову списку `O(1)`. Злиття відкладається до моменту, коли пам'ять вичерпається.

#### Smallbins (Дрібні кошики)
- Масив із 62 двозв'язних циклічних списків для розмірів від 80 байтів до 1024 байтів (із суворим кроком у 16 байтів).
- Кожен список містить блоки **одного точного розміру**.
- Пошук займає `O(1)`: алокатор вираховує індекс списку простою формулою `bin_idx = size >> 4` і забирає перший елемент за принципом FIFO.

#### Largebins (Великі кошики)
- 63 двозв'язні списки, де кожен список обслуговує не один фіксований розмір, а певний числовий діапазон (наприклад, кошик від 1024 до 1152 байтів).
- Блоки всередині списку відсортовані за спаданням розміру.
- Пошук виконує алгоритм *Best-Fit* або *Good-Fit* для вибору найменшого підхожого блоку.

#### Unsorted Bin (Невпорядкований кошик)
- Єдиний транзитний двозв'язний список, куди потрапляють усі звільнені чанки зі `smallbins` та `largebins`.
- Слугує кешем другого рівня: якщо програма щойно звільнила блок на 120 байтів і одразу запитує 120 байтів, алокатор повторно видає цей блок без проходження всієї ієрархії сортування.

### Стратегії підбору блоку всередині списку

Коли потрібний точний розмір відсутній, алокатор обирає блок із більших вільних ділянок за однією зі стратегій:
- **First-Fit (Перший підхожий):** сканує список від початку й бере перший знайдений блок, чий розмір `size >= requested`. Швидкий метод, але накопичує дрібні уламки на початку списку.
- **Best-Fit (Найкращий підхожий):** переглядає весь список і обирає блок із мінімальною різницею `(size - requested)`. Мінімізує відходи кожного виділення, але повільний `O(N)` і створює велику кількість крихітних, непридатних до використання залишків.
- **Next-Fit (Наступний підхожий):** починає пошук не від голови списку, а з місця, де завершився попередній вдалий пошук. Рівномірніше розподіляє блоки по адресній смузі.

Після знаходження більшого блоку алокатор виконує його **розбиття** (англ. *splitting*): відрізає частину під запит, а залишок перетворює на новий вільний чанк і повертає у відповідний bin.

## Двійковий Buddy Allocator

Альтернативою системі списків на основі граничних тегів є **двійковий алокатор близнюків** (англ. *binary buddy allocator*, від англ. *buddy* — «приятель, близнюк»). Цей алгоритм виключає необхідність збереження розмірів у футерах завдяки суворій геометрії степенів двійки.

![Двійковий Buddy Allocator: розбиття та злиття блоків степенів двійки](/root/eng/sf-lang/memory-allocator-internals/img/buddy-split-merge.svg)
*Принцип Buddy-алокації: блок рекурсивно ділиться на дві рівні половини, поки не досягне мінімального розміру запиту. Адреса сусіда-близнюка обчислюється миттєво через оператор побітового виключного АБО (XOR).*

### Математика адрес близнюків

Нехай увесь пул пам'яті має розмір `2ᴹ` (наприклад, 64 КіБ, `M = 16`). Будь-яке виділення округлюється вгору до найближчого степеня двійки `2ᵏ`.

Якщо запит вимагає 8 КіБ, а в наявності є лише вільний блок на 32 КіБ, алокатор ділить 32 КіБ навпіл: утворюються два блоки по 16 КіБ з відносними зсувами `0x0000` та `0x4000`. Один із блоків 16 КіБ ділиться ще раз навпіл — на два блоки по 8 КіБ із відносними зсувами `0x0000` та `0x2000`.

Головна перевага полягає у визначенні адреси сусіднього близнюка для блоку порядку `k` з адресою `addr`:

```
buddy_addr = block_addr ^ (1 << k)
```

**Крок обчислення адреси через XOR:**
```
Адреса блоку:      0x0000 = 0b0000000000000000
Розмір блоку:      8 КіБ  = 0b0010000000000000 (1 << 13)
Адреса близнюка:   0x2000 = 0b0010000000000000 [результат XOR]
```

Коли блок звільняється, алокатор за один такт обчислює адресу його близнюка. Якщо близнюк також вільний і має такий самий порядок `k`, вони видаляються зі списків і зливаються в один блок порядку `k+1`. Процес рекурсивно продовжується вгору за деревом.

Практичну програмну реалізацію цього механізму з повнофункціональними тестами розібрано у вставці про [реалізацію двійкового Buddy-алокатора](root:sf-lang/memory-allocator-internals/proj-buddy-allocator.md).

## Коалесценція та повернення пам'яті ядру

Коли блоки пам'яті виділяються й звільняються у випадковому порядку, виникає явище **фрагментації** (від лат. *fragmentum* — «уламок»):
- **Внутрішня фрагментація:** надлишок пам'яті всередині виділеного чанка через вирівнювання на 16 байтів або округлення до степенів двійки.
- **Зовнішня фрагментація:** наявність великого сумарного обсягу вільної пам'яті, яка розбита на крихітні незв'язні уламки, через що запит на один великий суцільний блок зазнає невдачі.

### Коалесценція суміжних блоків

Єдиним способом боротьби із зовнішньою фрагментацією є **коалесценція** (англ. *coalescing*, від лат. *coalescere* — «зростатися, зливатися») — об'єднання двох або трьох суміжних вільних чанків в один великий неперервний блок.

![Коалесценція вільних блоків за граничними тегами Кнута](/root/eng/sf-lang/memory-allocator-internals/img/coalescing-boundary-tags.svg)
*Двостороннє злиття: при звільненні чанка B алокатор перевіряє лівого сусіда A (через біт PREV_INUSE) та правого сусіда C (за адресою B + size_B) і зшиває їх в єдиний блок розміром 192 байти за O(1).*

Коли викликається `free(B)`:
1. **Злиття назад (Backward coalescing):** алокатор дивиться на біт `PREV_INUSE` у заголовку `B`. Якщо він дорівнює нулю, чанк `A` ліворуч вільний. Алокатор читає `prev_size` чанка `A`, вилучає `A` з його поточного списку вільних блоків, об'єднує розміри `size = size_A + size_B` і встановлює новий початок чанка за адресою `A`.
2. **Злиття вперед (Forward coalescing):** алокатор обчислює адресу правого сусіда `C = B + size_B`. Читає заголовок чанка `C`. Якщо `C` вільний (перевіряється заголовок наступного за ним чанка `D`, чи встановлений там біт `PREV_INUSE`), `C` вилучається зі списку, а його розмір додається до загального: `size = size + size_C`.
3. Отриманий гігантський блок записує новий розмір у свій заголовок і футер та поміщається в `Unsorted bin`.

Усі ці кроки виконуються за сталий час `O(1)` без повного сканування пам'яті.

### Тримінг пам'яті: повернення сторінок операційній системі

Навіть після успішної коалесценції пам'ять залишається всередині адресного простору процесу. Якщо високонавантажений сервер обробив денний пік запитів, виділивши 16 ГіБ RAM, а вночі використовує лише 500 МБ, утримання 15.5 ГіБ вільної пам'яті всередині алокатора заблокує ресурси фізичної DRAM для решти процесів сервера.

Для повернення пам'яті назад операційній системі застосовують механізм **тримінгу** (англ. *memory trimming*, від англ. *trim* — «підрізати, підрівнювати»):

1. **Зниження верхівки купи `sbrk(-N)`:** якщо вільний чанк максимального розміру безпосередньо примикає до точки розриву програми `brk` і його розмір перевищує поріг `M_TRIM_THRESHOLD` (за замовчуванням 128 КіБ), алокатор зсуває `brk` вниз, віддаючи віртуальну пам'ять ядру.
2. **Анулювання сторінок через `madvise`:** якщо великий вільний блок лежить у середині купи або всередині mmap-арени (де змінити `brk` неможливо), алокатор викликає системний виклик ядра:

:::tabs
```c
#include <sys/mman.h>

// Повідомляє ядру, що фізичні сторінки за цією адресою можна вивільнити
madvise(page_aligned_addr, length, MADV_DONTNEED);
```
```cpp
#include <sys/mman.h>

// Вивільнення фізичних кадрів DRAM у ядрі
::madvise(page_aligned_addr, length, MADV_DONTNEED);
```
:::

Прапорець `MADV_DONTNEED` повідомляє віртуальній пам'яті ядра Linux: процес більше не потребує фізичних даних за цими адресами. Ядро негайно **скидає відповідні записи в таблицях сторінок і повертає фізичні кадри DRAM у пул вільної пам'яті операційної системи**. Проте віртуальний адресний діапазон залишається зарезервованим за процесом. Якщо програма пізніше знову звернеться до цих адрес через `malloc` і запише туди байти, процесор викличе сторінковий збій і ядро прозоро виділить нові нульові кадри DRAM.

Огляд системних функцій налаштування порогів та інструментів діагностики дивіться у вставці про [інтерфейс системного налаштування й діагностики алокатора](root:sf-lang/memory-allocator-internals/api-allocator-tuning.md).

## Багатопотокове масштабування: Арени та tcache

У сучасних багатопотокових серверах десятки потоків виконують сотні тисяч операцій `malloc`/`free` на секунду. Якщо всі вони звертаються до єдиного набору списків вільних блоків, спільний м'ютекс блокування перетворює пам'ять на головне вузьке місце системи.

Сучасні алокатори (`ptmalloc3`, `jemalloc`, `mimalloc`, `tcmalloc`) вирішують цю проблему за допомогою багаторівневої ієрархії кешів.

![Багаторівнева ієрархія алокатора динамічної пам'яті](/root/eng/sf-lang/memory-allocator-internals/img/multi-tier-hierarchy.svg)
*Ієрархія кешування пам'яті: 99% запитів обслуговуються на рівні 1 локальним кешем потоку `tcache` за лічені такти без блокувань. Рівні 2 та 3 залучаються лише при промахах кешу або масивних виділеннях.*

### 1. Арени пам'яті (Memory Arenas)

Щоб усунути глобальний замок, `ptmalloc` створює набір незалежних **арен** (від лат. *arena* — «поле для змагань, арена»). Кожна арена має власні структури: списки `fastbins`, `smallbins`, `largebins` та власний незалежний м'ютекс.

Кількість арен обмежується ядром:
```
N_arenas = 8 × N_cores  (на 64-бітних архітектурах)
N_arenas = 2 × N_cores  (на 32-бітних архітектурах)
```

Коли новий потік вперше викликає `malloc`, алокатор призначає йому одну з вільних арен за круговою схемою (*Round-Robin*). Потоки, прив'язані до різних арен, виділяють і звільняють пам'ять одночасно на різних ядрах процесора, не блокуючи один одного.

### 2. Локальний кеш потоку (Thread-Local Cache / tcache)

Починаючи з версії glibc 2.26, `ptmalloc` запозичив ідею `tcmalloc` та `jemalloc`, запровадивши **tcache** (*thread cache*).

Кожен потік процесу володіє власною структурою `tcache_perthread_struct`, розташованою у локальній пам'яті потоку (Thread-Local Storage, TLS через ключове слово `__thread`).
- `tcache` містить 64 однозв'язні стеки для розмірів від 24 до 1032 байтів.
- Кожен стек вміщує до 7 вільних чанків.

**Шлях виділення (Fast Path):**
Коли потік виконує `malloc(64)`:
1. Алокатор обчислює індекс кошика `tcache`.
2. Якщо в списку є хоча б один чанк, він витягується з голови стека:

:::tabs
```c
void *ptr = tcache->entries[bin_idx];
tcache->entries[bin_idx] = *(void**)ptr;
tcache->counts[bin_idx]--;
return ptr;
```
```cpp
void *ptr = tcache->entries[bin_idx];
tcache->entries[bin_idx] = *reinterpret_cast<void**>(ptr);
tcache->counts[bin_idx]--;
return ptr;
```
:::

Ця операція виконується за **5–10 тактів процесора** (рівнозначно кільком машинним інструкціям переміщення регістрів). У ній **немає жодних системних викликів, атомарних інструкцій CAS або захоплень м'ютексів**.

Лише якщо відповідний список у `tcache` порожній (промах кешу), потік захоплює м'ютекс своєї арени (Рівень 2), витягує пакет із 7 блоків одразу, один віддає користувачеві, а 6 залишає у своєму `tcache` на майбутнє.

## Практична інженерна реалізація: Segregated Freelist з коалесценцією

Створимо компактний, повністю автономний інженерний алокатор пам'яті на фіксованому системному пулі. Реалізація використовує граничні теги Кнута, явні розділені списки вільних блоків (*Segregated Bins*), розбиття блоків (*splitting*) під час алокації та миттєве двостороннє злиття (*coalescing*) під час звільнення.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ALIGNMENT 16
#define ALIGN(size) (((size) + (ALIGNMENT - 1)) & ~(ALIGNMENT - 1))

#define PREV_INUSE_FLAG 0x1
#define SIZE_MASK (~(size_t)(ALIGNMENT - 1))

#define HEAP_CAPACITY (256 * 1024) // 256 КіБ тестової пам'яті
#define NUM_BINS 8

typedef struct BlockHeader {
    size_t prev_size; // Використовується, лише якщо попередній блок вільний
    size_t size_flags; // Розмір блоку + прапорець PREV_INUSE у молодшому біті
    struct BlockHeader* next_free; // Вбудований покажчик на наступний вільний блок
    struct BlockHeader* prev_free; // Вбудований покажчик на попередній вільний блок
} BlockHeader;

#define HEADER_OVERHEAD (sizeof(size_t) * 2) // 16 байтів на заголовок
#define MIN_BLOCK_SIZE (ALIGN(sizeof(BlockHeader)))

typedef struct {
    uint8_t memory[HEAP_CAPACITY];
    BlockHeader* bins[NUM_BINS];
} SimpleAllocator;

static inline size_t get_size(const BlockHeader* b) {
    return b->size_flags & SIZE_MASK;
}

static inline bool is_prev_inuse(const BlockHeader* b) {
    return (b->size_flags & PREV_INUSE_FLAG) != 0;
}

static inline void set_size_and_flags(BlockHeader* b, size_t size, bool prev_inuse) {
    b->size_flags = (size & SIZE_MASK) | (prev_inuse ? PREV_INUSE_FLAG : 0);
}

static int get_bin_index(size_t size) {
    if (size <= 64)   return 0;
    if (size <= 128)  return 1;
    if (size <= 256)  return 2;
    if (size <= 512)  return 3;
    if (size <= 1024) return 4;
    if (size <= 4096) return 5;
    if (size <= 16384) return 6;
    return 7;
}

static void bin_insert(SimpleAllocator* a, BlockHeader* b) {
    int idx = get_bin_index(get_size(b));
    b->next_free = a->bins[idx];
    b->prev_free = NULL;
    if (a->bins[idx] != NULL) {
        a->bins[idx]->prev_free = b;
    }
    a->bins[idx] = b;
}

static void bin_remove(SimpleAllocator* a, BlockHeader* b) {
    int idx = get_bin_index(get_size(b));
    if (b->prev_free != NULL) {
        b->prev_free->next_free = b->next_free;
    } else {
        a->bins[idx] = b->next_free;
    }
    if (b->next_free != NULL) {
        b->next_free->prev_free = b->prev_free;
    }
    b->next_free = NULL;
    b->prev_free = NULL;
}

void allocator_init(SimpleAllocator* a) {
    memset(a->bins, 0, sizeof(a->bins));

    BlockHeader* initial = (BlockHeader*)a->memory;
    set_size_and_flags(initial, HEAP_CAPACITY, true);
    initial->prev_size = 0;
    initial->next_free = NULL;
    initial->prev_free = NULL;

    bin_insert(a, initial);
}

void* my_malloc(SimpleAllocator* a, size_t size) {
    if (size == 0) return NULL;

    size_t total_size = ALIGN(size + HEADER_OVERHEAD);
    if (total_size < MIN_BLOCK_SIZE) total_size = MIN_BLOCK_SIZE;

    int start_bin = get_bin_index(total_size);
    BlockHeader* victim = NULL;

    for (int i = start_bin; i < NUM_BINS; ++i) {
        BlockHeader* curr = a->bins[i];
        while (curr != NULL) {
            if (get_size(curr) >= total_size) {
                victim = curr;
                break;
            }
            curr = curr->next_free;
        }
        if (victim != NULL) break;
    }

    if (victim == NULL) return NULL; // OOM або фрагментація

    bin_remove(a, victim);
    size_t victim_size = get_size(victim);
    size_t remainder_size = victim_size - total_size;

    if (remainder_size >= MIN_BLOCK_SIZE) {
        // Розбиття (Splitting)
        set_size_and_flags(victim, total_size, is_prev_inuse(victim));

        BlockHeader* remainder = (BlockHeader*)((uint8_t*)victim + total_size);
        set_size_and_flags(remainder, remainder_size, true); // Попередній (victim) зайнятий
        remainder->prev_size = total_size;

        // Оновлюємо футер для сусіда remainder
        if ((uint8_t*)remainder + remainder_size < a->memory + HEAP_CAPACITY) {
            BlockHeader* next_phys = (BlockHeader*)((uint8_t*)remainder + remainder_size);
            next_phys->prev_size = remainder_size;
        }

        bin_insert(a, remainder);
    } else {
        // Віддаємо блок цілком
        if ((uint8_t*)victim + victim_size < a->memory + HEAP_CAPACITY) {
            BlockHeader* next_phys = (BlockHeader*)((uint8_t*)victim + victim_size);
            next_phys->size_flags |= PREV_INUSE_FLAG;
        }
    }

    // Повертаємо покажчик на корисні дані (одразу за заголовком)
    return (void*)((uint8_t*)victim + HEADER_OVERHEAD);
}

void my_free(SimpleAllocator* a, void* ptr) {
    if (ptr == NULL) return;

    BlockHeader* b = (BlockHeader*)((uint8_t*)ptr - HEADER_OVERHEAD);
    size_t size = get_size(b);
    bool prev_inuse = is_prev_inuse(b);

    // 1. Коалесценція назад (Backward coalescing)
    if (!prev_inuse) {
        BlockHeader* prev_block = (BlockHeader*)((uint8_t*)b - b->prev_size);
        bin_remove(a, prev_block);
        size += get_size(prev_block);
        prev_inuse = is_prev_inuse(prev_block);
        b = prev_block;
    }

    // 2. Коалесценція вперед (Forward coalescing)
    BlockHeader* next_block = (BlockHeader*)((uint8_t*)b + size);
    if ((uint8_t*)next_block < a->memory + HEAP_CAPACITY) {
        // Перевіряємо, чи вільний наступний блок
        BlockHeader* next_next = (BlockHeader*)((uint8_t*)next_block + get_size(next_block));
        bool next_is_free = true;
        if ((uint8_t*)next_next < a->memory + HEAP_CAPACITY) {
            next_is_free = !is_prev_inuse(next_next);
        }

        if (next_is_free) {
            bin_remove(a, next_block);
            size += get_size(next_block);
        } else {
            // Наступний блок зайнятий: скидаємо його PREV_INUSE у 0
            next_block->size_flags &= ~PREV_INUSE_FLAG;
            next_block->prev_size = size;
        }
    }

    set_size_and_flags(b, size, prev_inuse);

    // Оновлюємо футер вільного блоку для його правого сусіда
    BlockHeader* next_phys = (BlockHeader*)((uint8_t*)b + size);
    if ((uint8_t*)next_phys < a->memory + HEAP_CAPACITY) {
        next_phys->prev_size = size;
        next_phys->size_flags &= ~PREV_INUSE_FLAG;
    }

    bin_insert(a, b);
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <algorithm>

template <size_t HeapCapacity = 256 * 1024>
class SegregatedAllocator {
public:
    static constexpr size_t Alignment = 16;
    static constexpr size_t NumBins = 8;
    static constexpr size_t PrevInUseFlag = 0x1;
    static constexpr size_t SizeMask = ~(Alignment - 1);

    enum class AllocError {
        OutOfMemory,
        InvalidSize,
        InvalidPointer
    };

    SegregatedAllocator() noexcept {
        reset();
    }

    void reset() noexcept {
        bins_.fill(nullptr);

        auto* initial = reinterpret_cast<BlockHeader*>(memory_.data());
        initial->prev_size = 0;
        initial->set_size_and_flags(HeapCapacity, true);
        initial->next_free = nullptr;
        initial->prev_free = nullptr;

        bin_insert(initial);
    }

    [[nodiscard]] std::expected<std::span<std::byte>, AllocError> allocate(size_t payload_bytes) noexcept {
        if (payload_bytes == 0 || payload_bytes > HeapCapacity) {
            return std::unexpected(AllocError::InvalidSize);
        }

        const size_t total_size = std::max(align_up(payload_bytes + HeaderOverhead), MinBlockSize);
        const int start_bin = get_bin_index(total_size);
        BlockHeader* victim = nullptr;

        for (size_t i = start_bin; i < NumBins; ++i) {
            BlockHeader* curr = bins_[i];
            while (curr != nullptr) {
                if (curr->get_size() >= total_size) {
                    victim = curr;
                    break;
                }
                curr = curr->next_free;
            }
            if (victim != nullptr) break;
        }

        if (victim == nullptr) {
            return std::unexpected(AllocError::OutOfMemory);
        }

        bin_remove(victim);
        const size_t victim_size = victim->get_size();
        const size_t remainder_size = victim_size - total_size;

        if (remainder_size >= MinBlockSize) {
            victim->set_size_and_flags(total_size, victim->is_prev_inuse());

            auto* remainder = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(victim) + total_size);
            remainder->set_size_and_flags(remainder_size, true);
            remainder->prev_size = total_size;

            if (reinterpret_cast<std::byte*>(remainder) + remainder_size < memory_.data() + HeapCapacity) {
                auto* next_phys = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(remainder) + remainder_size);
                next_phys->prev_size = remainder_size;
            }

            bin_insert(remainder);
        } else {
            if (reinterpret_cast<std::byte*>(victim) + victim_size < memory_.data() + HeapCapacity) {
                auto* next_phys = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(victim) + victim_size);
                next_phys->size_flags |= PrevInUseFlag;
            }
        }

        auto* user_ptr = reinterpret_cast<std::byte*>(victim) + HeaderOverhead;
        return std::span<std::byte>(user_ptr, total_size - HeaderOverhead);
    }

    void deallocate(std::span<std::byte> user_span) noexcept {
        if (user_span.empty() || user_span.data() < memory_.data() ||
            user_span.data() >= memory_.data() + HeapCapacity) {
            return;
        }

        auto* b = reinterpret_cast<BlockHeader*>(user_span.data() - HeaderOverhead);
        size_t size = b->get_size();
        bool prev_inuse = b->is_prev_inuse();

        // Коалесценція назад
        if (!prev_inuse) {
            auto* prev_block = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(b) - b->prev_size);
            bin_remove(prev_block);
            size += prev_block->get_size();
            prev_inuse = prev_block->is_prev_inuse();
            b = prev_block;
        }

        // Коалесценція вперед
        auto* next_block = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(b) + size);
        if (reinterpret_cast<std::byte*>(next_block) < memory_.data() + HeapCapacity) {
            auto* next_next = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(next_block) + next_block->get_size());
            bool next_is_free = true;
            if (reinterpret_cast<std::byte*>(next_next) < memory_.data() + HeapCapacity) {
                next_is_free = !next_next->is_prev_inuse();
            }

            if (next_is_free) {
                bin_remove(next_block);
                size += next_block->get_size();
            } else {
                next_block->size_flags &= ~PrevInUseFlag;
                next_block->prev_size = size;
            }
        }

        b->set_size_and_flags(size, prev_inuse);

        auto* next_phys = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(b) + size);
        if (reinterpret_cast<std::byte*>(next_phys) < memory_.data() + HeapCapacity) {
            next_phys->prev_size = size;
            next_phys->size_flags &= ~PrevInUseFlag;
        }

        bin_insert(b);
    }

private:
    struct BlockHeader {
        size_t prev_size{0};
        size_t size_flags{0};
        BlockHeader* next_free{nullptr};
        BlockHeader* prev_free{nullptr};

        [[nodiscard]] size_t get_size() const noexcept {
            return size_flags & SizeMask;
        }

        [[nodiscard]] bool is_prev_inuse() const noexcept {
            return (size_flags & PrevInUseFlag) != 0;
        }

        void set_size_and_flags(size_t sz, bool prev_busy) noexcept {
            size_flags = (sz & SizeMask) | (prev_busy ? PrevInUseFlag : 0);
        }
    };

    static constexpr size_t HeaderOverhead = sizeof(size_t) * 2;
    static constexpr size_t MinBlockSize = (sizeof(BlockHeader) + Alignment - 1) & ~(Alignment - 1);

    alignas(std::max_align_t) std::array<std::byte, HeapCapacity> memory_{};
    std::array<BlockHeader*, NumBins> bins_{};

    [[nodiscard]] static constexpr size_t align_up(size_t sz) noexcept {
        return (sz + (Alignment - 1)) & ~(Alignment - 1);
    }

    [[nodiscard]] static int get_bin_index(size_t sz) noexcept {
        if (sz <= 64)   return 0;
        if (sz <= 128)  return 1;
        if (sz <= 256)  return 2;
        if (sz <= 512)  return 3;
        if (sz <= 1024) return 4;
        if (sz <= 4096) return 5;
        if (sz <= 16384) return 6;
        return 7;
    }

    void bin_insert(BlockHeader* b) noexcept {
        const int idx = get_bin_index(b->get_size());
        b->next_free = bins_[idx];
        b->prev_free = nullptr;
        if (bins_[idx] != nullptr) {
            bins_[idx]->prev_free = b;
        }
        bins_[idx] = b;
    }

    void bin_remove(BlockHeader* b) noexcept {
        const int idx = get_bin_index(b->get_size());
        if (b->prev_free != nullptr) {
            b->prev_free->next_free = b->next_free;
        } else {
            bins_[idx] = b->next_free;
        }
        if (b->next_free != nullptr) {
            b->next_free->prev_free = b->prev_free;
        }
        b->next_free = nullptr;
        b->prev_free = nullptr;
    }
};
```
:::

> 🔧 **Навіщо це.** Внутрішня будова алокатора демонструє фундаментальний інженерний баланс: пам'ять неможливо оптимізувати за швидкістю, обсягом і фрагментацією одночасно. Застосування розділених списків розмірних класів (*Segregated Bins*) скорочує час пошуку до `O(1)`, граничні теги Кнута дозволяють миттєво зливати вільні уламки для подолання зовнішньої фрагментації, а локальні кеші потоків (`tcache`) усувають блокування на багатоядерних системах. Розуміння цих рівнів абстракції дозволяє розробнику свідомо проектувати високонавантажені структури даних і точно діагностувати деградацію пам'яті у виробничих системах.
