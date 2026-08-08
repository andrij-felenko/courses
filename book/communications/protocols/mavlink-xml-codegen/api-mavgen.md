# 📋 mavgen: контракт інструменту й форма згенерованого коду

Це довідник до `mavgen` — програми, яка перетворює XML-опис MAVLink на працездатний кодек обраною мовою. Тут зібрано те, що доводиться шукати щоразу наново: повний перелік ключів командного рядка з чинними усталеними значеннями, таблиця мов, дерево файлів на виході й точні сигнатури згенерованих функцій — щоб знайти потрібний символ, не гортаючи заголовок на кілька тисяч рядків.

Усе звірено з деревом `ArduPilot/pymavlink` та `mavlink/c_library_v2` станом на серпень 2026 року. Там, де опублікована документація розходиться з кодом, розходження позначено окремо — і вірити треба коду.

## Виклик

`mavgen` живе в пакеті `pymavlink` і власного виконуваного файлу не має. Надійний спосіб запуску — модулем, бо він не залежить від того, що потрапило в `PATH`:

```sh
python -m pymavlink.tools.mavgen \
    --lang=C --wire-protocol=2.0 \
    --output=build/generated/mavlink \
    modules/mavlink/message_definitions/v1.0/common.xml
```

Увесь контракт командного рядка вміщається в чотири ключі й позиційні файли опису:

```
mavgen.py [-h] [-o OUTPUT] [--lang LANG] [--wire-protocol {0.9,1.0,2.0}]
          [--no-validate] [--strict-units] XML [XML ...]
```

| ключ | що робить | усталено |
|---|---|---|
| `-o`, `--output` | куди складати результат | `mavlink` |
| `--lang` | мова кодека; значення — з переліку нижче | `Python` |
| `--wire-protocol` | версія протоколу: `0.9`, `1.0` або `2.0` | `1.0` |
| `--no-validate` | вимкнути перевірку XML за схемою | перевірка ввімкнена |
| `--strict-units` | ще й перевіряти атрибути `units` полів | вимкнено |
| `XML …` | один або кілька файлів опису (позиційні) | обов'язкові |

Чотири речі в цій таблиці регулярно кусають.

**Усталена версія протоколу — `1.0`, а не `2.0`.** Забути `--wire-protocol=2.0` — найдешевший спосіб отримати кодек, який мовчки не бачить половини сучасного трафіку: без цього ключа генератор випускає бібліотеку MAVLink 1, без розширень і без підпису.

**`--output` означає різне для різних мов.** Для C це **тека**, куди ляже дерево заголовків. Для Python це **ім'я файлу**: генератор допише `.py`, якщо його немає, і запише один модуль. Тобто `--output=out/dialect` для C дасть теку `out/dialect/`, а для Python — файл `out/dialect.py`.

**Перевірка XML потребує `lxml`.** Якщо бібліотека не встановлена, `mavgen` не падає: він друкує попередження про те, що `lxml`/`libxml2`/`libxslt` не знайдено, і **тихо працює далі без перевірки**. Наслідок практичний: збірка на машині без `lxml` пропустить помилку в описі, яку та сама збірка на іншій машині зловить. Якщо перевірка вам потрібна — вимагайте `lxml` явно, а не сподівайтеся на нього.

**`--strict-units` вимкнено не випадково.** Історичний корпус описів має чимало полів з відсутніми або неканонічними одиницями, тому суворий режим на `common.xml` дасть купу зауважень. Вмикати його варто на **власному діалекті**, де ви самі відповідаєте за дисципліну.

Кілька XML-файлів можна дати відразу — кожен обробляється окремо й отримує свою теку на виході.

Код повернення інструмента — `1`, якщо генерація не вдалася. Це не дрібниця: саме він робить `mavgen` придатним для кроку збірки, де мовчазний нуль після провалу означав би збірку зі старими заголовками.

Той самий контракт доступний і з Python — це зручно, коли генерацію вбудовують у власний скрипт і не хочуть будувати рядок команди:

```python
from pymavlink.generator import mavgen

opts = mavgen.Opts(output="build/generated/mavlink",
                   wire_protocol="2.0", language="C",
                   validate=True, strict_units=False)
ok = mavgen.mavgen(opts, ["message_definitions/v1.0/common.xml"])
```

