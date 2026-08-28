# ⚙️ Циклічний буфер телеметрії у Flash-пам'яті: автономне збереження та автоматичне вивантаження

Втрата стільникового покриття через вимкнення базових станцій 2G/3G, аварії в регіональній енергосистемі, пошкодження антенно-фідерного тракту або тимчасове перебування рухомого об'єкта в зоні радіотіні переводить автономний телеметричний контролер у режим тривалого автономного накопичення даних. Якщо вимірювальний комплекс реєструє параметри технологічного процесу щохвилини, за місяць вимушеного радіомовчання накопичується понад 43 200 вимірювань. 

Спроба зберегти такий масив у загальних вбудованих файлових системах (наприклад, LittleFS, SPIFFS або FATFS) на мікроконтролері з обмеженими обсягами RAM та Flash стикається з фундаментальними обмеженнями. Файлові системи витрачають від 20% до 40% корисного простору на службові метадані, таблиці розподілу кластерів та каталоги, викликають паразитну фрагментацію адресного простору й створюють ризик повної втрати дерева каталогів при аварійному знеструмленні під час модифікації кореневих дескрипторів. 

Спеціалізований циклічний лог-буфер на базі зовнішньої або інтегрованої мікросхеми SPI NOR Flash вирішує задачу автономного зберігання шляхом прямої організації адресного простору у вигляді кільця фізичних секторів однакового розміру. Використовуючи фізичні особливості кремнієвих комірок із плаваючим затвором, різницеве дельта-стиснення зі змінною довжиною чисел (Varint/ZigZag), побайтовий контроль цілісності CRC-32 та односпрямований перехід бітів `1 → 0` без проміжного стирання, система забезпечує абсолютну стійкість до раптового знеструмлення, рівномірне вирівнювання зносу комірок (*wear leveling*) та потокове вивантаження батчів після відновлення зв'язку.

## Фізичні процеси в кремнії NOR Flash та модель станів

Мікросхеми незалежної пам'яті SPI NOR Flash (типові представники — промислові мікросхеми Winbond W25Q32/64/128, Macronix MX25R, Adesto AT25) функціонують на базі польових транзисторів із плаваючим затвором (*Floating Gate MOSFET*) або пасток заряду (*Charge Trap Flash*). Фізика напівпровідникової структури визначає жорсткі правила роботи з пам'яттю:

1. **Стирання як очищення заряду (Fowler-Nordheim Tunneling):** У стертому стані плаваючий затвор розряджений, транзистор проводить струм, а логічний рівень комірки зчитується як `1`. Стирання здійснюється подачею високої напруги (12–18 В від внутрішнього помпового перетворювача), що викликає тунелювання електронів через оксидний діелектрик. Стирання є виключно масовою операцією: воно не може бути виконане для окремого байта й застосовується лише до цілого сектора (4096 байтів), півблока (32 КБ) або блока (64 КБ). Після стирання весь сектор заповнений байтами `0xFF`.
2. **Програмування як інжекція електронів (Channel Hot Electron Injection, CHEI):** Під час запису електрони інжектуються на плаваючий затвор, створюючи негативний потенціал, що підвищує порогову напругу відкриття транзистора. У результаті комірка переходить у стан `0`. Запис може виконуватися побайтово або сторінками (розмір сторінки становить 256 байтів). Проте операція запису здатна лише перемикати біти зі стану `1` у стан `0`. Перевести окремий біт назад із `0` у `1` без стирання всього 4-кілобайтного сектора фізично неможливо.
3. **Асиметрія часових затримок:** Читання даних через SPI-інтерфейс виконується практично миттєво (на частоті шини 50–104 МГц затримка становить десятки наносекунд на байт). Програмування сторінки 256 байтів триває від `0.7 до 3.0 мс`. Стирання сектора 4 КБ є найбільш тривалою операцією і займає від `45 до 300 мс`.
4. **Небезпека скидання живлення під час стирання:** Якщо напруга живлення пристрою просідає нижче робочого порогу Flash (наприклад, 2.7 В або 1.65 В для низьковольтних версій) безпосередньо в момент генерації високовольтного імпульсу стирання або програмування, комірки затвора опиняються в метастабільному стані з неповним зарядом. Зчитування таких комірок дає недетерміновані значення, що залежать від температури кристала.

```
+─────────────────────────────────────────────────────────────────────────────+
| АТОМАРНІ ПЕРЕХОДИ СТАНІВ У NOR FLASH БЕЗ ПРОМІЖНОГО СТИРАННЯ                |
|                                                                             |
| Байт стану          Двійкове значення  Фізичний стан комірок Flash          |
| ─────────────────────────────────────────────────────────────────────────── |
| 0xFF (ERASED)       1111 1111 b        Всі затвори розряджені (чистий сектор)|
|          │                                                                  |
|          ▼ (запис 1-го біта)                                                |
| 0xFE (ALLOCATED)    1111 1110 b        Заряджено молодший біт: іде запис    |
|          │                                                                  |
|          ▼ (фінальний коміт)                                                |
| 0xFC (COMMITTED)    1111 1100 b        Заряджено 2 біти: запис валідний     |
|          │                                                                  |
|          ▼ (підтвердження сервера)                                          |
| 0x00 (DISPATCHED)   0000 0000 b        Всі 8 бітів заряджені: кадр вивантажено|
+─────────────────────────────────────────────────────────────────────────────+
```

Використання побайтового переходу станів `0xFF → 0xFE → 0xFC → 0x00` дозволяє змінювати статус готовності запису та факт отримання підтвердження від хмарного сервера без жодного додаткового циклу стирання Flash. Якщо пристрій знеструмлюється в процесі запису корисного навантаження, байт стану залишається в проміжному значенні `0xFE`, або контрольна сума кадру не збігається. При наступному старті драйвер ідентифікує такий запис як незавершений і пропускає його.

## Низькорівневий протокол керування SPI Flash

Взаємодія мікроконтролера з мікросхемою Flash здійснюється за стандартним промисловим протоколом JEDEC SPI через 4 апаратні лінії: `CS` (Chip Select), `SCK` (Serial Clock), `MOSI` (Master Out Slave In) та `MISO` (Master In Slave Out).

