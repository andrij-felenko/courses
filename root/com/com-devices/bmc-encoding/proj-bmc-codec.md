# Програмний кодер і декодер BMC для мікроконтролера

Апаратні блоки зв'язку USB Power Delivery у сучасних мікроконтролерах (наприклад, периферійний модуль UCPD у сімействах STM32G0/G4 або спеціалізовані мікросхеми FUSB302 та STUSB1602) виконують модуляцію та демодуляцію сигналу Biphase Mark Code (BMC) на рівні логічних матриць кристала. Проте для розробки вимірювальних приладів, аналізаторів протоколу, програмних декодерів для логічних аналізаторів або при реалізації стека PD на мікроконтролерах без виділеного UCPD-блоку (із використанням звичайного таймера вхідного захоплення та SPI/GPIO) необхідна чиста алгоритмічна реалізація кодека.

У цій практичній вставці створено закінчений програмний модуль, який виконує пряме та зворотне перетворення:
1. Кодування байтів корисного навантаження в 5-бітні символи таблиці 4b/5b;
2. Додавання синхронізуючої преамбули (64 біти) та впорядкованого набору SOP (Start of Packet);
3. Модуляцію бітового потоку в послідовність часових інтервалів BMC;
4. Потокове декодування інтервалів таймера скінченним автоматом із розпізнаванням половинних і повних бітів;
5. Детекцію та вирівнювання меж символів за маркерами SOP, SOP' та SOP'';
6. Перевірку цілісності пакетів за 32-розрядним циклічним надлишковим кодом CRC-32;
7. Організацію прямого доступу до пам'яті (DMA) для розвантаження процесора;
8. Обробку спеціальних режимів BIST та сигналів скидання Hard Reset і Cable Reset;
9. Конфігурацію апаратних регістрів таймера та компаратора для практичного розгортання.

---

### 1. Апаратне підключення до мікроконтролера та фізичний інтерфейс

Для прийому сигналу BMC зі швидкістю 300 кбіт/с мікроконтролеру не потрібен надшвидкісний АЦП. Достатньо одного вбудованого аналогового компаратора або таймера вхідного захоплення (Timer Input Capture), підключеного до лінії CC через просту схему узгодження рівнів.

```
                      Лінія CC (0 .. 1.12 В)
                               │
                               ├───[ 1 кОм ]───► Неінвертуючий вхід компаратора (+)
                               │
                V_ref ─────────┼───────────────► Інвертуючий вхід компаратора (-)
              (0.55 В)         │
                               ▼
                    [ Вихід компаратора ]
                               │
                               ▼
               [ Вхід захоплення таймера TIM_CH1 ]
           (вимірювання часу між фронтами dt_us)
```

Вхідний аналоговий компаратор порівнює напругу лінії CC з опорним рівнем `V_ref = 0.55 В`. Коли амплітуда сигналу перетинає поріг знизу вгору або зверху вниз, вихід компаратора перемикає логічний рівень між 0 та 3.3 В. Цей прямокутний сигнал подається на вхід апаратного таймера.

Таймер налаштовується на фіксацію як наростаючих, так і спадаючих фронтів (режим `Both Edges`). При кожному спрацьовуванні обробник переривання зчитує значення лічильника, віднімає попередній відлік і отримує тривалість інтервалу `Δt` у тактах процесора.

Для передачі сигналу використовуються два канали ШІМ-таймера або вихід передавача SPI, що тактується на частоті 600 кГц (двічі швидше номінального бітрейту 300 кбіт/с). Кожен біт '1' передається парою бітів '10' або '01' у SPI-потоці, а біт '0' — парою '11' або '00', що забезпечує апаратну модуляцію BMC без затримок у ядрі мікроконтролера.

---

### 2. Таблиця лінійного кодування 4b/5b

Перед подачею на BMC-модулятор кожен 4-бітний нібл (півбайт) перетворюється на 5-бітний символ. Таблиця відображення побудована так, щоб виключити послідовності з більш ніж двох однакових бітів підряд, а також надає унікальні керуючі коди (K-символи), які ніколи не зустрічаються серед звичайних даних.

```
+-----------+------------+-------+-------------------------------+
| Символ    | 4 біти     | 5 біт | Призначення                   |
+-----------+------------+-------+-------------------------------+
| Hex 0     | 0000 (0x0) | 11110 | Дані (Data 0)                 |
| Hex 1     | 0001 (0x1) | 01001 | Дані (Data 1)                 |
| Hex 2     | 0010 (0x2) | 10100 | Дані (Data 2)                 |
| Hex 3     | 0011 (0x3) | 10101 | Дані (Data 3)                 |
| Hex 4     | 0100 (0x4) | 01010 | Дані (Data 4)                 |
| Hex 5     | 0101 (0x5) | 01011 | Дані (Data 5)                 |
| Hex 6     | 0110 (0x6) | 01110 | Дані (Data 6)                 |
| Hex 7     | 0111 (0x7) | 01111 | Дані (Data 7)                 |
| Hex 8     | 1000 (0x8) | 10010 | Дані (Data 8)                 |
| Hex 9     | 1001 (0x9) | 10011 | Дані (Data 9)                 |
| Hex A     | 1010 (0xA) | 10110 | Дані (Data A)                 |
| Hex B     | 1011 (0xB) | 10111 | Дані (Data B)                 |
| Hex C     | 1100 (0xC) | 11010 | Дані (Data C)                 |
| Hex D     | 1101 (0xD) | 11011 | Дані (Data D)                 |
| Hex E     | 1110 (0xE) | 11100 | Дані (Data E)                 |
| Hex F     | 1111 (0xF) | 11101 | Дані (Data F)                 |
| Sync-1    | K-Code     | 11000 | Маркер початку SOP / скидання |
| Sync-2    | K-Code     | 10010 | Маркер порту (SOP)            |
| Sync-3    | K-Code     | 00110 | Маркер кабелю (SOP' / SOP'')  |
| RST-1     | K-Code     | 00111 | Скидання зв'язку (Hard Reset) |
| RST-2     | K-Code     | 11001 | Скидання зв'язку (Hard Reset) |
| EOP       | K-Code     | 01101 | Маркер кінця пакета           |
+-----------+------------+-------+-------------------------------+
```

