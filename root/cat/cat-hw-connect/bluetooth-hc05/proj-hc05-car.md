# ⚙️ Машинка на HC-05: керування з телефона, телеметрія, аварійний стоп

<preknowlist>
- [Інтерфейс HC-05/HC-06 у коді](root:cat-hw-connect/bluetooth-hc05/api-hc05-uart.md) — порт (`available/read/write/print`), режим AT і читання ніжки STATE; застосунок нижче будується просто над цим інтерфейсом.
- [Таймер millis()](root:sf-devices/millis-micros) — неблокувальний відлік часу без `delay`; ним шлемо телеметрію періодично, не заморожуючи керування.
</preknowlist>

Маючи інтерфейс модуля в руках — порт (`available/read/write/print`), режим AT і ніжку STATE (усе це в [довіднику інтерфейсу](root:cat-hw-connect/bluetooth-hc05/api-hc05-uart.md)) — зберемо з нього справжній прилад. Наскрізний приклад один: **машинка на керуванні з телефона**. Телефон під'єднується по Bluetooth і шле однобайтові команди; машинка їх виконує; назад машинка шле телеметрію; а якщо зв'язок обірвався посеред руху — сама спиняється. Тут три струмки інформації з інтерфейсу сходяться в одну робочу програму, і видно, як кожен грає свою роль.

---

## Задача: що саме робить машинка

Зафіксуймо конкретну ціль, щоб код був не абстрактний. Прилад — машинка з двома моторами. Телефон під'єднується по Bluetooth і шле однобайтові команди:

```
'F' — вперед      'S' — стоп
'B' — назад       цифра '0'…'9' — швидкість (0 = стоп, 9 = повний хід)
'L' — вліво
'R' — вправо
```

А назад машинка раз на секунду шле в телефон рядок телеметрії, щоб на екрані був стан:

```
BAT:7.42 SPD:6\r\n
```

Начебто дрібниця, але тут уже сидять усі три струмки з інтерфейсу. Команди приходять — треба **читати** їх без блокування, щоб машинка не «глухла». Телеметрію треба **писати** періодично, не спиняючи керування. І якщо зв'язок обірвався посеред руху — треба це **помітити** (STATE) і спинити мотори, бо інакше машинка поїде в стіну з останньою командою «вперед».

---

## Команди всередину: байти стають діями

Порт віддає нам байти — наша робота тут перетворити ці байти на рух моторів. Ось де струмок «телефон → машинка» стає керуванням.

```cpp
const int LEFT_MOTOR = 5, RIGHT_MOTOR = 6;   // ШІМ-ніжки моторів (приклад)
int speedLevel = 5;                           // поточна швидкість 0…9

void applyDrive(int leftDir, int rightDir);   // ваша функція: напрям кожного мотора

void handleCommand(char c) {
    switch (c) {
        case 'F': applyDrive(+1, +1); break;   // вперед: обидва мотори вперед
        case 'B': applyDrive(-1, -1); break;   // назад
        case 'L': applyDrive(-1, +1); break;   // поворот: мотори в різні боки
        case 'R': applyDrive(+1, -1); break;
        case 'S': applyDrive( 0,  0); break;   // стоп
        default:
            if (c >= '0' && c <= '9')          // цифра-символ → рівень швидкості
                speedLevel = c - '0';          // '7' - '0' == 7
            break;
    }
}

void loop() {
    while (btSerial.available()) {             // забрати ВСІ накопичені байти
        char c = btSerial.read();
        handleCommand(c);
    }
    // ...тут телеметрія й контроль зв'язку, які додамо нижче...
}
```

Тут два важливі рішення. По-перше, читаємо в `while`, а не в `if`: між ітераціями `loop` могло накопичитися кілька байтів, і треба вибрати їх усі, інакше буфер відстає й керування «залипає». По-друге, `c - '0'` — стандартний трюк: символ цифри `'7'` має ASCII-код 55, символ `'0'` — 48, різниця 55−48=7 дає саме число. Розбір команди — це `switch` по символу, а не по «радіо»: модуль давно за кадром, у руках лише байти.

Приємний наслідок: `handleCommand` **не залежить від плати**. Звідки прилітає байт — програмний порт Uno, `Serial2` на ESP32 чи `USART1` на STM32 — логіці керування байдуже; міняється лише об'єкт-порт, з якого ви читаєте.

---

## Телеметрія назад: пишемо в порт без блокування

