// Мала машина станів, що виловлює один кадр UBX-TIM-TP з потоку байтів.
// Викликається на кожен прийнятий по UART байт (напр., із його ISR/черги).
#include <array>
#include <cstdint>

class UbxTimTpParser {
public:
    struct TimTp {
        std::uint32_t towMS;      // ціла частина часу тижня, мс
        std::uint32_t towSubMS;   // дробова частина, пс × 2⁻³²
        std::int32_t  qErr;       // помилка квантування, пс (знакова)
        std::uint16_t week;       // номер тижня
        std::uint8_t  flags;
        std::uint8_t  refInfo;
    };

    // Згодувати один байт; true — щойно зібрано валідний кадр (у msg()).
    bool feed(std::uint8_t b) {
        switch (st_) {
        case St::Sync1: if (b == kSync1) st_ = St::Sync2;          break;  // чекаємо 0xB5
        case St::Sync2: st_ = (b == kSync2) ? St::Cls : St::Sync1; break;  // потім 0x62
        case St::Cls:   cls_ = b; ckA_ = b; ckB_ = ckA_; st_ = St::Id;  break; // клас (старт CK)
        case St::Id:    id_ = b;  addCk(b); st_ = St::LenLo;            break; // номер
        case St::LenLo: len_ = b; addCk(b); st_ = St::LenHi;           break; // довжина LSB
        case St::LenHi:                                                        // довжина MSB
            len_ |= static_cast<std::uint16_t>(b) << 8; addCk(b);
            idx_ = 0;
            // Беремо лише TIM-TP потрібної довжини; решту кадрів пропускаємо.
            st_ = (cls_ == kCls && id_ == kId && len_ == kLen) ? St::Body : St::Sync1;
            break;
        case St::Body:  buf_[idx_++] = b; addCk(b);                    // тіло навантаження
            if (idx_ >= len_) st_ = St::CkA;
            break;
        case St::CkA:   st_ = (b == ckA_) ? St::CkB : St::Sync1;       break; // звірити CK_A
        case St::CkB:                                                          // звірити CK_B
            if (b == ckB_) {                                            // кадр цілий
                msg_ = TimTp{ rdU32(0), rdU32(4),
                              static_cast<std::int32_t>(rdU32(8)),      // знакова!
                              static_cast<std::uint16_t>(buf_[12] | (buf_[13] << 8)),
                              buf_[14], buf_[15] };
                ++count_;                                              // свіже повідомлення
                st_ = St::Sync1;
                return true;
            }
            st_ = St::Sync1;
            break;
        }
        return false;
    }

    const TimTp&  msg()   const { return msg_; }
    std::uint32_t count() const { return count_; }

private:
    static constexpr std::uint8_t  kSync1 = 0xB5, kSync2 = 0x62;
    static constexpr std::uint8_t  kCls = 0x0D, kId = 0x01;
    static constexpr std::uint16_t kLen = 16;

    enum class St { Sync1, Sync2, Cls, Id, LenLo, LenHi, Body, CkA, CkB };

    void addCk(std::uint8_t b) { ckA_ += b; ckB_ += ckA_; }

    std::uint32_t rdU32(std::size_t off) const {   // little-endian → uint32
        return  static_cast<std::uint32_t>(buf_[off])
             | (static_cast<std::uint32_t>(buf_[off + 1]) << 8)
             | (static_cast<std::uint32_t>(buf_[off + 2]) << 16)
             | (static_cast<std::uint32_t>(buf_[off + 3]) << 24);
    }

    St st_ = St::Sync1;
    std::uint8_t  cls_ = 0, id_ = 0, ckA_ = 0, ckB_ = 0;
    std::uint16_t len_ = 0, idx_ = 0;
    std::array<std::uint8_t, kLen> buf_{};
    TimTp msg_{};
    std::uint32_t count_ = 0;   // лічильник валідних кадрів (для головного циклу)
};
