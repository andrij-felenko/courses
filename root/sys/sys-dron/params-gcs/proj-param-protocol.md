# ⚙️ Завантаження всіх параметрів по MAVLink: протокол і його пастки

**Задача.** Наземна станція щойно під'єдналася до апарата й має показати оператору **повний** список параметрів — а їх понад тисячу. Канал між землею й бортом тонкий і **ненадійний**: пакети губляться, приходять не по черзі, дублюються. Наївне «попросив — отримав усе» тут не працює: якщо десяток `PARAM_VALUE` загубиться по дорозі, станція покаже неповний набір і нічого про це не знатиме. Тому навколо простих повідомлень MAVLink збудовано **маленький протокол із підрахунком**: запит усього списку, відстеження за номерами, перезапит загублених, і окремо — надійний запис із підтвердженням. Напишімо його логіку мовою прошивки (C/C++) і подивимося, де саме він рятує від тихих помилок.

Усе тримається на чотирьох повідомленнях. Станція шле `PARAM_REQUEST_LIST` (дай усе), `PARAM_REQUEST_READ` (дай одне — за іменем або номером) і `PARAM_SET` (запиши нове). Борт на **кожен** із цих запитів відповідає одним і тим самим повідомленням — `PARAM_VALUE`, де лежить не лише значення, а й два ключові числа: `param_count` (скільки всього параметрів) і `param_index` (котрий це за порядком, з нуля). Саме ця пара перетворює потік окремих пакетів на щось, що можна **перевірити на повноту**.

:::tabs
```cpp
// Поля PARAM_VALUE, які несе кожна відповідь борту:
struct mavlink_param_value_t {
    float    param_value;     // значення, ЗАВЖДИ як IEEE-754 float
    uint16_t param_count;     // скільки всього параметрів на апараті
    uint16_t param_index;     // індекс ЦЬОГО параметра (0 .. count-1)
    char     param_id[16];    // ім'я; якщо рівно 16 символів — БЕЗ \0 у кінці
    uint8_t  param_type;      // як трактувати float: int8/16/32, uint…, float
};
```
```python
import struct
from dataclasses import dataclass

# Поля PARAM_VALUE, які несе кожна відповідь борту:
@dataclass
class ParamValue:
    param_value: float    # значення, ЗАВЖДИ як IEEE-754 float
    param_count: int      # скільки всього параметрів на апараті
    param_index: int      # індекс ЦЬОГО параметра (0 .. count-1)
    param_id: bytes       # ім'я; якщо рівно 16 байтів — БЕЗ \0 у кінці
    param_type: int       # як трактувати float: int8/16/32, uint…, float
```
```go
// Поля PARAM_VALUE, які несе кожна відповідь борту:
type ParamValue struct {
    ParamValue float32   // значення, ЗАВЖДИ як IEEE-754 float
    ParamCount uint16    // скільки всього параметрів на апараті
    ParamIndex uint16    // індекс ЦЬОГО параметра (0 .. count-1)
    ParamID    [16]byte  // ім'я; якщо рівно 16 байтів — БЕЗ \0 у кінці
    ParamType  uint8     // як трактувати float: int8/16/32, uint…, float
}
```
:::

## Float, що насправді ціле

Перша пастка ховається в типі `param_value`. По дроту значення **завжди** їде як 4-байтовий `float` — навіть `FRAME_CLASS`, що за змістом ціле, навіть прапорець `0/1`. Який це насправді тип, каже окреме поле `param_type`. Тому станція не може просто привласнити `float` у ціле через мову — велике 32-бітне ціле в `float` не влізе без втрати точності, і `1000001` стане `1000000`. Правильно — **перекласти байти**, а не число:

:::tabs
```cpp
// Дістати ціле з param_value, не псуючи старші біти:
int32_t param_as_int(float v) {
    int32_t out;
    memcpy(&out, &v, sizeof(out));   // ті самі 4 байти, інша інтерпретація
    return out;
}
```
```python
import struct

# Дістати ціле з param_value, не псуючи старші біти:
def param_as_int(v: float) -> int:
    # ті самі 4 байти, інша інтерпретація
    return struct.unpack("<i", struct.pack("<f", v))[0]
```
```go
import "math"

// Дістати ціле з param_value, не псуючи старші біти:
func paramAsInt(v float32) int32 {
    // ті самі 4 байти, інша інтерпретація
    return int32(math.Float32bits(v))
}
```
:::