Тепер зустрічний струмок — машинка → телефон. Раз на секунду шлемо рядок стану. Наївно було б написати `delay(1000)` між посилками, але це заморозило б керування: доки машинка «спить» секунду, вона не читає команд і не спиняється. Тому час відмірюємо за вільним лічильником мілісекунд, що тікає сам собою від увімкнення (в Arduino це [`millis()`](root:sf-devices/millis-micros), на ESP32 — `esp_timer_get_time()`, на STM32 — `HAL_GetTick()`) — звіряємося з годинником і шлемо, коли настав момент, не блокуючи цикл.

```cpp
uint32_t lastTelemetry = 0;

float readBattery();   // ваш давач: напруга акумулятора у вольтах

void loop() {
    // 1) читати команди (як вище)
    while (btSerial.available()) handleCommand(btSerial.read());

    // 2) раз на секунду слати телеметрію — БЕЗ delay
    uint32_t now = millis();
    if (now - lastTelemetry >= 1000) {
        lastTelemetry = now;

        float bat = readBattery();
        // "BAT:7.42 SPD:6\r\n" — той самий формат, що читає застосунок телефона
        btSerial.print("BAT:");
        btSerial.print(bat, 2);          // два знаки після коми
        btSerial.print(" SPD:");
        btSerial.print(speedLevel);
        btSerial.print("\r\n");          // кінець рядка — застосунок ріже потік по ньому
    }
}
```

Ключова деталь у форматі: телеметрія завершується `\r\n`. Це не примха модуля (у прозорому режимі йому байдуже, які байти возити) — це **домовленість між машинкою і застосунком** на телефоні. Приймач на тому кінці читає потік і ріже його на рядки саме по `\r\n`; без роздільника всі посилки злипнуться в одну нескінченну стрічку, і застосунок не знатиме, де кінчається одне значення й починається наступне. Роздільник у прозорому потоці завжди призначаєте **ви самі** — модуль тут ні до чого.

Зверніть увагу: число йде в порт **як текст** із двома знаками після коми, а не сирими байтами (`print(bat, 2)` в Arduino, `snprintf(buf, sizeof buf, "%.2f", bat)` там, де рядок форматуємо самі). Це важливо — на іншому кінці людина (чи простий парсер застосунку) читає `7.42`, а не чотири байти IEEE-754, які довелося б розкодовувати.

---

## STATE як сторож: обрив зв'язку спиняє мотори

Третій струмок — сам факт зв'язку. Ніжку STATE для рухомого приладу треба ловити на **момент обриву**: щойно STATE впав з 1 у 0, негайно спинити мотори, щоб машинка не поїхала далі з останньою командою. Від плати тут потрібен лише звичайний цифровий вхід, який ми читаємо щоцикл, — це вміє будь-який мікроконтролер, різняться самі назви викликів.

:::tabs
== Arduino (Uno / Nano)

```arduino
const int PIN_STATE = 7;    // STATE модуля → цей вхід МК
bool wasConnected = false;

void setup() {
    // ...інша ініціалізація...
    pinMode(PIN_STATE, INPUT);
}

void loop() {
    // ...читання команд і телеметрія...

    bool connected = digitalRead(PIN_STATE);   // 1 = є з'єднання, 0 = немає

    if (wasConnected && !connected) {
        // зв'язок ЩОЙНО обірвався — аварійний стоп
        applyDrive(0, 0);
        Serial.println("Зв'язок втрачено — мотори зупинено.");
    }
    wasConnected = connected;
}
```

== ESP-IDF (ESP32)

```esp-idf
#include "driver/gpio.h"
#include "esp_log.h"

#define PIN_STATE GPIO_NUM_4        // STATE модуля → цей вхід МК

static const char *TAG = "car";
static bool wasConnected = false;

static void stateInit(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_STATE,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,   // поки модуль мовчить, вхід не «висить»
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
}

static void statePoll(void) {                   // виклик у головному циклі задачі
    bool connected = gpio_get_level(PIN_STATE); // 1 = є з'єднання, 0 = немає

    if (wasConnected && !connected) {
        // зв'язок ЩОЙНО обірвався — аварійний стоп
        applyDrive(0, 0);
        ESP_LOGW(TAG, "Зв'язок втрачено — мотори зупинено.");
    }
    wasConnected = connected;
}
```

== STM32 (HAL)

