# ⚙️ Nano в коді: набір робочих прикладів

Плата в руках — це ще півсправи. Друга половина в тому, щоб змусити її робити те, чого ви хочете, і не наступити на десяток граблів, кожні з яких коштують вечора. Тут зібрано ті виклики, з яких складається майже будь-який проєкт на Nano: поговорити з комп'ютером по `Serial`, прочитати кнопку й потенціометр, видати «майже аналоговий» рівень через ШІМ, витягти число з давача по I²C та по SPI, крутити кілька справ одночасно без `delay`, і, нарешті, заснути, щоб дожити на батарейці до ранку. Кожен блок збудований однаково: **задача → ідея → робочий код → де воно вкусить**. Код — справжній, компільований під ATmega328P, а не начерк «десь так».

Одне спільне попередження, яке стосується всього подальшого. У Nano лише **2 КБ SRAM** — оперативної пам'яті, у якій живуть усі змінні, буфери й стек. Це та стеля, об яку розбиваються найзагадковіші баги: плата раптом перезавантажується, `Serial` виводить кракозябри, давач «замовкає» — а насправді просто скінчилася пам'ять і стек наліз на купу. Тому всюди нижче тексти в лапках загорнуті в `F()`, і чому — розберемо окремо. Тримайте цю цифру в голові: 2048 байтів, і ні байтом більше.

## Serial: як плата говорить із комп'ютером

**Задача.** Вивести на екран комп'ютера числа з давача, а заодно приймати команди назад — увімкнути щось, змінити режим. Це найперше, що роблять на будь-якій платі: без вікна, куди сиплються числа, ви наосліп.

**Ідея.** У ATmega328P є один апаратний UART — вузол, що сам, без участі програми, вистукує байти по лінії `TX` і ловить їх по `RX`. Кожне середовище відчиняє до нього свої двері: Arduino ховає вузол за об'єктом `Serial` (`begin` задає швидкість, `print`/`println` шлють текст, `available`/`read` забирають те, що прийшло), ESP-IDF ставить драйвер `uart_driver_install` і читає `uart_read_bytes`, STM32 HAL дає `HAL_UART_Transmit`/`HAL_UART_Receive`. Дія скрізь та сама, різняться лише імена. Швидкість — це **бод** (baud, на честь Еміля Бодо), кількість символів-станів лінії за секунду; обидва боки мусять домовитися про одне число, інакше замість тексту полізе сміття.

:::tabs
```arduino
void setup() {
    Serial.begin(9600);            // 9600 бод — обидва боки мусять збігтися
    Serial.println(F("Готовий")); // F() тримає рядок у флеші, не в SRAM
}

void loop() {
    // приймання: одна літера-команда
    if (Serial.available() > 0) {      // у буфері є хоч байт?
        char cmd = Serial.read();
        if (cmd == '1') digitalWrite(LED_BUILTIN, HIGH);
        if (cmd == '0') digitalWrite(LED_BUILTIN, LOW);
    }

    // передавання: показник щосекунди
    static unsigned long last = 0;
    if (millis() - last >= 1000) {
        last = millis();
        int v = analogRead(A0);
        Serial.print(F("A0 = "));
        Serial.println(v);             // число + перехід рядка
    }
}
```
```esp-idf
#include "driver/uart.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "esp_log.h"
#include "esp_timer.h"

static const char *TAG = "app";
#define LED GPIO_NUM_2

void app_main(void) {
    const uart_config_t cfg = {
        .baud_rate  = 9600,             // 9600 бод — обидва боки мусять збігтися
        .data_bits  = UART_DATA_8_BITS,
        .parity     = UART_PARITY_DISABLE,
        .stop_bits  = UART_STOP_BITS_1,
        .flow_ctrl  = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    ESP_ERROR_CHECK(uart_driver_install(UART_NUM_0, 256, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(UART_NUM_0, &cfg));
    gpio_set_direction(LED, GPIO_MODE_OUTPUT);
    ESP_LOGI(TAG, "Готовий");           // сталі рядки й так лежать у флеші

    int64_t last = 0;
    while (1) {
        uint8_t cmd;                    // приймання: одна літера-команда
        if (uart_read_bytes(UART_NUM_0, &cmd, 1, pdMS_TO_TICKS(10)) == 1) {
            if (cmd == '1') gpio_set_level(LED, 1);
            if (cmd == '0') gpio_set_level(LED, 0);
        }
        int64_t now = esp_timer_get_time();   // мікросекунди від старту
        if (now - last >= 1000000) {          // передавання: показник щосекунди
            last = now;
            ESP_LOGI(TAG, "лічильник = %d", (int)(now / 1000000));
        }
    }
}
```
```stm32
#include "stm32f4xx_hal.h"
#include <stdio.h>
#include <string.h>

extern UART_HandleTypeDef huart2;   // 9600 бод виставлено в CubeMX

static void tx(const char *s) {     // передати рядок і дочекатися кінця
    HAL_UART_Transmit(&huart2, (uint8_t *)s, strlen(s), HAL_MAX_DELAY);
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();
    tx("Готовий\r\n");

    uint32_t last = 0;
    while (1) {
        uint8_t cmd;                // приймання: одна літера-команда
        if (HAL_UART_Receive(&huart2, &cmd, 1, 10) == HAL_OK) {
            if (cmd == '1') HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
            if (cmd == '0') HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
        }
        uint32_t now = HAL_GetTick();   // мілісекунди від старту
        if (now - last >= 1000) {       // передавання: показник щосекунди
            last = now;
            char line[32];
            snprintf(line, sizeof line, "лічильник = %lu\r\n",
                     (unsigned long)(now / 1000));
            tx(line);
        }
    }
}
```
:::

Про швидкості. Класичні значення — 9600, 57600, 115200 бод. Менше — надійніше на довгих чи брудних лініях; більше — швидше сиплються дані, але зростає ризик поодиноких помилок. Для налагодження 9600 вистачає з головою; коли треба перекачати багато (лог на кожен цикл), беруть 115200. Головне — **виставити те саме число у моніторі порту**: якщо плата шле на 115200, а монітор слухає на 9600, ви побачите рядок безглуздих символів. Це, до речі, перша підозра, коли «Serial показує кракозябри»: не збіглася швидкість.

**Пастки.**

