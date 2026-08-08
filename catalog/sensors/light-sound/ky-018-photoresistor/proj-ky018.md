# ⚙️ KY-018 у коді: калібрування, поріг із гістерезисом, згладжування

Один вимір АЦП — одна нога, одне число: це вже вміє найперший приклад під будь-яку платформу (`analogRead` в Arduino, `adc_oneshot_read` в ESP-IDF, `HAL_ADC_GetValue` на STM32). Але між «прочитати число» і «зробити на ньому робочий пристрій» лежить прірва, у яку валиться кожен, хто не був там раніше. Число тремтить, хоч світло стоїть непорушно. Поріг, підібраний увечері, вранці бреше. Світло, зав'язане на поріг, починає нервово моргати в сутінках. Та сама програма, залита в другий екземпляр тієї самої платки, поводиться інакше. Усе це — не збіг обставин і не брак, а прямі наслідки того, **чим є** відлік KY-018: це не «яскравість», а миттєва позиція шумної напруги дільника на шкалі АЦП, ще й зсунута в кожного екземпляра по-своєму.

Тож задача цієї вставки — не показати ще раз одне читання АЦП, а провести весь шлях від сирого числа до сигналу, якому можна довіряти рішення: **виміряти власний діапазон платки** (калібрування), **приборкати тремтіння** (згладжування), **перекласти відлік у зрозумілі одиниці** (відсотки), і **прийняти стійке рішення без брязкоту** (поріг із гістерезисом). Наприкінці збереться маленька самодостатня «бібліотека давача» — один об'єкт, влаштований однаково під Arduino, ESP-IDF і STM32 HAL, і в якому кожен рядок стоїть тому, що без нього щось ламається на живому залізі.

Код тут — справжня прошивка, яку можна залити й побачити результат; не псевдокод. Кожен приклад показано вкладками під три середовища — Arduino, ESP-IDF і STM32 HAL. Логіка в них одна: узяти відлік з аналогового входу, полічити, витримати паузу. Різняться лише імена, якими кожне середовище зве ту саму ногу АЦП, той самий такт часу й ту саму ногу виходу.

## Задача перша: свій діапазон. Калібрування під кімнату

Найперша ілюзія новачка — що відлік має «природний» сенс: мовляв, 0 — це темрява, максимум — яскраве світло, а посередині — сутінки. Насправді ні. Крайні значення шкали АЦП (0 і 1023 на 10-бітному АЦП Uno, 0 і 4095 на 12-бітному — ESP32 чи типовий STM32) відповідають крайнім напругам на вході, а не крайнім освітленостям. Реальний KY-018 у реальній кімнаті майже ніколи не дає ані чистого нуля, ані повного максимуму: у «темряві» під столом він покаже не 0, а, скажімо, 40; на «яскравому» настільному світлі — не 1023, а 850. Ці два числа — **справжні межі саме цієї платки в саме цьому місці**, і поки ти їх не знаєш, будь-який поріг ти ставиш наосліп.

> 🔧 **Навіщо це.** Калібрування — це не «покращення точності», а переклад із чужої системи координат у свою. Без нього код мислить у голих одиницях АЦП, які самі собою нічого не означають; після нього — у частках власного діапазону платки, і той самий поріг «половина яскравості» стає осмисленим і переносним у часі (не між екземплярами — про це нижче). Це різниця між «нижче 300» (магічне число, що завтра збреше) і «нижче 50 % мого діапазону» (твердження, яке лишається правдою).

Ідея калібрування проста до непристойності: перш ніж вимірювати світло, **покажи платці свої крайні умови й запам'ятай, які числа вона на них дає**. Накрий очок долонею — оце твоя «темрява», запиши мінімум. Присвіти ліхтариком (або просто дай робоче освітлення кімнати) — оце твоє «світло», запиши максимум. Тепер будь-який пізніший відлік можна помістити між цими двома кілочками й сказати, на скільки відсотків він від темряви до світла.

Найчесніший спосіб зробити це — **автокалібрування за кілька секунд руху**: крутиш освітлення туди-сюди, а програма стежить за побаченими крайнощами й розсовує межі під них. Ось робочий фрагмент, який за задані секунди збирає min і max:

:::tabs
```arduino
const uint8_t PIN_LDR = A0;

int rawMin = 1023;   // почнемо з «перевернутих» меж, щоб перший же відлік їх стягнув
int rawMax = 0;

void calibrate(uint16_t seconds) {
  uint32_t until = millis() + (uint32_t)seconds * 1000;
  while (millis() < until) {
    int v = analogRead(PIN_LDR);
    if (v < rawMin) rawMin = v;    // побачили темніше — опустили дно
    if (v > rawMax) rawMax = v;    // побачили світліше — підняли стелю
    delay(5);
  }
}
```

```esp-idf
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LDR_CHAN  ADC_CHANNEL_6    // GPIO34 — канал блоку ADC1

static adc_oneshot_unit_handle_t adc1;
static int raw_min = 4095;   // «перевернуті» межі, щоб перший же відлік їх стягнув
static int raw_max = 0;

static void calibrate(uint16_t seconds) {
  TickType_t until = xTaskGetTickCount() + pdMS_TO_TICKS(seconds * 1000);
  while (xTaskGetTickCount() < until) {
    int v = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &v));
    if (v < raw_min) raw_min = v;  // побачили темніше — опустили дно
    if (v > raw_max) raw_max = v;  // побачили світліше — підняли стелю
    vTaskDelay(pdMS_TO_TICKS(5));
  }
}
```

```stm32
#include "main.h"

extern ADC_HandleTypeDef hadc1;  // CubeMX: ADC1, вхід IN0 → PA0, 12 біт

static uint16_t ldr_read(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

static int raw_min = 4095;   // «перевернуті» межі, щоб перший же відлік їх стягнув
static int raw_max = 0;

static void calibrate(uint16_t seconds) {
  uint32_t until = HAL_GetTick() + (uint32_t)seconds * 1000;
  while (HAL_GetTick() < until) {
    int v = ldr_read();
    if (v < raw_min) raw_min = v;  // побачили темніше — опустили дно
    if (v > raw_max) raw_max = v;  // побачили світліше — підняли стелю
    HAL_Delay(5);
  }
}
```
:::

Тонкість, що відрізняє живий код від наївного, — у стартових значеннях. `rawMin` починається з **найбільшого** можливого числа, `rawMax` — з **найменшого**. Це навмисне «неправильно»: перший же реальний відлік менший за повну шкалу (1023 чи 4095), тож одразу стягне `rawMin` донизу; перший же відлік більший за 0 підніме `rawMax`. Почни ти з `rawMin = 0`, і жоден відлік ніколи не буде меншим — межа застрягне на нулі назавжди. Цей прийом («ініціалізуй екстремум протилежною межею») — класичний, і варто його впізнавати, бо він зринає всюди, де шукають min/max потоку.

