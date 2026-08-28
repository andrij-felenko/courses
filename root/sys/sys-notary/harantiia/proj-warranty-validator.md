# ⚙️ Валідатор гарантійних умов та апаратного журналу подій

Сервісні інженери під час приймання поверненого обладнання стикаються з необхідністю швидкої, об'єктивної та юридично бездоганної перевірки дотримання користувачем установлених правил експлуатації. Ручний аналіз сотень байтів сирого дампу енергонезалежної пам'яті EEPROM або FLASH забирає багато часу і створює ризик людської помилки при розшифруванні бітових прапорців датчиків, інтегруванні температурного навантаження чи перевірці криптографічних контрольних сум.

Цей практичний модуль містить повноцінну автономну утиліту валідації гарантійного стану, яка приймає на вхід бінарний образ захищеного журналу подій «чорного ящика», верифікує його структуру та контрольні суми, зіставляє зафіксовані сенсорні екстремуми з політикою допустимих умов експлуатації виробника та генерує структурований діагностичний звіт із фінальним вердиктом рекламації (Return Merchandise Authorization, RMA).

```
+───────────────────────────────────────────────────────────────────────────+
| СХЕМА АВТОМАТИЗОВАНОГО АНАЛІЗУ ГАРАНТІЙНОГО ЛОГУ                          |
|                                                                           |
|   [Вхідний образ пам'яті EEPROM] ──► [Декодер заголовка та подій]         |
|                                                  │                        |
|                                                  ▼                        |
|   [Конфігурація політики вендора] ──► [Двигун правил валідації]           |
|   (Ліміти POH, T_max, V_max, Shock,              │                        |
|    LCI, Tamper, Boot, TempBudget)                ▼                        |
|                                           [Генератор звіту RMA]           |
|                                                  │                        |
|                                                  ▼                        |
|   Результат: APPROVED / REJECTED_LIQUID / REJECTED_EOS / REJECTED_EXPIRED |
+───────────────────────────────────────────────────────────────────────────+
```

## Апаратне середовище та зняття діагностичного дампу

У промислових контролерах, блоках керування двигунами, дронах та автомобільних модулях журнал гарантійних подій зберігається у виділеній мікросхемі SPI/I2C EEPROM або захищеному блоці енергонезалежної пам'яті FRAM (наприклад, Microchip 24CW128 або Cypress FM25V02A). 

На сервісному стенді підключення до пристрою здійснюється одним із трьох способів:
1. **Зовнішнє голчасте поле (Pogo-pin fixture):** Застосовується на конвеєрі або в авторизованих сервісних центрах без повного розбирання пристрою. Голки тестового стенда контактують із технологічними тестовими точками (Test Points, TP) на платі, підключаючись до шини I2C/SPI та лінії апаратного дозволу зчитування.
2. **Сервісний діагностичний інтерфейс (UDS по шині CAN або RS-485):** Пристрій переводиться у розширений діагностичний режим (Diagnostic Session `$03` за стандартом ISO 14229-1), після чого образ журналу вивантажується стандартними пакетами сервісу `$22` (Read Data By Identifier) або через захищений файловий трансфер `$38` (Request File Transfer).
3. **Пряме зчитування пам'яті на програматорі:** У разі катастрофічного пошкодження основного мікроконтролера мікросхему EEPROM випоюють або підключають кліпсою SOIC-8 безпосередньо до апаратного програматора (наприклад, CH341A або Dediprog).

Отриманий бінарний файл містить сирий образ пам'яті фіксованого розміру (від 512 байтів до 4 кілобайтів), який передається на вхід валідатора.

## Протокол вивантаження журналу через UART та SWD на RMA-стенді

Для автоматизованого зняття бінарного образу на сервісному RMA-стенді застосовують два стандартизовані апаратні канали зв'язку:

### 1. Сервісний протокол обміну по UART

Якщо мікроконтролер пристрою зберігає базову працездатність, зняття дампу виконується через асинхронний послідовний інтерфейс UART (швидкість 115 200 або 921 600 бод, формат 8-N-1). Сервісний стенд переводить пристрій у режим діагностичного завантажувача або термінала подачею керуючої послідовності байтів під час апаратного скидання лінії RESET.

Кадр протоколу передачі даних має таку двійкову структуру:
- **Байт початку кадру (Start of Frame, SOF):** Константа `0x7E`.
- **Ідентифікатор команди (`cmd_id`, 1 байт):** Команда зчитування блоку журналу `CMD_READ_LOG = 0xA5`.
- **Зміщення адреси (`offset`, 2 байти, Little-Endian):** Початкова адреса блоку в енергонезалежній пам'яті EEPROM.
- **Довжина запитуваного блоку (`payload_len`, 2 байти):** Розмір порції даних (зазвичай 64 або 128 байтів для узгодження з розміром сторінки EEPROM).
- **Корисне навантаження (Payload):** Зчитані байти пам'яті (у відповіді стенду).
- **Контрольна сума кадру (`frame_crc16`, 2 байти):** Поліном CRC16-CCITT для захисту лінії передачі від імпульсних завад.
- **Байт кінця кадру (End of Frame, EOF):** Константа `0x7F`.

У разі помилки контрольної суми або тайм-ауту відповіді (> 100 мс) стенд виконує автоматичний повтор запиту (ARQ) до трьох спроб, що гарантує надійність зчитування навіть в умовах сильних промислових електромагнітних завад.

### 2. Прямий доступ до пам'яті через інтерфейс налагодження SWD

Якщо прошивка мікроконтролера пошкоджена або процесор заблокований в аварійному циклі обробника винятків (HardFault), вивантаження здійснюється через інтерфейс Serial Wire Debug (SWD), що потребує лише двох сигнальних ліній: тактового сигналу `SWCLK` та двоспрямованої лінії даних `SWDIO`.

