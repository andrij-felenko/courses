# 📋 Як надійно читати давач перешкод у коді: інверсія, дрижання, стробування EN

<preknowlist>
- [Придушення дрижання](topic:hw-digital/contact-debounce) — приймати новий стан лише коли він протримався достатньо довго; тут це рятує від тремтіння виходу компаратора на межі спрацювання.
- [Мікроконтролер: що всередині](topic:hw-arch/mcu-blocks) — процесор і піни вводу-виводу, `pinMode`/`digitalRead`/`digitalWrite`; на цьому тримається весь код.
- [Рівні «0» і «1»](topic:hw-digital/logic-levels-as-ranges) — що плата читає як HIGH/LOW; вихід давача активний **нулем**, і весь код будується навколо цього.
- [Період і переповнення лічильника](topic:hw-arch/timer-overflow) — беззнаковий `millis()` колись «перекрутиться» через нуль; віднімання `t − t0` це переживає, пряме порівняння — ні.
</preknowlist>

Плата вже прозвонена, три (чи чотири) дроти на місці, гвинтик дальності виставлено на око по індикаторному світлодіоду, і `digitalRead` уже повертає біт. Здавалося б, писати нема чого: `if (digitalRead(pin) == LOW) …` — і поїхали. Але щойно цей рядок потрапляє в реального робота, який повільно під'їжджає до стіни, він починає брехати десятками разів за секунду. Тому справжня прошивка давача перешкод — це не один `digitalRead`, а **обгортка**, що ховає три речі, на яких новачки обпікаються поспіль: інверсію виходу (щоб решта коду думала прямими словами «є перешкода = true»), тремтіння сигналу на порозі, і — окремо для KY-032 — необхідність періодично гасити несучу, інакше приймач осліпне сам собою. Зберемо цю обгортку від найпростішого до повного — це той чистий інтерфейс, на який спирається будь-яка логіка руху над давачем. Потрібне від контролера — мінімум: один цифровий вхід (краще з внутрішньою підтяжкою), лічильник мілісекунд і — для KY-032 — один цифровий вихід. Приклади нижче йдуть вкладками: Arduino (базово ATmega328P, 16 МГц) як найкоротший вхід, ESP-IDF і STM32 HAL — та сама логіка, лише своїм API.

## Задача: перетворити один тремтливий біт на надійну подію

Вихід FC-51 і KY-032 — цифровий і рівно один. На перший погляд читати його елементарно, і саме ця простота оманлива. Проблем рівно три, і кожну треба закрити в коді, бо жодна не лікується гвинтиком.

Перша — **інверсія**. Вихід активний нулем: спокій — це HIGH, а перешкода притягує лінію в LOW. Прочитати пін і думати, що одиниця — це «є перешкода» (`digitalRead(pin)` в Arduino, `gpio_get_level()` в ESP-IDF, `HAL_GPIO_ReadPin()` у STM32 — байдуже), — класична помилка, від якої робот об'їжджає порожнечу й в'їжджає в стіну. Обгортка мусить перевернути біт **один раз, у єдиному місці**, і назовні віддавати чесне `true = перешкода поруч`, щоб решта коду ніде не мусила пам'ятати про активний нуль.

Друга — **дрижання** (англ. *jitter*, *chatter*). Вихід давача — це вихід компаратора, а компаратор без гістерезису біля самого порога поводиться нервово. Коли перешкода рівно на межі виставленої дальності — робот повзе, кут поверхні змінюється, відбите світло топчеться коло порога, — вихід починає швидко клацати HIGH-LOW-HIGH десятки разів за секунду. Це та сама хвороба, що в механічної [кнопки з її дрижанням контактів](topic:hw-digital/contact-debounce), тільки джерело інше: не механіка, а сигнал, що застряг на порозі. Голий `digitalRead` побачить цю тремтливу мішанину як сотні окремих подій «з'явилось / зникло», і якщо робот реагує на кожну зміну — він смикається, а лічильник спрацювань бреше.

