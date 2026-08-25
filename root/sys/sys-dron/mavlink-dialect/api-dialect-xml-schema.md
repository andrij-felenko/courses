# Специфікація XML-схеми діалектів MAVLink

Машиночитний опис протоколу MAVLink базується на декларативних документах у форматі XML. Кожен файл діалекту є формальною схемою, з якої компілятор `mavgen` генерує бінарні структури даних, функції серіалізації, константи числових переліків та розрахунок контрольних сум `CRC_EXTRA` для цільових мов програмування (C, C++, Python, Rust, Go, Java). Цей довідник містить повну специфікацію структури XML-документа діалекту, правила вкладеності тегів, допустимі атрибути, матрицю відображення типів даних та вимоги валідації.

---

### 1. Коренева структура документа: тег `<mavlink>`

Будь-який файл діалекту є валідним XML-документом, коренем якого є обов'язковий елемент `<mavlink>`.

```xml
<?xml version="1.0"?>
<mavlink>
  <include>common.xml</include>
  <version>3</version>
  <dialect>42</dialect>

  <enums>
    <!-- Визначення числових переліків і команд -->
  </enums>

  <messages>
    <!-- Визначення бінарних структур повідомлень -->
  </messages>
</mavlink>
```

#### Службові дочірні елементи верхнього рівня

| Тег | Кратність | Призначення та системна поведінка |
| :--- | :--- | :--- |
| `<include>` | 0 .. N | Підключає батьківський XML-файл діалекту. Шлях вказується відносно поточної теки схем. Парсер рекурсивно об'єднує всі включені файли, формуючи єдине дерево AST та запобігаючи повторному завантаженню дублікатів. |
| `<version>` | 0 .. 1 | Ціле число від 1 до 255 (наприклад, `<version>3</version>`), що визначає мінорну версію діалекту. Це значення компілятор автоматично підставляє у константу `MAVLINK_VERSION` та у поле `mavlink_version` повідомлення `HEARTBEAT`. |
| `<dialect>` | 0 .. 1 | Числовий ідентифікатор діалекту (ціле додатне число). Використовується генератором для створення захисних макросів заголовкових файлів бібліотеки. |
| `<enums>` | 0 .. 1 | Контейнер для всіх числових переліків, бітових масок та навігаційних команд `MAV_CMD`. |
| `<messages>` | 0 .. 1 | Контейнер для всіх визначень двійкових повідомлень. |

---

### 2. Секція переліків: елементи `<enums>` та `<enum>`

Елемент `<enums>` групує всі переліки діалекту. Кожен окремий перелік описується тегом `<enum>`. Переліки можуть виступати як звичайними взаємовиключними списками станів, так і бітовими масками або словниками команд.

```xml
<enum name="LASER_RANGEFINDER_STATE" bitmask="false">
  <description>Робочі стани лазерного модуля далекоміра.</description>
  <entry value="0" name="LASER_STATE_OFF">
    <description>Модуль знеструмлено або лазерний діод вимкнено.</description>
  </entry>
  <entry value="1" name="LASER_STATE_STANDBY">
    <description>Режим очікування готовності до імпульсного пострілу.</description>
  </entry>
  <entry value="2" name="LASER_STATE_ACTIVE">
    <description>Випромінювання активне, триває періодичне сканування дистанції.</description>
  </entry>
  <entry value="4" name="LASER_STATE_FAULT">
    <description>Аварійний стан: критичний перегрів оптичного випромінювача.</description>
  </entry>
</enum>
```

#### Атрибути елемента `<enum>`