RMA-стенд використовує апаратний адаптер налагодження (наприклад, CMSIS-DAP або J-Link) для прямої взаємодії з модулем Debug Access Port (DAP) ядра ARM Cortex-M:
1. **Ініціалізація порту налагодження:** Відправлення послідовності перемикання JTAG-to-SWD (`0xE79E`) та читання регістру `IDCODE` для ідентифікації типу процесора й перевірки фізичного контакту.
2. **Конфігурація Memory Access Port (MEM-AP):** Запис базової адреси системної шини AHB/APB у регістр `TAR` (Transfer Address Register).
3. **Пряме читання блоку пам'яті:** Зчитування даних через регістр `DRW` (Data Read/Write) в режимі автоматичного інкременту адреси без необхідності виконання інструкцій центральним процесором (Non-intrusive memory dump).

Якщо вміст журналу подій дублюється або кешується в статичній оперативній пам'яті (SRAM) контролера, зчитування через SWD дозволяє отримати актуальний стан системи за лічені мілісекунди без ризику повторного пошкодження флеш-пам'яті.

## Інженерна анатомія бінарних полів журналу EEPROM

Для забезпечення надійності зберігання даних заголовок та записи журналу вирівнюються за межами 4-байтних або 32-байтних слів із фіксованим порядком байтів (Little-Endian):

- **Магічне число `magic` (4 байти):** Значення `0x52524157` (символи ASCII "WARR" у little-endian). Дозволяє валідатору негайно визначити, чи містить переданий файл коректний образ гарантійного сховища, чи це випадкове сміття або неініціалізована чиста мікросхема (`0xFFFFFFFF`).
- **Версія схеми `schema_version` (2 байти):** Визначає структуру записів. Відокремлення версії схеми від довжини заголовка дозволяє валідатору підтримувати зворотну сумісність при аналізі пристроїв різних років випуску з різними ревізіями прошивки.
- **Унікальний ідентифікатор `device_uuid` (16 байтів):** 128-бітний ідентифікатор вузла, що формується під час заводського калібрування на основі унікального апаратного ідентифікатора кремнієвого кристала (Silicon UID) та серійного номера виробу.
- **Монотонні лічильники (`power_on_hours`, `boot_count`, `thermal_cycles`):** Енергонезалежні 32-бітні лічильники, що інкрементуються виключно в бік збільшення.
- **Кумулятивна бітова маска порушень `violation_flags` (4 байти):** Кожен біт відповідає окремому апаратному датчику. Використання бітової маски є принциповим інженерним рішенням: у момент аварії (наприклад, потрапляння морської води) одночасно спрацьовує LCI-датчик, падає опір шини живлення, виникає стрибок струму та перегрів ключів. Бітова маска дозволяє зафіксувати всі супутні фактори одночасно в єдиному 32-бітному регістрі.

## Фізичні фактори та алгоритмічні критерії оцінки

Валідатор оцінює пристрій за шістьма незалежними інженерними вимірами:

### 1. Монотонний лічильник напрацювання (Power-On Hours, POH)

Календарний термін володіння (наприклад, 24 місяці з дати продажу) не завжди корелює з фактичним напрацюванням промислового вузла. Контролер містить апаратний монотонний таймер, який інкрементує лічильник робочих годин щогодини перебування під напругою та зберігає значення в EEPROM. Валідатор порівнює `power_on_hours` із максимальним ресурсом, передбаченим комерційним гарантійним контрактом (наприклад, 17 520 годин для двох років безперервної цілодобової роботи).

Крім мотогодин, аналізується лічильник кількості вмикань приладу (`boot_count`). Якщо кількість запусків перевищує допустимий ресурс контактної групи реле живлення чи пускових конденсаторів (наприклад, понад 50 000 увімкнень), це сигналізує про нецільове використання приладу в режимі частого комутування живлення.

### 2. Кумулятивний температурний бюджет (Thermal Budget Integration)

Короткочасний пік температури (наприклад, нагрівання до 75 °C під час пікового обчислювального навантаження) є штатною ситуацією. Проте тривала робота за підвищеної температури прискорює деградацію пайки та кремнієвих кристалів за законом Арреніуса. 

Валідатор аналізує масив температурних записів і обчислює інтеграл теплового навантаження понад базовий поріг:

```
Thermal_Dose = ∑ (T_recorded[i] - T_threshold) * Δt_hours   [кумулятивна доза перегріву]
```

Для прецизійного аналізу валідатор також може розраховувати еквівалентний коефіцієнт прискорення старіння (Acceleration Factor, AF):

```
AF_inst = exp[(E_a / k_B) * (1 / T_nominal - 1 / T_recorded)] [миттєве прискорення деградації]
```

Якщо кумулятивна теплова доза перевищує допустимий ліміт політики (наприклад, 2000 градусо-годин понад 85 °C), гарантія анулюється через хронічний тепловий стрес.

### 3. Електричне перевантаження (EOS) та імпульсні перенапруги

Сенсори напруги фіксують пікове значення напруги вхідної шини V_peak та тривалість сплеску. Валідатор розрізняє три категорії електричного стану:
- **Штатний діапазон:** 18.0 В ≤ V ≤ 28.0 В для номінальної промислової шини 24 В.
- **Тимчасовий перехідний процес (Transient Surge):** 28.0 В < V ≤ 36.0 В тривалістю < 50 мс (поглинається вхідним LC-фільтром та TVS-діодом, не анулює гарантію).
- **Руйнівне перенапруження (EOS / Reverse Polarity):** V > 36.0 В або зворотна полярність V < -0.5 В (фіксується тригером захисту та призводить до негайного анулювання гарантії).

### 4. Контакт із рідиною (LCI) та імпедансний аналіз вологості

