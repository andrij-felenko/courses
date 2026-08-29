#include "receiver.hpp"

#include <utility>

#include "crc16.hpp"

namespace radio {

void BitReceiver::toHunt()
{
    state_ = State::Hunt;
    armed_ = false;
    altRun_ = 0;
    bitCount_ = 0;
    acc_ = 0;
    crcPos_ = 0;
    body_.clear();
}

void BitReceiver::flush()
{
    fifo_.clear();
    overrun_ = false;
    toHunt();
}

void BitReceiver::pushBit(bool bit)
{
    if (state_ == State::Hunt) {
        // Детектор преамбули: рахуємо довжину серії чергувань 0/1. Поки серії
        // не було, корелятор вимкнено — інакше тепловий шум сам ловив би
        // синхрослово кілька разів на секунду.
        altRun_ = (bit != lastBit_) ? altRun_ + 1 : 1;
        lastBit_ = bit;

        if (!armed_ && altRun_ >= kPreambleDetectBits) {
            armed_ = true;
            searchLeft_ = kSyncSearchBits;
            ++stats_.arms;
        }

        shift_ = (shift_ << 1) | static_cast<std::uint32_t>(bit ? 1u : 0u);

        if (!armed_) {
            return;
        }

        if ((shift_ & kSyncMask) == kSyncWord) {
            // Строб байтового вирівнювання: наступний біт стає старшим бітом
            // першого байта тіла. Саме тут із потоку бітів народжуються байти.
            ++stats_.syncs;
            state_ = State::Length;
            bitCount_ = 0;
            acc_ = 0;
            crcPos_ = 0;
            body_.clear();
            whitener_.reset();
            crc_ = kCrcInit;
            return;
        }

        if (--searchLeft_ == 0) {
            // Вікно вийшло: то була не преамбула, а щось на неї схоже.
            armed_ = false;
            altRun_ = 0;
        }
        return;
    }

    // Усередині кадру просто збираємо байти, старший біт першим.
    acc_ = static_cast<std::uint8_t>((acc_ << 1) | (bit ? 1u : 0u));
    if (++bitCount_ == 8) {
        const std::uint8_t raw = acc_;
        acc_ = 0;
        bitCount_ = 0;
        onByte(raw);
    }
}

void BitReceiver::pushByteMsbFirst(std::uint8_t byte)
{
    for (int bit = 7; bit >= 0; --bit) {
        pushBit(((byte >> bit) & 1u) != 0);
    }
}

void BitReceiver::onByte(std::uint8_t raw)
{
    // Тіло кадру скрембльоване, і той самий LFSR знімає з нього маску.
    const std::uint8_t byte = whitener_(raw);

    switch (state_) {
    case State::Length:
        if (byte == 0 || byte > kMaxPayload) {
            // Найчастіша причина — фантомний сync у шумі: візерунок «знайшовся»,
            // а кадру за ним немає.
            ++stats_.lengthErrors;
            toHunt();
            return;
        }
        need_ = byte;
        crc_ = crcUpdate(crc_, byte);
        body_.reserve(need_);
        state_ = State::Data;
        return;

    case State::Data:
        body_.push_back(byte);
        crc_ = crcUpdate(crc_, byte);
        if (body_.size() == need_) {
            state_ = State::Crc;
        }
        return;

    case State::Crc: {
        crcRx_[crcPos_++] = byte;
        if (crcPos_ < crcRx_.size()) {
            return;
        }
        const auto received = static_cast<std::uint16_t>(
            (static_cast<std::uint16_t>(crcRx_[0]) << 8) | crcRx_[1]);

        if (received == crc_) {
            ++stats_.frames;
            deliver();
        } else {
            // Апаратний блок тут просто не піднімає RX_DONE і скидає покажчик
            // FIFO — пошкоджений кадр зникає мовчки.
            ++stats_.crcErrors;
        }
        toHunt();
        return;
    }

    case State::Hunt:
    default:
        toHunt();
        return;
    }
}

void BitReceiver::deliver()
{
    if (fifo_.size() >= kFifoDepth) {
        // Хост не встиг вичитати попередній кадр по SPI. Реальний трансивер
        // тут піднімає ознаку переповнення й стоїть до CMD_FLUSHRX.
        overrun_ = true;
        ++stats_.overruns;
        return;
    }
    fifo_.push_back(std::move(body_));
}

std::optional<std::vector<std::uint8_t>> BitReceiver::pop()
{
    if (fifo_.empty()) {
        return std::nullopt;
    }
    auto packet = std::move(fifo_.front());
    fifo_.pop_front();
    return packet;
}

} // namespace radio