> 🔧 **Навіщо це.** Якщо станція покаже `ATC_RAT_RLL_P` округленим до цілого, оператор подумає, що коефіцієнт `0`, і занулить керування. А якщо вона зіпсує велике ціле (наприклад, бітову маску ввімкнених давачів), запис назад **тихо перевизначить** конфігурацію апарата. Тому байтова, а не числова, інтерпретація `param_value` — питання не стилю, а безпеки.

Який саме це тип, каже `param_type` — значення з переліку `MAV_PARAM_TYPE`. Станція мусить тримати **обидві** дороги: для справжніх дробових (`REAL32`) брати `float` як є, а для цілих (`INT8…INT32`, `UINT8…UINT32`) — перекладати байти. Дрібний, але злий нюанс: апарат на ArduPilot повертає `param_type` як `REAL32` навіть для тих параметрів, що за змістом цілі, тож остаточне трактування станція бере з власного довідника імен, а не лише з типу в пакеті.

:::tabs
```cpp
// Перетягнути значення в потрібне ціле за оголошеним типом:
int32_t typed_int(const mavlink_param_value_t *p) {
    switch (p->param_type) {
        case MAV_PARAM_TYPE_INT8:
        case MAV_PARAM_TYPE_INT16:
        case MAV_PARAM_TYPE_INT32:
        case MAV_PARAM_TYPE_UINT8:
        case MAV_PARAM_TYPE_UINT16:
        case MAV_PARAM_TYPE_UINT32:
            return param_as_int(p->param_value);   // байти, не округлення
        default:
            return (int32_t) lroundf(p->param_value);  // справді float
    }
}
```
```python
_INT_TYPES = {
    MAV_PARAM_TYPE_INT8,  MAV_PARAM_TYPE_INT16,  MAV_PARAM_TYPE_INT32,
    MAV_PARAM_TYPE_UINT8, MAV_PARAM_TYPE_UINT16, MAV_PARAM_TYPE_UINT32,
}

# Перетягнути значення в потрібне ціле за оголошеним типом:
def typed_int(p: ParamValue) -> int:
    if p.param_type in _INT_TYPES:
        return param_as_int(p.param_value)      # байти, не округлення
    return round(p.param_value)                 # справді float
```
```go
// Перетягнути значення в потрібне ціле за оголошеним типом:
func typedInt(p *ParamValue) int32 {
    switch p.ParamType {
    case mavParamTypeInt8, mavParamTypeInt16, mavParamTypeInt32,
        mavParamTypeUint8, mavParamTypeUint16, mavParamTypeUint32:
        return paramAsInt(p.ParamValue) // байти, не округлення
    default:
        return int32(math.Round(float64(p.ParamValue))) // справді float
    }
}
```
:::

## Читання всіх: рахуй за номерами, перепитуй загублені

Тепер головне. Станція шле `PARAM_REQUEST_LIST` **один раз** і починає приймати `PARAM_VALUE`. Перший же пакет каже, скільки всього параметрів (`param_count`) — і станція заводить таблицю «отримано / ні» на стільки клітинок. Далі кожен пакет відмічає свою клітинку за `param_index`. Ключова деталь — **таймер після кожного** `PARAM_VALUE`: поки пакети йдуть, його щоразу перезапускають; щойно потік замовк на умовний час — список або повний, або в ньому є діри.

