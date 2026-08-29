#include <algorithm>

#include "modbus_slave.hpp"

namespace node {

void ModbusSlave::begin(std::uint32_t kernelClkHz) noexcept {
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;

    // Ядро USART тактуємо від HSI16: тоді приймач живий і в Stop 2, і перший
    // же старт-біт від ведучого будить мікроконтролер.
    RCC->CCIPR = (RCC->CCIPR & ~RCC_CCIPR_USART1SEL) | (2u << RCC_CCIPR_USART1SEL_Pos);
    RCC->CR |= RCC_CR_HSION | RCC_CR_HSIASFS;
    while ((RCC->CR & RCC_CR_HSIRDY) == 0u) { }

    const mcu::Pin tx{GPIOA, 9};
    const mcu::Pin rx{GPIOA, 10};
    tx.alternate(7);   // AF7 = USART1
    rx.alternate(7);

    de_.mode(mcu::Pin::Mode::Output);
    de_.write(false);   // спокійний стан — прослуховування лінії

    USART1->CR1 = 0;
    USART1->BRR = kernelClkHz / kBaud;

    // t3.5 між символами: 3.5 × 11 бітів ≈ 39 бітових інтервалів. Детектор
    // Receiver Timeout відміряє їх апаратно — саме ця пауза й означає
    // «кадр скінчився», програмному таймеру тут не встигнути.
    USART1->RTOR = 39u;
    USART1->CR2 = USART_CR2_RTOEN;
    USART1->CR3 = USART_CR3_WUFIE | (3u << USART_CR3_WUS_Pos);   // прокидання по RXNE
    USART1->CR1 = USART_CR1_UE | USART_CR1_UESM | USART_CR1_TE | USART_CR1_RE |
                  USART_CR1_RXNEIE | USART_CR1_RTOIE;

    NVIC_SetPriority(USART1_IRQn, 2u);
    NVIC_EnableIRQ(USART1_IRQn);
}

void ModbusSlave::handleIrq() noexcept {
    const std::uint32_t isr = USART1->ISR;

    if (isr & USART_ISR_WUF) {
        USART1->ICR = USART_ICR_WUCF;   // прокинулися від старт-біта
    }

    if (isr & (USART_ISR_ORE | USART_ISR_FE | USART_ISR_NE)) {
        USART1->ICR = USART_ICR_ORECF | USART_ICR_FECF | USART_ICR_NCF;
        ++overruns_;
        rxLen_ = 0;   // кадр однаково битий
    }

    if (isr & USART_ISR_RXNE) {
        const auto byte = static_cast<std::byte>(USART1->RDR);

        if (!frameReady_ && rxLen_ < kRxSize) {
            rx_[rxLen_++] = byte;
        } else if (rxLen_ >= kRxSize) {
            rxLen_ = 0;   // довший за наш буфер — точно не наш
        }
    }

    if (isr & USART_ISR_RTOF) {
        USART1->ICR = USART_ICR_RTOCF;

        if (rxLen_ > 0 && !frameReady_) {
            std::copy_n(rx_.begin(), rxLen_, frame_.begin());
            frameLen_ = rxLen_;
            frameReady_ = true;
            events_.push(Event::Rs485Frame);
        }
        rxLen_ = 0;
    }

    // Передавання: байти віддаємо по TXE, лінію DE знімаємо тільки по TC.
    if ((USART1->CR1 & USART_CR1_TXEIE) && (isr & USART_ISR_TXE)) {
        if (txPos_ < txLen_) {
            USART1->TDR = static_cast<std::uint32_t>(tx_[txPos_++]);
        } else {
            USART1->CR1 &= ~USART_CR1_TXEIE;
            USART1->ICR = USART_ICR_TCCF;
            USART1->CR1 |= USART_CR1_TCIE;
        }
    }

    if ((USART1->CR1 & USART_CR1_TCIE) && (isr & USART_ISR_TC)) {
        USART1->ICR = USART_ICR_TCCF;
        USART1->CR1 &= ~USART_CR1_TCIE;
        // TXE каже лише «регістр звільнився». Зняти DE там, де він
        // з'являється, означає обрізати останній байт просто в лінії —
        // тому DE живе рівно до TC, і жодна RAII-обгортка області
        // видимості цього не зробить: передавання переживає виклик.
        de_.write(false);
        txBusy_ = false;
        events_.push(Event::Rs485Sent);
    }
}

void ModbusSlave::send(std::span<const std::byte> frame) noexcept {
    if (frame.empty() || frame.size() > kTxSize || txBusy_) return;

    std::copy(frame.begin(), frame.end(), tx_.begin());
    txLen_ = frame.size();
    txPos_ = 0;
    txBusy_ = true;

    de_.write(true);
    // Трансиверу потрібні одиниці мікросекунд на перехід у передавання;
    // без цієї паузи перший біт піде в лінію, якої ще ніхто не тримає.
    mcu::time::delayUs(2);

    USART1->ICR = USART_ICR_TCCF;
    USART1->CR1 |= USART_CR1_TXEIE;
}

void ModbusSlave::service(const Record& last) noexcept {
    if (!frameReady_) return;

    std::array<std::byte, kRxSize> request{};
    std::size_t length = 0;
    {
        const mcu::ScopedIrqLock lock;
        length = frameLen_;
        std::copy_n(frame_.begin(), length, request.begin());
        frameReady_ = false;
    }

    if (length < 4) return;                                  // коротше за адресу+код+CRC
    if (static_cast<std::uint8_t>(request[0]) != kNodeId) return;   // кадр не наш — мовчимо

    const std::span<const std::byte> body{request.data(), length - 2};
    const auto received = static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(request[length - 2]) |
        (static_cast<std::uint16_t>(request[length - 1]) << 8));

    if (crc16(body) != received) return;   // биту суму лишаємо без відповіді

    lastPollMs_ = mcu::time::millis();
    masterSeen_ = true;

    std::array<std::byte, kTxSize> response{};
    std::size_t n = 0;
    const auto function = static_cast<std::uint8_t>(request[1]);

    if (function == kFuncReadHolding) {
        response[n++] = std::byte{kNodeId};
        response[n++] = std::byte{kFuncReadHolding};
        response[n++] = static_cast<std::byte>(kRecordSize);

        const RecordBytes payload = toBytes(last);
        std::copy(payload.begin(), payload.end(), response.begin() + n);
        n += kRecordSize;
    } else {
        // Виняткова відповідь: ведучий має знати, що вузол живий, але такої
        // функції не має. Мовчання він прочитав би як обрив лінії.
        response[n++] = std::byte{kNodeId};
        response[n++] = static_cast<std::byte>(function | 0x80u);
        response[n++] = std::byte{kExcIllegalFunction};
    }

    const std::uint16_t crc = crc16(std::span<const std::byte>{response.data(), n});
    response[n++] = static_cast<std::byte>(crc & 0xFFu);
    response[n++] = static_cast<std::byte>(crc >> 8);

    send(std::span<const std::byte>{response.data(), n});
}

}  // namespace node
