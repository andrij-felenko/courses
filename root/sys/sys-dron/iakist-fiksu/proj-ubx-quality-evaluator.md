# ⚙️ Реалізація аналізатора якості навігаційних повідомлень UBX

Цей програмний модуль реалізує повноцінний потоковий парсер бінарного протоколу u-blox UBX для навігаційного повідомлення `UBX-NAV-PVT` (клас `0x01`, ідентифікатор `0x07`) та блок багаторівневого оцінювання метрик якості супутникового фіксу на мовах C та C++. Без прямого розбору бінарних кадрів польотний контролер безпілотника не може автономно валідувати геометрію сузір'я (PDOP/HDOP), рівень сигналу, статус фазового розв'язку RTK та коваріації точності перед увімкненням автономних режимів навігації.

---

### 1. Анатомія та поля бінарного кадру UBX-NAV-PVT

Повідомлення `UBX-NAV-PVT` є основним навігаційним кадром сучасних супутникових модулів u-blox (зокрема сімейств NEO-M8N, NEO-M9N, ZED-F9P). Модуль транслює цей кадр із періодичністю від 1 до 25 Гц через інтерфейс UART, SPI або I2C. На відміну від текстових повідомлень стандарту NMEA-0183, бінарний формат передає дані в прямому машинному представленні (little-endian) з фіксованим вирівнюванням, що усуває ресурсомістке форматування рядків та забезпечує повну точність вимірів швидкості, часу та просторових коваріацій.

Загальна структура транспортного кадру UBX складається з шести послідовних полів:
1. **Двобайтний заголовок синхронізації:** байти `0xB5 0x62` (символи `µb`). Вони слугують маркером початку пакета в неперервному потоці байтів послідовного порту.
2. **Клас повідомлення (`msgClass`):** 1 байт. Для навігаційних повідомлень використовується клас `0x01` (`NAV`).
3. **Ідентифікатор повідомлення (`msgID`):** 1 байт. Для кадру PVT (Position, Velocity, Time) задано значення `0x07`.
4. **Довжина корисного навантаження (`length`):** 2 байти (little-endian uint16). Для повної версії `UBX-NAV-PVT` довжина становить рівно `92` байти.
5. **Корисне навантаження (`payload`):** 92 байти бінарних навігаційних параметрів.
6. **Контрольна сума Флетчера (Fletcher-8):** 2 байти (`CK_A`, `CK_B`), що обчислюються над усіма байтами пакета, починаючи від `msgClass` і завершуючи останнім байтом `payload`.

#### Ключові бітові поля та прапорці корисного навантаження:
- `iTOW` (uint32, байти 0..3): час тижня GPS у мілісекундах (Time of Week), що використовується для точної часової прив'язки вимірів до шкали бортового таймера польотного контролера.
- `fixType` (uint8, байт 20): тип навігаційного фіксу (`0` — No Fix, `1` — Dead Reckoning, `2` — 2D Fix, `3` — 3D Fix, `4` — GNSS + Dead Reckoning, `5` — Time Only).
- `flags` (uint8, байт 21): бітова маска прапорців стану розв'язку:
  - Біт 0 (`gnssFixOK`): супутниковий розв'язок дійсний та відповідає внутрішнім критеріям збіжності приймача;
  - Біт 1 (`diffSoln`): застосовано диференційні кодові поправки DGPS або SBAS;
  - Біти 6..7 (`carrSoln`): статус фазового розв'язку несучої хвилі (`0` — без RTK, `1` — RTK Float із дійсними неоднозначностями, `2` — RTK Fixed із фіксованими цілими фазовими неоднозначностями).
- `numSV` (uint8, байт 23): загальна кількість супутників усіх активованих систем (GPS, Galileo, GLONASS, BeiDou), що були використані в навігаційному розв'язку поточної епохи.
- `hAcc` та `vAcc` (uint32, байти 40..47): розраховані приймачем оцінки радіуса кола 1σ-похибки у горизонтальній площині та інтервалу 1σ-похибки за висотою в міліметрах.
- `pDOP` (uint16, байти 76..77): значення просторового геометричного фактора, помножене на фіксований коефіцієнт `100` (значення `150` відповідає `PDOP = 1.50`).