Тут `language` можна писати в будь-якому регістрі: усередині `mavgen()` назву однаково зводять до нижнього.

> ⚠️ Ключа `--error-limit`, який досі стоїть у прикладі виводу `--help` на сайті документації, **у чинному інструменті немає**. Він існував із довідкою «maximum number of validation errors to display», нічого не робив і був вилучений комітом «delete unused arg error_limit of mavgen.py» у липні 2025 року. Статус: перевірено за історією змін файлу `tools/mavgen.py` у сховищі `ArduPilot/pymavlink`. Опублікований приклад виводу застарів іще й тим, що містить `Python2`, якого в переліку мов уже немає.

## Мови

Значення `--lang` звіряється зі списком **буква в букву**: `C`, а не `c`, `C++11`, а не `Cpp11`. Регістр усередині `mavgen()` таки зводиться до нижнього, але вже після перевірки командного рядка, тож на CLI це не рятує — помилка в регістрі дасть відмову ще до початку роботи. Сам перелік:

| `--lang` | модуль-генератор | що виходить | версії протоколу |
|---|---|---|---|
| `C` | `mavgen_c` | дерево заголовків, лише `static inline` | 1 і 2 |
| `C++11` | `mavgen_cpp11` | заголовки з шаблонами | 1 і 2 |
| `Python`, `Python3` | `mavgen_python` | один модуль `.py` | 1 і 2 |
| `TypeScript` | `mavgen_typescript` | модулі TypeScript | 1 і 2 |
| `Java` | `mavgen_java` | класи Java | 1 і 2 |
| `WLua` | `mavgen_wlua` | розбирач для Wireshark | 1 і 2 |
| `CS` | `mavgen_cs` | класи C# | лише 1 |
| `JavaScript`, `JavaScript_Stable` | `mavgen_javascript_stable` | модуль для Node | лише 1 |
| `ObjC` | `mavgen_objc` | класи Objective-C | лише 1 |
| `Swift` | `mavgen_swift` | класи Swift | лише 1 |
| `JavaScript_NextGen` | `mavgen_javascript` | новіший варіант для Node | поза офіційним переліком |
| `Lua` | `mavgen_lua` | модуль Lua | поза офіційним переліком |
| `Ada` | `mavgen_ada` | пакети Ada (окрема гілка для 2.0) | поза офіційним переліком |
| `Spin2` | `mavgen_spin2` | код для Propeller 2 | поза офіційним переліком |

Останні чотири рядки потребують пояснення. Ці генератори **є в коді** й приймаються ключем `--lang`, але офіційне твердження документації про підтримувані версії їх не згадує: воно перелічує C, C++11, Python, TypeScript, Java й WLua як такі, що дають і MAVLink 1, і MAVLink 2, а C#, JavaScript, ObjC і Swift — як такі, що дають лише MAVLink 1. Статус: перелік значень звірено з константою `supportedLanguages` у `generator/mavgen.py`, твердження про версії — з опублікованою настановою; підтримка «позаофіційних» генераторів тримається на зусиллі окремих людей, і перевіряти її треба на своєму описі.

`Python` і `Python3` ведуть в один і той самий генератор — це не дві різні мови, а історичний слід.

## Що з'являється на диску після `--lang=C`

Тека виходу формується правилом `<--output>/<ім'я XML-файлу без розширення>`. Один виклик обробляє не лише названий файл, а й **усе, що він підключає** тегом `<include>`, — тому тек буде стільки, скільки описів у ланцюгу. «Нерухомі» заголовки, однакові для всіх діалектів, лягають у корінь `--output` і **копіюються, а не генеруються**.

```text
build/generated/mavlink/
├── checksum.h              ─┐
├── mavlink_conversions.h    │  скопійовані як є,
├── mavlink_get_info.h       │  однакові для будь-якого діалекту
├── mavlink_helpers.h        │
├── mavlink_sha256.h         │
├── mavlink_types.h          │
├── protocol.h              ─┘
├── minimal/
│   ├── mavlink.h            ← єдиний файл, який підключає прикладний код
│   ├── minimal.h            ← таблиці діалекту + переліки
│   ├── version.h
│   ├── testsuite.h
│   └── mavlink_msg_heartbeat.h
├── standard/
│   └── …
└── common/
    ├── mavlink.h
    ├── common.h
    ├── version.h
    ├── testsuite.h
    ├── mavlink_msg_attitude.h
    ├── mavlink_msg_sys_status.h
    └── …                    ← по одному заголовку на повідомлення
```

