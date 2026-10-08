#include "stm32_timer_hal.hpp"

Stm32Timer::Stm32Timer(TIM_RegisterMap* timer_regs) noexcept
    : regs_(timer_regs) {
}

void Stm32Timer::initEncoderMode(uint8_t filter_icf) {
    if (!regs_) {
        return;
    }

    // 1. Зупиняємо таймер для безпечного переналаштування регістрів
    regs_->CR1 &= ~Stm32TimerRegs::CR1_CEN;

    // 2. Налаштування режиму підпорядкування (Slave Mode Control Register): Encoder Mode 3 (SMS = 011)
    // У цьому режимі лічильник зміщується за кожним фронтом і спадом сигналів на каналах CH1 та CH2 (x4)
    uint32_t smcr = regs_->SMCR;
    smcr &= ~0x0007U; // Очищення бітів SMS
    smcr |= Stm32TimerRegs::SMCR_SMS_ENC3;
    regs_->SMCR = smcr;

    // 3. Конфігурація вхідних каналів CH1 та CH2 у регістрі CCMR1
    // CC1S = 01 (вхід TI1), CC2S = 01 (вхід TI2)
    // Обмеження значення цифрового фільтра ICF діапазоном 0x0..0xF (4 біти)
    uint8_t icf = filter_icf & 0x0FU;
    uint32_t ccmr1 = regs_->CCMR1;
    ccmr1 &= ~(0x00FFU | 0xFF00U); // Очищення бітів конфігурації каналів 1 та 2
    ccmr1 |= Stm32TimerRegs::CCMR1_CC1S_TI1 | (icf << Stm32TimerRegs::CCMR1_IC1F_POS);
    ccmr1 |= Stm32TimerRegs::CCMR1_CC2S_TI2 | (icf << Stm32TimerRegs::CCMR1_IC2F_POS);
    regs_->CCMR1 = ccmr1;

    // 4. Налаштування полярності сигналів у CCER (пряма полярність без інверсії)
    regs_->CCER &= ~(Stm32TimerRegs::CCER_CC1P | Stm32TimerRegs::CCER_CC2P);

    // 5. Встановлення автоперезавантаження ARR у максимальне 16-бітне значення (65535)
    // Скидання дільника частоти PSC у 0 (пряма лічба вхідних імпульсів)
    regs_->PSC = 0;
    regs_->ARR = 0xFFFFU;
    regs_->CNT = 0;

    // 6. Запуск таймера
    regs_->CR1 |= Stm32TimerRegs::CR1_CEN;
}

uint16_t Stm32Timer::getCounter() const {
    return static_cast<uint16_t>(regs_ ? (regs_->CNT & 0xFFFFU) : 0);
}

void Stm32Timer::setCounter(uint16_t value) {
    if (regs_) {
        regs_->CNT = value;
    }
}

bool Stm32Timer::isCountingDown() const {
    if (!regs_) {
        return false;
    }
    // Біт DIR у CR1 вказує напрямок: 1 — лічба вниз (underflow), 0 — лічба вгору (overflow)
    return (regs_->CR1 & Stm32TimerRegs::CR1_DIR) != 0;
}

void Stm32Timer::enableUpdateInterrupt() {
    if (regs_) {
        regs_->DIER |= Stm32TimerRegs::DIER_UIE;
    }
}

void Stm32Timer::disableUpdateInterrupt() {
    if (regs_) {
        regs_->DIER &= ~Stm32TimerRegs::DIER_UIE;
    }
}

bool Stm32Timer::getAndClearUpdateFlag() {
    if (!regs_) {
        return false;
    }
    if ((regs_->SR & Stm32TimerRegs::SR_UIF) != 0) {
        regs_->SR &= ~Stm32TimerRegs::SR_UIF; // Очищення прапорця
        return true;
    }
    return false;
}

bool Stm32Timer::getUpdateFlag() const {
    if (!regs_) {
        return false;
    }
    return (regs_->SR & Stm32TimerRegs::SR_UIF) != 0;
}

void Stm32Timer::configureExtiZPin() {
    // Налаштування зовнішньої лінії EXTI для підключення індексної мітки Z
    exti_configured_ = true;
}
