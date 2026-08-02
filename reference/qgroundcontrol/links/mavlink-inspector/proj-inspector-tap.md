# ⚙️ `mavtap`: спостерігач за потоком MAVLink, зібраний з нуля

Це чотириста рядків, які підключаються до потоку MAVLink і тримають живу таблицю: що прилітає, від кого, як часто і що всередині. Жодного рядка, присвяченого конкретному повідомленню, у них немає — програма нічого не знає ні про батареї, ні про положення, ні про регулятори обертів, і саме тому працює на будь-якому діалекті, зокрема на вашому власному.

## Задача

Програма командного рядка з одним джерелом байтів і трьома роботами:

```
mavtap --udp 14550 --select BATTERY_STATUS[0]
mavtap --tlog flight.tlog --log ATTITUDE.roll
```

1. **Таблиця рядків.** Кожне окреме джерело значень — свій рядок: назва повідомлення, компонент, лічильник кадрів, оцінка частоти.
2. **Поля вибраного рядка** — розкладені з навантаження за описом повідомлення, з розгорнутими масивами.
3. **Запис одного поля в CSV** — щоб потім побудувати криву чим завгодно.
4. **Файл телеметрії читається так само, як живий канал** — та сама таблиця, ті самі числа, незалежно від того, за скільки прочитався файл.

Чого програма не робить: не тлумачить змісту. Вона не знає, що `BATTERY_STATUS.voltages` — це напруги в мілівольтах, і не переводить їх у вольти. Усе, що вона вміє, — правильно дістати з байтів число потрібного типу. Ця відмова від тлумачення і є сенсом такого інструмента: показане ним не може виявитися помилкою обробника, бо обробника немає.

## Шов: розібраний кадр і більше нічого

Уся програма висить на одному виклику:

```cpp
void onMessage(const mavlink_message_t& m, uint64_t tUsec);
```

Байти в кадри складає [інкрементний розбирач](book:programming/stream-parser) бібліотеки — автомат, який їсть потік по байту, тримає стан на канал і повертає одиницю рівно тоді, коли зібрав цілий кадр і звірив контрольну суму. Усе, що не зійшлося, до `onMessage` не доходить узагалі: погана сума, невідомий номер повідомлення, чужа версія протоколу.

Джерел два, і обидва зводяться до годування того самого автомата:

```cpp
for (ssize_t i = 0; i < n; ++i)
    if (mavlink_parse_char(kChannel, buf[i], &msg, &st)) onMessage(msg, tUsec);
```

Файл телеметрії проходить крізь той самий автомат — не тому, що інакше не вийшло б (межі кадрів у ньому відомі точно), а тому, що це робить два режими справді однаковими. Розбирач дає не лише перевірку суми: він **дописує нулі в хвіст навантаження**. Це важить більше, ніж здається. Версія 2 протоколу зобов'язана обрізати нульові байти в кінці навантаження перед надсиланням, тож у кадрі фізично може не бути останніх полів. Розбирач, знайшовши в таблиці свого діалекту повну довжину цього повідомлення, заповнює нулями все, що не долетіло, — і подальший код може читати будь-яке поле, не питаючи, чи воно взагалі було в кадрі. Кадр, зібраний руками в обхід розбирача, такої гарантії не має, і читання «зайвого» поля дало б залишки попереднього повідомлення в тому самому буфері.

Сам формат файлу телеметрії простий — вісім байтів часу, за ними кадр як прийшов, — але має досить своїх особливостей, щоб їх розбирати окремо: порядок байтів мітки у файлі не записаний, довжини запису теж немає. Тут узято найпростіше прочитання; повний [читач логу з перемотуванням](book:qgroundcontrol/telemetry-logging/proj-tlog-reader.md) розібрано окремо.

Ще одна дрібниця, без якої не збереться взагалі нічого:

```cpp
#define MAVLINK_USE_MESSAGE_INFO   // ДО #include <common/mavlink.h>
```

Таблиці опису повідомлень — необов'язкова частина згенерованих заголовків. Без цього визначення функції `mavlink_get_message_info` просто не існує, а разом із нею немає й усієї програми.

## Ключ рядка: третя частина — дані, а не код

Один кадр — не одне джерело значень. Автопілот, підвіс і камера мають спільний ідентифікатор системи й різні ідентифікатори компонента; ба більше, один компонент шле те саме повідомлення про різні речі — окремо про кожну батарею, окремо про кожну четвірку регуляторів, а `NAMED_VALUE_FLOAT` узагалі є контейнером «ім'я — число», у якому за одним номером ходять десятки величин. Тому ключ рядка — трійка: номер повідомлення, компонент і значення розрізняльного поля.

Перші дві частини лежать [прямо в заголовку кадру](book:communications/mavlink-packet) — ідентифікатори системи, компонента, номер повідомлення і порядковий номер відправника. Третю треба звідкись узяти, і тут є розвилка. Можна зашити в код перелік «повідомлення 147 розрізняти за полем `id`» — і щоразу перезбирати програму, коли в діалекті з'явиться щось нове. А можна зробити цей перелік **даними**:

```cpp
static std::unordered_map<uint32_t, unsigned> g_instField;   // msgid → номер поля

static bool addInstanceRule(const char* msgName, const char* fieldName, bool quiet = false);
```

Правило задається парою імен — `--instance BATTERY_STATUS=id` — і розв'язується на старті: бібліотека знаходить опис повідомлення за назвою, програма шукає в ньому поле за назвою й запам'ятовує **номер поля**, щоб у гарячому шляху не порівнювати рядків. Усе інше — тип, зсув у навантаженні, довжина масиву — береться з того самого опису під час роботи.