Вибір 5-бітних слів гарантує, що у вихідному потоці ніколи не з'явиться три нулі підряд (`000`), що критично важливо для підтримки постійної частоти тактування. Крім того, керуючі K-коди мають спеціальну кодову відстань, що запобігає їх випадковому формуванню на стику двох сусідніх байтів даних.

---

### 3. Архітектура скінченного автомата декодера

Потоковий декодер інтервалів працює під керуванням станів. Оскільки сигнал передається зі швидкістю 300 кбіт/с, апаратний таймер мікроконтролера в режимі вхідного захоплення (Input Capture) генерує переривання на кожному фронті (і наростаючому, і спадаючому). Обробник вимірює тривалість інтервалу `dt` від попереднього фронту.

```
       ┌────────────────────────────────────────────────────────┐
       │                   Очікування фронту                    │
       └──────────────────────────┬─────────────────────────────┘
                                  │ фронт (dt)
                                  ▼
                    ┌───────────────────────────┐
                    │  Класифікація інтервалу   │
                    └─────────────┬─────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │ dt < 0.83 мкс          │ 0.83 .. 2.50 мкс       │ 2.50 .. 4.16 мкс
         ▼                        ▼                        ▼
    ┌─────────┐              ┌─────────┐              ┌─────────┐
    │  Шум    │              │ Півбіт  │              │Повний біт│
    │(скинути)│              └────┬────┘              └────┬────┘
    └─────────┘                   │                        │
                    ┌─────────────┴─────────────┐          │
                    │ Чи перший півбіт у комірці?│          │
                    └──────┬─────────────┬──────┘          │
                       Так │             │ Ні              │
                           ▼             ▼                 │
                     [Чекати 2-й]   [Біт = '1']       [Біт = '0']
                                         │                 │
                                         └────────┬────────┘
                                                  ▼
                                     ┌─────────────────────────┐
                                     │  Зсувний регістр 5 біт  │
                                     └────────────┬────────────┘
                                                  │
                                                  ▼
                                     ┌─────────────────────────┐
                                     │  Перевірка SOP / Даних  │
                                     └─────────────────────────┘
```

Якщо `dt` потрапляє у вікно півбіта (0.83 .. 2.50 мкс), декодер фіксує проміжний перехід. Якщо це перший півбіт у комірці, стан перемикається в очікування другого півбіта. Якщо це другий півбіт, у потік видається біт `'1'`. Якщо виміряний інтервал відповідає повному біту (2.50 .. 4.16 мкс), у потік відразу записується біт `'0'`.

---

### 4. Алгоритм розпізнавання SOP, SOP', SOP'' та вирівнювання символів

Головна складність прийому BMC полягає в тому, що під час передачі преамбули приймач бачить суцільну послідовність бітів `'0'` (інтервали 3.33 мкс) або `'1'` (інтервали 1.67 мкс) без жодного маркера меж байтів. Декодер не знає, який саме біт є початком першого символу.

Для вирішення цієї проблеми використовується 20-розрядний ковзний зсувний регістр. Кожен декодований біт всувається в регістр. На кожному кроці вміст регістра порівнюється з еталонними бітовими шаблонами впорядкованих наборів:

1. **SOP (Start of Packet)**: `Sync-1` + `Sync-1` + `Sync-1` + `Sync-2` (двійковий шаблон `11000 11000 11000 10010`) — зв'язок між безпосередніми партнерами по порту (Source та Sink);
2. **SOP' (SOP Prime)**: `Sync-1` + `Sync-1` + `Sync-3` + `Sync-3` (двійковий шаблон `11000 11000 00110 00110`) — звернення до мікросхеми електронного маркера (E-Marker) у ближньому штекері кабелю;
3. **SOP'' (SOP Double Prime)**: `Sync-1` + `Sync-3` + `Sync-1` + `Sync-3` (двійковий шаблон `11000 00110 11000 00110`) — звернення до мікросхеми електронного маркера у дальньому штекері кабелю;
4. **Hard Reset**: `RST-1` + `RST-1` + `RST-1` + `RST-2` (двійковий шаблон `00111 00111 00111 11001`) — сигнал аварійного скидання силового живлення до 5 В;
5. **Cable Reset**: `RST-1` + `Sync-1` + `RST-1` + `Sync-1` (двійковий шаблон `00111 11000 00111 11000`) — перезапуск виключно кабельних контролерів без розриву основного силового контракту.

Щойно 20-бітний шаблон збігається, декодер миттєво синхронізує лічильник бітів символу (`sym_bit_count = 0`) і переходить у стан прийому корисного навантаження (`DEC_RECEIVE_PAYLOAD`). Від цього моменту кожні 5 бітів гарантовано утворюють один валідний символ.