Що робити зі зібраними межами? Або зберегти в код константами (коли умови стабільні — прилад завжди в тому самому місці), або тримати в пам'яті на кожен запуск, або — найнадійніше для «поставив і забув» пристрою — записати в **енергонезалежну пам'ять** (у кожного середовища вона зветься по-своєму: `EEPROM` на Uno, NVS в ESP-IDF, окрема сторінка Flash чи мікросхема EEPROM на STM32), щоб калібрування пережило вимкнення живлення. Для навчального макета досить першого-другого; для реального виробу — третє.

Є й пастка калібрування, про яку мовчать: якщо під час збору меж на очок **не потрапило** ані справжньої темряви, ані справжнього світла, межі вийдуть вузькими й брехливими. Тому автокалібрування завжди супроводжують інструкцією користувачеві («покрутіть освітлення»), а ще краще — доповнюють **скиданням підозріло вузького діапазону**: якщо `rawMax − rawMin` вийшов зовсім малим (платка не побачила контрасту), калібрування недійсне, треба повторити.

## Задача друга: у зрозумілі одиниці. Перерахунок у відсотки

Маючи власні межі, сирий відлік легко перекласти у **відсоток яскравості** — 0 % на своїй темряві, 100 % на своєму світлі. Це та сама лінійна інтерполяція, що ховається в Arduino-функції `map`, тільки чесно виписана:

```cpp
// сирий відлік → 0..100 % у межах власного діапазону платки
uint8_t toPercent(int raw) {
  if (raw <= rawMin) return 0;
  if (raw >= rawMax) return 100;
  return (uint32_t)(raw - rawMin) * 100 / (rawMax - rawMin);
}
```

Тут дві деталі несуть вагу, і обидві — про арифметику цілих на мікроконтролері. Перша: **обрізання по краях** (`raw <= rawMin` та `raw >= rawMax`) обов'язкове, бо після калібрування реальний відлік цілком може вийти **за** збережені межі — стало ще темніше або ще яскравіше, ніж під час калібрування. Без обрізання формула дасть від'ємний відсоток або більший за 100, і далі все попливе. Друга: **порядок множення й ділення**. Написати `(raw - rawMin) / (rawMax - rawMin) * 100` — типова згубна помилка: цілочислове ділення першим дасть 0 у майже всіх випадках (чисельник менший за знаменник → 0), і ти отримаєш 0 % скрізь, крім самого максимуму. Тому **множимо на 100 ПЕРШИМ**, поки чисельник великий, і аж тоді ділимо. А `(uint32_t)` попереду рятує від переповнення: `(raw - rawMin) * 100` для 12-бітного ESP32 може сягнути `4095 · 100 = 409500`, що не влазить у 16-бітний `int` Arduino Uno (стеля 32767) — без розширення до 32 біт число «загорнеться» й дасть сміття.

> 🔧 **Навіщо це.** Ці дві пастки — цілочислове ділення та переповнення — не специфічні для KY-018; вони чигають на кожен перерахунок відліку в будь-якому вбудованому коді, від давача температури до рівня пального. Хто раз побачив «завжди 0 %» від передчасного ділення чи «дике число» від переповнення `int`, той запам'ятовує правило назавжди: **у цілій арифметиці спершу множ, тоді ділі, і бери тип із запасом**. Готовий `map` це приховує, але приховує й тоді, коли межі підібрані так, що він тихо бреше, — тож розуміти механізм важливіше, ніж знати ім'я функції. Розкладку `map` по кроках і його типові підводні камені розібрано у [ковзному середньому й сусідніх замітках про цілу арифметику давачів](book:algorithms/moving-average) — тут досить пам'ятати сам порядок дій.

Чи це вже «яскравість у якихось одиницях»? Ні — і це чесно назвати. Відсоток лінійний **по відліку**, а відлік нелінійний по світлу (опір LDR падає з яскравістю приблизно логарифмічно). Тож 50 % відліку — це не «половина люксів», а «половина шляху напруги дільника між твоєю темрявою і твоїм світлом». Для «увімкни підсвітку, коли темніє» чи «наскільки зараз ясно за грубою шкалою» цього рівно досить; для метрології бери цифровий люксметр. Відсоток тут — **умовна одиниця**, зручна людині, а не фізична величина.

## Задача третя: приборкати тремтіння. Згладжування

Постав платку на стіл, не чіпай, не міняй світло — і подивись на потік відліків АЦП. Число не стоїть: воно дрібно тремтить на кілька одиниць туди-сюди навіть за абсолютно сталого освітлення. Це не «поганий давач» — це **шум**: власний шум АЦП (квантування, наведення на аналоговий вхід), мерехтіння мережевого світла на 50/100 Гц, теплові флуктуації. Для показу числа воно байдуже, але щойно на цьому тремтливому відліку висить **рішення** (поріг) — тремтіння перетворюється на брязкіт, і про це — наступна задача. Спершу приберемо саме тремтіння.

Ідея боротьби зі випадковим шумом стара як світ і природна: **не вір одному вимірюванню — усередни кілька**. Випадкові відхилення частково гасять одне одного, а справжній рівень лишається. Два робочі способи це зробити на мікроконтролері — **ковзне середнє** й **експоненційний фільтр**; вони не суперники, а два різні компроміси між гладкістю, затримкою й пам'яттю.

![Сірий тремкий сирий відлік і плавна зелена лінія після експоненційного фільтра; фільтр згладжує шум, але з невеликою затримкою слідує за справжньою сходинкою освітлення](/catalog/sensors/light-sound/ky-018-photoresistor/img/smoothing.svg)

*Той самий сигнал двічі: сірим — сирий `analogRead`, що тремтить від шуму АЦП; зеленим — після фільтра. Справжнє світло стрибнуло сходинкою посередині; фільтр доходить до нового рівня не миттєво, а за кілька кроків — це і є плата за гладкість.*

**Ковзне середнє** ([про нього — окрема стаття](book:algorithms/moving-average)) тримає буфер з останніх N відліків і видає їхнє середнє, з кожним новим відліком зсуваючи вікно. Просто й наочно, але коштує N комірок пам'яті й трохи бухгалтерії з кільцевим буфером. Ощадливий варіант («ковзне без буфера») тримає лише **суму**: додав новий відлік, відняв найдавніший.

**Експоненційний фільтр** (він же експоненційно зважене середнє, EMA; математично — найпростіший [БІХ-фільтр першого порядку](book:algorithms/iir-filter)) робить те саме дешевше й без буфера взагалі. Він тримає **одне** число — поточну згладжену оцінку — і з кожним новим відліком трохи підтягує її до нового значення:

```
y ← y + α · (нове − y)          0 < α ≤ 1
```

