# ⚙️ Проєкт: бібліотека для KY-026 і робот, що бачить вогонь по мерехтінню

Голий давач уже прозвонено: чотири піни, цифровий вихід дає біт, аналоговий — число з АЦП. Здавалося б, писати нема чого. Але між «прочитав пін» і «пристрій надійно відрізняє свічку від сонця у вікні» лежить рівно та частина роботи, заради якої взагалі беруть мікроконтролер, а не просто дзвінок із фотоелементом. Тут ми пройдемо цей проміжок до кінця: спершу зберемо невелику **бібліотеку-обгортку**, яка ховає інверсію DO та дрижання порогу за чесним інтерфейсом; потім — головне — навчимо код **впізнавати полумʼя за мерехтінням**, а не за яскравістю, і цим відсіємо сонце й лампу; і насамкінець складемо з двох давачів **пожежного робота**, що сам наводиться на найяскравіший вогонь. Уся логіка спирається лише на те, що є в будь-якому мікроконтролері — вхідний вивід, канал АЦП, лічильник часу, — тому кожен приклад іде вкладками: **Arduino** (ATmega328P, 16 МГц), **ESP-IDF** (той самий [ESP32](topic:cat-hw-boards/esp32-family), але рідним API) і **STM32 HAL**. Це не псевдокод, а справжні імена типів, виводів і функцій — той код, що компілюється й заливається.

## Задача: чого не вистачає «сирому» пінові

Пряме читання цифрового виводу — `digitalRead(PIN_DO)` в Arduino, `gpio_get_level()` в ESP-IDF, `HAL_GPIO_ReadPin()` на STM32 — працює рівно доти, доки нічого не йде не так. А не так іде постійно, і завжди по тих самих трьох причинах.

**Інверсія.** На більшості модулів KY-026 цифровий вихід інвертований: у спокої DO тримає HIGH, а вогонь кидає його в LOW. Отже, «є вогонь» — це `== LOW`, а не `== HIGH`, і половина прикладів у мережі мовчки помиляється боком. Хочеться написати логіку один раз так, щоб інверсія була **одним прапорцем** у налаштуванні, а не розсипалася по всьому коду знаком порівняння.

**Дрижання (англ. *bouncing*, «дрижання контакту»).** Коли яскравість жару топчеться рівно біля порога — свічка на межі дальності, легкий протяг колише полумʼя — вихід компаратора LM393 починає **швидко перемикатися** туди-сюди. Це не електрична вада, а неминучий наслідок порівняння шумного сигналу з чіткою межею: сигнал перетинає поріг десятки разів за секунду. Голе читання виводу побачить цю тремтливу мішанину, і подія «вогонь зʼявився» вистрелить сотнями хибних спрацювань за секунду. Лікування те саме, що й для механічної кнопки, — [придушення дрижання](topic:hw-digital/contact-debounce): вважати стан зміненим лише тоді, коли він **протримався** новим достатньо довго.

**Залежність AO від живлення.** Аналоговий вихід дає напругу **відносно напруги живлення** й читається [АЦП](topic:hw-analog/adc) теж відносно опорної напруги плати. Те саме полумʼя дасть на 5-вольтовому Arduino одне число, а на 3.3-вольтовому ESP32 — зовсім інше; те саме число з АЦП при різній опорній напрузі означає різну реальну напругу. Тому «поріг 300» ніколи не буває абсолютним — його треба **калібрувати під сцену й під плату**, а код має це полегшувати, а не приховувати.

**І головне — сонце.** Давач бачить [ближній інфрачервоний](topic:ph-electromagnetism/em-spectrum), а не вогонь. Пряме сонце крізь вікно, галогенова лампа, гаряча спіраль обігрівача світять у тій самій смузі 760–1100 нм не гірше за свічку й спокійно перекинуть будь-який поріг **без жодного полумʼя**. Жоден рівень сигналу не відрізнить вогонь від сонця, бо для фототранзистора вони однакові. Порогом цю пастку не закрити в принципі — потрібен інший підхід, і саме він тут головна ідея.

## Ідея №1: обгортка, що ховає інверсію та дрижання

Почнімо з простого — з бібліотеки, яка робить два перші клопоти невидимими. Задум мінімальний: клас `KY026`, якому при створенні кажуть номери пінів і **чи інвертований DO**, а він назовні дає чесні методи «є вогонь?» (уже з урахуванням інверсії й дрижання) та «яка сила жару?» (сире число АЦП). Ніякої магії — просто одне місце, де зібрано всі домовленості про цей конкретний давач.