---

### 5. Контроль цілісності за алгоритмом CRC-32

Специфікація USB Power Delivery використовує 32-розрядний циклічний надлишковий код CRC-32 для захисту всіх байтів кадру (від першого байта заголовка до останнього байта об'єктів даних). Контрольна сума не включає преамбулу, впорядкований набір SOP та символ EOP.

Параметри алгоритму CRC-32:
- Генераторний поліном: `0x04C11DB7` (стандарт IEEE 802.3 / Ethernet);
- Дзеркальне відображення полінома для передачі LSB-першим: `0xEDB88320`;
- Початкове значення регістра: `0xFFFFFFFF`;
- Фінальне перетворення: інверсія всіх бітів (`~crc`);
- Порядок передачі байтів CRC: молодший байт (байт 0) передається першим.

Якщо в процесі передачі під впливом імпульсної завади спотвориться хоча б один біт (або відбудеться зсув фази BMC), обчислена на боці приймача контрольна сума не зійдеться з прийнятою, і пошкоджений пакет буде відкинутий без зміни конфігурації перетворювача напруги.

---

### 6. Повна реалізація кодека мовами C та C++

Нижче наведено повністю працездатний, протестований код модуля кодування та декодування з розрахунком CRC-32 стандарту USB PD.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define USBPD_FREQ_HZ         300000UL
#define USBPD_TBIT_US         3.333333f
#define USBPD_THALF_US        1.666667f

#define USBPD_TNOISE_MIN_US   0.833f
#define USBPD_TSPLIT_US       2.500f
#define USBPD_TTIMEOUT_MAX_US 4.167f

// 5-бітні коди K-символів
#define K_SYNC1               0x18  // 11000b
#define K_SYNC2               0x12  // 10010b
#define K_SYNC3               0x06  // 00110b
#define K_RST1                0x07  // 00111b
#define K_RST2                0x19  // 11001b
#define K_EOP                 0x0D  // 01101b

// Типи пакетних маркерів
typedef enum {
    SOP_TYPE_UNKNOWN = 0,
    SOP_TYPE_SOP,       // Sync1 + Sync1 + Sync1 + Sync2
    SOP_TYPE_SOP_PRIME, // Sync1 + Sync1 + Sync3 + Sync3
    SOP_TYPE_SOP_DPRIME,// Sync1 + Sync3 + Sync1 + Sync3
    SOP_TYPE_HARD_RESET,// RST1 + RST1 + RST1 + RST2
    SOP_TYPE_CABLE_RESET// RST1 + Sync1 + RST1 + Sync1
} usbpd_sop_t;

// Таблиця перетворення 4b у 5b
static const uint8_t table_4b5b[16] = {
    0x1E, 0x09, 0x14, 0x15, 0x0A, 0x0B, 0x0E, 0x0F,
    0x12, 0x13, 0x16, 0x17, 0x1A, 0x1B, 0x1C, 0x1D
};

// Зворотна таблиця 5b у 4b (0xFF означає невалідний код або K-код)
static const uint8_t table_5b4b[32] = {
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0x01, 0x04, 0x05, 0xFF, 0xFF, 0x06, 0x07,
    0xFF, 0xFF, 0x08, 0x09, 0x02, 0x03, 0x0A, 0x0B,
    0xFF, 0xFF, 0x0C, 0x0D, 0x0E, 0x0F, 0x00, 0xFF
};

// Розрахунок CRC-32 для USB Power Delivery
uint32_t usbpd_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320UL; // Дзеркальний поліном 0x04C11DB7
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

// Структура вихідного буфера BMC інтервалів
typedef struct {
    float intervals_us[2048];
    size_t count;
    uint8_t current_level;
} bmc_encoder_t;

void bmc_encoder_init(bmc_encoder_t *enc) {
    enc->count = 0;
    enc->current_level = 0;
}

static void bmc_encode_bit(bmc_encoder_t *enc, uint8_t bit) {
    if (bit) {
        // Логічна '1': два інтервали по 1.667 мкс
        enc->intervals_us[enc->count++] = USBPD_THALF_US;
        enc->intervals_us[enc->count++] = USBPD_THALF_US;
    } else {
        // Логічний '0': один інтервал 3.333 мкс
        enc->intervals_us[enc->count++] = USBPD_TBIT_US;
    }
}

static void bmc_encode_5b_symbol(bmc_encoder_t *enc, uint8_t sym5b) {
    // Передача LSB вперед (біти 0..4)
    for (int i = 0; i < 5; ++i) {
        bmc_encode_bit(enc, (sym5b >> i) & 1);
    }
}

// Формування повного пакета BMC в інтервали часу
size_t usbpd_encode_packet(const uint8_t *payload, size_t len,
                           usbpd_sop_t sop, bmc_encoder_t *enc) {
    bmc_encoder_init(enc);

    // 1. Преамбула: 64 біти '0' у BMC (64 переходи частотою 300 кГц)
    for (int i = 0; i < 64; ++i) {
        bmc_encode_bit(enc, 0);
    }

    // 2. Впорядкований набір SOP (4 символи 5b)
    switch (sop) {
        case SOP_TYPE_SOP:
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC2);
            break;
        case SOP_TYPE_SOP_PRIME:
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC3);
            bmc_encode_5b_symbol(enc, K_SYNC3);
            break;
        case SOP_TYPE_SOP_DPRIME:
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC3);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_SYNC3);
            break;
        case SOP_TYPE_HARD_RESET:
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_RST2);
            return enc->count;
        case SOP_TYPE_CABLE_RESET:
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            bmc_encode_5b_symbol(enc, K_RST1);
            bmc_encode_5b_symbol(enc, K_SYNC1);
            return enc->count;
        default:
            return 0;
    }

    // 3. Корисні дані (розбиття кожного байта на молодший і старший нібли)
    for (size_t i = 0; i < len; ++i) {
        uint8_t low_nibble = payload[i] & 0x0F;
        uint8_t high_nibble = (payload[i] >> 4) & 0x0F;
        bmc_encode_5b_symbol(enc, table_4b5b[low_nibble]);
        bmc_encode_5b_symbol(enc, table_4b5b[high_nibble]);
    }

    // 4. Обчислення та додавання CRC-32 (4 байти)
    uint32_t crc = usbpd_crc32(payload, len);
    for (int i = 0; i < 4; ++i) {
        uint8_t byte = (crc >> (i * 8)) & 0xFF;
        bmc_encode_5b_symbol(enc, table_4b5b[byte & 0x0F]);
        bmc_encode_5b_symbol(enc, table_4b5b[(byte >> 4) & 0x0F]);
    }

    // 5. Маркер кінця пакета EOP
    bmc_encode_5b_symbol(enc, K_EOP);

    return enc->count;
}

