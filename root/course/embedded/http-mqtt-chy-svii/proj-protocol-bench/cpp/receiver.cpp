// Валідація вхідного кадру на приймачі (C++23).
#include "receiver.hpp"

#include "bytes.hpp"

namespace telem {

std::expected<Receiver::Frame, DecodeError> Receiver::accept(std::span<const std::uint8_t> raw) noexcept
{
    // 1. Довжина. Датаграма буває довшою за кадр (доповнення канального
    // рівня), коротшою — ні: тоді читати нема чого.
    if (raw.size() < kFrameSize) {
        ++stats_.too_short;
        return std::unexpected(DecodeError::TooShort);
    }
    const auto frame_bytes = raw.first(kFrameSize);

    // 2. Синхробайт: найдешевша перевірка йде першою й відсіює більшість
    // сміття, що прилітає в ефірі, за одне порівняння.
    if (frame_bytes[0] != kMagic) {
        ++stats_.bad_magic;
        return std::unexpected(DecodeError::BadMagic);
    }

    ByteReader r{frame_bytes};
    const auto magic     = r.u8();
    const auto type      = r.u8();
    const auto seq       = r.u16le();
    const auto timestamp = r.u32le();
    const auto temp      = r.i16le();
    const auto humidity  = r.u16le();
    const auto vbat      = r.u16le();
    const auto crc       = r.u16le();
    static_cast<void>(magic);

    if (type != kTypeTelemetry) {
        ++stats_.bad_type;
        return std::unexpected(DecodeError::BadType);
    }

    // 3. CRC по тих самих 14 байтах, які рахував відправник.
    if (crc != crc16Ccitt(frame_bytes.first(kFrameCrcLen))) {
        ++stats_.bad_crc;
        return std::unexpected(DecodeError::BadCrc);
    }

    // 4. Номер послідовності. Наївне "seq <= last" ламається на переповненні
    // шістнадцяти бітів: після 65535 лічильник іде на 0, і сервер відкинув би
    // геть усе подальше. Тому дивимось на РІЗНИЦЮ у знаковій арифметиці:
    // додатна в межах піввікна (32767 кадрів) — новий кадр, недодатна —
    // дублікат або повтор старого запису.
    if (last_seq_.has_value()) {
        const auto delta = static_cast<std::int16_t>(seq - *last_seq_);
        if (delta <= 0) {
            ++stats_.replay;
            return std::unexpected(DecodeError::Replay);
        }
    }

    last_seq_ = seq;
    ++stats_.accepted;

    return Frame{
        .sample = Sample{
            .timestamp_s  = timestamp,
            .temp_centi_c = temp,
            .humidity_pct = humidity,
            .vbat_mv      = vbat,
        },
        .seq = seq,
    };
}

}  // namespace telem
