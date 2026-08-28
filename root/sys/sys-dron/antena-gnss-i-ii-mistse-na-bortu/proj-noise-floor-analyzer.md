# ⚙️ Автоматизований аналіз шумової полиці GNSS за протоколом UBX

У процесі передпольотної діагностики безпілотного апарата оператор або бортовий скрипт автопілота повинен отримати об'єктивну кількісну оцінку радіочастотної обстановки в навігаційних діапазонах. Якщо навігаційний модуль зазнає внутрішньобортового зашумлення від регуляторів обертів (ESC), перетворювачів напруги або відеопередавача (VTX), оцінка відношення сигнал/шум супутників `C/N₀` падає, а фазові вимірювання деградують аж до зриву супроводу несучої. Моніторинг радіочастотного тракту в реальному часі реалізується за допомогою опитування внутрішніх діагностичних повідомлень навігаційного приймача. У приймачах поколінь u-blox M8, M9 та F9 для цього призначено бінарне повідомлення `UBX-MON-RF` (клас `0x0A`, ідентифікатор `0x38`).

Діагностична утиліта підключається до послідовного порту приймача (UART), надсилає запит на видачу повідомлення або налаштовує його періодичну трансляцію, розбирає потік байтів за допомогою скінченного автомата, верифікує контрольну суму алгоритмом Флетчера (Fletcher-8) та аналізує метрики радіочастотного тракту для кожного активного діапазону.

### Структура діагностичного кадру UBX-MON-RF

Кожен бінарний пакет протоколу UBX починається з двобайтового заголовка синхронізації `0xB5 0x62`, після якого передаються однобайтові поля класу повідомлення, ідентифікатора, двобайтова довжина корисного навантаження (у форматі Little-Endian) та власне дані. Завершується пакет двома байтами контрольної суми `CK_A` та `CK_B`, які обчислюються над полями класу, ідентифікатора, довжини та корисного навантаження за циклічним алгоритмом додавання за модулем 256.

```
+---------+---------+-------+------+------------+------------------+------+------+
| SYNC_1  | SYNC_2  | CLASS |  ID  | LENGTH_LSB | PAYLOAD (N байт) | CK_A | CK_B |
|  0xB5   |  0x62   | 0x0A  | 0x38 | LENGTH_MSB |                  |      |      |
+---------+---------+-------+------+------------+------------------+------+------+
```

Математично контрольна сума є реалізацією алгоритму Fletcher-8 (RFC 1145), де два накопичувачі `CK_A` та `CK_B` ініціалізуються нулями та оновлюються для кожного наступного байта `D_i`:

```
CK_A[i] = (CK_A[i−1] + D_i) mod 256      [додавання поточного байта до першої суми]
CK_B[i] = (CK_B[i−1] + CK_A[i]) mod 256  [накопичення суми сум у другому байті]
```

Корисне навантаження `UBX-MON-RF` складається з однобайтового номера версії протоколу `version`, однобайтової кількості радіочастотних блоків `nBlocks` (для одночастотних модулів — 1, для мультидіапазонних, таких як ZED-F9P, — 2 або більше), двох зарезервованих байтів і повторюваного масиву структур для кожного радіотракту:

```
[Заголовок корисного навантаження: 4 байти]
- uint8_t  version       (версія структури повідомлення, зазвичай 0x00 або 0x01)
- uint8_t  nBlocks       (кількість апаратних RF-блоків у звіті)
- uint8_t  reserved1[2]  (резервні байти)

[Блок даних тракту RF: 24 байти на кожен блок]
- uint8_t  blockId       (індекс тракту: 0 = RF1 / L1-діапазон, 1 = RF2 / L2/L5-діапазон)
- uint8_t  flags         (прапорці стану антени: біт 0 — статус антени активний)
- uint8_t  antStatus     (стан підключення антени: 0 = INIT, 1 = DONTKNOW, 2 = OK, 3 = SHORT, 4 = OPEN)
- uint8_t  antPower      (живлення активної антени: 0 = OFF, 1 = ON, 2 = DONTKNOW)
- uint32_t postStatus    (бітова маска стану після обробки)
- uint16_t noisePerMS    (рівень шуму у вибірках корелятора, норма: 30...70, завада: > 100)
- uint16_t agcCnt        (значення лічильника АРП 0...8191, норма: > 6000, завада: < 4000)
- uint8_t  jamInd        (індикатор завади 0...255: 0...30 — чисто, > 100 — критична завада)
- uint8_t  flags2        (додаткові прапорці та джерело моніторингу)
- uint8_t  jammingState  (рівень придушення: 0 = невідомо, 1 = чисто, 2 = попередження, 3 = глушіння)
- uint8_t  reserved2     (резерв)
- uint32_t noiseExp      (експоненційна оцінка шуму базової смуги)
```

### Фізичний зміст діагностичних полів

Кожне поле блоку `UBX-MON-RF` відображає роботу конкретного апаратного каскаду радіочастотного приймача:

1. **Апаратний супервізор антени (`antStatus`, `antPower`):**
   Усередині модуля GNSS лінія живлення активної антени Bias-Tee проходить крізь струмовимірювальний шунт (зазвичай `0.5...2.0 Ом`) та компаратори напруги. Якщо струм споживання підсилювача LNA лежить у штатному діапазоні (зазвичай 5–25 мА), супервізор виставляє статус `antStatus = 2` (`OK`). Якщо кабель антени від'єднано або пошкоджено центральну жилу, струм падає нижче 1 мА, і виставляється статус `antStatus = 4` (`OPEN`). Якщо ж коаксіальний кабель затиснуто або пошкоджено діелектрик, виникає коротке замикання, струм перевищує 50 мА, і захисний ключ вимикає живлення антени (`antPower = 0`), сигналізуючи `antStatus = 3` (`SHORT`).

2. **Дисперсія шуму цифрового корелятора (`noisePerMS`):**
   Після оцифрування радіосигналу квадратурним АЦП (I/Q ADC) базова смуга обчислює середньоквадратичну дисперсію вибірок на ділянках, де відсутня кореляція з супутниковими PRN-кодами. За відсутності зовнішнього зашумлення величина `noisePerMS` коливається в межах 35–60 одиниць. Зростання цього показника під час роботи двигунів або передавачів свідчить про наявність широкосмугової завади, яка перекриває навігаційні канали.

3. **Лічильник петлі АРП (`agcCnt`):**
   Автоматичне регулювання підсилення підтримує оптимальну амплітуду сигналу на вході АЦП, захищаючи його від переповнення та нелінійних спотворень. Величина `agcCnt` змінюється від 0 (максимальне ослаблення атенюатором) до 8191 (максимальне підсилення тракту). У нормальних умовах з пасивною антеною значення перебуває в діапазоні 6500–8100. Якщо поруч працює потужний передавач (наприклад, VTX на 1.3 ГГц), паразитна потужність перевантажує вхід, і петля АРП «затискає» коефіцієнт підсилення, внаслідок чого `agcCnt` падає до 2000–3500.

4. **Індикатор глушіння (`jamInd` та `jammingState`):**
   Приймач аналізує співвідношення між рівнем шуму та інтегральною потужністю спектральних компонентів. Якщо виявлено неперервну гармоніку (CW-заваду) або імпульсне випромінювання, `jamInd` зростає від 0 (чистий ефір) до 255 (повне придушення сигналу).

### Алгоритм скінченного автомата та аналіз метрик

Для стійкого прийому бінарного потоку в умовах можливих спотворень даних послідовного порту використовується детермінований скінченний автомат (англ. *Finite State Machine*, FSM). Автомат має вісім станів: пошук першого байта синхронізації `0xB5`, перевірка другого байта `0x62`, зчитування класу, зчитування ідентифікатора, читання двох байтів довжини, наповнення буфера корисного навантаження та послідовна перевірка байтів контрольної суми `CK_A` і `CK_B`. Якщо в будь-якому стані надходить невідповідний байт, автомат скидає накопичувальний буфер і повертається до стану пошуку заголовка, уникаючи зависання чи переповнення пам'яті.