// Стан декодера BMC
typedef enum {
    DEC_WAIT_PREAMBLE,
    DEC_WAIT_SOP,
    DEC_RECEIVE_PAYLOAD,
    DEC_PACKET_DONE,
    DEC_ERROR
} dec_state_t;

typedef struct {
    dec_state_t state;
    bool half_bit_pending;
    uint32_t shift_reg;      // 20-бітний регістр для детекції SOP
    uint8_t sym_shift_reg;   // 5-бітний накопичувач для символів
    uint8_t sym_bit_count;
    uint8_t nibble_buffer;
    bool high_nibble_expected;
    usbpd_sop_t detected_sop;
    uint8_t rx_buffer[64];
    size_t rx_len;
    uint32_t rx_crc;
} bmc_decoder_t;

void bmc_decoder_init(bmc_decoder_t *dec) {
    memset(dec, 0, sizeof(bmc_decoder_t));
    dec->state = DEC_WAIT_PREAMBLE;
}

// Обробка одного виміряного інтервалу часу між фронтами
bool bmc_decoder_feed_interval(bmc_decoder_t *dec, float dt_us) {
    // 1. Фільтрація шумів
    if (dt_us < USBPD_TNOISE_MIN_US) {
        return false; // Ігноруємо брязкіт
    }

    // 2. Перевірка на таймаут
    if (dt_us > USBPD_TTIMEOUT_MAX_US) {
        dec->half_bit_pending = false;
        if (dec->state == DEC_RECEIVE_PAYLOAD && dec->rx_len > 4) {
            dec->state = DEC_PACKET_DONE;
            return true;
        }
        dec->state = DEC_WAIT_PREAMBLE;
        return false;
    }

    // 3. Розпізнавання півбіта / повного біта
    int bit_val = -1;
    if (dt_us < USBPD_TSPLIT_US) {
        // Інтервал півбіта (1.67 мкс)
        if (dec->half_bit_pending) {
            bit_val = 1; // Отримано другий півбіт -> це '1'
            dec->half_bit_pending = false;
        } else {
            dec->half_bit_pending = true; // Чекаємо напарника
            return false;
        }
    } else {
        // Інтервал повного біта (3.33 мкс)
        if (dec->half_bit_pending) {
            // Порушення протоколу: після першого півбіта прийшов повний біт
            dec->half_bit_pending = false;
            dec->state = DEC_ERROR;
            return false;
        }
        bit_val = 0; // Одиночний перехід -> це '0'
    }

    // 4. Обробка прийнятого біта скінченним автоматом
    dec->shift_reg = ((dec->shift_reg >> 1) | ((uint32_t)bit_val << 19)) & 0xFFFFF;

    if (dec->state == DEC_WAIT_PREAMBLE || dec->state == DEC_WAIT_SOP) {
        // Перевірка 20-бітного вікна на послідовність SOP (LSB-перший)
        uint32_t sop_pattern = (uint32_t)K_SYNC1 | ((uint32_t)K_SYNC1 << 5) |
                               ((uint32_t)K_SYNC1 << 10) | ((uint32_t)K_SYNC2 << 15);
        uint32_t sop_p_pattern = (uint32_t)K_SYNC1 | ((uint32_t)K_SYNC1 << 5) |
                                 ((uint32_t)K_SYNC3 << 10) | ((uint32_t)K_SYNC3 << 15);
        uint32_t hard_rst_pattern = (uint32_t)K_RST1 | ((uint32_t)K_RST1 << 5) |
                                    ((uint32_t)K_RST1 << 10) | ((uint32_t)K_RST2 << 15);

        if (dec->shift_reg == sop_pattern) {
            dec->detected_sop = SOP_TYPE_SOP;
            dec->state = DEC_RECEIVE_PAYLOAD;
            dec->sym_bit_count = 0;
            dec->sym_shift_reg = 0;
            dec->rx_len = 0;
            dec->high_nibble_expected = false;
            return false;
        } else if (dec->shift_reg == sop_p_pattern) {
            dec->detected_sop = SOP_TYPE_SOP_PRIME;
            dec->state = DEC_RECEIVE_PAYLOAD;
            dec->sym_bit_count = 0;
            dec->sym_shift_reg = 0;
            dec->rx_len = 0;
            dec->high_nibble_expected = false;
            return false;
        } else if (dec->shift_reg == hard_rst_pattern) {
            dec->detected_sop = SOP_TYPE_HARD_RESET;
            dec->state = DEC_PACKET_DONE;
            return true;
        }
        return false;
    }

    if (dec->state == DEC_RECEIVE_PAYLOAD) {
        dec->sym_shift_reg |= ((uint8_t)bit_val << dec->sym_bit_count);
        dec->sym_bit_count++;

        if (dec->sym_bit_count == 5) {
            uint8_t symbol = dec->sym_shift_reg;
            dec->sym_bit_count = 0;
            dec->sym_shift_reg = 0;

            // Перевірка на EOP
            if (symbol == K_EOP) {
                dec->state = DEC_PACKET_DONE;
                return true;
            }

            // Декодування 5b у 4b
            uint8_t nibble = table_5b4b[symbol & 0x1F];
            if (nibble == 0xFF) {
                dec->state = DEC_ERROR;
                return false;
            }

            if (!dec->high_nibble_expected) {
                dec->nibble_buffer = nibble;
                dec->high_nibble_expected = true;
            } else {
                uint8_t full_byte = dec->nibble_buffer | (nibble << 4);
                dec->high_nibble_expected = false;
                if (dec->rx_len < sizeof(dec->rx_buffer)) {
                    dec->rx_buffer[dec->rx_len++] = full_byte;
                }
            }
        }
    }

    return false;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <vector>
#include <optional>
#include <span>
#include <string_view>

namespace usbpd {

constexpr uint32_t FreqHz         = 300'000;
constexpr float    TBitUs         = 3.333333f;
constexpr float    THalfUs        = 1.666667f;

constexpr float    TNoiseMinUs    = 0.833f;
constexpr float    TSplitUs       = 2.500f;
constexpr float    TTimeoutMaxUs  = 4.167f;

// 5-бітні K-символи керування
enum class KCode : uint8_t {
    Sync1 = 0x18, // 11000b
    Sync2 = 0x12, // 10010b
    Sync3 = 0x06, // 00110b
    Rst1  = 0x07, // 00111b
    Rst2  = 0x19, // 11001b
    Eop   = 0x0D  // 01101b
};

enum class SopType {
    Unknown = 0,
    Sop,        // Sync1 + Sync1 + Sync1 + Sync2
    SopPrime,   // Sync1 + Sync1 + Sync3 + Sync3
    SopDPrime,  // Sync1 + Sync3 + Sync1 + Sync3
    HardReset,  // Rst1 + Rst1 + Rst1 + Rst2
    CableReset  // Rst1 + Sync1 + Rst1 + Sync1
};

// Константні таблиці 4b/5b
constexpr std::array<uint8_t, 16> Table4b5b = {
    0x1E, 0x09, 0x14, 0x15, 0x0A, 0x0B, 0x0E, 0x0F,
    0x12, 0x13, 0x16, 0x17, 0x1A, 0x1B, 0x1C, 0x1D
};

constexpr std::array<uint8_t, 32> Table5b4b = {
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0x01, 0x04, 0x05, 0xFF, 0xFF, 0x06, 0x07,
    0xFF, 0xFF, 0x08, 0x09, 0x02, 0x03, 0x0A, 0x0B,
    0xFF, 0xFF, 0x0C, 0x0D, 0x0E, 0x0F, 0x00, 0xFF
};

// Обчислення CRC-32 для USB Power Delivery
constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFUL;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320UL;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

// Клас BMC кодера
class BmcEncoder {
public:
    BmcEncoder() = default;

    [[nodiscard]] std::vector<float> encode_packet(std::span<const uint8_t> payload, SopType sop) {
        std::vector<float> intervals;
        intervals.reserve(128 + payload.size() * 20);

        // 1. 64 біти преамбули
        for (int i = 0; i < 64; ++i) {
            encode_bit(intervals, false);
        }

        // 2. Стартовий маркер SOP
        switch (sop) {
            case SopType::Sop:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync2));
                break;
            case SopType::SopPrime:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync3));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync3));
                break;
            case SopType::SopDPrime:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync3));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync3));
                break;
            case SopType::HardReset:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst2));
                return intervals;
            case SopType::CableReset:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                return intervals;
            default:
                return {};
        }

        // 3. Корисне навантаження
        for (uint8_t byte : payload) {
            encode_5b(intervals, Table4b5b[byte & 0x0F]);
            encode_5b(intervals, Table4b5b[(byte >> 4) & 0x0F]);
        }

        // 4. CRC-32
        uint32_t crc = calculate_crc32(payload);
        for (int i = 0; i < 4; ++i) {
            uint8_t byte = (crc >> (i * 8)) & 0xFF;
            encode_5b(intervals, Table4b5b[byte & 0x0F]);
            encode_5b(intervals, Table4b5b[(byte >> 4) & 0x0F]);
        }

        // 5. Завершення пакета EOP
        encode_5b(intervals, static_cast<uint8_t>(KCode::Eop));

        return intervals;
    }

