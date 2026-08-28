# Програмний кодер DShot та декодер телеметрії

Реалізація протоколу DShot на вбудованих мікроконтролерах вимагає поєднання швидкісної підготовки буферів прямого доступу до пам'яті (DMA) для керування апаратними таймерами та надійного програмного декодування двосторонньої телеметрії (GCR). У цьому проекті наведено закінчену бібліотеку формування 16-бітного цифрового кадру DShot, заповнення масиву регістрів захоплення/порівняння таймера, а також декодер відповіді регулятора з обчисленням реальної швидкості обертання двигуна (RPM).

## Архітектура кодера та декодера

Робота з DShot на стороні керуючого процесора (польотного контролера) розбивається на два незалежні функціональні контури:

1. **Контур передачі (TX)**:
   - Перетворення 11-бітного значення газу (`0` або `48...2047`) та прапорця телеметрії `TLM` у 16-бітний кадр із 4-бітним CRC.
   - Розгортання 16 бітів у масив із 17 слів для каналу таймера: логічний `0` записується як `33%` періоду таймера, логічна `1` — як `67%` періоду, а 17-й елемент встановлюється в `0` для утримання лінії в низькому стані після завершення передачі.
   - Запуск передачі через DMA без навантаження процесорного ядра.

2. **Контур прийому та телеметрії (RX)**:
   - Захоплення 21-бітного вхідного потоку eGCR через вхід Input Capture таймера або апаратний UART в режимі Single-Wire Half-Duplex.
   - Зворотне перетворення чотирьох 5-бітних символів GCR у 4-бітні ніблі даних (табличний декодер 5b4b).
   - Перевірка 4-бітної контрольної суми телеметрії.
   - Виділення мантиси й експоненти, обчислення електричного періоду `T_comm` та перерахунок у фізичні оберти на хвилину (RPM) з урахуванням конфігурації магнітних полюсів ротора.

## Математичне виведення швидкості обертання

Регулятор вимірює часовий інтервал між послідовними комутаціями фаз двигуна. У 3-фазному безколекторному двигуні повний електричний період комутації поля складається з 6 послідовних кроків перемикання силових транзисторів (6-step trapezoidal commutation).

Якщо `T_comm` — це тривалість одного кроку комутації в мікросекундах (`10⁻⁶ с`), то один повний електричний оберт магнітного поля статора триває:

```
T_elec_rev = 6 · T_comm · 10⁻⁶ [секунд]
```

Кількість електричних обертів за одну секунду дорівнює `1 / T_elec_rev`. Відповідно, частота обертання електричного поля за одну хвилину (ERPM, Electrical Revolutions Per Minute) виражається формулою:

```
ERPM = (60 / T_elec_rev)
     = 60 / (6 · T_comm · 10⁻⁶)
     = 10000000 / T_comm [об/хв]
```

Для переходу від електричних обертів магнітного поля до механічних обертів вихідного вала ротора необхідно врахувати кількість пар постійних магнітів (магнітних полюсів) ротора `P_pairs = P_poles / 2`:

```
RPM = ERPM / P_pairs [механічних об/хв]
```

Ця формула реалізована в наведеному нижче декодері телеметрії з попередньою перевіркою ділення на нуль при зупиненому моторі.

## Покроковий числовий приклад кодування та декодування кадру

Для наочного розуміння простежимо повний шлях перетворення команди газу в цифровий потік та зворотний розбір телеметрії.

### 1. Формування пакета газу
Припустимо, що польотний контролер передає команду газу `1000` (приблизно `48.7%` тяги) без запиту аналогової телеметрії (`TLM = 0`) у режимі Bi-directional DShot:

- Зсув значення на 1 біт уліво: `data = (1000 << 1) | 0 = 2000` (у шістнадцятковому вигляді `0x07D0`).
- Розбиття на 4-бітні ніблі: `Nibble_0 = 0x0`, `Nibble_1 = 0xD`, `Nibble_2 = 0x7`.
- Обчислення XOR-суми: `csum = 0x0 ^ 0xD ^ 0x7 = 0xA` (`1010` у двійковому коді).
- Інверсія контрольної суми для двостороннього режиму: `csum_bidir = (~0xA) & 0x0F = 0x5` (`0101` у двійковому коді).
- Підсумковий 16-бітний кадр: `frame = (0x7D0 << 4) | 0x5 = 0x7D05` (`0111 1101 0000 0101`).

### 2. Заповнення масиву таймера
Для таймера з `ARR = 280` (DShot600 при частоті тактування 168 МГц):
- Біти зі значенням `1` (позиції 14, 13, 12, 11, 10, 8, 2, 0) отримують поріг `CCR = 187`.
- Біти зі значенням `0` (позиції 15, 9, 7, 6, 5, 4, 3, 1) отримують поріг `CCR = 93`.
- 17-й елемент встановлюється в `0`. Масив передається контролеру DMA.