*Виводи `D0` і `D1` зайняті.* Апаратний UART фізично сидить на `D0` (`RX`) та `D1` (`TX`). Той самий USB-міст, що заливає скетч, теж висить на цих лініях. Тому: (1) не чіпляйте на `D0`/`D1` сторонні дроти — вони конфліктнуть із заливкою й із `Serial`; (2) якщо ви **все ж** щось туди повісили, заливка може обірватися, бо ваш пристрій «перебиває» програматор — від'єднайте його на час прошивки. Правило просте: `D0`/`D1` — службові, лишіть їх у спокої, а для власного UART до іншого пристрою беріть `SoftwareSerial` на будь-якій іншій парі виводів.

*Авто-скид на відкриття порту.* Коли комп'ютер відкриває послідовний порт, лінія `DTR` через конденсатор смикає `RESET`, і плата **перезавантажується** — це той самий авто-скид, що дає заливати без кнопки. Наслідок, який лякає новачків: щойно ви відкриваєте монітор порту, скетч стартує спочатку, і перші рядки, надіслані одразу в `setup()`, можна не побачити — вони пішли, поки монітор ще під'єднувався. Якщо треба гарантовано побачити стартове повідомлення, додайте на початку `setup()` невелику паузу або дочекайтеся, доки `Serial` готовий.

*`F()` рятує пам'ять.* Кожен `Serial.print("текст")` без `F()` кладе цей рядок **у SRAM** — назавжди, на весь час роботи. Десяток діагностичних рядків — і сотні байтів дефіцитної пам'яті з'їдено дарма. `F("текст")` лишає літери у флеш-пам'яті (її 32 КБ, багато), а бере звідти по одній лише в мить друку. Загортайте у `F()` **кожен** сталий текст — це найдешевший спосіб не впертися в стелю SRAM.

## Цифровий вхід і вихід: кнопка з підтяжкою

**Задача.** Прочитати кнопку (натиснута чи ні) і засвітити світлодіод. Основа основ, але саме тут ховається класичний баг «кнопка спрацьовує сама собою».

**Ідея.** Будь-який вивід МК має два основні режими. У режимі виходу ви ним **керуєте**: `HIGH` подає на вивід напругу живлення ядра (у Nano це ~5 В, у ESP32 чи STM32 — 3.3 В), `LOW` — 0 В; в Arduino це `digitalWrite(pin, HIGH)`, в ESP-IDF `gpio_set_level`, у STM32 HAL `HAL_GPIO_WritePin`. У режимі входу ви вивід **читаєте**: `digitalRead(pin)` (відповідно `gpio_get_level`, `HAL_GPIO_ReadPin`) каже, який на ньому рівень. Проблема з простим входом у тому, що неприєднаний вивід ні до чого не притягнутий і ловить наводки з повітря — читається то `HIGH`, то `LOW` навмання. Лік — **внутрішня підтяжка**: вбудований у чип резистор, що м'яко притягує вивід до `HIGH`; він є практично в кожному МК. В Arduino його вмикає режим `INPUT_PULLUP`, в ESP-IDF — поле `.pull_up_en` у `gpio_config`, у STM32 — `.Pull = GPIO_PULLUP`. Вішаєте кнопку між виводом і землею — і логіка перевертається: вільний вивід читається `HIGH`, натиснута кнопка притягує до `LOW`.

:::tabs
```arduino
const uint8_t PIN_BTN = 2;      // кнопка між D2 і GND
const uint8_t PIN_LED = 13;     // вбудований світлодіод

void setup() {
    pinMode(PIN_BTN, INPUT_PULLUP);   // вільний стан = HIGH, натиск = LOW
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    bool pressed = (digitalRead(PIN_BTN) == LOW);  // натиснуто = замкнуто на GND
    digitalWrite(PIN_LED, pressed ? HIGH : LOW);
}
```
```esp-idf
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_BTN GPIO_NUM_4      // кнопка між GPIO4 і GND
#define PIN_LED GPIO_NUM_2

void app_main(void) {
    const gpio_config_t btn = {
        .pin_bit_mask = 1ULL << PIN_BTN,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,   // вільний стан = 1, натиск = 0
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&btn));
    gpio_set_direction(PIN_LED, GPIO_MODE_OUTPUT);

    while (1) {
        bool pressed = (gpio_get_level(PIN_BTN) == 0);  // натиснуто = замкнуто на GND
        gpio_set_level(PIN_LED, pressed);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```
```stm32
#include "stm32f4xx_hal.h"

// кнопка між PC13 і GND, світлодіод на PA5
int main(void) {
    HAL_Init(); SystemClock_Config();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef btn = {
        .Pin  = GPIO_PIN_13,
        .Mode = GPIO_MODE_INPUT,
        .Pull = GPIO_PULLUP,              // вільний стан = 1, натиск = 0
    };
    HAL_GPIO_Init(GPIOC, &btn);

    GPIO_InitTypeDef led = {
        .Pin = GPIO_PIN_5, .Mode = GPIO_MODE_OUTPUT_PP,
        .Pull = GPIO_NOPULL, .Speed = GPIO_SPEED_FREQ_LOW,
    };
    HAL_GPIO_Init(GPIOA, &led);

    while (1) {
        // натиснуто = замкнуто на GND
        bool pressed = (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5,
                          pressed ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }
}
```
:::

**Пастки.**

*Без підтяжки вивід «плаває».* Найпоширеніша помилка новачка — `pinMode(PIN_BTN, INPUT)` замість `INPUT_PULLUP` і кнопка без зовнішнього резистора. Плата «бачить» натискання, яких не було, бо вивід ловить наводку від руки, від мережі 50 Гц, від сусіднього дроту. `INPUT_PULLUP` прибирає це одним словом і без жодної зайвої деталі — тому його майже завжди й беруть для кнопок.

*Дребезг контактів.* Механічна кнопка не замикається чисто: у першу мілісекунду контакт кілька разів «дзвенить», і `digitalRead` встигає побачити серію `LOW`–`HIGH`–`LOW`. Якщо ви рахуєте натискання, один натиск порахується за три-п'ять. Найпростіший лік — після зміни стану почекати ~20 мс (не через `delay`, а по `millis`, як нижче) і лише тоді вірити новому значенню.