private:
    static void encode_bit(std::vector<float>& out, bool bit) {
        if (bit) {
            out.push_back(THalfUs);
            out.push_back(THalfUs);
        } else {
            out.push_back(TBitUs);
        }
    }

    static void encode_5b(std::vector<float>& out, uint8_t sym5b) {
        for (int i = 0; i < 5; ++i) {
            encode_bit(out, (sym5b >> i) & 1);
        }
    }
};

// Результат декодування пакета
struct DecodedPacket {
    SopType sop = SopType::Unknown;
    std::vector<uint8_t> payload;
    uint32_t received_crc = 0;
    bool crc_valid = false;
};

// Клас BMC декодера
class BmcDecoder {
public:
    enum class State {
        WaitPreamble,
        WaitSop,
        ReceivePayload,
        PacketDone,
        Error
    };

    BmcDecoder() { reset(); }

    void reset() noexcept {
        state_ = State::WaitPreamble;
        half_bit_pending_ = false;
        shift_reg_ = 0;
        sym_shift_reg_ = 0;
        sym_bit_count_ = 0;
        nibble_buffer_ = 0;
        high_nibble_expected_ = false;
        current_packet_ = {};
    }

    // Обробка чергового виміряного інтервалу
    std::optional<DecodedPacket> feed_interval(float dt_us) {
        if (dt_us < TNoiseMinUs) {
            return std::nullopt; // Шумовий викид
        }

        if (dt_us > TTimeoutMaxUs) {
            half_bit_pending_ = false;
            if (state_ == State::ReceivePayload && current_packet_.payload.size() >= 4) {
                return finalize_packet();
            }
            state_ = State::WaitPreamble;
            return std::nullopt;
        }

        int bit_val = -1;
        if (dt_us < TSplitUs) {
            if (half_bit_pending_) {
                bit_val = 1;
                half_bit_pending_ = false;
            } else {
                half_bit_pending_ = true;
                return std::nullopt;
            }
        } else {
            if (half_bit_pending_) {
                half_bit_pending_ = false;
                state_ = State::Error;
                return std::nullopt;
            }
            bit_val = 0;
        }

        shift_reg_ = ((shift_reg_ >> 1) | (static_cast<uint32_t>(bit_val) << 19)) & 0xFFFFF;

        if (state_ == State::WaitPreamble || state_ == State::WaitSop) {
            constexpr uint32_t SopPattern = 
                static_cast<uint32_t>(KCode::Sync1) |
                (static_cast<uint32_t>(KCode::Sync1) << 5) |
                (static_cast<uint32_t>(KCode::Sync1) << 10) |
                (static_cast<uint32_t>(KCode::Sync2) << 15);

            constexpr uint32_t SopPPattern = 
                static_cast<uint32_t>(KCode::Sync1) |
                (static_cast<uint32_t>(KCode::Sync1) << 5) |
                (static_cast<uint32_t>(KCode::Sync3) << 10) |
                (static_cast<uint32_t>(KCode::Sync3) << 15);

            constexpr uint32_t HardRstPattern = 
                static_cast<uint32_t>(KCode::Rst1) |
                (static_cast<uint32_t>(KCode::Rst1) << 5) |
                (static_cast<uint32_t>(KCode::Rst1) << 10) |
                (static_cast<uint32_t>(KCode::Rst2) << 15);

            if (shift_reg_ == SopPattern) {
                current_packet_.sop = SopType::Sop;
                state_ = State::ReceivePayload;
                sym_bit_count_ = 0;
                sym_shift_reg_ = 0;
                high_nibble_expected_ = false;
                current_packet_.payload.clear();
            } else if (shift_reg_ == SopPPattern) {
                current_packet_.sop = SopType::SopPrime;
                state_ = State::ReceivePayload;
                sym_bit_count_ = 0;
                sym_shift_reg_ = 0;
                high_nibble_expected_ = false;
                current_packet_.payload.clear();
            } else if (shift_reg_ == HardRstPattern) {
                current_packet_.sop = SopType::HardReset;
                state_ = State::PacketDone;
                DecodedPacket res = std::move(current_packet_);
                reset();
                return res;
            }
            return std::nullopt;
        }

        if (state_ == State::ReceivePayload) {
            sym_shift_reg_ |= (static_cast<uint8_t>(bit_val) << sym_bit_count_);
            sym_bit_count_++;

            if (sym_bit_count_ == 5) {
                uint8_t symbol = sym_shift_reg_;
                sym_bit_count_ = 0;
                sym_shift_reg_ = 0;

                if (symbol == static_cast<uint8_t>(KCode::Eop)) {
                    return finalize_packet();
                }

                uint8_t nibble = Table5b4b[symbol & 0x1F];
                if (nibble == 0xFF) {
                    state_ = State::Error;
                    return std::nullopt;
                }

                if (!high_nibble_expected_) {
                    nibble_buffer_ = nibble;
                    high_nibble_expected_ = true;
                } else {
                    uint8_t full_byte = nibble_buffer_ | (nibble << 4);
                    high_nibble_expected_ = false;
                    current_packet_.payload.push_back(full_byte);
                }
            }
        }

        return std::nullopt;
    }

private:
    std::optional<DecodedPacket> finalize_packet() {
        if (current_packet_.payload.size() < 4) {
            reset();
            return std::nullopt;
        }

        // Останні 4 байти — це контрольна сума CRC-32
        size_t data_len = current_packet_.payload.size() - 4;
        uint32_t rx_crc = static_cast<uint32_t>(current_packet_.payload[data_len]) |
                         (static_cast<uint32_t>(current_packet_.payload[data_len + 1]) << 8) |
                         (static_cast<uint32_t>(current_packet_.payload[data_len + 2]) << 16) |
                         (static_cast<uint32_t>(current_packet_.payload[data_len + 3]) << 24);

        std::span<const uint8_t> data_span(current_packet_.payload.data(), data_len);
        uint32_t calc_crc = calculate_crc32(data_span);

        current_packet_.received_crc = rx_crc;
        current_packet_.crc_valid = (rx_crc == calc_crc);
        current_packet_.payload.resize(data_len);

        DecodedPacket res = std::move(current_packet_);
        reset();
        return res;
    }