Ця дрібна зміна дає несподівано багато. Розрізняльне поле буває не лише числом: у `NAMED_VALUE_FLOAT` це `char[10]` з іменем величини. Правило «прочитати поле, назване в таблиці, і перетворити на короткий текст» покриває обидва випадки одним кодом: число друкується за своїм типом, символьний масив береться як рядок до першого нуля. Окремих гілок для налагоджувальних повідомлень не потрібно взагалі.

Ключ, зібраний із трьох частин, лягає в [таблицю з хешуванням](book:algorithms/hash-table) — структуру, яка знаходить запис за ключем за сталий час, розсіюючи ключі по кошиках хеш-функцією. Один нюанс варто продумати наперед: третя частина ключа — текст, і найпростіше зробити її `std::string`. Тоді кожен кадр створює тимчасовий рядок лише заради пошуку. Короткі рядки більшість реалізацій тримає в самому об'єкті, без звертання до купи, — але покладатися на це в шляху, яким проходить кожен кадр, не варто. Тому ключ носить власний буфер:

```cpp
struct Inst {                    // значення розрізняльного поля як короткий текст
    char    s[24] = {};          // 20 цифр найбільшого uint64 і char[10] імені — обоє влазять
    uint8_t n     = 0;
};
```

Двадцять чотири байти на стеку, порівняння через `memcmp`, хеш через прохід по `n` байтах — і жодного виділення пам'яті на кадр.

## Поля постають з опису

Коли рядок з'являється вперше, програма будує його поля, нічого не знаючи про повідомлення. Усе потрібне лежить у таблиці, яку [генератор коду](book:communications/mavlink-xml-codegen) виписав із XML-опису діалекту в заголовок: для кожного поля — ім'я, тип, зсув у навантаженні й довжина масиву.

```cpp
typedef struct __mavlink_field_info {
    const char            *name;
    const char            *print_format;
    mavlink_message_type_t type;
    unsigned int           array_length;
    unsigned int           wire_offset;
    unsigned int           structure_offset;
} mavlink_field_info_t;
```

Це [рефлексія](book:programming/reflection-metaprogramming) — опис даних, що існує окремо від коду й доступний під час виконання, — лише зроблена не мовою, а генератором. Наслідок той, заради якого все й затівалося: додайте у свій діалект нове повідомлення, перезберіть — і воно з'явиться в таблиці з усіма полями, без жодної правки.

Одне перетворення робиться свідомо: числовий масив розгортається в окремі поля-елементи. Масив із десяти напруг, показаний одним рядком, не можна ні порівняти сам із собою, ні винести на криву; розгорнутий на `voltages[0]`…`voltages[9]`, він дає десять незалежних величин. Зсув елемента виводиться арифметикою — зсув масиву плюс номер, помножений на розмір типу. Символьні масиви цього не отримують: ім'я величини не є числом, і як число воно нікому не потрібне.

![Розгортання масиву в елементи й зсуви розширених полів у навантаженні BATTERY_STATUS](/reference/qgroundcontrol/links/mavlink-inspector/img/proj-payload-layout.svg)

*Зсув елемента рахується від зсуву масиву; розширені поля дописано в кінець, і їхні зсуви вирівняними не є.*

Два місця тут ловлять того, хто пише таке вперше.

**Порядок полів в описі — не порядок у навантаженні.** Таблиця перелічує поля так, як вони стоять в XML, а на дроті вони переставлені за спаданням розміру типу. У `NAMED_VALUE_FLOAT` це видно голим оком: опис іде `time_boot_ms`, `name`, `value`, а зсуви в них — 0, 8 і 4. Порядок в описі добрий для показу людині; про місце в байтах питати можна лише `wire_offset`.

**Зсув поля не вирівняний під свій тип.** Це не рідкісний крайній випадок, а норма: розширені поля версії 2 дописуються в кінець в оголошеному порядку, без пересортування, щоб додавання поля не ламало сумісности. У `BATTERY_STATUS` через це `voltages_ext` — масив `uint16_t` — стоїть за зсувом 41, а `fault_bitmask` типу `uint32_t` за зсувом 50. Початок навантаження кратний восьми, отже жодна з цих адрес не вирівняна. Приведення вказівника до `uint16_t*` тут або впаде на архітектурі, яка [вимагає вирівнювання](book:programming/memory-alignment), або порушить [правила псевдонімів](book:programming/strict-aliasing) — обіцянку компіляторові, що об'єкт читають лише через його справжній тип; порушену, вона дає не помилку, а тихо неправильний код після оптимізації. Обидві проблеми знімає одна звичка:

```cpp
template <typename T>
static T wireRead(const mavlink_message_t& m, unsigned off) {
    T v{};
    std::memcpy(&v, _MAV_PAYLOAD(&m) + off, sizeof(T));   // ЗАВЖДИ memcpy
    return v;
}
```

Тут немає ціни, за яку варто торгуватися: компілятор перетворює `memcpy` відомого розміру на одну машинну команду завантаження.

## Рахувати всіх, розкладати лише вибраного

Тепер найдорожче місце. Розкладання одного кадру на дванадцять полів — це дванадцять перетворень числа на текст і дванадцять порівнянь із попереднім значенням. Порахуймо, скільки цього набігає.

```
Умова: 40 рядків у таблиці, 200 кадрів за секунду,
       12 полів у середньому після розгортання масивів,
       такт друку — раз на секунду, вибраний рядок приходить 10 разів за секунду.

розкладати все на кожному кадрі       200 × 12 = 2400 розкладань/с
рядок вибрано, розклад на кадрі        10 × 12 =  120 розкладань/с
рядок вибрано, розклад на друці         1 × 12 =   12 розкладань/с
пишеться ОДНЕ поле, розклад на кадрі   10 ×  1 =   10 розкладань/с
```