Датчики плати реєструють аналоговий опір інтердигітальних пар на друкованій платі. Якщо зафіксовано падіння опору нижче 10 кОм при спрацюванні хімічного LCI-індикатора, система кваліфікує це як пряме затоплення приладу електропровідною рідиною.

Якщо опір перебуває в діапазоні 50 кОм – 1 МОм без зміни кольору LCI-стікера, це кваліфікується як висока відносна вологість навколишнього середовища без прямого залиття (конденсат), що розглядається як пом'якшувальний фактор у разі наявності захисного лакового покриття (Conformal Coating).

### 5. Механічний удар та перевантаження

Дані 3-осьового MEMS-акселерометра оцінюються за вектором сумарного прискорення:

```
A_total = sqrt(A_x^2 + A_y^2 + A_z^2)                  [модуль сумарного вектора перевантаження]
```

Перевищення порогу 50.0 g свідчить про падіння на тверду поверхню з висоти понад 1.5 метра або аварійне зіткнення, що спричиняє відшарування важких компонентів (трансформаторів, дроселів, конденсаторів) або мікротріщини в безсвинцевих паяних кульках BGA-мікросхем.

### 6. Апаратний контроль розкриття та цілісність прошивки (Tamper & Firmware)

Прапорець розкриття корпусу (розрив серпантинного контуру кришки) у поєднанні зі статусом перевірки підпису завантажувача Secure Boot формує доказ несанкціонованої модифікації апаратного або програмного забезпечення.

## Алгоритм кільцевого буфера подій (Circular Ring-Buffer)

Для збереження детальної хронології аварійних подій використовується кільцевий буфер фіксованої місткості (32 записи):

```
+───────────────────────────────────────────────────────────────────────────+
| СТРУКТУРА КІЛЬЦЕВОГО БУФЕРА ЗАПИСІВ АВАРІЙНИХ ПОДІЙ                       |
|                                                                           |
|   [Запис 0] ──► [Запис 1] ──► ... ──► [Запис k] ──► ... ──► [Запис 31]    |
|       ▲                                 ▲                                 |
|       │                                 │                                 |
|   Head Index (Найстаріший)          Tail Index (Найновіший запис)        |
+───────────────────────────────────────────────────────────────────────────+
```

Кожен запис містить відносну часову мітку мотогодин (`timestamp_poh`), тип події, моментальні значення температури, напруги та прискорення в момент фіксації аварії, а також індивідуальну контрольну суму CRC32.

Під час аналізу кільцевого буфера валідатор виконує:
1. Послідовну верифікацію контрольної суми кожного окремого запису.
2. Фільтрацію пошкоджених записів у разі раптового знеструмлення контролера під час запису сторінки EEPROM.
3. Хронологічне сортування подій для відновлення точного ланцюга розвитку аварії (наприклад, визначення того, що перегрів виник за дві години до подачі перенапруги).

## Алгоритмічний розрахунок контрольних сум CRC32 для захищеного журналу

Цілісність гарантійного сховища забезпечується дворівневою системою контрольних сум на базі стандартизованого 32-бітного циклічного надлишкового коду CRC32 (поліном IEEE 802.3 `0x04C11DB7`, зворотний поліном `0xEDB88320` для little-endian обробки).

### Математичні властивості та вибір полінома CRC32

Вибір полінома IEEE 802.3 зумовлений його високою здатністю виявлення апаратних помилок у блоках даних обсягом до кількох кілобайтів:
- **100% виявлення поодиноких і подвійних бітових інверсій:** Гарантується відлов випадкових збоїв осередків пам'яті EEPROM, викликаних витоком заряду плаваючого затвора або паразитними наведеннями шини.
- **100% виявлення непарної кількості бітових помилок:** Будь-яке непарне число спотворених бітів гарантовано змінює контрольний залишок через наявність множника `(x + 1)` у факторизації генераторного полінома.
- **Виявлення пакетних помилок (Burst Errors):** Будь-який пакет помилок довжиною до 32 бітів виявляється зі стовідсотковою гарантією, а для пакетів довжиною понад 32 біти ймовірність пропуску дефекту становить лише `1 / (2^32) ≈ 2.33 * 10^-10`.

### Дворівнева схема контролю цілісності

Валідатор розділяє перевірку цілісності на два ізольовані етапи:

1. **Контрольна сума основного заголовка (`header_crc32`):**
   Обчислюється над усіма системними полями заголовка від початку структури `warranty_image_header_t` до поля `header_crc32` (довжина обчислення становить `sizeof(warranty_image_header_t) - sizeof(uint32_t)`). Це фіксує незмінність загальної конфігурації, ідентифікатора пристрою UUID та сумарних лічильників напрацювання. Якщо CRC заголовка не збігається, весь образ негайно кваліфікується як пошкоджений (`DECISION_REJECTED_CORRUPTED`), оскільки неможливо довіряти базовим лічильникам мотогодин.

2. **Індивідуальні контрольні суми записів кільцевого буфера (`record_crc32`):**
   Кожен запис `sensor_violation_entry_t` містить власну контрольну суму, розраховану за першими 12 байтами структури (без останнього 4-байтного поля CRC). Це критично для захисту від раптового знеструмлення пристрою:
   - Якщо під час аварії живлення зникає в момент запису чергового 16-байтного слота в EEPROM, пошкоджується виключно поточний незавершений запис.
   - Валідатор перевіряє кожну подію окремо: пошкоджений запис ізолюється, тоді як усі попередні історичні записи успішно верифікуються та враховуються при розрахунку сумарного теплового навантаження й аналізі хронології відмови.

### Оптимізація обчислення: побітовий алгоритм та LUT-таблиці

У мікроконтролерах із суворими обмеженнями розміру Flash-пам'яті застосовують побітовий зсувний алгоритм, який не вимагає виділення пам'яті під статичні таблиці коефіцієнтів:

:::tabs
@tab C (C99)
```c
uint32_t crc32_bitwise(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint32_t)data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc & 1U) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
        }
    }
    return crc ^ 0xFFFFFFFFU;
}
```
@tab C++ (C++20)
```cpp
[[nodiscard]] constexpr uint32_t crc32_bitwise(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (const uint8_t byte : data) {
        crc ^= static_cast<uint32_t>(byte);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 1U) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
        }
    }
    return crc ^ 0xFFFFFFFFU;
}
```
:::

На RMA-стенді та у високопродуктивних діагностичних сканерах застосовують табличний алгоритм із попередньо розрахованим масивом із 256 елементів (`crc_table[256]`), що підвищує швидкість обробки даних майже на порядок за рахунок обробки цілого байта за одну табличну вибірку. Сучасні 32-бітні ядра Cortex-M4/M7/M33 також мають вбудований апаратний блок прискорення CRC, сумісний із даним поліномом на апаратному рівні.

## Захист від збоїв живлення: двоетапний буфер (Ping-Pong Buffer Strategy)

Вбудовані мікросхеми EEPROM вимагають від 3 до 5 мілісекунд для завершення внутрішнього циклу запису сторінки (Page Write Time t_wr ≈ 3–5 мс). Якщо в цей момент напруга живлення V_cc падає нижче порогу скидання супервізора живлення (V_rst ≈ 2.7 В), записувана сторінка пошкоджується.

Для гарантування надійності сховища застосовується дзеркальна схема розміщення пам'яті:
- **Сектор A (Primary Sector):** Базова адреса `0x0000`.
- **Сектор B (Mirror Sector):** Базова адреса `0x0800`.

Кожен сектор містить власний 32-бітний монотонний номер генерації (`sequence_counter`) та індивідуальну контрольну суму CRC32. Під час завантаження валідатор зчитує обидва сектори:
1. Якщо обидва сектори валідні за CRC32, для аналізу обирається сектор із більшим значенням `sequence_counter`.
2. Якщо один із секторів пошкоджений через раптове вимкнення живлення в момент аварії, валідатор автоматично використовує цілісний дзеркальний сектор, фіксуючи попередження про факт аварійного скидання.

## Криптографічна автентифікація: HMAC-SHA256 проти фізичної підміни

Звичайний поліноміальний код CRC32 захищає дані від випадкових бітових спотворень та шумів шини передачі даних, проте не захищає від цілеспрямованої фальсифікації. Зловмисник, маючи доступ до апаратного програматора мікросхем EEPROM, може вручну обнулити лічильник мотогодин або скинути бітову маску порушень, після чого перерахувати значення CRC32.

Для запобігання фальсифікації в критичних промислових виробах застосовують апаратний криптографічний автентифікатор (наприклад, Microchip ATECC608 або NXP EdgeLock SE050):
- У захищеній пам'яті крипточипа зберігається 256-бітний фабричний секретний ключ K_audit.
- Кожен фінальний блок гарантійного журналу підписується обчисленням коду автентифікації повідомлення:

```
Auth_Tag = HMAC_SHA256(K_audit, Header_Data || Device_UUID || Violation_Flags)
```

Валідатор на сервісному стенді виконує запит до захищеного HSM-модуля або авторизованого сервера виробника, перевіряючи справжність підпису. Будь-яка невідповідність підпису однозначно свідчить про спробу підміни даних та призводить до негайного анулювання гарантії.

## Мапування на діагностичні коди несправностей (DTC за ISO 14229)

Для безшовної інтеграції з дилерськими та сервісними сканерами валідатор здійснює трансляцію апаратних прапорців журналу в стандартизовані діагностичні коди DTC (Diagnostic Trouble Codes):

- `FLAG_LIQUID_INGRESS` → `DTC 0x9A01` (Enclosure Liquid Ingress Detected).
- `FLAG_OVERVOLTAGE_EOS` → `DTC 0x0562` (System Power Supply Overvoltage Excursion).
- `FLAG_OVERHEAT` → `DTC 0x0119` (Thermal Junction Over-Temperature Shutdown).
- `FLAG_MECHANICAL_SHOCK` → `DTC 0x6205` (Excessive Acceleration Impact Peak).
- `FLAG_TAMPER_OPEN` → `DTC 0x9E04` (Security Tamper Mesh Circuit Breach).
- `FLAG_FW_UNAUTHORIZED` → `DTC 0x9E08` (Secure Boot Payload Signature Validation Fault).

## Регламент проведення технічної експертизи для сервісного персоналу

Під час надходження рекламаційного зразка уповноважений сервісний інженер дотримується стандартизованого протоколу аудиту:

1. **Вхідна фотофіксація:** Фотографування зовнішнього стану приладу, серійних номерів, гарантійних стиків та оптичних віконець LCI-індикаторів під ультрафіолетовим та видимим спектром освітлення для виявлення слідів висихання органічних рідин чи спроб відмивання плати у спиртових розчинах.
2. **Зняття контрольного дампу EEPROM:** Підключення діагностичного адаптера до захищеного порту стенда та зчитування повного бінарного образу в форматі `.bin` або `.hex`. Знятий дамп негайно підписується цифровим сертифікатом сервісного стенда та архівується в центральній базі даних рекламацій.
3. **Запуск автоматизованого валідатора:** Передача бінарного образу у валідатор із параметрами політики, що відповідають серійній ревізії виробу та конкретному контракту продажу.
4. **Оформлення технічного висновку:** Генерація звіту RMA. Якщо вердикт позитивний (`APPROVED`), виріб передається на лінію безоплатного ремонту або заміни. Якщо вердикт негативний (`REJECTED`), сформований звіт із графіком температурних піків та бінарними доказами перенапруги чи контакту з водою автоматично додається до офіційного листа-відповіді клієнту із зазначенням технічної причини відмови.

## Крайові випадки та аномалії обробки журналів

Під час проєктування валідатора враховано такі специфічні інженерні ситуації:

1. **Раптове знеструмлення (Brownout) під час запису в EEPROM:**
   Якщо живлення зникло в момент фіксації чергового запису аварії, контрольна сума CRC32 останнього блоку буде пошкоджена. Валідатор ізолює битий блок, не відкидаючи валідні попередні записи в кільцевому буфері.
2. **Збій годинника реального часу (RTC Battery Depletion):**
   Якщо літієва батарейка резервного живлення розрядилася нижче 2.0 В, календарний час RTC скидається на епоху за замовчуванням (1 січня 1970 або 2000 року). Валідатор спирається на монотонний лічильник POH, який не залежить від стану батарейки RTC.
3. **Множинні супутні порушення:**
   Якщо прилад одночасно зазнав затоплення та подальшого електричного пробою, валідатор фіксує всі виявлені фактори в діагностичному протоколі з визначенням первинної причини катастрофи.
4. **Хибні спрацьовування датчиків через електромагнітні завади (EMI):**
   Короткочасні сплески наведень можуть спричинити поодинокі збої АЦП. Валідатор перевіряє тривалість події за лічильником термічних циклів та кількістю підтверджених записів у буфері.
5. **Дрейф нульового рівня та термокомпенсація вимірювальних кіл:**
   Під час тривалої експлуатації вимірювальні резистивні шунти та операційні підсилювачі зазнають температурного дрейфу. Валідатор враховує технологічний допуск ±2.5% при оцінці граничних значень напруги перед ухваленням рішення про анулювання гарантії.

## Повна реалізація валідатора гарантійних умов

Нижче наведено робочий код повної утиліти валідації гарантійних логів двома мовами: C99 та C++20.

:::tabs
@tab C (C99)
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define WARRANTY_MAGIC          0x52524157U /* "WARR" */
#define WARRANTY_SCHEMA_V2      0x0002U
#define MAX_RECORDS_CAPACITY    32U

/* Бітові маски порушень */
#define FLAG_LIQUID_INGRESS     (1U << 0)
#define FLAG_OVERVOLTAGE_EOS    (1U << 1)
#define FLAG_OVERHEAT           (1U << 2)
#define FLAG_MECHANICAL_SHOCK   (1U << 3)
#define FLAG_TAMPER_OPEN        (1U << 4)
#define FLAG_FW_UNAUTHORIZED    (1U << 5)
#define FLAG_REV_POLARITY       (1U << 6)

typedef enum {
    DECISION_APPROVED = 0,
    DECISION_REJECTED_EXPIRED,
    DECISION_REJECTED_LIQUID,
    DECISION_REJECTED_ELECTRICAL,
    DECISION_REJECTED_THERMAL,
    DECISION_REJECTED_MECHANICAL,
    DECISION_REJECTED_TAMPER,
    DECISION_REJECTED_CORRUPTED
} warranty_decision_t;

#pragma pack(push, 1)

typedef struct {
    uint32_t timestamp_poh;
    uint16_t event_type;
    int16_t  peak_temperature_deci_c;
    uint32_t peak_voltage_mv;
    uint16_t peak_shock_deci_g;
    uint8_t  sensor_flags;
    uint8_t  reserved;
    uint32_t record_crc32;
} sensor_violation_entry_t;

typedef struct {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t header_len;
    uint8_t  device_uuid[16];
    uint32_t power_on_hours;
    uint32_t boot_count;
    uint32_t thermal_cycles;
    uint32_t violation_flags;
    int16_t  max_recorded_temp_deci_c;
    uint32_t max_recorded_voltage_mv;
    uint16_t max_recorded_shock_deci_g;
    uint16_t record_count;
    uint32_t header_crc32;
} warranty_image_header_t;

typedef struct {
    warranty_image_header_t header;
    sensor_violation_entry_t records[MAX_RECORDS_CAPACITY];
} warranty_eeprom_image_t;

#pragma pack(pop)

typedef struct {
    uint32_t max_allowed_poh;
    int16_t  max_allowed_temp_deci_c;
    uint32_t max_allowed_voltage_mv;
    uint16_t max_allowed_shock_deci_g;
    uint32_t max_thermal_dose_allowed;
} warranty_policy_t;

typedef struct {
    warranty_decision_t decision;
    uint32_t active_violations;
    uint32_t valid_records_parsed;
    uint32_t calculated_thermal_dose;
    char reason_details[256];
} rma_audit_report_t;

static uint32_t crc32_ieee(const uint8_t *buffer, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)buffer[i];
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc & 1U) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
        }
    }
    return crc ^ 0xFFFFFFFFU;
}

void init_default_policy(warranty_policy_t *policy) {
    if (!policy) return;
    policy->max_allowed_poh = 17520;           /* 2 роки цілодобової роботи */
    policy->max_allowed_temp_deci_c = 850;      /* 85.0 °C */
    policy->max_allowed_voltage_mv = 28000;     /* 28.0 В */
    policy->max_allowed_shock_deci_g = 500;     /* 50.0 g */
    policy->max_thermal_dose_allowed = 2000;    /* Градусо-годин перегріву */
}