Третя стосується **тільки KY-032** і взагалі не схожа на перші дві. Її приймач HS0038 має всередині автоматичне регулювання підсилення (англ. *automatic gain control*, AGC), яке **навмисне глушить будь-який сигнал, що триває надто довго без пауз** — навіть правильні 38 кГц. Логіка виробника була проста: справжній пульт шле короткі пачки імпульсів із паузами, тож приймач вважає нескінченне рівне мерехтіння «фоном» і придушує його. У давачі перешкод діод світить безперервно — і без утручання приймач за секунду-дві «звикне» до власної несучої й перестане бачити відбите. Це підтверджено прямо: HS0038-подібний модуль **сам гасить безперервний сигнал будь-якої частоти, зокрема й 38 кГц**, тож несучу треба періодично уривати піном `EN`, і тримати `EN` у HIGH радять **не довше приблизно 2 мс** поспіль, а між увімкненнями давати короткий LOW. Це вже не «прочитати біт» — це керувати давачем у такт, і жоден приклад із трьох дротів про це не згадує.

```
що дає давач:           HIGH у спокої,  LOW коли перешкода   (активний нуль)
чого код мусить досягти: true  = перешкода поруч             (чесна подія)
                         + не смикатись на дрижанні порога
                         + (KY-032) не дати приймачеві осліпнути від власної несучої
```

> 🔧 **Навіщо це.** Різниця між голим «прочитав пін — і поїхали» (`digitalRead(pin) == LOW` чи що там за функція у вашому середовищі) і справжньою обгорткою — це різниця між демо на столі й роботом, що реально їздить. На столі перешкода або є, або нема, ти тримаєш долоню чітко — і голий `digitalRead` «працює». На підлозі перешкода приходить під кутом, на межі дальності, у русі; вихід дрижить, а KY-032 ще й сам себе засліплює, якщо його не стробувати. Обгортка коштує тридцять рядків, а економить години здивування «чому воно бачить стіни, яких нема, і не бачить тих, що є».

## Ідея: один клас ховає всю брудну правду

Домовмося про межу. Назовні давач має виглядати гранично просто: спитав `sensor.obstacle()` — отримав `true`/`false`, чесне, вже без інверсії й без дрижання. Уся брудна правда — перевернутий біт, таймер дрижання, стробування `EN` — живе **всередині** класу й ніколи не тече в код робота. Це і є сенс обгортки: код керма пише той, хто думає про повороти, а не про активний нуль.

Клас робимо однаковим для обох давачів, бо назовні вони віддають той самий інвертований біт; різниця — лише в тому, що KY-032 додатково має пін `EN`, який треба стробувати. Тому обгортка знає про `EN` необов'язково: передав його номер — клас сам стробує несучу й читає вихід у правильні моменти; не передав (FC-51 або KY-032 із заводським джампером на `EN`) — клас просто читає вихід із придушенням дрижання. Один клас, дві поведінки, вибір — за наявністю піна `EN`.

Придушення дрижання зробимо **не блокуючим**: жодного `delay`. Давач опитуємо в кожному оберті головного циклу (в Arduino це `loop()`, в ESP-IDF — задача опитування, у STM32 — `while (1)` або такт таймера), запам'ятовуємо сирий стан і **мітку часу** його останньої зміни; підтвердженим вважаємо той стан, що протримався незмінним довше за поріг `debounceMs`. Для механічної кнопки типовий поріг — близько 50 мс, але для робота, що їде, це задовго: 50 мс на швидкості 0.3 м/с — це 1.5 см «сліпоти» після кожної зміни. Тому для рефлексу об'їзду беруть менше, 5–15 мс: досить, щоб проковтнути тремтіння порога, і замало, щоб помітно запізнити реакцію. Поріг — параметр, а не константа, саме тому.

> Механізм придушення дрижання (чому неблокуючий таймер на `millis()` кращий за `delay`, і чому стан вважають зміненим лише після паузи стабільності) розібрано окремо — [придушення дрижання](topic:hw-digital/contact-debounce): та сама ідея, лише джерело тремтіння тут не механічне, а поріг компаратора.

## Крок 1: обгортка над FC-51 (три піни, лише інверсія й дрижання)

Почнемо з простішого давача — FC-51, у якого немає `EN`. Обгортці треба закрити дві проблеми: перевернути біт і придушити дрижання. Ось клас цілком, розібраний по деталях.