Набір скопійованих заголовків залежить від версії протоколу:

| `--wire-protocol` | що копіюється в корінь |
|---|---|
| `0.9` | `protocol.h`, `mavlink_helpers.h`, `mavlink_types.h`, `checksum.h` |
| `1.0` | те саме + `mavlink_conversions.h` |
| `2.0` | те саме + `mavlink_get_info.h`, `mavlink_sha256.h` |

**Підключати треба рівно один файл — `mavlink.h` свого діалекту.** Заголовки окремих повідомлень і заголовок діалекту напряму включати не можна: `common.h` починається з `#error Wrong include order`, якщо макрос `MAVLINK_H` ще не визначено. Причина не в педантизмі: `mavlink.h` перед усім іншим виставляє `MAVLINK_STX`, `MAVLINK_ENDIAN`, `MAVLINK_ALIGNED_FIELDS`, `MAVLINK_CRC_EXTRA` і хеш первинного опису, а решта заголовків уже покладаються на ці значення.

Уся згенерована C-бібліотека складається **тільки із заголовків**, і всі функції в ній — `static inline`. Об'єктного файлу немає, лінкувати нема чого; ціна — код кодека дублюється в кожній одиниці трансляції, яку компілятор потім здебільшого викидає.

![З одного елемента опису народжується структура, набір макросів, десяток функцій, рядок у таблиці сум і клас у модулі Python](/book/communications/protocols/mavlink-xml-codegen/img/artifacts.svg)
*Праворуч — усе, що з'являється з одного `<message>`. Символи в трьох групах узгоджені між собою за побудовою: та сама довжина, той самий відбиток, той самий порядок полів.*

## Заголовок одного повідомлення

Файл `mavlink_msg_<name_lower>.h` містить рівно чотири речі: макроси-константи, структуру, функції запису й функції читання. Далі всюди за приклад узято `ATTITUDE`.

### Макроси

| макрос | значення для `ATTITUDE` | зміст |
|---|---|---|
| `MAVLINK_MSG_ID_ATTITUDE` | `30` | визначник повідомлення |
| `MAVLINK_MSG_ID_ATTITUDE_LEN` | `28` | повна довжина корисних даних, з розширеннями |
| `MAVLINK_MSG_ID_ATTITUDE_MIN_LEN` | `28` | довжина базової частини, без розширень |
| `MAVLINK_MSG_ID_ATTITUDE_CRC` | `39` | `CRC_EXTRA` — відбиток набору полів |
| `MAVLINK_MSG_ID_30_LEN`, `MAVLINK_MSG_ID_30_MIN_LEN`, `MAVLINK_MSG_ID_30_CRC` | ті самі | псевдоніми за числом замість імені |
| `MAVLINK_MSG_ATTITUDE_FIELD_<ПОЛЕ>_LEN` | — | довжина поля-масиву; з'являється лише для масивів |
| `MAVLINK_MESSAGE_INFO_ATTITUDE` | — | опис полів для самоаналізу: ім'я, тип, зміщення, `offsetof` |

Пара `_LEN` і `_MIN_LEN` — це і є механізм розширень у числах. У `ATTITUDE` розширень немає, тож вони рівні; у `SYS_STATUS` (визначник 1) базова частина — 31 байт, а повна — 43.

### Структура

```c
typedef struct __mavlink_attitude_t {
 uint32_t time_boot_ms; /*< [ms]    Timestamp …*/
 float roll;            /*< [rad]   Roll angle …*/
 float pitch;
 float yaw;
 float rollspeed;
 float pitchspeed;
 float yawspeed;
} mavlink_attitude_t;
```

Поля йдуть у **дротовому** порядку — тому, що вийшов після сортування за розміром, а не тому, у якому вони записані в XML. Завдяки сортуванню зміщення кожного поля тут природно кратне його розміру, тож звичайна C-структура лягає байт у байт на корисні дані без жодного заповнювача.