void validate_warranty_log(
    const warranty_eeprom_image_t *image,
    const warranty_policy_t *policy,
    rma_audit_report_t *report
) {
    if (!image || !policy || !report) return;

    memset(report, 0, sizeof(rma_audit_report_t));

    /* 1. Перевірка цілісності заголовка */
    if (image->header.magic != WARRANTY_MAGIC ||
        image->header.schema_version != WARRANTY_SCHEMA_V2) {
        report->decision = DECISION_REJECTED_CORRUPTED;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Invalid image magic (0x%08X) or schema version (%d)",
                 image->header.magic, image->header.schema_version);
        return;
    }

    const size_t header_check_size = sizeof(warranty_image_header_t) - sizeof(uint32_t);
    const uint32_t computed_header_crc = crc32_ieee((const uint8_t *)&image->header, header_check_size);
    if (image->header.header_crc32 != computed_header_crc) {
        report->decision = DECISION_REJECTED_CORRUPTED;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Header CRC mismatch: stored=0x%08X, computed=0x%08X",
                 image->header.header_crc32, computed_header_crc);
        return;
    }

    report->active_violations = image->header.violation_flags;

    /* 2. Парсинг та валідація записів кільцевого буфера */
    uint16_t actual_records = image->header.record_count;
    if (actual_records > MAX_RECORDS_CAPACITY) {
        actual_records = MAX_RECORDS_CAPACITY;
    }

    uint32_t total_thermal_dose = 0;
    for (uint16_t i = 0; i < actual_records; ++i) {
        const sensor_violation_entry_t *rec = &image->records[i];
        const size_t rec_check_size = sizeof(sensor_violation_entry_t) - sizeof(uint32_t);
        const uint32_t computed_rec_crc = crc32_ieee((const uint8_t *)rec, rec_check_size);

        if (rec->record_crc32 == computed_rec_crc) {
            report->valid_records_parsed++;
            if (rec->peak_temperature_deci_c > policy->max_allowed_temp_deci_c) {
                total_thermal_dose += (uint32_t)(rec->peak_temperature_deci_c - policy->max_allowed_temp_deci_c);
            }
        }
    }
    report->calculated_thermal_dose = total_thermal_dose;

    /* 3. Оцінка політики та визначення вердикту */
    if (image->header.violation_flags & FLAG_LIQUID_INGRESS) {
        report->decision = DECISION_REJECTED_LIQUID;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Liquid Contact Indicator (LCI) or moisture sensor tripped");
        return;
    }

    if ((image->header.violation_flags & FLAG_TAMPER_OPEN) ||
        (image->header.violation_flags & FLAG_FW_UNAUTHORIZED)) {
        report->decision = DECISION_REJECTED_TAMPER;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Tamper seal enclosure opened or unauthorized firmware signature");
        return;
    }

    if ((image->header.violation_flags & FLAG_OVERVOLTAGE_EOS) ||
        (image->header.violation_flags & FLAG_REV_POLARITY) ||
        (image->header.max_recorded_voltage_mv > policy->max_allowed_voltage_mv)) {
        report->decision = DECISION_REJECTED_ELECTRICAL;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Electrical Overstress: peak voltage %u mV exceeds limit %u mV",
                 image->header.max_recorded_voltage_mv, policy->max_allowed_voltage_mv);
        return;
    }

    if ((image->header.violation_flags & FLAG_OVERHEAT) ||
        (image->header.max_recorded_temp_deci_c > policy->max_allowed_temp_deci_c) ||
        (total_thermal_dose > policy->max_thermal_dose_allowed)) {
        report->decision = DECISION_REJECTED_THERMAL;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Thermal abuse: peak %.1f C, cumulative dose %u deg-hours",
                 image->header.max_recorded_temp_deci_c / 10.0, total_thermal_dose);
        return;
    }

    if ((image->header.violation_flags & FLAG_MECHANICAL_SHOCK) ||
        (image->header.max_recorded_shock_deci_g > policy->max_allowed_shock_deci_g)) {
        report->decision = DECISION_REJECTED_MECHANICAL;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Mechanical shock: peak %.1f g exceeds limit %.1f g",
                 image->header.max_recorded_shock_deci_g / 10.0,
                 policy->max_allowed_shock_deci_g / 10.0);
        return;
    }

    if (image->header.power_on_hours > policy->max_allowed_poh) {
        report->decision = DECISION_REJECTED_EXPIRED;
        snprintf(report->reason_details, sizeof(report->reason_details),
                 "Operating hours expired: %u POH > limit %u POH",
                 image->header.power_on_hours, policy->max_allowed_poh);
        return;
    }

    report->decision = DECISION_APPROVED;
    snprintf(report->reason_details, sizeof(report->reason_details),
             "All sensor limits and policies validated successfully. Warranty repair approved.");
}

void print_audit_report(const rma_audit_report_t *report, const warranty_image_header_t *hdr) {
    if (!report || !hdr) return;

    printf("================ RMA DIAGNOSTIC REPORT ================\n");
    printf("Device UUID: ");
    for (int i = 0; i < 16; ++i) printf("%02X", hdr->device_uuid[i]);
    printf("\nOperating Hours (POH): %u hours | Boot Count: %u\n", hdr->power_on_hours, hdr->boot_count);
    printf("Max Temp: %.1f C | Max Voltage: %u mV | Max Shock: %.1f g\n",
           hdr->max_recorded_temp_deci_c / 10.0, hdr->max_recorded_voltage_mv,
           hdr->max_recorded_shock_deci_g / 10.0);
    printf("Valid Records Parsed: %u | Calculated Thermal Dose: %u\n",
           report->valid_records_parsed, report->calculated_thermal_dose);
    printf("-------------------------------------------------------\n");

    switch (report->decision) {
        case DECISION_APPROVED:
            printf("VERDICT: [APPROVED] Free Warranty Repair\n");
            break;
        case DECISION_REJECTED_LIQUID:
            printf("VERDICT: [REJECTED] Liquid Ingress Damage\n");
            break;
        case DECISION_REJECTED_ELECTRICAL:
            printf("VERDICT: [REJECTED] Electrical Overstress (EOS)\n");
            break;
        case DECISION_REJECTED_THERMAL:
            printf("VERDICT: [REJECTED] Thermal Operating Limit Exceeded\n");
            break;
        case DECISION_REJECTED_MECHANICAL:
            printf("VERDICT: [REJECTED] Mechanical Shock / Impact\n");
            break;
        case DECISION_REJECTED_TAMPER:
            printf("VERDICT: [REJECTED] Tamper Seal Breach / Unauthorized Mod\n");
            break;
        case DECISION_REJECTED_EXPIRED:
            printf("VERDICT: [REJECTED] Warranty Operating Period Expired\n");
            break;
        case DECISION_REJECTED_CORRUPTED:
            printf("VERDICT: [REJECTED] Log Checksum / Integrity Failure\n");
            break;
    }
    printf("Reason: %s\n", report->reason_details);
    printf("=======================================================\n");
}
```
@tab C++ (C++20)
```cpp
#include <iostream>
#include <iomanip>
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <string>
#include <string_view>
#include <expected>
#include <algorithm>

