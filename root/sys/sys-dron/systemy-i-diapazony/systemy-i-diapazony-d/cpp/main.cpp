#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <vector>
#include <optional>
#include <concepts>

namespace gnss::ubx {

inline constexpr uint8_t Sync1 = 0xB5;
inline constexpr uint8_t Sync2 = 0x62;

enum class MessageClass : uint8_t {
    Nav = 0x01,
    Cfg = 0x06
};

enum class MessageId : uint8_t {
    NavPvt   = 0x07,
    CfgValSet = 0x8A
};

enum class Layer : uint8_t {
    Ram   = 0x01,
    Bbr   = 0x02,
    Flash = 0x04
};

enum class DynamicModel : uint8_t {
    Portable    = 0,
    Stationary  = 2,
    Pedestrian  = 3,
    Automotive  = 4,
    Airborne1g  = 6,
    Airborne2g  = 7,
    Airborne4g  = 8
};

enum class FixType : uint8_t {
    NoFix        = 0,
    DeadReckon   = 1,
    Fix2D        = 2,
    Fix3D        = 3,
    GnssPlusDr   = 4,
    TimeOnly     = 5
};

/* Ключі конфігурації Generation 9/10 */
namespace cfg_key {
    inline constexpr uint32_t SignalGpsEna     = 0x1031001F;
    inline constexpr uint32_t SignalGpsL5Ena   = 0x10310022;
    inline constexpr uint32_t SignalGalEna     = 0x10310021;
    inline constexpr uint32_t SignalGalE5aEna  = 0x10310027;
    inline constexpr uint32_t SignalBdsEna     = 0x10310024;
    inline constexpr uint32_t SignalBdsB2aEna  = 0x10310029;
    inline constexpr uint32_t SignalGloEna     = 0x10310023;
    inline constexpr uint32_t NavSpgDynModel   = 0x20110021;
    inline constexpr uint32_t RateMeas         = 0x30210001;
    inline constexpr uint32_t RateNav          = 0x30210002;
}

#pragma pack(push, 1)
struct NavPvtPayload {
    uint32_t iTOW;          // GPS Time of Week (мс)
    uint16_t year;          // Рік (UTC)
    uint8_t  month;         // Місяць (1..12)
    uint8_t  day;           // День (1..31)
    uint8_t  hour;          // Година (0..23)
    uint8_t  min;           // Хвилина (0..59)
    uint8_t  sec;           // Секунда (0..60)
    uint8_t  valid;         // Прапорці валідності часу
    uint32_t tAcc;          // Точність часу (нс)
    int32_t  nano;          // Дробова частина секунди (нс)
    FixType  fixType;       // Тип навігаційного фіксу
    uint8_t  flags;         // Прапорці статусу фіксу
    uint8_t  flags2;        // Додаткові прапорці
    uint8_t  numSV;         // Кількість супутників у навігаційному розв'язку
    int32_t  lon;           // Довгота (масштаб 1e-7 градуса)
    int32_t  lat;           // Широта (масштаб 1e-7 градуса)
    int32_t  height;        // Висота над еліпсоїдом WGS-84 (мм)
    int32_t  hMSL;          // Висота над середнім рівнем моря (мм)
    uint32_t hAcc;          // Горизонтальна оцінка точності (мм)
    uint32_t vAcc;          // Вертикальна оцінка точності (мм)
    int32_t  velN;          // Швидкість на північ NED (мм/с)
    int32_t  velE;          // Швидкість на схід NED (мм/с)
    int32_t  velD;          // Вертикальна швидкість униз NED (мм/с)
    int32_t  gSpeed;        // Горизонтальна швидкість (мм/с)
    int32_t  headMot;       // Курс руху (масштаб 1e-5 градуса)
    uint32_t sAcc;          // Точність оцінки швидкості (мм/с)
    uint32_t headAcc;       // Точність оцінки курсу (1e-5 градуса)
    uint16_t pDOP;          // Position DOP (масштаб 0.01)
    uint8_t  flags3;        // Прапорці диференційного/RTK розв'язку
    uint8_t  reserved1[5];
    int32_t  headVeh;       // Курс орієнтації корпусу
    int16_t  magDec;        // Магнітне схилення
    uint16_t magAcc;        // Точність магнітного схилення

