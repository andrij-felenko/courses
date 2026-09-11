#include "Xpt8871Player.hpp"

Xpt8871Player::Xpt8871Player(HardwareCallbacks callbacks, Config config)
    : hw_(callbacks), config_(config) {
    // Початковий перевід підсилювача у стан сну (SHDN = LOW) для енергозбереження
    powerDown();
}

Xpt8871Player::~Xpt8871Player() {
    // RAII: під час виходу з області видимості апаратура безпечно вимикається
    stop();
}

bool Xpt8871Player::enqueue(std::span<const int16_t> samples, uint16_t id) {
    if (samples.empty() || queueCount_ >= QUEUE_CAPACITY) {
        return false;
    }

    // Розміщення сповіщення у статичній кільцевій черзі
    queue_[queueTail_] = SoundClip{id, samples, 0};
    queueTail_ = (queueTail_ + 1) % QUEUE_CAPACITY;
    ++queueCount_;

    // Реагування на додавання звуку залежно від поточного стану енергоспоживання
    if (state_ == State::Idle) {
        // Підсилювач спав — подаємо логічну 1 на SHDN і починаємо фазу стабілізації
        wakeUp();
    } else if (state_ == State::StandbyPending) {
        // Підсилювач ще увімкнений після попереднього звуку — граємо миттєво без затримки BYP
        startPlayback();
    } else if (state_ == State::Playing && !bufferHasAudio_[1 - activeDmaBuffer_]) {
        // Якщо інший буфер пари ping-pong був вільний, негайно наповнюємо його новим звуком
        const size_t inactive = 1 - activeDmaBuffer_;
        const size_t filled = fillBuffer(pingPongBuffers_[inactive]);
        bufferHasAudio_[inactive] = (filled > 0);
    }

    return true;
}

void Xpt8871Player::update() {
    const uint32_t now = (hw_.getMillis ? hw_.getMillis() : 0);

    switch (state_) {
    case State::Idle:
        // Підсилювач перебуває у сні, процесор не навантажується
        break;

    case State::PoweringUp:
        // Очікуємо заряду внутрішнього конденсатора на виводі BYP до VDD/2 (anti-pop таймінг)
        if (now - stateTimestamp_ >= config_.stabilizationDelayMs) {
            startPlayback();
        }
        break;

    case State::Playing:
        processPlayingState();
        break;

    case State::StandbyPending:
        // Якщо за час таймауту нових звуків не надійшло, переходимо у сон
        if (now - stateTimestamp_ >= config_.autoSleepDelayMs) {
            powerDown();
        }
        break;
    }
}

void Xpt8871Player::stop() {
    clearQueue();
    bufferHasAudio_[0] = false;
    bufferHasAudio_[1] = false;
    powerDown();
}

void Xpt8871Player::clearQueue() {
    queueHead_ = 0;
    queueTail_ = 0;
    queueCount_ = 0;
}

void Xpt8871Player::wakeUp() {
    if (hw_.setShutdownPin) {
        hw_.setShutdownPin(true); // Логічна 1 на вході SHDN активує XPT8871
    }
    state_ = State::PoweringUp;
    stateTimestamp_ = (hw_.getMillis ? hw_.getMillis() : 0);
}

void Xpt8871Player::powerDown() {
    bufferHasAudio_[0] = false;
    bufferHasAudio_[1] = false;
    if (hw_.setShutdownPin) {
        hw_.setShutdownPin(false); // Логічний 0 на вході SHDN переводить мікросхему в сон
    }
    state_ = State::Idle;
}

void Xpt8871Player::startPlayback() {
    // Первинне заповнення обох пінг-понг буферів перед стартом апаратного потоку
    const size_t s0 = fillBuffer(pingPongBuffers_[0]);
    const size_t s1 = fillBuffer(pingPongBuffers_[1]);

    bufferHasAudio_[0] = (s0 > 0);
    bufferHasAudio_[1] = (s1 > 0);

    if (bufferHasAudio_[0]) {
        activeDmaBuffer_ = 0;
        state_ = State::Playing;
        if (hw_.transmitDma) {
            hw_.transmitDma(pingPongBuffers_[0]);
        }
    } else {
        // Якщо черга спорожніла до початку відтворення
        state_ = State::StandbyPending;
        stateTimestamp_ = (hw_.getMillis ? hw_.getMillis() : 0);
    }
}