Коли природного збігу немає — а це буває через поля-розширення, які не сортуються, — генератор бере структуру в макрос `MAVPACKED(…)`, який просить компілятор пакувати щільно. Умова точна: щойно хоч у одного поля зміщення на дроті не ділиться націло на розмір його елемента, повідомлення позначається як таке, що потребує пакування. Саме на збігу зміщень тримається швидка гілка розпакування: там, де порядок байтів і вирівнювання платформи збігаються з дротовими, `_decode` робить просте `memcpy`. Чому щільне пакування взагалі потребує окремої вказівки компіляторові — [пакування бінарного протоколу](book:programming/wire-format-packing); про сам порядок байтів у корисних даних — [порядок байтів](book:programming/endianness).

### Функції запису

Усі вони заповнюють `mavlink_message_t` і **повертають повну довжину кадру в байтах** — заголовок, корисні дані, сума й підпис разом, а не довжину корисних даних. Плутанина тут коштує зайвого або обрізаного відправлення.

Основна форма, від якої походять решта:

```c
uint16_t mavlink_msg_attitude_pack(
        uint8_t system_id, uint8_t component_id, mavlink_message_t* msg,
        uint32_t time_boot_ms, float roll, float pitch, float yaw,
        float rollspeed, float pitchspeed, float yawspeed);
```

Усі шість варіантів різняться лише **початком** списку аргументів — самі поля йдуть у тому самому вигляді й порядку, а в `_encode*` замість них стоїть готова структура:

| функція | що стоїть перед полями | навіщо саме вона |
|---|---|---|
| `…_pack` | `sysid, compid, msg` | звичайний випадок, канал `MAVLINK_COMM_0` |
| `…_pack_chan` | `sysid, compid, chan, msg` | свій лічильник послідовності на кожну лінію |
| `…_pack_status` | `sysid, compid, _status, msg` | власний стан замість глобального — коли статичних змінних не можна |
| `…_encode` | `sysid, compid, msg` + `const mavlink_attitude_t*` замість полів | дані вже лежать у структурі |
| `…_encode_chan` | `sysid, compid, chan, msg` + структура | те саме з явним каналом |
| `…_encode_status` | `sysid, compid, _status, msg` + структура | те саме з власним станом |

`_encode*` — це буквально обгортки навколо відповідних `_pack*`, які розкладають структуру в аргументи. Різниця між трьома парами не в даних, а в тому, **звідки береться лічильник послідовності**: усталений канал, названий канал чи переданий стан.

Ще трійця з'являється лише тоді, коли ви визначили `MAVLINK_USE_CONVENIENCE_FUNCTIONS` і надали бібліотеці спосіб виштовхнути байти в лінію:

```c
void mavlink_msg_attitude_send(mavlink_channel_t chan,
        uint32_t time_boot_ms, float roll, float pitch, float yaw,
        float rollspeed, float pitchspeed, float yawspeed);

void mavlink_msg_attitude_send_struct(mavlink_channel_t chan,
        const mavlink_attitude_t* attitude);

void mavlink_msg_attitude_send_buf(mavlink_message_t* msgbuf, mavlink_channel_t chan,
        uint32_t time_boot_ms, float roll, float pitch, float yaw,
        float rollspeed, float pitchspeed, float yawspeed);
```

Третя тут — не примха. `_send` кладе кадр на стек; `_send_buf` бере під це чужий буфер (звичайно — приймальний буфер того самого каналу) і тим економить сотні байтів стека, чого на мікроконтролері часом досить, щоб задача взагалі жила. Її генерують лише для повідомлень, які влазять у `MAVLINK_MAX_PAYLOAD_LEN` (255 байтів).

### Функції читання

```c
/* По одному читачеві на кожне поле: дістає значення просто з корисних даних. */
uint32_t mavlink_msg_attitude_get_time_boot_ms(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_roll(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_pitch(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_yaw(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_rollspeed(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_pitchspeed(const mavlink_message_t* msg);
float    mavlink_msg_attitude_get_yawspeed(const mavlink_message_t* msg);

/* Розкласти все повідомлення в структуру. */
void mavlink_msg_attitude_decode(const mavlink_message_t* msg, mavlink_attitude_t* attitude);
```