:::tabs
```arduino
// ── KY026.h ──────────────────────────────────────────────────────────────
#pragma once
#include <Arduino.h>

class KY026 {
public:
  // pinDO / pinAO — піни; invertedDO=true, якщо спокій=HIGH, вогонь=LOW
  // (як на більшості модулів). debounceMs — скільки стан має протриматись.
  KY026(uint8_t pinDO, uint8_t pinAO, bool invertedDO = true,
        uint16_t debounceMs = 40)
    : _pinDO(pinDO), _pinAO(pinAO), _inverted(invertedDO),
      _debounceMs(debounceMs) {}

  void begin() {
    pinMode(_pinDO, INPUT);
    // AO — аналоговий, режим задавати не треба; поріг DO задає гвинтик на платі
    _stable   = rawFlame();      // початковий стан — той, що зараз
    _lastRaw  = _stable;
    _changedAt = millis();
  }

  // Сирий біт «поріг перейдено», уже розвернутий під інверсію.
  // true == є вогонь (за гвинтиком на платі), без придушення дрижання.
  bool rawFlame() const {
    int v = digitalRead(_pinDO);
    return _inverted ? (v == LOW) : (v == HIGH);
  }

  // Головний метод: викликай часто (у loop). Повертає СТАБІЛЬНИЙ стан
  // «є вогонь», що змінюється лише після витримки debounceMs.
  bool update() {
    bool now = rawFlame();
    if (now != _lastRaw) {          // сире значення сіпнулося — почни відлік
      _lastRaw   = now;
      _changedAt = millis();
    } else if (now != _stable &&
               (millis() - _changedAt) >= _debounceMs) {
      _stable = now;                // новий стан протримався — приймаємо
    }
    return _stable;
  }

  bool flame() const { return _stable; }   // останній стабільний стан

  int  strength() const { return analogRead(_pinAO); }  // сира сила жару

private:
  uint8_t  _pinDO, _pinAO;
  bool     _inverted;
  uint16_t _debounceMs;
  bool     _stable = false, _lastRaw = false;
  uint32_t _changedAt = 0;
};
```
```esp-idf
// ── ky026.h ── ESP-IDF: DO — звичайний GPIO, AO — канал АЦП, час — esp_timer
#pragma once
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_timer.h"

typedef struct {
    gpio_num_t    pin_do;
    adc_channel_t ch_ao;        // AO живе на КАНАЛІ АЦП, а не просто «на піні»
    bool          inverted;     // спокій=1, вогонь=0 — як на більшості модулів
    uint32_t      debounce_us;  // витримка стану, мікросекунди
    adc_oneshot_unit_handle_t adc;
    bool     stable, last_raw;
    int64_t  changed_at;
} ky026_t;

// Сирий біт «поріг перейдено», уже розвернутий під інверсію.
static inline bool ky026_raw(const ky026_t *s) {
    int v = gpio_get_level(s->pin_do);
    return s->inverted ? (v == 0) : (v == 1);
}

static inline void ky026_begin(ky026_t *s) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << s->pin_do,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,   // модуль сам тягне лінію
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));

    adc_oneshot_chan_cfg_t ch = {
        .atten    = ADC_ATTEN_DB_12,           // послаблення: міряти майже до 3.3 В
        .bitwidth = ADC_BITWIDTH_DEFAULT,      // 12 біт → 0..4095
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s->adc, s->ch_ao, &ch));

    s->stable = s->last_raw = ky026_raw(s);
    s->changed_at = esp_timer_get_time();      // мікросекунди від старту
}

// Кликати часто. Той самий секундомір, лише годинник у мікросекундах.
static inline bool ky026_update(ky026_t *s) {
    bool now = ky026_raw(s);
    int64_t t = esp_timer_get_time();
    if (now != s->last_raw) { s->last_raw = now; s->changed_at = t; }
    else if (now != s->stable && (t - s->changed_at) >= s->debounce_us) s->stable = now;
    return s->stable;
}

static inline int ky026_strength(const ky026_t *s) {
    int raw = 0;
    adc_oneshot_read(s->adc, s->ch_ao, &raw);  // сира сила жару, 0..4095
    return raw;
}
```
```stm32
/* ── ky026.h ── STM32 HAL: DO — GPIO-вхід, AO — канал ADC, час — HAL_GetTick */
#pragma once
#include "stm32f4xx_hal.h"
#include <stdbool.h>

typedef struct {
    GPIO_TypeDef      *port_do;   /* напр. GPIOA */
    uint16_t           pin_do;    /* напр. GPIO_PIN_2 */
    ADC_HandleTypeDef *hadc;      /* АЦП, зведений CubeMX на вивід AO */
    bool      inverted;           /* спокій=SET, вогонь=RESET */
    uint32_t  debounce_ms;
    bool      stable, last_raw;
    uint32_t  changed_at;
} ky026_t;

/* Сирий біт «поріг перейдено», уже розвернутий під інверсію. */
static inline bool ky026_raw(const ky026_t *s) {
    GPIO_PinState v = HAL_GPIO_ReadPin(s->port_do, s->pin_do);
    return s->inverted ? (v == GPIO_PIN_RESET) : (v == GPIO_PIN_SET);
}

static inline void ky026_begin(ky026_t *s) {
    /* Такт порту й режим виводу (GPIO_MODE_INPUT, GPIO_NOPULL) уже задано
       в MX_GPIO_Init(); поріг DO задає гвинтик на платі, а не код. */
    s->stable = s->last_raw = ky026_raw(s);
    s->changed_at = HAL_GetTick();             /* мілісекунди від старту */
}

/* Кликати часто з головного циклу — той самий секундомір придушення дрижання. */
static inline bool ky026_update(ky026_t *s) {
    bool now = ky026_raw(s);
    uint32_t t = HAL_GetTick();
    if (now != s->last_raw) { s->last_raw = now; s->changed_at = t; }
    else if (now != s->stable && (t - s->changed_at) >= s->debounce_ms) s->stable = now;
    return s->stable;
}

static inline int ky026_strength(ky026_t *s) {
    HAL_ADC_Start(s->hadc);
    HAL_ADC_PollForConversion(s->hadc, 10);    /* 10 мс стелі — з головою */
    int raw = (int)HAL_ADC_GetValue(s->hadc);  /* сира сила жару, 0..4095 */
    HAL_ADC_Stop(s->hadc);
    return raw;
}
```
:::

Придивись до `update()` — уся суть придушення дрижання в тих семи рядках, і вона варта того, щоб її зрозуміти, а не просто скопіювати. Ми тримаємо два стани: `_lastRaw` — що пін показав **щойно**, і `_stable` — стан, у який ми **повірили**. Коли сире значення міняється, ми не віримо йому одразу, а лише **запускаємо секундомір** (`_changedAt`). Якщо наступні читання показують те саме нове значення й воно **протрималося** довше за `debounceMs` — тоді, і лише тоді, ми переносимо його в `_stable`. Одна коротка сіпка (сигнал стрибнув через поріг і одразу назад) скидає секундомір і так і не доживає до того, щоб її прийняли. Тремтливий рій перемикань на межі порога перетворюється на один чистий перехід.

> 🔧 **Навіщо це.** `debounceMs` — це прямий обмін між **швидкістю** й **спокоєм**. Малі 5–10 мс — реакція майже миттєва, але тремтіння на межі просочується. Великі 100–200 мс — жодного хибного клацання, але й на справжній вогонь пристрій відгукнеться з помітною затримкою. Для тривоги над плитою бери більше (спокій дорожчий), для робота, що кермує на вогонь, — менше (важлива швидкість). Тримаючи це числом у конструкторі, ти крутиш баланс під задачу, не чіпаючи логіку.

Користуватися нею — три рядки, і вся негарна правда про інверсію лишається всередині:

:::tabs
```arduino
// DO на D2, AO на A0; DO інвертований (звірено по індикаторному світлодіоду).
KY026 sensor(2, A0, /*invertedDO=*/true, /*debounceMs=*/40);

void setup() {
  Serial.begin(9600);
  sensor.begin();
}

void loop() {
  bool flame = sensor.update();          // стабільний стан, без дрижання
  int  ir    = sensor.strength();        // сира сила жару, якщо треба
  Serial.print(flame ? "ВОГОНЬ  " : "спокій  ");
  Serial.println(ir);
  delay(10);                             // update() любить, щоб її кликали часто
}
```
```esp-idf
// DO на GPIO4, AO на GPIO34 (ADC1_CH6 — блок, дружній до Wi-Fi).
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "ky026";

static ky026_t sensor = {
    .pin_do = GPIO_NUM_4, .ch_ao = ADC_CHANNEL_6,
    .inverted = true, .debounce_us = 40 * 1000,
};

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &sensor.adc));
    ky026_begin(&sensor);

    for (;;) {                                  // це і є loop(), лише свій власний
        bool flame = ky026_update(&sensor);     // стабільний стан, без дрижання
        int  ir    = ky026_strength(&sensor);   // сира сила жару, якщо треба
        ESP_LOGI(TAG, "%s  %d", flame ? "ВОГОНЬ" : "спокій", ir);
        vTaskDelay(pdMS_TO_TICKS(10));          // update() любить часті виклики
    }
}
```
```stm32
/* DO на PA2, AO на PA0 (ADC1_IN0); обидва виводи звів CubeMX. */
extern ADC_HandleTypeDef hadc1;

static ky026_t sensor = {
    .port_do = GPIOA, .pin_do = GPIO_PIN_2, .hadc = &hadc1,
    .inverted = true, .debounce_ms = 40,
};

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();                        /* PA2 — вхід DO */
    MX_ADC1_Init();                        /* PA0 — аналоговий AO */
    ky026_begin(&sensor);

    while (1) {
        bool flame = ky026_update(&sensor); /* стабільний стан, без дрижання */
        int  ir    = ky026_strength(&sensor);
        printf("%s  %d\r\n", flame ? "ВОГОНЬ" : "спокій", ir);  /* через UART */
        HAL_Delay(10);                     /* update() любить часті виклики */
    }
}
```
:::