void Xpt8871Player::processPlayingState() {
    // Перевірка завершення поточної апаратної DMA-передачі
    const bool isBusy = (hw_.isDmaBusy ? hw_.isDmaBusy() : false);
    if (isBusy) {
        return; // Апаратна частина ще зайнята трансляцією поточного буфера
    }

    const size_t nextBuffer = 1 - activeDmaBuffer_;

    if (bufferHasAudio_[nextBuffer]) {
        // Миттєвий запуск передачі підготовленого другого буфера (відсутність чутних пауз)
        activeDmaBuffer_ = nextBuffer;
        if (hw_.transmitDma) {
            hw_.transmitDma(pingPongBuffers_[nextBuffer]);
        }

        // Поки апаратура транслює nextBuffer, процесор заповнює щойно звільнений буфер
        const size_t prevBuffer = 1 - nextBuffer;
        const size_t filled = fillBuffer(pingPongBuffers_[prevBuffer]);
        bufferHasAudio_[prevBuffer] = (filled > 0);
    } else {
        // Усі аудіодані відтворено, переходимо в режим очікування автозасинання
        state_ = State::StandbyPending;
        stateTimestamp_ = (hw_.getMillis ? hw_.getMillis() : 0);
    }
}

size_t Xpt8871Player::fillBuffer(std::span<int16_t> dest) {
    size_t samplesFilled = 0;
    const size_t destSize = dest.size();

    while (samplesFilled < destSize && queueCount_ > 0) {
        SoundClip& currentClip = queue_[queueHead_];
        const size_t remainingInClip = currentClip.samples.size() - currentClip.playbackOffset;
        const size_t toCopy = std::min(destSize - samplesFilled, remainingInClip);

        const bool isClipStart = (currentClip.playbackOffset == 0);
        const size_t startOffsetInDest = samplesFilled;

        // Копіювання аудіовибірок у вихідний буфер
        for (size_t i = 0; i < toCopy; ++i) {
            dest[samplesFilled + i] = currentClip.samples[currentClip.playbackOffset + i];
        }

        if (isClipStart) {
            // Плавне програмне наростання гучності для усунення клацання на початку сигналу
            applySoftFade(dest.subspan(startOffsetInDest, toCopy), toCopy, true);
        }

        currentClip.playbackOffset += toCopy;
        samplesFilled += toCopy;

        // Якщо поточний звуковий фрагмент завершився
        if (currentClip.playbackOffset >= currentClip.samples.size()) {
            // Плавне програмне згасання гучності перед закінченням вибірок
            const size_t fadeWindow = std::min(samplesFilled - startOffsetInDest, FADE_SAMPLES);
            applySoftFade(dest.subspan(samplesFilled - fadeWindow, fadeWindow), fadeWindow, false);

            // Вилучення сповіщення з черги
            queueHead_ = (queueHead_ + 1) % QUEUE_CAPACITY;
            --queueCount_;
        }
    }

    // Заповнення залишку буфера тишею (нулями), якщо звук скінчився раніше кінця буфера
    if (samplesFilled < destSize) {
        std::fill(dest.begin() + samplesFilled, dest.end(), static_cast<int16_t>(0));
    }

    return samplesFilled;
}

void Xpt8871Player::applySoftFade(std::span<int16_t> buffer, size_t count, bool fadeIn) {
    if (count == 0 || buffer.empty()) {
        return;
    }

    const size_t len = std::min({count, buffer.size(), FADE_SAMPLES});
    if (len == 0) {
        return;
    }

    // Лінійне масштабування цілочисельних вибірок без операцій із плаваючою комою
    for (size_t i = 0; i < len; ++i) {
        const int32_t factor = fadeIn ? static_cast<int32_t>(i)
                                      : static_cast<int32_t>(len - 1 - i);
        const size_t idx = fadeIn ? i : (buffer.size() - len + i);
        buffer[idx] = static_cast<int16_t>((static_cast<int32_t>(buffer[idx]) * factor) / static_cast<int32_t>(len));
    }
}