### 3. Декодування відповіді регулятора
Нехай від регулятора отримано 20-бітний GCR-потік `0x96B5A`:
- Розбиття на 5-бітні блоки: `GCR3 = 0x12` (`10010`), `GCR2 = 0x1A` (`11010`), `GCR1 = 0x1A` (`11010`), `GCR0 = 0x1A` (`11010`).
- Перетворення за таблицею: `nib3 = 0x8`, `nib2 = 0xC`, `nib1 = 0xC`, `nib0 = 0xC`.
- Відновлене 12-бітне значення: `0x8CC`, прийнятий CRC: `0xC`.
- Перевірка контрольної суми: `calc_crc = (~(0x8CC ^ (0x8CC >> 4) ^ (0x8CC >> 8))) & 0x0F = (~(0xC ^ 0xC ^ 0x8)) & 0x0F = (~0x8) & 0x0F = 0x7`. Якщо контрольна сума збігається, дані передаються в контур обчислення обертів.
- Виділення порядку й мантиси з `0x8CC`: експонента `E = (0x8CC >> 9) & 0x7 = 4`, мантиса `M = 0x8CC & 0x1FF = 204`.
- Період комутації: `T_comm = 204 << 4 = 3264 мкс`.
- Швидкість електричного поля: `ERPM = 10000000 / 3264 = 3063 об/хв`.
- Механічна швидкість вала для 14-полюсного мотора (`P_pairs = 7`): `RPM = 3063 / 7 = 437 об/хв`.

## Повна реалізація мовами C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define DSHOT_DISARM_VALUE        0
#define DSHOT_MIN_THROTTLE        48
#define DSHOT_MAX_THROTTLE        2047
#define DSHOT_DMA_BUFFER_SIZE     17

typedef struct {
    uint32_t timer_arr;        /* Значення Auto-Reload Register таймера */
    uint32_t ccr_bit0;         /* Поріг компаратора для логічного 0 (33% ARR) */
    uint32_t ccr_bit1;         /* Поріг компаратора для логічного 1 (67% ARR) */
    uint8_t motor_pole_pairs;  /* Кількість пар полюсів ротора (типово 7 для 14P) */
    bool bidirectional;        /* true = інвертований CRC для Bi-dir DShot */
} dshot_config_t;

typedef struct {
    bool valid;
    uint32_t erpm;
    uint32_t rpm;
    uint8_t raw_type;
    uint8_t raw_payload;
} dshot_telemetry_t;

/* Таблиця декодування 5b4b GCR (32 елементи для швидкого індексування) */
static const int8_t gcr_decode_table[32] = {
    -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,  /* 0x00 - 0x07 */
    -1,   -1,   -1,   -1,   -1, 0x0D, 0x0E, 0x0F,  /* 0x08 - 0x0F: 13, 14, 15 */
    -1,   -1, 0x08, 0x09,   -1, 0x05, 0x0A, 0x0B,  /* 0x10 - 0x17: 8, 9, 5, 10, 11 */
    -1, 0x00, 0x0C, 0x01,   -1, 0x04, 0x02, 0x03   /* 0x18 - 0x1F: 0, 12, 1, 4, 2, 3 */
};

/* Ініціалізація структури конфігурації */
void dshot_init(dshot_config_t *cfg, uint32_t timer_arr, uint8_t pole_pairs, bool bidir) {
    cfg->timer_arr = timer_arr;
    cfg->ccr_bit0 = (timer_arr * 33) / 100;
    cfg->ccr_bit1 = (timer_arr * 67) / 100;
    cfg->motor_pole_pairs = (pole_pairs > 0) ? pole_pairs : 7;
    cfg->bidirectional = bidir;
}

/* Формування 16-бітного пакета DShot */
uint16_t dshot_create_packet(uint16_t throttle, bool request_tlm, bool bidirectional) {
    if (throttle > DSHOT_MAX_THROTTLE) {
        throttle = DSHOT_MAX_THROTTLE;
    }

    uint16_t packet = (throttle << 1) | (request_tlm ? 1 : 0);
    uint16_t csum = 0;
    uint16_t csum_data = packet;

    /* 4-бітний XOR трьох ніблів */
    for (int i = 0; i < 3; i++) {
        csum ^= (csum_data & 0x0F);
        csum_data >>= 4;
    }

    if (bidirectional) {
        csum = (~csum) & 0x0F;
    } else {
        csum &= 0x0F;
    }

    return (packet << 4) | csum;
}