Після успішної перевірки контрольної суми модуль аналізу зіставляє виміряні величини із встановленими порогами безпеки:
1. Якщо `jamInd > 120` або `jammingState == 3`, фіксується подія критичного глушіння (наприклад, включення потужного наземного засобу РЕБ або пряма наводка від відеопередавача 1.3 ГГц).
2. Якщо `noisePerMS` зростає більш ніж на 20% під час розкрутки двигунів БПЛА, фіксується кондуктивна та випромінювальна завада від комутації ключів ESC, що вимагає встановлення додаткових LC-фільтрів або виносу антени на щоглу.
3. Якщо значення `agcCnt` різко падає при незмінному `noisePerMS`, це вказує на потрапляння в приймальний тракт потужного позасмугового сигналу, який перевантажує вхідний підсилювач LNA і змушує систему АРП знижувати коефіцієнт передачі для захисту АЦП від насичення.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define UBX_SYNC1 0xB5
#define UBX_SYNC2 0x62
#define UBX_CLASS_MON 0x0A
#define UBX_ID_MON_RF 0x38
#define UBX_MAX_PAYLOAD 256

typedef enum {
    UBX_STATE_SYNC1 = 0,
    UBX_STATE_SYNC2,
    UBX_STATE_CLASS,
    UBX_STATE_ID,
    UBX_STATE_LEN_LSB,
    UBX_STATE_LEN_MSB,
    UBX_STATE_PAYLOAD,
    UBX_STATE_CKA,
    UBX_STATE_CKB
} ubx_state_t;

typedef struct {
    uint8_t block_id;
    uint8_t ant_status;
    uint8_t ant_power;
    uint16_t noise_per_ms;
    uint16_t agc_cnt;
    uint8_t jam_ind;
    uint8_t jamming_state;
} gnss_rf_block_metrics_t;

typedef struct {
    uint8_t version;
    uint8_t num_blocks;
    gnss_rf_block_metrics_t blocks[4];
    bool valid;
} gnss_rf_report_t;

typedef enum {
    RF_STATUS_OK = 0,
    RF_STATUS_WARNING_NOISE,
    RF_STATUS_CRITICAL_JAMMING,
    RF_STATUS_AGC_SATURATED
} rf_health_status_t;

typedef struct {
    ubx_state_t state;
    uint8_t msg_class;
    uint8_t msg_id;
    uint16_t payload_len;
    uint16_t payload_idx;
    uint8_t payload[UBX_MAX_PAYLOAD];
    uint8_t ck_a;
    uint8_t ck_b;
    uint8_t calc_ck_a;
    uint8_t calc_ck_b;
} ubx_parser_ctx_t;

static void ubx_update_checksum(uint8_t byte, uint8_t *ck_a, uint8_t *ck_b) {
    *ck_a = (uint8_t)(*ck_a + byte);
    *ck_b = (uint8_t)(*ck_b + *ck_a);
}

void ubx_parser_init(ubx_parser_ctx_t *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(ubx_parser_ctx_t));
    ctx->state = UBX_STATE_SYNC1;
}

