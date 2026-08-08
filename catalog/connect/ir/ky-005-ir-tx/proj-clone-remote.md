# ⚙️ Клон пульта: зняти код рідного пульта й повторити його через KY-005

<preknowlist>
- [Модуляція несучої 38 кГц](book:communications/carrier-ir-modulation) — біт «одиниця» — це не постійне світло, а пачка мигання на 38 кГц; приймач ловить лише цю частоту.
- [Приймач VS1838B](book:connect/vs1838b-ir-rx) — трипіновий ІЧ-приймач, яким на кроці 1 «підслуховують» рідний пульт.
- [IRremote для KY-005: підключення й виклики](book:connect/ky-005-ir-tx/api-irremote-nec.md) — як підключити бібліотеку (`.hpp`, `IrSender.begin(pin)`) і що означають аргументи `sendNEC`.
</preknowlist>

Ось те, заради чого KY-005 найчастіше й тримають на столі: перетворити плату на клон вашого власного пульта, який десь загубився чи розсипав кнопки. Робиться це в **два кроки** — спершу приймачем підслухати, потім передавачем повторити, — і бібліотека тут робить дивовижно приємну річ: вона сама пише вам готовий рядок коду для передачі.

**Крок 1. Слухаємо пульт.** Беремо будь-який ІЧ-приймач (той самий VS1838B/KY-022) і вішаємо його на ногу, яка вміє помічати обидва фронти — через зовнішнє переривання або через захоплення таймера; більше від мікроконтролера тут нічого не треба (в Arduino нехай це буде вивід 2, на ESP32 — канал RMT, на STM32 — вхід таймера). Далі заливаємо крихітну програму-«слухача» і по черзі тиснемо кнопки живого пульта, наводячи його на приймач:

:::tabs
```arduino
#include <IRremote.hpp>

const int PIN_RECV = 2;   // сюди підключений ІЧ-ПРИЙМАЧ (не передавач!)

void setup() {
    Serial.begin(115200);
    IrReceiver.begin(PIN_RECV, ENABLE_LED_FEEDBACK);   // почати приймання
    Serial.println("Тисни кнопки пульта...");
}

void loop() {
    if (IrReceiver.decode()) {            // прийнято повний кадр?
        IrReceiver.printIRResultShort(&Serial);   // що це було (протокол/адреса/команда)
        IrReceiver.printIRSendUsage(&Serial);     // ГОТОВИЙ рядок, ЯКИМ це переслати
        Serial.println();
        IrReceiver.resume();              // готові ловити наступну кнопку
    }
}
```
```esp-idf
#include "driver/rmt_rx.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "ir_nec_encoder.h"   // nec_parse_frame() — з прикладу rmt/ir_nec_transceiver

#define PIN_RECV GPIO_NUM_2   // сюди підключений ІЧ-ПРИЙМАЧ (не передавач!)
static QueueHandle_t q;
static rmt_symbol_word_t symbols[64];

// колбек з ISR: кадр дочитано, віддаємо його задачі
static bool on_done(rmt_channel_handle_t ch, const rmt_rx_done_event_data_t *ed, void *arg) {
    BaseType_t hp = pdFALSE;
    xQueueSendFromISR(q, ed, &hp);
    return hp == pdTRUE;
}

void app_main(void) {
    q = xQueueCreate(4, sizeof(rmt_rx_done_event_data_t));
    rmt_channel_handle_t rx = NULL;
    rmt_rx_channel_config_t cfg = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000,          // 1 тик = 1 мкс
        .mem_block_symbols = 64,
        .gpio_num = PIN_RECV,
    };
    ESP_ERROR_CHECK(rmt_new_rx_channel(&cfg, &rx));
    rmt_rx_event_callbacks_t cbs = { .on_recv_done = on_done };
    ESP_ERROR_CHECK(rmt_rx_register_event_callbacks(rx, &cbs, NULL));
    ESP_ERROR_CHECK(rmt_enable(rx));

    const rmt_receive_config_t rcfg = {
        .signal_range_min_ns = 1250,       // коротше — то шум
        .signal_range_max_ns = 12000000,   // довше — то вже кінець кадру
    };
    ESP_LOGI("ir", "Тисни кнопки пульта...");
    while (1) {
        ESP_ERROR_CHECK(rmt_receive(rx, symbols, sizeof(symbols), &rcfg));
        rmt_rx_done_event_data_t ed;
        xQueueReceive(q, &ed, portMAX_DELAY);      // прийнято повний кадр
        uint16_t addr, cmd;
        if (nec_parse_frame(ed.received_symbols, ed.num_symbols, &addr, &cmd))
            ESP_LOGI("ir", "NEC address=0x%02X command=0x%02X", addr, cmd);
    }
}
```
```stm32
/* TIM3: лічильник на 1 МГц (1 тик = 1 мкс), CH1 — захоплення на ОБОХ фронтах.
   Вхід CH1 — вихід ІЧ-приймача. nec_decode() — свій десяток рядків: біт = 1,
   якщо пауза після імпульсу ≈1690 мкс, і 0, якщо ≈560 мкс. */
extern TIM_HandleTypeDef htim3;

#define MAX_GAPS 140
static uint16_t gap[MAX_GAPS];        // тривалості імпульсів і пауз, мкс
static volatile uint16_t n_gaps;
static uint16_t prev;

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
    uint16_t now = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
    if (n_gaps < MAX_GAPS) gap[n_gaps++] = now - prev;   // різниця й є тривалість
    prev = now;
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM3_Init(); MX_USART2_UART_Init();
    HAL_TIM_IC_Start_IT(&htim3, TIM_CHANNEL_1);          // почати приймання
    printf("Тисни кнопки пульта...\r\n");

    while (1) {
        HAL_Delay(100);                   // пауза довша за міжкадрову — кадр завершився
        if (n_gaps > 66) {                // NEC: преамбула + 32 біти
            uint8_t addr, cmd;
            if (nec_decode(gap, n_gaps, &addr, &cmd))
                printf("NEC address=0x%02X command=0x%02X\r\n", addr, cmd);
        }
        n_gaps = 0;                       // готові ловити наступну кнопку
    }
}
```
:::