:::tabs
```arduino
#include <Arduino.h>

class IrObstacle {
public:
  // pin      — цифровий вхід, куди йде OUT давача
  // debounceMs — скільки стан має протриматись, щоб його прийняти (мс)
  // usePullup  — чи вмикати внутрішню підтяжку (лікує «плаваючу» лінію)
  IrObstacle(uint8_t pin, uint16_t debounceMs = 8, bool usePullup = true)
    : _pin(pin), _debounceMs(debounceMs), _usePullup(usePullup) {}

  void begin() {
    pinMode(_pin, _usePullup ? INPUT_PULLUP : INPUT);
    // початковий стан читаємо одразу, щоб не «клацнути» на старті
    _rawLast   = readRaw();
    _stable     = _rawLast;
    _changedAt = millis();
  }

  // Викликати часто (кожен loop). Оновлює підтверджений стан.
  void update() {
    bool raw = readRaw();
    if (raw != _rawLast) {          // сирий стан щойно смикнувся
      _rawLast   = raw;
      _changedAt = millis();        // перезапускаємо відлік стабільності
    }
    // прийняти новий стан лише коли він протримався досить довго
    if (raw != _stable && (millis() - _changedAt) >= _debounceMs) {
      _stable = raw;
    }
  }

  // Чесна подія: true = перешкода поруч (інверсію вже враховано).
  bool obstacle() const { return _stable; }

private:
  // Сирий біт → логічна «перешкода»: активний нуль, тож LOW = true.
  bool readRaw() const { return digitalRead(_pin) == LOW; }

  uint8_t  _pin;
  uint16_t _debounceMs;
  bool     _usePullup;
  bool     _rawLast   = false;
  bool     _stable     = false;
  uint32_t _changedAt = 0;
};
```
```esp-idf
#include "driver/gpio.h"
#include "esp_timer.h"

typedef struct {
    gpio_num_t pin;
    uint32_t   debounce_ms;   // скільки стан має протриматись, щоб його прийняти
    bool       raw_last, stable;
    int64_t    changed_at;    // мкс від старту (лічильник 64-бітний — не перекрутиться)
} ir_obstacle_t;

// Сирий біт → логічна «перешкода»: активний нуль, тож 0 = true.
static bool ir_read_raw(const ir_obstacle_t *s) {
    return gpio_get_level(s->pin) == 0;
}

esp_err_t ir_obstacle_begin(ir_obstacle_t *s, gpio_num_t pin,
                            uint32_t debounce_ms, bool use_pullup) {
    s->pin = pin;
    s->debounce_ms = debounce_ms;
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << pin,
        .mode         = GPIO_MODE_INPUT,
        // внутрішня підтяжка лікує «плаваючу» лінію
        .pull_up_en   = use_pullup ? GPIO_PULLUP_ENABLE : GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    esp_err_t err = gpio_config(&cfg);
    if (err != ESP_OK) return err;
    // початковий стан читаємо одразу, щоб не «клацнути» на старті
    s->raw_last = s->stable = ir_read_raw(s);
    s->changed_at = esp_timer_get_time();
    return ESP_OK;
}

// Викликати часто — із задачі опитування. Оновлює підтверджений стан.
void ir_obstacle_update(ir_obstacle_t *s) {
    bool    raw = ir_read_raw(s);
    int64_t now = esp_timer_get_time();
    if (raw != s->raw_last) {              // сирий стан щойно смикнувся
        s->raw_last   = raw;
        s->changed_at = now;               // перезапускаємо відлік стабільності
    }
    // прийняти новий стан лише коли він протримався досить довго
    if (raw != s->stable && (now - s->changed_at) >= (int64_t)s->debounce_ms * 1000)
        s->stable = raw;
}

// Чесна подія: true = перешкода поруч (інверсію вже враховано).
bool ir_obstacle(const ir_obstacle_t *s) { return s->stable; }
```
```stm32
#include "stm32f4xx_hal.h"
#include <stdbool.h>

typedef struct {
    GPIO_TypeDef *port;
    uint16_t      pin;
    uint16_t      debounce_ms;  // скільки стан має протриматись, щоб його прийняти
    bool          raw_last, stable;
    uint32_t      changed_at;   // мітка HAL_GetTick(), мс
} IrObstacle;

// Сирий біт → логічна «перешкода»: активний нуль, тож RESET = true.
static bool IrReadRaw(const IrObstacle *s) {
    return HAL_GPIO_ReadPin(s->port, s->pin) == GPIO_PIN_RESET;
}

// Такт порту (__HAL_RCC_GPIOx_CLK_ENABLE) має бути вже ввімкнений.
void IrObstacle_Begin(IrObstacle *s, GPIO_TypeDef *port, uint16_t pin,
                      uint16_t debounce_ms, bool usePullup) {
    s->port = port;  s->pin = pin;  s->debounce_ms = debounce_ms;
    GPIO_InitTypeDef gi = {0};
    gi.Pin  = pin;
    gi.Mode = GPIO_MODE_INPUT;
    // внутрішня підтяжка лікує «плаваючу» лінію
    gi.Pull = usePullup ? GPIO_PULLUP : GPIO_NOPULL;
    HAL_GPIO_Init(port, &gi);
    // початковий стан читаємо одразу, щоб не «клацнути» на старті
    s->raw_last = s->stable = IrReadRaw(s);
    s->changed_at = HAL_GetTick();
}

// Викликати часто (кожен оберт while(1) або з такту таймера).
void IrObstacle_Update(IrObstacle *s) {
    bool     raw = IrReadRaw(s);
    uint32_t now = HAL_GetTick();
    if (raw != s->raw_last) {              // сирий стан щойно смикнувся
        s->raw_last   = raw;
        s->changed_at = now;               // перезапускаємо відлік стабільності
    }
    // прийняти новий стан лише коли він протримався досить довго
    if (raw != s->stable && (now - s->changed_at) >= s->debounce_ms)
        s->stable = raw;
}

// Чесна подія: true = перешкода поруч (інверсію вже враховано).
bool IrObstacle_Obstacle(const IrObstacle *s) { return s->stable; }
```
:::