:::tabs
```cpp
#define PARAM_TIMEOUT_MS  1000     // тиша довша за це = потік завмер

static char    (*names)[16];       // таблиця імен, розмір param_count
static float    *values;
static bool     *got;              // got[i] — чи прийшов параметр i
static uint16_t  total;            // param_count з першого пакета
static uint16_t  have;             // скільки вже маємо
static uint32_t  last_rx_ms;       // коли прийшов останній PARAM_VALUE

// Викликається на КОЖЕН вхідний PARAM_VALUE:
void on_param_value(const mavlink_param_value_t *p) {
    if (total == 0) {                      // перший пакет задає розмір
        total  = p->param_count;
        names  = (char(*)[16]) calloc(total, 16);
        values = (float*)      calloc(total, sizeof(float));
        got    = (bool*)       calloc(total, sizeof(bool));
    }
    uint16_t i = p->param_index;
    if (i < total && !got[i]) {            // дублікати ігноруємо
        memcpy(names[i], p->param_id, 16);
        values[i] = p->param_value;
        got[i]    = true;
        have++;
    }
    last_rx_ms = now_ms();                 // потік живий — зсуваємо таймер
}
```
```python
PARAM_TIMEOUT_MS = 1000     # тиша довша за це = потік завмер

class ParamDownload:
    def __init__(self):
        self.total = 0            # param_count з першого пакета
        self.have = 0             # скільки вже маємо
        self.names = []           # таблиця імен, розмір param_count
        self.values = []
        self.got = []             # got[i] — чи прийшов параметр i
        self.last_rx_ms = 0       # коли прийшов останній PARAM_VALUE

    # Викликається на КОЖЕН вхідний PARAM_VALUE:
    def on_param_value(self, p: ParamValue) -> None:
        if self.total == 0:                       # перший пакет задає розмір
            self.total  = p.param_count
            self.names  = [b""]    * self.total
            self.values = [0.0]    * self.total
            self.got    = [False]  * self.total
        i = p.param_index
        if i < self.total and not self.got[i]:    # дублікати ігноруємо
            self.names[i]  = p.param_id[:16]
            self.values[i] = p.param_value
            self.got[i]    = True
            self.have     += 1
        self.last_rx_ms = now_ms()                # потік живий — зсуваємо таймер
```
```go
const paramTimeoutMS = 1000 // тиша довша за це = потік завмер

type ParamDownload struct {
    Total    uint16     // param_count з першого пакета
    Have     uint16     // скільки вже маємо
    Names    [][16]byte // таблиця імен, розмір param_count
    Values   []float32
    Got      []bool     // Got[i] — чи прийшов параметр i
    LastRxMS uint32     // коли прийшов останній PARAM_VALUE
}

// Викликається на КОЖЕН вхідний PARAM_VALUE:
func (d *ParamDownload) OnParamValue(p *ParamValue) {
    if d.Total == 0 { // перший пакет задає розмір
        d.Total = p.ParamCount
        d.Names = make([][16]byte, d.Total)
        d.Values = make([]float32, d.Total)
        d.Got = make([]bool, d.Total)
    }
    i := p.ParamIndex
    if i < d.Total && !d.Got[i] { // дублікати ігноруємо
        d.Names[i] = p.ParamID
        d.Values[i] = p.ParamValue
        d.Got[i] = true
        d.Have++
    }
    d.LastRxMS = nowMS() // потік живий — зсуваємо таймер
}
```
:::

Коли таймер спрацював, а `have < total` — пройдися таблицею й **адресно** перепитай кожну порожню клітинку, цього разу `PARAM_REQUEST_READ` за **індексом** (`param_index = i`, а `param_id` лишаємо порожнім). Тут є своя домовленість: `PARAM_REQUEST_READ` уміє адресувати параметр **двома способами** — або людським іменем (`param_id`, а `param_index = -1`), або номером (`param_index ≥ 0`, тоді `param_id` ігнорується). Для перезапиту дір номер зручніший: загублену клітинку ми знаємо саме за індексом, а імені її ще можемо й не мати (адже пакет із цим іменем — той самий, що загубився). Перепитувати по одному параметру надійніше за повторний `PARAM_REQUEST_LIST`: не треба знову гнати весь список заради десятка втрачених, і кожен перезапит б'є точно в ціль.

