# ⚙️ Прошивка для KY-031: ловимо короткий стук і читаємо його ритм

Читати KY-031 у циклі, як звичайну кнопку, спокусливо просто — і рівно доти працює, доки `loop` порожній. Варто додати в програму бодай один справжній обов'язок (оновити дисплей, відправити пакет по Wi-Fi, зачекати `delay`), і давач зненацька «глухне»: стукаєш — тиша. Плата не зламалась. Просто контакт усередині KY-031 замикається на **кілька мілісекунд**, а поки процесор возився з дисплеєм, ці мілісекунди минули з розімкненим виводом до наступного читання виводу. Опитування прийшло тоді, коли замикання вже скінчилось.

Ця вставка — про те, як ловити стук **надійно**, незалежно від того, чим забитий головний цикл, і що з тим стуком робити далі: як відрізнити один удар від пружинного торохтіння, як зібрати з голого «замкнено» грубу **серію стуків** (скільки ударів і з якими паузами), і як на цій серії збудувати **замок «на секретний стук»**, що відмикається лише на правильний ритм. Код кожного кроку даємо вкладками під три середовища — Arduino (AVR: Uno, Nano, Pro Mini), ESP-IDF і STM32 HAL: робота та сама, різняться лише назви викликів. Різницю між платформами розберемо там, де вона справжня, бо саме на ній ламаються переноси.

Одну домовленість тримаємо наскрізь, і вона задає весь код нижче: вивід S читаємо **активним-НИЗЬКО** через увімкнену внутрішню підтяжку. У спокої вхід у ВИСОКО («1»), удар садить його на землю коротким НИЗЬКО («0»). Тобто подія — це `LOW`, а перехід, що її ловить залізо, — **фронт спаду** (FALLING), падіння з 1 у 0.

<preknowlist>
- [Переривання](topic:programming/interrupts) — як залізо саме зупиняє головний код і викликає коротку функцію-обробник на зовнішню подію; без цього повільний `loop` губить короткі імпульси.
- [Точний час (millis/micros)](topic:programming/millis-micros) — як міряти проміжки без `delay`, лічачи мілісекунди від старту; на цьому тримається і придушення торохтіння, і читання пауз між стуками.
- [Брязкіт контактів](topic:electronics/contact-debounce) — чому механічний контакт замикається не чисто, а короткою чергою «замкнув-розімкнув»; той самий ефект перетворює один стук на пачку спрацювань.
- [Підтяжки](topic:electronics/floating-pullups) — навіщо цифровому входу підтяжка й чому без неї він ловить наведення; тут усе читання стоїть на внутрішній підтяжці вгору (`INPUT_PULLUP`).
</preknowlist>

## Чому опитування проґавлює удар — і скільки часу маємо

Спершу відчуймо масштаб проблеми в числах, бо саме він диктує вибір між опитуванням і перериванням. Замикання KY-031 триває, скажімо, приблизно 2 мілісекунди (реально від одиниць до десятка, залежно від сили удару й екземпляра). Головний цикл, який раз на оберт малює щось на I²C-дисплеї, легко займає 30–50 мс на один прохід. Порахуймо, з якою ймовірністю опитування взагалі потрапить у вікно замкненого контакту:

```
частка часу, коли контакт замкнений ≈ 2 мс / 40 мс = 0.05 = 5%
шанс проґавити один удар          ≈ 95%
```

Дев'ятнадцять стуків із двадцяти зникнуть безслідно. І це не «іноді збоїть» — це **систематична глухота**: чим важчий цикл, тим менша частка, тим більше пропусків. Побороти її опитуванням можна лише одним способом — гнати читання виводу так часто, щоб проміжок між читаннями був **коротшим за замикання**, тобто мілісекунду-дві. Але тоді весь цикл мусить лишатися коротшим за ці дві мілісекунди — жодного `delay`, жодного повільного дисплея. На практиці це нездійсненна дисципліна: варто одній підпрограмі затягнутися, і давач знову сліпне.

> 🔧 **Навіщо це.** Правило звучить так: **опитування придатне лише в короткому, нічим не забитому циклі**. Скетч на початку статті-опису (голий `digitalRead` у `loop`) — саме такий випадок і саме тому працює: там `loop` порожній. Щойно ваша програма робить ще щось відчутне за часом, опитування стає ненадійним, і читати давач треба **перериванням**. Це не питання смаку — це питання, чи взагалі спрацює пристрій.

Правильна відповідь — перекласти ловіння моменту на **залізо**. Мікроконтролер уміє слідкувати за виводом апаратно й, побачивши фронт спаду, **сам** на мить кинути головний код і викликати коротку функцію-обробник — [переривання](topic:programming/interrupts). Йому байдуже, чим зайнятий головний цикл: перехід 1→0 буде зафіксований, навіть якщо тривав мілісекунду. Обробник лише ставить прапорець «був стук», а вся неспішна робота (порахувати, надрукувати, блимнути) лишається в головному циклі — `loop` у скетчі, задача FreeRTOS в ESP-IDF, `while (1)` у `main` на STM32.

## Ловимо стук перериванням: крихітний обробник і прапорець

Візьмімо базову схему й перепишімо її на переривання. Ідея проста і в ній — ключ до всього: **обробник має бути крихітний**. Він не друкує, не рахує ритм, не запалює світлодіод — він лише зводить прапорець `volatile bool knocked = true`. Головний цикл на дозвіллі бачить прапорець, обробляє подію й скидає його. Так переривання забирає в процесора лічені мікросекунди, а вся логіка тече у звичайному темпі `loop`.