/* Заповнення буфера DMA значеннями CCR для таймера */
void dshot_fill_dma_buffer(const dshot_config_t *cfg, uint16_t packet, uint32_t *dma_buf) {
    for (int i = 0; i < 16; i++) {
        /* Старший біт іде першим (MSB first) */
        if (packet & (1 << (15 - i))) {
            dma_buf[i] = cfg->ccr_bit1;
        } else {
            dma_buf[i] = cfg->ccr_bit0;
        }
    }
    /* Завершальний рівень для міжкадрової паузи */
    dma_buf[16] = 0;
}

/* Декодування 20/21-бітного GCR потоку телеметрії */
bool dshot_decode_telemetry(const dshot_config_t *cfg, uint32_t raw_gcr, dshot_telemetry_t *out) {
    out->valid = false;
    out->erpm = 0;
    out->rpm = 0;

    /* Виділяємо чотири 5-бітні GCR символи (20 бітів) */
    uint8_t gcr3 = (raw_gcr >> 15) & 0x1F;
    uint8_t gcr2 = (raw_gcr >> 10) & 0x1F;
    uint8_t gcr1 = (raw_gcr >> 5)  & 0x1F;
    uint8_t gcr0 = (raw_gcr >> 0)  & 0x1F;

    int8_t nib3 = gcr_decode_table[gcr3];
    int8_t nib2 = gcr_decode_table[gcr2];
    int8_t nib1 = gcr_decode_table[gcr1];
    int8_t nib0 = gcr_decode_table[gcr0];

    if (nib3 < 0 || nib2 < 0 || nib1 < 0 || nib0 < 0) {
        return false; /* Помилка GCR-символу */
    }

    uint16_t value_12bit = ((uint16_t)nib3 << 8) | ((uint16_t)nib2 << 4) | (uint16_t)nib1;
    uint8_t received_crc = (uint8_t)nib0;

    /* Перевірка контрольної суми відповіді телеметрії */
    uint8_t calc_crc = (~(value_12bit ^ (value_12bit >> 4) ^ (value_12bit >> 8))) & 0x0F;
    if (calc_crc != received_crc) {
        return false; /* Помилка контрольної суми */
    }

    out->valid = true;
    out->raw_type = (value_12bit >> 8) & 0x0F;
    out->raw_payload = value_12bit & 0xFF;

    /* Розпакування періоду ERPM (експонента E = 3 біти, мантиса M = 9 бітів) */
    uint8_t exponent = (value_12bit >> 9) & 0x07;
    uint16_t mantissa = value_12bit & 0x01FF;

    if (mantissa == 0) {
        out->erpm = 0;
        out->rpm = 0;
        return true;
    }

    /* Період комутації в мікросекундах */
    uint32_t period_us = (uint32_t)mantissa << exponent;
    if (period_us == 0) {
        return true;
    }

    /* ERPM = (1000000 мкс / T_comm) * (60 сек / 6 кроків) = 10000000 / period_us */
    out->erpm = 10000000UL / period_us;
    out->rpm = out->erpm / cfg->motor_pole_pairs;

    return true;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <optional>

namespace dshot {

constexpr uint16_t DisarmValue = 0;
constexpr uint16_t MinThrottle = 48;
constexpr uint16_t MaxThrottle = 2047;
constexpr size_t DmaBufferSize = 17;

struct Config {
    uint32_t timerArr{0};
    uint32_t ccrBit0{0};
    uint32_t ccrBit1{0};
    uint8_t motorPolePairs{7};
    bool bidirectional{true};

    constexpr Config(uint32_t arr, uint8_t polePairs = 7, bool bidir = true) noexcept
        : timerArr(arr),
          ccrBit0((arr * 33) / 100),
          ccrBit1((arr * 67) / 100),
          motorPolePairs(polePairs > 0 ? polePairs : 7),
          bidirectional(bidir) {}
};

struct Telemetry {
    uint32_t erpm{0};
    uint32_t rpm{0};
    uint8_t rawType{0};
    uint8_t rawPayload{0};
};

class ProtocolEngine {
public:
    explicit constexpr ProtocolEngine(Config config) noexcept : cfg_(config) {}

    [[nodiscard]] constexpr uint16_t createPacket(uint16_t throttle, bool requestTlm) const noexcept {
        const uint16_t clamped = (throttle > MaxThrottle) ? MaxThrottle : throttle;
        const uint16_t packet = (clamped << 1) | (requestTlm ? 1 : 0);
        
        uint16_t csum = 0;
        uint16_t csumData = packet;
        for (int i = 0; i < 3; ++i) {
            csum ^= (csumData & 0x0F);
            csumData >>= 4;
        }

        csum = cfg_.bidirectional ? ((~csum) & 0x0F) : (csum & 0x0F);
        return (packet << 4) | csum;
    }

    void fillDmaBuffer(uint16_t packet, std::span<uint32_t, DmaBufferSize> buffer) const noexcept {
        for (size_t i = 0; i < 16; ++i) {
            buffer[i] = (packet & (1 << (15 - i))) ? cfg_.ccrBit1 : cfg_.ccrBit0;
        }
        buffer[16] = 0;
    }

    [[nodiscard]] std::optional<Telemetry> decodeTelemetry(uint32_t rawGcr) const noexcept {
        const uint8_t gcr[4] = {
            static_cast<uint8_t>((rawGcr >> 15) & 0x1F),
            static_cast<uint8_t>((rawGcr >> 10) & 0x1F),
            static_cast<uint8_t>((rawGcr >> 5) & 0x1F),
            static_cast<uint8_t>(rawGcr & 0x1F)
        };

        int8_t nibbles[4];
        for (size_t i = 0; i < 4; ++i) {
            nibbles[i] = GcrTable[gcr[i]];
            if (nibbles[i] < 0) {
                return std::nullopt;
            }
        }

        const uint16_t val12 = (static_cast<uint16_t>(nibbles[0]) << 8) |
                               (static_cast<uint16_t>(nibbles[1]) << 4) |
                                static_cast<uint16_t>(nibbles[2]);
        const uint8_t rxCrc = static_cast<uint8_t>(nibbles[3]);

        const uint8_t expectedCrc = (~(val12 ^ (val12 >> 4) ^ (val12 >> 8))) & 0x0F;
        if (expectedCrc != rxCrc) {
            return std::nullopt;
        }

        Telemetry tlm{};
        tlm.rawType = (val12 >> 8) & 0x0F;
        tlm.rawPayload = static_cast<uint8_t>(val12 & 0xFF);

        const uint8_t exponent = (val12 >> 9) & 0x07;
        const uint16_t mantissa = val12 & 0x01FF;

        if (mantissa == 0) {
            return tlm;
        }

        const uint32_t periodUs = static_cast<uint32_t>(mantissa) << exponent;
        if (periodUs > 0) {
            tlm.erpm = 10000000UL / periodUs;
            tlm.rpm = tlm.erpm / cfg_.motorPolePairs;
        }

        return tlm;
    }

private:
    Config cfg_;

    static constexpr std::array<int8_t, 32> GcrTable = {
        -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,
        -1,   -1,   -1,   -1,   -1, 0x0D, 0x0E, 0x0F,
        -1,   -1, 0x08, 0x09,   -1, 0x05, 0x0A, 0x0B,
        -1, 0x00, 0x0C, 0x01,   -1, 0x04, 0x02, 0x03
    };
};

} // namespace dshot
```
:::

## Покроковий аналіз виконання коду та особливості оптимізації

1. **Ефективність табличного декодера GCR**:
   Таблиця `gcr_decode_table` містить 32 байти і прямо адресується 5-бітним двійковим числом `raw_gcr & 0x1F`. Це виключає повільні цикли пошуку або розгалуження через оператори вибору `switch-case`, забезпечуючи детермінований сталий час декодування в `O(1)` операцій процесора. Невалідні комбінації GCR закодовані від'ємним числом `-1` і повертають помилку розбору до перевірки контрольної суми, заощаджуючи час на обчислення XOR.

2. **Формування буфера DMA без ділення в гарячому циклі**:
   Значення регістрів порівняння таймера `ccr_bit0` та `ccr_bit1` обчислюються один раз під час ініціалізації функції `dshot_init()`. Функція заповнення буфера `dshot_fill_dma_buffer()` виконує виключно швидкі бітові операції зсуву та маскування, що займає менше `100 тактів` процесора ARM Cortex-M4/M7 для всіх 16 бітів кадру.

3. **Скидання рядків кешу даних (D-Cache Coherency)**:
   На високопродуктивних мікроконтролерах із роздільним кешем пам'яті (STM32H7, STM32F7) масив `dma_buf` повинен розміщуватися в пам'яті типу DTCM або вирівнюватися по межі 32 байтів із викликом інструкції скидання кешу перед кожною транзакцією: `SCB_CleanDCache_by_Addr((uint32_t *)dma_buf, sizeof(dma_buf))`. Без очищення кешу контролер DMA передасть у регістр таймера застарілі дані з оперативної пам'яті, що викличе спотворення команди газу або блокування передачі.

4. **Апаратна фільтрація завад при перемиканні лінії**:
   У режимі Bi-directional DShot під час захисної паузи перемикання лінії (`t_guard ≈ 30 мкс`) на сигнальному проводі можуть виникати паразитичні коливання перехідного процесу. Вхідний таймер Input Capture або приймач UART повинен активувати апаратний цифровий фільтр тригера (наприклад, біти `IC1F` у регістрі `TIMx_CCMR1`), щоб відхиляти сплески тривалістю менше `100 нс` і запобігати хибному старту прийому телеметрії.