:::tabs
```cpp
// Викликається періодично, поки список неповний:
void param_download_tick(void) {
    if (total == 0) return;                       // ще не почали
    if (have >= total) { on_download_done(); return; }
    if (now_ms() - last_rx_ms < PARAM_TIMEOUT_MS) return;   // ще йдуть

    // потік завмер, але маємо не все — перепитуємо діри по одній
    for (uint16_t i = 0; i < total; i++) {
        if (!got[i]) {
            send_param_request_read(/*index=*/ i);
        }
    }
    last_rx_ms = now_ms();                         // дамо їм час відповісти
}
```
```python
# Викликається періодично, поки список неповний:
def param_download_tick(self) -> None:
    if self.total == 0:                           # ще не почали
        return
    if self.have >= self.total:
        self.on_download_done()
        return
    if now_ms() - self.last_rx_ms < PARAM_TIMEOUT_MS:  # ще йдуть
        return

    # потік завмер, але маємо не все — перепитуємо діри по одній
    for i in range(self.total):
        if not self.got[i]:
            send_param_request_read(index=i)
    self.last_rx_ms = now_ms()                    # дамо їм час відповісти
```
```go
// Викликається періодично, поки список неповний:
func (d *ParamDownload) Tick() {
    if d.Total == 0 { // ще не почали
        return
    }
    if d.Have >= d.Total {
        d.onDownloadDone()
        return
    }
    if nowMS()-d.LastRxMS < paramTimeoutMS { // ще йдуть
        return
    }

    // потік завмер, але маємо не все — перепитуємо діри по одній
    for i := uint16(0); i < d.Total; i++ {
        if !d.Got[i] {
            sendParamRequestRead(i)
        }
    }
    d.LastRxMS = nowMS() // дамо їм час відповісти
}
```
:::

Чому саме так, а не «попросив список — довірився»? Бо `param_count` дає **незалежну** мірку: станція знає очікувану кількість ще до того, як отримає всі пакети, тож **бачить** саму наявність дір, а не сподівається, що їх немає. Без цього лічильника втрачений `PARAM_VALUE` нічим не відрізнявся б від кінця списку.

Тепер про числа. Борт **не вистрілює** весь список миттєво — він віддає параметри потоком із обмеженою швидкістю (типово кількадесят на секунду), щоб не забити канал телеметрії. Прикинемо, скільки триває чесне завантаження:

```
параметрів:         1200
темп віддачі:        ~50 шт/с   (борт стримить, не все одразу)
час «чистого» зливу = 1200 / 50 = 24 с
таймер тиші:          1 с       (після останнього PARAM_VALUE)
→ повне завантаження ≈ 24..25 с, якщо нічого не загубилося
```

Звідси два практичні висновки. По-перше, таймер тиші має бути **помітно довшим** за проміжок між пакетами в потоці (~20 мс при 50 шт/с), інакше станція вирішить, що потік скінчився, на першій же дрібній затримці й кинеться даремно перепитувати. По-друге, ці 24 секунди — нормальна ціна першого під'єднання; саме тому станції кешують параметри й при повторному з'єднанні лише **звіряють** `param_count`, а не тягнуть усе наново.

## Запис: підтвердження приходить тим самим PARAM_VALUE

