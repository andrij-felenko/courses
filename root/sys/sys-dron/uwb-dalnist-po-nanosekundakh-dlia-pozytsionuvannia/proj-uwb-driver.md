# ⚙️ Драйвер двостороннього дальноміра UWB на базі Decawave DW1000

Вимірювання дистанції за протоколом Double-Sided Two-Way Ranging (DS-TWR) на безпілотному апараті вимагає низькорівневого керування апаратним трансивером UWB (наприклад, Decawave DW1000 / DW3000) через послідовну шину SPI. Автопілот повинен із субнаносекундною точністю реєструвати системні таймстемпи передачі й прийому, враховувати апаратні затримки радіотракту, коректно обробляти переповнення 40-бітного лічильника системного часу та аналізувати діагностику імпульсної характеристики каналу (CIR) для фільтрації хибних відбиттів від стін (NLOS).

## Апаратні регістри та часова шкала трансивера

Трансивер DW1000 містить внутрішній тактовий генератор цифрового блока фіксації часу з частотою `63.8976 ГГц` (`128 × 499.2 МГц`). Один квант системного часу (1 LSB) дорівнює:

```
T_tick = 1 / 63 897 600 000 Гц ≈ 15.65104167 пікосекунди
```

Часові мітки прийому та передачі зберігаються у 40-бітних регістрах пам'яті трансивера:
- `SYS_TIME` (адреса 0x06, розмір 5 байтів) — поточний системний час чипа (40 біт);
- `TX_TIME` (адреса 0x17, розмір 5 байтів) — точний апаратний момент виходу першого символу преамбули кадру в антену;
- `RX_TIME` (адреса 0x15, розмір 5 байтів) — точний момент детектування точки першого променя (First Path) преамбули прийнятого кадру;
- `RX_FQUAL` (адреса 0x12, розмір 8 байтів) — діагностика якості прийому: амплітуди першого піка `FP_AMPL1`, `FP_AMPL2`, `FP_AMPL3` та індекс субдискретної точки початку імпульсу `FP_INDEX`;
- `RX_FINFO` (адреса 0x10, розмір 4 байти) — довжина прийнятого кадру та кількість накопичених символів преамбули `RXPACC`;
- `SYS_STATUS` (адреса 0x0F, розмір 5 байтів) — регістр статусних прапорців подій (`TXFRS` — передачу завершено, `RXFCG` — кадр прийнято без помилок CRC, `RXRFCE` — помилка CRC, `RXPHE` — помилка заголовка PHY, `RXRFTO` — таймаут очікування відповіді).

Оскільки апаратний лічильник 40-бітний, його повне переповнення відбувається кожні:

```
T_wrap
= 2⁴⁰ · 15.65104 · 10⁻¹² с
= 1 099 511 627 776 · 15.65104 · 10⁻¹² с
≈ 17.207 секунди
```

Будь-яке віднімання часових міток `ΔT = t_end − t_start` мусить виконуватися виключно у беззнаковій 40-бітній арифметиці з накладанням бітової маски `0xFFFFFFFFFFULL`, що гарантує математично точний результат навіть при переході через межу переповнення лічильника.

## Протокол SPI та структура заголовків трансивера

Зв'язок між польотним контролером та чипом DW1000 здійснюється за 4-провідним інтерфейсом SPI у режимі Mode 0 (CPOL = 0, CPHA = 0). Максимальна тактова частота шини SPI становить 20 МГц для операцій читання/запису даних, проте під час початкової ініціалізації після скидання (до стабілізації внутрішнього PLL) частота SPI не повинна перевищувати 3 МГц.

