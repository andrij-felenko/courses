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