Прочитай цей рядок як фізику, а не формулу. `нове − y` — це наскільки новий відлік розійшовся з нашою поточною оцінкою; ми зсуваємо оцінку в бік нового **не повністю, а на частку α**. Малий α (скажімо, 0.1) — оцінка лінива, тягнеться до нового повільно: дуже гладко, але з помітною **затримкою** (фільтр «відстає» від різкої зміни світла). Великий α (0.5) — жвава, майже наздоганяє кожен відлік: реагує швидко, але й шуму пропускає більше. `α = 1` — фільтра нема взагалі (`y` = нове). Уся суть фільтра — свідомо вибрати цей компроміс під задачу: для повільної кімнатної освітленості добре лягає α десь 0.1…0.3.

Ось обидва фільтри робочим кодом. Спершу експоненційний — коротший і найуживаніший:

:::tabs
```arduino
const uint8_t PIN_LDR = A0;

float smoothed = 0;                 // згладжена оцінка (float, щоб α працював тонко)
const float ALPHA = 0.2f;           // 0.1 гладше+лінивіше · 0.5 жвавіше+шумніше

void setup() {
  Serial.begin(9600);
  smoothed = analogRead(PIN_LDR);   // засіяти першим відліком, а не нулем
}

void loop() {
  int raw = analogRead(PIN_LDR);
  smoothed += ALPHA * (raw - smoothed);   // y ← y + α·(нове − y)
  Serial.println((int)smoothed);
  delay(20);
}
```

```esp-idf
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "ldr";
#define LDR_CHAN  ADC_CHANNEL_6     // GPIO34 — канал блоку ADC1
#define ALPHA     0.2f              // 0.1 гладше+лінивіше · 0.5 жвавіше+шумніше

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t init = { .unit_id = ADC_UNIT_1 };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, LDR_CHAN, &ch));

  int raw = 0;
  ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &raw));
  float smoothed = raw;             // засіяти першим відліком, а не нулем

  for (;;) {
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &raw));
    smoothed += ALPHA * (raw - smoothed);   // y ← y + α·(нове − y)
    ESP_LOGI(TAG, "%d", (int)smoothed);
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}
```

```stm32
#include "main.h"
#include <stdio.h>

extern ADC_HandleTypeDef  hadc1;    // CubeMX: ADC1, вхід IN0 → PA0, 12 біт
extern UART_HandleTypeDef huart2;   // куди друкуємо замість Serial

#define ALPHA 0.2f                  // 0.1 гладше+лінивіше · 0.5 жвавіше+шумніше

static uint16_t ldr_read(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

void ldr_loop(void) {               // кликати з main() після MX_*_Init()
  float smoothed = ldr_read();      // засіяти першим відліком, а не нулем
  char line[24];
  for (;;) {
    uint16_t raw = ldr_read();
    smoothed += ALPHA * (raw - smoothed);   // y ← y + α·(нове − y)
    int n = snprintf(line, sizeof line, "%d\r\n", (int)smoothed);
    HAL_UART_Transmit(&huart2, (uint8_t *)line, n, HAL_MAX_DELAY);
    HAL_Delay(20);
  }
}
```
:::

Дрібниця, яку легко проґавити й потім довго дивуватися: **засівання** `smoothed` першим відліком ще до входу в цикл — байдуже, зветься те місце `setup()`, початком `app_main()` чи рядком після `MX_ADC1_Init()`. Залиш там нуль — і фільтр перші секунди повзтиме від нуля до реального рівня, даючи брехливо «темні» числа на старті. Засіяв першим виміром — фільтр стартує вже біля правди. І `float` тут не примха: якби `smoothed` був `int`, добуток `α·(нове − y)` для малих різниць округлявся б до нуля, і фільтр «застрягав» би, не доходячи до цілі — знову ж таки пастка цілої арифметики.

Ковзне середнє без буфера, коли хочеться саме його (рівномірне вікно, передбачувана затримка рівно на пів-вікна):

:::tabs
```arduino
const uint8_t PIN_LDR = A0;
const uint8_t N = 16;               // розмір вікна (степінь двійки — зручно для ділення)

int   buf[N];                       // кільцевий буфер відліків
uint8_t idx = 0;                    // куди писати наступний
long  sum = 0;                      // поточна сума вмісту буфера
bool  filled = false;               // чи буфер уже повний

void setup() {
  Serial.begin(9600);
  for (uint8_t i = 0; i < N; i++) buf[i] = 0;
}

int movingAverage(int raw) {
  sum -= buf[idx];                  // викинути найдавніший відлік із суми
  buf[idx] = raw;                   // покласти новий на його місце
  sum += raw;                       // додати новий у суму
  idx = (idx + 1) % N;              // зсунути вказівник по колу
  if (idx == 0) filled = true;
  uint8_t count = filled ? N : idx; // поки не заповнилось — ділимо на реальну кількість
  return count ? (int)(sum / count) : raw;
}

void loop() {
  int raw = analogRead(PIN_LDR);
  Serial.println(movingAverage(raw));
  delay(20);
}
```

```esp-idf
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "ldr";
#define LDR_CHAN  ADC_CHANNEL_6     // GPIO34
#define N         16                // розмір вікна

static int      buf[N];             // кільцевий буфер відліків
static uint8_t  idx = 0;            // куди писати наступний
static long     sum = 0;            // поточна сума вмісту буфера
static bool     filled = false;     // чи буфер уже повний

static int moving_average(int raw) {
  sum -= buf[idx];                  // викинути найдавніший відлік із суми
  buf[idx] = raw;                   // покласти новий на його місце
  sum += raw;                       // додати новий у суму
  idx = (idx + 1) % N;              // зсунути вказівник по колу
  if (idx == 0) filled = true;
  uint8_t count = filled ? N : idx; // поки не заповнилось — ділимо на реальну кількість
  return count ? (int)(sum / count) : raw;
}

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t init = { .unit_id = ADC_UNIT_1 };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, LDR_CHAN, &ch));

  for (;;) {
    int raw = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &raw));
    ESP_LOGI(TAG, "%d", moving_average(raw));
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}
```

```stm32
#include "main.h"
#include <stdio.h>

extern ADC_HandleTypeDef  hadc1;    // ADC1, вхід IN0 → PA0
extern UART_HandleTypeDef huart2;

#define N 16                        // розмір вікна

static int     buf[N];              // кільцевий буфер відліків
static uint8_t idx = 0;             // куди писати наступний
static long    sum = 0;             // поточна сума вмісту буфера
static bool    filled = false;      // чи буфер уже повний

static uint16_t ldr_read(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

static int moving_average(int raw) {
  sum -= buf[idx];                  // викинути найдавніший відлік із суми
  buf[idx] = raw;                   // покласти новий на його місце
  sum += raw;                       // додати новий у суму
  idx = (idx + 1) % N;              // зсунути вказівник по колу
  if (idx == 0) filled = true;
  uint8_t count = filled ? N : idx; // поки не заповнилось — ділимо на реальну кількість
  return count ? (int)(sum / count) : raw;
}

void ldr_loop(void) {               // кликати з main() після MX_*_Init()
  char line[24];
  for (;;) {
    int raw = ldr_read();
    int n = snprintf(line, sizeof line, "%d\r\n", moving_average(raw));
    HAL_UART_Transmit(&huart2, (uint8_t *)line, n, HAL_MAX_DELAY);
    HAL_Delay(20);
  }
}
```
:::