namespace warranty_validator {

inline constexpr uint32_t kMagic = 0x52524157U; // "WARR"
inline constexpr uint16_t kSchemaV2 = 0x0002U;
inline constexpr size_t kMaxRecords = 32;

enum class ViolationFlag : uint32_t {
    None             = 0,
    LiquidIngress    = 1U << 0,
    OvervoltageEos   = 1U << 1,
    Overheat         = 1U << 2,
    MechanicalShock  = 1U << 3,
    TamperOpen       = 1U << 4,
    FirmwareUnauth   = 1U << 5,
    ReversePolarity  = 1U << 6
};

[[nodiscard]] constexpr ViolationFlag operator|(ViolationFlag a, ViolationFlag b) noexcept {
    return static_cast<ViolationFlag>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr bool has_flag(ViolationFlag value, ViolationFlag flag) noexcept {
    return (static_cast<uint32_t>(value) & static_cast<uint32_t>(flag)) != 0;
}

enum class RmaVerdict : uint8_t {
    ApprovedWarranty,
    RejectedExpired,
    RejectedLiquid,
    RejectedElectrical,
    RejectedThermal,
    RejectedMechanical,
    RejectedTamper,
    RejectedCorrupted
};

#pragma pack(push, 1)

struct SensorViolationEntry {
    uint32_t timestamp_poh{0};
    uint16_t event_type{0};
    int16_t  peak_temperature_deci_c{0};
    uint32_t peak_voltage_mv{0};
    uint16_t peak_shock_deci_g{0};
    uint8_t  sensor_flags{0};
    uint8_t  reserved{0};
    uint32_t record_crc32{0};
};

struct WarrantyImageHeader {
    uint32_t magic{kMagic};
    uint16_t schema_version{kSchemaV2};
    uint16_t header_len{sizeof(WarrantyImageHeader)};
    std::array<uint8_t, 16> device_uuid{};
    uint32_t power_on_hours{0};
    uint32_t boot_count{0};
    uint32_t thermal_cycles{0};
    ViolationFlag violation_flags{ViolationFlag::None};
    int16_t  max_recorded_temp_deci_c{0};
    uint32_t max_recorded_voltage_mv{0};
    uint16_t max_recorded_shock_deci_g{0};
    uint16_t record_count{0};
    uint32_t header_crc32{0};
};

struct WarrantyEepromImage {
    WarrantyImageHeader header;
    std::array<SensorViolationEntry, kMaxRecords> records{};
};

#pragma pack(pop)

struct PolicyConfig {
    uint32_t max_allowed_poh{17520};          // 2 роки
    int16_t  max_allowed_temp_deci_c{850};     // 85.0 °C
    uint32_t max_allowed_voltage_mv{28000};    // 28.0 В
    uint16_t max_allowed_shock_deci_g{500};    // 50.0 g
    uint32_t max_thermal_dose_allowed{2000};   // Градусо-годин перегріву
};

struct AuditReport {
    RmaVerdict verdict{RmaVerdict::RejectedCorrupted};
    ViolationFlag active_violations{ViolationFlag::None};
    uint32_t valid_records_parsed{0};
    uint32_t calculated_thermal_dose{0};
    std::string details{};
};

[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (const uint8_t byte : data) {
        crc ^= static_cast<uint32_t>(byte);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 1U) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
        }
    }
    return crc ^ 0xFFFFFFFFU;
}