В Arduino-варіанті тут працюють дві функції, що коштують золота. `printIRResultShort` друкує в монітор порту, що саме приймач розпізнав, а `printIRSendUsage` — і в цьому вся краса — друкує **готовий виклик**, яким цю кнопку слати назад. Ви тиснете, скажімо, «гучність +», а в моніторі з'являється:

```
Protocol=NEC Address=0xF1 Command=0x76 Raw-Data=0x89760EF1 32 bits LSB first
Send with: IrSender.sendNEC(0xF1, 0x76, <numberOfRepeats>);
```

Другий рядок — це буквально код, який лишається скопіювати. Не треба гадати адресу, не треба розшифровувати hex вручну — бібліотека вже все розібрала й подала на тарілці. Проходите так усі потрібні кнопки, виписуєте їхні рядки — і у вас готова таблиця команд вашого пульта. Готовий рядок друкує саме ця бібліотека; але цінність не в рядку, а в парі **адреса + команда**, яку ви щойно зняли, — на ESP-IDF чи STM32 ви виписуєте ту саму пару з розібраного кадру й підставляєте її у свій передавач.

**Крок 2. Повторюємо передавачем.** Тепер знімаємо приймач і ставимо на його місце (через резистор) наш KY-005 — на ногу, яка вміє видавати несучу 38 кГц: це або апаратний ШІМ/таймер, або бібліотека, що робить те саме програмно (в Arduino нехай це буде вивід 3). Лишається вставити зняті адресу й команду, підмінивши `<numberOfRepeats>` на потрібне число:

:::tabs
```arduino
#include <IRremote.hpp>

void setup() {
    IrSender.begin(3);   // KY-005 через резистор на виводі 3
}

void loop() {
    // рядки, які нам надрукував printIRSendUsage — просто вставлені сюди:
    IrSender.sendNEC(0xF1, 0x76, 0);   // «гучність +», зняте з рідного пульта
    delay(2000);
    IrSender.sendNEC(0xF1, 0x77, 0);   // «гучність −»
    delay(2000);
}
```
```esp-idf
#include "driver/rmt_tx.h"
#include "freertos/FreeRTOS.h"
#include "ir_nec_encoder.h"        // енкодер NEC з прикладу rmt/ir_nec_transceiver

#define PIN_SEND GPIO_NUM_3        // KY-005 через резистор

void app_main(void) {
    rmt_channel_handle_t tx = NULL;
    rmt_tx_channel_config_t cfg = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000,   // 1 тик = 1 мкс
        .mem_block_symbols = 64,
        .trans_queue_depth = 4,
        .gpio_num = PIN_SEND,
    };
    ESP_ERROR_CHECK(rmt_new_tx_channel(&cfg, &tx));

    rmt_carrier_config_t carrier = { .frequency_hz = 38000, .duty_cycle = 0.33 };
    ESP_ERROR_CHECK(rmt_apply_carrier(tx, &carrier));   // несучу робить залізо

    rmt_encoder_handle_t nec = NULL;
    ir_nec_encoder_config_t enc = { .resolution = 1000000 };
    ESP_ERROR_CHECK(rmt_new_ir_nec_encoder(&enc, &nec));
    ESP_ERROR_CHECK(rmt_enable(tx));

    rmt_transmit_config_t tcfg = { .loop_count = 0 };
    // зняті адреса й команда — просто вставлені сюди:
    ir_nec_scan_code_t up = { .address = 0xF1, .command = 0x76 };   // «гучність +»
    ir_nec_scan_code_t dn = { .address = 0xF1, .command = 0x77 };   // «гучність −»
    while (1) {
        ESP_ERROR_CHECK(rmt_transmit(tx, nec, &up, sizeof(up), &tcfg));
        vTaskDelay(pdMS_TO_TICKS(2000));
        ESP_ERROR_CHECK(rmt_transmit(tx, nec, &dn, sizeof(dn), &tcfg));
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
```
```stm32
/* TIM1_CH1 → нога KY-005: ШІМ 38 кГц зі шпаруватістю ≈1/3.
   «Імпульс» — це увімкнена несуча, «пауза» — вимкнена. delay_us() — свій
   лічильник (DWT->CYCCNT або вільний таймер), бо HAL_Delay() міряє мілісекунди. */
extern TIM_HandleTypeDef htim1;

static void mark(uint16_t us)  { HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1); delay_us(us); }
static void space(uint16_t us) { HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_1);  delay_us(us); }

static void send_nec(uint8_t addr, uint8_t cmd) {
    uint32_t frame = addr | (uint32_t)(uint8_t)~addr << 8 |
                     (uint32_t)cmd << 16 | (uint32_t)(uint8_t)~cmd << 24;
    mark(9000); space(4500);                        // преамбула NEC
    for (int i = 0; i < 32; i++) {                  // молодшим бітом уперед
        mark(560);
        space(((frame >> i) & 1) ? 1690 : 560);     // довга пауза = «1»
    }
    mark(560);                                      // завершальний імпульс
    HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_1);
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM1_Init();
    while (1) {
        // зняті адреса й команда — просто вставлені сюди:
        send_nec(0xF1, 0x76);   // «гучність +», зняте з рідного пульта
        HAL_Delay(2000);
        send_nec(0xF1, 0x77);   // «гучність −»
        HAL_Delay(2000);
    }
}
```
:::

Усе. Плата тепер шле точнісінько ті самі кадри, що й фабричний пульт, — бо ви не вигадували коди, а зняли справжні. Це найнадійніший шлях: жодних довідників, жодних здогадів про адресу; що приймач почув від пульта, те передавач і повторить.

А що робити, коли `printIRResultShort` пише `Protocol=UNKNOWN`? Це значить, що пульт говорить протоколом, якого бібліотека не знає в обличчя (часто так з пультами кондиціонерів — там довгі нестандартні кадри). Тоді розпізнати за протоколом не вийде, але **сирі таймінги** імпульсів приймач усе одно записав, і їх можна тупо відтворити «як є» — прогнавши той самий масив тривалостей крізь генератор несучої: в Arduino це `IrSender.sendRaw(...)`, на ESP32 — ті самі `rmt_symbol_word_t` у `rmt_transmit()`, на STM32 — той-таки масив, поданий парами «імпульс — пауза». Клон вийде точний, хоч і без розуміння, що за протокол; для «повторити цю конкретну кнопку» цього досить.

> Другий бік цієї лінії — сам приймач, який ловить пачки й перетворює мигання назад у логічні рівні (звідки бібліотека вже дістає протокол, адресу й команду): [приймач VS1838B](book:connect/vs1838b-ir-rx). Саме його ставлять на «крок 1», щоб підслухати рідний пульт.