Розберемо, чому саме так, бо кожна дрібниця тут — від конкретних граблів.

`readRaw()` — **єдине** місце, де живе інверсія: `digitalRead(_pin) == LOW` (в ESP-IDF — `gpio_get_level(pin) == 0`, у STM32 HAL — `HAL_GPIO_ReadPin(...) == GPIO_PIN_RESET`) перетворює активний нуль давача на чесне `true = перешкода`. Більше ніде в усій програмі слово `LOW` щодо цього давача не з'явиться — і саме тому решта коду не мусить пам'ятати про інверсію. Це не косметика: коли за півроку повернешся до проєкту, ти дивитимешся на `sensor.obstacle()` і читатимеш його прямо, без розшифрування.

Дрижання придушено через дві змінні стану. `_rawLast` — останній сирий біт, `_changedAt` — коли він востаннє смикнувся. Щойно сирий стан змінився, ми не віримо йому одразу — ми **перезапускаємо годинник**. Прийняти новий стан у `_stable` дозволяємо лише тоді, коли від останнього смикання минуло `_debounceMs` без нових смикань, тобто сигнал **устоявся**. Поки вихід тремтить на порозі, `_changedAt` весь час оновлюється, поріг стабільності ніколи не набігає, і `_stable` спокійно тримає старе значення — робот не смикається. Це те саме, що робить порядна бібліотека дебаунсу кнопок, тільки написане прямо, щоб було видно кожну шестерню.

Ключове й непомітне: `millis() - _changedAt`. Ми **віднімаємо** мітки часу, а не порівнюємо `millis() >= _changedAt + _debounceMs`. Це навмисно. Лічильник мілісекунд усюди беззнаковий і 32-бітний — `millis()` в Arduino, `HAL_GetTick()` у STM32 HAL, тік FreeRTOS в ESP-IDF, — тож він переповнюється (перекручується через нуль) приблизно раз на 49.7 дня; віднімання беззнакових це переживає коректно навіть у мить перекруту, а додавання до мітки — ні, там вилізе хибне спрацювання. (Де є 64-бітний лічильник мікросекунд — як `esp_timer_get_time()` в ESP-IDF — проблеми просто немає, і код нижче користується саме ним.) Дрібниця, що на столі ніколи не проявиться, а в пристрої, який працює тижнями, вилізе раз — і це рівно [період і переповнення лічильника](topic:hw-arch/timer-overflow).

Використання — гранично коротке, і вся суть у тому, що код робота не бачить жодної з трьох проблем:

:::tabs
```arduino
IrObstacle front(2);        // OUT давача на D2, дебаунс 8 мс за замовчуванням

void setup() {
  Serial.begin(9600);
  front.begin();
}

void loop() {
  front.update();                     // опитати давач (неблокуюче)
  if (front.obstacle())
    Serial.println("ПЕРЕШКОДА");
  else
    Serial.println("вільно");
  // тут може бути будь-яка інша робота — update() не блокує
}
```
```esp-idf
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char   *TAG = "ir";
static ir_obstacle_t front;   // OUT давача на GPIO4, дебаунс 8 мс

static void ir_task(void *arg) {
    for (;;) {
        ir_obstacle_update(&front);              // опитати давач (неблокуюче)
        ESP_LOGI(TAG, "%s", ir_obstacle(&front) ? "ПЕРЕШКОДА" : "вільно");
        vTaskDelay(pdMS_TO_TICKS(2));            // крок опитування
    }
}

void app_main(void) {
    ESP_ERROR_CHECK(ir_obstacle_begin(&front, GPIO_NUM_4, 8, true));
    xTaskCreate(ir_task, "ir", 2048, NULL, 5, NULL);
    // інші задачі живуть паралельно — опитування їх не блокує
}
```
```stm32
static IrObstacle front;

int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    IrObstacle_Begin(&front, GPIOA, GPIO_PIN_0, 8, true);  // OUT давача на PA0

    while (1) {
        IrObstacle_Update(&front);            // опитати давач (неблокуюче)
        if (IrObstacle_Obstacle(&front))
            printf("ПЕРЕШКОДА\r\n");          // printf перенаправлено на UART
        else
            printf("вільно\r\n");
        // тут може бути будь-яка інша робота — Update() не блокує
    }
}
```
:::

> 🔧 **Навіщо це.** Помітьте, що `loop()` **нічого не знає** про активний нуль, про дрижання, про таймери. Він питає `obstacle()` — і отримує правду. Уся ця чистота коштувала одного класу, і саме вона робить різницю, коли давачів стане два, три чи чотири: логіка керма пишеться на чесних `true`/`false`, а не на мішанині `digitalRead(...) == LOW` з таймерами навперемішку. Обгортка — це не «гарний стиль заради стилю», це те, що дає скласти складнішу поведінку без помилок.

## Крок 2: KY-032 і стробування EN — годуємо AGC паузами

Тепер найтонше місце всієї теми, якого немає у FC-51. Якщо в KY-032 зняти заводський джампер із `EN` і взяти керування на себе, доведеться робити те, що на перший погляд суперечить здоровому глузду: **періодично вимикати давач, щоб він краще бачив**.

Причина — в тому самому AGC приймача HS0038. Він створений ловити пульти, а пульт шле короткі пачки по десятку-сотні періодів 38 кГц із паузами між ними; тривалий безперервний сигнал приймач вважає перешкодою-фоном і поступово **приглушує його підсилення до нуля** — байдуже, чи це паразитне ІЧ, чи власна несуча давача. Тому якщо тримати `EN` у HIGH завжди (несуча біжить безперервно), приймач за одну-дві секунди «втомиться» й перестане бачити відбите: давач наче живий, індикатор живлення горить, а перешкоди він більше не помічає. Лікування — **уривати несучу**: тримати `EN` у HIGH короткими вікнами й між ними скидати в LOW, щоб AGC встиг «розслабитись». Практична межа з опису самого модуля: `EN` не має лишатися в HIGH **довше ніж приблизно 2 мс** поспіль, а перед наступним HIGH треба короткий LOW.

Як `EN` узагалі вмикає давач — варто знати, бо це пояснює, чому LOW його справді гасить. Знятий джампер лишає вхід `RESET` (ніжка 4) генератора NE555 притягнутим до землі через резистор-підтяжку (близько 22 кОм) — а поки NE555 у скиданні, він **не коливається**, несучої нема. Подаєш на `EN` HIGH — знімаєш скидання, генератор оживає, діод починає мерехтіти на 38 кГц. Опускаєш `EN` у LOW — знову скидання, несуча гасне. Тобто `EN` — це вимикач генератора, а не окремий «сплячий режим»: керуючи ним, ти буквально вмикаєш і вимикаєш 38-кГц блимання діода.