Два слова, без яких код тихо не працюватиме, — це `volatile` і придушення торохтіння. Прапорець `volatile`, бо його міняє обробник «за спиною» головного коду: без цього слова компілятор має право вирішити, що в `loop` прапорець ніхто не чіпає, і **закешувати** його в регістрі — цикл читатиме стару копію й ніколи не побачить стуку. А торохтіння — це вже знайомий [брязкіт контактів](topic:electronics/contact-debounce): пружина, торкнувшись стрижня, відскакує й торкається знову, тож один удар дає не один фронт спаду, а цілу чергу. Кожен фронт — окреме переривання. Без керування один стук намотає лічильник на п'ять-десять.

Гасять це **вікном-локаутом** (англ. lockout — «замкнено на час»): зарахувавши стук, кілька десятків мілісекунд просто ігноруємо вхід. Пружина за цей час устигає вгамуватись, і наступний правдивий стук піде вже за глухим вікном. Важлива тонкість, специфічна для AVR: **час локауту міряємо в `loop`, а не в обробнику**. Причина у пристрої `millis()` — він рахує час на тому ж таймерному перериванні, яке під час нашого обробника **зупинено**, тож усередині обробника `millis()` завмирає й повертає стале значення. Тому мітку часу ставимо там, де годинник іде, — у головному циклі.

**Умова.** Вивід S давача — на вивід, що вміє зовнішнє переривання на фронті спаду (на Uno/Nano таких лише два, D2 і D3, — беремо D2; на ESP32 годиться майже кожен GPIO — беремо GPIO4; на STM32 будь-який, з огляду на спільні лінії EXTI, — беремо PA0). Внутрішня підтяжка вгору, читаємо активним-НИЗЬКО. Світлодіод — на вільний вихід (D13 · GPIO2 · PC13). Треба надійно зловити кожен стук навіть при повільному циклі, порахувати стуки в монітор і не рахувати торохтіння за окремі події.

:::tabs

```arduino
const uint8_t KNOCK = 2;              // вивід S — на D2 (переривання INT0)
const uint8_t LED   = 13;             // вбудований світлодіод
const unsigned long LOCKOUT = 60;     // глухе вікно після стуку, мс

volatile bool knockFlag = false;      // ставить обробник, скидає loop
unsigned long lastKnock = 0;          // час зарахованого стуку (міряємо в loop)
unsigned long count     = 0;

void onKnock() {                      // обробник: мусить бути КРИХІТНИЙ
    knockFlag = true;                 // єдина дія — звести прапорець
}

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);     // спокій = 1, удар тягне до 0
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
    // ловимо фронт спаду 1→0; digitalPinToInterrupt переводить № піна у № переривання
    attachInterrupt(digitalPinToInterrupt(KNOCK), onKnock, FALLING);
}

void loop() {
    if (knockFlag) {                  // обробник щось зафіксував
        knockFlag = false;            // одразу скидаємо, щоб не зациклитись
        unsigned long now = millis();
        if (now - lastKnock > LOCKOUT) {   // поза глухим вікном — це правдивий стук
            lastKnock = now;
            count++;
            digitalWrite(LED, HIGH);
            Serial.print("стук #");
            Serial.println(count);
        }
        // якщо всередині вікна — прапорець просто з'їдено, це відскок пружини
    }
    if (millis() - lastKnock > 30) digitalWrite(LED, LOW);  // гасимо світлодіод
}
```

```esp-idf
#include <stdio.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define KNOCK       GPIO_NUM_4        // вивід S (на ESP32 годиться майже будь-який)
#define LED         GPIO_NUM_2
#define LOCKOUT_US  60000             // глухе вікно після стуку, мкс

static const char *TAG = "knock";
static volatile bool knock_flag = false;   // ставить обробник, скидає цикл

static void IRAM_ATTR on_knock(void *arg) {   // обробник: мусить бути КРИХІТНИЙ
    knock_flag = true;                        // єдина дія — звести прапорець
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << KNOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,   // спокій = 1, удар тягне до 0
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,    // фронт спаду 1→0
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(KNOCK, on_knock, NULL));

    int64_t last = 0;                 // час зарахованого стуку, мкс від старту
    unsigned count = 0;
    while (1) {
        int64_t now = esp_timer_get_time();
        if (knock_flag) {                        // обробник щось зафіксував
            knock_flag = false;                  // одразу скидаємо
            if (now - last > LOCKOUT_US) {       // поза вікном — правдивий стук
                last = now;
                count++;
                gpio_set_level(LED, 1);
                ESP_LOGI(TAG, "стук #%u", count);
            }
            // якщо всередині вікна — прапорець з'їдено, це відскок пружини
        }
        if (now - last > 30000) gpio_set_level(LED, 0);   // гасимо світлодіод
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
```