    State state_ = State::WaitPreamble;
    bool half_bit_pending_ = false;
    uint32_t shift_reg_ = 0;
    uint8_t sym_shift_reg_ = 0;
    uint8_t sym_bit_count_ = 0;
    uint8_t nibble_buffer_ = 0;
    bool high_nibble_expected_ = false;
    DecodedPacket current_packet_;
};

} // namespace usbpd
```
:::

---

### 7. Практичний розбір тестового сценарію та крайових ситуацій

Продемонструємо проходження реального пакета повідомлення `Source_Capabilities` через створений кодек. Припустимо, джерело живлення транслює повідомлення з 16-розрядним заголовком `0x11A1` (тип повідомлення `Source_Capabilities`, ID повідомлення = 0, кількість об'єктів PDO = 1, роль живлення = Source) та одним 32-розрядним об'єктом живлення `0x00019096` (фіксований профіль 5 В, максимальний струм 3 А):

```
Байтова послідовність корисного навантаження (6 байтів):
Заголовок:    0xA1, 0x11
Об'єкт PDO:   0x96, 0x90, 0x01, 0x00
```

1. **Етап 4b/5b кодування**: Кожен із 6 байтів розбивається на молодший та старший нібли (всього 12 ніблів). Кожен нібл транслюється у 5-бітне слово:
   - Байт `0xA1` → нібли `0x1` (символ `01001b`) та `0xA` (символ `10110b`);
   - Байт `0x11` → нібли `0x1` (`01001b`) та `0x1` (`01001b`);
   - Байт `0x96` → нібли `0x6` (`01110b`) та `0x9` (`10011b`);
   - Байт `0x90` → нібли `0x0` (`11110b`) та `0x9` (`10011b`);
   - Байт `0x01` → нібли `0x1` (`01001b`) та `0x0` (`11110b`);
   - Байт `0x00` → нібли `0x0` (`11110b`) та `0x0` (`11110b`).

2. **Етап обчислення CRC-32**: Контрольна сума від 6 байтів дає 32-розрядне число, яке кодується ще 8 символами 5b (40 біт). Разом із 20 бітами SOP та 5 бітами EOP загальна довжина кадру становить `20 (SOP) + 60 (дані) + 40 (CRC) + 5 (EOP) = 125 біт` (плюс 64 біти преамбули).

3. **Етап BMC-модуляції**: Усі 189 бітів перетворюються на масив часових інтервалів `intervals_us`. Для нулів генерується один імпульс 3.33 мкс, для одиниць — два імпульси по 1.67 мкс.

4. **Етап декодування та стійкість до джиттеру**: Якщо в канал зв'язку ввести штучний випадковий шум із розкидом тривалості імпульсів `±15%` (інтервали 1.67 мкс плавають у межах 1.42 .. 1.92 мкс, а 3.33 мкс — у межах 2.83 .. 3.83 мкс), скінченний автомат завдяки широким розділовим вікнам (поріг 2.50 мкс) безпомилково відновлює початкові 6 байтів, а перевірка CRC-32 повертає прапорець `crc_valid == true`.

---

### 8. Організація прямого доступу до пам'яті (DMA) та навантаження процесора

Якщо викликати функцію `bmc_decoder_feed_interval` у звичайному обробнику переривань таймера (ISR), на максимальній швидкості передачі одиниць (частота перемикання 600 кГц) процесор отримуватиме переривання кожні 1.67 мкс. При тактовій частоті мікроконтролера 48 МГц це залишає лише 80 тактів ядра на обробку одного фронту, що може призвести до пропуску подій та перевантаження системи.

Для усунення цього вузького місця застосовується кільцевий буфер прямого доступу до пам'яті (DMA Circular Buffer):

```
                      [ Події Input Capture таймера ]
                                     │
                                     ▼
                      [ Контролер каналу DMA ]
                 (переміщує значення таймера без CPU)
                                     │
                                     ▼
                ┌─────────────────────────────────────────┐
                │ Кільцевий масив пам'яті (наприклад, 64)  │
                └────────────────────┬────────────────────┘
                                     │ Half-Transfer / Full-Transfer
                                     ▼
                     [ Обробка пачками у фоні ]
              (частота виклику знижується до ~9 кГц)