Різниця між першим і третім рядком — двісті разів, і вся вона з'явилася з одного спостереження: **на екрані одночасно розгорнуто щонайбільше один рядок**. Решта 2388 розкладань за секунду робилися б заради того, щоб їх ніхто не побачив.

Звідси розділення, яке проходить крізь усю програму. Кожен кадр робить лише дешеві речі:

```cpp
Row& row = it->second;
++row.count;
row.last = m;                            // копія ОСТАННЬОГО кадру — 296 байтів
if (row.anyLogged) logSample(row, tUsec);
```

Порівняймо ціни чесно, бо тут легко злякатися не того.

```
дешевий шлях — на КОЖЕН кадр
  хеш трійки й пошук рядка         одне звертання по пам'ять
  ++лічильник, перевірка номера    одиниці тактів
  memcpy 296 байтів із кеша        близько десятка тактів

дорогий шлях — на КОЖНЕ поле
  memcpy ≤ 8 байтів                одиниці тактів
  число → текст                    десятки–сотні тактів
  порівняння з попереднім          десятки тактів
  сповіщення спостерігача          від десятків тактів (виклик функції)
                                   до десятків тисяч (перемальовка панелі)
```

Копія цілого кадру виглядає марнотратством — двісті дев'яносто шість байтів заради дев'ятибайтового серцебиття, — а насправді коштує менше, ніж перетворення **одного** числа на текст:

```
sizeof(mavlink_message_t) на 64-бітній машині:
  сума, прапорці, ідентифікатори       16 Б  (msgid:24 вирівняне до чотирьох)
  payload64[33]                       264 Б  ((255 + 2 + 7) / 8 = 33 слова по 8 Б)
  ck[2] + signature[13]                16 Б  (з кінцевим вирівнюванням структури)
                                    ───────
                                      296 Б

200 кадрів/с × 296 Б = 59 КБ/с записів у пам'ять
```

Шістдесят кілобайтів за секунду не помітить ніхто. Розмір копії відомий на етапі компіляції, тож вона розгортається в кілька векторних записів у пам'ять, що вже лежить у кеші. Спокуса копіювати лише `msg.len` фактичних байтів економить дев'яносто відсотків байтів — і додає розгалуження та копію змінної довжини, яка на таких розмірах повільніша за копію сталої. Оптимізувати тут нема чого.

А от чому копія взагалі потрібна — питання цікавіше за економію. **Прихід кадрів і показ таблиці ведуть різні годинники.** Кадри приходять, коли їх шле апарат; таблиця друкується, коли настав такт. Збережена копія — це буфер між двома незалежними ритмами: у момент друку в рядку завжди є з чого розкласти поля, навіть якщо останній кадр цього типу прийшов дев'ять секунд тому. Без копії панель рідкісного повідомлення стояла б порожньою до наступного приходу.

І звідси ж випливає, чому розділення саме подвійне, а не просте «розкладати лише вибране».

**Таблиця дивиться на найсвіжіше значення** — її досить розкласти на такті друку, з копії. Сто оновлень за секунду однаково ніхто не встигне прочитати: око бере від сили десяток.

**Крива не має права проґавити відлік.** Сплеск, що прожив один кадр між двома друками, при розкладанні на такті просто зникне. Тому поле, яке пишеться в CSV, розкладається на **приході** — але саме воно одне, а не всі дванадцять полів рядка.

Дві потреби — два моменти розкладання, і кожна платить рівно за те, що їй потрібно.

## Такт частоти веде час потоку

Частота рахується найгрубішим із можливих способів: скільки кадрів прийшло за такт. Різниця лічильників, поділена на тривалість такту, і є частотою в герцах. Показувати її напряму незручно — цілочислове рахування дає смикання на одиницю, — тому свіжий відлік змішується з попереднім значенням:

```cpp
const double instHz = double(row.count - row.lastCount) / elapsedSec;
row.rateHz = (1.0 - kAlphaNew) * row.rateHz + kAlphaNew * instHz;
```

Це [експоненційне згладжування](book:math/exponential-smoothing) — зважене середнє, у якому вага старих відліків спадає геометрично. Вага свіжого тут велика, чотири п'ятих: показник майже не бреше, але вже не тремтить.

Важливіше за коефіцієнт те, **чим міряється `elapsedSec`**. Спокуса підставити одиницю велика: такт же секундний. Але таймер ніколи не спрацьовує рівно, а на файлі поняття «секунда» взагалі інше. Тому такт веде **годинник самого потоку**:

- живий канал — [монотонний годинник](book:programming/monotonic-vs-wall-time) машини, той, що міряє проміжки й не переводиться разом із настінним часом;
- файл телеметрії — мітка часу запису.

```cpp
if (tUsec >= lastTickUsec + uint64_t(kTickSec * 1e6)) {
    tap.tick(double(tUsec - lastTickUsec) / 1e6);
    ...
}
```

Це той рядок, через який файл поводиться як живий потік. Прочитаний за секунду, годинний лог дасть **ті самі** частоти, що й програний у темпі польоту: обидва рахують кадри за власним часом логу. Підставити туди настінний годинник — і швидке читання показало б тисячі герців.

## Втрата чи подвоєння: один лічильник розрізняє

Ключ рядка не містить каналу — і це навмисно. Питання, на яке відповідає таблиця, звучить «скільки цього долітає до мене», а не «якою дорогою». Але звідси й пастка: апарат, під'єднаний і радіомодемом, і кабелем, дасть один рядок і **суму** двох потоків. Подвоєна частота серцебиття — майже завжди не дивна прошивка, а два шляхи до однієї станції.