*`A6` і `A7` — не для кнопок.* На Nano виводи `A6`/`A7` уміють **лише аналогове** читання; `digitalRead` і `INPUT_PULLUP` на них не працюють — усередині чипа там просто немає цих ланок. Кнопку на них не повісити: вона мовчатиме. Це фізична межа саме Nano, і про неї легко забути, бо решта аналогових входів (`A0`–`A5`) цифрове читання підтримують.

## analogRead: виміряти напругу

**Задача.** Прочитати положення потенціометра, яскравість фоторезистора, напругу з давача — усе, що подається плавним рівнем 0–5 В.

**Ідея.** Майже в кожному МК є [аналого-цифровий перетворювач](topic:electronics/adc): він порівнює вхідну напругу з опорною й видає ціле число. Розрядність — властивість конкретного чипа: у ATmega328P перетворювач **десятибітний**, у ESP32 і більшості STM32 — дванадцятибітний. Десять бітів означає діапазон 0…1023: `0` — це 0 В, `1023` — це опорна напруга (за замовчуванням 5 В). Тобто крок одного відліку:

```
крок = Uопор / 1024 = 5.0 / 1024 ≈ 0.0049 В ≈ 4.9 мВ
```

Щоб із сирого відліку дістати вольти, множимо назад:

```
U = відлік · Uопор / 1023
```

:::tabs
```arduino
void setup() {
    Serial.begin(9600);
}

void loop() {
    int raw = analogRead(A0);            // 0..1023
    float volts = raw * 5.0 / 1023.0;    // назад у вольти
    Serial.print(raw);
    Serial.print(F("  ->  "));
    Serial.print(volts, 3);              // три знаки після коми
    Serial.println(F(" В"));
    delay(200);
}
```
```esp-idf
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "adc";

void app_main(void) {
    adc_oneshot_unit_handle_t adc1;
    const adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc1));

    const adc_oneshot_chan_cfg_t ch = {
        .bitwidth = ADC_BITWIDTH_12,     // 12 бітів: 0..4095
        .atten    = ADC_ATTEN_DB_12,     // послаблення входу — стеля близько 3.3 В
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, ADC_CHANNEL_0, &ch));

    while (1) {
        int raw = 0;
        ESP_ERROR_CHECK(adc_oneshot_read(adc1, ADC_CHANNEL_0, &raw));
        float volts = raw * 3.3f / 4095.0f;         // назад у вольти
        ESP_LOGI(TAG, "%d  ->  %.3f В", raw, volts);
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}
```
```stm32
#include "stm32f4xx_hal.h"
#include <stdio.h>

extern ADC_HandleTypeDef hadc1;   // канал і час вибірки виставлено в CubeMX

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_ADC1_Init(); MX_USART2_UART_Init();

    while (1) {
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
            uint32_t raw = HAL_ADC_GetValue(&hadc1);   // 0..4095, 12 бітів
            float volts = raw * 3.3f / 4095.0f;        // назад у вольти
            printf("%lu  ->  %.3f В\r\n", (unsigned long)raw, volts);
        }
        HAL_ADC_Stop(&hadc1);
        HAL_Delay(200);
    }
}
```
:::

Опорну напругу можна змінити функцією `analogReference`. За замовчуванням це `DEFAULT` — живлення 5 В. Є ще `INTERNAL` — вбудоване джерело **1.1 В** саме в ATmega328P: коли ви міряєте маленькі напруги (термопара, слабкий давач), 1.1 В як стеля дає набагато дрібніший крок (1.1 / 1024 ≈ 1.1 мВ) і точніший вимір. Є `EXTERNAL` — коли на вивід `AREF` подано власну опорну напругу.

> 🔧 **Навіщо це.** Тут причаїлася пастка, що псує чип. Якщо ви подали напругу на `AREF` ззовні, але **забули** викликати `analogReference(EXTERNAL)` перед першим `analogRead`, то всередині чипа лишиться підключеним внутрішнє джерело — і воно **зіткнеться** з вашим зовнішнім прямо на виводі `AREF`. Це коротке замикання двох джерел, яке може спалити вхід. Правило: подаєте своє на `AREF` — **першою** дією виставте `analogReference(EXTERNAL)`, і лише потім читайте. І ніколи не подавайте на `AREF` більше за 5 В чи менше за 0 В.

**Пастки.**

*Перше читання після зміни опорної — «брудне».* Коли ви перемкнули `analogReference`, внутрішньому джерелу треба мить устоятися. Перший `analogRead` після зміни може дати хибне число — зробіть один «холостий» вимір і викиньте його.

*Високий опір джерела спотворює вимір.* АЦП усередині має маленький конденсатор, який треба зарядити за час вибірки. Якщо джерело «слабке» (великий вихідний опір — скажімо, дільник із мегаомних резисторів), конденсатор не встигає зарядитися й відлік «пливе» вниз. Лік — або нижчі опори в дільнику (десятки кілоом), або пауза між `analogSettle` й читанням, або кілька читань поспіль (перше «прогріває» вхід).

## analogWrite і ШІМ: майже аналоговий вихід

**Задача.** Плавно регулювати яскравість світлодіода чи швидкість мотора — не «увімк/вимк», а «на скільки».

**Ідея.** Цифровий вивід уміє лише два рівні. Але якщо дуже швидко вмикати й вимикати його — скажімо, 490 разів на секунду — і міняти **частку часу**, коли він увімкнений, то середня потужність вийде будь-якою між 0 і повною. Око не встигає за миготінням і бачить рівну яскравість; мотор через інерцію бачить середній струм. Це **широтно-імпульсна модуляція** (ШІМ, англ. *PWM — pulse-width modulation*): несемо «аналогову» величину шириною імпульсів. Робить це апаратний таймер, і кожне середовище відкриває його по-своєму: в Arduino `analogWrite(pin, duty)` бере `duty` від 0 (завжди вимкнено) до 255 (завжди ввімкнено), 127 — половина часу ввімкнено, тобто ~50 % яскравості; в ESP-IDF ту саму частку задає модуль `LEDC`, у STM32 — регістр порівняння таймера.