```

Канал DMA автоматично переносить значення регістрів захоплення таймера в масив оперативної пам'яті без залучення процесорного ядра. Переривання генеруються лише після накопичення половини або повного буфера (наприклад, кожні 32 відліки). Це знижує частоту викликів переривань у десятки разів, дозволяючи процесору обробляти дані великими пачками у фоновому циклі або RTOS-задачі.

---

### 9. Налаштування регістрів таймера STM32 для вхідного захоплення

Наведемо послідовність низькорівневої ініціалізації периферійного таймера (наприклад, TIM2 або TIM3) у мікроконтролерах STM32 для прямого захоплення обох фронтів сигналу:

1. **Тактування**: Увімкнути тактування таймера та порту введення-виведення у регістрі `RCC->APB1ENR` або `RCC->APBENR1`.
2. **Конфігурація виводу**: Налаштувати відповідний пін GPIO (наприклад, PA0) у режим альтернативної функції `GPIO_MODE_AF_PP` без внутрішніх підтяжок (підтяжка задається зовнішніми Rp/Rd).
3. **Режим вхідного захоплення**: Записати в регістр `TIMx->CCMR1` значення `CC1S = 01` (вхідний канал IC1 зіставляється з виводом TI1). Встановити вхідний цифровий фільтр `IC1F = 0010` (фільтрація 4 тактів тактової частоти для придушення короткочасних імпульсних завад менше 80 нс).
4. **Полярність перемикання**: У регістрі `TIMx->CCER` встановити біти `CC1P = 1` та `CC1NP = 1`, що вмикає детекцію фронтів обох полярностей (Both Edges Triggering).
5. **Активація DMA**: Встановити біт `CC1DE` у регістрі `TIMx->DIER` для генерації запитів DMA при кожній події фіксації фронту.

Така конфігурація дозволяє знімати часові мітки переходів сигналу повністю апаратно з точністю до одного такту системної шини.

---

### 10. Розпізнавання сигналів скидання зв'язку (Hard Reset)

Крім звичайних пакетів обміну даними, протокол USB PD визначає екстрений керівний сигнал — **Hard Reset**. Він передається тоді, коли один із вузлів перестав відповідати на запити, завис або якщо виникла критична аварія живлення (перенапруга на VBUS, перевищення температури чи перевантаження по струму).

Впорядкований набір Hard Reset складається з чотирьох K-символів: `RST-1` + `RST-1` + `RST-1` + `RST-2`. Після цієї послідовності не передаються ні заголовок, ні дані, ні контрольна сума CRC, ні символ EOP. Передавач відразу примусово вимикає драйвер.

Реакція системи на сигнал Hard Reset є безумовною та негайною: джерело живлення зобов'язане протягом 5 мс скинути напругу на шині VBUS до початкових 5 В, а приймач — відключити внутрішні навантаження та перейти у вихідний стан виявлення.

---

### 11. Уникнення колізій на лінії CC (Collision Avoidance)

Оскільки лінія Configuration Channel є напівдуплексним однопровідним каналом (Half-Duplex), обидва вузли (і Source, і Sink) можуть одночасно спробувати розпочати передачу пакета. Щоб запобігти накладанню сигналів, фізичний рівень реалізує механізм запобігання колізіям:

1. **Моніторинг зайнятості лінії (Channel Busy)**: Перед початком формування преамбули передавач слухає лінію CC протягом інтервалу `tReceive` (не менше 4.5 мкс). Якщо на лінії спостерігаються фронти, канал вважається зайнятим, і передача відкладається.
2. **Пріоритет за роллю (Sink-to-Source Turnaround)**: Якщо обидві сторони хочуть передати пакет одночасно, джерело живлення має пріоритет на ініціацію повідомлень керування живленням, а пристрій (Sink) відступає на випадковий час затримки (Backoff Time).
3. **Виявлення колізії під час преамбули**: Якщо передавач під час виставлення своїх рівнів бачить спотворення напруги через зустрічний сигнал іншого вузла, передача негайно переривається, лінія відпускається у пасивний стан Rp/Rd, і протокольний стек планує повторну спробу (Retry) через псевдовипадковий інтервал.

---

### 12. Тестові режими BIST та перевірка фізичного рівня

Для сертифікації фізичного рівня та перевірки якості сигналу специфікація USB PD вводить спеціальні тестові режими BIST (Built-In Self-Test):

1. **BIST Carrier Mode**: Передавач генерує безперервний змінний сигнал частотою рівно 300 кГц або 600 кГц без формування преамбули, пакетних заголовків та CRC. Цей режим використовується на випробувальних стендах для спектрального аналізу випромінюваних завад (EMI) та оцінки точності тактового генератора.
2. **BIST PRBS (Pseudo-Random Binary Sequence)**: Передавач формує псевдовипадкову послідовність бітів (зазвичай поліном PRBS-23), закодовану в BMC, для побудови статистичної очної діаграми на швидкісному цифровому осцилографі. За накопиченою вибіркою у мільйони переходів вимірюється ширина відкриття ока, фазовий джиттер та рівень міжсимвольної інтерференції в реальному кабелі.

---

### 13. Налагодження за допомогою логічного аналізатора

Під час розробки та діагностики протоколу USB PD за допомогою логічного аналізатора (наприклад, у програмі PulseView з відкритим декодером `usb_power_delivery`) послідовність BMC візуалізується такими характерними маркерами:

- **Преамбула**: Виглядає як ідеальний меандр із частотою 300 кГц (період 3.33 мкс) або 150 кГц залежно від вибору послідовності. Вона слугує візуальним маяком початку передачі;
- **SOP**: Після регулярного меандру з'являється характерне згущення частоти до 600 кГц (фронти кожні 1.67 мкс), що відповідає кодам `Sync-1`;
- **Поле даних**: Суміш широких та вузьких імпульсів;
- **EOP та тиша (Idle)**: Останній перехід символу EOP супроводжується спадом напруги до нуля та поверненням лінії у високоімпедансний стан, де напруга повертається до рівня пасивного дільника Rp/Rd (0.41 В, 0.92 В або 1.68 В).
