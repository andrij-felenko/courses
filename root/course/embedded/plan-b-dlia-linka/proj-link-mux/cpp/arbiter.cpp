#include "arbiter.hpp"

namespace linkmux {

std::string_view stateName(ArbiterState state) noexcept {
    switch (state) {
    case ArbiterState::PrimaryActive:      return "основний";
    case ArbiterState::FallbackActive:     return "резерв";
    case ArbiterState::RecoveryEvaluation: return "перевірка повернення";
    case ArbiterState::Blackout:           return "повний блекаут";
    }
    return "?";
}

std::string_view modeName(RadioMode mode) noexcept {
    switch (mode) {
    case RadioMode::Active: return "передача+прийом";
    case RadioMode::Listen: return "лише прийом";
    case RadioMode::Sleep:  return "сон";
    }
    return "?";
}

MultiLinkArbiter::MultiLinkArbiter(Transceiver& primary, Transceiver& fallback,
                                   Millis now) noexcept
    : bearers_{Bearer{primary, LinkQuality{primary.slot()}},
               Bearer{fallback, LinkQuality{fallback.slot()}}},
      stateSince_(now),
      sniffNext_(now) {
    setMode(bearers_[0], RadioMode::Active);
    setMode(bearers_[1], RadioMode::Listen);
    bearers_[0].quality.resume(now);
    bearers_[1].quality.resume(now);
    bearers_[0].freeAt = now;
    bearers_[1].freeAt = now;
}

void MultiLinkArbiter::setMode(Bearer& b, RadioMode mode) noexcept {
    if (b.mode == mode) {
        return;
    }
    b.mode = mode;
    b.radio.setMode(mode);
}

const LinkQuality& MultiLinkArbiter::quality(BearerId id) const noexcept {
    return bearer(id).quality;
}

std::string_view MultiLinkArbiter::bearerName(BearerId id) const noexcept {
    return bearer(id).radio.name();
}

std::uint32_t MultiLinkArbiter::txFrames(BearerId id) const noexcept {
    return bearer(id).txFrames;
}

std::uint32_t MultiLinkArbiter::txErrors(BearerId id) const noexcept {
    return bearer(id).txErrors;
}

void MultiLinkArbiter::enterState(ArbiterState next, Millis now) noexcept {
    if (state_ == next) {
        return;
    }
    state_      = next;
    stateSince_ = now;
    ++switches_;

    Bearer& prim = bearers_[0];
    Bearer& fall = bearers_[1];

    switch (next) {
    case ArbiterState::PrimaryActive:
        active_ = BearerId::Primary;
        setMode(prim, RadioMode::Active);
        setMode(fall, RadioMode::Listen);   // резерв слухає, але не гріє підсилювач
        fall.quality.resume(now);
        break;

    case ArbiterState::FallbackActive:
        active_ = BearerId::Fallback;
        setMode(fall, RadioMode::Active);
        // Заглушений основний тримати в ефірі — це 3..8 Вт батареї в нікуди.
        // Замість цього черговий прийом: 10 мс слухаємо раз на 500 мс.
        setMode(prim, RadioMode::Sleep);
        sniffNext_ = now + kSniffPeriod;
        sniffOpen_ = false;
        // На 10..50 кбіт/с відео не пролізе — черга йде геть одразу, а не
        // лежить, збільшуючи затримку всьому іншому.
        queues_.flush(Priority::Video);
        break;

    case ArbiterState::RecoveryEvaluation:
        // Слухаємо безперервно й міряємо з чистого аркуша: старе вікно повне
        // нулів завади й ніколи б не опустилося під поріг повернення.
        setMode(prim, RadioMode::Listen);
        sniffOpen_ = true;
        prim.quality.reset(now);
        break;

    case ArbiterState::Blackout:
        setMode(prim, RadioMode::Listen);
        setMode(fall, RadioMode::Listen);
        sniffOpen_ = true;
        prim.quality.resume(now);
        break;
    }
}

void MultiLinkArbiter::sniffTick(Millis now) noexcept {
    Bearer& prim = bearers_[0];
    if (!sniffOpen_) {
        if (now >= sniffNext_) {
            sniffOpen_ = true;
            prim.quality.resume(now);
            setMode(prim, RadioMode::Listen);
        }
    } else if (now >= sniffNext_ + kSniffWindow) {
        sniffOpen_  = false;
        sniffNext_ += kSniffPeriod;
        setMode(prim, RadioMode::Sleep);
    }
}

void MultiLinkArbiter::onFrameReceived(BearerId id, const Frame& frame, Millis now) noexcept {
    Bearer& b = bearer(id);
    if (b.mode == RadioMode::Sleep) {
        return;   // приймач спав — кадру бути не могло, це луна з кільця
    }
    b.quality.onFrame(frame.seq, frame.rssiDbm, frame.snrDb, now);
}

void MultiLinkArbiter::update(Millis now) noexcept {
    Bearer& prim = bearers_[0];
    Bearer& fall = bearers_[1];

    if (prim.mode != RadioMode::Sleep) { prim.quality.onTick(now); }
    if (fall.mode != RadioMode::Sleep) { fall.quality.onTick(now); }

    const bool primDead = prim.quality.silence(now) > kPrimarySilence
                       || prim.quality.per() >= kFailoverPer;
    const bool fallDead = fall.quality.silence(now) > kFallbackSilence;

    switch (state_) {
    case ArbiterState::PrimaryActive:
        if (primDead) {
            enterState(fallDead ? ArbiterState::Blackout : ArbiterState::FallbackActive, now);
        }
        break;

    case ArbiterState::FallbackActive:
        if (primDead && fallDead) {
            enterState(ArbiterState::Blackout, now);
        } else if (prim.quality.silence(now) <= kPrimarySilence) {
            // Кадр, спійманий у вікні чергового прийому, — привід почати перевірку
            enterState(ArbiterState::RecoveryEvaluation, now);
        } else {
            sniffTick(now);
        }
        break;

    case ArbiterState::RecoveryEvaluation:
        if (primDead) {
            // Зрив під час перевірки: назад у резерв, витримка починається заново
            enterState(ArbiterState::FallbackActive, now);
        } else if (now - stateSince_ >= kHysteresisDwell && prim.quality.per() <= kRecoveryPer) {
            enterState(ArbiterState::PrimaryActive, now);
        }
        break;

    case ArbiterState::Blackout:
        if (!fallDead) {
            enterState(ArbiterState::FallbackActive, now);
        } else if (!primDead) {
            enterState(ArbiterState::PrimaryActive, now);
        }
        break;
    }
}

std::expected<void, TxError> MultiLinkArbiter::routePacket(Priority prio,
                                                      std::span<const std::uint8_t> data,
                                                      Millis now) noexcept {
    if (data.size() > kMaxPayload) {
        return std::unexpected(TxError::PayloadTooLarge);
    }
    if (state_ == ArbiterState::Blackout) {
        // Ефіру немає взагалі. Тримати команди в черзі небезпечно: за секунди
        // вони застаріють. Верхній рівень має вмикати автономне повернення.
        return std::unexpected(TxError::Blackout);
    }
    if (prio == Priority::Video && active_ == BearerId::Fallback) {
        return std::unexpected(TxError::NoBandwidth);   // відкидаємо тут, а не в драйвері
    }

    const Frame frame = Frame::make(prio, data, txSeq_++,
                                    static_cast<std::uint32_t>(now.count()));
    if (!queues_.push(prio, frame)) {
        return std::unexpected(TxError::QueueFull);
    }
    return {};
}

void MultiLinkArbiter::duplicateCritical(const Frame& frame, Millis now) noexcept {
    Bearer& other = bearer(active_ == BearerId::Primary ? BearerId::Fallback : BearerId::Primary);
    if (other.mode == RadioMode::Sleep) {
        return;   // сплячий модуль не будимо заради копії
    }
    if (now < other.freeAt) {
        return;   // зайнятий передавач: копія не варта черги
    }
    if (const auto rc = other.radio.send(frame); !rc) {
        ++other.txErrors;
        return;
    }
    ++other.txFrames;
    other.freeAt = now + other.radio.airTime();
}

std::size_t MultiLinkArbiter::pump(Millis now) noexcept {
    if (state_ == ArbiterState::Blackout) {
        return 0;   // немає кому віддавати
    }

    std::size_t sent = 0;
    for (const Priority prio : kPriorityOrder) {
        while (const Frame* head = queues_.front(prio)) {
            Bearer& act = bearer(active_);
            if (now < act.freeAt) {
                return sent;   // передавач ще в ефірі: черга чекає, ми не крутимось
            }

            // Копію беремо до popFront: слот звільниться й може бути перезаписаний
            const bool duplicate = (prio == Priority::Critical
                                    && state_ == ArbiterState::RecoveryEvaluation);
            Frame copy;
            if (duplicate) {
                copy = *head;
            }

            if (const auto rc = act.radio.send(*head); !rc) {
                ++act.txErrors;
                return sent;   // залізо захлинулось — спробуємо наступного разу
            }
            ++act.txFrames;
            act.freeAt = now + act.radio.airTime();
            queues_.popFront(prio);
            ++sent;

            // Поки не впевнені в жодному носії, критичну команду шлемо обома
            if (duplicate) {
                duplicateCritical(copy, now);
            }
        }
    }
    return sent;
}

}  // namespace linkmux