:::tabs
```arduino
const uint8_t PIN_LED = 9;   // ~D9 — має апаратний ШІМ

void setup() {
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    // плавне «дихання»: яскравість вгору й вниз
    for (int d = 0; d <= 255; d++) { analogWrite(PIN_LED, d); delay(5); }
    for (int d = 255; d >= 0; d--) { analogWrite(PIN_LED, d); delay(5); }
}
```
```esp-idf
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED 2   // будь-який GPIO: ШІМ розводить матриця, не жорсткі виводи

static void set_duty(int d) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, d);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void app_main(void) {
    const ledc_timer_config_t tm = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .timer_num       = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT,   // 8 бітів: duty 0..255, як у Arduino
        .freq_hz         = 5000,               // частоту обираємо самі
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tm));

    const ledc_channel_config_t ch = {
        .gpio_num = PIN_LED, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel  = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0,
        .duty = 0, .hpoint = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ch));

    while (1) {
        // плавне «дихання»: яскравість вгору й вниз
        for (int d = 0;   d <= 255; d++) { set_duty(d); vTaskDelay(pdMS_TO_TICKS(5)); }
        for (int d = 255; d >= 0;   d--) { set_duty(d); vTaskDelay(pdMS_TO_TICKS(5)); }
    }
}
```
```stm32
#include "stm32f4xx_hal.h"

extern TIM_HandleTypeDef htim2;   // TIM2_CH1 на PA0, ARR = 255 (виставлено в CubeMX)

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM2_Init();
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);

    while (1) {
        // плавне «дихання»: яскравість вгору й вниз; CCR — це і є duty
        for (int d = 0; d <= 255; d++) {
            __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, d);
            HAL_Delay(5);
        }
        for (int d = 255; d >= 0; d--) {
            __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, d);
            HAL_Delay(5);
        }
    }
}
```
:::

**Пастки.**

*ШІМ — лише на позначених `~` виводах.* Апаратний ШІМ на Nano мають **шість** виводів: `D3`, `D5`, `D6`, `D9`, `D10`, `D11` — саме вони помічені тильдою `~` на платі. Викличете `analogWrite` на будь-якому іншому цифровому виводі — він просто клацне в `HIGH` (для `duty ≥ 128`) або `LOW`, без жодного плавного переходу. Тому світлодіод «регулюється ступінчасто» — майже завжди означає, що дріт сидить не на тому виводі.

*Це не справжній аналог.* На виході ШІМ — прямокутні імпульси, а не рівна напруга. Світлодіод чи мотор усереднюють їх самі. Але якщо вам треба **справжня** плавна напруга (керувати підсилювачем, дати опорний рівень), поставте після виводу простий RC-фільтр (резистор + конденсатор), що згладить імпульси до постійного рівня, — або візьміть окремий ЦАП. Голий ШІМ подавати на аналоговий вхід іншої схеми як «напругу» не можна.

*Частота ~490 Гц може бути чутною.* На більшості виводів Nano ШІМ іде на ~490 Гц; на `D5`/`D6` — ~980 Гц. Для світлодіода це невидимо, а от у моторі чи п'єзо-динаміку 490 Гц може віддаватися чутним писком. Це нормально й лікується або вищою частотою (через прямий доступ до таймерів), або фільтром.

## Давач по I²C: два дроти на багатьох

**Задача.** Прочитати число з давача, що спілкується по [шині I²C](topic:communications/i2c-bus) — барометр, годинник реального часу, розширювач виводів. Таких дрібних мікросхем безліч, і всі вони чіпляються на **два спільні** дроти.

**Ідея.** I²C — це дві лінії: `SDA` (дані) і `SCL` (такт). На Nano вони жорстко закріплені за виводами **`A4` (SDA)** і **`A5` (SCL)**. Багато пристроїв висять на цій самій парі, і кожен має свою **адресу** (7-бітове число); ведучий (Nano) називає адресу, і відповідає лише той, кого покликали. У коді все це ховає драйвер шини — в Arduino це бібліотека `Wire` (`Wire.begin()` піднімає шину), в ESP-IDF `i2c_driver_install`, у STM32 HAL — описувач `hi2c`. Далі скрізь та сама транзакція «назви регістр → прочитай байти». Механіка обміну — старт, адреса, підтвердження — розібрана окремо; тут важливо, що читання регістра давача робиться у два кроки: спершу кажемо, який регістр хочемо, тоді забираємо його вміст.

Ось мінімальний, але **чесний** приклад — читаємо байт-ідентифікатор із давача, щоб переконатися, що він узагалі є на шині, і читаємо два байти виміру:

:::tabs
```arduino
#include <Wire.h>

const uint8_t ADDR    = 0x76;   // адреса давача (з даташита)
const uint8_t REG_ID  = 0xD0;   // регістр «хто ти»
const uint8_t REG_OUT = 0xF7;   // старший байт виміру

// прочитати n байтів від регістра reg у buf; true — успіх
bool i2c_read(uint8_t reg, uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(ADDR);
    Wire.write(reg);                          // назвати регістр
    if (Wire.endTransmission(false) != 0)     // повторний старт, без stop
        return false;                         // ніхто не підтвердив адресу
    if (Wire.requestFrom(ADDR, n) != n)       // попросити n байтів
        return false;                         // прийшло менше — збій
    for (uint8_t i = 0; i < n; i++) buf[i] = Wire.read();
    return true;
}

void setup() {
    Serial.begin(9600);
    Wire.begin();                             // A4 = SDA, A5 = SCL

    uint8_t id = 0;
    if (i2c_read(REG_ID, &id, 1))
        Serial.println(id, HEX);              // побачили ID — давач на шині
    else
        Serial.println(F("немає відповіді"));
}

void loop() {
    uint8_t raw[2];
    if (i2c_read(REG_OUT, raw, 2)) {
        int value = (raw[0] << 8) | raw[1];   // старший байт першим
        Serial.println(value);
    }
    delay(500);
}
```
```esp-idf
#include "driver/i2c.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define ADDR    0x76            // адреса давача (з даташита)
#define REG_ID  0xD0            // регістр «хто ти»
#define REG_OUT 0xF7            // старший байт виміру
static const char *TAG = "i2c";

// прочитати n байтів від регістра reg у buf; ESP_OK — успіх
static esp_err_t i2c_read(uint8_t reg, uint8_t *buf, size_t n) {
    // write_read = «назвати регістр → ПОВТОРНИЙ СТАРТ → читати», без stop усередині
    return i2c_master_write_read_device(I2C_NUM_0, ADDR, &reg, 1, buf, n,
                                        pdMS_TO_TICKS(100));
}

void app_main(void) {
    const i2c_config_t cfg = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = 21, .scl_io_num = 22,     // виводи обираємо самі, вони не жорсткі
        .sda_pullup_en = GPIO_PULLUP_ENABLE,     // слабка внутрішня підтяжка
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 100000,
    };
    ESP_ERROR_CHECK(i2c_param_config(I2C_NUM_0, &cfg));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0));

    uint8_t id = 0;
    if (i2c_read(REG_ID, &id, 1) == ESP_OK) ESP_LOGI(TAG, "ID = %02X", id);
    else                                    ESP_LOGE(TAG, "немає відповіді");

    while (1) {
        uint8_t raw[2];
        if (i2c_read(REG_OUT, raw, 2) == ESP_OK)
            ESP_LOGI(TAG, "%d", (raw[0] << 8) | raw[1]);   // старший байт першим
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
```
```stm32
#include "stm32f4xx_hal.h"
#include <stdio.h>

extern I2C_HandleTypeDef hi2c1;

#define ADDR    (0x76 << 1)     // HAL бере 8-бітову адресу: 7 бітів зсунуті вліво
#define REG_ID  0xD0            // регістр «хто ти»
#define REG_OUT 0xF7            // старший байт виміру

// Mem_Read сам робить «назвати регістр → повторний старт → читати»
static HAL_StatusTypeDef i2c_read(uint8_t reg, uint8_t *buf, uint16_t n) {
    return HAL_I2C_Mem_Read(&hi2c1, ADDR, reg, I2C_MEMADD_SIZE_8BIT, buf, n, 100);
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_I2C1_Init(); MX_USART2_UART_Init();

    uint8_t id = 0;
    if (i2c_read(REG_ID, &id, 1) == HAL_OK) printf("ID = %02X\r\n", id);
    else                                    printf("немає відповіді\r\n");

    while (1) {
        uint8_t raw[2];
        if (i2c_read(REG_OUT, raw, 2) == HAL_OK)
            printf("%d\r\n", (raw[0] << 8) | raw[1]);   // старший байт першим
        HAL_Delay(500);
    }
}
```
:::

Ключова деталь — `Wire.endTransmission(false)`: аргумент `false` каже «не відпускай шину, дай **повторний старт**». Без нього між «назвати регістр» і «прочитати» встромиться стоп, давач забуде, який регістр ви питали, і віддасть не те. Друга деталь — перевірка `requestFrom(...) != n`: якщо прийшло менше байтів, ніж просили (відвалився дріт, слабкі підтяжки), чесний код мусить це помітити, а не покласти в буфер сміття.

**Пастки.**

*Немає підтягувальних резисторів.* Лінії I²C працюють за принципом «відкритий колектор»: пристрої тільки притягують їх донизу, а вгору лінію тягнуть **зовнішні** резистори (типово 4.7 кОм на `SDA` та `SCL` до 5 В). Багато готових модулів мають ці резистори на собі — тоді нічого не треба. Але гола мікросхема без них на шині **мовчить**: без підтяжок лінія не може стати `HIGH`, і обмін не починається. Симптом — `endTransmission` завжди повертає помилку. Перш ніж винити код, перевірте, чи є підтяжки.

*5 В проти 3.3-вольтового давача.* Nano тягне лінії I²C до **5 В**. Багато сучасних давачів живляться від 3.3 В і не терплять 5 В на своїх виводах — можна спалити. Між 5-вольтовим Nano й 3.3-вольтовим давачем ставлять **перетворювач рівнів** для лінії I²C. Не покладайтеся тут і на пін `3V3` самого Nano як на живлення давача: на USB-C-версії з мостом CH340 він слабкий і просяде під навантаженням.

*Не той порядок байтів.* Вимір рідко влазить в один байт; давач ділить його на старший і молодший. Один давач кладе старший першим, інший — навпаки. Переплутаєте — число стрибатиме безглуздо, хоча шина працює. Порядок завжди звіряйте за даташитом конкретного чипа.

## Давач по SPI: швидко й на чотирьох дротах

**Задача.** Поговорити з пристроєм, якому мало I²C: SD-картою, дисплеєм, радіомодулем, швидким АЦП. Там, де потрібна швидкість, беруть [SPI](topic:communications/spi-bus).

**Ідея.** SPI — чотири лінії, і на Nano вони закріплені за `D13` (`SCK`, такт), `D11` (`MOSI`, дані від Nano до пристрою), `D12` (`MISO`, дані назад) і `D10` (`SS`, вибір пристрою). На відміну від I²C, тут немає адрес: кожен пристрій має **власну** лінію вибору (`SS` / *chip select*), і ви притягуєте її донизу, поки говорите саме з ним. Обмін дуже прямий і завжди двобічний: ви зсуваєте байт назовні по `MOSI` й **тим самим тактом** приймаєте байт по `MISO`. В Arduino це `SPI.transfer(x)`, який водночас шле й повертає; в ESP-IDF — `spi_device_polling_transmit` із парою буферів; у STM32 — `HAL_SPI_TransmitReceive`. Немає підтверджень, немає адрес — тому SPI швидкий, але й «сліпий»: він не скаже, чи хтось узагалі слухав.