Розрізнити це можна, не чіпаючи ключа. У заголовку кожного кадру є порядковий номер, який кожен компонент нарощує на кожному надісланому кадрі — на один байт, тобто по колу через кожні 256 кадрів. Різниця сусідніх номерів каже все:

```cpp
const uint8_t d = static_cast<uint8_t>(m.seq - s.last);   // навмисно за модулем 256
if      (d == 0)  ++s.dup;                 // той самий кадр удруге
else if (d == 1)  { }                      // рівно наступний
else if (d < 128) s.gap += (d - 1);        // стільки кадрів не долетіло
else              ++s.back;                // номер пішов назад
```

Віднімання беззнакових однобайтових чисел саме собою обертається за модулем 256, тож перехід через межу лічильника обробляти окремо не треба. Половина кола — сто двадцять вісім — ділить різниці на «попереду» й «позаду»: усе, що далі, читаємо як крок назад, а не як гігантську втрату.

Три картини виходять різні. Рівний потік: пропусків нема, дублів нема. Радіо губить: ростуть пропуски, а показана частота стає нижчою за ту, яку апарат підтвердив. Два шляхи: пропусків нема, а **половина кадрів здубльована** — бо кожен приходить двічі. Якщо ж дороги мають різну затримку, дублі перемішуються з кроками назад, і високий лічильник `back` каже те саме.

![Три картини лічильника послідовности: рівний потік, втрати, подвоєний шлях](/reference/qgroundcontrol/links/mavlink-inspector/img/proj-seq-doubling.svg)

*Той самий лічильник дає обидва діагнози: пропуски міряють утрати каналу, дублі виказують другу дорогу.*

> 🔧 **Навіщо це.** Дві однакові з вигляду скарги розділяються одним числом. «Частота вдвічі більша за очікувану», де половина кадрів здубльована, — це не апарат і не прошивка, а зайвий канал, який до того ж двічі витрачає смугу. «Частота нижча за підтверджену» з ненульовими пропусками — це канал не встигає, і різниця двох чисел прямо міряє, скільки з надісланого гине дорогою.

Точнішу оцінку втрат — з урахуванням того, що лічильник спільний на всі повідомлення компонента, — розібрано в [підрахунку втрат](book:qgroundcontrol/mavlink-handling/math-loss-counting.md); тут потрібне лише грубе розрізнення трьох випадків.

## Робочий код

Мова тут не обирається: програма компілюється зі згенерованими заголовками MAVLink і читає навантаження за зсувами, тож це C++ і нічого іншого. Джерело UDP написане під POSIX; на Windows ті самі двадцять рядків пишуться через Winsock.