Зауваж дрібницю, що рятує нерви: `update()` треба кликати **часто й рівномірно**. Вона не спить сама — вона лише дивиться на годинник (`millis()`, `esp_timer_get_time()`, `HAL_GetTick()` — назва різна, суть одна) при кожному виклику. Якщо між викликами вставити блокувальну затримку на пів секунди, придушення дрижання загрубне до кроку в піваунди. Тому у справжній програмі уникай довгих затримок у головному циклі; краще міряй час сам і не блокуй програму.

## Ідея №2: розпізнати вогонь за мерехтінням

Тепер — головне, те, заради чого варто було затівати код. Ми не можемо порогом відрізнити свічку від сонця, бо **за яскравістю** вони для давача однакові. Але є одна річ, якою полумʼя разюче відрізняється від будь-якого рівного джерела, і давач її бачить: **вогонь тремтить**.

Це не поетичний образ, а фізика, яку виміряли. Полумʼя — це висхідний потік розжарених газів; тепле легше за холодне, воно спливає, на його місце знизу підсмоктується холодне повітря, і на межі двох потоків із різною швидкістю народжується нестійкість, що скручує газ у вихори-кільця. Ці вихори зривають полумʼя вгору порціями — і воно **пульсує**. Для свічки й невеликого дифузійного полумʼя частота цих пульсацій лежить у вузькій, добре відомій смузі — **близько 10–12 Гц** (лабораторні виміри дають 10–20 Гц для малих полумʼїв; великі пожежі коливаються повільніше). Причина — саме сила тяжіння: без неї гарячий газ не спливав би, і полумʼя у невагомості горить рівною кулею без мерехтіння. Тому пульсація на десятку герц — це майже **підпис відкритого полумʼя в земній тяжкості**.

> Звідки саме «10–12 Гц» і чому це підпис вогню — з досліджень коливань дифузійного полумʼя: нестійкість висхідного плавучого потоку (модифікована нестійкість Кельвіна-Гельмгольца) породжує тороїдальні вихори, що зривають полумʼя з частотою, заданою плавучістю; для свічки вона стабільно тримається біля 10 Гц. Це доказовий, багатократно повторений експериментальний факт, а не оцінка. *(Frequency and Phase Characteristics of Candle Flame Oscillation, Scientific Reports, 2019; Flickering candle flames and their collective behavior, Scientific Reports, 2020.)*

А тепер порівняй: **сонце світить рівно**. Його ІЧ-потік сталий; лампа розжарення — теж (нитка гріється й остигає надто повільно, щоб мерехтіти на десятку герц); екран і світлодіодна лампа холодні й в ІЧ майже не світять. Виходить чіткий критерій, який не плутається там, де поріг безпорадний:

```
рівний сильний ІЧ           → сонце / лампа / обігрівач   → НЕ тривога
ІЧ, що пульсує на ~2–20 Гц   → полумʼя                      → ТРИВОГА
```

Тобто ми маємо шукати в аналоговому сигналі AO не рівень, а **змінну складову у смузі кількох-десятків герц**. Це, по суті, [смуговий фільтр](topic:com-signal/band-filters) плюс вимір амплітуди на виході. Робити повне перетворення Фур'є ([ДПФ](topic:com-signal/dft)) на маленькому мікроконтролері надмірно; для одного питання «чи є пульсація в потрібній смузі» вистачить набагато дешевшого прийому — **рахувати перетини середнього рівня**.

### Дешевий детектор мерехтіння: перетини середнього

Ідея проста до нахабства. Швидко-швидко семплюємо AO (скажімо, 200 разів на секунду). Тримаємо **повільне середнє** сигналу — воно йде за загальним рівнем ІЧ (і за сонцем, і за середньою яскравістю полумʼя). Тоді дивимось, **як часто сигнал перетинає це середнє знизу вгору**. Рівне джерело: миттєве значення весь час майже дорівнює середньому, перетинів майже нема (лише дрібний шум). Полумʼя: сигнал гуляє вгору-вниз навколо середнього кілька разів на секунду — і кожен «вгору» дає перетин. Порахував перетини за секунду — маєш **оцінку частоти мерехтіння** без жодної тригонометрії.