Звідси й спосіб читати давач правильно. Опитувати вихід треба **наприкінці** вікна, поки несуча ще йшла, — саме тоді приймач встиг відреагувати на відбите. Схема одного циклу така:

```
1. EN → HIGH               (пускаємо несучу)
2. чекаємо коротке вікно    (≈1 мс, ≤2 мс — щоб AGC не встиг придушити)
3. читаємо OUT              (у цей момент відповідь дійсна)
4. EN → LOW                 (гасимо несучу, даємо AGC розслабитись)
5. коротка пауза            (≈1 мс) — і знову з п.1
```

Розширимо обгортку так, щоб вона робила це **сама**, лишаючись неблокуючою: жодних затримок-заглушок, усе на мітках часу вільного лічильника. Клас тепер має необов'язковий пін `EN` і всередині крутить малесеньку машину станів «увімкнув → почекав → прочитав → вимкнув → почекав».

:::tabs
```arduino
class IrObstacleEN {
public:
  // pinOut — вихід OUT; pinEN — пін EN (0xFF = немає, поведінка як FC-51)
  IrObstacleEN(uint8_t pinOut, uint8_t pinEN = 0xFF,
               uint16_t debounceMs = 8)
    : _pinOut(pinOut), _pinEN(pinEN), _debounceMs(debounceMs) {}

  void begin() {
    pinMode(_pinOut, INPUT_PULLUP);
    if (hasEN()) {
      pinMode(_pinEN, OUTPUT);
      digitalWrite(_pinEN, LOW);       // старт із вимкненою несучою
    }
    _rawLast = _stable = readRaw();
    _changedAt = _phaseAt = millis();
    _enHigh = false;
  }

  void update() {
    if (hasEN()) strobe();             // ведемо цикл EN, читаємо у слушну мить
    else         debounceOnly(readRaw());
  }

  bool obstacle() const { return _stable; }

private:
  static const uint16_t EN_ON_MS  = 1;   // вікно несучої (≤2 мс!)
  static const uint16_t EN_OFF_MS = 1;   // пауза для розслаблення AGC

  bool hasEN() const { return _pinEN != 0xFF; }
  bool readRaw() const { return digitalRead(_pinOut) == LOW; }

  // Неблокуюча машина станів для EN.
  void strobe() {
    uint32_t now = millis();
    if (_enHigh) {
      if (now - _phaseAt >= EN_ON_MS) {  // вікно скінчилось
        debounceOnly(readRaw());         // читаємо ПОКИ несуча ще була
        digitalWrite(_pinEN, LOW);       // гасимо несучу
        _enHigh = false;
        _phaseAt = now;
      }
    } else {
      if (now - _phaseAt >= EN_OFF_MS) { // пауза скінчилась
        digitalWrite(_pinEN, HIGH);      // пускаємо несучу знову
        _enHigh = true;
        _phaseAt = now;
      }
    }
  }

  // Придушення дрижання — те саме, що у FC-51.
  void debounceOnly(bool raw) {
    uint32_t now = millis();
    if (raw != _rawLast) { _rawLast = raw; _changedAt = now; }
    if (raw != _stable && (now - _changedAt) >= _debounceMs) _stable = raw;
  }

  uint8_t  _pinOut, _pinEN;
  uint16_t _debounceMs;
  bool     _rawLast = false, _stable = false, _enHigh = false;
  uint32_t _changedAt = 0, _phaseAt = 0;
};
```
```esp-idf
#include "driver/gpio.h"
#include "esp_timer.h"

#define EN_ON_US   1000   // вікно несучої (≤2 мс!)
#define EN_OFF_US  1000   // пауза для розслаблення AGC

typedef struct {
    gpio_num_t out, en;       // en = GPIO_NUM_NC → піна нема, поведінка як FC-51
    uint32_t   debounce_ms;
    bool       raw_last, stable, en_high;
    int64_t    changed_at, phase_at;
} ir_en_t;

static bool has_en(const ir_en_t *s)    { return s->en != GPIO_NUM_NC; }
static bool en_read_raw(const ir_en_t *s) { return gpio_get_level(s->out) == 0; }

static gpio_config_t pin_cfg(gpio_num_t p, gpio_mode_t mode, gpio_pullup_t pu) {
    gpio_config_t c = { .pin_bit_mask = 1ULL << p, .mode = mode, .pull_up_en = pu,
                        .pull_down_en = GPIO_PULLDOWN_DISABLE,
                        .intr_type = GPIO_INTR_DISABLE };
    return c;
}

esp_err_t ir_en_begin(ir_en_t *s, gpio_num_t out, gpio_num_t en, uint32_t debounce_ms) {
    s->out = out;  s->en = en;  s->debounce_ms = debounce_ms;
    gpio_config_t in_cfg = pin_cfg(out, GPIO_MODE_INPUT, GPIO_PULLUP_ENABLE);
    ESP_ERROR_CHECK(gpio_config(&in_cfg));
    if (has_en(s)) {
        gpio_config_t en_cfg = pin_cfg(en, GPIO_MODE_OUTPUT, GPIO_PULLUP_DISABLE);
        ESP_ERROR_CHECK(gpio_config(&en_cfg));
        gpio_set_level(en, 0);             // старт із вимкненою несучою
    }
    s->raw_last = s->stable = en_read_raw(s);
    s->changed_at = s->phase_at = esp_timer_get_time();
    s->en_high = false;
    return ESP_OK;
}

// Придушення дрижання — те саме, що без EN.
static void debounce_only(ir_en_t *s, bool raw) {
    int64_t now = esp_timer_get_time();
    if (raw != s->raw_last) { s->raw_last = raw; s->changed_at = now; }
    if (raw != s->stable && (now - s->changed_at) >= (int64_t)s->debounce_ms * 1000)
        s->stable = raw;
}

// Неблокуюча машина станів для EN.
void ir_en_update(ir_en_t *s) {
    if (!has_en(s)) { debounce_only(s, en_read_raw(s)); return; }
    int64_t now = esp_timer_get_time();
    if (s->en_high) {
        if (now - s->phase_at >= EN_ON_US) {      // вікно скінчилось
            debounce_only(s, en_read_raw(s));     // читаємо ПОКИ несуча ще була
            gpio_set_level(s->en, 0);             // гасимо несучу
            s->en_high = false;  s->phase_at = now;
        }
    } else {
        if (now - s->phase_at >= EN_OFF_US) {     // пауза скінчилась
            gpio_set_level(s->en, 1);             // пускаємо несучу знову
            s->en_high = true;   s->phase_at = now;
        }
    }
}

bool ir_en_obstacle(const ir_en_t *s) { return s->stable; }
```
```stm32
#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define EN_ON_MS   1u   // вікно несучої (≤2 мс!)
#define EN_OFF_MS  1u   // пауза для розслаблення AGC

typedef struct {
    GPIO_TypeDef *outPort;  uint16_t outPin;
    GPIO_TypeDef *enPort;   uint16_t enPin;   // enPort = NULL → піна EN нема
    uint16_t      debounce_ms;
    bool          raw_last, stable, en_high;
    uint32_t      changed_at, phase_at;
} IrObstacleEN;

static bool HasEN(const IrObstacleEN *s)   { return s->enPort != NULL; }
static bool ReadRaw(const IrObstacleEN *s) {
    return HAL_GPIO_ReadPin(s->outPort, s->outPin) == GPIO_PIN_RESET;
}

// Такти обох портів (__HAL_RCC_GPIOx_CLK_ENABLE) мають бути ввімкнені.
void IrObstacleEN_Begin(IrObstacleEN *s, GPIO_TypeDef *outPort, uint16_t outPin,
                        GPIO_TypeDef *enPort, uint16_t enPin, uint16_t debounce_ms) {
    s->outPort = outPort;  s->outPin = outPin;
    s->enPort  = enPort;   s->enPin  = enPin;
    s->debounce_ms = debounce_ms;

    GPIO_InitTypeDef gi = {0};
    gi.Pin = outPin;  gi.Mode = GPIO_MODE_INPUT;  gi.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(outPort, &gi);
    if (HasEN(s)) {
        GPIO_InitTypeDef go = {0};
        go.Pin   = enPin;
        go.Mode  = GPIO_MODE_OUTPUT_PP;
        go.Pull  = GPIO_NOPULL;
        go.Speed = GPIO_SPEED_FREQ_LOW;
        HAL_GPIO_Init(enPort, &go);
        HAL_GPIO_WritePin(enPort, enPin, GPIO_PIN_RESET);  // старт без несучої
    }
    s->raw_last = s->stable = ReadRaw(s);
    s->changed_at = s->phase_at = HAL_GetTick();
    s->en_high = false;
}

// Придушення дрижання — те саме, що без EN.
static void DebounceOnly(IrObstacleEN *s, bool raw) {
    uint32_t now = HAL_GetTick();
    if (raw != s->raw_last) { s->raw_last = raw; s->changed_at = now; }
    if (raw != s->stable && (now - s->changed_at) >= s->debounce_ms) s->stable = raw;
}

// Неблокуюча машина станів для EN.
void IrObstacleEN_Update(IrObstacleEN *s) {
    if (!HasEN(s)) { DebounceOnly(s, ReadRaw(s)); return; }
    uint32_t now = HAL_GetTick();
    if (s->en_high) {
        if (now - s->phase_at >= EN_ON_MS) {                          // вікно скінчилось
            DebounceOnly(s, ReadRaw(s));                              // читаємо ПОКИ несуча ще була
            HAL_GPIO_WritePin(s->enPort, s->enPin, GPIO_PIN_RESET);   // гасимо несучу
            s->en_high = false;  s->phase_at = now;
        }
    } else {
        if (now - s->phase_at >= EN_OFF_MS) {                         // пауза скінчилась
            HAL_GPIO_WritePin(s->enPort, s->enPin, GPIO_PIN_SET);     // пускаємо несучу
            s->en_high = true;   s->phase_at = now;
        }
    }
}

bool IrObstacleEN_Obstacle(const IrObstacleEN *s) { return s->stable; }
```
:::