class WarrantyValidatorEngine {
public:
    [[nodiscard]] static AuditReport evaluate(
        const WarrantyEepromImage& image,
        const PolicyConfig& policy
    ) noexcept {
        AuditReport report{};
        const auto& hdr = image.header;

        // 1. Перевірка магічного підпису та схеми
        if (hdr.magic != kMagic || hdr.schema_version != kSchemaV2) {
            report.verdict = RmaVerdict::RejectedCorrupted;
            report.details = "Invalid EEPROM image signature or unsupported schema version";
            return report;
        }

        // 2. Перевірка CRC32 заголовка
        constexpr size_t kHeaderCrcSize = sizeof(WarrantyImageHeader) - sizeof(uint32_t);
        const auto header_span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&hdr), kHeaderCrcSize
        );
        if (hdr.header_crc32 != calculate_crc32(header_span)) {
            report.verdict = RmaVerdict::RejectedCorrupted;
            report.details = "Header CRC32 integrity checksum mismatch";
            return report;
        }

        report.active_violations = hdr.violation_flags;

        // 3. Аналіз записів подій
        const uint16_t records_to_parse = std::min<uint16_t>(hdr.record_count, kMaxRecords);
        uint32_t total_thermal_dose = 0;

        for (size_t i = 0; i < records_to_parse; ++i) {
            const auto& rec = image.records[i];
            constexpr size_t kRecCrcSize = sizeof(SensorViolationEntry) - sizeof(uint32_t);
            const auto rec_span = std::span<const uint8_t>(
                reinterpret_cast<const uint8_t*>(&rec), kRecCrcSize
            );

            if (rec.record_crc32 == calculate_crc32(rec_span)) {
                report.valid_records_parsed++;
                if (rec.peak_temperature_deci_c > policy.max_allowed_temp_deci_c) {
                    total_thermal_dose += static_cast<uint32_t>(rec.peak_temperature_deci_c - policy.max_allowed_temp_deci_c);
                }
            }
        }
        report.calculated_thermal_dose = total_thermal_dose;

        // 4. Оцінка політик відповідності
        if (has_flag(hdr.violation_flags, ViolationFlag::LiquidIngress)) {
            report.verdict = RmaVerdict::RejectedLiquid;
            report.details = "Liquid Contact Indicator (LCI) or moisture sensor triggered";
            return report;
        }

        if (has_flag(hdr.violation_flags, ViolationFlag::TamperOpen) ||
            has_flag(hdr.violation_flags, ViolationFlag::FirmwareUnauth)) {
            report.verdict = RmaVerdict::RejectedTamper;
            report.details = "Tamper switch open event or unauthorized firmware signature";
            return report;
        }

        if (has_flag(hdr.violation_flags, ViolationFlag::OvervoltageEos) ||
            has_flag(hdr.violation_flags, ViolationFlag::ReversePolarity) ||
            hdr.max_recorded_voltage_mv > policy.max_allowed_voltage_mv) {
            report.verdict = RmaVerdict::RejectedElectrical;
            report.details = "Electrical overstress: voltage exceeded maximum ratings";
            return report;
        }

        if (has_flag(hdr.violation_flags, ViolationFlag::Overheat) ||
            hdr.max_recorded_temp_deci_c > policy.max_allowed_temp_deci_c ||
            total_thermal_dose > policy.max_thermal_dose_allowed) {
            report.verdict = RmaVerdict::RejectedThermal;
            report.details = "Thermal abuse: temperature limit or cumulative thermal dose exceeded";
            return report;
        }

        if (has_flag(hdr.violation_flags, ViolationFlag::MechanicalShock) ||
            hdr.max_recorded_shock_deci_g > policy.max_allowed_shock_deci_g) {
            report.verdict = RmaVerdict::RejectedMechanical;
            report.details = "Mechanical shock peak exceeded drop-impact threshold";
            return report;
        }

        if (hdr.power_on_hours > policy.max_allowed_poh) {
            report.verdict = RmaVerdict::RejectedExpired;
            report.details = "Total operating hours exceeded contractual warranty limit";
            return report;
        }

        report.verdict = RmaVerdict::ApprovedWarranty;
        report.details = "Device operated strictly within specified limits. Warranty approved.";
        return report;
    }
};

void display_report(const AuditReport& report, const WarrantyImageHeader& hdr) {
    std::cout << "================ RMA DIAGNOSTIC REPORT ================\n";
    std::cout << "Device UUID: ";
    for (const uint8_t byte : hdr.device_uuid) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    std::cout << std::dec << "\n";
    std::cout << "POH: " << hdr.power_on_hours << " h | Boot Count: " << hdr.boot_count << "\n";
    std::cout << "Max Temp: " << (hdr.max_recorded_temp_deci_c / 10.0) << " C | "
              << "Max Voltage: " << hdr.max_recorded_voltage_mv << " mV | "
              << "Max Shock: " << (hdr.max_recorded_shock_deci_g / 10.0) << " g\n";
    std::cout << "Valid Records: " << report.valid_records_parsed
              << " | Thermal Dose: " << report.calculated_thermal_dose << "\n";
    std::cout << "-------------------------------------------------------\n";

    switch (report.verdict) {
        case RmaVerdict::ApprovedWarranty:
            std::cout << "VERDICT: [APPROVED] Free Warranty Repair\n";
            break;
        case RmaVerdict::RejectedLiquid:
            std::cout << "VERDICT: [REJECTED] Liquid Damage\n";
            break;
        case RmaVerdict::RejectedElectrical:
            std::cout << "VERDICT: [REJECTED] Electrical Overstress (EOS)\n";
            break;
        case RmaVerdict::RejectedThermal:
            std::cout << "VERDICT: [REJECTED] Thermal Excursion\n";
            break;
        case RmaVerdict::RejectedMechanical:
            std::cout << "VERDICT: [REJECTED] Mechanical Impact Damage\n";
            break;
        case RmaVerdict::RejectedTamper:
            std::cout << "VERDICT: [REJECTED] Tamper / Unauthorized Modification\n";
            break;
        case RmaVerdict::RejectedExpired:
            std::cout << "VERDICT: [REJECTED] Warranty Term Expired\n";
            break;
        case RmaVerdict::RejectedCorrupted:
            std::cout << "VERDICT: [REJECTED] Corrupted Log Image\n";
            break;
    }
    std::cout << "Details: " << report.details << "\n";
    std::cout << "=======================================================\n";
}

} // namespace warranty_validator
```
:::

## Інтеграція в тестові конвеєри та сервісні бази даних

Представлений модуль може бути скомпільований як автономна консольна утиліта CLI, динамічна бібліотека `.so` / `.dll` для інтеграції у фірмове ПЗ сервісних центрів або вбудований безпосередньо у прошивку автоматизованих тестових стендів (ATE) на базі Linux чи FreeRTOS.

Під час виконання тесту утиліта формує структурований JSON-об'єкт, сумісний із системами управління рекламаціями (ERP / CRM), що містить:
- Унікальний ідентифікатор пристрою (`device_uuid`).
- Загальну кількість відпрацьваних мотогодин (`power_on_hours`).
- Перелік активних прапорців порушень (`violation_flags`).
- Підсумковий статус рішення RMA (`verdict_code`).
- Текстове інженерне обґрунтування для включення в офіційний протокол технічної експертизи.

Завдяки відокремленню структури бінарних даних від параметрів конфігурації політик, порогові значення напруги, температури та прискорення можуть легко налаштовуватися під різні лінійки виробів (наприклад, комерційні прилади 0–70 °C чи промислові модулі -40–+85 °C) без необхідності перекомпіляції ядра аналізу логів.