```stm32
#include "main.h"               // STATE модуля → PA0: у CubeMX GPIO_Input, Pull-down
#include <stdbool.h>

#define STATE_PORT  GPIOA
#define STATE_PIN   GPIO_PIN_0

static bool wasConnected = false;

static void statePoll(void) {   // виклик у головному циклі while(1)
    // 1 = є з'єднання, 0 = немає
    bool connected = (HAL_GPIO_ReadPin(STATE_PORT, STATE_PIN) == GPIO_PIN_SET);

    if (wasConnected && !connected) {
        // зв'язок ЩОЙНО обірвався — аварійний стоп
        applyDrive(0, 0);
        printf("Зв'язок втрачено — мотори зупинено.\r\n");   // консоль налагодження
    }
    wasConnected = connected;
}
```
:::

Логіка `wasConnected && !connected` спрацьовує **рівно на переході** 1→0, а не щоцикл, доки зв'язку немає. Це важливо: реагувати треба на *подію* обриву (один раз спинити), а не безперервно спамити «немає зв'язку».

> 🔧 **Навіщо це.** Без STATE машинка, у якої обірвався зв'язок посеред команди «вперед», поїде в стіну — бо остання команда в буфері лишилась «вперед», а нової «стоп» уже ніхто не пришле. STATE перетворює це з катастрофи на аварійний стоп за міліметри. Це не прикраса, а елемент безпеки будь-чого рухомого на радіокеруванні: пульт може вийти із зони, розрядитись, зависнути — і пристрій мусить це помітити сам, а не чекати команди, якої вже не буде.

---

## Повна програма машинки: усе разом