Для поля-масиву читач має інший вигляд: він приймає буфер і повертає кількість скопійованих елементів — скажімо, `uint16_t mavlink_msg_<name>_get_<field>(const mavlink_message_t* msg, float* <field>)`.

У `_decode` захована вся домовленість про короткі кадри: він спершу **обнуляє всю структуру**, а тоді копіює `min(msg->len, _LEN)` байтів. Тому кадр від старого відправника, у якому немає полів-розширень, дає нулі в цих полях — і це не помилка, а визначена поведінка. Прикладний код зобов'язаний тлумачити нуль у полі-розширенні як «даних немає».

Окремі читачі не безкоштовні: кожен наново відлічує зміщення від початку корисних даних. Читати поодинці варто, коли з великого повідомлення потрібне одне поле; брати все — через `_decode`.

## Спільні таблиці діалекту

Найважливіше в заголовку діалекту — таблиця, що дозволяє розбирачеві перевірити суму, ще не знаючи, що всередині кадру.

```c
typedef struct __mavlink_msg_entry {
    uint32_t msgid;
    uint8_t  crc_extra;
    uint8_t  min_msg_len;          /* довжина базової частини */
    uint8_t  max_msg_len;          /* повна довжина з розширеннями */
    uint8_t  flags;                /* MAV_MSG_ENTRY_FLAG_* */
    uint8_t  target_system_ofs;    /* зміщення поля-адресата; чи воно є — каже flags */
    uint8_t  target_component_ofs;
} mavlink_msg_entry_t;

/* У common.h: суцільний список, упорядкований за визначником. */
#define MAVLINK_MESSAGE_CRCS {{0, 50, 9, 9, 0, 0, 0}, \
                              {1, 124, 31, 43, 0, 0, 0}, \
                              {2, 137, 12, 12, 0, 0, 0}, \
                              /* … */ {30, 39, 28, 28, 0, 0, 0}, /* … */}
```

Прапорці `flags` кажуть, чи має повідомлення адресата: `MAV_MSG_ENTRY_FLAG_HAVE_TARGET_SYSTEM` = 1, `MAV_MSG_ENTRY_FLAG_HAVE_TARGET_COMPONENT` = 2. Разом зі зміщеннями це дає ретрансляторові змогу вирішити, куди слати кадр, **не розпаковуючи його** — прочитати один байт за відомим зміщенням.

Доступ до таблиці — через `mavlink_get_msg_entry(uint32_t msgid)` з `mavlink_helpers.h`. Список упорядкований за визначником, і функція шукає в ньому [двійковим пошуком](book:algorithms/binary-search): це важливо, бо виклик трапляється на **кожен прийнятий кадр**, а записів у діалекті — сотні.

Решта спільних макросів:

| макрос | де оголошений | зміст |
|---|---|---|
| `MAVLINK_MESSAGE_LENGTHS` | `<діалект>.h` | довжини корисних даних; спадок MAVLink 1 |
| `MAVLINK_MESSAGE_INFO`, `MAVLINK_MESSAGE_NAMES` | `<діалект>.h` | опис полів і імена для самоаналізу; збираються лише для **первинного** опису й потребують `mavlink_get_info.h` |
| `MAVLINK_BUILD_DATE` | `version.h` | дата генерації рядком |
| `MAVLINK_WIRE_PROTOCOL_VERSION` | `version.h` | `"2.0"` або `"1.0"` — те, що просили ключем |
| `MAVLINK_MAX_DIALECT_PAYLOAD_SIZE` | `version.h` | найдовші корисні дані в цьому діалекті |
| `MAVLINK_PRIMARY_XML_HASH` | `mavlink.h` | хеш імені первинного опису |

Сам кадр у пам'яті виглядає так — це не структура з дроту, а робоче подання, у якому корисні дані вирівняні на вісім байтів:

```c
typedef struct __mavlink_message {
    uint16_t checksum;
    uint8_t  magic;              /* 0xFD для MAVLink 2, 0xFE для MAVLink 1 */
    uint8_t  len;                /* довжина корисних даних, можливо обрізаних */
    uint8_t  incompat_flags;
    uint8_t  compat_flags;
    uint8_t  seq;
    uint8_t  sysid;
    uint8_t  compid;
    uint32_t msgid:24;           /* 24 біти, як на дроті */
    uint64_t payload64[(MAVLINK_MAX_PAYLOAD_LEN + MAVLINK_NUM_CHECKSUM_BYTES + 7) / 8];
    uint8_t  ck[2];
    uint8_t  signature[MAVLINK_SIGNATURE_BLOCK_LEN];  /* 13 байтів */
} mavlink_message_t;
```

Тип поля `payload64` обраний саме як `uint64_t` заради вирівнювання — щоб доступ до `double` усередині корисних даних не був невирівняним. Дістатися до байтів можна макросом `_MAV_PAYLOAD(msg)`. Що означають поля заголовка й звідки взялися 13 байтів підпису — [пакет MAVLink](book:communications/mavlink-packet) і [криптографічний підпис MAVLink 2](book:communications/mavlink-v2-signing).

## Відповідність типів

Одна й та сама таблиця типів працює в обидва боки: з неї генератор бере і тип поля в C, і символ формату для пакувальника Python.

| тип у XML | тип у C | символ у `struct` (Python) |
|---|---|---|
| `float` | `float` | `f` |
| `double` | `double` | `d` |
| `char` | `char` | `c` (масив — `<N>s`) |
| `int8_t` / `uint8_t` | `int8_t` / `uint8_t` | `b` / `B` |
| `int16_t` / `uint16_t` | `int16_t` / `uint16_t` | `h` / `H` |
| `int32_t` / `uint32_t` | `int32_t` / `uint32_t` | `i` / `I` |
| `int64_t` / `uint64_t` | `int64_t` / `uint64_t` | `q` / `Q` |
| `uint8_t_mavlink_version` | `uint8_t` | `B` |

Масив `type[N]` у C стає `type name[N]`, у Python — префіксом кількості перед символом: `float[4]` → `4f`. Рядок формату завжди починається з `<` — молодшим байтом уперед.

## Еквівалент у pymavlink

Виклик з `--lang=Python` дає **один модуль**, у якому лежить усе: константи, переліки, класи повідомлень і клас `MAVLink` — сам кодек, що збирає й розбирає кадри.

```python
MAVLINK_MSG_ID_ATTITUDE = 30

class MAVLink_attitude_message(MAVLink_message):
    id = MAVLINK_MSG_ID_ATTITUDE
    msgname = "ATTITUDE"
    fieldnames = ["time_boot_ms", "roll", "pitch", "yaw",
                  "rollspeed", "pitchspeed", "yawspeed"]
    ordered_fieldnames = ["time_boot_ms", "roll", "pitch", "yaw",
                          "rollspeed", "pitchspeed", "yawspeed"]
    fieldtypes = ["uint32_t", "float", "float", "float", "float", "float", "float"]
    fieldunits_by_name = {"time_boot_ms": "ms", "roll": "rad", "pitch": "rad",
                          "yaw": "rad", "rollspeed": "rad/s",
                          "pitchspeed": "rad/s", "yawspeed": "rad/s"}
    orders = [0, 1, 2, 3, 4, 5, 6]
    lengths = [1, 1, 1, 1, 1, 1, 1]
    array_lengths = [0, 0, 0, 0, 0, 0, 0]
    crc_extra = 39
    unpacker = struct.Struct("<Iffffff")
    instance_field = None
    instance_offset = -1

# наприкінці модуля — відповідність визначника класові (запис на кожне повідомлення)
mavlink_map = {
    MAVLINK_MSG_ID_HEARTBEAT: MAVLink_heartbeat_message,
    MAVLINK_MSG_ID_SYS_STATUS: MAVLink_sys_status_message,
    MAVLINK_MSG_ID_ATTITUDE: MAVLink_attitude_message,
}
```