:::tabs
```arduino
#include <SPI.h>

const uint8_t PIN_CS = 10;      // вибір пристрою (chip select)

// прочитати один регістр: шлемо адресу, приймаємо відповідь
uint8_t spi_read_reg(uint8_t reg) {
    digitalWrite(PIN_CS, LOW);              // «слухай мене»
    SPI.transfer(reg | 0x80);               // старший біт = «читання» (типово)
    uint8_t value = SPI.transfer(0x00);     // порожній байт — щоб зсунути відповідь
    digitalWrite(PIN_CS, HIGH);             // «все, відпускаю»
    return value;
}

void setup() {
    Serial.begin(9600);
    pinMode(PIN_CS, OUTPUT);
    digitalWrite(PIN_CS, HIGH);             // спокій = не вибрано
    SPI.begin();                            // D13/D11/D12 налаштує сама
    // швидкість, порядок бітів і режим — з даташита пристрою:
    SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
}

void loop() {
    uint8_t id = spi_read_reg(0x0F);        // умовний регістр «хто ти»
    Serial.println(id, HEX);
    delay(500);
}
```
```esp-idf
#include "driver/spi_master.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static spi_device_handle_t dev;
static const char *TAG = "spi";

// прочитати один регістр: шлемо адресу, приймаємо відповідь
static uint8_t spi_read_reg(uint8_t reg) {
    uint8_t tx[2] = { reg | 0x80, 0x00 };   // старший біт = «читання» (типово)
    uint8_t rx[2] = { 0 };
    spi_transaction_t t = { .length = 16, .tx_buffer = tx, .rx_buffer = rx };
    ESP_ERROR_CHECK(spi_device_polling_transmit(dev, &t));  // CS смикає драйвер сам
    return rx[1];                           // відповідь прийшла в другому байті
}

void app_main(void) {
    const spi_bus_config_t bus = {
        .mosi_io_num = 23, .miso_io_num = 19, .sclk_io_num = 18,
        .quadwp_io_num = -1, .quadhd_io_num = -1,
    };
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));

    // швидкість, режим і лінія вибору — з даташита пристрою:
    const spi_device_interface_config_t cfg = {
        .clock_speed_hz = 1000000, .mode = 0,   // MSB-first — типово
        .spics_io_num = 5, .queue_size = 1,
    };
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &cfg, &dev));

    while (1) {
        ESP_LOGI(TAG, "%02X", spi_read_reg(0x0F));   // умовний регістр «хто ти»
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
```
```stm32
#include "stm32f4xx_hal.h"
#include <stdio.h>

extern SPI_HandleTypeDef hspi1;   // швидкість, MSB-first і режим — у CubeMX

#define CS_PORT GPIOA
#define CS_PIN  GPIO_PIN_4        // вибір пристрою: звичайний GPIO, смикаємо вручну

// прочитати один регістр: шлемо адресу, приймаємо відповідь
static uint8_t spi_read_reg(uint8_t reg) {
    uint8_t tx[2] = { reg | 0x80, 0x00 };   // старший біт = «читання» (типово)
    uint8_t rx[2] = { 0 };
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);  // «слухай мене»
    HAL_SPI_TransmitReceive(&hspi1, tx, rx, 2, 100);     // шлемо й приймаємо разом
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);    // «все, відпускаю»
    return rx[1];                           // відповідь прийшла в другому байті
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_SPI1_Init(); MX_USART2_UART_Init();
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);    // спокій = не вибрано

    while (1) {
        printf("%02X\r\n", spi_read_reg(0x0F));          // умовний регістр «хто ти»
        HAL_Delay(500);
    }
}
```
:::

Три параметри `SPISettings` — це те, на чому спотикаються найчастіше. **Швидкість** (тут 1 МГц) не має перевищувати межу пристрою. **Порядок бітів** — `MSBFIRST` чи `LSBFIRST`, з якого кінця байта йдуть біти. **Режим** (`SPI_MODE0`…`3`) задає, за яким фронтом такту читати дані й у якому спокої тримати лінію `SCK`. Усі три беруться з даташита пристрою; помилитеся в будь-якому — обмін піде, але цифри будуть маренням.

**Пастки.**

*`SS` (`D10`) має лишатися виходом.* Тонкість AVR: якщо вивід `SS` (`D10`) зробити **входом** і він випадково впаде в `LOW`, апаратний SPI перемкнеться в режим «підлеглого» й замовкне як ведучий. Тому навіть якщо ви керуєте пристроєм з іншого виводу, `D10` тримайте налаштованим як `OUTPUT`. Це часте джерело «SPI раптом перестав працювати».

*Знову 5 В проти 3.3 В.* SD-картки й багато радіомодулів живляться від 3.3 В і бояться 5 В на лініях. Nano ж жене `SCK`/`MOSI`/`SS` на 5 В. Потрібен перетворювач рівнів на цих трьох лініях (лінію `MISO`, що йде **від** давача, зазвичай можна лишити — Nano прочитає й 3.3 В як `HIGH`). Пряме під'єднання 3.3-вольтової SD-картки до 5-вольтового Nano — класичний спосіб її спалити.

*Забутий `beginTransaction`.* Якщо на шині кілька пристроїв із **різними** швидкостями чи режимами, кожен обмін обгортайте в `beginTransaction`/`endTransaction` з правильними для цього пристрою налаштуваннями. Інакше швидкий пристрій дістане параметри повільного (або навпаки) і віддасть сміття.

## millis замість delay: робити кілька справ разом

**Задача.** Блимати світлодіодом раз на секунду **і** водночас читати кнопку без затримки, **і** щосекунди слати число по `Serial`. З `delay` це неможливо: поки плата «спить» у `delay(1000)`, вона глуха до кнопки.

**Ідея.** `delay(1000)` **зупиняє все** на секунду — процесор просто крутиться на місці. Замість «почекати секунду» треба питати «а чи минула вже секунда?» і бігти далі, якщо ні. Для цього потрібен лічильник часу від старту — він є всюди: в Arduino це `millis()` (мілісекунди), у STM32 HAL `HAL_GetTick()` (теж мілісекунди), в ESP-IDF `esp_timer_get_time()` (мікросекунди). Ви запам'ятовуєте, коли востаннє зробили дію, і на кожному колі головного циклу перевіряєте, чи різниця доросла до потрібного інтервалу. Плата тоді не зупиняється ніколи — вона тисячі разів на секунду оббігає всі справи й робить ту, чий час настав. Там, де під рукою є RTOS (ESP-IDF, Zephyr), ту саму одночасність частіше роблять інакше: розводять справи по окремих задачах, кожна спить своїм `vTaskDelay`, а планувальник віддає процесор тій, чий час настав.

