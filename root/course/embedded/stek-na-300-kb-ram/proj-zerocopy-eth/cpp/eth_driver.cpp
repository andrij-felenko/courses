#include "eth_driver.hpp"

/// Сигнал «прийшов кадр» задачі прийому. Живе в netif_glue.cpp, бо семафор
/// належить прив'язці до lwIP, а не апаратурі.
extern "C" void ethernetif_notify_from_isr(void);

namespace net {
namespace {

/// Один буфер прийому. Перевіряємо рівно те, що ламає zero-copy на живому
/// залізі: пул порожній, пул віддав ланцюжок, payload не по межі кеш-лінії.
[[nodiscard]] std::expected<PbufRef, InitError> allocRxBuffer() noexcept
{
    PbufRef buf{pbuf_alloc(PBUF_RAW, kFrameBufSize, PBUF_POOL)};
    if (!buf) {
        return std::unexpected(InitError::PoolExhausted);
    }
    if (buf.get()->next != nullptr || buf.get()->len < kFrameBufSize) {
        return std::unexpected(InitError::ChainedBuffer);
    }
    if ((buf.address() & (kCacheLine - 1U)) != 0U) {
        // Інвалідація зачепила б чужі дані в тій самій лінії — паразитне
        // перезаписування, яке потім шукають тижнями.
        return std::unexpected(InitError::Misaligned);
    }
    return std::move(buf);
}

/// Скільки ланок ланцюжка справді треба покласти в дескриптори.
[[nodiscard]] std::expected<std::size_t, TxError> countSegments(const pbuf* frame) noexcept
{
    std::size_t need = 0;
    for (const pbuf* q = frame; q != nullptr; q = q->next) {
        if (q->len == 0) {
            continue;
        }
        if (q->len > tdes::sizeMask) {
            return std::unexpected(TxError::SegmentTooLong);
        }
        ++need;
    }
    if (need == 0) {
        return std::unexpected(TxError::EmptyFrame);
    }
    if (need > kTxDescCount) {
        return std::unexpected(TxError::TooManySegments);
    }
    return need;
}

}  // namespace

ZeroCopyMac& mac() noexcept
{
    static ZeroCopyMac instance;
    return instance;
}

std::expected<void, InitError> ZeroCopyMac::init() noexcept
{
    const std::uint32_t rxBase = rx_.link();
    const std::uint32_t txBase = tx_.link();

    for (std::size_t i = 0; i < kRxDescCount; ++i) {
        auto buf = allocRxBuffer();
        if (!buf) {
            // Гілка помилки нічого не «прибирає» руками: масив PbufRef
            // сам поверне в пул усе, що встиг забрати.
            for (auto& taken : rxBuffers_) {
                taken.reset();
            }
            return std::unexpected(buf.error());
        }

        Descriptor& d = rx_.at(i);
        d.buffer = buf->address();
        d.control = rdes::chained | (kFrameBufSize & rdes::sizeMask);
        if (i + 1 == kRxDescCount) {
            // У режимі ланцюжка апаратура йде за RDES3; біт лишаємо як явну
            // позначку кінця кільця для того, хто читатиме дамп.
            d.control |= rdes::endOfRing;
        }

        // Буфер віддаємо апаратурі: усе, що процесор про нього пам'ятає
        // в кеші, треба викинути, інакше стек прочитає стару копію.
        cache::invalidate(buf->payload().data(), kFrameBufSize);
        d.status = rdes::own;

        rxBuffers_[i] = std::move(*buf);
    }

    for (std::size_t i = 0; i < kTxDescCount; ++i) {
        Descriptor& d = tx_.at(i);
        d.buffer = 0;
        d.control = 0;
        d.status = tdes::chained | (i + 1 == kTxDescCount ? tdes::endOfRing : 0U);
    }

    // Дескриптори щойно писав процесор, а читати їх буде DMA повз кеш.
    rx_.flush();
    tx_.flush();
    rx_.rewind();
    tx_.rewind();

    ETH->DMARDLAR = rxBase;
    ETH->DMATDLAR = txBase;

    ETH->DMAIER |= ETH_DMAIER_NISE | ETH_DMAIER_RIE | ETH_DMAIER_TIE |
                   ETH_DMAIER_AISE | ETH_DMAIER_RBUIE;
    ETH->MACCR |= ETH_MACCR_TE | ETH_MACCR_RE;

    ETH->DMAOMR |= ETH_DMAOMR_FTF;  // скидання FIFO передачі, біт самоочисний
    for (std::uint32_t spin = 0; spin < 100'000U; ++spin) {
        if ((ETH->DMAOMR & ETH_DMAOMR_FTF) == 0U) {
            break;
        }
    }
    ETH->DMAOMR |= ETH_DMAOMR_ST | ETH_DMAOMR_SR;

    NVIC_SetPriority(ETH_IRQn, 5);  // нижче за поріг RTOS-безпечних переривань
    NVIC_EnableIRQ(ETH_IRQn);
    return {};
}

void ZeroCopyMac::returnToDma(Descriptor& d) noexcept
{
    d.status = rdes::own;
    cache::clean(&d, sizeof(Descriptor));
}

void ZeroCopyMac::resumeReceiver() noexcept
{
    // Поки кільце стояло порожнім, DMA міг заснути на Receive Buffer
    // Unavailable. Прапорець знімається записом одиниці, будить — DMARPDR.
    if ((ETH->DMASR & ETH_DMASR_RBUS) != 0U) {
        ETH->DMASR = ETH_DMASR_RBUS;
        ETH->DMARPDR = 0U;
    }
}

PbufRef ZeroCopyMac::receive() noexcept
{
    for (std::size_t scanned = 0; scanned < kRxDescCount; ++scanned) {
        Descriptor& d = rx_.at(rx_.index());

        // Статус писав DMA — власна копія в кеші тут завжди застаріла.
        cache::invalidate(&d, sizeof(Descriptor));
        if ((d.status & rdes::own) != 0U) {
            return {};  // дескриптор ще в роботі апаратури
        }

        const std::uint32_t status = d.status;
        const std::uint32_t frameLen = (status & rdes::frameLenMask) >> rdes::frameLenShift;
        const bool single = (status & (rdes::firstSeg | rdes::lastSeg)) ==
                            (rdes::firstSeg | rdes::lastSeg);
        const bool sane = single && (status & rdes::errorSummary) == 0U && frameLen > 4U &&
                          frameLen <= kFrameBufSize;

        PbufRef out;
        if (sane) {
            // Спершу дістаємо заміну — і лише якщо вона є, віддаємо кадр стеку.
            if (auto fresh = allocRxBuffer(); fresh.has_value()) {
                // FL рахує ще й 4 байти FCS, які стеку не потрібні.
                const auto len = static_cast<std::uint16_t>(frameLen - 4U);

                out = std::move(rxBuffers_[rx_.index()]);
                cache::invalidate(out.payload().data(), len);
                out.resize(len);

                d.buffer = fresh->address();
                cache::invalidate(fresh->payload().data(), kFrameBufSize);
                rxBuffers_[rx_.index()] = std::move(*fresh);
            }
            // Заміни немає — кадр гине, буфер лишається прив'язаним до
            // дескриптора. Апаратний ланцюжок цілий, приймач працює далі.
        }

        returnToDma(d);
        rx_.advance();
        resumeReceiver();

        if (out) {
            return out;
        }
        // Кадр відкинуто — дивимось наступний дескриптор, а не виходимо.
    }
    return {};
}

void ZeroCopyMac::reclaimSent() noexcept
{
    for (std::size_t i = 0; i < kTxDescCount; ++i) {
        if (!txFrames_[i]) {
            continue;
        }
        Descriptor& d = tx_.at(i);
        cache::invalidate(&d, sizeof(Descriptor));
        if ((d.status & tdes::own) != 0U) {
            continue;  // DMA ще читає цей буфер
        }
        // Контекст задачі, не переривання: тут pbuf має право повертатися
        // в пул і чіпати блокування стека.
        txFrames_[i].reset();
    }
}

std::expected<void, TxError> ZeroCopyMac::send(pbuf* frame) noexcept
{
    if (frame == nullptr || frame->tot_len == 0) {
        return std::unexpected(TxError::EmptyFrame);
    }

    reclaimSent();

    const auto need = countSegments(frame);
    if (!need) {
        return std::unexpected(need.error());
    }

    const std::size_t first = tx_.index();
    for (std::size_t k = 0; k < *need; ++k) {
        Descriptor& d = tx_.at(first + k);
        cache::invalidate(&d, sizeof(Descriptor));
        if ((d.status & tdes::own) != 0U) {
            return std::unexpected(TxError::RingFull);
        }
    }

    // Ланцюжок pbuf розкладаємо по дескрипторах один в один: зібрати ланки
    // в суцільний буфер означало б викинути весь zero-copy.
    std::size_t k = 0;
    for (pbuf* q = frame; q != nullptr; q = q->next) {
        if (q->len == 0) {
            continue;
        }
        Descriptor& d = tx_.at(first + k);

        // Пакет процесор щойно склав у своєму кеші — до старту DMA байти
        // мусять опинитися у фізичній SRAM.
        cache::clean(q->payload, q->len);

        d.buffer = reinterpret_cast<std::uint32_t>(q->payload);
        d.control = q->len & tdes::sizeMask;

        std::uint32_t st = tdes::chained;
        if ((first + k) % kTxDescCount == kTxDescCount - 1) {
            st |= tdes::endOfRing;
        }
        if (k == 0) {
            st |= tdes::firstSeg;
        }
        if (k + 1 == *need) {
            st |= tdes::lastSeg | tdes::interruptOnCompletion;
        }
        d.status = st;  // поки БЕЗ own
        ++k;
    }

    // Одне посилання на весь кадр, і висить воно на ОСТАННЬОМУ дескрипторі:
    // поки DMA не дійшов до кінця, звільняти ланцюжок не можна.
    txFrames_[(first + *need - 1) % kTxDescCount] = PbufRef::share(frame);

    // Володіння віддаємо задом наперед: якби перший дескриптор дістав own
    // раніше за останній, DMA почав би передавати недобудований кадр.
    for (std::size_t back = *need; back-- > 0;) {
        Descriptor& d = tx_.at(first + back);
        d.status |= tdes::own;
        cache::clean(&d, sizeof(Descriptor));
    }
    __DSB();

    tx_.advance(*need);

    if ((ETH->DMASR & ETH_DMASR_TBUS) != 0U) {
        ETH->DMASR = ETH_DMASR_TBUS;
    }
    ETH->DMATPDR = 0U;  // Transmit Poll Demand: «подивись у кільце ще раз»
    return {};
}

void ZeroCopyMac::serviceIrq() noexcept
{
    const std::uint32_t sr = ETH->DMASR;

    if ((sr & ETH_DMASR_RS) != 0U) {
        ETH->DMASR = ETH_DMASR_RS;
        // Тільки сигнал задачі. Ні виділення, ні звільнення pbuf тут не можна:
        // пул захищений блокуванням стека, а не забороною переривань.
        ethernetif_notify_from_isr();
    }

    if ((sr & ETH_DMASR_TS) != 0U) {
        ETH->DMASR = ETH_DMASR_TS;
        // Буфери передачі звільнить reclaimSent() у контексті задачі.
    }

    if ((sr & ETH_DMASR_RBUS) != 0U) {
        // Пул був порожній, приймач спинився: знімаємо прапорець, штовхаємо
        // DMA і будимо задачу — вона розгребе кільце.
        ETH->DMASR = ETH_DMASR_RBUS;
        ETH->DMARPDR = 0U;
        ethernetif_notify_from_isr();
    }

    ETH->DMASR = sr & (ETH_DMASR_NIS | ETH_DMASR_AIS);
}

}  // namespace net