Ключова пара — `fieldnames` і `ordered_fieldnames`. Перший список іде в **порядку XML** (у ньому конструктор приймає аргументи, у ньому ж їх бачить прикладний код), другий — у **дротовому**. Масив `orders` каже, як переставити одне в друге; `lengths` і `array_lengths` описують поля-масиви. Коли `mavlink_map` знаходить клас за визначником, розбирач розпаковує байти через `unpacker`, а тоді переставляє значення за `orders` — і лише після цього створює об'єкт.

`instance_field` разом з `instance_offset` — молодша механіка: вони називають поле, що розрізняє **екземпляри** одного типу повідомлення (скажімо, номер батареї), щоб потік не зливався в одну змінну.

Атрибут повідомлення тепер зветься `msgname`; старе ім'я `name` лишили як застарілий псевдонім заради сумісності. У коді, який ще працює зі старими генераціями, трапиться саме `name`.

Методи відправлення живуть у класі `MAVLink` — по два на кожне повідомлення:

```python
def attitude_encode(self, time_boot_ms, roll, pitch, yaw,
                    rollspeed, pitchspeed, yawspeed):
    return MAVLink_attitude_message(time_boot_ms, roll, pitch, yaw,
                                    rollspeed, pitchspeed, yawspeed)

def attitude_send(self, time_boot_ms, roll, pitch, yaw,
                  rollspeed, pitchspeed, yawspeed, force_mavlink1=False):
    self.send(self.attitude_encode(time_boot_ms, roll, pitch, yaw,
                                   rollspeed, pitchspeed, yawspeed),
              force_mavlink1=force_mavlink1)
```

Тобто `<name>_encode` збирає об'єкт, `<name>_send` збирає й одразу відправляє. Відповідність до C прямолінійна: `attitude_encode` ↔ `mavlink_msg_attitude_pack`, `attitude_send` ↔ `mavlink_msg_attitude_send`.

Мінімальний робочий приклад — прийняти й відправити:

```python
from pymavlink import mavutil

master = mavutil.mavlink_connection("udpin:0.0.0.0:14550")
master.wait_heartbeat()

msg = master.recv_match(type="ATTITUDE", blocking=True)
print(msg.roll, msg.pitch, msg.yaw)     # поля — звичайні атрибути об'єкта

master.mav.attitude_send(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
```

## Генерація як крок збірки

Згенерований код — похідний продукт, і місце йому в теці збірки, а не в сховищі поруч із рукописним. Виклик оформлюють [власною командою збірки](book:build-systems/custom-commands) з явними залежностями від XML, щоб генерація повторювалася сама, коли опис змінився:

```cmake
find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(MAVLINK_XML ${CMAKE_SOURCE_DIR}/modules/mavlink/message_definitions/v1.0/common.xml)
set(MAVLINK_OUT ${CMAKE_BINARY_DIR}/generated/mavlink)

add_custom_command(
    OUTPUT  ${MAVLINK_OUT}/common/mavlink.h
    COMMAND ${Python3_EXECUTABLE} -m pymavlink.tools.mavgen
            --lang=C --wire-protocol=2.0
            --output=${MAVLINK_OUT} ${MAVLINK_XML}
    DEPENDS ${MAVLINK_XML}
    COMMENT "mavgen: C-кодек із common.xml")

add_custom_target(mavlink_headers DEPENDS ${MAVLINK_OUT}/common/mavlink.h)

add_library(mavlink INTERFACE)
add_dependencies(mavlink mavlink_headers)
target_include_directories(mavlink INTERFACE ${MAVLINK_OUT})
```

Ціль — інтерфейсна, бо компілювати нічого: бібліотека складається з самих заголовків (додавати залежності до `INTERFACE`-бібліотеки CMake дозволяє з версії 3.3). Файл-свідок у `OUTPUT` — це `common/mavlink.h`; перелічувати всі згенеровані заголовки не потрібно й шкідливо, бо їхній список залежить від опису.

Одна пастка тут лишається на вас. У `DEPENDS` стоїть лише названий XML, а `common.xml` тягне за собою `standard.xml` і `minimal.xml` тегом `<include>` — правка в них перегенерації **не запустить**. Або перелічуйте весь ланцюг у `DEPENDS`, або, якщо описи приходять окремим сховищем, [прив'яжіть його до конкретної ревізії](book:build-systems/version-pinning) й покладайтеся на зміну ревізії як на сигнал.
