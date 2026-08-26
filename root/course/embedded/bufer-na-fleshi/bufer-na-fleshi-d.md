# Буфер на флеші: накопичити й віддати потім

<preknowlist>
- [Гарантії доставки: щонайбільше раз, щонайменше раз, фактично раз](root:sf-distributed/delivery-guarantees) — чому мережевий транспорт втрачає пакети та як рівні доставки визначають необхідність локального буфера.
- [Повтори й експоненційний відступ](root:sf-distributed/retries-backoff) — алгоритми повторних спроб передачі накопичених даних після відновлення зв'язку.
- [Життя без зв'язку: що пристрій вирішує сам](root:embedded/zhyttia-bez-zviazku) — принципи автономної поведінки вузла та розділення контурів швидкого керування й повільної синхронізації.
- [Мертва черга й отруйне повідомлення](root:sf-distributed/dead-letter-queue) — ізоляція пошкоджених пакетів під час розбору черги повідомлень.
</preknowlist>

Автономна телеметрична станція на магістральному газопроводі або сейсмічний датчик у віддаленому гірському районі живляться від сонячної панелі з буферним залізо-фосфатним акумулятором. Під час тривалого бурану стільниковий зв'язок або супутниковий канал зникають на три тижні. Датчики вібрації, тиску й температури продовжують опитуватися кожні десять секунд, генеруючи по 64 байти структурованих вимірювань у кожному циклі опитування. Якщо мікроконтролер зберігає ці дані у динамічній оперативній пам'яті (SRAM), перше ж глибоке просідання напруги батареї (англ. *brownout*) або планове перезавантаження від сторожового таймера (англ. *Watchdog Timer*) миттєво знищує всі накопичені тисячі спостережень.

Спроба розв'язати проблему за допомогою мікросхеми EEPROM стикається з браком ємності: типовий чіп I2C EEPROM має обсяг 4–32 КБ, чого вистачає лише на кілька годин автономного логування. З іншого боку, встановлення дешевої енергонезалежної флеш-пам'яті SPI NOR Flash (наприклад, чіпів серії W25Q32 або MX25L64 на 4–8 МБ) відкриває гігантський простір для сотень тисяч записів, але негайно карає розробника апаратною специфікою кремнію. 

Якщо програміст реалізує на флеш-пам'яті наївний масив або класичний кільцевий буфер з оперативної пам'яті — зі зберіганням покажчиків голови й хвоста у фіксованому нульовому секторі, — цей сектор вичерпує свій ліміт у 100 000 циклів стирання рівно за шість днів безперервної роботи. Якщо ж для збереження повідомлень змонтувати повноцінну файлову систему, то раптове знеструмлення під час модифікації кореневих таблиць FAT або дескрипторів файлів призводить до незворотного пошкодження структури сховища та втрати всієї черги.

Енергонезалежний кільцевий буфер на Flash-пам'яті (англ. *Non-Volatile Flash Sector-Ring FIFO*) проєктується на зовсім інших засадах: нульовий оверхед метаданих, природне кругове вирівнювання зносу (англ. *Wear Leveling*), виведення стану черги без фіксованих покажчиків та гарантована стійкість до знеструмлення (англ. *Power-Cut Resilience*) на рівні окремих бітових переходів.

---

### Фізичні обмеження Flash-пам'яті: чому наївний буфер вбиває кристал

Щоб спроєктувати надійну структуру даних поверх Flash, необхідно розуміти фізичні процеси всередині напівпровідникової комірки з плаваючим затвором (англ. *Floating Gate*) або пасткою заряду (англ. *Charge Trap*).

![Асиметрія операцій читання, програмування та стирання в SPI NOR Flash](/root/course/embedded/bufer-na-fleshi/img/flash-asymmetry.svg)
*Асиметрія операцій читання, програмування та стирання в SPI NOR Flash: читання довільне й не руйнує діелектрик; запис можливий лише скиданням бітів 1 → 0; стирання виконується лише великими секторами по 4 КБ високою напругою.*

В енергонезалежній пам'яті SPI NOR Flash існує сувора ієрархія організації простору:
1. **Сторінка (Page, 256 байтів)** — мінімальна одиниця пакетного програмування. За один сеанс передачі по SPI можна записати від 1 до 256 байтів, але виключно в межах однієї фізичної сторінки (від адреси `0x...00` до `0x...FF`).
2. **Сектор (Sector, 4096 байтів / 4 КБ)** — мінімальна фізична одиниця стирання.
3. **Блок (Block, 32 КБ або 64 КБ)** — група з 8 або 16 секторів, що підтримує прискорене блокове стирання.
4. **Кристал (Chip, 1–32 МБ)** — сукупність усіх блоків.

Головна апаратна властивість NOR Flash полягає у фундаментальній **асиметрії між записом і стиранням**:
- **Читання (Read)** виконується побайтово з довільним доступом на повній частоті SPI (до 50–104 МГц). Читання не викликає деградації діелектрика і має нескінченний ресурс.
- **Програмування (Page Program)** змінює стан бітів **виключно з логічної одиниці в логічний нуль (`1 -> 0`)**. Процес полягає в інжекції електронів у плаваючий затвор під дією помірної напруги. Записати нуль поверх одиниці можна будь-якої миті, але перетворити хоча б один біт із `0` назад у `1` операцією запису фізично неможливо.
- **Стирання (Sector Erase)** скидає **всі біти цілого сектора 4096 байтів назад у логічну одиницю (`0xFF`)**. Для видалення електронів із затворів подається високовольтний імпульс (12–20 В), який викликає тунелювання Фаулера-Нордгейма. Цей імпульс поступово руйнує тонкий шар діоксиду кремнію навколо затвора.

Через деградацію діоксиду виробники гарантують лише близько **100 000 циклів стирання** для кожного сектора. Після вичерпання цього ресурсу комірки втрачають здатність утримувати заряд, з'являються биті біти та спотворення інформації.

#### Катастрофа наївного кільцевого буфера
У класичному RAM-буфері стан черги описується структурою:

:::tabs
```c
struct NaiveRing {
    uint32_t head;       /* Зміщення для запису */
    uint32_t tail;       /* Зміщення для читання */
    uint8_t  data[8192]; /* Кільцевий масив даних */
};
```
```cpp
struct NaiveRing {
    uint32_t head{0};                 // Зміщення для запису
    uint32_t tail{0};                 // Зміщення для читання
    std::array<uint8_t, 8192> data{}; // Кільцевий масив даних
};
```
:::

Якщо перенести цю модель у флеш-пам'ять і оновлювати зміщення `head` у перших байтах сектора `0` при кожній появі нового вимірювання (наприклад, раз на 5 секунд), то кожне оновлення покажчика вимагає:
1. Зчитати поточний сектор 4 КБ у RAM мікроконтролера.
2. Модифікувати значення `head`.
3. Виконати команду стирання сектора (Sector Erase) на флеші (витративши 50–100 мс часу та до 20 мА струму).
4. Записати 4 КБ назад на флеш.

Розрахуймо час до повної фізичної смерті кристала:
```
Кількість операцій стирання на добу = 86400 с / 5 с = 17 280 циклів/добу.
Час до досягнення 100 000 циклів = 100 000 / 17 280 ≈ 5.78 днів.
```
Через менш ніж шість днів роботи сектор `0` флеш-пам'яті буде незворотно спалений, а весь прилад перетвориться на сміття. Коефіцієнт посилення запису (англ. *Write Amplification Factor, WAF*) тут досягає катастрофічного значення: заради оновлення 4 байтів метаданих стирається й перезаписується 4096 байтів флешу (`WAF = 4096 / 4 = 1024`).

#### Апаратні команди та таймінги SPI NOR Flash
Робота з чіпом Flash відбувається через стандартний набір SPI-інструкцій:
- `0x06` — **Write Enable (WREN)**: встановлює апаратний прапорець `WEL` (Write Enable Latch) у регістрі стану чіпа. Без попереднього надсилання цієї команди будь-яка спроба запису або стирання буде проігнорована кремнієм.
- `0x05` — **Read Status Register 1 (RDSR)**: зчитує байт регістру стану. Молодший біт 0 (`BUSY` або `WIP` — Write In Progress) дорівнює `1`, доки чіп зайнятий виконанням внутрішнього циклу програмування або стирання.
- `0x20` — **Sector Erase (4 KB)**: стирає вказаний сектор за адресою. Операція триває від 40 до 200 мс.
- `0x02` — **Page Program (1–256 B)**: записує байти в межах поточної сторінки. Операція триває від 0.7 до 3.0 мс.
- `0x03` / `0x0B` — **Read Data / Fast Read**: пряме читання масиву байтів на частоті до 50–104 МГц.
- `0xB9` / `0xAB` — **Deep Power-Down / Release Deep Power-Down**: переведення мікросхеми в режим наднизького споживання (струм знижується з 15 мкА в Standby до 1 мкА в глибокому сні), що критично для приладів із живленням від автономних батарей.

Оскільки стирання сектора триває до 200 мс, блокуюче очікування прапорця `BUSY` у головному потоці неприпустиме: воно зірве таймінги високошвидкісних контурів опитування датчиків чи регулювання двигунів. Тому підготовка (стирання) наступного вільного сектора повинна виконуватися завчасно у фоновій низькопріоритетній задачі RTOS.

Саме тому надійний буфер на Flash повинен базуватися на **посекційному логовому розподілі** (англ. *Log-Structured Sector Ring*), де операція стирання виконується лише тоді, коли вичерпано весь фізичний об'єм сектора, а покажчики ніколи не перезаписують одні й ті самі комірки.

---

### Архітектура секційного кільцевого буфера (Sector-Ring FIFO)

Секційний кільцевий буфер виділяє у флеш-пам'яті неперервний діапазон із N фізичних секторів (наприклад, 256 секторів по 4 КБ = 1 МБ сховища). Кожен сектор розглядається як окрема неподільна ланка кільцевого ланцюга.

![Архітектура секційного кільцевого буфера на флеш-пам'яті](/root/course/embedded/bufer-na-fleshi/img/sector-ring-fifo.svg)
*Архітектура секційного кільцевого буфера: кільце секторів із монотонною нумерацією, активні сектори запису (Head) та вичитування (Tail), послідовне заповнення без фіксованих таблиць покажчиків.*

Кожен фізичний сектор у кільці перебуває в одному з чотирьох логічних станів:
- **FREE / ERASED (`0xFF`)** — сектор повністю стертий, заповнений байтами `0xFF` і готовий до запису нових даних.
- **HEAD (Active Write)** — сектор, у який просто зараз драйвер послідовно дописує нові вхідні повідомлення.
- **QUEUED / COMMITTED** — сектор, повністю заповнений зафіксованими повідомленнями, які очікують відправлення в мережу.
- **TAIL (Active Read)** — найстаріший сектор із накопиченими повідомленнями, з якого мережевий стек вичитує дані для відправлення на сервер.

#### Анатомія сектора
Кожен сектор починається зі структурованого **заголовка сектора (Sector Header)** фіксованого розміру (16 байтів), за яким слідує неперервний потік записів змінної або фіксованої довжини:

```
┌────────────────────────────────────────────────────────────────────────┐
│ СЕКТОР FLASH (4096 байтів)                                             │
├───────────────────┬───────────────────┬───────────────────┬────────────┤
│ Sector Header     │ Record #0         │ Record #1         │ Record #N  │
│ (16 байтів)       │ (Header + Data)   │ (Header + Data)   │ ...        │
└───────────────────┴───────────────────┴───────────────────┴────────────┘
```

Формат заголовка сектора:

:::tabs
```c
typedef struct __attribute__((packed)) {
    uint32_t magic;          /* Магічне число валідності сектора: 0x53454354 ("SECT") */
    uint32_t sector_seq;     /* Глобальний монотонний номер сектора (0, 1, 2, ...) */
    uint8_t  state_flags;    /* Прапорці стану сектора (0xFF -> 0xFE -> 0xFC -> 0x00) */
    uint8_t  reserved[3];    /* Вирівнювання до 4 байтів */
    uint32_t header_crc32;   /* Контрольна сума заголовка */
} flash_sector_header_t;
```
```cpp
struct SectorHeader {
    uint32_t magic{0x53454354U}; // ASCII "SECT"
    uint32_t sector_seq{0};       // Монотонний номер сектора
    uint8_t  state_flags{0xFFU};  // Стан: 0xFF -> 0xFE -> 0xFC -> 0x00
    std::array<uint8_t, 3> reserved{0, 0, 0};
    uint32_t header_crc32{0};
} __attribute__((packed));
```
:::

#### Анатомія запису (Record)
Кожне повідомлення, яке потрапляє в чергу, загортається у власний фрейм із заголовком фіксованої довжини та тілом корисного навантаження (англ. *Payload*):

:::tabs
```c
typedef struct __attribute__((packed)) {
    uint16_t record_magic;   /* Магічне число запису: 0x5243 ("RC") */
    uint16_t payload_len;    /* Довжина корисного навантаження в байтах */
    uint32_t record_seq;     /* Монотонний номер повідомлення */
    uint8_t  status_flag;    /* Атомарний прапорець транзакції: 0xFF -> 0xFE -> 0xFC -> 0x00 */
    uint8_t  priority;       /* Пріоритет: 0 = звичайна телеметрія, 1 = тривога/аварія */
    uint16_t reserved;       /* Резерв / прапорці стиснення */
    uint32_t payload_crc32;  /* CRC32 корисних даних для захисту від спотворень */
} flash_record_header_t;
```
```cpp
struct RecordHeader {
    uint16_t record_magic{0x5243U}; // ASCII "RC"
    uint16_t payload_len{0};
    uint32_t record_seq{0};
    uint8_t  status_flag{0xFFU};    // 0xFF -> 0xFE -> 0xFC -> 0x00
    uint8_t  priority{0};
    uint16_t reserved{0};
    uint32_t payload_crc32{0};
} __attribute__((packed));
```
:::

Правило розміщення записів усередині сектора просте: записи укладаються послідовно один за одним (англ. *Append-Only*). Якщо розмір чергового запису `(sizeof(flash_record_header_t) + payload_len)` перевищує залишок вільного місця у поточному Head-секторі, цей сектор закривається, драйвер переходить до наступного фізичного сектора `(head_sector_idx + 1) % TOTAL_SECTORS`, перевіряє, що він стертий, записує новий `Sector Header` з `sector_seq = prev_seq + 1`, і записує повідомлення на початок нового сектора. 

Завдяки цьому записи ніколи не розриваються між двома секторами, що усуває потребу у складних таблицях фрагментації.

---

### Атомарне фіксування транзакцій та стійкість до раптового знеструмлення

Найнебезпечніша ситуація для вбудованої системи — раптове зникнення живлення або скидання процесора в момент, коли по SPI передаються байти нового запису. Якщо система використовує просту схему «записав довжину і дані», знеструмлення посеред операції призведе до появи «розірваного запису» (англ. *Torn Write*). При наступному старті драйвер прочитає сміття, інтерпретує його як валідні дані, надішле на сервер спотворений пакет або взагалі зависне через некоректне значення довжини.

Для досягнення абсолютної стійкості до аварійного вимкнення живлення використовується **автомат станів на побітовому скиданні (State Transition Machine)**.

![Життєвий цикл байта статусу запису на Flash](/root/course/embedded/bufer-na-fleshi/img/record-state-machine.svg)
*Життєвий цикл байта статусу запису: перехід між станами здійснюється виключно скиданням окремих бітів 1 → 0 без необхідності попереднього стирання сектора.*

Розгляньмо, як змінюється байт `status_flag` у заголовку запису протягом його життя:

1. **Свіжий сектор (FREE / ERASED):**
   Уся область пам'яті заповнена байтами `0xFF` (`1111 1111b`).
2. **Резервування та запис тіла (IN_PROGRESS):**
   Драйвер готує структуру `flash_record_header_t`, де поле `status_flag` встановлено в `0xFE` (`1111 1110b`, скинуто біт 0). Драйвер записує заголовок і корисне навантаження в один або два виклики `Page Program`. 
   *Якщо живлення вимкнеться просто зараз*, під час наступного ввімкнення система побачить статус `0xFE` або пошкоджений CRC. Такий запис вважається незавершеним і безпечно ігнорується!
3. **Атомарний коміт (COMMITTED):**
   Після того як вся довжина корисних даних записана і перевірена, драйвер виконує запис рівно **одного байта** за адресою поля `status_flag`, записуючи туди значення `0xFC` (`1111 1100b`, скинуто біт 1). 
   Оскільки операція скидає біт із `1` в `0`, вона не вимагає стирання сектора і виконується апаратною флешкою гарантовано атомарно. Щойно біт 1 став нулем, запис офіційно вважається зафіксованим (Committed) і стає видимим для читача `Tail`.
4. **Підтвердження вичитування (CONSUMED / DELETED):**
   Коли мережевий стек вичитав повідомлення з буфера, передав його по MQTT/HTTP і отримав від сервера підтвердження прийому (ACK), драйвер перезаписує байт статусу значенням `0x00` (`0000 0000b`). Запис помічається як видалений.

#### Обмеження на часткове програмування сторінки (Page Program Disturb)
У специфікаціях сучасних мікросхем NOR Flash вказується параметр `NOP` (англ. *Number of Partial Program Cycles*) — максимальна кількість послідовних операцій програмування окремих байтів у межах однієї й тієї самої 256-байтної сторінки без проміжного стирання сектора. 

Для більшості індустріальних чіпів SPI Flash параметр NOP ≥ 4 (а для багатьох чіпів NOR Flash дозволено довільне побайтове програмування доти, доки біти змінюються лише з `1` в `0`). У нашій схемі кожен запис викликає рівно **дві** операції програмування:
1. Запис тіла запису зі статусом `0xFE`.
2. Запис байта підтвердження коміту `0xFC`.
Це повністю вкладається в паспорти надійності всіх провідних виробників (Winbond, Macronix, Micron, GigaDevice).

#### Алгоритм відновлення та монтування буфера при старті (Mount Recovery Scan)
Коли прилад вмикається після аварійного знеструмлення або перезавантаження, в оперативній пам'яті немає жодного покажчика. Драйвер виконує швидке сканування флеш-пам'яті:

```
Крок 1. Сканування заголовків усіх N секторів (читання 16 байтів на сектор).
        Для 256 секторів це лише 4096 байтів передачі по SPI (менше 1 мс).
Крок 2. Відбір секторів із валідним magic == 0x53454354 та валідним CRC заголовка.
Крок 3. Пошук Head та Tail:
        - Head Sector = сектор із максимальним монотонним номером sequence.
        - Tail Sector = сектор із мінімальним sequence серед тих, де є невичитані записи.
Крок 4. Сканування Head-сектора:
        - Драйвер крокує по записах від початку сектора.
        - Знаходить останній валідний запис зі статусом COMMITTED (0xFC).
        - Якщо натрапляє на запис зі статусом 0xFE або пошкодженим CRC32 (розірваний запис) — 
          драйвер перезаписує його статус нулями (0x00), анулюючи пошкоджений хвіст.
        - Встановлює вказівник вільного місця write_offset на перші байти 0xFF.
```

Така процедура гарантує детермінований старт за фіксований час без ризику втрати раніше зафіксованих даних.

---

### Політики вирівнювання зносу та деградація при переповненні сховища

Організація черги у вигляді ланцюга секторів забезпечує ідеальне кругове вирівнювання зносу (англ. *Wear Leveling*): кожен сектор стирається рівно один раз за повний оберт кільця.

Порахуймо реальний ресурс флеш-буфера для типового промислового датчика:
- Розмір виділеної пам'яті: **2 МБ (512 секторів по 4096 байтів)**.
- Розмір одного вимірювання: 48 байтів даних + 16 байтів заголовка = **64 байти**.
- Період опитування датчика: **10 секунд**.
- Швидкість генерації даних:
```
Швидкість = 64 байти / 10 с = 6.4 байта/с = 552 960 байтів/добу ≈ 540 КБ/добу.
```
- Час одного повного оберту буфера:
```
Час оберту = 2 097 152 байти / 552 960 байтів/добу ≈ 3.79 доби.
```
- Ресурс флеш-чіпа при гарантованих 100 000 циклах стирання на сектор:
```
Загальний термін служби = 100 000 циклів * 3.79 доби ≈ 379 000 діб ≈ 1038 років!
```
Навіть якщо датчик записуватиме дані щосекунди, ресурсу 2 МБ флешу вистачить на **понад 100 років** безперервної роботи.

#### Стратегії поведінки при переповненні буфера (Buffer Overflow)
Що відбувається, коли зв'язок відсутній тижнями, і кільцевий буфер заповнюється повністю (голова `Head` наздоганяє хвіст `Tail`)? Вибір політики визначається бізнес-вимогами до даних.

![Політики обробки переповнення кільцевого буфера](/root/course/embedded/bufer-na-fleshi/img/overflow-policies.svg)
*Політики переповнення буфера: витіснення найстаріших записів (FIFO Drop), блокування нових (LIFO Drop) та ізольоване мульти-кільце з гарантованим збереженням аварійних тривог.*

Існує три базові стратегії деградації:

1. **FIFO Drop (Drop Oldest / Ring Overwrite):**
   Коли новий запис не вміщується у вільні сектори, драйвер примусово просуває вказівник `Tail` уперед на один сектор, стирає найстаріший сектор і віддає його під новий `Head`.
   *Застосування:* моніторинг поточної телеметрії (температура, вологість, напруга живлення). Свіжі дані за останні три дні значно цінніші для оператора, ніж тритижневий масив застарілих чисел.

2. **LIFO / Tail Drop (Drop Newest / Preserving Initial Incident):**
   Коли буфер заповнений, драйвер відмовляється приймати нові вимірювання і відкидає їх, зберігаючи первинний накопичений зріз даних.
   *Застосування:* аналіз першопричин аварій (англ. *Root Cause Analysis*). Перші 10 000 подій з моменту аварії містять безпосередню причину катастрофи, тому їх категорично заборонено перезаписувати фоновим шумом.

3. **Пріоритетне мульти-кільце (Priority Multi-Ring Architecture):**
   Фізична флеш-пам'ять ділиться на два незалежні логічні кільцеві буфери:
   - **Кільце телеметрії (Regular Ring, 90% простору)** — працює за політикою *FIFO Drop*, забезпечуючи свіжість графіків.
   - **Кільце тривог та подій (Alarm Ring, 10% простору)** — зберігає спрацьовування кінцевиків, перевищення тиску, відкриття шафи. Це кільце ніколи не затирається автоматично і генерує критичну помилку, якщо пам'ять вичерпано.

#### Агрегація та ущільнення даних на льоту (In-place Data Downsampling)
Для систем із жорстким обмеженням пам'яті можливий гібридний підхід: коли зв'язку немає понад 24 години, фонова задача мікроконтролера вичитує з найстарішого сектора хвилинні вимірювання, обчислює для них агреговані значення (мінімум, максимум, середнє за 1 годину), записує один компактний агрегований запис в архівний сектор і стирає вихідний сектор. Це дозволяє скоротити обсяг застарілих спостережень у 60 разів без втрати ключових трендів.

---

### Повний драйвер енергонезалежної черги на C та C++

Розгляньмо закінчену, безпечну та високоефективну реалізацію Flash Ring Buffer. Драйвер спроєктовано за стандартом zero-allocation (жодних викликів `malloc` або динамічної пам'яті) і спирається на мінімальний апаратний рівень абстракції (HAL) для роботи з SPI Flash.

#### 1. Апаратний інтерфейс (Flash HAL) та структури даних

:::tabs
```c
/* flash_ring_buffer.h */
#ifndef FLASH_RING_BUFFER_H
#define FLASH_RING_BUFFER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FLASH_SECTOR_SIZE       4096U
#define FLASH_SECTOR_MAGIC      0x53454354U /* ASCII "SECT" */
#define FLASH_RECORD_MAGIC      0x5243U     /* ASCII "RC"   */

/* Прапорці життєвого циклу запису */
#define RECORD_STATUS_FREE        0xFFU
#define RECORD_STATUS_WRITING     0xFEU
#define RECORD_STATUS_COMMITTED   0xFCU
#define RECORD_STATUS_CONSUMED    0x00U

/* Результати операцій */
typedef enum {
    FLASH_RING_OK = 0,
    FLASH_RING_ERR_FULL,
    FLASH_RING_ERR_EMPTY,
    FLASH_RING_ERR_CORRUPTED,
    FLASH_RING_ERR_IO,
    FLASH_RING_ERR_INVALID_PARAM
} flash_ring_status_t;

/* Апаратні операції Flash HAL */
typedef struct {
    int (*read)(uint32_t addr, uint8_t *buf, size_t len);
    int (*write_page)(uint32_t addr, const uint8_t *buf, size_t len);
    int (*erase_sector)(uint32_t sector_addr);
} flash_hal_t;

/* Заголовок сектора (16 байтів) */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t sector_seq;
    uint8_t  state_flag;
    uint8_t  reserved[3];
    uint32_t header_crc32;
} flash_sector_hdr_t;

/* Заголовок запису (16 байтів) */
typedef struct __attribute__((packed)) {
    uint16_t record_magic;
    uint16_t payload_len;
    uint32_t record_seq;
    uint8_t  status_flag;
    uint8_t  priority;
    uint16_t reserved;
    uint32_t payload_crc32;
} flash_record_hdr_t;

/* Контекст кільцевого буфера */
typedef struct {
    flash_hal_t hal;
    uint32_t    start_addr;       /* Початкова фізична адреса у Flash */
    uint32_t    sector_count;     /* Загальна кількість виділених секторів */
    uint32_t    head_sector_idx;  /* Індекс активного сектора для запису (0..sector_count-1) */
    uint32_t    tail_sector_idx;  /* Індекс активного сектора для читання */
    uint32_t    head_offset;      /* Зміщення всередині Head-сектора для наступного запису */
    uint32_t    tail_offset;      /* Зміщення всередині Tail-сектора для читання */
    uint32_t    next_record_seq;  /* Монотонний лічильник повідомлень */
    uint32_t    next_sector_seq;  /* Монотонний лічильник секторів */
    bool        overwrite_on_full;/* true = FIFO Drop, false = блокування при переповненні */
} flash_ring_t;

/* Публічний API */
flash_ring_status_t flash_ring_init(flash_ring_t *ring, const flash_hal_t *hal, 
                                    uint32_t start_addr, uint32_t sector_count, 
                                    bool overwrite_on_full);

flash_ring_status_t flash_ring_push(flash_ring_t *ring, const uint8_t *payload, 
                                    uint16_t len, uint8_t priority);

flash_ring_status_t flash_ring_peek(flash_ring_t *ring, uint8_t *payload_buf, 
                                    uint16_t max_buf_len, uint16_t *out_len, 
                                    uint32_t *out_record_seq);

flash_ring_status_t flash_ring_commit_pop(flash_ring_t *ring);

#ifdef __cplusplus
}
#endif

#endif /* FLASH_RING_BUFFER_H */
```
```cpp
// FlashRingBuffer.hpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <concepts>

namespace embedded::storage {

inline constexpr uint32_t FlashSectorSize    = 4096U;
inline constexpr uint32_t FlashSectorMagic   = 0x53454354U; // ASCII "SECT"
inline constexpr uint16_t FlashRecordMagic   = 0x5243U;     // ASCII "RC"

enum class RecordStatus : uint8_t {
    Free      = 0xFFU,
    Writing   = 0xFEU,
    Committed = 0xFCU,
    Consumed  = 0x00U
};

enum class RingError {
    Full,
    Empty,
    Corrupted,
    IoError,
    InvalidParameter
};

struct SectorHeader {
    uint32_t               magic{FlashSectorMagic};
    uint32_t               sector_seq{0};
    uint8_t                state_flag{static_cast<uint8_t>(RecordStatus::Free)};
    std::array<uint8_t, 3> reserved{0, 0, 0};
    uint32_t               header_crc32{0};
} __attribute__((packed));

struct RecordHeader {
    uint16_t record_magic{FlashRecordMagic};
    uint16_t payload_len{0};
    uint32_t record_seq{0};
    uint8_t  status_flag{static_cast<uint8_t>(RecordStatus::Free)};
    uint8_t  priority{0};
    uint16_t reserved{0};
    uint32_t payload_crc32{0};
} __attribute__((packed));

// Концепт для апаратного драйвера SPI Flash
template <typename T>
concept FlashDriver = requires(T driver, uint32_t addr, const uint8_t* src, uint8_t* dst, size_t len) {
    { driver.read(addr, dst, len) } -> std::same_as<int>;
    { driver.write_page(addr, src, len) } -> std::same_as<int>;
    { driver.erase_sector(addr) } -> std::same_as<int>;
};

} // namespace embedded::storage
```
:::

#### 2. Реалізація базових операцій (Монтування, Push, Peek, Pop)

:::tabs
```c
/* flash_ring_buffer.c */
#include "flash_ring_buffer.h"
#include <string.h>

/* Проста еталонна реалізація CRC32 (IEEE 802.3) */
static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320U & (0 - (crc & 1)));
        }
    }
    return ~crc;
}

static uint32_t get_sector_addr(const flash_ring_t *ring, uint32_t sector_idx) {
    return ring->start_addr + (sector_idx * FLASH_SECTOR_SIZE);
}

/* Ініціалізація та сканування флешу для відновлення стану */
flash_ring_status_t flash_ring_init(flash_ring_t *ring, const flash_hal_t *hal, 
                                    uint32_t start_addr, uint32_t sector_count, 
                                    bool overwrite_on_full) {
    if (!ring || !hal || sector_count < 2) {
        return FLASH_RING_ERR_INVALID_PARAM;
    }

    ring->hal = *hal;
    ring->start_addr = start_addr;
    ring->sector_count = sector_count;
    ring->overwrite_on_full = overwrite_on_full;
    ring->next_record_seq = 1;
    ring->next_sector_seq = 1;

    uint32_t max_sec_seq = 0;
    uint32_t min_sec_seq = 0xFFFFFFFFU;
    int head_idx = -1;
    int tail_idx = -1;

    /* Фаза 1: Сканування заголовків усіх секторів */
    for (uint32_t i = 0; i < sector_count; i++) {
        flash_sector_hdr_t sec_hdr;
        uint32_t addr = get_sector_addr(ring, i);
        if (ring->hal.read(addr, (uint8_t*)&sec_hdr, sizeof(sec_hdr)) != 0) {
            return FLASH_RING_ERR_IO;
        }

        if (sec_hdr.magic == FLASH_SECTOR_MAGIC) {
            if (sec_hdr.sector_seq >= max_sec_seq) {
                max_sec_seq = sec_hdr.sector_seq;
                head_idx = (int)i;
            }
            if (sec_hdr.sector_seq <= min_sec_seq) {
                min_sec_seq = sec_hdr.sector_seq;
                tail_idx = (int)i;
            }
        }
    }

    /* Якщо жоден сектор не ініціалізовано — форматуємо сектор 0 */
    if (head_idx == -1) {
        ring->head_sector_idx = 0;
        ring->tail_sector_idx = 0;
        ring->head_offset = sizeof(flash_sector_hdr_t);
        ring->tail_offset = sizeof(flash_sector_hdr_t);

        ring->hal.erase_sector(get_sector_addr(ring, 0));
        flash_sector_hdr_t hdr = {
            .magic = FLASH_SECTOR_MAGIC,
            .sector_seq = 1,
            .state_flag = RECORD_STATUS_COMMITTED,
            .header_crc32 = 0
        };
        hdr.header_crc32 = calc_crc32((const uint8_t*)&hdr, sizeof(hdr) - 4);
        ring->hal.write_page(get_sector_addr(ring, 0), (const uint8_t*)&hdr, sizeof(hdr));
        ring->next_sector_seq = 2;
        return FLASH_RING_OK;
    }

    ring->head_sector_idx = (uint32_t)head_idx;
    ring->tail_sector_idx = (uint32_t)tail_idx;
    ring->next_sector_seq = max_sec_seq + 1;

    /* Фаза 2: Сканування Head-сектора для пошуку вільного зміщення */
    uint32_t cur_offset = sizeof(flash_sector_hdr_t);
    uint32_t head_base_addr = get_sector_addr(ring, ring->head_sector_idx);

    while (cur_offset + sizeof(flash_record_hdr_t) <= FLASH_SECTOR_SIZE) {
        flash_record_hdr_t rec;
        ring->hal.read(head_base_addr + cur_offset, (uint8_t*)&rec, sizeof(rec));

        if (rec.record_magic == 0xFFFFU && rec.status_flag == RECORD_STATUS_FREE) {
            /* Знайдено чисте місце для нових записів */
            break;
        }

        if (rec.record_magic == FLASH_RECORD_MAGIC) {
            if (rec.record_seq >= ring->next_record_seq) {
                ring->next_record_seq = rec.record_seq + 1;
            }
            cur_offset += sizeof(flash_record_hdr_t) + rec.payload_len;
        } else {
            /* Пошкоджений хвіст після знеструмлення — зупиняємо зміщення тут */
            break;
        }
    }
    ring->head_offset = cur_offset;
    ring->tail_offset = sizeof(flash_sector_hdr_t);

    return FLASH_RING_OK;
}

/* Додавання нового повідомлення в кільцевий буфер */
flash_ring_status_t flash_ring_push(flash_ring_t *ring, const uint8_t *payload, 
                                    uint16_t len, uint8_t priority) {
    if (!ring || !payload || len == 0) {
        return FLASH_RING_ERR_INVALID_PARAM;
    }

    uint32_t total_record_size = sizeof(flash_record_hdr_t) + len;
    if (total_record_size > (FLASH_SECTOR_SIZE - sizeof(flash_sector_hdr_t))) {
        return FLASH_RING_ERR_INVALID_PARAM; /* Повідомлення більше за вільний розмір сектора */
    }

    /* Перевірка: чи поміщається запис у поточний Head-сектор */
    if (ring->head_offset + total_record_size > FLASH_SECTOR_SIZE) {
        uint32_t next_head = (ring->head_sector_idx + 1) % ring->sector_count;

        /* Перевірка на переповнення кільця */
        if (next_head == ring->tail_sector_idx) {
            if (!ring->overwrite_on_full) {
                return FLASH_RING_ERR_FULL;
            }
            /* FIFO Drop: примусово зміщуємо Tail і стираємо найстаріший сектор */
            ring->tail_sector_idx = (ring->tail_sector_idx + 1) % ring->sector_count;
            ring->tail_offset = sizeof(flash_sector_hdr_t);
        }

        /* Підготовка нового сектора */
        ring->head_sector_idx = next_head;
        uint32_t sec_addr = get_sector_addr(ring, ring->head_sector_idx);
        ring->hal.erase_sector(sec_addr);

        flash_sector_hdr_t sec_hdr = {
            .magic = FLASH_SECTOR_MAGIC,
            .sector_seq = ring->next_sector_seq++,
            .state_flag = RECORD_STATUS_COMMITTED,
            .header_crc32 = 0
        };
        sec_hdr.header_crc32 = calc_crc32((const uint8_t*)&sec_hdr, sizeof(sec_hdr) - 4);
        ring->hal.write_page(sec_addr, (const uint8_t*)&sec_hdr, sizeof(sec_hdr));
        ring->head_offset = sizeof(flash_sector_hdr_t);
    }

    /* Формування заголовка запису зі статусом WRITING (0xFE) */
    flash_record_hdr_t rec_hdr = {
        .record_magic = FLASH_RECORD_MAGIC,
        .payload_len = len,
        .record_seq = ring->next_record_seq++,
        .status_flag = RECORD_STATUS_WRITING,
        .priority = priority,
        .reserved = 0,
        .payload_crc32 = calc_crc32(payload, len)
    };

    uint32_t rec_addr = get_sector_addr(ring, ring->head_sector_idx) + ring->head_offset;

    /* Запис заголовка та пейлоаду */
    ring->hal.write_page(rec_addr, (const uint8_t*)&rec_hdr, sizeof(rec_hdr));
    ring->hal.write_page(rec_addr + sizeof(rec_hdr), payload, len);

    /* Атомарний коміт: скидання статусу в 0xFC */
    uint8_t commit_val = RECORD_STATUS_COMMITTED;
    uint32_t status_addr = rec_addr + offsetof(flash_record_hdr_t, status_flag);
    ring->hal.write_page(status_addr, &commit_val, 1);

    ring->head_offset += total_record_size;
    return FLASH_RING_OK;
}

/* Підглядання (Peek) найстарішого непереданого повідомлення */
flash_ring_status_t flash_ring_peek(flash_ring_t *ring, uint8_t *payload_buf, 
                                    uint16_t max_buf_len, uint16_t *out_len, 
                                    uint32_t *out_record_seq) {
    if (!ring || !payload_buf || !out_len) {
        return FLASH_RING_ERR_INVALID_PARAM;
    }

    while (1) {
        if (ring->tail_sector_idx == ring->head_sector_idx && 
            ring->tail_offset >= ring->head_offset) {
            return FLASH_RING_ERR_EMPTY;
        }

        uint32_t rec_addr = get_sector_addr(ring, ring->tail_sector_idx) + ring->tail_offset;
        flash_record_hdr_t rec_hdr;
        ring->hal.read(rec_addr, (uint8_t*)&rec_hdr, sizeof(rec_hdr));

        /* Якщо сектор закінчився — переходимо до наступного сектора */
        if (rec_hdr.record_magic != FLASH_RECORD_MAGIC || 
            ring->tail_offset + sizeof(rec_hdr) > FLASH_SECTOR_SIZE) {
            if (ring->tail_sector_idx == ring->head_sector_idx) {
                return FLASH_RING_ERR_EMPTY;
            }
            ring->tail_sector_idx = (ring->tail_sector_idx + 1) % ring->sector_count;
            ring->tail_offset = sizeof(flash_sector_hdr_t);
            continue;
        }

        /* Якщо запис уже вичитаний (0x00) — пропускаємо його */
        if (rec_hdr.status_flag == RECORD_STATUS_CONSUMED) {
            ring->tail_offset += sizeof(flash_record_hdr_t) + rec_hdr.payload_len;
            continue;
        }

        /* Якщо запис валідний і зафіксований (0xFC) */
        if (rec_hdr.status_flag == RECORD_STATUS_COMMITTED) {
            if (rec_hdr.payload_len > max_buf_len) {
                return FLASH_RING_ERR_INVALID_PARAM;
            }

            ring->hal.read(rec_addr + sizeof(rec_hdr), payload_buf, rec_hdr.payload_len);

            /* Перевірка цілісності даних */
            uint32_t actual_crc = calc_crc32(payload_buf, rec_hdr.payload_len);
            if (actual_crc != rec_hdr.payload_crc32) {
                /* Отруйне повідомлення: помічаємо видаленим і йдемо далі */
                uint8_t consume_val = RECORD_STATUS_CONSUMED;
                ring->hal.write_page(rec_addr + offsetof(flash_record_hdr_t, status_flag), 
                                     &consume_val, 1);
                ring->tail_offset += sizeof(flash_record_hdr_t) + rec_hdr.payload_len;
                continue;
            }

            *out_len = rec_hdr.payload_len;
            if (out_record_seq) *out_record_seq = rec_hdr.record_seq;
            return FLASH_RING_OK;
        }

        /* Якщо статус WRITING (0xFE) або пошкоджений */
        ring->tail_offset += sizeof(flash_record_hdr_t) + rec_hdr.payload_len;
    }
}

/* Підтвердження успішного відправлення: маркування запису як CONSUMED */
flash_ring_status_t flash_ring_commit_pop(flash_ring_t *ring) {
    if (!ring) return FLASH_RING_ERR_INVALID_PARAM;

    uint32_t rec_addr = get_sector_addr(ring, ring->tail_sector_idx) + ring->tail_offset;
    flash_record_hdr_t rec_hdr;
    ring->hal.read(rec_addr, (uint8_t*)&rec_hdr, sizeof(rec_hdr));

    if (rec_hdr.record_magic == FLASH_RECORD_MAGIC) {
        uint8_t consumed = RECORD_STATUS_CONSUMED;
        ring->hal.write_page(rec_addr + offsetof(flash_record_hdr_t, status_flag), &consumed, 1);
        ring->tail_offset += sizeof(flash_record_hdr_t) + rec_hdr.payload_len;
        return FLASH_RING_OK;
    }

    return FLASH_RING_ERR_CORRUPTED;
}
```
```cpp
// FlashRingQueue.hpp
#pragma once

#include "FlashRingBuffer.hpp"
#include <optional>
#include <algorithm>

namespace embedded::storage {

template <FlashDriver Driver, uint32_t SectorCount, bool OverwriteOnFull = true>
class FlashRingQueue {
public:
    explicit FlashRingQueue(Driver& driver, uint32_t start_addr)
        : driver_(driver), start_addr_(start_addr) {}

    std::expected<void, RingError> init() noexcept {
        uint32_t max_seq = 0;
        int head = -1, tail = -1;

        for (uint32_t i = 0; i < SectorCount; ++i) {
            SectorHeader hdr{};
            if (driver_.read(get_sector_addr(i), reinterpret_cast<uint8_t*>(&hdr), sizeof(hdr)) != 0) {
                return std::unexpected(RingError::IoError);
            }
            if (hdr.magic == FlashSectorMagic) {
                if (hdr.sector_seq >= max_seq) {
                    max_seq = hdr.sector_seq;
                    head = static_cast<int>(i);
                }
                if (tail == -1 || hdr.sector_seq < next_sector_seq_) {
                    tail = static_cast<int>(i);
                }
            }
        }

        if (head == -1) {
            head_idx_ = tail_idx_ = 0;
            head_offset_ = tail_offset_ = sizeof(SectorHeader);
            format_sector(0, 1);
            next_sector_seq_ = 2;
            return {};
        }

        head_idx_ = static_cast<uint32_t>(head);
        tail_idx_ = static_cast<uint32_t>(tail);
        next_sector_seq_ = max_seq + 1;
        recover_head_offset();
        return {};
    }

    std::expected<void, RingError> push(std::span<const uint8_t> payload, uint8_t priority = 0) noexcept {
        const uint32_t rec_size = sizeof(RecordHeader) + static_cast<uint32_t>(payload.size());
        if (rec_size > (FlashSectorSize - sizeof(SectorHeader))) {
            return std::unexpected(RingError::InvalidParameter);
        }

        if (head_offset_ + rec_size > FlashSectorSize) {
            const uint32_t next_head = (head_idx_ + 1) % SectorCount;
            if (next_head == tail_idx_) {
                if constexpr (!OverwriteOnFull) {
                    return std::unexpected(RingError::Full);
                }
                tail_idx_ = (tail_idx_ + 1) % SectorCount;
                tail_offset_ = sizeof(SectorHeader);
            }
            head_idx_ = next_head;
            format_sector(head_idx_, next_sector_seq_++);
            head_offset_ = sizeof(SectorHeader);
        }

        RecordHeader rec{
            .record_magic = FlashRecordMagic,
            .payload_len = static_cast<uint16_t>(payload.size()),
            .record_seq = next_record_seq_++,
            .status_flag = static_cast<uint8_t>(RecordStatus::Writing),
            .priority = priority,
            .reserved = 0,
            .payload_crc32 = compute_crc(payload)
        };

        const uint32_t rec_addr = get_sector_addr(head_idx_) + head_offset_;
        driver_.write_page(rec_addr, reinterpret_cast<const uint8_t*>(&rec), sizeof(rec));
        driver_.write_page(rec_addr + sizeof(rec), payload.data(), payload.size());

        // Атомарна фіксація (коміт)
        const uint8_t commit_val = static_cast<uint8_t>(RecordStatus::Committed);
        driver_.write_page(rec_addr + offsetof(RecordHeader, status_flag), &commit_val, 1);

        head_offset_ += rec_size;
        return {};
    }

    struct PeekResult {
        uint32_t record_seq;
        uint16_t payload_len;
    };

    std::expected<PeekResult, RingError> peek(std::span<uint8_t> out_buf) noexcept {
        while (true) {
            if (tail_idx_ == head_idx_ && tail_offset_ >= head_offset_) {
                return std::unexpected(RingError::Empty);
            }

            const uint32_t addr = get_sector_addr(tail_idx_) + tail_offset_;
            RecordHeader rec{};
            driver_.read(addr, reinterpret_cast<uint8_t*>(&rec), sizeof(rec));

            if (rec.record_magic != FlashRecordMagic || tail_offset_ + sizeof(rec) > FlashSectorSize) {
                if (tail_idx_ == head_idx_) return std::unexpected(RingError::Empty);
                tail_idx_ = (tail_idx_ + 1) % SectorCount;
                tail_offset_ = sizeof(SectorHeader);
                continue;
            }

            if (rec.status_flag == static_cast<uint8_t>(RecordStatus::Consumed)) {
                tail_offset_ += sizeof(RecordHeader) + rec.payload_len;
                continue;
            }

            if (rec.status_flag == static_cast<uint8_t>(RecordStatus::Committed)) {
                if (out_buf.size() < rec.payload_len) {
                    return std::unexpected(RingError::InvalidParameter);
                }
                driver_.read(addr + sizeof(rec), out_buf.data(), rec.payload_len);
                if (compute_crc(out_buf.subspan(0, rec.payload_len)) != rec.payload_crc32) {
                    mark_consumed(addr);
                    tail_offset_ += sizeof(RecordHeader) + rec.payload_len;
                    continue;
                }
                return PeekResult{rec.record_seq, rec.payload_len};
            }
            tail_offset_ += sizeof(RecordHeader) + rec.payload_len;
        }
    }

    std::expected<void, RingError> commit_pop() noexcept {
        const uint32_t addr = get_sector_addr(tail_idx_) + tail_offset_;
        RecordHeader rec{};
        driver_.read(addr, reinterpret_cast<uint8_t*>(&rec), sizeof(rec));
        if (rec.record_magic == FlashRecordMagic) {
            mark_consumed(addr);
            tail_offset_ += sizeof(RecordHeader) + rec.payload_len;
            return {};
        }
        return std::unexpected(RingError::Corrupted);
    }

private:
    Driver&  driver_;
    uint32_t start_addr_{0};
    uint32_t head_idx_{0};
    uint32_t tail_idx_{0};
    uint32_t head_offset_{sizeof(SectorHeader)};
    uint32_t tail_offset_{sizeof(SectorHeader)};
    uint32_t next_record_seq_{1};
    uint32_t next_sector_seq_{1};

    [[nodiscard]] constexpr uint32_t get_sector_addr(uint32_t idx) const noexcept {
        return start_addr_ + (idx * FlashSectorSize);
    }

    void format_sector(uint32_t idx, uint32_t seq) noexcept {
        const uint32_t addr = get_sector_addr(idx);
        driver_.erase_sector(addr);
        SectorHeader hdr{
            .magic = FlashSectorMagic,
            .sector_seq = seq,
            .state_flag = static_cast<uint8_t>(RecordStatus::Committed),
            .reserved = {0, 0, 0},
            .header_crc32 = 0
        };
        hdr.header_crc32 = compute_crc(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr) - 4));
        driver_.write_page(addr, reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr));
    }

    void mark_consumed(uint32_t rec_addr) noexcept {
        const uint8_t consumed = static_cast<uint8_t>(RecordStatus::Consumed);
        driver_.write_page(rec_addr + offsetof(RecordHeader, status_flag), &consumed, 1);
    }

    void recover_head_offset() noexcept {
        uint32_t offset = sizeof(SectorHeader);
        const uint32_t base = get_sector_addr(head_idx_);
        while (offset + sizeof(RecordHeader) <= FlashSectorSize) {
            RecordHeader rec{};
            driver_.read(base + offset, reinterpret_cast<uint8_t*>(&rec), sizeof(rec));
            if (rec.record_magic == 0xFFFFU && rec.status_flag == static_cast<uint8_t>(RecordStatus::Free)) {
                break;
            }
            if (rec.record_magic == FlashRecordMagic) {
                next_record_seq_ = std::max(next_record_seq_, rec.record_seq + 1);
                offset += sizeof(RecordHeader) + rec.payload_len;
            } else {
                break;
            }
        }
        head_offset_ = offset;
        tail_offset_ = sizeof(SectorHeader);
    }

    static uint32_t compute_crc(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (const uint8_t b : data) {
            crc ^= b;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & (0 - (crc & 1)));
            }
        }
        return ~crc;
    }
};

} // namespace embedded::storage
```
:::

#### 3. Патерн безпечної відправки повідомлень (Peek -> Send -> Commit/Pop)
Критична перевага розділення операцій `peek()` та `commit_pop()` полягає у дотриманні гарантії доставки **щонайменше один раз (At-Least-Once Delivery)**:

:::tabs
```c
/* Приклад використання в задачі мережевої синхронізації */
void telemetry_sync_task(flash_ring_t *ring, network_client_t *net) {
    uint8_t payload[256];
    uint16_t len = 0;
    uint32_t seq = 0;

    while (1) {
        /* 1. Підглядаємо найстаріше повідомлення без видалення */
        flash_ring_status_t status = flash_ring_peek(ring, payload, sizeof(payload), &len, &seq);
        if (status == FLASH_RING_ERR_EMPTY) {
            vTaskDelay(pdMS_TO_TICKS(1000)); /* Черга порожня — чекаємо */
            continue;
        }

        /* 2. Відправляємо пакет по мережі з таймаутом */
        int net_res = network_send_packet(net, payload, len);
        if (net_res == 0) {
            /* 3. Тільки після успішного ACK від сервера видаляємо запис з Flash */
            flash_ring_commit_pop(ring);
        } else {
            /* Помилка мережі: робимо експоненційний відступ, запис залишається в черзі */
            vTaskDelay(pdMS_TO_TICKS(5000));
        }
    }
}
```
```cpp
// Приклад використання в C++ потоці синхронізації
template <embedded::storage::FlashDriver Driver, uint32_t N>
void sync_telemetry_loop(embedded::storage::FlashRingQueue<Driver, N>& queue, NetworkClient& net) {
    std::array<uint8_t, 256> payload_buffer{};

    while (true) {
        auto peek_res = queue.peek(payload_buffer);
        if (!peek_res.has_value()) {
            if (peek_res.error() == embedded::storage::RingError::Empty) {
                sleep_for(std::chrono::seconds(1));
                continue;
            }
            break;
        }

        const auto payload_span = std::span{payload_buffer.data(), peek_res->payload_len};
        if (net.send_packet(payload_span)) {
            // ACK отримано: фіксуємо вилучення з черги
            queue.commit_pop();
        } else {
            // Обрив зв'язку: експоненційний відступ
            sleep_for(std::chrono::seconds(5));
        }
    }
}
```
:::

Якщо живлення приладу зникне просто посеред виклику `network_send_packet()`, після перезавантаження драйвер знову прочитає цей самий запис під час наступного `peek()` і повторно відправить його на сервер. Сервер, завдяки наявності поля `record_seq`, виконає дедуплікацію пакета за принципом ідемпотентності.

---

### Крайові випадки, апаратні пастки та діагностика

Навіть ідеально вивірений алгоритм логування може дати збій, якщо не враховувати апаратну специфіку зовнішніх мікросхем Flash.

#### 1. Загортання сторінки (Page Wrap-Around Trap)
Усі мікросхеми SPI NOR Flash мають апаратний внутрішній буфер запису розміром рівно 256 байтів. Якщо ви надішлете команду `Page Program` на 64 байти, починаючи з адреси `0x0000FE` (тобто за 2 байти до кінця сторінки), мікросхема запише перші 2 байти за адресами `0x0000FE` та `0x0000FF`, а решту 62 байти **запише не в наступну сторінку, а загорне на початок поточної (`0x000000`..`0x00003D`)**, безповоротно затерши власний заголовок сектора!

*Правило захисту:* Низькорівневий HAL-драйвер запису `write_page` зобов'язаний самостійно розбивати будь-яку транзакцію на шматки, які ніколи не перетинають 256-байтну межу сторінки (`addr & ~0xFFU`).

#### 2. Просідання напруги та поріг апаратного скидання (Brownout Reset vs Flash Vmin)
Більшість мікроконтролерів (STM32, ESP32, nRF52) здатні виконувати код при напрузі живлення аж до 1.7–1.8 В. Натомість більшість чіпів SPI Flash (наприклад, Winbond W25QxxJV) вимагають мінімальної напруги **2.7 В** (або 2.3 В для серій низької напруги). 

Якщо при розряджанні батареї напруга падає до 2.2 В, а в мікроконтролері не налаштовано апаратний детектор просідання напруги (BOR, англ. *Brownout Reset*), контролер продовжує виконувати код і надсилає команди запису по SPI. Flash-пам'ять у цей момент перебуває у непередбачуваному стані: внутрішній помповий перетворювач високої напруги не здатний пробити затвор, запис завершується помилкою або пошкоджує сусідні комірки.

*Правило захисту:* Завжди конфігурувати апаратний BOR мікроконтролера на поріг, вищий за мінімальну паспортну напругу чіпа Flash (типово 2.8–2.9 В). При досягненні цього порогу процесор повинен бути негайно утриманий у стані апаратного скидання.

#### 3. Апаратний прапорець Write Enable (WEL) та біти захисту секторів
Перед кожною операцією програмування чи стирання на чіп Flash необхідно надсилати команду `0x06` (`Write Enable`) і перевіряти біт `WEL` у регістрі стану (Status Register 1). Якщо шина SPI шумить, команда `WREN` може бути спотворена. Запис без перевірки `WEL` призведе до тихого ігнорування операції флешкою.

Крім того, після скидання живлення регістри блокування (Block Protect Bits `BP0..BP3`) повинні бути апаратно сконфігуровані в нуль, інакше спроба очистити сектор викличе відмову.

#### 4. Обробка «отруйного повідомлення» (Poison Pill Packet)
Якщо окремий запис зазнав фізичного пошкодження бітів на флеші (наприклад, через радіаційне випромінювання або деградацію комірки), його CRC32 перестане збігатися під час виклику `peek()`. Якщо драйвер у відповідь на помилку CRC просто поверне код помилки й залишить вказівник `tail_offset` на місці, мережевий стек зациклиться, намагаючись нескінченно перечитувати той самий битий пакет і блокуючи всю чергу відправлення.

*Правило захисту:* При виявленні невідповідності CRC32 драйвер автоматично маркує статус пошкодженого запису як `0x00` (`CONSUMED / INVALID`), збільшує діагностичний лічильник помилок та негайно переходить до наступного запису черги.

---

### Підсумкова архітектурна матриця

| Характеристика | Наївний буфер (FAT/RAM style) | Sector-Ring FIFO (Дана архітектура) |
| :--- | :--- | :--- |
| **Знос Flash (WAF)** | Катастрофічний (WAF = 100–1000) | Ідеальний мінімум (WAF ≈ 1.02) |
| **Термін служби 2 МБ Flash** | 5–10 днів | 100–800 років |
| **Стійкість до знеструмлення** | Вразливий до пошкодження метаданих | 100% атомарність (скидання бітів `1 -> 0`) |
| **Використання RAM** | 4–16 КБ (буфери секторів і таблиці) | < 128 байтів (лише індекси й зміщення) |
| **Час старту пристрою** | Повільне монтування FS | < 1 мс (сканування 16 Б заголовків секторів) |
| **Політика переповнення** | Зависання / помилка виділення місця | FIFO Drop / LIFO Drop / Priority Multi-Ring |