Ключова ідея тут — що ми **не пересумовуємо** весь буфер щоразу (це коштувало б N дій на кожен відлік), а тримаємо `sum` і правимо її двома операціями: мінус найдавніший, плюс найновіший. Це і робить «ковзне» дешевим — робота стала (O(1)), скільки б не було вікно. Прапорець `filled` і `count` дбають про чесний старт: поки буфер не набрався, ділимо на скільки реально є, а не на N (інакше перші відліки занижені порожніми нулями). Обери один із двох фільтрів під задачу: EMA — коли треба дешево й без буфера, ковзне — коли треба точно передбачувана затримка й рівний внесок кожного відліку. Глибше про те, [чому будь-яке згладжування неминуче додає затримку](book:algorithms/smoothing-vs-lag), — в окремій замітці; для KY-018, давача й так повільного, ця затримка зазвичай губиться на тлі власної інерції LDR.

## Задача четверта: стійке рішення. Поріг із гістерезисом

Тепер найголовніше практичне — прийняти рішення «темно / світло» так, щоб воно **не брязкотіло**. Наївний поріг («темно, якщо відлік нижчий за 300») має підступну ваду рівно там, де він найпотрібніший, — **на межі**. Коли освітлення топчеться біля самого порогу (справжні сутінки, тінь від хмари, людина пройшла повз лампу), відлік — навіть згладжений — час від часу перетинає поріг то вгору, то вниз. І прив'язане до нього світло починає нервово блимати ввімк-вимк по кілька разів: не тому, що надворі щось миготить, а тому, що ми поставили різке рішення на плавну величину коло самого краю.

Ліки — **гістерезис**: розвести ввімкнення й вимкнення на **два різні пороги** й лишити між ними «мертву зону», у якій стан не міняється взагалі. Умикаємо світло, коли стало по-справжньому темно (відлік упав нижче **нижнього** порогу); вимикаємо не тоді, щойно відлік ледь переліз назад, а аж коли стало помітно світліше (піднявся вище **верхнього** порогу). Поки відлік гуляє в зазорі між порогами — стан просто тримається, який був. Тремтіння на межі більше нікого не перемикає, бо будь-яка з двох меж від поточного стану далеко.

![Крива освітленості, що плавно темніє з дрібним тремтінням; два штрихові пороги — вищий на вимкнення, нижчий на ввімкнення — і жовта мертва зона між ними, де стан не змінюється](/catalog/sensors/light-sound/ky-018-photoresistor/img/hysteresis.svg)

*Освітленість повільно спадає, дрібно тремтячи. З одним порогом кожен перетин коло краю смикав би світло. З двома — стан міняється лише на дальній межі: увімкнули, аж коли відлік провалився під нижній поріг; назад вимкне тільки підйом вище верхнього. Тремтіння в жовтій зоні нікого не перемикає.*

У коді гістерезис — це буквально кілька рядків, і головна їх ідея: **рішення залежить не лише від відліку, а й від поточного стану**. Той самий відлік у «мертвій зоні» лишає світло ввімкненим, якщо воно вже було ввімкнене, і вимкненим, якщо було вимкнене:

:::tabs
```arduino
const uint8_t PIN_LDR = A0;
const uint8_t PIN_LED = 13;

const int DARK_ON  = 300;   // темніше цього → УВІМКНУТИ (нижній поріг)
const int LIGHT_OFF = 400;  // світліше цього → ВИМКНУТИ (верхній поріг)

bool lampOn = false;        // поточний стан — частина рішення!

void setup() {
  pinMode(PIN_LED, OUTPUT);
}

void loop() {
  int light = analogRead(PIN_LDR);   // (краще — уже згладжений; див. збірку нижче)

  if (!lampOn && light < DARK_ON)      lampOn = true;    // було світло, стало темно
  else if (lampOn && light > LIGHT_OFF) lampOn = false;  // було темно, стало світло
  // якщо відлік між порогами — жодна умова не спрацює, стан лишається

  digitalWrite(PIN_LED, lampOn ? HIGH : LOW);
  delay(50);
}
```

```esp-idf
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LDR_CHAN   ADC_CHANNEL_6    // GPIO34
#define PIN_LED    GPIO_NUM_2

#define DARK_ON    1200   // темніше цього → УВІМКНУТИ (нижній поріг, 12 біт)
#define LIGHT_OFF  1600   // світліше цього → ВИМКНУТИ (верхній поріг)

void app_main(void) {
  gpio_config_t io = { .pin_bit_mask = 1ULL << PIN_LED, .mode = GPIO_MODE_OUTPUT };
  ESP_ERROR_CHECK(gpio_config(&io));

  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t init = { .unit_id = ADC_UNIT_1 };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, LDR_CHAN, &ch));

  bool lamp_on = false;             // поточний стан — частина рішення!
  for (;;) {
    int light = 0;                  // (краще — уже згладжений; див. збірку нижче)
    ESP_ERROR_CHECK(adc_oneshot_read(adc1, LDR_CHAN, &light));

    if (!lamp_on && light < DARK_ON)       lamp_on = true;   // було світло, стало темно
    else if (lamp_on && light > LIGHT_OFF) lamp_on = false;  // було темно, стало світло
    // якщо відлік між порогами — жодна умова не спрацює, стан лишається

    gpio_set_level(PIN_LED, lamp_on);
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}
```

```stm32
#include "main.h"

extern ADC_HandleTypeDef hadc1;     // ADC1, вхід IN0 → PA0, 12 біт

#define DARK_ON    1200   // темніше цього → УВІМКНУТИ (нижній поріг, 12 біт)
#define LIGHT_OFF  1600   // світліше цього → ВИМКНУТИ (верхній поріг)

static uint16_t ldr_read(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

void lamp_loop(void) {              // кликати з main() після MX_*_Init()
  bool lamp_on = false;             // поточний стан — частина рішення!
  for (;;) {
    uint16_t light = ldr_read();    // (краще — уже згладжений; див. збірку нижче)

    if (!lamp_on && light < DARK_ON)       lamp_on = true;   // було світло, стало темно
    else if (lamp_on && light > LIGHT_OFF) lamp_on = false;  // було темно, стало світло
    // якщо відлік між порогами — жодна умова не спрацює, стан лишається

    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin,
                      lamp_on ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_Delay(50);
  }
}
```
:::

Уся магія — у двох умовах, і кожна дивиться **і** на відлік, **і** на стан. `!lampOn && light < DARK_ON` — умикаємо, тільки якщо зараз вимкнено **й** стало по-справжньому темно. `lampOn && light > LIGHT_OFF` — вимикаємо, тільки якщо зараз увімкнено **й** стало помітно світло. Коли відлік у зазорі `DARK_ON..LIGHT_OFF`, жодна умова не істинна — і `lampOn` лишається незмінним. Ширина зазору (тут 100 одиниць) — це запас стійкості: вужчий зазор чутливіший, але гірше гасить тремтіння; ширший стійкіший, але «тупіший» на справжні повільні зміни. Підбирають його під розмах шуму: зазор має бути помітно **більшим** за амплітуду тремтіння відліку, інакше шум усе одно перестрибне обидві межі.