:::tabs
```arduino
// ── FlameFlicker: детектор пульсації полумʼя за перетинами середнього ──────
// Ідея: полумʼя мерехтить на ~2..20 Гц; сонце/лампа світять рівно.
// Рахуємо, скільки разів за вікно сигнал AO перетнув своє повільне середнє
// знизу вгору → це частота мерехтіння в Гц. Є пульсація в смузі → вогонь.
class FlameFlicker {
public:
  FlameFlicker(uint8_t pinAO, float loFlickHz = 2.0f, float hiFlickHz = 20.0f)
    : _pinAO(pinAO), _lo(loFlickHz), _hi(hiFlickHz) {}

  void begin() {
    _mean = analogRead(_pinAO);   // старт середнього — з поточного рівня
    _prevAbove = false;
    _crossings = 0;
    _winStart  = millis();
    _lastFreq  = 0.0f;
  }

  // Кликати ДУЖЕ часто (ціль ~200 Гц вибірки). Раз на вікно оновлює частоту.
  void sample() {
    int v = analogRead(_pinAO);

    // Повільне середнє (експоненційне згладжування): йде за рівнем, не за пульсом.
    // alpha малий → середнє «важке», реагує на секунди, ігнорує пульс на 10 Гц.
    const float alpha = 0.02f;
    _mean += alpha * (v - _mean);

    // Перетин середнього знизу вгору — як тригер Шмітта, з зоною нечутливості
    // проти шуму: рахуємо перехід, лише коли сигнал піднявся вище (_mean+_hyst);
    // повторно «зводимося» тільки після падіння нижче (_mean-_hyst). У самій
    // зоні між порогами стан НЕ міняється — тому дрібний шум не накручує лічильник.
    if (!_prevAbove && v > _mean + _hyst) {   // піднялися вище верхнього порога
      _crossings++;
      _prevAbove = true;                      // взвели — до падіння нижче не рахуємо
    } else if (_prevAbove && v < _mean - _hyst) {
      _prevAbove = false;                     // впали нижче нижнього — знову готові
    }

    // Раз на вікно — переводимо кількість перетинів у частоту.
    uint32_t now = millis();
    uint32_t dt  = now - _winStart;
    if (dt >= _windowMs) {
      _lastFreq = (_crossings * 1000.0f) / dt;   // перетинів за секунду = Гц
      _crossings = 0;
      _winStart  = now;
    }
  }

  float freq()   const { return _lastFreq; }                 // Гц мерехтіння
  bool  flame()  const { return _lastFreq >= _lo && _lastFreq <= _hi; }
  int   level()  const { return (int)_mean; }                // середній рівень ІЧ

private:
  uint8_t  _pinAO;
  float    _lo, _hi;
  float    _mean = 0;
  float    _hyst = 8.0f;      // зона нечутливості (сирі одиниці АЦП)
  bool     _prevAbove = false;
  uint16_t _crossings = 0;
  uint32_t _winStart  = 0;
  const uint16_t _windowMs = 1000;   // вікно виміру частоти
  float    _lastFreq = 0.0f;
};
```
```esp-idf
// ── flicker.c ── та сама логіка; вибірку рівномірно жене задача FreeRTOS,
// а годинник — esp_timer (мікросекунди). Пороги в 12-бітних одиницях.
typedef struct {
    adc_oneshot_unit_handle_t adc;
    adc_channel_t ch;
    float    lo, hi;          // смуга «вогняних» частот, Гц
    float    mean, hyst;      // повільне середнє й зона нечутливості
    bool     prev_above;
    uint16_t crossings;
    int64_t  win_start;       // мкс
    float    last_freq;
} flicker_t;

static void flicker_begin(flicker_t *f) {
    int v = 0;
    adc_oneshot_read(f->adc, f->ch, &v);
    f->mean = (float)v;       // старт середнього — з поточного рівня
    f->hyst = 32.0f;          // 12 біт замість 10 → зона нечутливості вчетверо ширша
    f->prev_above = false;
    f->crossings  = 0;
    f->win_start  = esp_timer_get_time();
    f->last_freq  = 0.0f;
}

// Кликати з задачі рівним кроком ~5 мс (200 Гц вибірки).
static void flicker_sample(flicker_t *f) {
    int v = 0;
    if (adc_oneshot_read(f->adc, f->ch, &v) != ESP_OK) return;

    const float alpha = 0.02f;            // «важке» середнє: йде за рівнем, не за пульсом
    f->mean += alpha * ((float)v - f->mean);

    // Перетин знизу вгору з гістерезисом — той самий тригер Шмітта в коді.
    if (!f->prev_above && v > f->mean + f->hyst) { f->crossings++; f->prev_above = true; }
    else if (f->prev_above && v < f->mean - f->hyst) f->prev_above = false;

    int64_t now = esp_timer_get_time();
    int64_t dt  = now - f->win_start;
    if (dt >= 1000000) {                  // вікно 1 с, час у мікросекундах
        f->last_freq = (f->crossings * 1000000.0f) / (float)dt;
        f->crossings = 0;
        f->win_start = now;
    }
}

static bool  flicker_flame(const flicker_t *f) { return f->last_freq >= f->lo && f->last_freq <= f->hi; }
static int   flicker_level(const flicker_t *f) { return (int)f->mean; }
```
```stm32
/* ── flicker.c ── та сама логіка, але вибірку веде ЗАЛІЗО: таймер запускає
   ADC, DMA приносить число, а рахунок робиться просто в callback. Головний
   цикл при цьому вільний — і жодна довга операція не зіб'є частоту вибірки. */
typedef struct {
    float    lo, hi;          /* смуга «вогняних» частот, Гц */
    float    mean, hyst;
    bool     prev_above;
    uint16_t crossings;
    uint32_t win_start;       /* мс, HAL_GetTick() */
    float    last_freq;
} flicker_t;

flicker_t flick = { .lo = 2.0f, .hi = 20.0f, .hyst = 32.0f };  /* 12 біт → ширша зона */
static volatile uint16_t adc_raw;         /* сюди DMA кладе кожну вибірку */

/* TIM3 зведений у CubeMX на 200 Гц і віддає TRGO як тригер ADC1;
   на старті — HAL_ADC_Start_DMA(&hadc1, (uint32_t *)&adc_raw, 1). */
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance != ADC1) return;
    float v = (float)adc_raw;

    const float alpha = 0.02f;            /* «важке» середнє: йде за рівнем, не за пульсом */
    flick.mean += alpha * (v - flick.mean);

    /* Перетин знизу вгору з гістерезисом — той самий тригер Шмітта в коді. */
    if (!flick.prev_above && v > flick.mean + flick.hyst) { flick.crossings++; flick.prev_above = true; }
    else if (flick.prev_above && v < flick.mean - flick.hyst) flick.prev_above = false;

    uint32_t now = HAL_GetTick(), dt = now - flick.win_start;
    if (dt >= 1000) {                     /* вікно 1 с */
        flick.last_freq = (flick.crossings * 1000.0f) / (float)dt;
        flick.crossings = 0;
        flick.win_start = now;
    }
}

bool flicker_flame(void) { return flick.last_freq >= flick.lo && flick.last_freq <= flick.hi; }
int  flicker_level(void) { return (int)flick.mean; }
```
:::

Три деталі тут не випадкові, і кожна лікує конкретну ваду наївного лічильника.

**Повільне середнє замість сталого порога.** Якби ми рахували перетини навколо фіксованого числа, детектор зламався б від зміни фонового ІЧ: увімкнули світло — і рівень поїхав, а разом із ним і хибні перетини. Експоненційне середнє (`_mean += alpha*(v-_mean)`) — це найдешевший [фільтр нижніх частот](topic:com-signal/moving-average): при малому `alpha` воно **важке**, повзе за рівнем сигналу за секунди й геть не встигає за пульсом на 10 Гц. Тому пульс завжди «стирчить» над своїм власним, повільно пливучим середнім, хоч би як мінявся фон.

**Зона нечутливості (гістерезис).** Без неї найдрібніший шум АЦП, торкаючись середнього, генерував би зливу фальшивих перетинів і показував би «мерехтіння» на порожньому місці. `_hyst` вимагає, щоб сигнал відійшов від середнього на помітну величину вгору (щоб зарахувати перетин) і повернувся нижче на стільки ж (щоб дозволити наступний). Це той самий гістерезис, що й у компаратора з позитивним зворотним звʼязком, тільки в коді.

**Смуга, а не одна частота.** Ми ловимо не рівно 10 Гц, а весь діапазон `2..20 Гц`, бо реальна частота пливе з розміром полумʼя, протягами, дальністю. Заразом нижня межа `2 Гц` відсікає повільні наведення (людина пройшла, тінь ковзнула), а верхня `20 Гц` — електричні перешкоди й брижі АЦП. Усе, що мерехтить у людській «вогняній» смузі, — вогонь; рівне (0 Гц) — сонце; надто швидке — шум.

Складаємо разом. Тепер «є вогонь» означає **і** достатній рівень ІЧ (щоб не ловити мерехтіння тіней у темряві), **і** пульсацію у вогняній смузі:

:::tabs
```arduino
FlameFlicker flick(A0);
const int MIN_LEVEL = 120;   // мінімум середнього ІЧ, щоб взагалі розглядати

void setup() {
  Serial.begin(9600);
  flick.begin();
}

void loop() {
  flick.sample();                        // семплюй якомога частіше

  bool bright   = flick.level() > MIN_LEVEL;   // є помітний ІЧ
  bool flickers = flick.flame();               // і він пульсує 2..20 Гц
  bool realFire = bright && flickers;          // вогонь, а не сонце

  static uint32_t t = 0;
  if (millis() - t > 200) {              // друкуй нечасто, семплюй часто
    t = millis();
    Serial.print("рівень="); Serial.print(flick.level());
    Serial.print("  f=");     Serial.print(flick.freq(), 1);
    Serial.print(" Гц  →  "); Serial.println(realFire ? "ВОГОНЬ" : "спокій");
  }
}
```
```esp-idf
#define MIN_LEVEL 480         // мінімум середнього ІЧ у 12-бітних одиницях

static flicker_t flick = { .ch = ADC_CHANNEL_6, .lo = 2.0f, .hi = 20.0f };

// Окрема задача семплює рівним кроком — це надійніше за лічильник у loop().
static void flame_task(void *arg) {
    flicker_begin(&flick);
    TickType_t next = xTaskGetTickCount();
    int n = 0;
    for (;;) {
        flicker_sample(&flick);                       // семплюй якомога рівніше

        if (++n >= 40) {                              // друкуй нечасто, семплюй часто
            n = 0;
            bool bright   = flicker_level(&flick) > MIN_LEVEL;  // є помітний ІЧ
            bool flickers = flicker_flame(&flick);              // і він пульсує 2..20 Гц
            ESP_LOGI(TAG, "рівень=%d  f=%.1f Гц  →  %s",
                     flicker_level(&flick), flick.last_freq,
                     (bright && flickers) ? "ВОГОНЬ" : "спокій");
        }
        vTaskDelayUntil(&next, pdMS_TO_TICKS(5));     // рівні 5 мс = 200 Гц вибірки
    }
}

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &flick.adc));
    adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(flick.adc, flick.ch, &ch));
    xTaskCreate(flame_task, "flame", 4096, NULL, 5, NULL);
}
```
```stm32
#define MIN_LEVEL 480         /* мінімум середнього ІЧ у 12-бітних одиницях */

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init(); MX_DMA_Init(); MX_ADC1_Init(); MX_TIM3_Init();

    flick.win_start = HAL_GetTick();
    HAL_ADC_Start_DMA(&hadc1, (uint32_t *)&adc_raw, 1);  /* вибірку жене TIM3 */
    HAL_TIM_Base_Start(&htim3);                          /* 200 Гц, без жодного delay */

    uint32_t t = 0;
    while (1) {
        /* Головний цикл лише друкує: рахунок уже зробив callback у перериванні. */
        if (HAL_GetTick() - t > 200) {
            t = HAL_GetTick();
            bool bright   = flicker_level() > MIN_LEVEL;   /* є помітний ІЧ */
            bool flickers = flicker_flame();               /* і він пульсує 2..20 Гц */
            printf("рівень=%d  f=%.1f Гц  →  %s\r\n",
                   flicker_level(), flick.last_freq,
                   (bright && flickers) ? "ВОГОНЬ" : "спокій");
        }
    }
}
```
:::

Наведи на цю програму сонце крізь вікно — рівень високий, а `f` тримається біля нуля: «спокій». Черкни запальничкою — рівень підскочить і `f` осяде десь у `8..12 Гц`: «ВОГОНЬ». Ось та відмінність, якої голий поріг не вміє, а десяток рядків коду вміє. Саме так (тільки надійніше й на кількох смугах) працюють дорослі промислові детектори полумʼя.

> 🔧 **Навіщо це.** Перехід від «яскраво» до «мерехтить яскраво» — це перехід від іграшки до інструмента. Порогова платка спрацьовує від сонця й тому нікому не потрібна там, де є вікно. Детектор мерехтіння відсіює всі **рівні** джерела — сонце, лампи, обігрівачі — і лишає саме те, що пульсує по-вогняному. Ти не додав жодної деталі, лише подивився на сигнал у часі, а не в моменті, — і давач за копійки почав робити те, за що з дорослих беруть тисячі. Це головний урок обробки сигналу: **інформація часто не в рівні, а в тому, як рівень міняється**.

Чесна межа й цього прийому: мерехтіння видно **лише коли давач семплює швидко**. Якщо головний цикл забитий повільними речами (запис на карту, мережа з блокуванням), вибірка просяде нижче кількох десятків герц, і за [теоремою відліків](topic:com-signal/nyquist-aliasing) пульс на 10 Гц просто не потрапить у дані — детектор осліпне. Тому `sample()` має крутитися часто; блокувальні операції винось у переривання таймера або роби неблокувально.

## Складання: пожежний робот на двох давачах

Тепер зберемо все у класичну задачу гуртків — **візок, що сам їде на вогонь і гасить його**. Він показує, навіщо тут аналоговий вихід і навіщо два давачі одразу.

Ідея наведення — груба, але навдивовижу дієва, і в неї немає жодної тригонометрії. Ставимо **два давачі**, розвівши їхні «очі» врізнобіч — лівий дивиться вліво-вперед, правий вправо-вперед. Порівнюємо силу жару зліва й справа: сильніше зліва — крутимо вліво, сильніше справа — вправо, порівну — їдемо прямо на вогонь. Це той самий принцип, за яким метелик летить на світло двома очима, тільки в нас замість очей два фототранзистори, а замість крил два колеса. Коли жар з обох давачів переростає поріг «гасити» — вмикаємо вентилятор і задуваємо полумʼя.

Спершу — розкладка й найнижчий шар, керування двома моторами (припустимо звичайний драйвер на два входи-напрямки й ШІМ-швидкість на кожен бік; конкретні піни — під твою плату):