---

### 2. Алгоритм контрольної суми Флетчера та стійкість до завад

Для захисту від спотворень даних у лініях передачі UART протокол UBX використовує 8-бітний модифікований алгоритм контрольної суми Флетчера (Fletcher-8, RFC 1145). На відміну від простого порозрядного додавання за модулем 2 (XOR-контрольної суми в NMEA), алгоритм Флетчера формує два накопичувальні байти `CK_A` та `CK_B`, які залежать не лише від значень байтів, а й від їхнього точного порядку в кадрі:

```
CK_A = 0,  CK_B = 0
Для кожного байта D[k] від msgClass до кінця payload:
    CK_A = (CK_A + D[k]) mod 256
    CK_B = (CK_B + CK_A) mod 256
```

Якщо під час передачі в послідовному каналі виникає зсув байтів або перестановка двох сусідніх байтів місцями, сума XOR не виявить помилки, тоді як акумулятор `CK_B` гарантовано змінить своє значення, запобігаючи попаданню пошкодженого кадру в навігаційний фільтр EKF.

---

### 3. Реалізація скінченного автомата розбору та блоку оцінювання

Потоковий парсер реалізовано у вигляді детермінованого скінченного автомата (англ. *Finite State Machine*, FSM). Автомат обробляє потік побайтово без потреби динамічного виділення пам'яті (zero-allocation), що критично для детермінізму задач реального часу в операційних системах FreeRTOS чи NuttX.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UBX_SYNC1 0xB5
#define UBX_SYNC2 0x62
#define UBX_CLASS_NAV 0x01
#define UBX_ID_NAV_PVT 0x07
#define UBX_NAV_PVT_PAYLOAD_LEN 92

typedef enum {
    UBX_STATE_SYNC1 = 0,
    UBX_STATE_SYNC2,
    UBX_STATE_CLASS,
    UBX_STATE_ID,
    UBX_STATE_LEN1,
    UBX_STATE_LEN2,
    UBX_STATE_PAYLOAD,
    UBX_STATE_CK_A,
    UBX_STATE_CK_B
} ubx_parser_state_t;

typedef enum {
    GNSS_QUALITY_REJECTED = 0,
    GNSS_QUALITY_POOR,
    GNSS_QUALITY_ACCEPTABLE,
    GNSS_QUALITY_EXCELLENT
} gnss_quality_level_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t iTOW;          // Час тижня GPS (мс)
    uint16_t year;          // Рік (UTC)
    uint8_t  month;         // Місяць (1..12)
    uint8_t  day;           // День (1..31)
    uint8_t  hour;          // Година (0..23)
    uint8_t  min;           // Хвилина (0..59)
    uint8_t  sec;           // Секунда (0..60)
    uint8_t  valid;         // Прапорці валідності часу
    uint32_t tAcc;          // Точність часу (нс)
    int32_t  nano;          // Дріб секунди (нс)
    uint8_t  fixType;       // Тип фіксу: 0=NoFix, 2=2D, 3=3D, 4=DGPS, 5=TimeOnly
    uint8_t  flags;         // Прапорці фіксу (gnssFixOK, diffSoln, carrSoln)
    uint8_t  flags2;        // Додаткові прапорці
    uint8_t  numSV;         // Кількість супутників, використаних у розв'язку
    int32_t  lon;           // Довгота (1e-7 град)
    int32_t  lat;           // Широта (1e-7 град)
    int32_t  height;        // Висота над еліпсоїдом WGS84 (мм)
    int32_t  hMSL;          // Висота над середнім рівнем моря MSL (мм)
    uint32_t hAcc;          // Оцінка горизонтальної точності (мм)
    uint32_t vAcc;          // Оцінка вертикальної точності (мм)
    int32_t  velN;          // Швидкість на Північ (мм/с)
    int32_t  velE;          // Швидкість на Схід (мм/с)
    int32_t  velD;          // Швидкість Вниз (мм/с)
    int32_t  gSpeed;        // Горизонтальна швидкість (мм/с)
    int32_t  headMot;       // Курс руху (1e-5 град)
    uint32_t sAcc;          // Точність швидкості (мм/с)
    uint32_t headAcc;       // Точність курсу (1e-5 град)
    uint16_t pDOP;          // Просторовій DOP (масштаб 0.01)
    uint16_t flags3;        // Прапорці валідності розв'язку
    uint8_t  reserved1[4];
    int32_t  headVeh;       // Курс корпусу (для 2-антенних систем)
    int16_t  magDec;        // Магнітне схилення
    uint16_t magAcc;        // Точність магнітного схилення
} ubx_nav_pvt_payload_t;
#pragma pack(pop)