* **`name`** *(обов'язковий, рядок)* — унікальний машинний ідентифікатор переліку у верхньому регістрі (наприклад, `MAV_AUTOPILOT`, `MAV_TYPE`, `GIMBAL_DEVICE_FLAGS`). Використовується як ім'я типу `enum` у згенерованому коді C/C++ та Rust.
* **`bitmask`** *(необов'язковий, boolean: `"true"` або `"false"`)* — якщо встановлено `"true"`, константи переліку інтерпретуються як позиційні бітові маски (`1`, `2`, `4`, `8`, `16`, `...`). У генераторах C/C++ це поле генерує сумісні оператори побітового «АБО» (`|`), а в графічних інтерфейсах (QGroundControl) відображає список незалежних прапорців-перемикачів замість спадного списку (dropdown).

#### Дочірні елементи `<entry>`
Кожне окреме значення всередині `<enum>` задається тегом `<entry>`:

* **`value`** *(обов'язковий, ціле число)* — числове значення константи. Дозволяються десяткові числа (`value="1"`) або шістнадцяткові літерали (`value="0x04"`).
* **`name`** *(обов'язковий, рядок)* — глобально унікальне ім'я константи (наприклад, `MAV_STATE_ACTIVE`). Ім'я повинно бути унікальним у межах усього простору імен прошивки, оскільки в мові C константи `enum` мають глобальну видимість.
* **`<description>`** *(необов'язковий)* — текст документації, який переноситься у Doxygen-коментарі кодека.

#### Атрибути життєвого циклу констант

```xml
<entry value="10" name="OLD_FEATURE_MODE">
  <deprecated since="2024-01" replaced_by="NEW_FEATURE_MODE">Застарілий режим; використовуйте NEW_FEATURE_MODE.</deprecated>
  <description>Опис старої константи.</description>
</entry>

<entry value="11" name="EXPERIMENTAL_MODE">
  <wip>Чорновий режим: проходить польові випробування, структура може змінюватися.</wip>
  <description>Експериментальний режим.</description>
</entry>
```

* **`<deprecated>`** — позначає константу як застарілу. Підтримує атрибути `since` (дата вилучення) та `replaced_by` (ім'я рекомендованої заміни). Генератор C/C++ додає атрибут `[[deprecated]]` або `__attribute__((deprecated))`.
* **`<wip>`** — позначає константу як робочу версію (Work In Progress). Попереджає сторонніх розробників про можливі несумісні зміни у наступних релізах.

---

### 3. Специфікація навігаційних команд: `<enum name="MAV_CMD">`

Перелік `MAV_CMD` є спеціалізованим ядром командного інтерфейсу MAVLink. Записи цього переліку описують дії, які надсилаються апарату через повідомлення `COMMAND_LONG` (#76) або `COMMAND_INT` (#75).

Кожна команда містить до 7 параметрів з плаваючою комою, призначення яких документується тегами `<param index="1..7">`:

```xml
<enum name="MAV_CMD">
  <entry value="42050" name="MAV_CMD_DO_TRIGGER_SPECTRAL_SCAN">
    <description>Запустити процес спектрального сканування цілі.</description>
    <param index="1" label="Довжина хвилі (нм)" minValue="400" maxValue="1100" default="850">
      Центральна довжина оптичної хвилі сенсора.
    </param>
    <param index="2" label="Час експозиції (мс)" units="ms" minValue="1" maxValue="5000" default="100">
      Тривалість накопичення заряду матриці.
    </param>
    <param index="3" label="Кількість знімків" minValue="1" maxValue="100" increment="1" default="1">
      Кількість кадрів у серії.
    </param>
    <param index="4" label="Режим фільтра" enum="SPECTRAL_FILTER_TYPE" default="0">
      Тип активного оптичного фільтра.
    </param>
    <param index="5" label="Зарезервовано">Порожній слот (передавати NaN).</param>
    <param index="6" label="Зарезервовано">Порожній слот (передавати NaN).</param>
    <param index="7" label="Зарезервовано">Порожній слот (передавати NaN).</param>
  </entry>
</enum>
```

#### Атрибути елемента `<param>`

| Атрибут | Тип | Опис та застосування |
| :--- | :--- | :--- |
| `index` | ціле (1..7) | **Обов'язковий.** Номер слота параметра у повідомленні `COMMAND_LONG` / `COMMAND_INT`. |
| `label` | рядок | Короткий людиночитний заголовок для відображення в інтерфейсі наземної станції QGC. |
| `units` | рядок | Фізичні одиниці вимірювання (`m`, `m/s`, `deg`, `cdeg`, `ms`, `Hz`, `%`, `V`, `A`). |
| `enum` | рядок | Посилання на перелік `<enum>`, значення якого допустимі для цього параметра. |
| `minValue` | число | Мінімально допустиме значення для валідації введених оператором даних. |
| `maxValue` | число | Максимально допустиме значення для валідації введених оператором даних. |
| `increment` | число | Крок зміни значення у графічному інтерфейсі (стрілочки вгору/вниз). |
| `default` | число | Значення за замовчуванням, яке підставляється під час створення місії. |
| `decimalDigits` | ціле | Кількість знаків після коми для відображення у формі вводу. |
| `reserved` | boolean | Якщо `"true"`, позначає слот як невикористаний (у кадрі передається `0` або `NaN`). |

---

### 4. Секція повідомлень: елементи `<messages>` та `<message>`

Секція `<messages>` містить перелік усіх бінарних повідомлень діалекту.

```xml
<message id="42010" name="PAYLOAD_SPECTRAL_STATUS">
  <description>Телеметричний статус мультиспектрального сенсора.</description>
  <field type="uint32_t" name="time_boot_ms" units="ms">Час роботи з моменту старту.</field>
  <field type="float"    name="integration_time_ms" units="ms">Фактичний час інтегрування.</field>
  <field type="float"    name="sensor_temperature" units="degC">Температура матриці в градусах Цельсія.</field>
  <field type="uint16_t" name="spectral_irradiance" units="mW/m^2">Сумарна освітленість.</field>
  <field type="uint8_t"  name="filter_mode" enum="SPECTRAL_FILTER_TYPE">Активний оптичний фільтр.</field>
  <field type="uint8_t"  name="status_flags" display="bitmask" enum="PAYLOAD_STATUS_FLAGS">Прапорці стану.</field>
  <extensions/>
  <field type="uint32_t" name="calibration_crc">Контрольна сума поточної калібрувальної матриці.</field>
  <field type="uint8_t"  name="gain_level" default="1">Коефіцієнт аналогового підсилення сенсора.</field>
</message>
```

#### Атрибути елемента `<message>`
* **`id`** *(обов'язковий, ціле число)* — числовий Message ID. Для кастомних приватних діалектів повинен належати діапазону `42000 .. 42999`.
* **`name`** *(обов'язковий, рядок)* — машиночитне ім'я повідомлення у верхньому регістрі.

#### Структура тіла `<message>`
Тіло повідомлення складається з послідовності тегів `<field>`, розділених опціональним одинарним тегом `<extensions/>`:
1. **Базові поля (до `<extensions/>`):**
   * Сортуються генератором за спаданням розміру типу (8B → 4B → 2B → 1B).
   * Беруть участь у формуванні хешу `CRC_EXTRA`.
   * Обов'язкові для передачі у MAVLink 1 та MAVLink 2.
2. **Розділювач `<extensions/>`:**
   * Одинарний тег, який позначає початок розширеної частини повідомлення у MAVLink 2.
3. **Розширені поля (після `<extensions/>`):**
   * Розташовуються в пам'яті суворо у порядку оголошення в XML (не сортуються).
   * **Не впливають** на значення `CRC_EXTRA`.
   * Підтримують механізм нульового обтинання (Zero-Truncation) в ефірі.

---

### 5. Система типів полів `<field>` та їхня матриця відображення

MAVLink гарантує сувору бінарну сумісність завдяки фіксованій розрядності та детермінованому порядку байтів (little-endian) на фізичній лінії зв'язку.

#### Матриця відповідності типів MAVLink цільовим мовам

| Тип MAVLink XML | Розмір (байт) | C/C++ тип | Python (`struct`) | Rust тип | Go тип | Вирівнювання (байт) |
| :--- | :---: | :--- | :---: | :--- | :--- | :---: |
| `uint8_t` | 1 | `uint8_t` | `B` (int) | `u8` | `uint8` | 1 |
| `int8_t` | 1 | `int8_t` | `b` (int) | `i8` | `int8` | 1 |
| `char` | 1 | `char` | `c` (bytes) | `char` / `u8` | `byte` | 1 |
| `uint16_t` | 2 | `uint16_t` | `H` (int) | `u16` | `uint16` | 2 |
| `int16_t` | 2 | `int16_t` | `h` (int) | `i16` | `int16` | 2 |
| `uint32_t` | 4 | `uint32_t` | `I` (int) | `u32` | `uint32` | 4 |
| `int32_t` | 4 | `int32_t` | `i` (int) | `i32` | `int32` | 4 |
| `uint64_t` | 8 | `uint64_t` | `Q` (int) | `u64` | `uint64` | 8 |
| `int64_t` | 8 | `int64_t` | `q` (int) | `i64` | `int64` | 8 |
| `float` | 4 | `float` (IEEE 754) | `f` (float) | `f32` | `float32` | 4 |
| `double` | 8 | `double` (IEEE 754) | `d` (float) | `f64` | `float64` | 8 |
| `uint8_t_mavlink_version` | 1 | `uint8_t` | `B` (int) | `u8` | `uint8` | 1 |

#### Статичні масиви та рядки
Статичні масиви оголошуються додаванням розмірності в квадратних дужках:
* `type="uint16_t[4]"` — масив із 4 елементів розміром 2 байти кожен (загальний розмір 8 байтів).
* `type="char[16]"` — текстовий рядок фіксованої довжини 16 байтів. Якщо рядок коротший за 16 символів, він повинен закінчуватися нуль-термінатором `\0`, а всі наступні байти заповнюються нулями.
* Масиви розглядаються сортувальником за розміром **одного елемента**, а не всього масиву: `uint16_t[4]` сортується серед 2-байтових полів.

#### Атрибути елемента `<field>`

| Атрибут | Тип | Опис та правила використання |
| :--- | :--- | :--- |
| `type` | рядок | **Обов'язковий.** Базовий тип із таблиці або одновимірний масив `type="T[N]"`. |
| `name` | рядок | **Обов'язковий.** Машинне ім'я поля в нижньому регістрі (`snake_case`). |
| `enum` | рядок | Посилання на перелік `<enum>`, що визначає допустимі значення для цього поля. |
| `display` | рядок | `"bitmask"` — відображати поле як набір окремих прапорців. |
| `units` | рядок | Одиниці вимірювання за міжнародною системою SI (`m`, `rad`, `deg`, `cdeg`, `s`, `ms`, `us`, `degC`, `V`, `A`, `m/s`, `rad/s`, `Hz`, `%`). |
| `print_format` | рядок | Форматний рядок для `printf` (наприклад, `print_format="%.3f"`). |
| `default` | рядок | Значення за замовчуванням при ініціалізації структури. |
| `invalid` | рядок | Число, що сигналізує про відсутність даних сенсора (`invalid="NaN"` для `float`, `invalid="UINT32_MAX"`). |
| `instance` | boolean | Якщо `"true"`, позначає поле як індекс датчика у мультисенсорних конфігураціях (наприклад, номер IMU або номер батареї). |

---

### 6. Словник стандартизованих одиниць вимірювання (`units`)

MAVLink підтримує фіксований перелік одиниць вимірювання у тегах полів та параметрів команд. Використання стандартизованих значень гарантує, що наземні станції керування (QGroundControl, Mission Planner) зможуть коректно відображати дані у вибраній користувачем системі мір:

* **Відстань і довжина:** `m` (метри), `cm` (сантиметри), `mm` (міліметри), `km` (кілометри).
* **Швидкість:** `m/s` (метри за секунду), `cm/s` (сантиметри за секунду), `km/h` (кілометри за годину).
* **Прискорення:** `m/s/s` або `m/s^2` (метри за секунду в квадраті), `mg` (мілі-g).
* **Кути та орієнтація:** `rad` (радіани), `rad/s` (радіани за секунду), `deg` (градуси), `cdeg` (соті долі градуса, `deg · 100`), `degE7` (градуси, помножені на `10^7` для координат WGS-84), `deg/s` (градуси за секунду).
* **Час:** `s` (секунди), `ds` (децисекунди), `cs` (сантисекунди), `ms` (мілісекунди), `us` (мікросекунди), `ns` (наносекунди), `Hz` (герци), `kHz`, `MHz`, `rpm` (оберти за хвилину).
* **Електрика та живлення:** `V` (вольти), `mV` (мілівольти), `cV` (сантивольти), `A` (ампери), `mA` (міліампери), `cA` (сантиампери), `Ah` (ампер-години), `mAh` (міліампер-години), `Wh` (ват-години), `W` (вати), `mW` (мілівати), `J` (джоулі).
* **Температура:** `degC` (градуси Цельсія), `cdegC` (соті долі градуса Цельсія), `K` (кельвіни).
* **Тиск та магнетизм:** `hPa` (гектопаскалі / мілібари), `Pa` (паскалі), `bar` (бари), `mbar` (мілібари), `gauss` (гауси), `mG` (мілігауси), `nT` (нанотесли).
* **Об'єм даних та швидкість передачі:** `B` (байти), `kB` (кілобайти), `MB` (мегабайти), `B/s` (байти за секунду), `kB/s` (кілобайти за секунду), `KiB` (кібібайти), `MiB` (мебібайти).
* **Відносні величини:** `%` (відсотки, 0..100), `d%` (десяті долі відсотка), `c%` (соті долі відсотка), `ratio` (коефіцієнт від 0.0 до 1.0), `dB` (децибели), `dBm` (децибел-мілівати).

---

### 7. Специфікація прапорців протоколу MAVLink 2

Заголовок кадру MAVLink 2 містить два байти керуючих бітових прапорців: `incompat_flags` та `compat_flags`.

#### Прапорці несумісності (`incompat_flags`, `MAVLINK_IFLAG`)
Якщо парсер виявляє встановлений біт, якого немає у його скомпільованій таблиці, пакет **негайно відхиляється**.

| Біт | Маска | Константа C | Призначення |
| :---: | :---: | :--- | :--- |
| 0 | `0x01` | `MAVLINK_IFLAG_SIGNED` | Пакет захищено цифровим підписом HMAC-SHA256 (до кадру додано 13 байтів аутентифікації). |
| 1..7 | `0x02..0x80` | *Зарезервовано* | Зарезервовано для майбутніх структурних змін формату кадру на фізичному рівні. |

#### Прапорці сумісності (`compat_flags`, `MAVLINK_CFLAG`)
Якщо парсер виявляє невідомий встановлений біт, він **ігнорує його** та продовжує штатний розбір корисних даних.

| Біт | Маска | Константа C | Призначення |
| :---: | :---: | :--- | :--- |
| 0..7 | `0x01..0x80` | *Зарезервовано* | Інформаційні прапорці маршрутизації, пріоритету або додаткових опцій каналу зв'язку. |

---

### 8. Опції генератора коду `mavgen` (CLI Reference)

Інструмент генерації коду `mavgen` є частиною бібліотеки `pymavlink` і підтримує гнучку конфігурацію параметрів компіляції діалектів:

```bash
python -m pymavlink.tools.mavgen \
    --lang=C \
    --wire-protocol=2.0 \
    --output=build/mavlink \
    --error-limit=5 \
    --strict-units \
    my_custom_dialect.xml
```

#### Параметри командного рядка `mavgen`

* **`--lang={C,C++11,Python,CS,WLua,ObjC,Java}`** — цільова мова програмування для згенерованого кодека.
* **`--wire-protocol={1.0,2.0}`** — версія бінарного формату кадру (за замовчуванням `2.0`). Для підтримки Message ID понад 255 обов'язково вказуйте `2.0`.
* **`--output=<DIRECTORY_OR_FILE>`** — цільова тека (для мов C/C++) або ім'я вихідного файлу (для Python).
* **`--error-limit=<N>`** — максимальна кількість помилок парсингу XML перед перериванням роботи (за замовчуванням `5`).
* **`--strict-units`** — вмикає сувору валідацію одиниць вимірювання за офіційним словником MAVLink. За наявності нестандартного значення генерація завершується з помилкою.
* **`--no-validate`** — вимикає перевірку діапазонів Message ID та повторюваних констант (не рекомендується у виробничих середовищах).

---

### 9. Алгоритм сортування полів та природне вирівнювання

Щоб сгенеровані C-структури можна було накладати безпосередньо на буфер прийому DMA без виникнення винятків апаратного вирівнювання (`unaligned memory access fault`) на архітектурах ARM Cortex-M0/M3, генератор сортує базові поля повідомлення.

#### Кроки алгоритму сортування

1. Вхідний список полів повідомлення розділяється на дві групи: базові поля (до `<extensions/>`) та розширені поля (після `<extensions/>`).
2. Кожному базовому полю присвоюється ключ сортування:
   * Розмір базового типу в байтах: `uint64_t`/`double` = 8, `uint32_t`/`float` = 4, `uint16_t`/`int16_t` = 2, `uint8_t`/`char` = 1.
   * Для масивів `T[N]` розмір визначається за базовим типом `T` (масив `uint16_t[4]` отримує розмір 2).
3. Виконується **стійке сортування (stable sort)** за незростанням розміру типу (від 8 до 1). Стійкість гарантує, що поля однакового розміру зберігають свій початковий порядок з XML-файлу.
4. Розширені поля додаються до кінця відсортованого списку без перевпорядкування.

```
Приклад сортування повідомлення SENSOR_DATA:
Початковий порядок в XML:
  1. uint8_t  sensor_id   (розмір 1)
  2. uint64_t timestamp   (розмір 8)
  3. float    voltage     (розмір 4)
  4. uint16_t raw_val[4]  (розмір 2)
  5. uint8_t  mode        (розмір 1)

Порядок на дроті після сортування (базовий розмір = 22 байти):
  Зміщення 0..7  : uint64_t timestamp   (кратне 8 ✓)
  Зміщення 8..11 : float    voltage     (кратне 4 ✓)
  Зміщення 12..19: uint16_t raw_val[4]  (кратне 2 ✓)
  Зміщення 20    : uint8_t  sensor_id   (кратне 1 ✓)
  Зміщення 21    : uint8_t  mode        (кратне 1 ✓)
```

Усі зміщення полів строго діляться на розмір свого типу, що дозволяє виконувати розпакування за одну операцію копіювання пам'яті (`memcpy`).

---

### 10. Структура згенерованого C/C++ коду

Для кожного повідомлення генератор створює окремий заголовковий файл `mavlink_msg_<name_lowercase>.h`, який містить три ключові компоненти:

1. **Макроси метаданих повідомлення:**

:::tabs
```c
/* Згенеровані макроси метаданих C */
#define MAVLINK_MSG_ID_PAYLOAD_SPECTRAL_STATUS 42010
#define MAVLINK_MSG_ID_PAYLOAD_SPECTRAL_STATUS_LEN 17
#define MAVLINK_MSG_ID_PAYLOAD_SPECTRAL_STATUS_MIN_LEN 12
#define MAVLINK_MSG_ID_PAYLOAD_SPECTRAL_STATUS_CRC 185
```
```cpp
// Згенеровані типізовані константи C++
namespace mavlink::custom {
constexpr uint32_t MSG_ID_PAYLOAD_SPECTRAL_STATUS = 42010;
constexpr uint8_t  MSG_LEN_PAYLOAD_SPECTRAL_STATUS = 17;
constexpr uint8_t  MSG_MIN_LEN_PAYLOAD_SPECTRAL_STATUS = 12;
constexpr uint8_t  MSG_CRC_PAYLOAD_SPECTRAL_STATUS = 185;
}
```
:::

   * `LEN` — повна максимальна довжина повідомлення включно з розширеними полями (17 байтів).
   * `MIN_LEN` — базова довжина повідомлення до тегу `<extensions/>` (12 байтів).
   * `CRC` — байт `CRC_EXTRA` (185), обчислений для базової частини.

2. **Двійкова структура даних:**

:::tabs
```c
/* Згенерована запакована структура C */
MAVPACKED(
typedef struct __mavlink_payload_spectral_status_t {
    uint32_t time_boot_ms;        /*< [ms] Час роботи */
    float integration_time_ms;   /*< [ms] Час інтегрування */
    float sensor_temperature;    /*< [degC] Температура */
    uint16_t spectral_irradiance;/*< [mW/m^2] Освітленість */
    uint8_t filter_mode;         /*< Активний фільтр */
    uint8_t status_flags;        /*< Прапорці */
    uint32_t calibration_crc;    /*< [ext] Контрольна сума калібрування */
    uint8_t gain_level;          /*< [ext] Підсилення */
}) mavlink_payload_spectral_status_t;
```
```cpp
// Згенерована типізована структура C++
namespace mavlink::custom::msg {

struct alignas(8) PAYLOAD_SPECTRAL_STATUS {
    uint32_t time_boot_ms;
    float integration_time_ms;
    float sensor_temperature;
    uint16_t spectral_irradiance;
    uint8_t filter_mode;
    uint8_t status_flags;
    uint32_t calibration_crc;
    uint8_t gain_level;
};

} // namespace mavlink::custom::msg
```
:::

3. **Функції серіалізації та декодування:**
   * `mavlink_msg_payload_spectral_status_pack(...)` — серіалізує окремі змінні безпосередньо у вихідний буфер повідомлення `mavlink_message_t`.
   * `mavlink_msg_payload_spectral_status_encode(...)` — запаковує готову структуру.
   * `mavlink_msg_payload_spectral_status_decode(...)` — копіює корисні дані з отриманого кадру в структуру, автоматично зануляючи відсутні байти розширення при отриманні короткого або обрізаного пакета.

---

### 11. Специфікація кодеків для Rust та Go

Сучасні бекенди наземних комплексів та бортові комп'ютери обробки відео використовують генератори для мов Rust та Go.

#### Модель даних у Rust (`mavlink-rust`)
Генератор Rust створює суворо типізований перелік повідомлень та структури з автоматичною підтримкою серіалізації через `bincode`:

```rust
#[derive(Clone, Debug, PartialEq)]
pub struct PayloadSpectralStatusData {
    pub time_boot_ms: u32,
    pub integration_time_ms: f32,
    pub sensor_temperature: f32,
    pub spectral_irradiance: u16,
    pub filter_mode: u8,
    pub status_flags: u8,
    pub calibration_crc: u32,
    pub gain_level: u8,
}

#[derive(Clone, Debug, PartialEq)]
pub enum MavMessage {
    Heartbeat(HeartbeatData),
    PayloadSpectralStatus(PayloadSpectralStatusData),
    // Решта повідомлень діалекту...
}
```

Обробка вхідного потоку в Rust виконується через безпечний патерн-матчинг, що унеможливлює некоректний доступ до пам'яті:

```rust
match message {
    MavMessage::PayloadSpectralStatus(data) => {
        println!("Отримано статус сенсора: темп = {:.1}°C", data.sensor_temperature);
    }
    _ => {}
}
```

#### Модель даних у Go (`gomavlib`)
Для мови Go бібліотека `gomavlib` генерує структури зі спеціальними тегами полів, що керують порядком сортування та серіалізацією:

```go
type MessagePayloadSpectralStatus struct {
    TimeBootMs         uint32  `mavlink:"0"`
    IntegrationTimeMs  float32 `mavlink:"4"`
    SensorTemperature  float32 `mavlink:"8"`
    SpectralIrradiance uint16  `mavlink:"12"`
    FilterMode         uint8   `mavlink:"14"`
    StatusFlags        uint8   `mavlink:"15"`
    CalibrationCrc     uint32  `mavlink:"16,extension"`
    GainLevel          uint8   `mavlink:"20,extension"`
}

func (m *MessagePayloadSpectralStatus) GetID() uint32 {
    return 42010
}
```

---

### 12. Специфікація XML Schema (XSD) для валідації діалектів

Офіційна граматика схеми MAVLink описується документом XML Schema Definition (XSD). Вона задає суворі обмеження на типи елементів, регулярні вирази назв полів та допустимі діапазони числових значень.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

  <!-- Кореневий елемент mavlink -->
  <xs:element name="mavlink">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="include" type="xs:string" minOccurs="0" maxOccurs="unbounded"/>
        <xs:element name="version" type="xs:unsignedByte" minOccurs="0" maxOccurs="1"/>
        <xs:element name="dialect" type="xs:unsignedInt" minOccurs="0" maxOccurs="1"/>
        <xs:element name="enums" type="enumsType" minOccurs="0" maxOccurs="1"/>
        <xs:element name="messages" type="messagesType" minOccurs="0" maxOccurs="1"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>

  <!-- Тип для валідації повідомлення -->
  <xs:complexType name="messageType">
    <xs:sequence>
      <xs:element name="description" type="xs:string" minOccurs="0"/>
      <xs:choice maxOccurs="unbounded">
        <xs:element name="field" type="fieldType"/>
        <xs:element name="extensions" type="emptyType"/>
      </xs:choice>
    </xs:sequence>
    <xs:attribute name="id" type="xs:unsignedInt" use="required"/>
    <xs:attribute name="name" type="namePattern" use="required"/>
  </xs:complexType>

  <!-- Обмеження для назви повідомлення: лише верхній регістр та підкреслення -->
  <xs:simpleType name="namePattern">
    <xs:restriction base="xs:string">
      <xs:pattern value="[A-Z0-9_]+"/>
    </xs:restriction>
  </xs:simpleType>

</xs:schema>
```

Валідація будь-якого діалекту за допомогою системної утиліти `xmllint` виконується однією командою перед запуском компілятора:

```bash
xmllint --noout --schema mavlink_schema.xsd my_custom_dialect.xml
```

---

### 13. Оптимізація ресурсів мікроконтролера в кодеках C

Під час компіляції згенерованих C-кодеків для систем із критично обмеженим обсягом пам'яті (Flash < 64 КБ, RAM < 16 КБ) розробник може керувати генерацією коду за допомогою макросів препроцесора:

* `MAVLINK_COMM_NUM_BUFFERS` — визначає кількість фізичних комунікаційних каналів. За замовчуванням дорівнює 4 (`MAVLINK_COMM_0 .. MAVLINK_COMM_3`). Зменшення цього числа до 1 або 2 звільняє системну пам'ять для статичних буферів розбору кадру `mavlink_status_t`.
* `MAVLINK_USE_CONVENIENCE_FUNCTIONS` — якщо визначено, вмикає автоматичну генерацію функцій прямої відправки `mavlink_msg_<name>_send()`, які потребують реалізації низькорівневої функції `comm_send_ch()`.
* `MAVLINK_NO_CONVERSION_HELPERS` — відключає допоміжні функції перетворення типів, що дозволяє зекономити до 8 КБ Flash-пам'яті програм.
* `MAVLINK_ALIGNED_FIELDS` — активує швидкий шлях прямого копіювання `memcpy` замість побайтового кодування зміщень на архітектурах зі швидким доступом до вирівняних даних.

---

### 14. Скрипт автоматизованої перевірки діалекту

Перед передачею XML-файлу до генератора `mavgen` у конвеєрах CI/CD виконується статична верифікація схеми. Нижче наведено базовий скрипт валідації на Python, що перевіряє унікальність ідентифікаторів повідомлень, діапазони Message ID та відсутність циклічних посилань:

```python
import xml.etree.ElementTree as ET
import os
import sys

def validate_dialect(xml_path, seen_ids=None, visited_files=None):
    if seen_ids is None:
        seen_ids = {}
    if visited_files is None:
        visited_files = set()

    real_path = os.path.abspath(xml_path)
    if real_path in visited_files:
        return seen_ids
    visited_files.add(real_path)

    tree = ET.parse(real_path)
    root = tree.getroot()

    if root.tag != 'mavlink':
        raise ValueError(f"Кореневий тег повинен бути <mavlink>, знайдено <{root.tag}>")

    base_dir = os.path.dirname(real_path)
    for inc in root.findall('include'):
        inc_path = os.path.join(base_dir, inc.text.strip())
        validate_dialect(inc_path, seen_ids, visited_files)

    messages = root.find('messages')
    if messages is not None:
        for msg in messages.findall('message'):
            msg_id = int(msg.attrib['id'])
            msg_name = msg.attrib['name']

            if msg_id in seen_ids:
                prev_name, prev_file = seen_ids[msg_id]
                raise ValueError(
                    f"Колізія Message ID {msg_id}: повідомлення '{msg_name}' у {os.path.basename(real_path)} "
                    f"конфліктує з '{prev_name}' у {os.path.basename(prev_file)}"
                )
            seen_ids[msg_id] = (msg_name, real_path)

    return seen_ids

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Використання: python validate_dialect.py <path_to_dialect.xml>")
        sys.exit(1)
    try:
        all_messages = validate_dialect(sys.argv[1])
        print(f"Успішно перевірено: знайдено {len(all_messages)} унікальних повідомлень.")
    except Exception as e:
        print(f"ПОМИЛКА ВАЛІДАЦІЇ: {e}", file=sys.stderr)
        sys.exit(1)
```

---

### 15. Еталонний приклад повної схеми діалекту

Нижче наведено повний зразок валідного файлу діалекту, що демонструє всі ключові можливості синтаксису: підключення базового стандарту, оголошення переліку станів, розширення списку команд `MAV_CMD` та визначення повідомлення з базовими й розширеними полями:

```xml
<?xml version="1.0"?>
<mavlink>
  <include>common.xml</include>
  <version>3</version>
  <dialect>42</dialect>

  <enums>
    <enum name="PAYLOAD_SPECTRAL_FILTER" bitmask="false">
      <description>Оптичні фільтри спектральної камери.</description>
      <entry value="0" name="SPECTRAL_FILTER_CLEAR">
        <description>Прозоре оптичне скло (повний діапазон 400..1000 нм).</description>
      </entry>
      <entry value="1" name="SPECTRAL_FILTER_RED_EDGE">
        <description>Вузькосмуговий фільтр 705 нм (хлорофіл).</description>
      </entry>
      <entry value="2" name="SPECTRAL_FILTER_NIR">
        <description>Ближній інфрачервоний діапазон 840 нм.</description>
      </entry>
    </enum>

    <enum name="MAV_CMD">
      <entry value="42050" name="MAV_CMD_DO_TRIGGER_SPECTRAL_CAPTURE">
        <description>Виконати синхронний знімок усіма спектральними матрицями.</description>
        <param index="1" label="Експозиція (мс)" units="ms" minValue="1" maxValue="1000" default="50">Час накопичення.</param>
        <param index="2" label="Номер фільтра" enum="PAYLOAD_SPECTRAL_FILTER" default="0">Позиція револьвера фільтрів.</param>
        <param index="3" label="Кількість кадрів" minValue="1" maxValue="20" default="1">Серійна зйомка.</param>
        <param index="4" label="Зарезервовано">Порожній слот.</param>
        <param index="5">Зарезервовано.</param>
        <param index="6">Зарезервовано.</param>
        <param index="7">Зарезервовано.</param>
      </entry>
    </enum>
  </enums>

  <messages>
    <message id="42001" name="PAYLOAD_SPECTRAL_TELEMETRY">
      <description>Періодична телеметрія стану спектральної камери.</description>
      <field type="uint32_t" name="time_boot_ms" units="ms">Час від старту живлення.</field>
      <field type="float"    name="focal_temperature" units="degC">Температура оптичного блоку.</field>
      <field type="uint16_t" name="raw_intensity[4]">Відліки чотирьох фотодіодів освітленості.</field>
      <field type="uint8_t"  name="active_filter" enum="PAYLOAD_SPECTRAL_FILTER">Поточний фільтр.</field>
      <extensions/>
      <field type="uint32_t" name="frame_counter" default="0">Загальний лічильник збережених знімків.</field>
      <field type="uint8_t"  name="sd_storage_pct" units="%" invalid="UINT8_MAX">Відсоток заповнення карти пам'яті.</field>
    </message>
  </messages>
</mavlink>
```

---

### 16. Правила сумісності та розширення переліків між версіями

Щоб підтримувати безперервну інтеграцію між різними релізами діалекту та уникнути збоїв у роботі старіших наземних станцій, розробники схем зобов'язані дотримуватися правил еволюції переліків:

1. **Заборона повторного використання числових значень:** Якщо константу видалено або оголошено застарілою через `<deprecated>`, її числовий код `value` назавжди резервується і ніколи не призначається новим режимам.
2. **Обов'язкове нульове значення безпечного стану:** Значення `value="0"` завжди резервується під невизначений або безпечний стан за замовчуванням (наприклад, `STATE_UNKNOWN` або `STATE_OFF`). Це гарантує, що при отриманні зануленого буфера розширення або невизначеної пам'яті система не активує небезпечний виконавчий механізм (лазер чи мотор).
3. **Обробка невідомих кодів у коді приймача:** У конструкціях `switch (state)` завжди реалізується гілка `default:`, яка безпечно реєструє невідомий режим від новішої прошивки замість аварійної зупинки програми.

---

### 17. Правила валідації та діагностика помилок компіляції

Під час аналізу XML-файлів компілятор `mavgen` здійснює перевірку цілісності схеми. Нижче наведено перелік типових помилок та способи їх усунення:

1. **Колізія Message ID (`Duplicate message ID`):**
   * *Причина:* Двом повідомленням у діалекті або включеному `common.xml` призначено однаковий числовий номер `id`.
   * *Виправлення:* Змініть ідентифікатор кастомного повідомлення на вільний номер із діапазону `42000 .. 42999`.
2. **Колізія імені константи (`Duplicate enum entry`):**
   * *Причина:* Два різних переліки містять елемент `<entry>` з однаковим атрибутом `name`.
   * *Виправлення:* Додайте специфічний вендорний префікс до імені константи (наприклад, `MYPAYLOAD_STATE_OFF` замість загального `STATE_OFF`).
3. **Недійсний тип поля (`Unknown field type`):**
   * *Причина:* Використано непідтримуваний тип даних (наприклад, `string`, `bool`, `int`, `uint24_t`).
   * *Виправлення:* Замініть `string` на `char[N]`, `bool` на `uint8_t`, а нестандартні типи — на канонічні типи MAVLink фіксованої довжини.
4. **Помилка циклічного включення (`Circular include detected`):**
   * *Причина:* Файл `A.xml` включає `B.xml`, а `B.xml` містить `<include>A.xml</include>`.
   * *Виправлення:* Побудуйте дерево включень як спрямований ациклічний граф (DAG) із вершиною у `minimal.xml`.
5. **Некоректний індекс параметра команди (`Invalid command param index`):**
   * *Причина:* У тегу `<param>` вказано індекс поза межами діапазону 1..7 або один і той самий індекс повторюється двічі.
   * *Виправлення:* Перевірте нумерацію слотів від 1 до 7 без пропусків та дублів.