:::tabs
```arduino
// ── Пожежний робот: наведення на найяскравіше полумʼя двома KY-026 ─────────
// AO лівого давача — A0, правого — A1. DO не використовуємо: тут важить
// ВЕЛИЧИНА жару, а не факт. Мотори — через простий драйвер (напрямок + ШІМ).

const uint8_t AO_L = A0, AO_R = A1;     // аналогові виходи давачів
const uint8_t FAN  = 7;                 // ключ вентилятора-гасія

// Драйвер моторів: піни напрямку + ШІМ-швидкості лівого й правого борту.
const uint8_t L_DIR = 4, L_PWM = 5;
const uint8_t R_DIR = 8, R_PWM = 6;

void drive(int left, int right) {       // швидкості −255..+255 (знак = напрямок)
  digitalWrite(L_DIR, left  >= 0);
  digitalWrite(R_DIR, right >= 0);
  analogWrite(L_PWM, constrain(abs(left),  0, 255));
  analogWrite(R_PWM, constrain(abs(right), 0, 255));
}
```
```esp-idf
// ── Пожежний робот на ESP-IDF: напрямок — GPIO, швидкість — блок LEDC ──────
// AO лівого давача — ADC1_CH6 (GPIO34), правого — ADC1_CH7 (GPIO35).
#include "driver/ledc.h"
#include <stdlib.h>

#define AO_L_CH  ADC_CHANNEL_6
#define AO_R_CH  ADC_CHANNEL_7
#define FAN      GPIO_NUM_23            // ключ вентилятора-гасія
#define L_DIR    GPIO_NUM_25
#define R_DIR    GPIO_NUM_26
#define L_PWM_IO 14
#define R_PWM_IO 27

static void motors_init(void) {
    gpio_config_t io = { .pin_bit_mask = (1ULL << L_DIR) | (1ULL << R_DIR) | (1ULL << FAN),
                         .mode = GPIO_MODE_OUTPUT };
    ESP_ERROR_CHECK(gpio_config(&io));

    ledc_timer_config_t tm = { .speed_mode = LEDC_LOW_SPEED_MODE,
                               .duty_resolution = LEDC_TIMER_8_BIT,   // duty 0..255
                               .timer_num = LEDC_TIMER_0,
                               .freq_hz = 20000,                      // за межею чутності
                               .clk_cfg = LEDC_AUTO_CLK };
    ESP_ERROR_CHECK(ledc_timer_config(&tm));

    const int io_pwm[2] = { L_PWM_IO, R_PWM_IO };
    for (int c = 0; c < 2; c++) {
        ledc_channel_config_t ch = { .gpio_num = io_pwm[c], .speed_mode = LEDC_LOW_SPEED_MODE,
                                     .channel = c, .timer_sel = LEDC_TIMER_0, .duty = 0 };
        ESP_ERROR_CHECK(ledc_channel_config(&ch));
    }
}

static void set_duty(ledc_channel_t ch, int v) {
    if (v > 255) v = 255;
    ledc_set_duty(LEDC_LOW_SPEED_MODE, ch, v);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, ch);
}

static void drive(int left, int right) {   // швидкості −255..+255 (знак = напрямок)
    gpio_set_level(L_DIR, left  >= 0);
    gpio_set_level(R_DIR, right >= 0);
    set_duty(LEDC_CHANNEL_0, abs(left));
    set_duty(LEDC_CHANNEL_1, abs(right));
}
```
```stm32
/* ── Пожежний робот на STM32 HAL: напрямок — GPIO, швидкість — канали TIM2 ──
   AO лівого давача — ADC1_IN0 (PA0), правого — ADC1_IN1 (PA1).
   TIM2 зведений у CubeMX на PWM, Period = 255 → duty теж 0..255. */
#include <stdlib.h>

#define L_DIR_PORT GPIOB
#define L_DIR_PIN  GPIO_PIN_4
#define R_DIR_PORT GPIOB
#define R_DIR_PIN  GPIO_PIN_5
#define FAN_PORT   GPIOB
#define FAN_PIN    GPIO_PIN_6          /* ключ вентилятора-гасія */

extern TIM_HandleTypeDef htim2;

static void motors_init(void) {
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);   /* лівий борт */
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);   /* правий борт */
}

static void drive(int left, int right) {   /* швидкості −255..+255 (знак = напрямок) */
    HAL_GPIO_WritePin(L_DIR_PORT, L_DIR_PIN, left  >= 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(R_DIR_PORT, R_DIR_PIN, right >= 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);
    int dl = abs(left),  dr = abs(right);
    if (dl > 255) dl = 255;
    if (dr > 255) dr = 255;
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, dl);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, dr);
}
```
:::

Тепер — читання давачів. Тут дрібниця, на якій спотикаються всі: **сире читання АЦП смикається**, бо полумʼя ж мерехтить (те саме мерехтіння, що вище було другом, тут, для порівняння лівого з правим, — завада). Порівнювати два тремтливі числа марно: рішення «куди повертати» стрибатиме щокадру, і робот засмикається на місці. Тому кожен давач читаємо **згладжено** — тим самим повільним середнім, що вже знайоме:

:::tabs
```arduino
float irL = 0, irR = 0;                 // згладжена сила жару зліва / справа

void readSensors() {
  const float a = 0.15f;                // згладжування: гасить тремтіння полумʼя
  irL += a * (analogRead(AO_L) - irL);
  irR += a * (analogRead(AO_R) - irR);
}
```
```esp-idf
static adc_oneshot_unit_handle_t adc;   // ADC1 — блок, дружній до Wi-Fi
static float ir_l = 0, ir_r = 0;        // згладжена сила жару зліва / справа

static void read_sensors(void) {
    const float a = 0.15f;              // згладжування: гасить тремтіння полумʼя
    int l = 0, r = 0;
    adc_oneshot_read(adc, AO_L_CH, &l);
    adc_oneshot_read(adc, AO_R_CH, &r);
    ir_l += a * ((float)l - ir_l);
    ir_r += a * ((float)r - ir_r);
}
```
```stm32
/* ADC1 у режимі сканування двох рангів (IN0, IN1) + DMA circular; на старті —
   HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc_pair, 2), далі числа приходять самі. */
static volatile uint16_t adc_pair[2];   /* [0] — лівий канал, [1] — правий */
static float ir_l = 0, ir_r = 0;        /* згладжена сила жару зліва / справа */

static void read_sensors(void) {
    const float a = 0.15f;              /* згладжування: гасить тремтіння полумʼя */
    ir_l += a * ((float)adc_pair[0] - ir_l);
    ir_r += a * ((float)adc_pair[1] - ir_r);
}
```
:::

І сам мозок — короткий і прозорий. Уся поведінка робота виводиться з **різниці** та **суми** двох згладжених величин: різниця каже, **куди** повертати, сума — **чи вже близько** й чи пора гасити.