Тут важить порядок дій усередині `strobe()`. Ми читаємо `OUT` **до** того, як опустити `EN` у LOW, — тобто поки несуча ще йшла й відповідь приймача ще дійсна; опустиш `EN` раніше, читатимеш давач із уже згаслою несучою й отримаєш «вільно» завжди. Вікно `EN_ON_MS = 1` мс тримаємо свідомо коротшим за стелю ~2 мс, із запасом: лічильник мілісекунд має роздільність рівно 1 мс, тож коротшого вікна ним не задати, а 1 мс — рівно в безпечній зоні (де потрібна дрібніша сітка, беруть мікросекундний таймер, як `esp_timer_get_time()`). Пауза `EN_OFF_MS = 1` мс дає AGC розслабитись; цикл виходить приблизно 2 мс на повний оберт, тобто давач опитується сотні разів за секунду — для рефлексу об'їзду цього з головою.

> 🔧 **Навіщо це.** Це рідкісний випадок, коли «правильно» суперечить інтуїції: щоб KY-032 надійно бачив, його треба **періодично гасити**. Не знаючи цього, люди тримають `EN` на HIGH джампером «щоб працювало постійно» — і скаржаться, що давач за пару секунд сліпне на нерухому перешкоду. Джампер годиться лише для випадків, де перешкоди **проїжджають** повз (тоді AGC не встигає придушити рухому картинку); а для нерухомої стіни перед роботом, що завмер, потрібне саме стробування. Тому й `EN` виведено окремим піном: це не «вимикач для економії», а орган керування, без якого давач не показує повної чутливості. Якщо мороки з таймінгом не хочеш — лишай джампер і май на увазі обмеження; хочеш максимальної надійності — стробуй.

Для FC-51 усе теж працює цим самим класом: створи його **без** піна `EN` (в Arduino це `IrObstacleEN front(2);`, в ESP-IDF — `GPIO_NUM_NC`, у STM32 — `NULL` замість порту `EN`), і оновлення піде гілкою `debounceOnly` — та сама обгортка, лише без стробування. Один клас накриває обидва давачі.

> Уся ця обгортка існує заради однієї мети — дати рухові чесні біти. Як із пари таких давачів по кутах візка зібрати робота, що сам об'їжджає стіни, показано окремо: [двосенсорний робот-обхідник](topic:cat-hw-sensors/ir-obstacle/api-ir-obstacle.md) — проста кермова машина станів на двох `obstacle()`.