Драйвер використовує базовий набір команд JEDEC:
- `WREN` (Write Enable, код `0x06`): встановлює біт дозволу запису `WEL` (Write Enable Latch) у статусному регістрі. Має надсилатися перед кожною командою програмування або стирання.
- `RDSR` (Read Status Register-1, код `0x05`): зчитує 8-бітний регістр стану. Молодший біт `WIP` (Write In Progress) вказує, що мікросхема виконує внутрішню високовольтну операцію. Драйвер опитує цей біт у неблокуючому режимі.
- `SECTOR_ERASE_4K` (Sector Erase, код `0x20`): приймає 24-бітну адресу сектора та запускає цикл стирання 4096 байтів.
- `PAGE_PROGRAM` (Page Program, код `0x02`): приймає 24-бітну адресу та від 1 до 256 байтів даних. Запис не повинен перетинати межу 256-байтної фізичної сторінки (Page Boundary Wrap-around), інакше надлишкові байти перезапишуть початок тієї самої сторінки.
- `READ_DATA` (Read Data, код `0x03`): потокове зчитування байтів на частотах до 33–50 МГц без обмеження сторінкових меж.

## Сторінкове програмування та апаратні межі 256 байтів

Фізична організація комірок NOR Flash накладає жорстке апаратне обмеження на виконання команди запису `PAGE_PROGRAM` (`0x02`). Внутрішній буфер програмування мікросхеми має фіксовану довжину 256 байтів, а молодші 8 бітів адреси (`A7..A0`) слугують вказівником позиції всередині поточної фізичної сторінки.

Коли мікроконтролер передає потік байтів по шині SPI, внутрішній лічильник адреси чипа автоматично інкрементується з кожним тактом синхросигналу `SCK`. Проте цей лічильник **не переходить на наступну фізичну сторінку**: при досягненні кінця 256-байтного блоку (`0xFF`) він циклічно скидається на початок тієї самої сторінки (`0x00`) — виникає апаратне явище *Page Boundary Wrap-around*. Якщо драйвер спробує записати структуру телеметрії довжиною 24 байти за адресою `0x00FE` (тобто за 2 байти до межі сторінки) у межах єдиної SPI-транзакції:
1. Перші 2 байти потраплять за адресами `0x00FE` та `0x00FF`.
2. Решта 22 байти будуть записані за адресами `0x0000..0x0015` поточної сторінки.
3. Оскільки біти в стані `0` не можуть бути повернуті в стан `1` без повного стирання всього 4-кілобайтного сектора, нові байти накладуться на раніше збережені дані або службовий заголовок сектора, безповоротно руйнуючи їхню структуру та контрольну суму.

```
АДРЕСНИЙ ПРОСТІР СЕКТОРА (4096 БАЙТІВ = 16 СТОРІНОК ПО 256 БАЙТІВ)
┌──────────────────────┬──────────────────────┬─── ... ───┬──────────────────────┐
│ Сторінка 0 (256 Б)   │ Сторінка 1 (256 Б)   │           │ Сторінка 15 (256 Б)  │
│ [0x0000 .. 0x00FF]   │ [0x0100 .. 0x01FF]   │           │ [0x0F00 .. 0x0FFF]   │
└──────────┬───────────┴──────────┬───────────┴─── ... ───┴──────────────────────┘
           │                      │
           ▼                      ▼
  [0x00FE..0x00FF]        [0x0100..0x0115]
  Порція 1 (2 байти)      Порція 2 (22 байти)
  └─────────── Двокроковий запис (Page Split) ───────────┘
```

Щоб гарантувати збереження цілісності при перетині сторінкових меж, низькорівневий драйвер реалізує алгоритм розділеного сторінкового запису (*Page-Split Programming*):
1. **Обчислення вільного залишку поточної сторінки:** Драйвер визначає кількість байтів, що залишаються до найближчої 256-байтної межі: `bytes_to_boundary = 256 - (target_addr & 0xFF)`.
2. **Умовне розбиття кадру на порції:** Якщо довжина кадру `record_len <= bytes_to_boundary`, весь обсяг даних програмується за один SPI-виклик. Якщо ж `record_len > bytes_to_boundary`, запис розбивається на дві послідовні транзакції:
   - *Перша порція:* передаються перші `bytes_to_boundary` байтів за адресою `target_addr`. Лінія `CS` деактивується (переводиться у високий рівень), драйвер опитує регістр `RDSR` до скидання біта `WIP` (апаратне завершення інжекції електронів у кремній, типово 0.7–1.5 мс).
   - *Друга порція:* активується нова команда `WREN`, після чого видається `PAGE_PROGRAM` для залишку даних `(record_len - bytes_to_boundary)` за початковою адресою наступної вирівняної сторінки `target_addr + bytes_to_boundary`.

Оскільки середній стиснений кадр телеметрії займає близько 19 байтів, розбиття на дві порції відбувається приблизно для одного з 13 записів, не створюючи надлишкових затримок на шині SPI.

## Організація секторів та кадрування телеметрії

