// rs485_port.cpp — автомат кадру й прив'язка обробників переривань.
//
// Поля стану не позначені volatile: усе, що читається з головного контексту,
// читається під IrqGuard, а всередині переривання конкуренції немає — обробники
// шини мають однаковий пріоритет і не витісняють один одного.
#include "rs485_port.hpp"

#include <algorithm>
#include <utility>

namespace rs485 {

// Визначення тут, а не в заголовку периферії: там RxFlags ще неповний тип.
RxFlags Stm32Usart::Status::errors() const noexcept {
    return RxFlags{
        .overrun = (isr_ & reg::kOre) != 0,
        .framing = (isr_ & reg::kFe) != 0,
        .noise = (isr_ & (reg::kNe | reg::kPe)) != 0,
    };
}

HalfDuplexPort::HalfDuplexPort(Stm32Usart& hw, std::uint32_t baud) noexcept
    : hw_{hw}, timing_{Timing::forBaud(baud)} {
    hw_.stopTimer();
    hw_.enableTcIrq(false);
    hw_.setDriverEnable(false);   // стан спокою — приймання
}

void HalfDuplexPort::arm(TimerJob job, std::chrono::microseconds delay) noexcept {
    timerJob_ = job;
    hw_.armTimer(delay);
}

void HalfDuplexPort::abortTx(BusError error) noexcept {
    hw_.abortTx();
    hw_.enableTcIrq(false);
    hw_.setDriverEnable(false);

    echoPending_ = false;
    lastError_ = error;
    state_ = State::Guard;
    arm(TimerJob::Turnaround, timing_.frameGap);
}

std::expected<void, BusError> HalfDuplexPort::send(std::span<const std::uint8_t> frame) noexcept {
    if (frame.empty() || frame.size() > kCapacity) {
        return std::unexpected(BusError::TooLong);
    }

    const IrqGuard guard;
    if (state_ != State::Idle) {
        // приймання, передавання або ще не витримана пауза розвороту
        return std::unexpected(BusError::Busy);
    }

    std::copy(frame.begin(), frame.end(), txBuffer_.begin());
    txLength_ = frame.size();
    echoIndex_ = 0;
    echoPending_ = true;
    state_ = State::Transmitting;

    hw_.stopTimer();
    timerJob_ = TimerJob::None;

    // DE вгору — і одразу DMA; вивід тримаємо піднятим до події TC
    hw_.setDriverEnable(true);
    hw_.startTx(std::span<const std::uint8_t>{txBuffer_.data(), txLength_});
    return {};
}

std::optional<HalfDuplexPort::Frame> HalfDuplexPort::receive() noexcept {
    const IrqGuard guard;
    if (!frameReady_) {
        return std::nullopt;
    }
    return Frame{this, std::span<const std::uint8_t>{rxBuffer_.data(), rxLength_}};
}

void HalfDuplexPort::releaseFrame() noexcept {
    const IrqGuard guard;
    frameReady_ = false;
    if (state_ != State::Receiving) {
        rxLength_ = 0;
    }
}

std::optional<BusError> HalfDuplexPort::takeError() noexcept {
    const IrqGuard guard;
    return std::exchange(lastError_, std::nullopt);
}

void HalfDuplexPort::finishFrame() noexcept {
    timerJob_ = TimerJob::None;
    state_ = State::Idle;

    if (rxDiscard_) {
        stats_.overruns++;
        lastError_ = BusError::Overrun;
        rxDiscard_ = false;
        return;
    }
    if (rxLength_ == 0) {
        return;
    }
    if (frameBad_) {
        frameBad_ = false;
        rxLength_ = 0;
        return;
    }

    frameReady_ = true;
    stats_.frames++;
}

bool HalfDuplexPort::consumeEcho(std::uint8_t byte) noexcept {
    if (!echoPending_) {
        return false;
    }

    if (echoIndex_ >= txLength_ || byte != txBuffer_[echoIndex_]) {
        // Хтось перебиває нашу одиницю нулем — це другий передавач на шині
        stats_.collisions++;
        if (state_ == State::Transmitting || state_ == State::Draining) {
            abortTx(BusError::Collision);
        } else {
            echoPending_ = false;
            lastError_ = BusError::Collision;
        }
        return true;
    }

    if (++echoIndex_ == txLength_) {
        echoPending_ = false;   // лінія підтвердила весь кадр
    }
    return true;
}

void HalfDuplexPort::onRxByte(std::uint8_t byte) noexcept {
    // Відлуння приходить і в Guard: останній байт добігає майже одночасно з TC
    if (state_ == State::Transmitting || state_ == State::Draining || state_ == State::Guard) {
        if (consumeEcho(byte)) {
            return;
        }
        if (state_ != State::Guard) {
            return;
        }
        // Guard і відлуння вичерпано — це вже відповідь сусіда
    }

    if (state_ != State::Receiving) {
        rxLength_ = 0;
        frameBad_ = false;
        rxDiscard_ = frameReady_;   // попередній кадр ще орендовано
        state_ = State::Receiving;
    } else if (timerJob_ == TimerJob::FrameGap) {
        // Байт після T1.5 — за Modbus такий кадр недійсний
        frameBad_ = true;
        stats_.gaps++;
        lastError_ = BusError::Gap;
    }

    if (!rxDiscard_) {
        if (rxLength_ < kCapacity) {
            rxBuffer_[rxLength_++] = byte;
        } else {
            frameBad_ = true;
            stats_.overruns++;
            lastError_ = BusError::Overrun;
        }
    }

    arm(TimerJob::InterChar, timing_.interChar);   // watchdog кадру наново з кожним байтом
}

void HalfDuplexPort::onRxError(RxFlags flags) noexcept {
    if (flags.overrun) {
        stats_.overruns++;
        lastError_ = BusError::Overrun;
    }
    if (flags.framing) {
        stats_.framings++;
        lastError_ = BusError::Framing;
    }
    if (flags.noise) {
        stats_.noises++;
        lastError_ = BusError::Noise;
    }

    hw_.clearRxErrors();

    if (state_ == State::Transmitting || state_ == State::Draining) {
        // Нуль на місці стоп-біта під час власної передачі — колізія
        stats_.collisions++;
        abortTx(BusError::Collision);
        return;
    }

    if (state_ == State::Receiving) {
        frameBad_ = true;
        arm(TimerJob::InterChar, timing_.interChar);
    }
}

void HalfDuplexPort::onDmaComplete() noexcept {
    if (state_ != State::Transmitting) {
        return;
    }
    // Останній байт лише переписано в TDR — DE не чіпаємо, чекаємо TC
    state_ = State::Draining;
    hw_.enableTcIrq(true);
}

void HalfDuplexPort::onTransmissionComplete() noexcept {
    hw_.enableTcIrq(false);
    if (state_ != State::Draining) {
        return;
    }

    hw_.setDriverEnable(false);   // стоп-біт уже в дроті
    state_ = State::Guard;
    arm(TimerJob::Turnaround, timing_.frameGap);
}

void HalfDuplexPort::onTimer() noexcept {
    switch (timerJob_) {
    case TimerJob::InterChar:
        if (state_ == State::Receiving) {
            arm(TimerJob::FrameGap, timing_.frameGap - timing_.interChar);
        } else {
            timerJob_ = TimerJob::None;
        }
        break;

    case TimerJob::FrameGap:
        finishFrame();
        break;

    case TimerJob::Turnaround:
        if (echoPending_) {
            // Лінія не повернула наших байтів: обрив, КЗ або мертвий трансивер
            echoPending_ = false;
            stats_.noEcho++;
            lastError_ = BusError::NoEcho;
        }
        timerJob_ = TimerJob::None;
        state_ = State::Idle;
        break;

    case TimerJob::None:
        break;
    }
}

namespace {
Stm32Usart g_usart;
}  // namespace

HalfDuplexPort& bus(std::uint32_t baud) noexcept {
    // Порядок ініціалізації локальних static гарантований: спершу периферія, потім автомат.
    static Stm32Usart& hw = [baud]() -> Stm32Usart& {
        g_usart.configure(baud, Stm32Usart::kHardwareDriverEnable);
        return g_usart;
    }();
    static HalfDuplexPort port{hw, baud};
    return port;
}

}  // namespace rs485

extern "C" void USART1_IRQHandler() {
    const auto status = rs485::Stm32Usart::status();

    if (status.hasError()) {
        rs485::bus().onRxError(status.errors());
        return;
    }
    if (status.rxReady()) {
        rs485::bus().onRxByte(rs485::Stm32Usart::readByte());
    }
    if (status.transmissionComplete()) {
        rs485::Stm32Usart::clearTransmissionComplete();
        rs485::bus().onTransmissionComplete();
    }
}

extern "C" void DMA1_Channel4_IRQHandler() {
    if (rs485::Stm32Usart::takeDmaComplete()) {
        rs485::bus().onDmaComplete();
    }
}

extern "C" void TIM7_DAC_IRQHandler() {
    if (rs485::Stm32Usart::takeTimerEvent()) {
        rs485::bus().onTimer();
    }
}