```cpp
// mavtap.cpp — спостерігач за потоком MAVLink: рядки, частоти, поля, запис кривої.
//
// збірка (заголовки — з генерації mavgen для свого діалекту):
//   g++ -O2 -std=c++17 mavtap.cpp -I<тека згенерованих заголовків> -o mavtap
//
// БЕЗ ЦЬОГО ВИЗНАЧЕННЯ таблиць опису повідомлень у збірці не буде,
// і mavlink_get_message_info() просто не існуватиме.
#define MAVLINK_USE_MESSAGE_INFO
#include <common/mavlink.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <unordered_map>
#include <vector>

#if !defined(_WIN32)
#  include <netinet/in.h>
#  include <sys/socket.h>
#  include <sys/time.h>
#  include <unistd.h>
#endif

// ── сталі ───────────────────────────────────────────────────────────────────
constexpr uint8_t kChannel   = MAVLINK_COMM_0;   // свій слот розбирача
constexpr int     kStampBytes = 8;               // мітка часу запису .tlog
constexpr double  kTickSec    = 1.0;             // такт оцінювача частоти
constexpr double  kAlphaNew   = 0.8;             // вага свіжого відліку
constexpr size_t  kMaxRows    = 4096;            // стеля рядків на систему

// ── значення розрізняльного поля: короткий текст без виділення пам'яті ──────
struct Inst {
    char    s[24] = {};
    uint8_t n     = 0;

    bool operator==(const Inst& o) const {
        return n == o.n && std::memcmp(s, o.s, n) == 0;
    }
    void set(const char* p, size_t k) {
        n = static_cast<uint8_t>(k < sizeof(s) ? k : sizeof(s));
        std::memcpy(s, p, n);
    }
};

struct RowKey {
    uint32_t msgid  = 0;
    uint8_t  compid = 0;
    Inst     inst;

    bool operator==(const RowKey& o) const {
        return msgid == o.msgid && compid == o.compid && inst == o.inst;
    }
};

struct RowKeyHash {
    size_t operator()(const RowKey& k) const noexcept {
        uint64_t h = 1469598103934665603ULL;                 // FNV-1a, 64 біти
        auto mix = [&h](uint8_t b) { h ^= b; h *= 1099511628211ULL; };
        for (int i = 0; i < 4; ++i) mix(static_cast<uint8_t>(k.msgid >> (8 * i)));
        mix(k.compid);
        for (uint8_t i = 0; i < k.inst.n; ++i) mix(static_cast<uint8_t>(k.inst.s[i]));
        return static_cast<size_t>(h);
    }
};

// ── читання поля з навантаження ─────────────────────────────────────────────
static unsigned typeSize(mavlink_message_type_t t) {
    switch (t) {
    case MAVLINK_TYPE_CHAR:
    case MAVLINK_TYPE_UINT8_T:
    case MAVLINK_TYPE_INT8_T:   return 1;
    case MAVLINK_TYPE_UINT16_T:
    case MAVLINK_TYPE_INT16_T:  return 2;
    case MAVLINK_TYPE_UINT32_T:
    case MAVLINK_TYPE_INT32_T:
    case MAVLINK_TYPE_FLOAT:    return 4;
    default:                    return 8;
    }
}

// ЗАВЖДИ memcpy. Початок навантаження кратний восьми, але поле стоїть на своєму
// wire_offset: uint16_t за зсувом 41 і uint32_t за зсувом 50 — звичайна річ.
template <typename T>
static T wireRead(const mavlink_message_t& m, unsigned off) {
    T v{};
    std::memcpy(&v, _MAV_PAYLOAD(&m) + off, sizeof(T));
    return v;
}

struct Scalar { char txt[32]; };

static Scalar readScalar(const mavlink_message_t& m, mavlink_message_type_t t, unsigned off) {
    Scalar r{{0}};
    switch (t) {
    case MAVLINK_TYPE_UINT8_T:
        std::snprintf(r.txt, sizeof(r.txt), "%u",
                      unsigned(wireRead<uint8_t>(m, off))); break;
    case MAVLINK_TYPE_INT8_T:
        std::snprintf(r.txt, sizeof(r.txt), "%d",
                      int(wireRead<int8_t>(m, off))); break;
    case MAVLINK_TYPE_UINT16_T:
        std::snprintf(r.txt, sizeof(r.txt), "%u",
                      unsigned(wireRead<uint16_t>(m, off))); break;
    case MAVLINK_TYPE_INT16_T:
        std::snprintf(r.txt, sizeof(r.txt), "%d",
                      int(wireRead<int16_t>(m, off))); break;
    case MAVLINK_TYPE_UINT32_T:
        std::snprintf(r.txt, sizeof(r.txt), "%lu",
                      (unsigned long)wireRead<uint32_t>(m, off)); break;
    case MAVLINK_TYPE_INT32_T:
        std::snprintf(r.txt, sizeof(r.txt), "%ld",
                      (long)wireRead<int32_t>(m, off)); break;
    case MAVLINK_TYPE_UINT64_T:
        std::snprintf(r.txt, sizeof(r.txt), "%llu",
                      (unsigned long long)wireRead<uint64_t>(m, off)); break;
    case MAVLINK_TYPE_INT64_T:
        std::snprintf(r.txt, sizeof(r.txt), "%lld",
                      (long long)wireRead<int64_t>(m, off)); break;
    case MAVLINK_TYPE_FLOAT:
        std::snprintf(r.txt, sizeof(r.txt), "%.6g",
                      double(wireRead<float>(m, off))); break;
    case MAVLINK_TYPE_DOUBLE:
        std::snprintf(r.txt, sizeof(r.txt), "%.10g",
                      wireRead<double>(m, off)); break;
    default:
        r.txt[0] = '?'; r.txt[1] = '\0'; break;
    }
    return r;
}

// ── правила розрізнення примірників: ДАНІ, не код ───────────────────────────
static std::unordered_map<uint32_t, unsigned> g_instField;   // msgid → номер поля

static bool addInstanceRule(const char* msgName, const char* fieldName, bool quiet = false) {
    const mavlink_message_info_t* info = mavlink_get_message_info_by_name(msgName);
    if (!info) {
        if (!quiet) std::fprintf(stderr, "діалект не знає повідомлення %s\n", msgName);
        return false;
    }
    for (unsigned i = 0; i < info->num_fields; ++i) {
        if (std::strcmp(info->fields[i].name, fieldName) != 0) continue;
        const mavlink_message_type_t t = info->fields[i].type;
        if (t == MAVLINK_TYPE_FLOAT || t == MAVLINK_TYPE_DOUBLE) {
            std::fprintf(stderr, "%s.%s дробове — розрізняти таким не можна\n", msgName, fieldName);
            return false;
        }
        g_instField[info->msgid] = i;
        return true;
    }
    if (!quiet) std::fprintf(stderr, "у %s немає поля %s\n", msgName, fieldName);
    return false;
}

static void defaultInstanceRules() {
    static const char* kRules[][2] = {
        {"BATTERY_STATUS",    "id"},     {"ESC_INFO",   "index"},
        {"ESC_STATUS",        "index"},  {"DEBUG",      "ind"},
        {"NAMED_VALUE_FLOAT", "name"},   {"NAMED_VALUE_INT", "name"},
        {"DEBUG_VECT",        "name"},
        {"GIMBAL_DEVICE_ATTITUDE_STATUS", "gimbal_device_id"},
    };
    for (const auto& r : kRules) addInstanceRule(r[0], r[1], true);   // чого немає — мовчки повз
}

// Одне правило працює і для числа, і для рядка: NAMED_VALUE_FLOAT.name — char[10].
static Inst instanceOf(const mavlink_message_t& m, const mavlink_message_info_t* info) {
    Inst inst;
    const auto it = g_instField.find(m.msgid);
    if (it == g_instField.end()) return inst;              // повідомлення без примірників

    const mavlink_field_info_t& fi = info->fields[it->second];
    if (fi.type == MAVLINK_TYPE_CHAR) {
        const unsigned lim = fi.array_length ? fi.array_length : 1u;
        const char* p = _MAV_PAYLOAD(&m) + fi.wire_offset;
        size_t k = 0;
        while (k < lim && k < sizeof(inst.s) && p[k]) ++k;
        inst.set(p, k);
        return inst;
    }
    const Scalar sc = readScalar(m, fi.type, fi.wire_offset);
    inst.set(sc.txt, std::strlen(sc.txt));
    return inst;
}

// ── поля рядка ──────────────────────────────────────────────────────────────
struct Field {
    std::string            name;                        // з індексом: voltages[3]
    unsigned               off   = 0;                   // зсув у навантаженні
    mavlink_message_type_t type  = MAVLINK_TYPE_CHAR;
    unsigned               chars = 0;                   // >0 — рядковий масив
    std::string            text;                        // останнє показане
    bool                   logged = false;
};

// Порядок полів в описі — порядок XML, а НЕ порядок у навантаженні.
// Місце в байтах питаємо лише в wire_offset.
static std::vector<Field> buildFields(const mavlink_message_info_t* info) {
    std::vector<Field> out;
    out.reserve(info->num_fields);
    for (unsigned i = 0; i < info->num_fields; ++i) {
        const mavlink_field_info_t& fi = info->fields[i];

        if (fi.type == MAVLINK_TYPE_CHAR) {              // ім'я лишається одним полем
            Field f;
            f.name  = fi.name;
            f.off   = fi.wire_offset;
            f.type  = fi.type;
            f.chars = fi.array_length ? fi.array_length : 1u;
            out.push_back(std::move(f));
            continue;
        }
        if (fi.array_length == 0) {                      // скаляр
            Field f;
            f.name = fi.name;
            f.off  = fi.wire_offset;
            f.type = fi.type;
            out.push_back(std::move(f));
            continue;
        }
        const unsigned esz = typeSize(fi.type);          // масив → окремі елементи
        for (unsigned j = 0; j < fi.array_length; ++j) {
            Field f;
            f.name = std::string(fi.name) + "[" + std::to_string(j) + "]";
            f.off  = fi.wire_offset + j * esz;
            f.type = fi.type;
            out.push_back(std::move(f));
        }
    }
    return out;
}

// ── рядок і система ─────────────────────────────────────────────────────────
struct Row {
    RowKey             key;
    std::string        title;              // BATTERY_STATUS[1]
    uint64_t           count = 0, lastCount = 0;
    double             rateHz = 0.0;
    mavlink_message_t  last{};             // копія ОСТАННЬОГО кадру
    bool               selected  = false;
    bool               anyLogged = false;
    std::vector<Field> fields;
};

struct SeqState { uint8_t last = 0; bool have = false; uint64_t dup = 0, gap = 0, back = 0; };

struct System {
    std::unordered_map<RowKey, Row, RowKeyHash> rows;
    std::unordered_map<uint8_t, SeqState>       seq;
    bool overflow = false;
};

static bool matches(const std::string& title, const std::string& pat) {
    if (pat.empty()) return false;
    if (title == pat) return true;
    const size_t br = title.find('[');                   // BATTERY_STATUS = усі примірники
    return br != std::string::npos && title.compare(0, br, pat) == 0;
}

class Tap {
public:
    void selectPattern(const std::string& p) { _selectPat = p; }

    bool logSpec(const std::string& spec) {              // ROW.FIELD
        const size_t dot = spec.find('.');
        if (dot == std::string::npos) return false;
        _logRow   = spec.substr(0, dot);
        _logField = spec.substr(dot + 1);
        const std::string path = "mavtap-" + _logField + ".csv";
        _logOut = std::fopen(path.c_str(), "w");
        if (_logOut) std::fprintf(_logOut, "t_s,%s\n", _logField.c_str());
        return _logOut != nullptr;
    }

    void onMessage(const mavlink_message_t& m, uint64_t tUsec) {
        System& sys = _systems[m.sysid];                 // система з'являється з байта заголовка
        trackSeq(sys, m);

        const mavlink_message_info_t* info = mavlink_get_message_info(&m);
        if (!info) return;

        RowKey key;
        key.msgid  = m.msgid;
        key.compid = m.compid;
        key.inst   = instanceOf(m, info);

        auto it = sys.rows.find(key);
        if (it == sys.rows.end()) {
            if (sys.rows.size() >= kMaxRows) { sys.overflow = true; return; }
            it = sys.rows.emplace(key, makeRow(key, info)).first;
        }

        Row& row = it->second;
        ++row.count;                                     // ДЕШЕВО
        row.last = m;                                    // ДЕШЕВО: 296 Б, без купи
        if (row.anyLogged) logSample(row, tUsec);        // дорого — але лише записуване поле
    }

    void tick(double elapsedSec) {
        if (elapsedSec <= 0.0) return;
        for (auto& sp : _systems)
            for (auto& rp : sp.second.rows) {
                Row& row = rp.second;
                const double instHz = double(row.count - row.lastCount) / elapsedSec;
                row.rateHz    = (1.0 - kAlphaNew) * row.rateHz + kAlphaNew * instHz;
                row.lastCount = row.count;
            }
        if (_logOut) std::fflush(_logOut);
    }

    void print(uint64_t tUsec) {
        std::printf("\x1b[H\x1b[2J");                    // очистити екран
        std::printf("t = %.1f с\n", double(tUsec) / 1e6);

        for (auto& sp : _systems) {
            System& sys = sp.second;
            std::printf("\n-- система %u --\n", unsigned(sp.first));
            std::printf("   %-30s comp    кадрів      Гц\n", "рядок");

            std::vector<Row*> ordered;                   // порядок будуємо на друці:
            ordered.reserve(sys.rows.size());            // сорок рядків сортуються задарма
            for (auto& rp : sys.rows) ordered.push_back(&rp.second);
            std::sort(ordered.begin(), ordered.end(), [](const Row* a, const Row* b) {
                if (a->key.compid != b->key.compid) return a->key.compid < b->key.compid;
                return a->title < b->title;
            });

            for (const Row* r : ordered)
                std::printf("   %-30s %4u %9llu %7.1f\n", r->title.c_str(),
                            unsigned(r->key.compid), (unsigned long long)r->count, r->rateHz);

            for (const auto& sq : sys.seq)
                std::printf("   comp %u: пропущено %llu · здубльовано %llu · назад %llu\n",
                            unsigned(sq.first), (unsigned long long)sq.second.gap,
                            (unsigned long long)sq.second.dup,
                            (unsigned long long)sq.second.back);
            if (sys.overflow)
                std::printf("   стеля рядків досягнута — нові примірники не заводяться\n");

            for (Row* r : ordered) {                     // розкладання — тут, на такті друку
                if (!r->selected) continue;
                decodeRow(*r);
                std::printf("\n   %s\n", r->title.c_str());
                for (const Field& f : r->fields)
                    std::printf("      %-24s %s\n", f.name.c_str(), f.text.c_str());
            }
        }
        std::fflush(stdout);
    }

private:
    Row makeRow(const RowKey& key, const mavlink_message_info_t* info) const {
        Row r;
        r.key   = key;
        r.title = info->name;
        if (key.inst.n) r.title += "[" + std::string(key.inst.s, key.inst.n) + "]";
        r.fields   = buildFields(info);
        r.selected = matches(r.title, _selectPat);
        if (_logOut && matches(r.title, _logRow))
            for (Field& f : r.fields)
                if (f.name == _logField) { f.logged = true; r.anyLogged = true; }
        return r;
    }

    static void trackSeq(System& sys, const mavlink_message_t& m) {
        SeqState& s = sys.seq[m.compid];
        if (!s.have) { s.last = m.seq; s.have = true; return; }

        const uint8_t d = static_cast<uint8_t>(m.seq - s.last);   // за модулем 256
        if      (d == 0)  ++s.dup;                  // той самий кадр удруге — дві дороги
        else if (d == 1)  { }                       // рівно наступний
        else if (d < 128) s.gap += (d - 1);         // стільки кадрів не долетіло
        else              ++s.back;                 // номер пішов назад

        if (d != 0 && d < 128) s.last = m.seq;      // назад позначку не рухаємо
    }

    void decodeRow(Row& row) const {
        for (Field& f : row.fields) {
            if (f.chars) {                          // символьний масив — як текст
                const char* p = _MAV_PAYLOAD(&row.last) + f.off;
                size_t k = 0;
                while (k < f.chars && p[k]) ++k;
                f.text.assign(p, k);
                continue;
            }
            f.text = readScalar(row.last, f.type, f.off).txt;
        }
    }

    void logSample(Row& row, uint64_t tUsec) {
        for (const Field& f : row.fields) {
            if (!f.logged) continue;
            const Scalar sc = readScalar(row.last, f.type, f.off);
            std::fprintf(_logOut, "%.6f,%s\n", double(tUsec) / 1e6, sc.txt);
        }
    }

    std::map<uint8_t, System> _systems;                  // впорядкована за sysid — для друку
    std::string _selectPat, _logRow, _logField;
    std::FILE*  _logOut = nullptr;
};

// ── джерело: файл телеметрії ────────────────────────────────────────────────
// Запис — вісім байтів часу (мікросекунди від епохи, старший байт першим) і
// кадр як прийшов. Розпізнавання чужого порядку байтів і перемотування тут
// свідомо опущено: це задача окремого читача логу.
static int runTlog(const char* path, Tap& tap) {
    std::FILE* f = std::fopen(path, "rb");
    if (!f) { std::perror(path); return 1; }

    mavlink_message_t msg{};
    mavlink_status_t  st{};
    uint8_t  stamp[kStampBytes];
    uint64_t firstUsec = 0, lastTickUsec = 0;
    bool     started = false;

    while (std::fread(stamp, 1, kStampBytes, f) == size_t(kStampBytes)) {
        uint64_t tUsec = 0;
        for (int i = 0; i < kStampBytes; ++i) tUsec = (tUsec << 8) | stamp[i];

        // Межа кадру у файлі відома точно, тож стан каналу скидаємо на кожному
        // записі: недобудований залишок попереднього не має продовжуватися.
        mavlink_reset_channel_status(kChannel);

        bool got = false;
        int  c   = 0;
        for (int k = 0; k < MAVLINK_MAX_PACKET_LEN && (c = std::fgetc(f)) != EOF; ++k)
            if (mavlink_parse_char(kChannel, uint8_t(c), &msg, &st)) { got = true; break; }
        if (!got) break;                         // обірваний хвіст — звичайний кінець

        if (!started) { firstUsec = lastTickUsec = tUsec; started = true; }
        tap.onMessage(msg, tUsec - firstUsec);

        // ТАКТ ВЕДЕ ЧАС ЛОГУ: таблиця однакова, хоч файл читається за секунду,
        // хоч відтворюється в темпі польоту.
        if (tUsec >= lastTickUsec + uint64_t(kTickSec * 1e6)) {
            tap.tick(double(tUsec - lastTickUsec) / 1e6);
            tap.print(tUsec - firstUsec);
            lastTickUsec = tUsec;
        }
    }
    std::fclose(f);
    return 0;
}

// ── джерело: UDP ────────────────────────────────────────────────────────────
#if !defined(_WIN32)
static int runUdp(int port, Tap& tap) {
    const int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) { std::perror("socket"); return 1; }

    sockaddr_in addr{};
    addr.sin_family      = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port        = htons(uint16_t(port));
    if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        std::perror("bind");
        return 1;
    }

    timeval tv{};                                // щоб такт спрацьовував і в тиші
    tv.tv_usec = 200000;
    ::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    mavlink_message_t msg{};
    mavlink_status_t  st{};
    uint8_t buf[2048];

    using Clock = std::chrono::steady_clock;     // МОНОТОННИЙ: міряємо проміжок
    const auto t0 = Clock::now();
    auto lastTick = t0;

    for (;;) {
        const ssize_t n   = ::recv(fd, buf, sizeof(buf), 0);
        const auto    now = Clock::now();
        const uint64_t tUsec =
            std::chrono::duration_cast<std::chrono::microseconds>(now - t0).count();

        for (ssize_t i = 0; i < n; ++i)
            if (mavlink_parse_char(kChannel, buf[i], &msg, &st)) tap.onMessage(msg, tUsec);

        const double elapsed = std::chrono::duration<double>(now - lastTick).count();
        if (elapsed >= kTickSec) {
            tap.tick(elapsed);
            tap.print(tUsec);
            lastTick = now;
        }
    }
}
#endif

int main(int argc, char** argv) {
    const char* tlog = nullptr;
    int         port = 0;
    Tap         tap;

    defaultInstanceRules();

    for (int i = 1; i + 1 < argc; i += 2) {
        const std::string k = argv[i], v = argv[i + 1];
        if      (k == "--tlog")   tlog = argv[i + 1];
        else if (k == "--udp")    port = std::atoi(argv[i + 1]);
        else if (k == "--select") tap.selectPattern(v);
        else if (k == "--log")    tap.logSpec(v);
        else if (k == "--instance") {
            const size_t eq = v.find('=');
            if (eq != std::string::npos)
                addInstanceRule(v.substr(0, eq).c_str(), v.substr(eq + 1).c_str());
        }
    }

    if (tlog) return runTlog(tlog, tap);
#if !defined(_WIN32)
    if (port) return runUdp(port, tap);
#endif
    std::fprintf(stderr,
        "usage: mavtap (--tlog FILE | --udp PORT) [--select ROW]\n"
        "              [--log ROW.FIELD] [--instance MSG=FIELD]\n");
    return 2;
}
```