Формат заголовка SPI-транзакції DW1000 підтримує одно-, дво- та трибайтове кодування:
- Базовий 1-байтовий заголовок: містить біт читання/запису (R/W), біт наявності субадреси (Sub-Index) та 6-бітний номер файлу регістра (0x00–0x3F).
- Розширений заголовок із субадресою: дозволяє звертатися до окремих байтів або полів усередині великих масивів (наприклад, пам'яті накопичувача CIR `ACC_MEM` або буфера передавача `TX_BUFFER`).

Для досягнення максимальної частоти оновлення дальності (20–50 Гц на анкер) опитування статусу через SPI замінюється обробкою апаратного переривання по лінії `IRQ`: щойно чип виявляє валідний кадр або завершує передачу, він виставляє високий рівень на виводі `IRQ`, що пробуджує задачу драйвера в RTOS.

## Калібрування апаратної затримки антени

Апаратна часова мітка, зафіксована трансивером, включає не лише час поширення радіохвилі у відкритому просторі, а й внутрішні апаратні затримки:
1. Затримка проходження цифрових сигналів крізь логіку модулятора/демодулятора;
2. Затримка в аналогових фільтрах, підсилювачах низького шуму (LNA) та вихідному каскаді (PA);
3. Час поширення хвилі по мікросмужкових лініях друкованої плати та симетризувальному трансформаторі (балуні);
4. Фазовий центр самої антени.

Сумарна затримка для стандартного керамічного чи планарного модуля становить близько `513–515 нс` (понад 154 метри хибної дальності). Трансивер містить 16-бітні регістри автоматичної апаратної компенсації затримки:
- `TX_ANTD` (0x18) — затримка передавача;
- `LDO_RX_ANTD` (0x19) — затримка приймача.

Процедура калібрування полягає у встановленні тега та анкера на точно виміряній лазерним дальноміром відстані (наприклад, `5.000 м`). Драйвер виконує 1000 замірів DS-TWR із нульовими значеннями затримки антени, обчислює середню сиру дистанцію `d_raw` і розраховує калібрувальну поправку в тиках таймера:

```
ant_delay_ticks = (uint16_t)[ (d_raw − 5.0 м) / (c · T_tick · 2) ]
```

Отримане значення записується в енергонезалежну пам'ять автопілота або безпосередньо в OTP-пам'ять чіпа DW1000.

## Формат кадрів IEEE 802.15.4 UWB

Для забезпечення вимірювання за схемою DS-TWR використовуються три типи повідомлень:
1. `Poll` — опитування від тега дрона до анкера;
2. `Response` — відповідь анкера з фіксацією міток `t₂` та `t₃`;
3. `Final` — фінальний кадр тега, що містить мітки `t₁`, `t₄`, `t₅`.

Кадр містить стандартний заголовок IEEE 802.15.4: поле керування кадром (Frame Control), лічильник послідовності (Sequence Number), ідентифікатор мережі (PAN ID), 16-бітну адресу призначення (Destination Address) та адресу відправника (Source Address).

## Реалізація драйвера DS-TWR

Нижче наведено повну реалізацію обчислювального модуля та протокольного автомата DS-TWR з апаратною фільтрацією переповнення, розрахунком потужності першого променя (First Path Power) і повної потужності сигналу (Receive Signal Power) для детектування NLOS.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define UWB_SPEED_OF_LIGHT_M_S     299792458.0
#define UWB_TIME_RES_PICODECIMAL   15.65104167e-12
#define UWB_TIMESTAMP_MASK         0xFFFFFFFFFFULL
#define UWB_NLOS_THRESHOLD_DB      6.0

/* Опис кадрів протоколу TWR */
#define UWB_FRAME_POLL             0x01
#define UWB_FRAME_RESPONSE         0x02
#define UWB_FRAME_FINAL            0x03

typedef struct __attribute__((packed)) {
    uint8_t  frame_ctrl[2];
    uint8_t  seq_num;
    uint16_t pan_id;
    uint16_t dest_address;
    uint16_t src_address;
    uint8_t  message_type;
} uwb_header_t;

typedef struct __attribute__((packed)) {
    uwb_header_t header;
    uint64_t poll_tx_ts;     /* t1 (40 біт) */
    uint64_t resp_rx_ts;     /* t4 (40 біт) */
    uint64_t final_tx_ts;    /* t5 (40 біт) */
} uwb_final_msg_t;

typedef struct {
    float distance_meters;
    float first_path_power_dbm;
    float total_power_dbm;
    bool  is_nlos;
    bool  is_valid;
} uwb_range_result_t;

/* Віднімання 40-бітних часових міток з урахуванням переповнення 17.2 секунди */
static inline uint64_t uwb_ts_diff(uint64_t end_ts, uint64_t start_ts) {
    return (end_ts - start_ts) & UWB_TIMESTAMP_MASK;
}

/* Розрахунок діагностичних показників потужності за даними CIR */
void uwb_calculate_signal_quality(uint16_t fp_ampl1, uint16_t fp_ampl2, uint16_t fp_ampl3,
                                  uint16_t cir_pwr, uint16_t rxpacc,
                                  float *fpp_dbm, float *rxp_dbm, bool *is_nlos) {
    if (rxpacc == 0) {
        *fpp_dbm = -120.0f;
        *rxp_dbm = -120.0f;
        *is_nlos = true;
        return;
    }

    const float A = 121.74f; /* Константа для PRF 64 МГц у DW1000 */
    const float N = (float)rxpacc;

    /* First Path Power: FPP = 10 * log10((F1^2 + F2^2 + F3^2) / N^2) - A */
    float f1 = (float)fp_ampl1;
    float f2 = (float)fp_ampl2;
    float f3 = (float)fp_ampl3;
    float fp_sum_sq = (f1 * f1) + (f2 * f2) + (f3 * f3);
    *fpp_dbm = 10.0f * log10f(fp_sum_sq / (N * N)) - A;

    /* Receive Signal Power: RXP = 10 * log10((C * 2^17) / N^2) - A */
    float c_pwr = (float)cir_pwr;
    *rxp_dbm = 10.0f * log10f((c_pwr * 131072.0f) / (N * N)) - A;

    /* Якщо сумарна потужність перевищує перший промінь більше ніж на поріг -> NLOS */
    *is_nlos = (*rxp_dbm - *fpp_dbm) > UWB_NLOS_THRESHOLD_DB;
}

/* Обчислення дистанції за симетричною формулою DS-TWR */
uwb_range_result_t uwb_compute_ds_twr(uint64_t t1, uint64_t t2, uint64_t t3,
                                      uint64_t t4, uint64_t t5, uint64_t t6,
                                      uint16_t fp_ampl1, uint16_t fp_ampl2, uint16_t fp_ampl3,
                                      uint16_t cir_pwr, uint16_t rxpacc,
                                      int32_t ant_delay_ticks) {
    uwb_range_result_t result = {0};

    /* Інтервали тега та анкера */
    uint64_t t_round1 = uwb_ts_diff(t4, t1);
    uint64_t t_reply1 = uwb_ts_diff(t3, t2);
    uint64_t t_round2 = uwb_ts_diff(t6, t3);
    uint64_t t_reply2 = uwb_ts_diff(t5, t4);

    /* Формула симетричного DS-TWR: ToF = (T_r1 * T_r2 - T_p1 * T_p2) / (T_r1 + T_r2 + T_p1 + T_p2) */
    double r1 = (double)t_round1;
    double p1 = (double)t_reply1;
    double r2 = (double)t_round2;
    double p2 = (double)t_reply2;

    double numerator   = (r1 * r2) - (p1 * p2);
    double denominator = r1 + r2 + p1 + p2;

    if (denominator <= 0.0 || numerator <= 0.0) {
        result.is_valid = false;
        return result;
    }

    double tof_ticks = numerator / denominator;

    /* Віднімання калібрувальної затримки антени */
    tof_ticks -= (double)ant_delay_ticks;
    if (tof_ticks < 0.0) {
        tof_ticks = 0.0;
    }

    double tof_seconds = tof_ticks * UWB_TIME_RES_PICODECIMAL;
    result.distance_meters = (float)(tof_seconds * UWB_SPEED_OF_LIGHT_M_S);

    /* Діагностика якості каналу */
    uwb_calculate_signal_quality(fp_ampl1, fp_ampl2, fp_ampl3, cir_pwr, rxpacc,
                                 &result.first_path_power_dbm,
                                 &result.total_power_dbm,
                                 &result.is_nlos);

    result.is_valid = (result.distance_meters >= 0.0f && result.distance_meters <= 200.0f);
    return result;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <optional>
#include <span>

namespace uwb {

inline constexpr double SpeedOfLightMS     = 299792458.0;
inline constexpr double TimeResolutionSec  = 15.65104167e-12;
inline constexpr uint64_t TimestampMask    = 0xFFFFFFFFFFULL;
inline constexpr float NlosThresholdDb     = 6.0f;

enum class MessageType : uint8_t {
    Poll     = 0x01,
    Response = 0x02,
    Final    = 0x03
};

#pragma pack(push, 1)
struct Header {
    uint8_t     frame_ctrl[2]{};
    uint8_t     seq_num{0};
    uint16_t    pan_id{0};
    uint16_t    dest_address{0};
    uint16_t    src_address{0};
    MessageType message_type{MessageType::Poll};
};

struct FinalMessage {
    Header   header;
    uint64_t poll_tx_ts{0};     // t1
    uint64_t resp_rx_ts{0};     // t4
    uint64_t final_tx_ts{0};    // t5
};
#pragma pack(pop)

struct CirDiagnostics {
    uint16_t fp_ampl1{0};
    uint16_t fp_ampl2{0};
    uint16_t fp_ampl3{0};
    uint16_t cir_pwr{0};
    uint16_t rxpacc{0};
};

struct RangeResult {
    float distance_meters{0.0f};
    float first_path_power_dbm{0.0f};
    float total_power_dbm{0.0f};
    bool  is_nlos{false};
};

class RangingEngine {
public:
    explicit constexpr RangingEngine(int32_t antenna_delay_ticks = 16436) noexcept
        : antenna_delay_ticks_(antenna_delay_ticks) {}

    [[nodiscard]] static constexpr uint64_t diffTimestamp(uint64_t end_ts, uint64_t start_ts) noexcept {
        return (end_ts - start_ts) & TimestampMask;
    }

    [[nodiscard]] static std::pair<float, float> evaluatePower(const CirDiagnostics& diag) noexcept {
        if (diag.rxpacc == 0) {
            return {-120.0f, -120.0f};
        }
        constexpr float PrfConstantA = 121.74f;
        const float n = static_cast<float>(diag.rxpacc);
        const float f1 = static_cast<float>(diag.fp_ampl1);
        const float f2 = static_cast<float>(diag.fp_ampl2);
        const float f3 = static_cast<float>(diag.fp_ampl3);

        const float fp_sum = (f1 * f1) + (f2 * f2) + (f3 * f3);
        const float fpp = 10.0f * std::log10(fp_sum / (n * n)) - PrfConstantA;

        const float c_pwr = static_cast<float>(diag.cir_pwr);
        const float rxp = 10.0f * std::log10((c_pwr * 131072.0f) / (n * n)) - PrfConstantA;

        return {fpp, rxp};
    }

    [[nodiscard]] std::optional<RangeResult> computeDoubleSided(
        uint64_t t1, uint64_t t2, uint64_t t3,
        uint64_t t4, uint64_t t5, uint64_t t6,
        const CirDiagnostics& diag) const noexcept {

        const uint64_t t_round1 = diffTimestamp(t4, t1);
        const uint64_t t_reply1 = diffTimestamp(t3, t2);
        const uint64_t t_round2 = diffTimestamp(t6, t3);
        const uint64_t t_reply2 = diffTimestamp(t5, t4);

        const double r1 = static_cast<double>(t_round1);
        const double p1 = static_cast<double>(t_reply1);
        const double r2 = static_cast<double>(t_round2);
        const double p2 = static_cast<double>(t_reply2);

        const double numerator   = (r1 * r2) - (p1 * p2);
        const double denominator = r1 + r2 + p1 + p2;

        if (denominator <= 0.0 || numerator <= 0.0) {
            return std::nullopt;
        }

        double tof_ticks = (numerator / denominator) - static_cast<double>(antenna_delay_ticks_);
        if (tof_ticks < 0.0) {
            tof_ticks = 0.0;
        }

        const double tof_sec = tof_ticks * TimeResolutionSec;
        const float distance = static_cast<float>(tof_sec * SpeedOfLightMS);

        if (distance < 0.0f || distance > 200.0f) {
            return std::nullopt;
        }

        const auto [fpp, rxp] = evaluatePower(diag);
        const bool nlos = (rxp - fpp) > NlosThresholdDb;

        return RangeResult{
            .distance_meters      = distance,
            .first_path_power_dbm = fpp,
            .total_power_dbm      = rxp,
            .is_nlos              = nlos
        };
    }

private:
    int32_t antenna_delay_ticks_{16436};
};

} // namespace uwb
```
:::

## Типові помилки реалізації

1. **Неправильне віднімання таймстемпів без маски.** Лічильник системного часу має розрядність 40 біт. Якщо на 32-розрядній або 64-розрядній платформі виконати звичайне знакове віднімання `(int64_t)t4 - (int64_t)t1`, при переповненні результат стане від'ємним, що спричинить стрибок дальності на сотні кілометрів. Обов'язково застосовувати побітове множення `& 0xFFFFFFFFFFULL`.
2. **Неврахована затримка антени.** Якщо у формулу підставляти чисті відліки трансивера без калібрування `antenna_delay_ticks`, розрахована дальність буде завищена приблизно на 150 метрів. Затримка мусить калібруватися окремо для кожної плати за допомогою лазерного дальноміра на фіксованій відстані (наприклад, 5.0 метрів).
3. **Ігнорування статусу NLOS.** При польоті крізь дверні отвори або біля бетонних колон прямий промінь поглинається, а сигнал приходить відбитими шляхами. Якщо фільтр Калмана сприйме замір із завищенням на 1.5 метра без збільшення коваріації шуму вимірювання, автопілот різко смикне дрон у бік стіни.
4. **Блокування потоку в очікуванні переривання.** Трансивер витрачає від 0.5 до 2.0 мс на передачу кадру та очікування відповіді. Використання активного очікування (busy-wait polling) регістра `SYS_STATUS` у головному циклі польотного контролера заблокує високочастотний контур стабілізації кутових швидкостей (Rate Loop 1 кГц). Обмін пакетами UWB мусить виконуватися в окремому асинхронному низькопріоритетному потоці RTOS із повідомленнями через DMA та преривання.