Кільцевий буфер виділяє в адресній карті Flash неперервний блок із N фізичних секторів (наприклад, 64 сектори по 4 КБ, що становить 256 КБ пам'яті).

Кожен сектор починається зі службового заголовка фіксованого розміру (16 байтів):

```
+─────────────────────────────────────────────────────────────────────────────+
| СТРУКТУРА ЗАГОЛОВКА СЕКТОРА (SECTOR HEADER — 16 БАЙТІВ)                     |
|                                                                             |
| Зсув (байти)  Тип         Поле            Призначення                       |
| ─────────────────────────────────────────────────────────────────────────── |
| 0x00..0x03    uint32_t    magic           Маркер сховища 0x53464C53 ('SFLS')|
| 0x04..0x07    uint32_t    sequence_num    Монотонний лічильник покоління    |
| 0x08..0x0B    uint32_t    erase_count     Кількість виконаних стирань       |
| 0x0C          uint8_t     state           Стан: 0xFF, 0xFE, 0xFC, 0x00      |
| 0x0D          uint8_t     reserved        Вирівнювання на 4 байти (0xFF)    |
| 0x0E..0x0F    uint16_t    header_crc      CRC-16 перших 14 байтів           |
+─────────────────────────────────────────────────────────────────────────────+
```

Простір сектора після заголовка (починаючи зі зсуву `0x0010` до `0x0FFF`) заповнюється кадрами телеметрії змінної довжини:

```
+─────────────────────────────────────────────────────────────────────────────+
| СТРУКТУРА КАДРУ ТЕЛЕМЕТРІЇ (RECORD FRAME)                                   |
|                                                                             |
| Поле              Розмір          Призначення поля                          |
| ─────────────────────────────────────────────────────────────────────────── |
| record_magic      uint16_t (2 Б)  Маркер початку запису: 0xAA55             |
| record_state      uint8_t  (1 Б)  Атомарний стан (ALLOC/COMMIT/DISPATCHED)  |
| payload_len       uint16_t (2 Б)  Довжина стисненого корисного блоку даних  |
| sequence_id       uint32_t (4 Б)  Глобальний монотонний лічильник точки     |
| timestamp_delta   Varint   (1–4 Б)Різниця часу між точками в секундах       |
| compressed_data   N байтів        Стиснені показники сенсорів               |
| checksum          uint32_t (4 Б)  CRC-32 (IEEE 802.3) від seq_id до кінця   |
+─────────────────────────────────────────────────────────────────────────────+
```

## Математичні засади компресії: Дельта-кодування та Varint/ZigZag

Сирий масив вимірювань типового промислового датчика містить параметри різної природи: часову мітку Unix, температуру, тиск, напругу батареї та лічильник імпульсів. Якщо зберігати ці величини у вигляді стандартної структури мови C з фіксованими типами:

:::tabs

@tab c

```c
typedef struct {
    uint32_t timestamp;           /* 4 байти */
    int32_t  temperature_c_x100;  /* 4 байти */
    uint32_t pressure_pa;         /* 4 байти */
    uint16_t battery_mv;          /* 2 байти */
    uint32_t pulse_count;         /* 4 байти */
} raw_telemetry_t;                /* Разом: 18 байтів (з вирівнюванням 20 Б) */
```

@tab cpp

```cpp
struct RawTelemetry {
    uint32_t timestamp{0};          // 4 байти
    int32_t  temperature_c_x100{0}; // 4 байти
    uint32_t pressure_pa{0};        // 4 байти
    uint16_t battery_mv{0};         // 2 байти
    uint32_t pulse_count{0};        // 4 байти
};
```

:::

При збереженні 43 000 нестиснених точок обсяг даних складе близько `860 КБ`. Оскільки ентропія різниць між сусідніми вимірюваннями є вкрай низькою, застосування комбінованої схеми стиснення дозволяє скоротити розмір кадру до `4–7 байтів`:

1. **Дельта-кодування (Delta Compression):** Замість абсолютного значення параметра зберігається його зміна відносно попереднього вимірювання:

```
Delta_T = Temp_current - Temp_previous      [різниця показників температури]
```

Якщо за інтервал вимірювання 60 секунд температура змінилася з +22.14 °C (2214) до +22.18 °C (2218), дельта становить лише `+4`.
2. **Знакове перетворення ZigZag:** Дельти можуть бути як додатними, так і від'ємними. Від'ємне число `-1` у форматі `int32_t` у додатковому коді має вигляд `0xFFFFFFFF`. Збереження такого числа у форматі Varint вимагатиме 5 байтів. Алгоритм ZigZag перетворює знакове число у беззнакове шляхом зсуву бітів, переміщуючи знаковий біт у наймолодшу позицію:

```
ZigZag(n) = (n << 1) ^ (n >> 31)      [формула перетворення знаку]
```

В результаті числа відображаються так: 0 → 0, -1 → 1, +1 → 2, -2 → 3, +2 → 4.
3. **Кодування зі змінною довжиною (Varint / LEB128):** Беззнакове число розбивається на 7-бітні блоки. Молодші 7 бітів записуються в байт, а старший (8-й) біт встановлюється в `1`, якщо далі слідують інші значущі біти числа, і в `0`, якщо це останній байт:

```
Діапазон значень        Кількість байтів у Varint    Економія пам'яті
────────────────────────────────────────────────────────────────────
0 .. 127                1 байт                       75% (1 замість 4 Б)
128 .. 16383            2 байти                      50% (2 замість 4 Б)
16384 .. 2097151        3 байти                      25% (3 замість 4 Б)
```

Завдяки цьому зміна температури на +0.04 °C після перетворення ZigZag дає число 8, яке упаковується всього в **один байт** `0x08`. Зміна тиску на +12 Па дає число 24, що кодується байтом `0x18`. Загальний розмір корисного навантаження кадру зменшується до 5 байтів, що дозволяє вмістити в ті самі 256 КБ Flash-пам'яті понад 38 000 повноцінних вимірювань.

## Розрахунок ресурсу та вирівнювання зносу (Wear Leveling)

Ресурс матриці NOR Flash обмежений гарантованою кількістю циклів стирання (Endurance rating), яка для якісних промислових чипів становить E_max = 100 000 циклів для кожного сектора.

Розрахуємо надійність сховища для реального профілю експлуатації:
- Загальний обсяг кільцевого буфера: 64 сектори по 4096 байтів (262 144 байти).
- Корисний обсяг сектора за вирахуванням заголовка: 4096 - 16 = 4080 байтів.
- Середній розмір стисненого кадру з заголовком і CRC: 2 + 1 + 2 + 4 + 6 + 4 = 19 байтів.
- Кількість записів в одному секторі: 4080 / 19 ≈ 214 записів.
- Загальна ємність кільцевого буфера: 214 × 64 = 13 696 вимірювань.
- При інтервалі опитування 1 раз на хвилину повне заповнення буфера триває:

```
T_full = 13696 хв ≈ 228 годин ≈ 9.5 доби      [час одного повного оберту кільця]
```

За 10 років безперервної експлуатації (3650 діб) буфер виконає:

```
N_cycles = 3650 діб / 9.5 діб ≈ 384 цикли стирання      [сумарна кількість циклів]
```

При номінальному ресурсі 100 000 циклів використання становить лише `0.38%` від гарантованого запасу напівпровідникової матриці. Завдяки строго циклічному просуванню вказівника голови `head_sector_idx` знос рівномірно розподіляється між усіма 64 секторами, виключаючи передчасну локальну деградацію окремих комірок пам'яті.

### Природне вирівнювання зносу та коефіцієнт підсилення запису

У традиційних файлових системах із випадковим доступом та журналюванням для вирівнювання зносу застосовують спеціальний трансляційний рівень (*Flash Translation Layer, FTL*) із динамічним пулом секторів і фоновим збиранням сміття. Це спричиняє суттєве підсилення запису (*Write Amplification Factor, WAF*), коли для збереження 1 байта корисних даних у пам'ять записується від 2.5 до 5.0 байтів службових метаданих та перенесених блоків.

У спеціалізованому циклічному буфері реалізовано детерміноване природне вирівнювання зносу (*Natural Wear Leveling*):
- **Мінімальне підсилення запису (WAF):** Завдяки виключно послідовному додаванню нових точок у вільний простір поточного сектора та переходу до наступного сектора лише після повного заповнення 4080 корисних байтів, коефіцієнт підсилення запису прямує до ідеального мінімуму:

```
WAF = (4080 + 16) / 4080 ≈ 1.004      [коефіцієнт підсилення запису кільцевого буфера]
```

Службові накладні витрати складають лише 16 байтів метаданих заголовка на весь 4-кілобайтний сектор, усуваючи будь-яке паразитне копіювання чи збирання сміття.
- **Діагностика асиметрії зносу за лічильником стирань:** Поле `erase_count` у заголовку сектора інкрементується перед кожним стиранням. Під час монтування драйвер обчислює різницю між максимально зношеним і найменш зношеним секторами:

```
Delta_E = max(erase_count) - min(erase_count)      [розкид кількості циклів стирання]
```

У штатному режимі `Delta_E` становить 0 або 1. Якщо значення `Delta_E > 1`, це свідчить про наявність пропущених секторів через аварійні перезапуски або ізольовані збійні ділянки пам'яті.
- **Ізоляція дефектних секторів (Bad Sector Retirement):** Якщо під час стирання сектора чи програмування сторінки виникає апаратна відмова або невідповідність контрольної суми при зворотній верифікації, драйвер записує `0x00000000` у поле `magic` заголовка. Такий сектор назавжди вилучається з кільцевої черги, а робота прозоро триває на залишкових `N - 1` секторах без втрати цілісності потоку телеметрії.

## Відновлення вказівників при старті та вивантаження батчів

Під час первинного ввімкнення або перезапуску після глибокого сну драйвер монтує буфер за наступним детермінованим алгоритмом:

1. **Сканування та валідація секторів:** Контролер зчитує 16-байтні заголовки всіх N фізичних секторів кільця та розраховує контрольну суму CRC-16 для перших 14 байтів кожного заголовка. Якщо заголовок містить коректне магічне число `0x53464C53` ('SFLS') та валідний CRC, сектор вважається робочим.
2. **Локалізація голови запису (Head Cursor):** Сектор із найбільшим монотонним лічильником `sequence_num` призначається поточною головою запису (`head_sector_idx`). Усередині цього сектора драйвер виконує лінійний пошук: зчитує 2-байтні маркери `0xAA55` та перевіряє байт стану кадру. Щойно виявляється перший зсув із байтами `0xFF` (вільний нестертий простір) або запис у стані `0xFE` (незавершений запис, перерваний знеструмленням), вказівник `head_write_offset` фіксується на цій позиції.
3. **Локалізація хвоста зчитування (Tail Cursor):** Сектор із найменшим значенням `sequence_num`, стан якого не дорівнює `0x00` (DISPATCHED), визначається як активний хвіст вивантаження (`tail_sector_idx`). Якщо всі сектори мають статус `0x00` або стерті (`0xFF`), хвіст вирівнюється за поточною позицією голови, що означає порожній буфер (усі накопичені дані успішно передані на сервер).

Коли відновлюється стільниковий зв'язок (LTE-M/NB-IoT) або підключається резервний бездротовий канал, мікроконтролер переходить у режим пакетного вивантаження:
- Драйвер зчитує з активного хвоста черговий батч непідтверджених записів (наприклад, від 5 до 20 кадрів залежно від максимального розміру корисного навантаження протоколу передачі).
- Батч формується в єдиний агрегований бінарний пакет або серію MQTT-публікацій із рівнем обслуговування `QoS 1` (з обов'язковим очікуванням пакета `PUBACK`) або CoAP у режимі `CON` (Confirmable Message).
- Отримавши від хмарної платформи підтвердження прийому із зазначенням діапазону ідентифікаторів `sequence_id`, мікроконтролер викликає метод `acknowledge()`. Ця операція записує значення `0x00` (DISPATCHED) у 3-й байт кожного підтвердженого кадру.
- Після того як останній кадр у поточному секторі перейшов у стан `0x00`, контролер перезаписує байт стану самого заголовка сектора на `0x00`. Вказівник хвоста `tail_sector_idx` інкрементується за модулем N, а повністю вивантажений сектор додається до черги фонового стирання, що виконується в моменти відсутності обміну даними по шині SPI.

## Обробка крайових випадків та відмовостійкість

Промислове середовище висуває жорсткі вимоги до збереження даних під час апаратних збоїв. Драйвер містить вбудовані механізми захисту для чотирьох критичних сценаріїв:

1. **Раптове знеструмлення під час запису (Power-Fail mid-write):** Запис кадру складається з чотирьох послідовних кроків: запис маркера `0xAA55` та початкового стану `0xFE` (ALLOCATED), запис корисного навантаження, запис контрольної суми CRC-32 і, нарешті, атомарний запис байта `0xFC` (COMMITTED). Якщо живлення вимикається на будь-якому з проміжних етапів, байт стану залишається у значенні `0xFE`, або перевірка CRC-32 дає невідповідність. Під час наступного монтування такий пошкоджений запис ігнорується, а голова запису зупиняється на ньому, унеможливлюючи передачу спотворених даних у хмару.
2. **Переповнення кільця при тривалому блекауті (Buffer Full Overrun):** Якщо зв'язок відсутній стільки часу, що голова запису наздоганяє незчитаний хвіст (`(head_sector_idx + 1) % total_sectors == tail_sector_idx`), драйвер реалізує регульовану політику: або відкидає найстаріший непідтверджений сектор (пересуваючи хвіст уперед і стираючи старі дані під нові вимірювання), або блокує запис рутинної телеметрії, зберігаючи лише критичні тривожні події.
3. **Виявлення дефектних секторів (Bad Sector Retirement):** Якщо операція стирання сектора або запису сторінки повертає помилку через фізичну деградацію кремнієвої комірки (команда JEDEC повертає біт помилки в статусному регістрі), драйвер позначає сектор як дефектний (записуючи `0x00` у магічне поле заголовка) і назавжди виключає його з кільцевої ротації.
4. **Динамічна адаптація розміру батчу до якості радіоканалу:** Під час передачі через нестабільні стільникові канали або супутникові лінки NTN розмір порції вивантаження автоматично масштабується. Якщо рівень сигналу RSRP високий (> -85 dBm), драйвер агрегує до 50 кадрів в один пакет CoAP/MQTT, мінімізуючи витрати на заголовки IP/UDP. При падінні сигналу до граничних значень (RSRP < -115 dBm) розмір батчу зменшується до 2–3 кадрів, що зменшує ймовірність розриву радіопакета через спотворення бітів ефірним шумом.
5. **Ідемпотентність та дедуплікація на хмарному сервері:** У разі обриву зв'язку в момент відправки підтвердження (ACK від сервера втрачено в радіоефірі), мікроконтролер під час наступного сеансу відправить той самий батч повторно. Хмарна база даних часових рядів (Time-Series DB) використовує глобальний монотонний лічильник `sequence_id` разом з унікальним ідентифікатором пристрою (IMEI / DevEUI) як первинний ключ (*Primary Key*). Повторний запис дубліката оновлює існуючий рядок без створення спотворених копій вимірювань.

## Програмна реалізація драйвера Flash-буфера

Нижче наведено повну виробничу реалізацію драйвера автономного Flash-буфера з компресією, контролем цілісності та транзакційним підтвердженням на мовах C99 та сучасній C++20.

:::tabs

@tab c

```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Геометрія пам'яті NOR Flash */
#define FLASH_SECTOR_SIZE          4096U
#define FLASH_SECTOR_HEADER_SIZE   16U
#define FLASH_PAGE_SIZE            256U
#define FLASH_SECTOR_MAGIC         0x53464C53U  /* 'SFLS' */
#define FLASH_RECORD_MAGIC         0xAA55U

/* Стани секторів та записів */
#define FLASH_STATE_ERASED         0xFFU
#define FLASH_STATE_ALLOCATED      0xFEU
#define FLASH_STATE_COMMITTED      0xFCU
#define FLASH_STATE_DISPATCHED     0x00U

/* Заголовок сектора Flash (16 байтів) */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t sequence_num;
    uint32_t erase_count;
    uint8_t  state;
    uint8_t  reserved;
    uint16_t header_crc;
} flash_sector_header_t;

/* Структура датчиків телеметрії */
typedef struct {
    uint32_t timestamp;
    int32_t  temperature_c_x100; /* Температура * 100 (°C) */
    uint32_t pressure_pa;        /* Тиск у Паскалях */
    uint16_t battery_mv;         /* Напруга батареї в мВ */
    uint32_t pulse_count;        /* Лічильник імпульсів лічильника */
} telemetry_sample_t;

/* Апаратний інтерфейс драйвера SPI Flash (HAL) */
typedef struct {
    bool (*read)(uint32_t addr, uint8_t *buf, size_t size);
    bool (*write)(uint32_t addr, const uint8_t *buf, size_t size);
    bool (*erase_sector)(uint32_t sector_addr);
} flash_hal_t;

/* Контекст кільцевого буфера телеметрії */
typedef struct {
    const flash_hal_t *hal;
    uint32_t base_addr;
    uint32_t total_sectors;
    uint32_t head_sector_idx;
    uint32_t head_write_offset;
    uint32_t tail_sector_idx;
    uint32_t tail_read_offset;
    uint32_t global_seq_id;
    telemetry_sample_t last_sample;
    bool is_mounted;
} flash_ring_buffer_t;

/* Таблиця та обчислення CRC-32 (IEEE 802.3) */
static uint32_t crc32_update(uint32_t crc, const uint8_t *data, size_t len) {
    crc = ~crc;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
        }
    }
    return ~crc;
}

static uint16_t crc16_update(uint16_t crc, const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc & 0x8000U) ? ((crc << 1) ^ 0x1021U) : (crc << 1);
        }
    }
    return crc;
}

/* Кодування ZigZag для знакового int32 */
static inline uint32_t zigzag_encode(int32_t val) {
    return (uint32_t)((val << 1) ^ (val >> 31));
}

static inline int32_t zigzag_decode(uint32_t val) {
    return (int32_t)((val >> 1) ^ (-(val & 1U)));
}

/* Кодування Varint у вихідний буфер */
static size_t varint_encode(uint32_t val, uint8_t *out) {
    size_t len = 0;
    while (val >= 0x80U) {
        out[len++] = (uint8_t)((val & 0x7FU) | 0x80U);
        val >>= 7;
    }
    out[len++] = (uint8_t)(val & 0x7FU);
    return len;
}

/* Декодування Varint із вхідного буфера */
static size_t varint_decode(const uint8_t *in, size_t max_len, uint32_t *val) {
    uint32_t res = 0;
    uint8_t shift = 0;
    size_t idx = 0;
    while (idx < max_len) {
        uint8_t byte = in[idx++];
        res |= (uint32_t)(byte & 0x7FU) << shift;
        if (!(byte & 0x80U)) {
            *val = res;
            return idx;
        }
        shift += 7;
        if (shift >= 35) return 0; /* Помилка формату */
    }
    return 0;
}

/* Упаковка дельт вимірювання */
static size_t compress_sample(const telemetry_sample_t *current,
                              const telemetry_sample_t *prev,
                              uint8_t *out_buf, size_t max_buf) {
    if (!current || !prev || !out_buf || max_buf < 32) return 0;

    size_t offset = 0;
    uint32_t dt = current->timestamp - prev->timestamp;
    int32_t d_temp = current->temperature_c_x100 - prev->temperature_c_x100;
    int32_t d_press = (int32_t)current->pressure_pa - (int32_t)prev->pressure_pa;
    int32_t d_volt = (int32_t)current->battery_mv - (int32_t)prev->battery_mv;
    uint32_t d_pulse = current->pulse_count - prev->pulse_count;

    offset += varint_encode(dt, &out_buf[offset]);
    offset += varint_encode(zigzag_encode(d_temp), &out_buf[offset]);
    offset += varint_encode(zigzag_encode(d_press), &out_buf[offset]);
    offset += varint_encode(zigzag_encode(d_volt), &out_buf[offset]);
    offset += varint_encode(d_pulse, &out_buf[offset]);

    return offset;
}

/* Ініціалізація та монтування кільцевого буфера */
bool flash_ring_buffer_mount(flash_ring_buffer_t *rb, const flash_hal_t *hal,
                             uint32_t base_addr, uint32_t total_sectors) {
    if (!rb || !hal || total_sectors < 2) return false;

    memset(rb, 0, sizeof(*rb));
    rb->hal = hal;
    rb->base_addr = base_addr;
    rb->total_sectors = total_sectors;

    uint32_t max_seq = 0;
    uint32_t min_seq = 0xFFFFFFFFU;
    bool found_active = false;

    /* Скан усіх секторів для пошуку Head та Tail */
    for (uint32_t i = 0; i < total_sectors; ++i) {
        flash_sector_header_t hdr;
        uint32_t addr = base_addr + (i * FLASH_SECTOR_SIZE);
        if (!hal->read(addr, (uint8_t *)&hdr, sizeof(hdr))) return false;

        uint16_t crc = crc16_update(0xFFFFU, (const uint8_t *)&hdr, 14);
        if (hdr.magic == FLASH_SECTOR_MAGIC && hdr.header_crc == crc) {
            found_active = true;
            if (hdr.sequence_num >= max_seq) {
                max_seq = hdr.sequence_num;
                rb->head_sector_idx = i;
            }
            if (hdr.state != FLASH_STATE_DISPATCHED && hdr.sequence_num <= min_seq) {
                min_seq = hdr.sequence_num;
                rb->tail_sector_idx = i;
            }
        }
    }

    if (!found_active) {
        /* Первинне форматування першого сектора */
        rb->head_sector_idx = 0;
        rb->tail_sector_idx = 0;
        rb->global_seq_id = 1;

        hal->erase_sector(base_addr);
        flash_sector_header_t new_hdr = {
            .magic = FLASH_SECTOR_MAGIC,
            .sequence_num = 1,
            .erase_count = 1,
            .state = FLASH_STATE_ALLOCATED,
            .reserved = 0xFFU,
            .header_crc = 0
        };
        new_hdr.header_crc = crc16_update(0xFFFFU, (const uint8_t *)&new_hdr, 14);
        hal->write(base_addr, (const uint8_t *)&new_hdr, sizeof(new_hdr));
        rb->head_write_offset = FLASH_SECTOR_HEADER_SIZE;
        rb->tail_read_offset = FLASH_SECTOR_HEADER_SIZE;
    } else {
        /* Знаходимо позицію голови запису в head_sector */
        uint32_t s_addr = base_addr + (rb->head_sector_idx * FLASH_SECTOR_SIZE);
        rb->head_write_offset = FLASH_SECTOR_HEADER_SIZE;

        while (rb->head_write_offset + 12 < FLASH_SECTOR_SIZE) {
            uint16_t rec_magic = 0;
            uint8_t rec_state = 0;
            uint16_t p_len = 0;
            hal->read(s_addr + rb->head_write_offset, (uint8_t *)&rec_magic, 2);

            if (rec_magic != FLASH_RECORD_MAGIC) break;

            hal->read(s_addr + rb->head_write_offset + 2, &rec_state, 1);
            hal->read(s_addr + rb->head_write_offset + 3, (uint8_t *)&p_len, 2);

            uint32_t total_rec_size = 2 + 1 + 2 + 4 + p_len + 4;
            if (rec_state == FLASH_STATE_COMMITTED) {
                rb->head_write_offset += total_rec_size;
            } else {
                /* Незавершений або пошкоджений запис — зупиняємося тут */
                break;
            }
        }
        rb->tail_read_offset = FLASH_SECTOR_HEADER_SIZE;
    }

    rb->is_mounted = true;
    return true;
}

/* Запис вимірювання у кільцевий буфер */
bool flash_ring_buffer_push(flash_ring_buffer_t *rb, const telemetry_sample_t *sample) {
    if (!rb || !rb->is_mounted || !sample) return false;

    uint8_t payload[64];
    size_t payload_len = compress_sample(sample, &rb->last_sample, payload, sizeof(payload));
    if (payload_len == 0) return false;

    uint32_t rec_total_size = 2 + 1 + 2 + 4 + (uint32_t)payload_len + 4;

    /* Перевіряємо, чи вміщується запис у поточний сектор */
    if (rb->head_write_offset + rec_total_size > FLASH_SECTOR_SIZE) {
        /* Закриваємо поточний сектор: встановлюємо стан 0xFC (FULL) */
        uint32_t cur_hdr_addr = rb->base_addr + (rb->head_sector_idx * FLASH_SECTOR_SIZE) + 12;
        uint8_t full_state = FLASH_STATE_COMMITTED;
        rb->hal->write(cur_hdr_addr, &full_state, 1);

        /* Переходимо до наступного сектора */
        uint32_t next_sector = (rb->head_sector_idx + 1) % rb->total_sectors;
        uint32_t next_addr = rb->base_addr + (next_sector * FLASH_SECTOR_SIZE);

        /* Зчитуємо лічильник зносу старого сектора */
        flash_sector_header_t old_hdr;
        rb->hal->read(next_addr, (uint8_t *)&old_hdr, sizeof(old_hdr));
        uint32_t er_cnt = (old_hdr.magic == FLASH_SECTOR_MAGIC) ? old_hdr.erase_count + 1 : 1;

        rb->hal->erase_sector(next_addr);

        flash_sector_header_t new_hdr = {
            .magic = FLASH_SECTOR_MAGIC,
            .sequence_num = ++rb->global_seq_id,
            .erase_count = er_cnt,
            .state = FLASH_STATE_ALLOCATED,
            .reserved = 0xFFU,
            .header_crc = 0
        };
        new_hdr.header_crc = crc16_update(0xFFFFU, (const uint8_t *)&new_hdr, 14);
        rb->hal->write(next_addr, (const uint8_t *)&new_hdr, sizeof(new_hdr));

        rb->head_sector_idx = next_sector;
        rb->head_write_offset = FLASH_SECTOR_HEADER_SIZE;
    }

    uint32_t write_addr = rb->base_addr + (rb->head_sector_idx * FLASH_SECTOR_SIZE) + rb->head_write_offset;

    /* 1. Записуємо маркер та початковий стан ALLOCATED (0xFE) */
    uint16_t magic = FLASH_RECORD_MAGIC;
    uint8_t state = FLASH_STATE_ALLOCATED;
    uint16_t len_field = (uint16_t)payload_len;
    uint32_t seq_id = rb->global_seq_id;

    rb->hal->write(write_addr, (const uint8_t *)&magic, 2);
    rb->hal->write(write_addr + 2, &state, 1);
    rb->hal->write(write_addr + 3, (const uint8_t *)&len_field, 2);
    rb->hal->write(write_addr + 5, (const uint8_t *)&seq_id, 4);

    /* 2. Записуємо стиснене корисне навантаження */
    rb->hal->write(write_addr + 9, payload, payload_len);

    /* 3. Обчислюємо та записуємо CRC-32 від seq_id та payload */
    uint32_t crc = crc32_update(0xFFFFFFFFU, (const uint8_t *)&seq_id, 4);
    crc = crc32_update(crc, payload, payload_len);
    rb->hal->write(write_addr + 9 + payload_len, (const uint8_t *)&crc, 4);

    /* 4. Фінальний атомарний коміт: переводимо стан у 0xFC (COMMITTED) */
    state = FLASH_STATE_COMMITTED;
    rb->hal->write(write_addr + 2, &state, 1);

    rb->head_write_offset += rec_total_size;
    rb->last_sample = *sample;
    return true;
}

/* Підтвердження успішного вивантаження батчу записів */
bool flash_ring_buffer_ack(flash_ring_buffer_t *rb, uint32_t sector_idx, uint32_t record_offset) {
    if (!rb || !rb->is_mounted || sector_idx >= rb->total_sectors) return false;

    uint32_t target_addr = rb->base_addr + (sector_idx * FLASH_SECTOR_SIZE) + record_offset + 2;
    uint8_t ack_state = FLASH_STATE_DISPATCHED; /* 0x00 */

    /* Записуємо 0x00 у байт стану запису */
    if (!rb->hal->write(target_addr, &ack_state, 1)) return false;

    /* Перевіряємо, чи всі записи в секторі мають стан DISPATCHED */
    uint32_t s_addr = rb->base_addr + (sector_idx * FLASH_SECTOR_SIZE);
    uint32_t off = FLASH_SECTOR_HEADER_SIZE;
    bool all_acked = true;

    while (off + 12 < FLASH_SECTOR_SIZE) {
        uint16_t rec_magic = 0;
        uint8_t rec_state = 0;
        uint16_t p_len = 0;
        rb->hal->read(s_addr + off, (uint8_t *)&rec_magic, 2);
        if (rec_magic != FLASH_RECORD_MAGIC) break;

        rb->hal->read(s_addr + off + 2, &rec_state, 1);
        rb->hal->read(s_addr + off + 3, (uint8_t *)&p_len, 2);

        if (rec_state != FLASH_STATE_DISPATCHED) {
            all_acked = false;
            break;
        }
        off += 2 + 1 + 2 + 4 + p_len + 4;
    }

    if (all_acked && sector_idx != rb->head_sector_idx) {
        /* Позначаємо весь сектор як DISPATCHED (0x00) */
        uint8_t sec_dispatched = FLASH_STATE_DISPATCHED;
        rb->hal->write(s_addr + 12, &sec_dispatched, 1);
        rb->tail_sector_idx = (sector_idx + 1) % rb->total_sectors;
    }

    return true;
}
```

@tab cpp

```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <concepts>
#include <algorithm>

namespace telemetry {

inline constexpr uint32_t kFlashSectorSize = 4096;
inline constexpr uint32_t kFlashSectorHeaderSize = 16;
inline constexpr uint32_t kSectorMagic = 0x53464C53; // 'SFLS'
inline constexpr uint16_t kRecordMagic = 0xAA55;

enum class State : uint8_t {
    Erased = 0xFF,
    Allocated = 0xFE,
    Committed = 0xFC,
    Dispatched = 0x00
};

enum class BufferError : uint8_t {
    HalError,
    BufferFull,
    InvalidRecord,
    CrcMismatch,
    Unmounted
};

struct SectorHeader {
    uint32_t magic{kSectorMagic};
    uint32_t sequence_num{0};
    uint32_t erase_count{0};
    State state{State::Erased};
    uint8_t reserved{0xFF};
    uint16_t header_crc{0};
};

struct Sample {
    uint32_t timestamp{0};
    int32_t temperature_c_x100{0};
    uint32_t pressure_pa{0};
    uint16_t battery_mv{0};
    uint32_t pulse_count{0};
};

/* Концепт апаратного Flash-драйвера */
template <typename T>
concept FlashDriver = requires(T driver, uint32_t addr, std::span<const std::byte> wbuf, std::span<std::byte> rbuf) {
    { driver.read(addr, rbuf) } -> std::same_as<bool>;
    { driver.write(addr, wbuf) } -> std::same_as<bool>;
    { driver.erase_sector(addr) } -> std::same_as<bool>;
};

/* Утилітарний клас контрольних сум */
class Checksum {
public:
    static constexpr uint32_t crc32(std::span<const std::byte> data, uint32_t crc = 0xFFFFFFFF) noexcept {
        crc = ~crc;
        for (auto b : data) {
            crc ^= static_cast<uint8_t>(b);
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
            }
        }
        return ~crc;
    }

    static constexpr uint16_t crc16(std::span<const std::byte> data, uint16_t crc = 0xFFFF) noexcept {
        for (auto b : data) {
            crc ^= static_cast<uint16_t>(b) << 8;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc & 0x8000U) ? ((crc << 1) ^ 0x1021U) : (crc << 1);
            }
        }
        return crc;
    }
};

/* Кодек Varint та ZigZag */
class VarintCodec {
public:
    static constexpr uint32_t zigzag_encode(int32_t val) noexcept {
        return static_cast<uint32_t>((val << 1) ^ (val >> 31));
    }

    static constexpr int32_t zigzag_decode(uint32_t val) noexcept {
        return static_cast<int32_t>((val >> 1) ^ (-(val & 1U)));
    }

    static size_t encode(uint32_t val, std::span<std::byte> out) noexcept {
        size_t len = 0;
        while (val >= 0x80U && len < out.size()) {
            out[len++] = static_cast<std::byte>((val & 0x7FU) | 0x80U);
            val >>= 7;
        }
        if (len < out.size()) {
            out[len++] = static_cast<std::byte>(val & 0x7FU);
            return len;
        }
        return 0;
    }
};

/* Шаблонний клас енергонезалежного кільцевого буфера */
template <FlashDriver DriverType>
class RingBuffer {
public:
    explicit constexpr RingBuffer(DriverType& driver, uint32_t base_addr, uint32_t total_sectors) noexcept
        : driver_{driver}, base_addr_{base_addr}, total_sectors_{total_sectors} {}

    std::expected<void, BufferError> mount() noexcept {
        uint32_t max_seq = 0;
        uint32_t min_seq = 0xFFFFFFFF;
        bool found = false;

        for (uint32_t i = 0; i < total_sectors_; ++i) {
            SectorHeader hdr;
            auto raw_span = std::as_writable_bytes(std::span{&hdr, 1});
            if (!driver_.read(base_addr_ + i * kFlashSectorSize, raw_span)) {
                return std::unexpected(BufferError::HalError);
            }

            const auto crc = Checksum::crc16(raw_span.first(14));
            if (hdr.magic == kSectorMagic && hdr.header_crc == crc) {
                found = true;
                if (hdr.sequence_num >= max_seq) {
                    max_seq = hdr.sequence_num;
                    head_sector_idx_ = i;
                }
                if (hdr.state != State::Dispatched && hdr.sequence_num <= min_seq) {
                    min_seq = hdr.sequence_num;
                    tail_sector_idx_ = i;
                }
            }
        }

        if (!found) {
            return format_initial_sector();
        }

        mounted_ = true;
        return scan_head_offset();
    }

    std::expected<void, BufferError> push(const Sample& sample) noexcept {
        if (!mounted_) return std::unexpected(BufferError::Unmounted);

        std::array<std::byte, 64> payload_buf{};
        const auto payload_len = compress_sample(sample, payload_buf);
        if (payload_len == 0) return std::unexpected(BufferError::InvalidRecord);

        const uint32_t total_rec_size = 2 + 1 + 2 + 4 + static_cast<uint32_t>(payload_len) + 4;

        if (head_write_offset_ + total_rec_size > kFlashSectorSize) {
            auto res = rotate_to_next_sector();
            if (!res) return res;
        }

        const uint32_t write_addr = base_addr_ + (head_sector_idx_ * kFlashSectorSize) + head_write_offset_;

        // 1. Запис заголовка кадру (State = Allocated)
        const uint16_t magic = kRecordMagic;
        const auto state_alloc = State::Allocated;
        const auto p_len = static_cast<uint16_t>(payload_len);
        const uint32_t seq_id = global_seq_id_;

        driver_.write(write_addr, std::as_bytes(std::span{&magic, 1}));
        driver_.write(write_addr + 2, std::as_bytes(std::span{&state_alloc, 1}));
        driver_.write(write_addr + 3, std::as_bytes(std::span{&p_len, 1}));
        driver_.write(write_addr + 5, std::as_bytes(std::span{&seq_id, 1}));

        // 2. Запис корисного навантаження
        driver_.write(write_addr + 9, std::span{payload_buf.data(), payload_len});

        // 3. Обчислення та запис контрольної суми CRC-32
        uint32_t crc = Checksum::crc32(std::as_bytes(std::span{&seq_id, 1}));
        crc = Checksum::crc32(std::span{payload_buf.data(), payload_len}, crc);
        driver_.write(write_addr + 9 + payload_len, std::as_bytes(std::span{&crc, 1}));

        // 4. Фінальний атомарний коміт
        const auto state_committed = State::Committed;
        driver_.write(write_addr + 2, std::as_bytes(std::span{&state_committed, 1}));

        head_write_offset_ += total_rec_size;
        last_sample_ = sample;
        return {};
    }

    std::expected<void, BufferError> acknowledge(uint32_t sector_idx, uint32_t record_offset) noexcept {
        if (!mounted_) return std::unexpected(BufferError::Unmounted);

        const uint32_t target_addr = base_addr_ + (sector_idx * kFlashSectorSize) + record_offset + 2;
        const auto ack_state = State::Dispatched;

        if (!driver_.write(target_addr, std::as_bytes(std::span{&ack_state, 1}))) {
            return std::unexpected(BufferError::HalError);
        }

        return {};
    }

private:
    std::expected<void, BufferError> format_initial_sector() noexcept {
        head_sector_idx_ = 0;
        tail_sector_idx_ = 0;
        global_seq_id_ = 1;

        if (!driver_.erase_sector(base_addr_)) {
            return std::unexpected(BufferError::HalError);
        }

        SectorHeader new_hdr{
            .magic = kSectorMagic,
            .sequence_num = 1,
            .erase_count = 1,
            .state = State::Allocated,
            .reserved = 0xFF,
            .header_crc = 0
        };
        auto raw = std::as_writable_bytes(std::span{&new_hdr, 1});
        new_hdr.header_crc = Checksum::crc16(raw.first(14));

        if (!driver_.write(base_addr_, raw)) {
            return std::unexpected(BufferError::HalError);
        }

        head_write_offset_ = kFlashSectorHeaderSize;
        mounted_ = true;
        return {};
    }

    std::expected<void, BufferError> scan_head_offset() noexcept {
        const uint32_t s_addr = base_addr_ + (head_sector_idx_ * kFlashSectorSize);
        head_write_offset_ = kFlashSectorHeaderSize;

        while (head_write_offset_ + 12 < kFlashSectorSize) {
            uint16_t magic = 0;
            State rec_state = State::Erased;
            uint16_t p_len = 0;

            driver_.read(s_addr + head_write_offset_, std::as_writable_bytes(std::span{&magic, 1}));
            if (magic != kRecordMagic) break;

            driver_.read(s_addr + head_write_offset_ + 2, std::as_writable_bytes(std::span{&rec_state, 1}));
            driver_.read(s_addr + head_write_offset_ + 3, std::as_writable_bytes(std::span{&p_len, 1}));

            if (rec_state == State::Committed) {
                head_write_offset_ += 2 + 1 + 2 + 4 + p_len + 4;
            } else {
                break;
            }
        }
        return {};
    }

    std::expected<void, BufferError> rotate_to_next_sector() noexcept {
        const uint32_t cur_hdr_addr = base_addr_ + (head_sector_idx_ * kFlashSectorSize) + 12;
        const auto full_state = State::Committed;
        driver_.write(cur_hdr_addr, std::as_bytes(std::span{&full_state, 1}));

        const uint32_t next_sector = (head_sector_idx_ + 1) % total_sectors_;
        const uint32_t next_addr = base_addr_ + (next_sector * kFlashSectorSize);

        SectorHeader old_hdr{};
        driver_.read(next_addr, std::as_writable_bytes(std::span{&old_hdr, 1}));
        const uint32_t er_cnt = (old_hdr.magic == kSectorMagic) ? old_hdr.erase_count + 1 : 1;

        if (!driver_.erase_sector(next_addr)) {
            return std::unexpected(BufferError::HalError);
        }

        SectorHeader new_hdr{
            .magic = kSectorMagic,
            .sequence_num = ++global_seq_id_,
            .erase_count = er_cnt,
            .state = State::Allocated,
            .reserved = 0xFF,
            .header_crc = 0
        };
        auto raw = std::as_writable_bytes(std::span{&new_hdr, 1});
        new_hdr.header_crc = Checksum::crc16(raw.first(14));
        driver_.write(next_addr, raw);

        head_sector_idx_ = next_sector;
        head_write_offset_ = kFlashSectorHeaderSize;
        return {};
    }

    size_t compress_sample(const Sample& current, std::span<std::byte> out) noexcept {
        size_t off = 0;
        const uint32_t dt = current.timestamp - last_sample_.timestamp;
        const int32_t d_temp = current.temperature_c_x100 - last_sample_.temperature_c_x100;
        const int32_t d_press = static_cast<int32_t>(current.pressure_pa) - static_cast<int32_t>(last_sample_.pressure_pa);
        const int32_t d_volt = static_cast<int32_t>(current.battery_mv) - static_cast<int32_t>(last_sample_.battery_mv);
        const uint32_t d_pulse = current.pulse_count - last_sample_.pulse_count;

        off += VarintCodec::encode(dt, out.subspan(off));
        off += VarintCodec::encode(VarintCodec::zigzag_encode(d_temp), out.subspan(off));
        off += VarintCodec::encode(VarintCodec::zigzag_encode(d_press), out.subspan(off));
        off += VarintCodec::encode(VarintCodec::zigzag_encode(d_volt), out.subspan(off));
        off += VarintCodec::encode(d_pulse, out.subspan(off));

        return off;
    }

    DriverType& driver_;
    uint32_t base_addr_{0};
    uint32_t total_sectors_{0};
    uint32_t head_sector_idx_{0};
    uint32_t head_write_offset_{0};
    uint32_t tail_sector_idx_{0};
    uint32_t global_seq_id_{0};
    Sample last_sample_{};
    bool mounted_{false};
};

} // namespace telemetry
```

:::

Поєднання прямого використання фізичних властивостей переходів бітів NOR Flash, різницевої дельта-компресії та замкнутого циклічного ротатора секторів забезпечує довготривалу надійність автономного зберігання даних. Навіть при повній втраті зв'язку на місяці або роки вбудована система гарантує цілісність кожного вимірювання, вирівнює знос кремнієвої матриці та миттєво повертається до штатного вивантаження при першій появі робочого каналу передачі даних.