    [[nodiscard]] bool is3dFixed() const noexcept {
        return fixType == FixType::Fix3D || fixType == FixType::GnssPlusDr;
    }

    [[nodiscard]] bool isCarrierPhaseFixed() const noexcept {
        // Біти 6..7 у полі flags: 1 = Float RTK, 2 = Fixed RTK
        return ((flags >> 6) & 0x03) == 2;
    }
};
#pragma pack(pop)

struct Checksum {
    uint8_t a{0};
    uint8_t b{0};

    constexpr void update(uint8_t byte) noexcept {
        a = static_cast<uint8_t>(a + byte);
        b = static_cast<uint8_t>(b + a);
    }

    constexpr void update(std::span<const uint8_t> data) noexcept {
        for (uint8_t byte : data) {
            update(byte);
        }
    }
};

class FrameBuilder {
public:
    static std::vector<uint8_t> createMultiBandConfig(DynamicModel dyn = DynamicModel::Airborne4g,
                                                      uint16_t rateMeasMs = 100) {
        std::vector<uint8_t> payload;
        payload.reserve(64);

        // Version та цільові шари (RAM + BBR)
        payload.push_back(0x00);
        payload.push_back(static_cast<uint8_t>(Layer::Ram) | static_cast<uint8_t>(Layer::Bbr));
        payload.push_back(0x00);
        payload.push_back(0x00);

        auto addKeyU8 = [&payload](uint32_t key, uint8_t val) {
            const auto* kPtr = reinterpret_cast<const uint8_t*>(&key);
            payload.insert(payload.end(), kPtr, kPtr + 4);
            payload.push_back(val);
        };

        auto addKeyU16 = [&payload](uint32_t key, uint16_t val) {
            const auto* kPtr = reinterpret_cast<const uint8_t*>(&key);
            payload.insert(payload.end(), kPtr, kPtr + 4);
            const auto* vPtr = reinterpret_cast<const uint8_t*>(&val);
            payload.insert(payload.end(), vPtr, vPtr + 2);
        };

        // Активація констеляцій та частотних діапазонів L1 + L5
        addKeyU8(cfg_key::SignalGpsEna, 1);
        addKeyU8(cfg_key::SignalGpsL5Ena, 1);
        addKeyU8(cfg_key::SignalGalEna, 1);
        addKeyU8(cfg_key::SignalGalE5aEna, 1);
        addKeyU8(cfg_key::SignalBdsEna, 1);
        addKeyU8(cfg_key::SignalBdsB2aEna, 1);
        addKeyU8(cfg_key::SignalGloEna, 1);

        // Налаштування польотної динаміки та темпу вимірювань
        addKeyU8(cfg_key::NavSpgDynModel, static_cast<uint8_t>(dyn));
        addKeyU16(cfg_key::RateMeas, rateMeasMs);
        addKeyU16(cfg_key::RateNav, 1);

        return packMessage(MessageClass::Cfg, MessageId::CfgValSet, payload);
    }

private:
    static std::vector<uint8_t> packMessage(MessageClass cls, MessageId id,
                                            std::span<const uint8_t> payload) {
        std::vector<uint8_t> frame;
        frame.reserve(6 + payload.size() + 2);

        frame.push_back(Sync1);
        frame.push_back(Sync2);
        frame.push_back(static_cast<uint8_t>(cls));
        frame.push_back(static_cast<uint8_t>(id));

        const auto len = static_cast<uint16_t>(payload.size());
        frame.push_back(static_cast<uint8_t>(len & 0xFF));
        frame.push_back(static_cast<uint8_t>((len >> 8) & 0xFF));

        frame.insert(frame.end(), payload.begin(), payload.end());

        Checksum ck;
        ck.update(std::span<const uint8_t>{frame.data() + 2, frame.size() - 2});

        frame.push_back(ck.a);
        frame.push_back(ck.b);

        return frame;
    }
};

} // namespace gnss::ubx