Зберемо три струмки — команди всередину, телеметрія назовні, STATE як сторож — в одну робочу програму. Це вже не фрагменти, а те, що можна залити й поїхати. (Налаштування модуля — ім'я, PIN, швидкість — це окрема одноразова програма з `configureModule()` з [довідника інтерфейсу](root:cat-hw-connect/bluetooth-hc05/api-hc05-uart.md); тут модуль уже налаштований і працює прозорим містом.)

Від мікроконтролера потрібне на будь-якій платформі те саме: **UART** на 9600, заведений на модуль; **один цифровий вхід** під STATE; **лічильник мілісекунд**, щоб відміряти секунду телеметрії; і головний цикл, який нічим не блокується. Далі — три втілення того самого приладу: **Arduino** (Uno/Nano, програмний порт), **ESP-IDF** (ESP32, апаратний UART2) і **STM32 HAL** (USART1 із прийманням по перериванню). Це не транслітерація одного скетча: логіка приладу спільна, різниться лише те, як платформа дає порт, вхід і годинник.

:::tabs
== Arduino (Uno / Nano)

```arduino
#include <SoftwareSerial.h>

SoftwareSerial btSerial(10, 11);   // (RX ← TXD модуля, TX → RXD модуля через дільник)

const int PIN_STATE = 7;
const int LEFT_MOTOR = 5, RIGHT_MOTOR = 6;

int  speedLevel   = 5;
bool wasConnected = false;
uint32_t lastTelemetry = 0;

void applyDrive(int leftDir, int rightDir);   // ваша реалізація моторів
float readBattery();                          // ваш давач напруги

void handleCommand(char c) {
    switch (c) {
        case 'F': applyDrive(+1, +1); break;
        case 'B': applyDrive(-1, -1); break;
        case 'L': applyDrive(-1, +1); break;
        case 'R': applyDrive(+1, -1); break;
        case 'S': applyDrive( 0,  0); break;
        default:
            if (c >= '0' && c <= '9') speedLevel = c - '0';
            break;
    }
}

void setup() {
    Serial.begin(9600);        // монітор по USB
    btSerial.begin(9600);      // модуль, РОБОЧА швидкість (не 38400 — тут не AT)
    pinMode(PIN_STATE, INPUT);
    applyDrive(0, 0);          // старт зі стопу
}

void loop() {
    // 1) команди від телефона → дії
    while (btSerial.available()) {
        handleCommand(btSerial.read());
    }

    // 2) сторож зв'язку: обрив → аварійний стоп
    bool connected = digitalRead(PIN_STATE);
    if (wasConnected && !connected) {
        applyDrive(0, 0);
        Serial.println("Зв'язок втрачено — стоп.");
    }
    wasConnected = connected;

    // 3) телеметрія раз на секунду, без блокування
    uint32_t now = millis();
    if (connected && now - lastTelemetry >= 1000) {
        lastTelemetry = now;
        btSerial.print("BAT:");
        btSerial.print(readBattery(), 2);
        btSerial.print(" SPD:");
        btSerial.print(speedLevel);
        btSerial.print("\r\n");
    }
}
```

== ESP-IDF (ESP32)

```esp-idf
#include <stdio.h>
#include <stdbool.h>
#include "driver/uart.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define BT_UART    UART_NUM_2
#define PIN_TXD    GPIO_NUM_17      // → RXD модуля (3.3 В — дільник не потрібен)
#define PIN_RXD    GPIO_NUM_16      // ← TXD модуля
#define PIN_STATE  GPIO_NUM_4

static const char *TAG = "car";

static int      speedLevel    = 5;
static bool     wasConnected  = false;
static int64_t  lastTelemetry = 0;

void  applyDrive(int leftDir, int rightDir);   // ваша реалізація моторів
float readBattery(void);                       // ваш давач напруги

static void handleCommand(char c) {
    switch (c) {
        case 'F': applyDrive(+1, +1); break;
        case 'B': applyDrive(-1, -1); break;
        case 'L': applyDrive(-1, +1); break;
        case 'R': applyDrive(+1, -1); break;
        case 'S': applyDrive( 0,  0); break;
        default:
            if (c >= '0' && c <= '9') speedLevel = c - '0';
            break;
    }
}

static void btInit(void) {
    const uart_config_t cfg = {
        .baud_rate  = 9600,          // РОБОЧА швидкість модуля (не 38400 — тут не AT)
        .data_bits  = UART_DATA_8_BITS,
        .parity     = UART_PARITY_DISABLE,
        .stop_bits  = UART_STOP_BITS_1,
        .flow_ctrl  = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    ESP_ERROR_CHECK(uart_driver_install(BT_UART, 256, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(BT_UART, &cfg));
    ESP_ERROR_CHECK(uart_set_pin(BT_UART, PIN_TXD, PIN_RXD,
                                 UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));

    gpio_config_t st = {
        .pin_bit_mask = 1ULL << PIN_STATE,
        .mode         = GPIO_MODE_INPUT,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&st));
}

void app_main(void) {
    btInit();
    applyDrive(0, 0);                // старт зі стопу

    while (1) {
        // 1) команди від телефона → дії; 0 тиків очікування = НЕ блокуємось
        uint8_t buf[32];
        int n = uart_read_bytes(BT_UART, buf, sizeof buf, 0);
        for (int i = 0; i < n; i++) handleCommand((char)buf[i]);

        // 2) сторож зв'язку: обрив → аварійний стоп
        bool connected = gpio_get_level(PIN_STATE);
        if (wasConnected && !connected) {
            applyDrive(0, 0);
            ESP_LOGW(TAG, "Зв'язок втрачено — стоп.");
        }
        wasConnected = connected;

        // 3) телеметрія раз на секунду, без блокування
        int64_t now = esp_timer_get_time() / 1000;   // мкс → мс
        if (connected && now - lastTelemetry >= 1000) {
            lastTelemetry = now;
            char line[32];
            int len = snprintf(line, sizeof line, "BAT:%.2f SPD:%d\r\n",
                               readBattery(), speedLevel);
            uart_write_bytes(BT_UART, line, len);
        }

        vTaskDelay(pdMS_TO_TICKS(5));   // віддаємо процесор іншим задачам RTOS
    }
}
```

== STM32 (HAL)

```stm32
// USART1 (9600 8N1) → модуль, приймання по перериванню; STATE → PA0 (Input, Pull-down).
// Для "%.2f" у snprintf увімкніть підтримку float у printf: -u _printf_float.
#include "main.h"
#include <stdio.h>
#include <stdbool.h>

extern UART_HandleTypeDef huart1;

#define STATE_PORT  GPIOA
#define STATE_PIN   GPIO_PIN_0
#define RX_SIZE     64              // степінь двійки: індекс маскуємо, а не ділимо

static volatile uint8_t rxRing[RX_SIZE];
static volatile uint8_t rxHead = 0, rxTail = 0;
static uint8_t rxByte;

static int      speedLevel    = 5;
static bool     wasConnected  = false;
static uint32_t lastTelemetry = 0;

void  applyDrive(int leftDir, int rightDir);   // ваша реалізація моторів
float readBattery(void);                       // ваш давач напруги

// Байт із модуля лягає в кільце й одразу чекаємо наступний — головний цикл не спиняється.
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        rxRing[rxHead++ % RX_SIZE] = rxByte;
        HAL_UART_Receive_IT(huart, &rxByte, 1);
    }
}

static bool btAvailable(void) { return rxHead != rxTail; }
static char btRead(void)      { return (char)rxRing[rxTail++ % RX_SIZE]; }

static void handleCommand(char c) {
    switch (c) {
        case 'F': applyDrive(+1, +1); break;
        case 'B': applyDrive(-1, -1); break;
        case 'L': applyDrive(-1, +1); break;
        case 'R': applyDrive(+1, -1); break;
        case 'S': applyDrive( 0,  0); break;
        default:
            if (c >= '0' && c <= '9') speedLevel = c - '0';
            break;
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART1_UART_Init();

    HAL_UART_Receive_IT(&huart1, &rxByte, 1);   // запускаємо приймання
    applyDrive(0, 0);                           // старт зі стопу

    while (1) {
        // 1) команди від телефона → дії
        while (btAvailable()) handleCommand(btRead());

        // 2) сторож зв'язку: обрив → аварійний стоп
        bool connected = (HAL_GPIO_ReadPin(STATE_PORT, STATE_PIN) == GPIO_PIN_SET);
        if (wasConnected && !connected) applyDrive(0, 0);
        wasConnected = connected;

        // 3) телеметрія раз на секунду, без блокування
        uint32_t now = HAL_GetTick();           // мілісекунди від старту
        if (connected && now - lastTelemetry >= 1000) {
            lastTelemetry = now;
            char line[32];
            int len = snprintf(line, sizeof line, "BAT:%.2f SPD:%d\r\n",
                               readBattery(), speedLevel);
            HAL_UART_Transmit(&huart1, (uint8_t *)line, len, 100);
        }
    }
}
```
:::

Придивіться, як три задачі мирно живуть в одному нескінченному циклі **без жодного `delay`**. Команди вибираються всі одразу (`while`), сторож зв'язку перевіряється щоцикл (миттєва реакція на обрив), телеметрія йде за годинником `millis()` (не спиняючи керування). Це і є різниця між прикладом із підручника, що блокується на кожному кроці, і живим приладом, який робить кілька справ водночас. Один прохід циклу займає мікросекунди, тож машинка реагує на команду практично миттєво.

---

## Пастки з боку застосунку

Пастки самого інтерфейсу — швидкість AT, перехрещення TX/RX, дільник на RXD — зібрані в [довіднику інтерфейсу](root:cat-hw-connect/bluetooth-hc05/api-hc05-uart.md). Тут — те, на чому губиться час саме в **логіці приладу**.

**Блокувальна пауза в циклі — прилад глухне до всього.** `delay(1000)` (чи `HAL_Delay(1000)`) між посилками телеметрії заморожує керування на секунду: команди не читаються, STATE не перевіряється, аварійний стоп не спрацює. Періодичні дії робіть за вільним лічильником часу ([`millis()`](root:sf-devices/millis-micros), `esp_timer_get_time()`, `HAL_GetTick()`), лишаючи цикл вільним.

**Немає роздільника в потоці телеметрії — застосунок не ріже рядки.** У прозорому режимі модуль возить байти як є; ділити потік на осмислені шматки — ваша робота. Забудете `\r\n` (чи інший роздільник) наприкінці кожної посилки — на телефоні все зіллється в суцільну стрічку. Роздільник призначаєте ви, узгоджено з приймачем.

**Читання через `if` замість `while` — керування «залипає».** Якщо в `loop` забирати лише **один** байт за прохід, а команд накопичилось кілька, буфер відстає й машинка реагує з затримкою чи на стару команду. Забирайте **всі** накопичені байти в `while (available)`.

**Не читаєте STATE — рухомий прилад не помічає обриву.** Тиша в порту не означає «немає зв'язку»: напарник може бути на зв'язку, але мовчати. Єдиний надійний сигнал обриву — падіння STATE з 1 у 0. Без нього машинка з обірваним пультом поїде далі з останньою командою. Заведіть STATE на вхід і ловіть перехід 1→0 для аварійного стопу.

Звівши три струмки — команди всередину, телеметрію назовні, STATE як сторож — ви маєте живий прилад, а не демонстрацію. Уся «складність Bluetooth» так і лишається за чотирма викликами порту, а машинка робить те, заради чого модуль і брали: тихо перетворює байти на радіо й назад, а телефон — на пульт.