:::tabs
```arduino
const uint8_t PIN_LED = 13;
const uint8_t PIN_BTN = 2;

unsigned long ledLast = 0;      // коли востаннє перемкнули світлодіод
unsigned long msgLast = 0;      // коли востаннє слали повідомлення
bool ledOn = false;

void setup() {
    Serial.begin(9600);
    pinMode(PIN_LED, OUTPUT);
    pinMode(PIN_BTN, INPUT_PULLUP);
}

void loop() {
    unsigned long now = millis();

    // задача 1: блимати раз на секунду, нікого не блокуючи
    if (now - ledLast >= 1000) {
        ledLast = now;
        ledOn = !ledOn;
        digitalWrite(PIN_LED, ledOn ? HIGH : LOW);
    }

    // задача 2: слати число щопівсекунди
    if (now - msgLast >= 500) {
        msgLast = now;
        Serial.println(analogRead(A0));
    }

    // задача 3: кнопка реагує МИТТЄВО — жодного delay її не глушить
    if (digitalRead(PIN_BTN) == LOW) {
        // тут дія на натискання
    }
}
```
```esp-idf
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED GPIO_NUM_2
#define PIN_BTN GPIO_NUM_4
static const char *TAG = "app";

// задача 1: блимати раз на секунду, нікого не блокуючи
static void led_task(void *arg) {
    bool on = false;
    while (1) {
        on = !on;
        gpio_set_level(PIN_LED, on);
        vTaskDelay(pdMS_TO_TICKS(1000));   // спить ЦЯ задача, не весь чип
    }
}

// задача 2: слати число щопівсекунди
static void log_task(void *arg) {
    while (1) {
        ESP_LOGI(TAG, "%d", (int)xTaskGetTickCount());
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

void app_main(void) {
    gpio_set_direction(PIN_LED, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_BTN, GPIO_MODE_INPUT);
    gpio_set_pull_mode(PIN_BTN, GPIO_PULLUP_ONLY);

    xTaskCreate(led_task, "led", 2048, NULL, 5, NULL);
    xTaskCreate(log_task, "log", 2048, NULL, 5, NULL);

    while (1) {   // задача 3: кнопка реагує МИТТЄВО — сусіди її не глушать
        if (gpio_get_level(PIN_BTN) == 0) {
            // тут дія на натискання
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```
```stm32
#include "stm32f4xx_hal.h"
#include <stdio.h>

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();

    uint32_t ledLast = 0, msgLast = 0;   // коли востаннє робили кожну дію
    GPIO_PinState led = GPIO_PIN_RESET;

    while (1) {
        uint32_t now = HAL_GetTick();    // мілісекунди від старту

        // задача 1: блимати раз на секунду, нікого не блокуючи
        if (now - ledLast >= 1000) {
            ledLast = now;
            led = (led == GPIO_PIN_SET) ? GPIO_PIN_RESET : GPIO_PIN_SET;
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, led);
        }

        // задача 2: слати число щопівсекунди
        if (now - msgLast >= 500) {
            msgLast = now;
            printf("%lu\r\n", (unsigned long)now);
        }

        // задача 3: кнопка реагує МИТТЄВО — жодного HAL_Delay її не глушить
        if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET) {
            // тут дія на натискання
        }
    }
}
```
:::

**Пастки.**

*Порівнюйте різницю, а не самі значення.* `millis()` — це `unsigned long`, і приблизно через **49 діб** він переповнюється й скидається в нуль. Якщо писати `if (now >= ledLast + 1000)`, у мить переповнення логіка зламається. А от `if (now - ledLast >= 1000)` **переживає** переповнення завдяки арифметиці беззнакових чисел: різниця виходить правильною навіть коли `now` уже «пішло на друге коло». Тому канонічна форма — саме `now - last >= інтервал`, а не `now >= last + інтервал`.

*Тип має бути `unsigned long`.* Запам'ятаєте час у `int` — а `int` на Nano лише 16-бітовий і переповнюється вже на 32767. Через 33 секунди все зламається. Змінні під час — завжди `unsigned long`.

*Довгі роботи всередині `loop` усе одно блокують.* `millis`-підхід дає ілюзію одночасності, лише поки кожна дія коротка. Якщо всередині якоїсь гілки сидить власний `delay(200)` чи повільне читання, воно так само глушить решту на цей час. Тримайте кожен крок швидким; довгі операції розбивайте на стани.

## sleep: дожити на батарейці

**Задача.** Плата має жити місяцями від батарейки, а працює лише зрідка — раз на хвилину виміряти й заснути. Постійна робота з'їдає заряд за дні; треба спати між ділом.

**Ідея.** Режими сну є в кожному МК; різняться вони лише тим, що саме лишається живим і хто вміє розбудити. У ATmega328P у сні ядро зупиняється й струм падає з міліампер до **мікроамперів**. Найглибший — `SLEEP_MODE_PWR_DOWN`: гасне майже все, лишається тільки те, що може розбудити чип, — зовнішнє переривання чи **сторожовий таймер** (watchdog). Сторожовий таймер тут зручний: він сам «цокає» від власного генератора й будить чип через задані проміжки (макс. ~8 с за раз). Схема така: налаштувати watchdog на переривання → заснути → прокинутися по його сигналу → зробити діло → знову заснути. Будильник в інших чипах свій: у ESP32 це RTC-таймер, і глибокий сон там не «продовжує» програму, а стартує її наново; у STM32 будить теж RTC, а після режиму `STOP` доводиться заново піднімати такт.

:::tabs
```arduino
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <avr/interrupt.h>

// прокидання від сторожового таймера — обробник має бути, хай і порожній
ISR(WDT_vect) { /* просто будить чип */ }

void setup() {
    // налаштувати watchdog на переривання (не скид) кожні ~8 с
    cli();                                  // заборонити переривання на час зміни
    wdt_reset();
    WDTCSR = (1 << WDCE) | (1 << WDE);      // відкрити зміну
    WDTCSR = (1 << WDIE) | (1 << WDP3) | (1 << WDP0);  // WDIE=переривання, ~8 с
    sei();                                  // дозволити переривання назад
}

void loop() {
    // 1. корисна робота (тут — блимнути, а реально: виміряти й записати)
    digitalWrite(LED_BUILTIN, HIGH); delay(20); digitalWrite(LED_BUILTIN, LOW);

    // 2. заснути найглибше до наступного «цок» watchdog
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    sleep_cpu();          // ← тут ядро зупиняється; прокинеться в ISR(WDT_vect)
    sleep_disable();      // виконається вже після пробудження
}
```
```esp-idf
#include "esp_sleep.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED GPIO_NUM_2

void app_main(void) {
    // 1. корисна робота (тут — блимнути, а реально: виміряти й записати)
    gpio_set_direction(PIN_LED, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_LED, 1);
    vTaskDelay(pdMS_TO_TICKS(20));
    gpio_set_level(PIN_LED, 0);

    // 2. звести RTC-будильник на 8 с і заснути найглибше
    ESP_ERROR_CHECK(esp_sleep_enable_timer_wakeup(8ULL * 1000000));  // мікросекунди
    esp_deep_sleep_start();
    // ← сюди керування НЕ повертається: після глибокого сну чип стартує наново,
    //   з початку app_main. Стан, який має пережити сон, кладуть у RTC-пам'ять.
}
```
```stm32
#include "stm32f4xx_hal.h"

extern RTC_HandleTypeDef hrtc;   // джерело такту RTC — LSE 32768 Гц

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_RTC_Init();

    while (1) {
        // 1. корисна робота (тут — блимнути, а реально: виміряти й записати)
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
        HAL_Delay(20);
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);

        // 2. звести будильник RTC на 8 с: RTCCLK/16 = 2048 тиків на секунду
        HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, 8 * 2048, RTC_WAKEUPCLOCK_RTCCLK_DIV16);
        HAL_SuspendTick();       // інакше SysTick будив би нас щомілісекунди
        HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
        // ← а сюди керування повертається: після STOP програма йде далі,
        //   але такт скинуто на HSI — його треба підняти заново
        SystemClock_Config();
        HAL_ResumeTick();
        HAL_RTCEx_DeactivateWakeUpTimer(&hrtc);
    }
}
```
:::