```stm32
#include "main.h"
#include <stdio.h>                    // printf перенаправлено на UART

#define LOCKOUT 60u                   // глухе вікно після стуку, мс

volatile uint8_t knockFlag = 0;       // ставить обробник, скидає main

/* HAL сам кличе цей колбек із обробника EXTI — тримаємо його КРИХІТНИМ */
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin == GPIO_PIN_0) knockFlag = 1;    // єдина дія — звести прапорець
}

/* у stm32xxxx_it.c: вектор EXTI0 віддає керування в HAL */
void EXTI0_IRQHandler(void) { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0); }

int main(void) {
    HAL_Init();
    SystemClock_Config();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin  = GPIO_PIN_0;              // PA0 — вивід S
    g.Mode = GPIO_MODE_IT_FALLING;    // вхід із перериванням на фронті спаду
    g.Pull = GPIO_PULLUP;             // внутрішня підтяжка: спокій = 1
    HAL_GPIO_Init(GPIOA, &g);
    g.Pin   = GPIO_PIN_13;            // PC13 — світлодіод
    g.Mode  = GPIO_MODE_OUTPUT_PP;
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &g);
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);

    uint32_t lastKnock = 0, count = 0;
    while (1) {
        if (knockFlag) {                        // обробник щось зафіксував
            knockFlag = 0;                      // одразу скидаємо
            uint32_t now = HAL_GetTick();       // мілісекунди від старту
            if (now - lastKnock > LOCKOUT) {    // поза вікном — правдивий стук
                lastKnock = now;
                count++;
                HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
                printf("стук #%lu\r\n", (unsigned long)count);
            }
            // якщо всередині вікна — це відскок пружини, мовчимо
        }
        if (HAL_GetTick() - lastKnock > 30)     // гасимо світлодіод
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
    }
}
```

:::

Простежмо потік однієї події, бо в ньому вся сіль. Удар садить D2 у нуль — залізо ловить фронт спаду, кидає `loop`, викликає `onKnock`, той ставить `knockFlag = true`, і за мікросекунди керування повертається туди, де `loop` перервався. Наступний прохід циклу бачить прапорець, скидає його, дивиться на годинник. Якщо від попереднього зарахованого стуку минуло більше 60 мс — це новий стук: нарощуємо лічильник, спалахує світлодіод. Пружина відскакує й дає ще кілька фронтів у найближчі мілісекунди — кожен знову зводить прапорець, `loop` його бачить, але `now - lastKnock` тепер маленьке, менше за вікно, тож відскок **тихо з'їдається**. Стук порахований рівно один раз.

Чому саме 60 мс? Це компроміс двох страхів. Замало (скажімо, 10 мс) — і хвіст торохтіння виповзе за вікно, один стук зарахується двічі. Забагато (300 мс) — і два **навмисні** швидкі стуки поспіль зіллються в один, а для замка-на-ритм це смерть: ви не зможете вистукати частий дріб. Пружинне торохтіння KY-031 згасає за одиниці-десяток мілісекунд, тож 40–80 мс надійно накривають брязкіт, лишаючи змогу стукати доволі часто (до ~12–15 ударів за секунду). Зменшуйте вікно, якщо ловите здвоєні спрацювання; збільшуйте, якщо потрібен «чистий» рахунок і швидкий дріб не потрібен.