bool ubx_parser_feed_byte(ubx_parser_ctx_t *ctx, uint8_t b, gnss_rf_report_t *report) {
    if (!ctx || !report) return false;

    switch (ctx->state) {
        case UBX_STATE_SYNC1:
            if (b == UBX_SYNC1) {
                ctx->state = UBX_STATE_SYNC2;
            }
            break;

        case UBX_STATE_SYNC2:
            if (b == UBX_SYNC2) {
                ctx->state = UBX_STATE_CLASS;
                ctx->calc_ck_a = 0;
                ctx->calc_ck_b = 0;
            } else {
                ctx->state = UBX_STATE_SYNC1;
            }
            break;

        case UBX_STATE_CLASS:
            ctx->msg_class = b;
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            ctx->state = UBX_STATE_ID;
            break;

        case UBX_STATE_ID:
            ctx->msg_id = b;
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            ctx->state = UBX_STATE_LEN_LSB;
            break;

        case UBX_STATE_LEN_LSB:
            ctx->payload_len = b;
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            ctx->state = UBX_STATE_LEN_MSB;
            break;

        case UBX_STATE_LEN_MSB:
            ctx->payload_len |= (uint16_t)(b << 8);
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            ctx->payload_idx = 0;
            if (ctx->payload_len > UBX_MAX_PAYLOAD) {
                ctx->state = UBX_STATE_SYNC1;
            } else if (ctx->payload_len == 0) {
                ctx->state = UBX_STATE_CKA;
            } else {
                ctx->state = UBX_STATE_PAYLOAD;
            }
            break;

        case UBX_STATE_PAYLOAD:
            ctx->payload[ctx->payload_idx++] = b;
            ubx_update_checksum(b, &ctx->calc_ck_a, &ctx->calc_ck_b);
            if (ctx->payload_idx >= ctx->payload_len) {
                ctx->state = UBX_STATE_CKA;
            }
            break;

        case UBX_STATE_CKA:
            ctx->ck_a = b;
            ctx->state = UBX_STATE_CKB;
            break;

        case UBX_STATE_CKB:
            ctx->ck_b = b;
            ctx->state = UBX_STATE_SYNC1;
            if (ctx->ck_a == ctx->calc_ck_a && ctx->ck_b == ctx->calc_ck_b) {
                if (ctx->msg_class == UBX_CLASS_MON && ctx->msg_id == UBX_ID_MON_RF) {
                    if (ctx->payload_len >= 4) {
                        report->version = ctx->payload[0];
                        report->num_blocks = ctx->payload[1];
                        if (report->num_blocks > 4) report->num_blocks = 4;

                        for (uint8_t i = 0; i < report->num_blocks; ++i) {
                            size_t offset = 4 + (size_t)i * 24;
                            if (offset + 24 <= ctx->payload_len) {
                                gnss_rf_block_metrics_t *blk = &report->blocks[i];
                                blk->block_id = ctx->payload[offset + 0];
                                blk->ant_status = ctx->payload[offset + 2];
                                blk->ant_power = ctx->payload[offset + 3];
                                blk->noise_per_ms = (uint16_t)(ctx->payload[offset + 8] | (ctx->payload[offset + 9] << 8));
                                blk->agc_cnt = (uint16_t)(ctx->payload[offset + 10] | (ctx->payload[offset + 11] << 8));
                                blk->jam_ind = ctx->payload[offset + 12];
                                blk->jamming_state = ctx->payload[offset + 14];
                            }
                        }
                        report->valid = true;
                        return true;
                    }
                }
            }
            break;
    }
    return false;
}