typedef struct {
    ubx_parser_state_t state;
    uint8_t msg_class;
    uint8_t msg_id;
    uint16_t payload_len;
    uint16_t payload_idx;
    uint8_t ck_a;
    uint8_t ck_b;
    uint8_t calc_ck_a;
    uint8_t calc_ck_b;
    uint8_t payload_buf[UBX_NAV_PVT_PAYLOAD_LEN];
} ubx_parser_ctx_t;

typedef struct {
    gnss_quality_level_t quality;
    bool is_valid_3d_fix;
    bool is_rtk_fixed;
    float pdop;
    float h_acc_meters;
    float v_acc_meters;
    uint8_t satellites_used;
    bool arming_allowed;
} gnss_eval_report_t;

void ubx_parser_init(ubx_parser_ctx_t *ctx) {
    memset(ctx, 0, sizeof(ubx_parser_ctx_t));
    ctx->state = UBX_STATE_SYNC1;
}

static void ubx_update_checksum(ubx_parser_ctx_t *ctx, uint8_t byte) {
    ctx->calc_ck_a += byte;
    ctx->calc_ck_b += ctx->calc_ck_a;
}

bool ubx_parser_feed_byte(ubx_parser_ctx_t *ctx, uint8_t byte, ubx_nav_pvt_payload_t *out_pvt) {
    switch (ctx->state) {
    case UBX_STATE_SYNC1:
        if (byte == UBX_SYNC1) {
            ctx->state = UBX_STATE_SYNC2;
        }
        break;
    case UBX_STATE_SYNC2:
        if (byte == UBX_SYNC2) {
            ctx->state = UBX_STATE_CLASS;
            ctx->calc_ck_a = 0;
            ctx->calc_ck_b = 0;
        } else {
            ctx->state = (byte == UBX_SYNC1) ? UBX_STATE_SYNC2 : UBX_STATE_SYNC1;
        }
        break;
    case UBX_STATE_CLASS:
        ctx->msg_class = byte;
        ubx_update_checksum(ctx, byte);
        ctx->state = UBX_STATE_ID;
        break;
    case UBX_STATE_ID:
        ctx->msg_id = byte;
        ubx_update_checksum(ctx, byte);
        ctx->state = UBX_STATE_LEN1;
        break;
    case UBX_STATE_LEN1:
        ctx->payload_len = byte;
        ubx_update_checksum(ctx, byte);
        ctx->state = UBX_STATE_LEN2;
        break;
    case UBX_STATE_LEN2:
        ctx->payload_len |= ((uint16_t)byte << 8);
        ubx_update_checksum(ctx, byte);
        ctx->payload_idx = 0;
        if (ctx->payload_len == UBX_NAV_PVT_PAYLOAD_LEN &&
            ctx->msg_class == UBX_CLASS_NAV &&
            ctx->msg_id == UBX_ID_NAV_PVT) {
            ctx->state = UBX_STATE_PAYLOAD;
        } else {
            ctx->state = UBX_STATE_SYNC1;
        }
        break;
    case UBX_STATE_PAYLOAD:
        ctx->payload_buf[ctx->payload_idx++] = byte;
        ubx_update_checksum(ctx, byte);
        if (ctx->payload_idx >= ctx->payload_len) {
            ctx->state = UBX_STATE_CK_A;
        }
        break;
    case UBX_STATE_CK_A:
        ctx->ck_a = byte;
        ctx->state = UBX_STATE_CK_B;
        break;
    case UBX_STATE_CK_B:
        ctx->ck_b = byte;
        ctx->state = UBX_STATE_SYNC1;
        if (ctx->ck_a == ctx->calc_ck_a && ctx->ck_b == ctx->calc_ck_b) {
            memcpy(out_pvt, ctx->payload_buf, sizeof(ubx_nav_pvt_payload_t));
            return true;
        }
        break;
    }
    return false;
}