> 🔧 **Навіщо це.** Пара «згладжування + гістерезис» — це стандартний рецепт перетворення будь-якого шумного аналогового давача на надійний дискретний сигнал, і він далеко за межами KY-018: так роблять термостати (не вмикати й вимикати нагрів щосекунди коло уставки), давачі наближення, детектори рівня, тригери Шмітта в самому залізі. Згладжування прибирає **швидке** тремтіння (шум АЦП), гістерезис прибирає **повільне** гуляння коло порогу (сутінки). Одне без одного кульгає: гладкий сигнал усе одно перетне єдиний поріг на повільному спаді, а гістерезис на негладкому сигналі мусив би мати величезний зазор, щоб перекрити весь шум. Разом вони дають рішення, якому можна довірити реле. Той самий принцип двопорогового перемикання лежить в основі [гістерезису як фізичного явища в давачах](book:electronics/drift-hysteresis-noise).

## Збірка: маленька бібліотека давача, однакова скрізь

Розкидані фрагменти зведімо в одне — об'єкт давача `LightSensor`, який інкапсулює калібрування, згладжування, перерахунок у відсотки й поріг із гістерезисом. Це вже не «приклад заради демонстрації», а те, що не соромно покласти в реальний проєкт: увесь стан давача сидить усередині, назовні — кілька зрозумілих операцій. Логіка одна на всі три середовища, різниться лише спосіб її записати: в Arduino це природно лягає в клас C++, в ESP-IDF і STM32 HAL — у структуру стану плюс кілька функцій над нею, як там і прийнято. Єдину справжню відмінність заліза — розрядність АЦП — усюди винесено в одне число, задане під час налаштування.

:::tabs
```arduino
class LightSensor {
  uint8_t pin;
  int     rawMin, rawMax;     // межі власного діапазону (калібрування)
  float   smoothed;           // згладжена оцінка (EMA)
  float   alpha;              // сила фільтра 0..1
  bool    dark;               // поточний стан (для гістерезису)
  int     onThresh, offThresh;// пороги у ВІДСОТКАХ діапазону

public:
  LightSensor(uint8_t p, float a = 0.2f, int onPct = 30, int offPct = 45)
    : pin(p), rawMin(0), rawMax(0), smoothed(0),
      alpha(a), dark(false), onThresh(onPct), offThresh(offPct) {}

  void begin(int fullScale) {           // fullScale: 1023 для Uno, 4095 для ESP32
    rawMin = fullScale;                 // «перевернуті» старти під пошук min/max
    rawMax = 0;
    smoothed = analogRead(pin);         // засіяти фільтр першим відліком
  }

  // покрутіть освітлення протягом seconds — клас зловить ваші крайнощі
  void calibrate(uint16_t seconds) {
    uint32_t until = millis() + (uint32_t)seconds * 1000;
    while (millis() < until) {
      int v = analogRead(pin);
      if (v < rawMin) rawMin = v;
      if (v > rawMax) rawMax = v;
      delay(5);
    }
    if (rawMax - rawMin < 20) {          // діапазон підозріло вузький — калібрування недійсне
      rawMin = 0; rawMax = 0;            // (нуль-нуль = «не відкалібровано»)
    }
  }

  int  update() {                         // кликати щоцикл: оновлює фільтр, вертає сирий згладжений відлік
    int raw = analogRead(pin);
    smoothed += alpha * (raw - smoothed);
    return (int)smoothed;
  }

  uint8_t percent() {                     // 0..100 % у межах власного діапазону
    if (rawMax <= rawMin) return 0;       // ще не відкалібровано
    int s = (int)smoothed;
    if (s <= rawMin) return 0;
    if (s >= rawMax) return 100;
    return (uint32_t)(s - rawMin) * 100 / (rawMax - rawMin);
  }

  bool isDark() {                         // рішення з гістерезисом, у відсотках
    uint8_t p = percent();
    if (!dark && p < onThresh)       dark = true;    // стало темно
    else if (dark && p > offThresh)  dark = false;   // стало світло
    return dark;
  }
};
```

```esp-idf
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct {
  adc_oneshot_unit_handle_t adc;
  adc_channel_t chan;
  int   raw_min, raw_max;     // межі власного діапазону (калібрування)
  float smoothed;             // згладжена оцінка (EMA)
  float alpha;                // сила фільтра 0..1
  bool  dark;                 // поточний стан (для гістерезису)
  int   on_pct, off_pct;      // пороги у ВІДСОТКАХ діапазону
} light_sensor_t;

// full_scale: 4095 для 12-бітного АЦП ESP32
void light_begin(light_sensor_t *s, adc_oneshot_unit_handle_t adc, adc_channel_t chan,
                 int full_scale, float alpha, int on_pct, int off_pct) {
  s->adc = adc;  s->chan = chan;  s->alpha = alpha;
  s->on_pct = on_pct;  s->off_pct = off_pct;  s->dark = false;
  s->raw_min = full_scale;    // «перевернуті» старти під пошук min/max
  s->raw_max = 0;
  int raw = 0;
  ESP_ERROR_CHECK(adc_oneshot_read(adc, chan, &raw));
  s->smoothed = raw;          // засіяти фільтр першим відліком
}

// покрутіть освітлення протягом seconds — функція зловить ваші крайнощі
void light_calibrate(light_sensor_t *s, uint16_t seconds) {
  TickType_t until = xTaskGetTickCount() + pdMS_TO_TICKS(seconds * 1000);
  while (xTaskGetTickCount() < until) {
    int v = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(s->adc, s->chan, &v));
    if (v < s->raw_min) s->raw_min = v;
    if (v > s->raw_max) s->raw_max = v;
    vTaskDelay(pdMS_TO_TICKS(5));
  }
  if (s->raw_max - s->raw_min < 20) {   // діапазон підозріло вузький — калібрування недійсне
    s->raw_min = 0;  s->raw_max = 0;    // (нуль-нуль = «не відкалібровано»)
  }
}

int light_update(light_sensor_t *s) {   // кликати щоцикл: оновлює фільтр
  int raw = 0;
  ESP_ERROR_CHECK(adc_oneshot_read(s->adc, s->chan, &raw));
  s->smoothed += s->alpha * (raw - s->smoothed);
  return (int)s->smoothed;
}

uint8_t light_percent(const light_sensor_t *s) {  // 0..100 % власного діапазону
  if (s->raw_max <= s->raw_min) return 0;         // ще не відкалібровано
  int v = (int)s->smoothed;
  if (v <= s->raw_min) return 0;
  if (v >= s->raw_max) return 100;
  return (uint32_t)(v - s->raw_min) * 100 / (s->raw_max - s->raw_min);
}

bool light_is_dark(light_sensor_t *s) {           // рішення з гістерезисом, у відсотках
  uint8_t p = light_percent(s);
  if (!s->dark && p < s->on_pct)       s->dark = true;    // стало темно
  else if (s->dark && p > s->off_pct)  s->dark = false;   // стало світло
  return s->dark;
}
```