## Складність

```
n — рядків у системі · k — полів у рядку

прийняти кадр             O(1)         хеш трійки, лічильник, копія 296 Б
завести рядок             O(k)         один раз на рядок: список полів з опису
такт частоти              O(n)         раз на секунду по всіх рядках
друк таблиці              O(n log n)   сортування назв на кожному друці
розкласти вибраний рядок  O(k)         раз на друк
записати поле кривої      O(1)         на кожен кадр рядка, чиє поле пишуть
пам'ять                   O(n·k)       ≈ 300 Б на рядок плюс текст на поле
```

Сортування на кожному друці варте окремого слова, бо в станції зроблено інакше — там рядки тримають упорядкованими й уставляють двійковим пошуком. Причина не в швидкості: список **сам є моделлю**, до якої прив'язаний інтерфейс, і вставка посередині зсуває індекси, тобто виривала б вибраний рядок з-під курсора. Друкована таблиця такої проблеми не має — вона щоразу будується заново, тож упорядковувати сховище нема потреби.

## Пастки

**Приведення вказівника замість `memcpy`.** Найпоширеніша помилка в такому коді — `*(const uint16_t*)(payload + off)`. Вона виживає на тестових повідомленнях зі старими полями й падає на розширених: `voltages_ext` у `BATTERY_STATUS` стоїть за зсувом 41, `fault_bitmask` — за зсувом 50. На архітектурі, що вимагає вирівнювання, це виняток; на тій, що не вимагає, — тихе порушення правил псевдонімів, яке оптимізатор має право використати як завгодно. Тому доступ лише через `memcpy`, і про це варто домовитися один раз, а не згадувати щоразу.