Запис симетричний, але з власною пасткою. Станція шле `PARAM_SET` (ім'я + значення + тип) — і борт **зобов'язаний** відповісти `PARAM_VALUE`, навіть якщо запис **не вдався**: тоді у відповіді буде старе значення. Тобто підтвердження запису й трансляція значення — це **те саме** повідомлення. Отже, надійний запис — це «надішли й дочекайся, що значення в `PARAM_VALUE` справді змінилося на бажане»; не дочекався — повтори.

:::tabs
```cpp
#define SET_TIMEOUT_MS  1000
#define SET_RETRIES     3

bool param_set_blocking(const char *id, float want, uint8_t type) {
    for (int attempt = 0; attempt < SET_RETRIES; attempt++) {
        send_param_set(id, want, type);
        uint32_t t0 = now_ms();
        while (now_ms() - t0 < SET_TIMEOUT_MS) {
            mavlink_param_value_t pv;
            if (recv_param_value(&pv) && name_eq(pv.param_id, id)) {
                return float_eq(pv.param_value, want);   // борт підтвердив САМЕ це
            }
        }
        // тиша → пакет загубився, шлемо PARAM_SET ще раз
    }
    return false;   // борт так і не підтвердив — не вважаємо записаним
}
```
```python
SET_TIMEOUT_MS = 1000
SET_RETRIES    = 3

def param_set_blocking(id: bytes, want: float, type: int) -> bool:
    for _ in range(SET_RETRIES):
        send_param_set(id, want, type)
        t0 = now_ms()
        while now_ms() - t0 < SET_TIMEOUT_MS:
            pv = recv_param_value()
            if pv is not None and name_eq(pv.param_id, id):
                return float_eq(pv.param_value, want)   # борт підтвердив САМЕ це
        # тиша → пакет загубився, шлемо PARAM_SET ще раз
    return False   # борт так і не підтвердив — не вважаємо записаним
```
```go
const (
    setTimeoutMS = 1000
    setRetries   = 3
)

func paramSetBlocking(id []byte, want float32, typ uint8) bool {
    for attempt := 0; attempt < setRetries; attempt++ {
        sendParamSet(id, want, typ)
        t0 := nowMS()
        for nowMS()-t0 < setTimeoutMS {
            if pv, ok := recvParamValue(); ok && nameEq(pv.ParamID[:], id) {
                return floatEq(pv.ParamValue, want) // борт підтвердив САМЕ це
            }
        }
        // тиша → пакет загубився, шлемо PARAM_SET ще раз
    }
    return false // борт так і не підтвердив — не вважаємо записаним
}
```
:::

Два місця тут варті уваги. По-перше, порівнювати ім'я треба обережно: `param_id` **не має** завершального `\0`, якщо в нього рівно 16 символів, тож звичний `strcmp` забіжить за межі — порівнюй не більше за 16 байтів. По-друге, **не можна** вважати запис успішним за самим фактом відсилання `PARAM_SET`: поки не прийшов `PARAM_VALUE` з потрібним значенням, на апараті ще може стояти старе число.

:::tabs
```cpp
// Безпечне порівняння імен MAVLink-параметрів (16 байтів, можливо без \0):
bool name_eq(const char *a, const char *b) {
    return strncmp(a, b, 16) == 0;
}
```
```python
# Безпечне порівняння імен MAVLink-параметрів (16 байтів, можливо без \0):
def name_eq(a: bytes, b: bytes) -> bool:
    return a[:16] == b[:16]
```
```go
import "bytes"

// Безпечне порівняння імен MAVLink-параметрів (16 байтів, можливо без \0):
func nameEq(a, b []byte) bool {
    trim := func(s []byte) []byte {
        if len(s) > 16 {
            s = s[:16]
        }
        return bytes.TrimRight(s, "\x00")
    }
    return bytes.Equal(trim(a), trim(b))
}
```
:::

> 🔧 **Навіщо це.** Класична причина «я ж змінив параметр, а апарат поводиться по-старому» — саме мовчазний загублений `PARAM_SET`: станція показала нове число у себе, але до борту воно не дійшло, а підтвердження ніхто не перевірив. Цикл «запис → чекай на `PARAM_VALUE` із цим значенням → повтори» прибирає цілий клас таких «привидів». Те саме стосується запису пачки параметрів із файлу `.param`: кожен рядок треба підтвердити окремо, інакше частина «залиплих» значень тихо лишиться старою.

## Підтверджено ≠ записано у флеш

Є й тонша пастка, уже на боці борту. `PARAM_VALUE` каже, що нове значення прийняте й діє **в оперативній пам'яті**, — але вкладення його в незалежну пам'ять (`AP_Param` поверх флешу) часто **відкладене**: прошивка не пише у флеш на кожен `PARAM_SET`, бо флеш має обмежений ресурс перезаписів, а під час налаштування значення сиплються пачками. Запис у флеш робиться згодом, малими порціями у фоні. Практичний наслідок: якщо **смикнути живлення відразу** після заливання великого `.param`, частина щойно підтверджених значень може не дожити до перезавантаження — вони ще лежали в черзі на запис. Тому правильний ритуал після масового запису — дати апарату кілька секунд спокою, а потім **перечитати** ключові параметри назад і звірити; якщо вони повернулися правильними після (за потреби) перезавантаження, значить, осіли у флеш. Це той самий принцип, що й усюди з відкладеним записом: підтвердження прийому й гарантія збереження — дві різні події, і покладатися можна лише на перевірене перечитуванням.

## Що з усього цього винести

Простота повідомлень MAVLink оманлива: чотири поля `PARAM_VALUE` — і весь обмін. Та надійним його роблять не самі повідомлення, а **дисципліна навколо них**: підрахунок за `param_count`/`param_index` робить помітними **втрати** при читанні; перевірка `PARAM_VALUE` після `PARAM_SET` робить надійним **запис**; байтова інтерпретація `param_value` береже **цілі** значення від мовчазного псування; а пам'ять про відсутній `\0` у 16-символьному імені рятує від виходу за межі. Кожна з цих дрібниць закриває конкретну тиху помилку — і саме тому станції, яким можна довіряти налаштування апарата, реалізують протокол так, а не «попросив і повірив».