```stm32
#include "main.h"
#include <stdbool.h>

typedef struct {
  ADC_HandleTypeDef *adc;
  int   raw_min, raw_max;     // межі власного діапазону (калібрування)
  float smoothed;             // згладжена оцінка (EMA)
  float alpha;                // сила фільтра 0..1
  bool  dark;                 // поточний стан (для гістерезису)
  int   on_pct, off_pct;      // пороги у ВІДСОТКАХ діапазону
} light_sensor_t;

static uint16_t light_raw(light_sensor_t *s) {
  HAL_ADC_Start(s->adc);
  HAL_ADC_PollForConversion(s->adc, 10);
  uint16_t v = HAL_ADC_GetValue(s->adc);
  HAL_ADC_Stop(s->adc);
  return v;
}

// full_scale: 4095 для 12-бітного АЦП (типове для STM32), 1023 для 10-бітного режиму
void light_begin(light_sensor_t *s, ADC_HandleTypeDef *adc,
                 int full_scale, float alpha, int on_pct, int off_pct) {
  s->adc = adc;  s->alpha = alpha;
  s->on_pct = on_pct;  s->off_pct = off_pct;  s->dark = false;
  s->raw_min = full_scale;    // «перевернуті» старти під пошук min/max
  s->raw_max = 0;
  s->smoothed = light_raw(s); // засіяти фільтр першим відліком
}

// покрутіть освітлення протягом seconds — функція зловить ваші крайнощі
void light_calibrate(light_sensor_t *s, uint16_t seconds) {
  uint32_t until = HAL_GetTick() + (uint32_t)seconds * 1000;
  while (HAL_GetTick() < until) {
    int v = light_raw(s);
    if (v < s->raw_min) s->raw_min = v;
    if (v > s->raw_max) s->raw_max = v;
    HAL_Delay(5);
  }
  if (s->raw_max - s->raw_min < 20) {   // діапазон підозріло вузький — калібрування недійсне
    s->raw_min = 0;  s->raw_max = 0;    // (нуль-нуль = «не відкалібровано»)
  }
}

int light_update(light_sensor_t *s) {   // кликати щоцикл: оновлює фільтр
  int raw = light_raw(s);
  s->smoothed += s->alpha * (raw - s->smoothed);
  return (int)s->smoothed;
}

uint8_t light_percent(const light_sensor_t *s) {  // 0..100 % власного діапазону
  if (s->raw_max <= s->raw_min) return 0;         // ще не відкалібровано
  int v = (int)s->smoothed;
  if (v <= s->raw_min) return 0;
  if (v >= s->raw_max) return 100;
  return (uint32_t)(v - s->raw_min) * 100 / (s->raw_max - s->raw_min);
}

bool light_is_dark(light_sensor_t *s) {           // рішення з гістерезисом, у відсотках
  uint8_t p = light_percent(s);
  if (!s->dark && p < s->on_pct)       s->dark = true;    // стало темно
  else if (s->dark && p > s->off_pct)  s->dark = false;   // стало світло
  return s->dark;
}
```
:::

Чому пороги гістерезису тепер у **відсотках**, а не в сирих одиницях? Бо після калібрування відсоток осмислений і **переносний у часі**: «умикати темніше 30 %, вимикати світліше 45 %» лишається правдою й уранці, і ввечері, бо межі діапазону вимірюються заново, а не хардкодяться. Сирий поріг «300» такої стійкості не має — він прив'язаний до конкретного освітлення миті, коли його підбирали. Це прямий плід калібрування: воно окупається саме тут, роблячи логіку незалежною від абсолютних чисел АЦП.

Використання скрізь одне: налаштувати вхід, віддати давачу повну шкалу свого АЦП, відкалібруватися — і далі щоцикл питати відсоток та рішення. Перша вкладка — **Arduino Uno** (10-бітний АЦП → повна шкала 1023), поруч те саме на ESP-IDF і STM32 HAL, де шкала вже 4095:

:::tabs
```arduino
LightSensor sensor(A0, 0.2f, 30, 45);   // пін A0, α=0.2, пороги 30/45 %

void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  sensor.begin(1023);                   // 10-бітний АЦП Uno
  Serial.println("Калібрування: 5 с крутіть освітлення...");
  sensor.calibrate(5);
}

void loop() {
  sensor.update();                      // оновити фільтр
  uint8_t pct = sensor.percent();
  bool dark = sensor.isDark();
  digitalWrite(13, dark ? HIGH : LOW);  // вбудований світлодіод у темряві
  Serial.print("яскравість "); Serial.print(pct); Serial.print(" %  ");
  Serial.println(dark ? "ТЕМНО" : "світло");
  delay(50);
}
```

```esp-idf
#include "driver/gpio.h"
#include "esp_log.h"

static const char *TAG = "ldr";
static light_sensor_t sensor;

void app_main(void) {
  adc_oneshot_unit_handle_t adc1;
  adc_oneshot_unit_init_cfg_t init = { .unit_id = ADC_UNIT_1 };   // ADC1 — не свариться з Wi-Fi
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init, &adc1));
  adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, ADC_CHANNEL_6, &ch));  // GPIO34

  gpio_config_t io = { .pin_bit_mask = 1ULL << GPIO_NUM_2, .mode = GPIO_MODE_OUTPUT };
  ESP_ERROR_CHECK(gpio_config(&io));

  light_begin(&sensor, adc1, ADC_CHANNEL_6, 4095, 0.2f, 30, 45);  // 12-бітний АЦП
  ESP_LOGI(TAG, "Калібрування: 5 с крутіть освітлення...");
  light_calibrate(&sensor, 5);

  for (;;) {
    light_update(&sensor);              // оновити фільтр
    uint8_t pct = light_percent(&sensor);
    bool dark = light_is_dark(&sensor);
    gpio_set_level(GPIO_NUM_2, dark);   // світлодіод плати в темряві
    ESP_LOGI(TAG, "яскравість %u %%  %s", pct, dark ? "ТЕМНО" : "світло");
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}
```