**Нуль, якого не надсилали.** Розбирач дописує нулі в хвіст обрізаного навантаження, тож поле, якого в кадрі не було, читається як нуль і від справжнього нуля не відрізняється. Це неусувна властивість протоколу: інформації «не надіслано» в кадрі немає. Але поки кадри йдуть крізь розбирач, читати можна будь-яке поле. Кадр, зібраний у структуру руками — з файлу, з чужого коду, з тесту, — цієї гарантії не має, і його треба обнуляти самому.

**Спільний слот розбирача.** Бібліотека тримає стан на канал у статичній таблиці, а каналів обмежена кількість — шістнадцять на настільних системах, чотири на решті. Два джерела на одному слоті почнуть добудовувати кадри одне одному, і результат виглядатиме як зіпсований потік. Кожне джерело бере свій номер.

**Нескінченні примірники.** Ключ із розрізняльним полем зручний, доки значень небагато. `NAMED_VALUE_FLOAT` цю умову порушує легко: налагоджувальний код прошивки може слати сотні різних імен, а кожне заводить свій рядок зі своїм списком полів. Тому стеля рядків — не перестрахування, а необхідність; без неї таблиця росте, доки не з'їсть пам'ять.

**Такт, який не дорівнює секунді.** Ділити різницю лічильників на одиницю замість виміряного проміжку — помилка, яка на живому каналі дає кілька відсотків похибки й тому довго лишається непоміченою. На файлі вона стає катастрофічною: лог, прочитаний за секунду, покаже тисячі герців. Одне ділення на справжній проміжок закриває обидва випадки.

**Обгортання номера послідовности.** Лічильник однобайтовий і йде по колу через кожні 256 кадрів, тож утрата рівно двохсот п'ятдесяти шести кадрів поспіль невидима: різниця дає одиницю. На двадцяти герцах це тринадцять секунд повної тиші — рідко, але буває, і саме тоді, коли діагноз найпотрібніший. Виказує такий провал не лічильник пропусків, а частота, що сповзла до нуля й повернулася.

**Ключ без каналу.** Об'єднання каналів в один рядок — вибір, а не недогляд, і зворотний вибір теж має ціну. Додайте канал у ключ — і апарат на двох каналах дасть два комплекти рядків, кожен зі своєю частотою; питання «скільки цього долітає загалом» доведеться рахувати додаванням. Два різні питання, два різні ключі; лічильник дублів дозволяє відповісти на обидва, не перебудовуючи таблиці.