gnss_eval_report_t gnss_evaluate_pvt_quality(const ubx_nav_pvt_payload_t *pvt) {
    gnss_eval_report_t rep;
    memset(&rep, 0, sizeof(rep));

    rep.satellites_used = pvt->numSV;
    rep.pdop = (float)pvt->pDOP * 0.01f;
    rep.h_acc_meters = (float)pvt->hAcc * 0.001f;
    rep.v_acc_meters = (float)pvt->vAcc * 0.001f;

    bool gnss_fix_ok = (pvt->flags & 0x01) != 0;
    uint8_t carr_soln = (pvt->flags >> 6) & 0x03; // 0=None, 1=Float, 2=Fixed

    rep.is_valid_3d_fix = gnss_fix_ok && (pvt->fixType >= 3);
    rep.is_rtk_fixed = (carr_soln == 2);

    if (!rep.is_valid_3d_fix || rep.satellites_used < 6 || rep.pdop > 5.0f || rep.h_acc_meters > 5.0f) {
        rep.quality = GNSS_QUALITY_REJECTED;
        rep.arming_allowed = false;
    } else if (rep.pdop > 2.5f || rep.h_acc_meters > 2.5f || rep.satellites_used < 8) {
        rep.quality = GNSS_QUALITY_POOR;
        rep.arming_allowed = false;
    } else if (rep.pdop > 1.8f || rep.h_acc_meters > 1.2f) {
        rep.quality = GNSS_QUALITY_ACCEPTABLE;
        rep.arming_allowed = true;
    } else {
        rep.quality = GNSS_QUALITY_EXCELLENT;
        rep.arming_allowed = true;
    }

    return rep;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

namespace drone::gnss {

constexpr uint8_t UBX_SYNC1 = 0xB5;
constexpr uint8_t UBX_SYNC2 = 0x62;
constexpr uint8_t UBX_CLASS_NAV = 0x01;
constexpr uint8_t UBX_ID_NAV_PVT = 0x07;
constexpr size_t UBX_NAV_PVT_PAYLOAD_LEN = 92;

enum class FixType : uint8_t {
    NoFix = 0,
    DeadReckoningOnly = 1,
    Fix2D = 2,
    Fix3D = 3,
    GNSSPlusDeadReckoning = 4,
    TimeOnly = 5
};

enum class CarrierSolution : uint8_t {
    None = 0,
    Float = 1,
    Fixed = 2
};

enum class QualityLevel {
    Rejected = 0,
    Poor,
    Acceptable,
    Excellent
};

#pragma pack(push, 1)
struct UbxNavPvtPayload {
    uint32_t iTOW;          // Час тижня GPS (мс)
    uint16_t year;          // Рік
    uint8_t  month;         // Місяць
    uint8_t  day;           // День
    uint8_t  hour;          // Година
    uint8_t  min;           // Хвилина
    uint8_t  sec;           // Секунда
    uint8_t  valid;         // Валідність
    uint32_t tAcc;          // Точність часу (нс)
    int32_t  nano;          // Дріб секунди (нс)
    FixType  fixType;       // Тип фіксу
    uint8_t  flags;         // Прапорці (gnssFixOK, diffSoln)
    uint8_t  flags2;        // Додаткові прапорці
    uint8_t  numSV;         // Кількість супутників
    int32_t  lon;           // Довгота (1e-7 deg)
    int32_t  lat;           // Широта (1e-7 deg)
    int32_t  height;        // Висота WGS84 (мм)
    int32_t  hMSL;          // Висота MSL (мм)
    uint32_t hAcc;          // Горизонтальна точність (мм)
    uint32_t vAcc;          // Вертикальна точність (мм)
    int32_t  velN;          // Швидкість Північ (мм/с)
    int32_t  velE;          // Швидкість Схід (мм/с)
    int32_t  velD;          // Швидкість Вниз (мм/с)
    int32_t  gSpeed;        // Швидкість горизонт (мм/с)
    int32_t  headMot;       // Курс руху (1e-5 deg)
    uint32_t sAcc;          // Точність швидкості (мм/с)
    uint32_t headAcc;       // Точність курсу (1e-5 deg)
    uint16_t pDOP;          // Просторовій DOP (0.01)
    uint16_t flags3;        // Прапорці валідності
    uint8_t  reserved1[4];
    int32_t  headVeh;       // Курс корпусу
    int16_t  magDec;        // Магнітне схилення
    uint16_t magAcc;        // Точність магнітного схилення

    [[nodiscard]] constexpr bool isFixOk() const noexcept {
        return (flags & 0x01) != 0;
    }

    [[nodiscard]] constexpr CarrierSolution carrierSolution() const noexcept {
        return static_cast<CarrierSolution>((flags >> 6) & 0x03);
    }

    [[nodiscard]] constexpr float pdopFloat() const noexcept {
        return static_cast<float>(pDOP) * 0.01f;
    }

    [[nodiscard]] constexpr float hAccMeters() const noexcept {
        return static_cast<float>(hAcc) * 0.001f;
    }

    [[nodiscard]] constexpr float vAccMeters() const noexcept {
        return static_cast<float>(vAcc) * 0.001f;
    }
};
#pragma pack(pop)

struct QualityReport {
    QualityLevel quality{QualityLevel::Rejected};
    bool is_valid_3d_fix{false};
    bool is_rtk_fixed{false};
    float pdop{99.99f};
    float h_acc_meters{999.0f};
    float v_acc_meters{999.0f};
    uint8_t satellites_used{0};
    bool arming_allowed{false};
};

class UbxParser {
public:
    constexpr UbxParser() noexcept = default;

    std::optional<UbxNavPvtPayload> feed(uint8_t byte) noexcept {
        switch (m_state) {
        case State::Sync1:
            if (byte == UBX_SYNC1) m_state = State::Sync2;
            break;
        case State::Sync2:
            if (byte == UBX_SYNC2) {
                m_state = State::Class;
                m_calcCkA = 0;
                m_calcCkB = 0;
            } else {
                m_state = (byte == UBX_SYNC1) ? State::Sync2 : State::Sync1;
            }
            break;
        case State::Class:
            m_msgClass = byte;
            updateChecksum(byte);
            m_state = State::Id;
            break;
        case State::Id:
            m_msgId = byte;
            updateChecksum(byte);
            m_state = State::Len1;
            break;
        case State::Len1:
            m_payloadLen = byte;
            updateChecksum(byte);
            m_state = State::Len2;
            break;
        case State::Len2:
            m_payloadLen |= (static_cast<uint16_t>(byte) << 8);
            updateChecksum(byte);
            m_payloadIdx = 0;
            if (m_payloadLen == UBX_NAV_PVT_PAYLOAD_LEN &&
                m_msgClass == UBX_CLASS_NAV &&
                m_msgId == UBX_ID_NAV_PVT) {
                m_state = State::Payload;
            } else {
                m_state = State::Sync1;
            }
            break;
        case State::Payload:
            m_payloadBuf[m_payloadIdx++] = byte;
            updateChecksum(byte);
            if (m_payloadIdx >= m_payloadLen) {
                m_state = State::CkA;
            }
            break;
        case State::CkA:
            m_ckA = byte;
            m_state = State::CkB;
            break;
        case State::CkB:
            m_ckB = byte;
            m_state = State::Sync1;
            if (m_ckA == m_calcCkA && m_ckB == m_calcCkB) {
                UbxNavPvtPayload pvt{};
                std::memcpy(&pvt, m_payloadBuf.data(), sizeof(UbxNavPvtPayload));
                return pvt;
            }
            break;
        }
        return std::nullopt;
    }

private:
    enum class State {
        Sync1, Sync2, Class, Id, Len1, Len2, Payload, CkA, CkB
    };

    void updateChecksum(uint8_t byte) noexcept {
        m_calcCkA += byte;
        m_calcCkB += m_calcCkA;
    }

    State m_state{State::Sync1};
    uint8_t m_msgClass{0};
    uint8_t m_msgId{0};
    uint16_t m_payloadLen{0};
    uint16_t m_payloadIdx{0};
    uint8_t m_ckA{0};
    uint8_t m_ckB{0};
    uint8_t m_calcCkA{0};
    uint8_t m_calcCkB{0};
    std::array<uint8_t, UBX_NAV_PVT_PAYLOAD_LEN> m_payloadBuf{};
};

[[nodiscard]] inline QualityReport evaluateQuality(const UbxNavPvtPayload& pvt) noexcept {
    QualityReport rep;
    rep.satellites_used = pvt.numSV;
    rep.pdop = pvt.pdopFloat();
    rep.h_acc_meters = pvt.hAccMeters();
    rep.v_acc_meters = pvt.vAccMeters();

    rep.is_valid_3d_fix = pvt.isFixOk() && (static_cast<uint8_t>(pvt.fixType) >= 3);
    rep.is_rtk_fixed = (pvt.carrierSolution() == CarrierSolution::Fixed);

    if (!rep.is_valid_3d_fix || rep.satellites_used < 6 || rep.pdop > 5.0f || rep.h_acc_meters > 5.0f) {
        rep.quality = QualityLevel::Rejected;
        rep.arming_allowed = false;
    } else if (rep.pdop > 2.5f || rep.h_acc_meters > 2.5f || rep.satellites_used < 8) {
        rep.quality = QualityLevel::Poor;
        rep.arming_allowed = false;
    } else if (rep.pdop > 1.8f || rep.h_acc_meters > 1.2f) {
        rep.quality = QualityLevel::Acceptable;
        rep.arming_allowed = true;
    } else {
        rep.quality = QualityLevel::Excellent;
        rep.arming_allowed = true;
    }

    return rep;
}

} // namespace drone::gnss
```
:::

---

### 4. Практичне застосування в драйверах польотного стека

Наведений модуль інтегрується в драйвер супутникового приймача польотного контролера (наприклад, у компонент `src/drivers/gps/devices/src/ubx.cpp` операційної системи PX4 або модуль `AP_GPS_UBLOX` у стеку ArduPilot).

Він виконує три життєво важливі функції під час польоту безпілотного апарата:

1. **Захист від псевдофіксів (False Fix Rejection):**
   У складних умовах міської забудови модуль GNSS може видати статус `fixType = 3`, спостерігаючи лише 4 супутники з поганою геометрією (`PDOP = 6.5`) та наявністю відбитих променів. Оцінювач якості негайно виявляє невідповідність за порогами `hAcc > 2.5 м` та `pdop > 2.5` і блокує перемикання автопілота в режим автоматичного зльоту (`arming_allowed = false`).

2. **Динамічна адаптація коваріацій у фільтрі EKF2:**
   Значення оцінок точності `hAcc` та `vAcc` транслюються в матрицю дисперсій шуму вимірів `R_gnss` розширеного фільтра Калмана. Якщо дрон потрапляє в зону затінення і `hAcc` зростає з 0.8 м до 3.5 м, EKF2 автоматично зменшує вагові коефіцієнти супутникових вимірів і більше покладається на інтегрування даних акселерометрів та гіроскопів IMU.

3. **Моніторинг деградації RTK-зв'язку:**
   При роботі з базовою станцією відстежується перехід прапорця `carrSoln` зі стану `Fixed` (2) у стан `Float` (1). Це сигналізує про втрату наскрізного фазового супроводу супутників, що дозволяє польотному контролеру попередити оператора або тимчасово призупинити виконання високоточної місії картографування.