```stm32
#include <stdio.h>
#include <string.h>

extern ADC_HandleTypeDef  hadc1;
extern UART_HandleTypeDef huart2;

static light_sensor_t sensor;

static void say(const char *s) {
  HAL_UART_Transmit(&huart2, (uint8_t *)s, strlen(s), HAL_MAX_DELAY);
}

int main(void) {
  HAL_Init();  SystemClock_Config();
  MX_GPIO_Init();  MX_ADC1_Init();  MX_USART2_UART_Init();

  light_begin(&sensor, &hadc1, 4095, 0.2f, 30, 45);   // 12-бітний АЦП
  say("Калібрування: 5 с крутіть освітлення...\r\n");
  light_calibrate(&sensor, 5);

  char line[48];
  for (;;) {
    light_update(&sensor);              // оновити фільтр
    uint8_t pct = light_percent(&sensor);
    bool dark = light_is_dark(&sensor);
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin,       // світлодіод плати в темряві
                      dark ? GPIO_PIN_SET : GPIO_PIN_RESET);
    snprintf(line, sizeof line, "яскравість %u %%  %s\r\n", pct, dark ? "ТЕМНО" : "світло");
    say(line);
    HAL_Delay(50);
  }
}
```
:::

На **ESP32 під Arduino-ядром** різниться рівно один рядок налаштування — `begin(4095)` замість `begin(1023)`, бо АЦП там 12-бітний. Але з піном і самим АЦП ESP32 є принципові тонкощі, повз які не можна пройти, — їм окремий розділ нижче. Скелет же коду ідентичний:

```arduino
LightSensor sensor(34, 0.2f, 30, 45);   // GPIO34 — канал ADC1 (див. розділ про ESP32!)

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);             // 0..4095 (типове для ESP32)
  sensor.begin(4095);                   // 12-бітний АЦП
  sensor.calibrate(5);
}

void loop() {
  sensor.update();
  Serial.printf("яскравість %u %%  %s\n",
                sensor.percent(), sensor.isDark() ? "ТЕМНО" : "світло");
  delay(50);
}
```

Одна логіка, три середовища, різниця — в одному числі повної шкали. Саме заради цього діапазон не «зашитий» усередину давача, а переданий у `begin`: перенесення між платами не мусить чіпати логіку.

## ESP32: чому не будь-який пін і чому «сире» число бреше

На Arduino Uno АЦП простий і чесний: піни A0…A5, 10 біт, майже лінійно, `5·раве/1023 ≈ вольти`. ESP32 дає більше можливостей — і разом з ними більше способів наступити на граблі, специфічні саме для цього кремнію. Три речі треба знати, перш ніж вішати KY-018 на ESP32, інакше код скомпілюється, а поведінка буде дивною.

**Перше й найважче — не всякий пін уміє АЦП, а половина тих, що вміють, свариться з Wi-Fi.** У ESP32 два аналого-цифрові блоки: **ADC1** і **ADC2**. І тут пастка, на якій горить кожен, хто робить давач у пристрої з мережею: **ADC2 фізично захоплюється радіо, щойно вмикається Wi-Fi**. Драйвер Wi-Fi використовує ADC2 для власних потреб, і поки радіо активне, будь-яке читання з ADC2-піна — `analogRead` в Arduino, `adc_oneshot_read` в ESP-IDF — повертає сміття або помилку, не тому, що ти щось зробив не так, а тому, що канал зайнятий. Наслідок буває підступний до божевілля: код чудово працює на столі, поки Wi-Fi вимкнено, і «ламається», щойно пристрій під'єднується до мережі. (Джерело — офіційна документація Espressif: «ADC2 is used by the Wi-Fi driver, therefore the application can only use ADC2 when the Wi-Fi driver has not started».)

Ліки прості: **для давача завжди бери пін із блоку ADC1**. На класичному ESP32 (WROOM/WROVER) канали ADC1 виведені на **GPIO 32, 33, 34, 35, 36, 37, 38, 39** — це вісім ніг, вільних від конфлікту з радіо. Саме тому в прикладах вище стоїть GPIO34. Піни ADC2 (GPIO 0, 2, 4, 12–15, 25–27) лиши для чогось, що не читається одночасно з увімкненим Wi-Fi, — або взагалі не чіпай під аналог, якщо в пристрої є мережа.

```
ADC1 (безпечно з Wi-Fi): GPIO 32 33 34 35 36 37 38 39   ← бери сюди KY-018
ADC2 (конфлікт із Wi-Fi): GPIO 0 2 4 12 13 14 15 25 26 27  ← НЕ для давача в мережевому пристрої
```

Дрібний, але корисний нюанс: GPIO 34–39 на класичному ESP32 — **тільки входи**, без внутрішніх підтяжок і без режиму виходу. Для аналогового входу давача це якраз ідеально (нам і треба тільки читати), тож вони — природний перший вибір під KY-018.

**Друге — 12 біт, тобто 0…4095.** Це вже враховано в коді (`begin(4095)`, `analogReadResolution(12)`), але варто розуміти наслідок: та сама зміна світла дає на ESP32 у чотири рази більший розмах числа, ніж на Uno (4095 проти 1023). Тому **абсолютні** сирі пороги між платами не переносяться взагалі — те, що на Uno було «300», на ESP32 приблизно «1200». Це ще один аргумент за пороги у **відсотках**: вони переживають і зміну плати, бо рахуються від власного відкаліброваного діапазону, а не від абсолютної шкали.

**Третє — ADC ESP32 нелінійний, і «сире × константа» бреше.** У Uno перерахунок відліку у вольти майже точний. У ESP32 — ні: його АЦП помітно нелінійний, надто **по краях** діапазону (близько 0 і близько максимуму крива «завалюється»), і має розкид від чипа до чипа. Причина — в тому, як влаштований вхід: щоб читати аж до ~3.3 В, перед АЦП стоїть **атенюатор** (послаблювач), і його характеристика нелінійна. За замовчуванням Arduino-ядро ставить повну атенюацію (`ADC_11db`), що й дає діапазон приблизно 0…3.3 В; в ESP-IDF її задають явно в конфігурації каналу. Виглядає це так:

:::tabs
```arduino
analogSetPinAttenuation(34, ADC_11db);   // повна атенюація: діапазон ~0..3.3 В (типове)
```

```esp-idf
adc_oneshot_chan_cfg_t ch = {
  .atten    = ADC_ATTEN_DB_12,   // повна атенюація: ~0..3.3 В (у IDF до 5.2 звалася DB_11)
  .bitwidth = ADC_BITWIDTH_12,
};
ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, ADC_CHANNEL_6, &ch));  // GPIO34
```
:::

Менша атенюація (`ADC_0db`, `ADC_2_5db`, `ADC_6db`) звужує вимірюваний діапазон угорі — і тоді «яскраве» світло впреться в стелю раніше й читатиметься як 4095, «обрізавши» верх шкали. Для KY-018, де нам треба весь розмах від темряви до світла, лиши повну (`ADC_11db`) — вона тут якраз доречна.

Чи заважає нелінійність нашому завданню? Для **відносної** яскравості (відсотки, темніше/світліше, поріг) — майже ні: калібрування вимірює реальні межі *разом* з усіма викривленнями входу, а гістерезис працює з відсотками, тож абсолютна лінійність не потрібна. Нелінійність кусає лише тоді, коли з відліку хочуть **вольти чи люкси**. Якщо це справді треба — не множ сире число на константу вручну (це і є та «брехня»), а бери калібрований шлях: **заводське калібрування чипа**, записане в eFuse на виробництві, дає напругу в мілівольтах чесніше за будь-яку формулу. Arduino-ядро ховає його за одним викликом, ESP-IDF просить спершу створити схему калібрування:

:::tabs
```arduino
int mv = analogReadMilliVolts(34);   // калібровані мілівольти замість сире·константа
```

```esp-idf
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

adc_cali_handle_t cali;
adc_cali_line_fitting_config_t cfg = {
  .unit_id  = ADC_UNIT_1,
  .atten    = ADC_ATTEN_DB_12,
  .bitwidth = ADC_BITWIDTH_12,
};
ESP_ERROR_CHECK(adc_cali_create_scheme_line_fitting(&cfg, &cali));

int raw = 0, mv = 0;
ESP_ERROR_CHECK(adc_oneshot_read(adc1, ADC_CHANNEL_6, &raw));
ESP_ERROR_CHECK(adc_cali_raw_to_voltage(cali, raw, &mv));   // калібровані мілівольти
```
:::

Але для самого KY-018 напруга на дільнику — не мета: нас цікавить світло, а не вольти на вузлі S. Тож у нашій «бібліотеці давача» ми свідомо лишаємось у відсотках власного діапазону — там нелінійність АЦП розчиняється в калібруванні й ні на що не впливає. Глибше про 12-бітний АЦП ESP32, атенюацію й калібрування — у [статті про АЦП](book:electronics/adc); тут досить трьох правил: **пін бери з ADC1**, **шкала 0…4095**, а **вольти (якщо треба) — через заводське калібрування (`analogReadMilliVolts` чи `adc_cali_raw_to_voltage`), не множенням**.

## Складність і пастки: де це ламається на живому залізі

Код вище простий; день з'їдають не рядки, а те, чим KY-018 є фізично. Зберімо пастки в одне місце — це і є справжня «документація», якої нема в підписі до платки.

**Різнобій екземплярів — калібруй кожен окремо, поріг не переноси.** Два KY-018 з однієї партії в тій самій кімнаті легко дадуть відліки, що різняться в півтора раза: розкид опору самого LDR великий (це властивість технології, а не брак конкретної платки), плюс допуск сталого резистора 10 кОм. Прямий наслідок для коду: **абсолютний поріг, підібраний на одній платці, на іншій бреше**, і його не можна копіювати наосліп. Саме тому вся ця вставка веде до порогів у **відсотках** над **індивідуальним калібруванням**: кожна платка міряє свій діапазон сама, і «темніше 30 %» стає універсальним твердженням, тоді як «нижче 800» лишається місцевим. Заміняєш давач — перекалібруй; не сподівайся, що збережені сирі межі підійдуть новому екземпляру.

**Інерція LDR — фільтруй помірно, не жди швидкості.** Фоторезистор реагує на зміну світла не миттєво, а за десятки-сотні мілісекунд, ще й по-різному на потемніння і посвітлення (це його власна «пам'ять світла», інерція). Це має два наслідки для коду. Перший приємний: **давач уже сам себе згладжує** — власна повільність LDR гасить найшвидший шум ще до АЦП, тож агресивний цифровий фільтр (дуже малий α, велике вікно) тут зайвий і лише додасть непотрібної затримки поверх фізичної. Помірного α (0.2…0.3) досить. Другий обмежувальний: **не став KY-018 туди, де світло змінюється швидко** — ловити спалахи, рахувати оберти по відбитій мітці, приймати ІЧ-пульт. Жоден фільтр не поверне швидкості давачу, який фізично не встигає; там потрібен фотодіод чи фототранзистор, а не LDR. Пам'ятай межу: KY-018 — для **повільного** світла (день/ніч, «стало темніше в кімнаті»), і код мусить поважати цю природу, а не боротися з нею.

**Перенесення порогу між платами — рахуй у частках, не в одиницях.** Той самий код, залитий з Uno на ESP32, читатиме вчетверо більші числа (12 біт проти 10), а «сире × константа» у вольти на ESP32 ще й бреше через нелінійність. Зашитий сирий поріг переживе таку міграцію лише випадково. Ліки ті самі, що й від різнобою екземплярів: **тримай логіку у відсотках відкаліброваного діапазону**, а єдину справжню різницю плат — повну шкалу АЦП — передавай одним числом у `begin(1023)` / `begin(4095)`. Тоді перенесення коду між Uno й ESP32 не чіпає ані порогів, ані фільтра.

**Мережа з'їдає ADC2 — на ESP32 бери ADC1.** Повторю окремо, бо ця пастка коштує найбільше загубленого часу: якщо давач висить на піні блоку **ADC2**, він працюватиме на столі й **замовкне**, щойно ввімкнеться Wi-Fi, — радіо забирає ADC2 собі. Симптом оманливий («усе працювало, поки не додав мережу»), причина не в твоєму коді. Правило: на будь-якому мережевому ESP32-пристрої аналоговий давач — **тільки на ADC1** (GPIO 32–39 на класичному ESP32).

**«Завжди 0 %» або «дике число» — це ціла арифметика, не давач.** Дві найтиповіші програмні пастки перерахунку не мають стосунку до світла взагалі. «Завжди 0 %» (крім самого максимуму) — це **передчасне цілочислове ділення**: поділив, поки чисельник менший за знаменник, отримав 0. Ліки — множити на 100 **першим**. «Дике число» на межі діапазону — це **переповнення `int`**: `4095 · 100` не влазить у 16-бітний `int` Uno. Ліки — рахувати проміжок у `uint32_t`. Обидві пастки ловляться миттєво, коли знаєш, що вони існують, і коштують годину нишпорення, коли ні.

**Не забудь засіяти фільтр і врахувати старт калібрування.** Дві дрібниці старту, що дають «привида» на перших секундах. Незасіяний EMA (`smoothed = 0` замість першого відліку) повзе від нуля вгору — прилад «бачить темряву», якої нема, поки фільтр розганяється. І калібрування, під час якого на очок не потрапило контрасту, дає вузький брехливий діапазон — тому в коді стоїть перевірка `rawMax − rawMin < 20 → недійсно`. Обидва — не про фізику, а про акуратність ініціалізації; але саме на них спотикається «правильний» код, що чомусь бреше перші кілька секунд після ввімкнення.

Ось і вся «складність»: не в синтаксисі фільтрів чи гістерезису, а в поважанні того, чим KY-018 є насправді — повільним, шумним, індивідуальним давачем відносного світла на шумному АЦП. Калібрування дає йому свою систему координат, згладжування прибирає тремтіння АЦП, гістерезис прибирає гуляння на межі, а відсотки роблять пороги переносними в часі й між платами. Тримай ці чотири речі разом — і триногова платка за копійки чесно скаже пристрою, стало ясніше чи темніше, і не збреше й не заблимає на межі.