**Пастки.**

*Сплячий чип ≠ спляча плата.* Ось найважливіше і найприкріше. `SLEEP_MODE_PWR_DOWN` кладе **ядро** ATmega до мікроамперів — але сама плата Nano все одно тягне **~15–20 мА**, бо на ній світиться живильний світлодіод (~5 мА), працює лінійний стабілізатор AMS1117 (власне споживання) і, головне, **не спить міст CH340** — у нього немає виводу вимкнення, він жере струм завжди. Тобто на голій платі сон дає куди менший виграш, ніж обіцяє даташит чипа. Щоб дійти до по-справжньому мікроамперного споживання, доводиться **фізично** прибирати живильний світлодіод (випаяти його резистор) і від'єднувати CH340 — а це вже переробка плати. Для серйозно автономних проєктів часто беруть не Nano, а голий ATmega328P на своїй платі без цієї «обв'язки», або плату, де CH340 вимикається. Тому чесна оцінка: `sleep` на Nano корисний, але сам собою батарейку на місяці **не** розтягне — заважає онбордна периферія.

*Watchdog як скид проти watchdog як переривання.* Той самий сторожовий таймер уміє два різні діла: **скинути** чип (біт `WDE`) або **розбудити** перериванням (біт `WDIE`). Для періодичного сну потрібне саме переривання. Якщо переплутати й лишити режим скиду, плата не прокинеться в потрібне місце, а **перезавантажиться** — і крутитиметься по колу з `setup()`, ніби завмерла. Тому в налаштуванні вище стоїть `WDIE`, а обробник `ISR(WDT_vect)` мусить існувати (хай і порожній) — інакше після переривання без обробника чип теж піде на скид.

*Максимум ~8 с за раз.* Watchdog не вміє спати довше за ~8 секунд поспіль. Треба хвилину — засинайте вісім разів по вісім секунд у циклі, рахуючи «цоки». Це нормальна практика: лічильник пробуджень усередині `ISR` або в `loop`, і корисна робота — лише коли назбиралося потрібне число інтервалів.

*Периферія теж має заснути.* Сон гасить ядро, але зовнішній давач, дисплей чи радіомодуль продовжують жерти струм самі. Перед сном їх треба або вимкнути (транзистором по живленню), або перевести в їхній власний режим сну. Інакше плата спить, а давач поряд спокійно висмоктує батарею.

## Коли код не заливається: Old чи New Bootloader

Останнє, але найприкріше, бо стається ще **до** того, як ваш код почне працювати. Ви написали ідеальний скетч, тиснете «завантажити» — а середовище відповідає `avrdude: stk500_recv(): programmer is not responding`, і заливка падає. Перше, у що хочеться повірити, — мертва плата чи кабель. Майже завжди причина інша.

У флеші Nano поряд із вашим кодом живе **завантажувач** — крихітна програма, що приймає новий скетч по USB. На клонах його зашивають у двох різних версіях (старій і новій), і вони спілкуються **на різних швидкостях**. Середовище має знати, яка саме у вашої плати: у меню процесора є два пункти — звичайний і **«ATmega328P (Old Bootloader)»**. Якщо вибрано не той, рукостискання з платою не складається, і заливка обривається тією самою помилкою «не відповідає».

> 🔧 **Навіщо це.** Лік — один клац у меню, а не паяльник. Падає заливка на свіжому Nano, хоча плата світиться й порт видно, — **перемкніть тип завантажувача** (звичайний ↔ Old Bootloader) і спробуйте знову. Різні партії клонів шиються по-різному; цей єдиний пункт меню рятує найчастіше. Драйвер, кабель і сам чип тут ні до чого — просто дві версії завантажувача говорять на різних швидкостях, і середовищу треба підказати правильну.

## Спільна нитка всіх прикладів

Якщо звести все докупи, кожен блок вище тримається на одному й тому самому наборі звичок. Не блокувати плату там, де можна не блокувати (`millis`, не `delay`). Пам'ятати про фізичні межі саме Nano: `D0`/`D1` зайняті під `Serial`, `A6`/`A7` — тільки аналогові, ШІМ лише на шести `~`-виводах, `A4`/`A5` — це I²C, `D10`–`D13` — це SPI. Ніколи не забувати про 5-вольтові рівні, коли поряд 3.3-вольтова електроніка. І весь час косити оком на 2 КБ SRAM — загортати сталі тексти у `F()`, не тримати велетенських буферів, стежити, щоб стек мав куди рости.

Жоден із цих прикладів не «магія бібліотеки»: під кожним — проста апаратна причина, чому саме так. Зрозумієте причину — і перенесете той самий підхід на будь-який інший давач, дисплей чи модуль, лише підставивши інші адреси, регістри й масштаби з його даташита. Саме в цьому й сила старенького Nano: він робить видимою всю механіку, яку старші плати ховають, — і тому лишається чи не найкращим місцем, де по-справжньому розумієш, що відбувається під `digitalWrite`.