rf_health_status_t gnss_evaluate_rf_health(const gnss_rf_block_metrics_t *metrics, uint16_t baseline_noise) {
    if (!metrics) return RF_STATUS_OK;

    if (metrics->jam_ind > 100 || metrics->jamming_state == 3) {
        return RF_STATUS_CRITICAL_JAMMING;
    }
    if (metrics->agc_cnt < 4000) {
        return RF_STATUS_AGC_SATURATED;
    }
    if (baseline_noise > 0 && metrics->noise_per_ms > (uint16_t)(baseline_noise * 1.3f)) {
        return RF_STATUS_WARNING_NOISE;
    }
    return RF_STATUS_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <string_view>

enum class UbxClass : uint8_t {
    Mon = 0x0A
};

enum class UbxMonId : uint8_t {
    Rf = 0x38
};

enum class AntStatus : uint8_t {
    Init = 0,
    Unknown = 1,
    Ok = 2,
    Short = 3,
    Open = 4
};

enum class JammingState : uint8_t {
    Unknown = 0,
    Clean = 1,
    Warning = 2,
    Critical = 3
};

enum class RfHealthStatus {
    Ok,
    NoiseElevated,
    AgcSaturated,
    CriticalJamming
};

struct RfBlockMetrics {
    uint8_t block_id{0};
    AntStatus ant_status{AntStatus::Unknown};
    uint8_t ant_power{0};
    uint16_t noise_per_ms{0};
    uint16_t agc_cnt{0};
    uint8_t jam_ind{0};
    JammingState jamming_state{JammingState::Unknown};
};

struct RfDiagnosticReport {
    uint8_t version{0};
    uint8_t num_blocks{0};
    std::array<RfBlockMetrics, 4> blocks{};

    [[nodiscard]] constexpr RfHealthStatus evaluate(size_t block_idx, uint16_t baseline_noise) const noexcept {
        if (block_idx >= num_blocks) return RfHealthStatus::Ok;
        const auto& blk = blocks[block_idx];

        if (blk.jam_ind > 100 || blk.jamming_state == JammingState::Critical) {
            return RfHealthStatus::CriticalJamming;
        }
        if (blk.agc_cnt < 4000) {
            return RfHealthStatus::AgcSaturated;
        }
        if (baseline_noise > 0 && blk.noise_per_ms > static_cast<uint16_t>(baseline_noise * 1.3f)) {
            return RfHealthStatus::NoiseElevated;
        }
        return RfHealthStatus::Ok;
    }
};

class UbxMonRfParser {
public:
    enum class ParserError {
        BufferOverflow,
        InvalidChecksum,
        IncompletePayload
    };

    constexpr void reset() noexcept {
        state_ = State::Sync1;
        payload_len_ = 0;
        payload_idx_ = 0;
        ck_a_ = 0;
        ck_b_ = 0;
        calc_ck_a_ = 0;
        calc_ck_b_ = 0;
    }

    [[nodiscard]] std::expected<bool, ParserError> feed_byte(uint8_t b, RfDiagnosticReport& out_report) noexcept {
        switch (state_) {
            case State::Sync1:
                if (b == 0xB5) state_ = State::Sync2;
                break;

            case State::Sync2:
                if (b == 0x62) {
                    state_ = State::Class;
                    calc_ck_a_ = 0;
                    calc_ck_b_ = 0;
                } else {
                    state_ = State::Sync1;
                }
                break;

            case State::Class:
                msg_class_ = b;
                accumulate_ck(b);
                state_ = State::Id;
                break;

            case State::Id:
                msg_id_ = b;
                accumulate_ck(b);
                state_ = State::LenLsb;
                break;

            case State::LenLsb:
                payload_len_ = b;
                accumulate_ck(b);
                state_ = State::LenMsb;
                break;

            case State::LenMsb:
                payload_len_ |= static_cast<uint16_t>(b << 8);
                accumulate_ck(b);
                payload_idx_ = 0;
                if (payload_len_ > max_payload_size) {
                    state_ = State::Sync1;
                    return std::unexpected(ParserError::BufferOverflow);
                }
                state_ = (payload_len_ == 0) ? State::CkA : State::Payload;
                break;

            case State::Payload:
                payload_[payload_idx_++] = b;
                accumulate_ck(b);
                if (payload_idx_ >= payload_len_) {
                    state_ = State::CkA;
                }
                break;

            case State::CkA:
                ck_a_ = b;
                state_ = State::CkB;
                break;

            case State::CkB:
                ck_b_ = b;
                state_ = State::Sync1;
                if (ck_a_ != calc_ck_a_ || ck_b_ != calc_ck_b_) {
                    return std::unexpected(ParserError::InvalidChecksum);
                }
                if (msg_class_ == static_cast<uint8_t>(UbxClass::Mon) &&
                    msg_id_ == static_cast<uint8_t>(UbxMonId::Rf)) {
                    return parse_payload(out_report);
                }
                break;
        }
        return false;
    }

private:
    enum class State {
        Sync1,
        Sync2,
        Class,
        Id,
        LenLsb,
        LenMsb,
        Payload,
        CkA,
        CkB
    };

    static constexpr size_t max_payload_size = 256;

    constexpr void accumulate_ck(uint8_t b) noexcept {
        calc_ck_a_ = static_cast<uint8_t>(calc_ck_a_ + b);
        calc_ck_b_ = static_cast<uint8_t>(calc_ck_b_ + calc_ck_a_);
    }

    [[nodiscard]] std::expected<bool, ParserError> parse_payload(RfDiagnosticReport& out_report) const noexcept {
        if (payload_len_ < 4) {
            return std::unexpected(ParserError::IncompletePayload);
        }
        out_report.version = payload_[0];
        const uint8_t n_blocks = payload_[1];
        out_report.num_blocks = (n_blocks > 4) ? 4 : n_blocks;

        for (uint8_t i = 0; i < out_report.num_blocks; ++i) {
            const size_t offset = 4 + static_cast<size_t>(i) * 24;
            if (offset + 24 > payload_len_) break;

            auto& blk = out_report.blocks[i];
            blk.block_id = payload_[offset + 0];
            blk.ant_status = static_cast<AntStatus>(payload_[offset + 2]);
            blk.ant_power = payload_[offset + 3];
            blk.noise_per_ms = static_cast<uint16_t>(payload_[offset + 8] | (payload_[offset + 9] << 8));
            blk.agc_cnt = static_cast<uint16_t>(payload_[offset + 10] | (payload_[offset + 11] << 8));
            blk.jam_ind = payload_[offset + 12];
            blk.jamming_state = static_cast<JammingState>(payload_[offset + 14]);
        }
        return true;
    }

    State state_{State::Sync1};
    uint8_t msg_class_{0};
    uint8_t msg_id_{0};
    uint16_t payload_len_{0};
    uint16_t payload_idx_{0};
    uint8_t ck_a_{0};
    uint8_t ck_b_{0};
    uint8_t calc_ck_a_{0};
    uint8_t calc_ck_b_{0};
    std::array<uint8_t, max_payload_size> payload_{};
};
```
:::

### Пастки реалізації та крайові випадки

1. **Втрата синхронізації при просіданні напруги:** Під час різкої подачі газу напруга на шині 5 В польотного контролера може короткочасно просідати, спричиняючи втрату або спотворення байтів у буфері UART. Скінченний автомат обов'язково повинен обробляти поодинокі байти `0xB5` всередині корисного навантаження без переривання сесії, якщо довжина пакету ще не вичерпана.
2. **Багатодіапазонні приймачі:** У приймачах F9P перший блок (`blockId = 0`) описує тракт L1 (GPS L1, GLONASS G1, Galileo E1, BeiDou B1), а другий (`blockId = 1`) — тракт L2/L5 (GPS L2C, Galileo E5b, BeiDou B2I). Завада від відеопередавача 1.3 ГГц часто повністю блокує блок `blockId = 1` через низький частотний рознос, тоді як блок `blockId = 0` демонструє нормальні показники. Необхідно аналізувати кожен блок окремо, а не лише перший елемент масиву.
3. **Хибне спрацьовування індикатора завад при активній антені:** Якщо модуль використовує активну антену з надмірно високим власним підсиленням (> 32 dB), шум першого каскаду LNA може піднімати `noisePerMS` до значень 80–90 навіть у повній радіоізоляції. Оцінка має будуватися на відносній дельті між станом спокою та роботою силової установки.
4. **Конфлікт швидкостей послідовного порту:** За замовчуванням багато модулів GNSS запускаються на швидкості 9600 або 38400 біт/с. При частоті оновлення навігаційних повідомлень 5–10 Гц передача важких діагностичних пакетів `UBX-MON-RF` разом із `UBX-NAV-PVT` переповнює пропускну здатність UART-каналу. Перед увімкненням періодичної трансляції `UBX-MON-RF` швидкість порту необхідно програмно перевести на 115200 або 230400 біт/с конфігураційним повідомленням `UBX-CFG-PRT`.