:::tabs
```arduino
const float SEE_FIRE  = 200;   // сума жару, з якої робот починає їхати на вогонь
const float BURN_NEAR = 700;   // сума, з якої вважаємо, що впритул → гасити
const int   BASE_SPD  = 140;   // базова швидкість руху вперед
const float TURN_GAIN = 0.6f;  // наскільки різко кермувати за різницею

void setup() {
  pinMode(FAN, OUTPUT);
  pinMode(L_DIR, OUTPUT); pinMode(L_PWM, OUTPUT);
  pinMode(R_DIR, OUTPUT); pinMode(R_PWM, OUTPUT);
  digitalWrite(FAN, LOW);
  irL = analogRead(AO_L);               // старт середніх — з поточних значень
  irR = analogRead(AO_R);
}

void loop() {
  readSensors();
  float sum  = irL + irR;               // загальна близькість вогню
  float diff = irL - irR;               // >0 → жар зліва, <0 → справа

  if (sum < SEE_FIRE) {
    // Вогню не видно — стій (або тут можна крутитися й шукати).
    digitalWrite(FAN, LOW);
    drive(0, 0);
  }
  else if (sum >= BURN_NEAR) {
    // Впритул до полумʼя — стоп і дми, доки жар не впаде.
    drive(0, 0);
    digitalWrite(FAN, HIGH);
  }
  else {
    // Бачимо вогонь — їдемо на нього, підрулюючи за різницею.
    digitalWrite(FAN, LOW);
    int turn  = (int)(TURN_GAIN * diff);        // кермо пропорційно різниці
    int left  = BASE_SPD - turn;                // сильніше зліва → пригальмуй лівий
    int right = BASE_SPD + turn;                // → робот доверне ліворуч, на жар
    drive(left, right);
  }
  delay(20);                            // ~50 разів на секунду — досить для керма
}
```
```esp-idf
// Пороги в 12-бітних одиницях — уперед-калібровані під 0..4095, а не 0..1023.
#define SEE_FIRE   800.0f      // сума жару, з якої робот починає їхати на вогонь
#define BURN_NEAR 2800.0f      // сума, з якої вважаємо, що впритул → гасити
#define BASE_SPD   140         // базова швидкість руху вперед
#define TURN_GAIN  0.6f        // наскільки різко кермувати за різницею

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc));
    adc_oneshot_chan_cfg_t cfg = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc, AO_L_CH, &cfg));
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc, AO_R_CH, &cfg));
    motors_init();
    gpio_set_level(FAN, 0);

    int l = 0, r = 0;                          // старт середніх — з поточних значень
    adc_oneshot_read(adc, AO_L_CH, &l); ir_l = l;
    adc_oneshot_read(adc, AO_R_CH, &r); ir_r = r;

    for (;;) {
        read_sensors();
        float sum  = ir_l + ir_r;              // загальна близькість вогню
        float diff = ir_l - ir_r;              // >0 → жар зліва, <0 → справа

        if (sum < SEE_FIRE) {                  // вогню не видно — стій
            gpio_set_level(FAN, 0);
            drive(0, 0);
        } else if (sum >= BURN_NEAR) {         // впритул — стоп і дми
            drive(0, 0);
            gpio_set_level(FAN, 1);
        } else {                               // бачимо вогонь — їдемо, підрулюючи
            gpio_set_level(FAN, 0);
            int turn = (int)(TURN_GAIN * diff);
            drive(BASE_SPD - turn, BASE_SPD + turn);
        }
        vTaskDelay(pdMS_TO_TICKS(20));         // ~50 Гц — досить для керма
    }
}
```
```stm32
/* Пороги в 12-бітних одиницях — перекалібровані під 0..4095, а не 0..1023. */
#define SEE_FIRE   800.0f      /* сума жару, з якої робот починає їхати на вогонь */
#define BURN_NEAR 2800.0f      /* сума, з якої вважаємо, що впритул → гасити */
#define BASE_SPD   140         /* базова швидкість руху вперед */
#define TURN_GAIN  0.6f        /* наскільки різко кермувати за різницею */

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init(); MX_DMA_Init(); MX_ADC1_Init(); MX_TIM2_Init();
    motors_init();
    HAL_GPIO_WritePin(FAN_PORT, FAN_PIN, GPIO_PIN_RESET);

    HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc_pair, 2);
    HAL_Delay(5);                              /* дай DMA принести перші числа */
    ir_l = adc_pair[0];                        /* старт середніх — з поточних значень */
    ir_r = adc_pair[1];

    while (1) {
        read_sensors();
        float sum  = ir_l + ir_r;              /* загальна близькість вогню */
        float diff = ir_l - ir_r;              /* >0 → жар зліва, <0 → справа */

        if (sum < SEE_FIRE) {                  /* вогню не видно — стій */
            HAL_GPIO_WritePin(FAN_PORT, FAN_PIN, GPIO_PIN_RESET);
            drive(0, 0);
        } else if (sum >= BURN_NEAR) {         /* впритул — стоп і дми */
            drive(0, 0);
            HAL_GPIO_WritePin(FAN_PORT, FAN_PIN, GPIO_PIN_SET);
        } else {                               /* бачимо вогонь — їдемо, підрулюючи */
            HAL_GPIO_WritePin(FAN_PORT, FAN_PIN, GPIO_PIN_RESET);
            int turn = (int)(TURN_GAIN * diff);
            drive(BASE_SPD - turn, BASE_SPD + turn);
        }
        HAL_Delay(20);                         /* ~50 Гц — досить для керма */
    }
}
```
:::

Простеж логіку керма, бо в ній уся кмітливість. Якщо жар **сильніший зліва**, `diff` додатний, `turn` додатний; ми **віднімаємо** його від лівого колеса й **додаємо** до правого — лівий борт крутиться повільніше, правий швидше, і візок довертає **вліво**, туди, де вогонь яскравіший. Симетрично для правого боку. Що більша різниця — то різкіший доворот; коли жар зрівнявся (`diff≈0`), обидва колеса йдуть на `BASE_SPD`, і робот котиться **прямо на полумʼя**. Це найпростіший пропорційний регулятор: помилка наведення — це різниця давачів, а `TURN_GAIN` — його коефіцієнт. Хочеш плавнішого — зменш підсилення; хочеш жвавішого — збільш (аж доки не почне рискати).

> 🔧 **Навіщо це.** Тут видно, чому для наведення беруть **аналоговий** вихід, а не цифровий. DO дав би лише «є/нема вогонь» з кожного боку — і робот умів би тільки «вогонь десь ліворуч чи праворуч», грубо, ступінчасто, з рисканням. AO дає **величину**, а величина дає **різницю**, а різниця дає **плавне пропорційне кермо** — робот не сіпається між «вліво/вправо», а веде на вогонь м'яко, тим точніше, чим ближче. Той самий принцип двох рознесених давачів і керма за їхньою різницею — основа стеження за лінією, за світлом, за джерелом сигналу; вогонь тут лише окремий випадок.

## На ESP32: те саме, але стережися АЦП і Wi-Fi

Якщо мозок робота — [ESP32](topic:cat-hw-boards/esp32-family) (спокуса реальна: він потужніший і вміє Wi-Fi, щоб слати тривогу), код майже той самий, але аналогове читання має **три відмінності**, на яких легко обпектися, і всі вони — про АЦП.

**Роздільність інша.** У ESP32 АЦП **12-бітний**: читання дає `0..4095`, а не `0..1023`, як на Arduino Uno. Усі твої пороги (`SEE_FIRE`, `BURN_NEAR`, `THRESH`) виміряні для 10 біт — на ESP32 їх треба **перекалібрувати** (грубо кажучи, вчетверо більші числа, але надійніше — просто заміряй наново своїм давачем).

**Опорна напруга й діапазон.** За замовчуванням канал АЦП ESP32 упевнено міряє лише десь **до 1.1 В**, а вище — «зашкалює» й тримає стелю. Аналоговий сигнал KY-026 при 3.3-вольтовому живленні цілком може вилізти за цю межу. Тому канал треба перевести в режим із **послабленням** (англ. *attenuation*), щоб він брав аж до повних ~3.3 В:

:::tabs
```arduino
void setup() {
  // Дозволити АЦП міряти майже до 3.3 В (інакше стеля ≈1.1 В і сигнал «зрізається»).
  analogSetAttenuation(ADC_11db);   // на весь АЦП; або поканально analogSetPinAttenuation()
  // ... решта setup як вище
}
```
```esp-idf
// Те саме рідним API: послаблення задається ПОКАНАЛЬНО, при налаштуванні каналу.
// ADC_ATTEN_DB_12 — нове ім'я того самого режиму (старе ADC_ATTEN_DB_11 лишили
// як синонім заради сумісності).
adc_oneshot_chan_cfg_t ch = {
    .atten    = ADC_ATTEN_DB_12,       // діапазон ~0..3.1 В замість ~0..1.1 В
    .bitwidth = ADC_BITWIDTH_DEFAULT,  // 12 біт → 0..4095
};
ESP_ERROR_CHECK(adc_oneshot_config_channel(adc, ADC_CHANNEL_6, &ch));
```
:::

**І найпідступніше — конфлікт із Wi-Fi.** АЦП ESP32 поділено на два блоки: **ADC1** і **ADC2**. Коли працює Wi-Fi, він **захоплює ADC2 собі**, і читання з будь-якого каналу ADC2 починає повертати **сміття** — не помилку, а просто випадкові числа, що виглядають як дані. Це класична пастка «робота-пожежника з тривогою по Wi-Fi»: без мережі все працює, увімкнув Wi-Fi — і давачі «показують вогонь» на рівному місці або мовчать на справжньому. Лікування одне: **на ESP32 із Wi-Fi чіпляй давачі лише на піни ADC1** — це `GPIO 32–39` (`ADC1_CH*`). Тоді АЦП давачів і радіо не б'ються за той самий блок.

:::tabs
```arduino
// ESP32 + Wi-Fi: давачі ТІЛЬКИ на ADC1 (GPIO 32..39), інакше при активному
// Wi-Fi ADC2 віддає випадкові числа. Приклад: лівий давач — GPIO34, правий — GPIO35.
const uint8_t AO_L = 34;   // ADC1_CH6 — сумісний з Wi-Fi
const uint8_t AO_R = 35;   // ADC1_CH7 — сумісний з Wi-Fi
```
```esp-idf
// Рідне API взагалі не знає «пінів АЦП» — воно адресує БЛОК і КАНАЛ, тож
// вибір ADC1 тут не домовленість, а перший аргумент: ADC_UNIT_1.
adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };  // ADC2 забирає Wi-Fi
#define AO_L_CH  ADC_CHANNEL_6     // GPIO34
#define AO_R_CH  ADC_CHANNEL_7     // GPIO35
```
:::

Уся інша логіка — обгортка `KY026`, детектор `FlameFlicker`, наведення робота — переноситься на ESP32 без змін; міняються тільки числа порогів (через 12 біт) і вибір пінів (через ADC1). Обгортка тут окупається вдруге: оскільки вся робота з АЦП захована в методах `strength()`/`sample()`, підлаштувати її під ESP32 — це поправити конструктор і початкове налаштування, а не полювати на читання АЦП по всьому коді.

## Складність і пастки: коротко про те, де обпечешся

Зберемо в одному місці всі граблі, розкидані по коду вище, — бо саме на них іде більшість вечорів із цим давачем.

- **Бік порівняння DO (інверсія).** Найчастіша й найдурніша помилка: логіка написана під `== HIGH`, а модуль інвертований. Пристрій «бачить вогонь» у спокої й «сліпне» на полумʼї. Лікування — прапорець `invertedDO` в обгортці, а перед тим **звірка оком по індикаторному світлодіоду** модуля: піднеси вогонь, подивись, у який бік клацнув індикатор, — і став прапорець під нього. Не вгадуй за чужою таблицею.

- **Дрижання на межі порога.** Голе читання виводу на межі спрацювання видасть рій перемикань, і кожна подія «вогонь зʼявився» вистрелить сотні разів. Завжди проводь DO через **придушення дрижання** (метод `update()`), а поріг-гвинтик виставляй із запасом, а не рівно на межу.

- **Абсолютних порогів AO не існує.** Сире число залежить від напруги живлення модуля, від опорної напруги АЦП і від того, зверху чи знизу дільника стоїть фототранзистор (на одних платах більше ІЧ дає більше число, на інших — менше). **Завжди калібруй під свою сцену й плату**: піднеси-прибери запальничку, подивись у послідовну консоль, як стрибає сире число АЦП, — і став поріг та бік порівняння по факту, а не по здогаду.

- **Сонце й лампи розжарення.** Головна й непереборна порогом пастка. Давач бачить ближній ІЧ, а не вогонь; пряме сонце крізь вікно чи галогенка перекинуть будь-який рівневий поріг **без полумʼя**. Два ліки: фізичний (не став «око» так, щоб у нього світило сонце; звузь кут огляду) і програмний — **детектор мерехтіння** (`FlameFlicker`), що відрізняє пульсуюче полумʼя від рівного джерела. У серйозному застосуванні — обидва разом.

- **Замало швидка вибірка вбиває детектор мерехтіння.** Щоб побачити пульс на 10 Гц, треба семплювати десятки-сотні разів на секунду. Забив головний цикл блокувальними затримками, записом на карту чи мережею — вибірка просіла, і за [теоремою відліків](topic:com-signal/nyquist-aliasing) пульс зник із даних. Тримай `sample()` частим; повільне винось у переривання або роби неблокувально.

- **ESP32: 12 біт, послаблення, ADC2-проти-Wi-Fi.** Перекалібруй пороги під `0..4095`; увімкни послаблення до ~3.3 В (`ADC_11db` в Arduino, `ADC_ATTEN_DB_12` в ESP-IDF); **давачі — лише на ADC1 (GPIO 32–39)**, якщо в проєкті є Wi-Fi, інакше ADC2 віддаватиме випадкові числа при активному радіо. Ця трійця відповідальна за більшість «на Arduino працювало, на ESP32 ні».

- **Це рефлекс, а не сторож.** Хоч би який розумний був код, фізика давача лишається: близька відстань (метр-два), вузький конус (~60°), сліпота до тліючої без полумʼя пожежі. KY-026 — блискучий **точковий рефлекс на відкритий вогонь у полі зору** для робота, стенда чи простої тривоги над конкретним джерелом; він **не заміняє** сертифікований димовий сповіщувач там, де ціна помилки — життя. Код робить його розумнішим, але не робить його іншим приладом.

Підсумок простий. Голий пін дає біт і число; бібліотека-обгортка перетворює їх на **чесний, стабільний, незалежний від інверсії інтерфейс**; детектор мерехтіння перетворює давач яскравості на **давач вогню**, що не плутає полумʼя із сонцем; а двосенсорне наведення перетворює факт «є вогонь» на **дію** — робот, що сам знаходить полумʼя й гасить його. Уся ця відстань пройдена кількома десятками рядків справжнього C++ — і вона, а не сама платка, і є тим, за що беруть мікроконтролер.
