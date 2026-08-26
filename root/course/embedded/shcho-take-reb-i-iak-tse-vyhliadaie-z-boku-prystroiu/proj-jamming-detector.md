# ⚙️ Детектор та класифікатор радіоелектронних завад для вбудованих систем

Коли вбудований пристрій (БПЛА, наземний автономний робот або телеметричний датчик) потрапляє в зону дії радіоелектронної боротьби, прошивка не повинна чекати аварійного тайм-ауту втрати зв'язку (зазвичай 1–3 секунди), щоб зрозуміти, що канал деградував. Вчасне розпізнавання фізичного типу завади дозволяє системі миттєво вжити заходів протидії: перемкнути робочий канал FHSS, увімкнути вхідний атенюатор для виведення LNA з насичення, або відкинути скомпрометовані координати GNSS і перейти на інерціальне числення шляху.

Нижче наведено повний модуль обробки радіотелеметрії та класифікації загроз РЕБ на базі аналізу ковзного вікна показників трансивера та супутникового приймача.

---

## 1. Архітектура телеметричного аналізатора

Детектор спроектовано як детермінований автомат зі сталим часом виконання (без динамічного виділення пам'яті), який періодично отримує сирі виміри від радіомодуля (через SPI/UART) та GNSS-стека:

1. **Кільцевий буфер ковзного вікна** зберігає вибірки за останні `N` інтервалів (за замовчуванням `N = 16`, що відповідає останнім 1.6 секунди за частоти опитування 10 Гц).
2. **Статистичний аналізатор** обчислює середні значення, дисперсію RSSI, коефіцієнт втрат пакетів (PER), стан автоматичного регулювання підсилення (AGC) та розподіл відношення несуча/шум (CNR) супутників GNSS.
3. **Діагностична матриця правил** порівнює показники з пороговими константами та виносить вердикт про поточний стан радіоефіру.

```
       ┌────────────────────────┐
       │   RF Transceiver SPI   │──► [RSSI, SNR, AGC, Sync, CRC] ──┐
       └────────────────────────┘                                  │
                                                                   ▼
       ┌────────────────────────┐                          ┌──────────────┐      ┌─────────────────────────┐
       │     GNSS NMEA/UBX      │──► [CNR, Doppler, Clock] ─►  Статистика ─►│ Класифікатор загроз РЕБ │
       └────────────────────────┘                          │  і вікно     │      └─────────────────────────┘
                                                           └──────────────┘                   │
                                                                                              ▼
                                                                                   [ Вердикт та реакція ]
                                                                                   • Зміна каналу FHSS
                                                                                   • Увімкнення RF атенюатора
                                                                                   • Блокування GNSS / IMU
```

### Фіксація та нормалізація метрик

Усі внутрішні обчислення модуля виконуються у цілочисельній арифметиці з фіксованою комою, щоб гарантувати роботу на бюджетних мікроконтролерах Cortex-M0+/M3 без апаратного блоку FPU:
* `rssi_dbm` зберігається як знакове 16-бітне ціле число в дБм (наприклад, −85 дБм);
* `cnr_x10` для супутників зберігається як десяткові частки дБ-Гц (значення 42.5 дБ-Гц записується як 425);
* `agc_gain_code` нормалізується до діапазону 0–255 (де 0 відповідає мінімальному підсиленню або увімкненому атенюатору, а 255 — максимальному підсиленню LNA);
* Дисперсія RSSI `Var(RSSI) = E[(RSSI - μ)²]` обчислюється в один прохід через накопичувальний регістр квадратів різниць без втрати точності.

### Евристика однорідності сузір'я GNSS

Для розпізнавання супутникового спуфінгу модуль аналізує когерентність сигналів усього сузір'я. Замість важкого обчислення середньоквадратичного відхилення зі взяттям квадратного кореня, алгоритм застосовує середнє абсолютне відхилення (MAD, англ. *Mean Absolute Deviation*):

```
MAD = (1 / K) · ∑ |CNR[i] - CNR_avg|
```

Якщо понад 70% супутників мають рівень `CNR >= 51.0` дБ-Гц при загальному відхиленні `MAD <= 2.5` дБ-Гц, генератор випромінює всі супутникові коди з єдиної наземної антени. Справжні супутники, розкидані по всій небесній півсфері на різних кутах місця, фізично не можуть забезпечити таку неприродну однорідність енергетичних рівнів.

---

## 2. Повна реалізація модуля (C та C++)

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define EW_WINDOW_SIZE          16
#define EW_MAX_GNSS_SATS        12

#define EW_RSSI_JAM_THRESHOLD_DBM     (-65)
#define EW_RSSI_BARRAGE_THRESHOLD_DBM (-40)
#define EW_RSSI_PULSE_VARIANCE_MIN    (120)
#define EW_PER_JAM_THRESHOLD_PCT      (75)
#define EW_GNSS_SPOOF_CNR_THRESHOLD   (510) /* 51.0 дБ-Гц у сотих */
#define EW_GNSS_SPOOF_DEV_MAX         (25)  /* 2.5 дБ-Гц відхилення */

typedef enum {
    EW_THREAT_NONE = 0,
    EW_THREAT_WEAK_SIGNAL,
    EW_THREAT_SPOT_JAMMING,
    EW_THREAT_BARRAGE_BLOCKING,
    EW_THREAT_PULSE_JAMMING,
    EW_THREAT_GNSS_SPOOFING
} ew_threat_type_t;

typedef struct {
    int16_t  rssi_dbm;          /* Рівень вхідного сигналу, дБм */
    int8_t   snr_db;            /* Відношення сигнал/шум, дБ */
    uint8_t  agc_gain_code;     /* Стан підсилення AGC (0 - мін, 255 - макс) */
    bool     preamble_detected; /* Чи була знайдена преамбула/Sync Word */
    bool     crc_error;         /* Чи виявлено помилку контрольної суми */
} ew_rf_sample_t;

typedef struct {
    uint8_t prn;                /* Номер супутника */
    uint16_t cnr_x10;           /* CNR у дБ-Гц помножений на 10 (напр. 425 = 42.5) */
    int16_t  doppler_hz;        /* Доплерівський зсув частоти, Гц */
    uint8_t  elevation_deg;     /* Кут місця над горизонтом, градуси */
} ew_gnss_sat_t;

typedef struct {
    uint8_t sat_count;
    ew_gnss_sat_t sats[EW_MAX_GNSS_SATS];
    bool clock_jump_detected;
    bool pos_jump_without_imu;
} ew_gnss_frame_t;

typedef struct {
    ew_rf_sample_t rf_history[EW_WINDOW_SIZE];
    uint8_t        rf_head;
    uint8_t        rf_count;

    ew_threat_type_t current_threat;
    uint32_t         threat_duration_ms;
} ew_detector_t;

void ew_detector_init(ew_detector_t *det) {
    if (!det) return;
    memset(det, 0, sizeof(ew_detector_t));
    det->current_threat = EW_THREAT_NONE;
}

void ew_detector_push_rf(ew_detector_t *det, const ew_rf_sample_t *sample) {
    if (!det || !sample) return;
    det->rf_history[det->rf_head] = *sample;
    det->rf_head = (det->rf_head + 1) % EW_WINDOW_SIZE;
    if (det->rf_count < EW_WINDOW_SIZE) {
        det->rf_count++;
    }
}

static bool ew_check_gnss_spoofing(const ew_gnss_frame_t *gnss) {
    if (!gnss || gnss->sat_count < 4) return false;

    if (gnss->pos_jump_without_imu || gnss->clock_jump_detected) {
        return true;
    }

    uint32_t cnr_sum = 0;
    uint8_t high_cnr_count = 0;

    for (uint8_t i = 0; i < gnss->sat_count; i++) {
        cnr_sum += gnss->sats[i].cnr_x10;
        if (gnss->sats[i].cnr_x10 >= EW_GNSS_SPOOF_CNR_THRESHOLD) {
            high_cnr_count++;
        }
    }

    uint16_t cnr_avg = (uint16_t)(cnr_sum / gnss->sat_count);

    /* Обчислення середнього абсолютного відхилення рівнів сигналу */
    uint32_t dev_sum = 0;
    for (uint8_t i = 0; i < gnss->sat_count; i++) {
        int32_t diff = (int32_t)gnss->sats[i].cnr_x10 - (int32_t)cnr_avg;
        if (diff < 0) diff = -diff;
        dev_sum += (uint32_t)diff;
    }
    uint16_t cnr_mean_dev = (uint16_t)(dev_sum / gnss->sat_count);

    /* Ознака спуфінгу: понад 70% супутників мають неприродний CNR > 51 дБ-Гц
       і однаковий рівень сигналу від однієї передавальної антени */
    if ((high_cnr_count * 100 / gnss->sat_count) >= 70 && cnr_mean_dev <= EW_GNSS_SPOOF_DEV_MAX) {
        return true;
    }

    return false;
}

ew_threat_type_t ew_detector_evaluate(ew_detector_t *det, const ew_gnss_frame_t *gnss) {
    if (!det || det->rf_count == 0) return EW_THREAT_NONE;

    /* 1. Спершу перевіряємо спуфінг навігації */
    if (ew_check_gnss_spoofing(gnss)) {
        det->current_threat = EW_THREAT_GNSS_SPOOFING;
        return EW_THREAT_GNSS_SPOOFING;
    }

    /* 2. Обчислення статистик радіоканалу */
    int32_t rssi_sum = 0;
    uint32_t agc_sum = 0;
    uint8_t crc_errors = 0;
    uint8_t sync_hits = 0;

    for (uint8_t i = 0; i < det->rf_count; i++) {
        rssi_sum += det->rf_history[i].rssi_dbm;
        agc_sum += det->rf_history[i].agc_gain_code;
        if (det->rf_history[i].crc_error) crc_errors++;
        if (det->rf_history[i].preamble_detected) sync_hits++;
    }

    int16_t avg_rssi = (int16_t)(rssi_sum / det->rf_count);
    uint8_t avg_agc = (uint8_t)(agc_sum / det->rf_count);
    uint8_t per = (uint8_t)((crc_errors * 100) / det->rf_count);

    /* Обчислення дисперсії RSSI для імпульсних завад */
    uint32_t rssi_var_sum = 0;
    for (uint8_t i = 0; i < det->rf_count; i++) {
        int32_t diff = (int32_t)det->rf_history[i].rssi_dbm - (int32_t)avg_rssi;
        rssi_var_sum += (uint32_t)(diff * diff);
    }
    uint32_t rssi_variance = rssi_var_sum / det->rf_count;

    /* 3. Класифікація стану зв'язку */
    if (avg_rssi >= EW_RSSI_BARRAGE_THRESHOLD_DBM && avg_agc <= 30 && sync_hits == 0) {
        det->current_threat = EW_THREAT_BARRAGE_BLOCKING;
    } else if (avg_rssi >= EW_RSSI_JAM_THRESHOLD_DBM && per >= EW_PER_JAM_THRESHOLD_PCT && sync_hits <= 1) {
        det->current_threat = EW_THREAT_SPOT_JAMMING;
    } else if (rssi_variance >= EW_RSSI_PULSE_VARIANCE_MIN && per >= 40) {
        det->current_threat = EW_THREAT_PULSE_JAMMING;
    } else if (avg_rssi <= -105 && per >= EW_PER_JAM_THRESHOLD_PCT) {
        det->current_threat = EW_THREAT_WEAK_SIGNAL;
    } else {
        det->current_threat = EW_THREAT_NONE;
    }

    return det->current_threat;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <numeric>
#include <algorithm>

namespace embedded::ew {

enum class ThreatType : uint8_t {
    None = 0,
    WeakSignal,
    SpotJamming,
    BarrageBlocking,
    PulseJamming,
    GnssSpoofing
};

struct RfSample {
    int16_t rssi_dbm{0};
    int8_t  snr_db{0};
    uint8_t agc_gain_code{255};
    bool    preamble_detected{false};
    bool    crc_error{false};
};

struct GnssSatInfo {
    uint8_t  prn{0};
    uint16_t cnr_x10{0};     // CNR in dB-Hz * 10 (450 = 45.0 dB-Hz)
    int16_t  doppler_hz{0};
    uint8_t  elevation_deg{0};
};

struct GnssFrame {
    std::span<const GnssSatInfo> satellites;
    bool clock_jump_detected{false};
    bool position_jump_without_imu{false};
};

template <std::size_t WindowSize = 16>
class ThreatClassifier {
public:
    static constexpr int16_t  kRssiJamThresholdDbm{-65};
    static constexpr int16_t  kRssiBarrageThresholdDbm{-40};
    static constexpr uint32_t kRssiPulseVarianceMin{120};
    static constexpr uint8_t   kPerJamThresholdPct{75};
    static constexpr uint16_t  kGnssSpoofCnrThreshold{510}; // 51.0 dB-Hz
    static constexpr uint16_t  kGnssSpoofMaxDev{25};       // 2.5 dB-Hz

    constexpr ThreatClassifier() noexcept = default;

    void pushSample(const RfSample& sample) noexcept {
        m_history[m_head] = sample;
        m_head = (m_head + 1) % WindowSize;
        if (m_count < WindowSize) {
            ++m_count;
        }
    }

    [[nodiscard]] ThreatType evaluate(const std::optional<GnssFrame>& gnss = std::nullopt) noexcept {
        if (gnss.has_value() && isGnssSpoofed(*gnss)) {
            m_current_threat = ThreatType::GnssSpoofing;
            return m_current_threat;
        }

        if (m_count == 0) {
            m_current_threat = ThreatType::None;
            return m_current_threat;
        }

        const auto stats = computeRfStats();

        if (stats.avg_rssi >= kRssiBarrageThresholdDbm && stats.avg_agc <= 30 && stats.sync_hits == 0) {
            m_current_threat = ThreatType::BarrageBlocking;
        } else if (stats.avg_rssi >= kRssiJamThresholdDbm && stats.per >= kPerJamThresholdPct && stats.sync_hits <= 1) {
            m_current_threat = ThreatType::SpotJamming;
        } else if (stats.rssi_variance >= kRssiPulseVarianceMin && stats.per >= 40) {
            m_current_threat = ThreatType::PulseJamming;
        } else if (stats.avg_rssi <= -105 && stats.per >= kPerJamThresholdPct) {
            m_current_threat = ThreatType::WeakSignal;
        } else {
            m_current_threat = ThreatType::None;
        }

        return m_current_threat;
    }

    [[nodiscard]] ThreatType currentThreat() const noexcept {
        return m_current_threat;
    }

private:
    struct RfStats {
        int16_t  avg_rssi{0};
        uint8_t  avg_agc{0};
        uint8_t  per{0};
        uint8_t  sync_hits{0};
        uint32_t rssi_variance{0};
    };

    [[nodiscard]] RfStats computeRfStats() const noexcept {
        int32_t rssi_acc = 0;
        uint32_t agc_acc = 0;
        uint8_t crc_errors = 0;
        uint8_t sync_count = 0;

        for (std::size_t i = 0; i < m_count; ++i) {
            rssi_acc += m_history[i].rssi_dbm;
            agc_acc += m_history[i].agc_gain_code;
            if (m_history[i].crc_error) ++crc_errors;
            if (m_history[i].preamble_detected) ++sync_count;
        }

        const auto avg_rssi = static_cast<int16_t>(rssi_acc / static_cast<int32_t>(m_count));
        const auto avg_agc = static_cast<uint8_t>(agc_acc / m_count);
        const auto per = static_cast<uint8_t>((crc_errors * 100) / m_count);

        uint32_t var_acc = 0;
        for (std::size_t i = 0; i < m_count; ++i) {
            const int32_t diff = m_history[i].rssi_dbm - avg_rssi;
            var_acc += static_cast<uint32_t>(diff * diff);
        }

        return RfStats{
            .avg_rssi = avg_rssi,
            .avg_agc = avg_agc,
            .per = per,
            .sync_hits = sync_count,
            .rssi_variance = var_acc / m_count
        };
    }

    [[nodiscard]] static bool isGnssSpoofed(const GnssFrame& gnss) noexcept {
        if (gnss.satellites.size() < 4) return false;
        if (gnss.position_jump_without_imu || gnss.clock_jump_detected) return true;

        uint32_t cnr_sum = 0;
        std::size_t high_cnr_count = 0;

        for (const auto& sat : gnss.satellites) {
            cnr_sum += sat.cnr_x10;
            if (sat.cnr_x10 >= kGnssSpoofCnrThreshold) {
                ++high_cnr_count;
            }
        }

        const auto cnr_avg = static_cast<uint16_t>(cnr_sum / gnss.satellites.size());

        uint32_t dev_sum = 0;
        for (const auto& sat : gnss.satellites) {
            const auto diff = std::abs(static_cast<int32_t>(sat.cnr_x10) - static_cast<int32_t>(cnr_avg));
            dev_sum += static_cast<uint32_t>(diff);
        }
        const auto mean_dev = static_cast<uint16_t>(dev_sum / gnss.satellites.size());

        const auto high_pct = (high_cnr_count * 100) / gnss.satellites.size();
        return (high_pct >= 70 && mean_dev <= kGnssSpoofMaxDev);
    }

    std::array<RfSample, WindowSize> m_history{};
    std::size_t m_head{0};
    std::size_t m_count{0};
    ThreatType  m_current_threat{ThreatType::None};
};

} // namespace embedded::ew
```
:::

---

## 3. Інтеграція детектора в цикл обробки радіопакетів

Модуль класифікації викликається під час отримання чергового пакетного кадру або за спрацьовуванням таймера моніторингу радіоканалу (наприклад, кожні 100 мс).

:::tabs
```c
#include <stdio.h>

void on_radio_packet_received(ew_detector_t *det, int16_t rssi, int8_t snr, uint8_t agc, bool ok) {
    ew_rf_sample_t sample = {
        .rssi_dbm = rssi,
        .snr_db = snr,
        .agc_gain_code = agc,
        .preamble_detected = ok,
        .crc_error = !ok
    };

    ew_detector_push_rf(det, &sample);
    ew_threat_type_t threat = ew_detector_evaluate(det, NULL);

    switch (threat) {
        case EW_THREAT_SPOT_JAMMING:
            /* Негайно переходимо на резервний псевдовипадковий канал */
            // rf_fhss_force_channel_hop();
            break;
        case EW_THREAT_BARRAGE_BLOCKING:
            /* Вмикаємо атенюатор RF Front-End, щоб вивести LNA з насичення */
            // rf_frontend_set_attenuator(true);
            break;
        case EW_THREAT_PULSE_JAMMING:
            /* Збільшуємо надлишковість прямого виправлення помилок (FEC) */
            // rf_set_fec_rate(FEC_RATE_4_8);
            break;
        default:
            break;
    }
}
```
```cpp
#include <iostream>

void handleRadioTelemetry(embedded::ew::ThreatClassifier<16>& detector,
                          int16_t rssi, int8_t snr, uint8_t agc, bool packetOk) {
    detector.pushSample({
        .rssi_dbm = rssi,
        .snr_db = snr,
        .agc_gain_code = agc,
        .preamble_detected = packetOk,
        .crc_error = !packetOk
    });

    const auto threat = detector.evaluate();

    switch (threat) {
        case embedded::ew::ThreatType::SpotJamming:
            // rf_fhss_force_channel_hop();
            break;
        case embedded::ew::ThreatType::BarrageBlocking:
            // rf_frontend_set_attenuator(true);
            break;
        case embedded::ew::ThreatType::PulseJamming:
            // rf_set_fec_rate(FEC_RATE_4_8);
            break;
        default:
            break;
    }
}
```
:::

---

## 4. Зчитування телеметрії з апаратних трансиверів

Для наповнення структур `ew_rf_sample_t` драйвер радіотракту використовує специфічні регістри та команди конкретних мікросхем:

### Semtech SX1261 / SX1262 / SX1268
* **Миттєвий RSSI:** команда `GetRssiInst()` (код `0x15`) повертає байт `rssi_raw`, де `RSSI_дБм = -rssi_raw / 2`.
* **Пакетний статус:** команда `GetPacketStatus()` (код `0x14`) повертає `RssiPkt` та `SnrPkt` для останнього прийнятого кадру. Якщо пакет пошкоджено, прапорець `IRQ_CRC_ERR` у регістрі `GetIrqStatus()` сигналізує про помилку.
* **Стан AGC:** трансивер інформує про стан підсилення через внутрішній статус демодулятора, доступний у режимі безперервного прийому.

### Texas Instruments CC1312R / CC1352P
* Радіоядро Arm Cortex-M0 підтримує радіокоманди `CMD_PROP_RX` та `CMD_PROP_RX_ADV`.
* Структура звіту `rfc_propRxOutput_t` містить поля `lastRssi`, `nRxOk`, `nRxNok` (пакети з помилкою CRC), `nRxIgnored` (помилки преамбули/синхрослова).
* Регістри аналогового інтерфейсу `RFC_DBELL` надають доступ до поточного кроку підсилення LNA/VGA (поля `LNA_GAIN` та `VGA_GAIN`).

---

## 5. Крайові випадки та фільтрація хибних спрацьовувань

Практичне впровадження класифікатора вимагає врахування небезпечних крайових ситуацій, які можуть імітувати дію РЕБ:

1. **Затінення антени конструкцією апарата (Airframe Shadowing).** Під час різких маневрів (крену літака до 60° чи розвороту колісного шасі) карбоновий корпус або акумулятор перекривають пряму видимість на передавач. RSSI плавно просідає на 15–25 дБ, а PER тимчасово зростає. Відмінність від прицільного РЕБ полягає в тому, що при затіненні RSSI **падає разом із SNR**, тоді як при глушінні RSSI **зростає до максимуму при падінні SNR**.
2. **Електромагнітні завади від безколекторних двигунів (ESC/BLDC Noise).** ШІМ-комутація силіконових ключів регуляторів швидкості (ESC) випромінює широкосмугові імпульсні сплески на частотах 16–48 кГц із гармоніками до гігагерцового діапазону. Такі завади мають сувору кореляцію з рівнем газу (Throttle). Модуль детектора може блокувати вердикт `EW_THREAT_PULSE_JAMMING`, якщо сплески CRC синхронізовані зі стрибком струму двигунів.
3. **Холодний старт та заповнення вікна.** Поки буфер `rf_count < EW_WINDOW_SIZE`, класифікатор використовує пропорційне нормування знаменника або повертає `EW_THREAT_NONE`, запобігаючи хибному переходу в аварійний режим у перші мілісекунди після подачі живлення.
4. **Багатопроменеве поширення (Multipath Fading) у міській забудові.** Відбиття радіохвиль від залізобетонних будівель створює інтерференційні мінімуми (глибокі релеївські провали), де рівень RSSI коливається на 20–30 дБ за секунду під час руху. На відміну від імпульсного РЕБ, швидкість зміни сигналу при багатопроменевості обмежена максимальною швидкістю руху вузла (доплерівським розширенням смуги `f_d = v / λ`), тоді як імпульсна завада демонструє миттєвий стрибок між сусідніми семплами АЦП.
5. **Асинхронний поділ завдань в RTOS.** Обробка сирої телеметрії в прериванні (ISR) неприпустима через ризик блокування радіотракту. Драйвер трансивера передає структуру `ew_rf_sample_t` у неблокуючу чергу `xQueueSendFromISR()`, а класифікатор виконується у низькопріоритетному потоці телеметрії з періодичністю 50–100 мс. Повний цикл виконання функції `ew_detector_evaluate` на мікроконтролері з частотою 64 МГц займає менше 12 мікросекунд і потребує лише 180 байтів оперативної пам'яті (RAM).