Одна пастка переносу, про яку мовчать. На Uno й Nano зовнішнє переривання вміють **лише D2 і D3** — почепите S на будь-який інший вивід, і `attachInterrupt` мовчки нічого не зловить (компілятор не свариться, `digitalPinToInterrupt` просто поверне для «не-переривального» піна значення, що ні до чого не прив'язане). Тому S давача заводьте саме на D2 або D3. Якщо всі переривальні виводи вже зайняті, є вихід — переривання за зміною стану (pin-change) є на будь-якому піні, але це вже інша, складніша тема; для одного давача стуку двох апаратних входів вистачає завжди.

## Той самий давач на ESP32: IRAM_ATTR і чому годинник тут не завмирає

Переносимо скетч на ESP32 — і два місця треба поміняти, інакше або не збереться, або поводитиметься дивно.

Перше — **будь-який вивід придатний**. На ESP32 апаратне переривання вміє майже кожен GPIO, тож `digitalPinToInterrupt` тут радше формальність; вибирайте вільну ногу (з обережністю до кількох «особливих» — GPIO 34–39 лише входи без підтяжки, тому для `INPUT_PULLUP` беріть звичайний GPIO, наприклад 4, 5, 18, 19). Друге, і головне, — обробник **мусить** мати атрибут `IRAM_ATTR`. Ось чому: код ESP32 здебільшого лежить у зовнішній флеш-пам'яті, і звернення до неї повільне; ба більше, у моменти, коли флеш зайнята (наприклад, драйвер Wi-Fi щось із неї читає), викликати з неї обробник **не можна взагалі** — це впаде з панікою. `IRAM_ATTR` наказує покласти функцію в швидку внутрішню оперативну пам'ять (IRAM), звідки процесор викликає її миттєво й завжди безпечно. Забудете атрибут — на голому скетчі може й пронесе, але щойно додасте Wi-Fi чи Bluetooth, пристрій почне випадково перезавантажуватись у момент стуку. Це класична, важковловна пастка, тож ставте `IRAM_ATTR` одразу.

І приємна відмінність, що спрощує код: на ESP32 `millis()` та `micros()` читають апаратний лічильник і **працюють усередині обробника** — годинник тут не завмирає, як на AVR. Тож на ESP32 мітку часу можна ставити прямо в обробнику. Але звичка «обробник крихітний, логіка в loop» лишається доброю: тримаймо ту саму структуру.

**Умова.** Вивід S — на GPIO 4, внутрішня підтяжка вгору, активний-НИЗЬКО. Світлодіод — на GPIO 2 (вбудований на багатьох платах DevKit). Ловимо стук перериманням, з локаутом; хочемо, щоб код лишався надійним і поряд із Wi-Fi.

:::tabs

```arduino
const uint8_t KNOCK = 4;              // вивід S — на GPIO4 (на ESP32 годиться майже будь-який)
const uint8_t LED   = 2;              // вбудований світлодіод багатьох DevKit
const unsigned long LOCKOUT = 60;     // глухе вікно, мс

volatile bool     knockFlag = false;  // спільний з обробником — обов'язково volatile
volatile uint32_t knockAt   = 0;      // мітка часу; на ESP32 millis() в ISR працює

// IRAM_ATTR — покласти обробник у швидку внутрішню RAM (обов'язково, надто з Wi-Fi)
void IRAM_ATTR onKnock() {
    knockFlag = true;
    knockAt   = millis();             // на ESP32 годинник в ISR іде — можна мітити тут
}

unsigned long lastKnock = 0;
unsigned long count     = 0;

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);
    pinMode(LED, OUTPUT);
    Serial.begin(115200);
    attachInterrupt(digitalPinToInterrupt(KNOCK), onKnock, FALLING);
}

void loop() {
    if (knockFlag) {
        knockFlag = false;
        uint32_t t = knockAt;         // читаємо мітку, поставлену обробником
        if (t - lastKnock > LOCKOUT) {
            lastKnock = t;
            count++;
            digitalWrite(LED, HIGH);
            Serial.printf("стук #%lu\n", count);
        }
    }
    if (millis() - lastKnock > 30) digitalWrite(LED, LOW);
}
```

```esp-idf
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_timer.h"
#include "esp_log.h"

#define KNOCK       GPIO_NUM_4
#define LED         GPIO_NUM_2
#define LOCKOUT_US  60000

static const char *TAG = "knock";
static QueueHandle_t q;               // ISR → задача, без спільних змінних

/* IRAM_ATTR — той самий припис, що й у скетчі: обробник у внутрішній RAM */
static void IRAM_ATTR on_knock(void *arg) {
    int64_t t = esp_timer_get_time();      // годинник в ISR тут іде — мітимо одразу
    BaseType_t woken = pdFALSE;
    xQueueSendFromISR(q, &t, &woken);      // ISR лише кидає мітку в чергу
    if (woken) portYIELD_FROM_ISR();
}

static void knock_task(void *arg) {
    int64_t t, last = 0;
    unsigned count = 0;
    while (1) {
        if (xQueueReceive(q, &t, pdMS_TO_TICKS(30)) == pdTRUE) {
            if (t - last > LOCKOUT_US) {   // поза глухим вікном — правдивий стук
                last = t;
                count++;
                gpio_set_level(LED, 1);
                ESP_LOGI(TAG, "стук #%u", count);
            }
        } else {
            gpio_set_level(LED, 0);        // 30 мс тиші — гасимо світлодіод
        }
    }
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << KNOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));
    q = xQueueCreate(8, sizeof(int64_t));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(KNOCK, on_knock, NULL));
    xTaskCreate(knock_task, "knock", 3072, NULL, 5, NULL);
}
```

:::

Рідне ESP-IDF робить те саме на щабель суворіше: замість спільного `volatile`-прапорця обробник кидає мітку часу в **чергу** FreeRTOS, а окрема задача її забирає. Прапорець і черга розв'язують ту саму задачу «ISR коротко, робота — потім»; черга ще й сама будить задачу, тож нічого опитувати в циклі не треба. `ESP_INTR_FLAG_IRAM` при встановленні служби переривань — це те саме, що `IRAM_ATTR` на функції: наказ тримати обробник у внутрішній RAM.

Про одну тонкість чесно: `knockFlag` і `knockAt` — це змінні, які пише обробник на одному ядрі, а читає `loop`, можливо, на іншому (ESP32 двоядерний). Для окремого `bool` і окремого 32-бітного `uint32_t` це безпечно: читання й запис 32-бітного слова на ESP32 **атомарні** — не буває, щоб `loop` побачив «пів-значення». Тому спинлок (`portENTER_CRITICAL`) тут не потрібен. Він знадобився б, якби обробник і `loop` ділили **складнішу** структуру — масив, 64-бітне число, кілька зв'язаних полів, які треба прочитати узгоджено. Для нашого простого прапорця з міткою `volatile` достатньо, і код лишається чистим. Тримаймо це як межу: одне слово — `volatile` вистачить; кілька полів разом — обгортайте критичною секцією.

## Від голого «замкнено» до серії стуків

Тепер, коли один удар ловиться надійно й рахується рівно раз, зробимо наступний крок — навчимося чути **ритм**. KY-031 сам по собі ритму не знає: він уміє лише коротко замкнутись. Але маючи надійні моменти стуків із мітками часу, ми легко відновимо те, що людина відстукала: **скільки** було ударів і **які паузи** між ними. Оце і є «серія стуків» — і саме на ній стоїть будь-який замок-на-секретний-стук.

Ідея серії проста: збираємо не самі стуки, а **проміжки між сусідніми стуками**. Три удари «тук … тук-тук» — це два проміжки: довгий і короткий. Саме візерунок проміжків несе ритм; абсолютний темп (швидше чи повільніше відстукали те саме) нас цікавити не повинен, інакше замок вимагатиме від вас щоразу однакової швидкості, а людина так не вміє.

Ось де ховається головне рішення всієї конструкції — **як зрозуміти, що серія скінчилась**. Людина не натисне кнопку «я закінчив»; вона просто перестане стукати. Отже, кінець серії — це **достатньо довга тиша** після останнього стуку. Заводимо поріг, скажімо 800 мс: якщо після стуку 0.8 секунди нічого не сталося — серія завершена, час її розібрати. Коротші паузи — це паузи **всередині** ритму (між ударами того самого візерунка), довша — це «фраза скінчилась».

:::tabs

```arduino
const uint8_t KNOCK = 2;
const unsigned long LOCKOUT   = 60;    // придушення торохтіння, мс
const unsigned long GAP_END   = 800;   // тиша, що означає «серія скінчилась», мс
const uint8_t MAX_KNOCKS      = 12;    // стелю візерунка обмежуємо

volatile bool knockFlag = false;
void onKnock() { knockFlag = true; }

unsigned long lastKnock = 0;           // час останнього зарахованого стуку
unsigned long gaps[MAX_KNOCKS];        // проміжки між сусідніми стуками, мс
uint8_t nGaps  = 0;                    // скільки проміжків набралось
uint8_t nHits  = 0;                    // скільки стуків у поточній серії
bool inSeries  = false;                // чи йде набір серії

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);
    Serial.begin(9600);
    attachInterrupt(digitalPinToInterrupt(KNOCK), onKnock, FALLING);
}

void loop() {
    unsigned long now = millis();

    // 1) зафіксувати новий стук (з локаутом проти торохтіння)
    if (knockFlag) {
        knockFlag = false;
        if (now - lastKnock > LOCKOUT) {
            if (inSeries && nGaps < MAX_KNOCKS) {
                gaps[nGaps++] = now - lastKnock;   // проміжок від попереднього стуку
            }
            lastKnock = now;
            nHits++;
            inSeries = true;
        }
    }

    // 2) достатньо довга тиша після стуку → серія скінчилась, розбираємо
    if (inSeries && now - lastKnock > GAP_END) {
        Serial.print("серія: ");
        Serial.print(nHits);
        Serial.print(" стук(и), проміжки[мс]:");
        for (uint8_t i = 0; i < nGaps; i++) {
            Serial.print(' ');
            Serial.print(gaps[i]);
        }
        Serial.println();
        // скидаємо стан під наступну серію
        nGaps = 0;
        nHits = 0;
        inSeries = false;
    }
}
```

```esp-idf
#include <stdio.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define KNOCK       GPIO_NUM_4
#define LOCKOUT_US   60000     // придушення торохтіння, мкс
#define GAP_END_US  800000     // тиша, що означає «серія скінчилась», мкс
#define MAX_KNOCKS      12     // стелю візерунка обмежуємо

static const char *TAG = "knock";
static volatile bool knock_flag = false;
static void IRAM_ATTR on_knock(void *arg) { knock_flag = true; }

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << KNOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(KNOCK, on_knock, NULL));

    int64_t last = 0, gaps[MAX_KNOCKS];   // проміжки між сусідніми стуками
    int n_gaps = 0, n_hits = 0;
    bool in_series = false;

    while (1) {
        int64_t now = esp_timer_get_time();

        // 1) зафіксувати новий стук (з локаутом проти торохтіння)
        if (knock_flag) {
            knock_flag = false;
            if (now - last > LOCKOUT_US) {
                if (in_series && n_gaps < MAX_KNOCKS) gaps[n_gaps++] = now - last;
                last = now;
                n_hits++;
                in_series = true;
            }
        }

        // 2) достатньо довга тиша після стуку → серія скінчилась, розбираємо
        if (in_series && now - last > GAP_END_US) {
            char buf[96] = "";
            int p = 0;
            for (int i = 0; i < n_gaps; i++)
                p += snprintf(buf + p, sizeof(buf) - p, " %lld", gaps[i] / 1000);
            ESP_LOGI(TAG, "серія: %d стук(и), проміжки[мс]:%s", n_hits, buf);
            n_gaps = 0;
            n_hits = 0;
            in_series = false;
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
```

```stm32
#include "main.h"
#include <stdio.h>                 // printf перенаправлено на UART

#define LOCKOUT   60u              // придушення торохтіння, мс
#define GAP_END  800u              // тиша, що означає «серія скінчилась», мс
#define MAXN      12u              // стелю візерунка обмежуємо

volatile uint8_t knockFlag = 0;
void HAL_GPIO_EXTI_Callback(uint16_t pin) { if (pin == GPIO_PIN_0) knockFlag = 1; }
void EXTI0_IRQHandler(void) { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0); }

int main(void) {
    HAL_Init();
    SystemClock_Config();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin  = GPIO_PIN_0;           // PA0 — вивід S
    g.Mode = GPIO_MODE_IT_FALLING; // переривання на фронті спаду
    g.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &g);
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);

    uint32_t last = 0, gaps[MAXN];  // проміжки між сусідніми стуками, мс
    uint8_t nGaps = 0, nHits = 0, inSeries = 0;

    while (1) {
        uint32_t now = HAL_GetTick();

        // 1) зафіксувати новий стук (з локаутом проти торохтіння)
        if (knockFlag) {
            knockFlag = 0;
            if (now - last > LOCKOUT) {
                if (inSeries && nGaps < MAXN) gaps[nGaps++] = now - last;
                last = now;
                nHits++;
                inSeries = 1;
            }
        }

        // 2) достатньо довга тиша після стуку → серія скінчилась, розбираємо
        if (inSeries && now - last > GAP_END) {
            printf("серія: %u стук(и), проміжки[мс]:", (unsigned)nHits);
            for (uint8_t i = 0; i < nGaps; i++) printf(" %lu", (unsigned long)gaps[i]);
            printf("\r\n");
            nGaps = 0;
            nHits = 0;
            inSeries = 0;
        }
    }
}
```

:::

Простежмо приклад. Ви стукаєте «тук … тук-тук»: перший удар о 1000 мс, другий о 1600 мс, третій о 1750 мс, далі тиша. Перший стук лише запускає серію (`inSeries = true`, проміжок нема — ні від чого міряти). Другий приходить через 600 мс — у `gaps` лягає `600`. Третій через 150 мс — у `gaps` лягає `150`. Далі понад 800 мс нічого — умова тиші спрацьовує, і в монітор виходить: `серія: 3 стук(и), проміжки[мс]: 600 150`. Ми відновили ритм чисто у двох числах.

> 🔧 **Навіщо це.** Серія — це місток від «залізо смикнуло вивід» до «людина щось сказала стуком». Кількість ударів плюс візерунок пауз — уся інформація, яку KY-031 фізично здатний передати (силу він, нагадаю, не розрізняє). З цими двома числовими рядами вже можна порівнювати ритми, будувати команди («два стуки — увімкнути, три — вимкнути»), робити замок. Без кроку «серія» ви лишаєтесь на рівні окремих спалахів і нічого осмисленого з давача не витягнете.

## Замок на секретний стук: співставлення ритму

Складімо все докупи. Замок зберігає **еталонний ритм** — записаний заздалегідь візерунок проміжків. Ви стукаєте свою серію; замок будує її проміжки тим самим кодом, що вище, і **порівнює** з еталоном. Збіглося за ритмом — відмикаємо (блимаємо світлодіодом, клацаємо реле). Не збіглося — мовчимо.

Уся хитрість — у слові «збіглося». Наївне «числа рівні» не годиться геть: людина ніколи не відстукає той самий ритм двічі точно до мілісекунди, ба навіть темп щоразу трохи інший — то швидше, то повільніше. Тому порівнюємо не абсолютні мілісекунди, а **пропорції** проміжків, та ще й **з допуском**. Двокроковий рецепт:

Спершу **нормуємо** серію — ділимо кожен проміжок на найдовший у ній. Тепер ритм заданий не в мілісекундах, а в частках від найповільнішого удару: «повільно-швидко» стане, скажімо, `1.00, 0.25` — і залишиться таким, хоч відстукай ви його вдвічі швидше. Абсолютний темп зникає, лишається чистий візерунок. Далі — **порівняння з допуском**: два нормовані ритми вважаємо однаковими, якщо кожна пара відповідних часток різниться не більш ніж на поріг (наприклад 0.25). Людська рука в цей коридор влучає, а чужий, неправильний ритм — майже ніколи.

Формально, для двох серій однакової довжини з нормованими проміжками `a[i]` та `b[i]`:

```
ключ відчинено ⟺  для кожного i:  |a[i] − b[i]| ≤ TOL
                  і кількість стуків збіглась
                  (TOL ≈ 0.25 — коридор для людської руки)
```

Спершу — окрема функція, що з масиву проміжків робить нормований візерунок і зважує його на еталон. Далі — сам замок, що записує еталон на першу вашу серію (режим навчання) і відмикається на кожну наступну, схожу за ритмом.

:::tabs

```arduino
const uint8_t KNOCK = 2;
const uint8_t LED   = 13;             // «замок»: HIGH = відчинено
const unsigned long LOCKOUT = 60;
const unsigned long GAP_END = 800;
const uint8_t MAXN  = 12;
const float   TOL   = 0.25;           // допуск на частку (безрозмірний)

volatile bool knockFlag = false;
void onKnock() { knockFlag = true; }

unsigned long lastKnock = 0;
unsigned long gaps[MAXN];
uint8_t nGaps = 0, nHits = 0;
bool inSeries = false;

// еталон
unsigned long secretGaps[MAXN];
uint8_t secretN = 0;                  // 0 = ще не навчено
bool learning = true;                 // перша серія стане еталоном

// нормувати проміжки в частки від найдовшого; кладе результат у out[]
void normalize(unsigned long *src, uint8_t n, float *out) {
    unsigned long mx = 1;             // не ділимо на 0
    for (uint8_t i = 0; i < n; i++) if (src[i] > mx) mx = src[i];
    for (uint8_t i = 0; i < n; i++) out[i] = (float)src[i] / (float)mx;
}

// чи збігаються два ритми (однакова к-сть проміжків і кожна частка в допуску)
bool rhythmMatches(unsigned long *a, uint8_t na, unsigned long *b, uint8_t nb) {
    if (na != nb) return false;       // різна кількість стуків — точно не те
    if (na == 0)  return false;       // один стук ритму не має
    float fa[MAXN], fb[MAXN];
    normalize(a, na, fa);
    normalize(b, nb, fb);
    for (uint8_t i = 0; i < na; i++)
        if (fabs(fa[i] - fb[i]) > TOL) return false;   // хоч одна пара вибилась
    return true;
}

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
    attachInterrupt(digitalPinToInterrupt(KNOCK), onKnock, FALLING);
    Serial.println("Відстукайте секретний ритм — він стане ключем.");
}

void loop() {
    unsigned long now = millis();

    if (knockFlag) {
        knockFlag = false;
        if (now - lastKnock > LOCKOUT) {
            if (inSeries && nGaps < MAXN) gaps[nGaps++] = now - lastKnock;
            lastKnock = now;
            nHits++;
            inSeries = true;
        }
    }

    if (inSeries && now - lastKnock > GAP_END) {
        if (learning) {                        // перша серія → запам'ятати як ключ
            for (uint8_t i = 0; i < nGaps; i++) secretGaps[i] = gaps[i];
            secretN  = nGaps;
            learning = false;
            Serial.print("Ключ записано: ");
            Serial.print(nHits);
            Serial.println(" стук(и). Тепер відстукайте його, щоб відчинити.");
        } else {                               // наступні серії → звіряти з ключем
            if (rhythmMatches(gaps, nGaps, secretGaps, secretN)) {
                Serial.println(">>> ВІРНО — відчинено");
                digitalWrite(LED, HIGH);
            } else {
                Serial.println("... не той ритм");
                digitalWrite(LED, LOW);
            }
        }
        nGaps = 0; nHits = 0; inSeries = false;
    }
}
```

```esp-idf
#include <math.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define KNOCK       GPIO_NUM_4
#define LED         GPIO_NUM_2       // «замок»: 1 = відчинено
#define LOCKOUT_US   60000
#define GAP_END_US  800000
#define MAXN            12
#define TOL          0.25f           // допуск на частку (безрозмірний)

static const char *TAG = "lock";
static volatile bool knock_flag = false;
static void IRAM_ATTR on_knock(void *arg) { knock_flag = true; }

/* normalize() і rhythm_matches() — та сама чиста арифметика, що у вкладці
   Arduino (нормувати на найдовший проміжок, звірити частки з допуском):
   платформи вона не стосується, тож тут її не повторюємо */
static void normalize(const int64_t *src, int n, float *out);
static bool rhythm_matches(const int64_t *a, int na, const int64_t *b, int nb);

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << KNOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(KNOCK, on_knock, NULL));
    ESP_LOGI(TAG, "Відстукайте секретний ритм — він стане ключем.");

    int64_t last = 0, gaps[MAXN], secret[MAXN];
    int nGaps = 0, nHits = 0, secretN = 0;
    bool inSeries = false, learning = true;   // перша серія стане еталоном

    while (1) {
        int64_t now = esp_timer_get_time();

        if (knock_flag) {
            knock_flag = false;
            if (now - last > LOCKOUT_US) {
                if (inSeries && nGaps < MAXN) gaps[nGaps++] = now - last;
                last = now; nHits++; inSeries = true;
            }
        }

        if (inSeries && now - last > GAP_END_US) {
            if (learning) {                   // перша серія → запам'ятати як ключ
                for (int i = 0; i < nGaps; i++) secret[i] = gaps[i];
                secretN = nGaps; learning = false;
                ESP_LOGI(TAG, "Ключ записано: %d стук(и). Тепер відстукайте його.", nHits);
            } else if (rhythm_matches(gaps, nGaps, secret, secretN)) {
                ESP_LOGI(TAG, ">>> ВІРНО — відчинено");
                gpio_set_level(LED, 1);
            } else {
                ESP_LOGW(TAG, "... не той ритм");
                gpio_set_level(LED, 0);
            }
            nGaps = 0; nHits = 0; inSeries = false;
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
```

```stm32
#include "main.h"
#include <math.h>
#include <stdio.h>

#define LOCKOUT   60u
#define GAP_END  800u
#define MAXN      12u
#define TOL     0.25f                 // допуск на частку (безрозмірний)

volatile uint8_t knockFlag = 0;
void HAL_GPIO_EXTI_Callback(uint16_t pin) { if (pin == GPIO_PIN_0) knockFlag = 1; }
void EXTI0_IRQHandler(void) { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0); }

/* normalize() і rhythmMatches() — байт-у-байт ті самі, що у вкладці Arduino:
   чиста арифметика над масивом проміжків, HAL до неї стосунку не має */
static void normalize(const uint32_t *src, uint8_t n, float *out);
static uint8_t rhythmMatches(const uint32_t *a, uint8_t na, const uint32_t *b, uint8_t nb);

int main(void) {
    HAL_Init();
    SystemClock_Config();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin  = GPIO_PIN_0;
    g.Mode = GPIO_MODE_IT_FALLING;
    g.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &g);
    g.Pin   = GPIO_PIN_13;            // PC13 — «замок»: SET = відчинено
    g.Mode  = GPIO_MODE_OUTPUT_PP;
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &g);
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    printf("Відстукайте секретний ритм — він стане ключем.\r\n");

    uint32_t last = 0, gaps[MAXN], secret[MAXN];
    uint8_t nGaps = 0, nHits = 0, secretN = 0, inSeries = 0, learning = 1;

    while (1) {
        uint32_t now = HAL_GetTick();

        if (knockFlag) {
            knockFlag = 0;
            if (now - last > LOCKOUT) {
                if (inSeries && nGaps < MAXN) gaps[nGaps++] = now - last;
                last = now; nHits++; inSeries = 1;
            }
        }

        if (inSeries && now - last > GAP_END) {
            if (learning) {                   // перша серія → запам'ятати як ключ
                for (uint8_t i = 0; i < nGaps; i++) secret[i] = gaps[i];
                secretN = nGaps; learning = 0;
                printf("Ключ записано: %u стук(и). Тепер відстукайте його.\r\n",
                       (unsigned)nHits);
            } else if (rhythmMatches(gaps, nGaps, secret, secretN)) {
                printf(">>> ВІРНО — відчинено\r\n");
                HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
            } else {
                printf("... не той ритм\r\n");
                HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
            }
            nGaps = 0; nHits = 0; inSeries = 0;
        }
    }
}
```

:::

Прочитаймо, як він живе. Перша серія після ввімкнення потрапляє в гілку `learning`: її проміжки копіюються в `secretGaps`, і це віднині ключ. Кожна наступна серія йде у `rhythmMatches`: спершу відсів за кількістю стуків (якщо ударів не стільки — одразу «не те», навіть не рахуючи паузи), тоді обидва ритми нормуються й порівнюються частка до частки. Відстукали «повільно-швидко» на реєстрації, а тепер повторили вдвічі бадьоріше, але з тією ж пропорцією, — нормування зітре різницю темпу, частки збіжаться в межах допуску, замок відчиниться. Спробував хтось інший навмання — кількість стуків або пропорції не влучать у коридор, і замок промовчить.

Кілька чесних меж цієї схеми, щоб не видавати її за більше, ніж вона є. Це **не криптографія**, а зручність: секретний стук захищає від випадкового перехожого, а не від того, хто підгляне ваш ритм і повторить. KY-031 не знає сили удару, тож «тихо-голосно» в ключ закласти не вийде — лише кількість і паузи. Один-єдиний стук ритму не має (нема проміжків), тож замок вимагає щонайменше двох ударів — це закладено перевіркою `na == 0`. І пам'ять тут летка: після перезавантаження ключ забувається й вивчається наново; щоб він жив між увімкненнями, еталонні проміжки треба зберегти в незалежну пам'ять (EEPROM на AVR, `Preferences`/NVS на ESP32, окрема сторінка флеш або backup-регістри на STM32) — це прямий, але вже окремий доробок.

> 🔧 **Навіщо це.** Тут видно, чому «серія» була варта окремого кроку: замок — це лише тонка надбудова (нормування + допуск) над готовим потоком проміжків. Той самий потік однаково живить голосове «два стуки — світло», лічильник постуків у двері чи журнал подій. Побудувавши надійне ловіння одного стуку й чистий збір серії, ви дістаєте не один пристрій, а цілий клас — усе, де людина спілкується з приладом ритмом.

## Пастки, що з'їдають вечір

Зберемо в одне місце те, на чому реально гальмують, — з причиною й ліками, бо кожен з цих пунктів виглядає як «давач зламався», а насправді це передбачувана дрібниця в коді.

**Проґавлений стук у повільному циклі.** Симптом: у порожньому скетчі все ловиться, а в «справжній» програмі давач мовчить. Причина: `digitalRead` опитує вивід рідше, ніж триває 2-мілісекундне замикання. Ліки: читати **перериманням** на фронті спаду (`attachInterrupt … FALLING` у скетчі, `GPIO_INTR_NEGEDGE` в ESP-IDF, `GPIO_MODE_IT_FALLING` у STM32 HAL), а не опитуванням; обробник лише зводить `volatile`-прапорець.

**Один стук рахується кілька разів.** Симптом: тук — а лічильник +3. Причина: пружина відскакує й дає чергу фронтів спаду ([брязкіт контактів](topic:electronics/contact-debounce)). Ліки: **вікно-локаут** над зафіксованою подією — зарахувавши стук, ігнорувати вхід 40–80 мс.

**Прапорець «не бачиться» головним циклом.** Симптом: обробник явно спрацьовує (можна помітити осцилографом чи блиманням прямо в ISR для перевірки), а `loop` наче сліпий. Причина: прапорець **не** `volatile`, компілятор закешував його. Ліки: усі змінні, спільні між обробником і `loop`, оголошувати `volatile`.

**ESP32 випадково перезавантажується на стуку.** Симптом: голий скетч працює, з Wi-Fi/BLE — паніка й ребут у момент удару. Причина: обробник без `IRAM_ATTR` намагаються викликати з флеш-пам'яті, поки та зайнята. Ліки: **`void IRAM_ATTR onKnock()`** — покласти обробник у внутрішню RAM.

**`attachInterrupt` мовчить на AVR.** Симптом: на Uno/Nano переривання не приходять узагалі. Причина: S почеплено не на переривальний вивід. Ліки: на Uno/Nano зовнішнє переривання — **лише D2 і D3**; заводьте S туди (або переходьте на pin-change interrupt, якщо обидва зайняті).

**Рівень спокою «плаває» від плати.** Симптом: без стуку вхід то 1, то 0, спрацювання самі собою. Причина: покладаються на онбордний резистор плати, а він розведений по-різному (а на дешевих копіях його й нема), тож вивід почасти «висить» — [підтяжки](topic:electronics/floating-pullups) бракує. Ліки: **не гадати про плату**, вмикати внутрішню підтяжку вгору (`INPUT_PULLUP` · `GPIO_PULLUP_ENABLE` · `GPIO_PULLUP`) і читати активним-НИЗЬКО — тоді спокій гарантовано в одиниці незалежно від розводки.

**Два швидкі навмисні стуки зливаються в один.** Симптом: у ритмі не виходить вистукати частий дріб. Причина: вікно-локаут завелике й з'їдає правдивий швидкий стук разом із торохтінням. Ліки: зменшити `LOCKOUT` до нижньої межі, що ще накриває брязкіт (спробуйте 40 мс); балансуйте його проти появи здвоєних спрацювань.

**Хочу знати силу удару.** Симптом: намагаєтесь відрізнити слабкий стук від сильного — не виходить. Причина: KY-031 має цифровий вихід «замкнено/розімкнено», сили не міряє в принципі. Ліки: це не до нього — силу дає **п'єзодавач** через АЦП; KY-031 передає лише факт стуку та його ритм.

Наскрізна нитка всіх пасток одна: KY-031 — це вимикач, який на мить замикає удар, і всі труднощі ростуть із двох його рис — замикання коротке (звідси переривання) і брязке (звідси локаут). Тримайте ці дві думки в голові, і давач із «капризного» стає передбачуваним інструментом, що чисто чує стук і навіть його ритм.
