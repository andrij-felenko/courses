#include "ring_logger.hpp"

#include <algorithm>
#include <array>

namespace fl {
namespace {

constexpr std::uint32_t recordSize(std::size_t payload) noexcept
{
    return static_cast<std::uint32_t>(kRecordHeaderSize + payload + kCrcSize);
}

}  // namespace

std::uint32_t RingLogger::sectorAddress(std::uint32_t idx) const noexcept
{
    return baseAddress_ + idx * static_cast<std::uint32_t>(kSectorSize);
}

std::uint32_t RingLogger::nextLive(std::uint32_t from) const noexcept
{
    for (std::uint32_t step = 1; step <= kSectorCount; ++step) {
        const std::uint32_t idx = (from + step) % kSectorCount;
        if (!bad_.test(idx)) {
            return idx;
        }
    }
    return from;
}

std::expected<SectorHeader, LoggerError> RingLogger::readHeader(std::uint32_t idx)
{
    SectorHeaderBytes raw{};
    if (!device_.read(sectorAddress(idx), raw)) {
        return std::unexpected(LoggerError::Hal);
    }
    return SectorHeader::decode(raw);
}

// Читання назад і побайтове звіряння: «команду відіслано» ще не означає
// «дані в комірках», а SPI-лінія б'є біти частіше, ніж хочеться вірити.
std::expected<void, LoggerError> RingLogger::verify(std::uint32_t address,
                                                    std::span<const std::byte> expected)
{
    std::array<std::byte, 64> chunk{};
    std::size_t done = 0;

    while (done < expected.size()) {
        const std::size_t n = std::min(chunk.size(), expected.size() - done);
        const std::span<std::byte> window{chunk.data(), n};

        if (!device_.read(address + static_cast<std::uint32_t>(done), window)) {
            return std::unexpected(LoggerError::Hal);
        }
        if (!std::ranges::equal(window, expected.subspan(done, n))) {
            return std::unexpected(LoggerError::Hal);
        }
        done += n;
    }
    return {};
}

// Перехід стану гасить біти на місці — стирати сектор для цього не треба.
std::expected<void, LoggerError> RingLogger::writeState(std::uint32_t idx, SectorState state)
{
    std::array<std::byte, 4> raw{};
    putU32(raw, static_cast<std::uint32_t>(state));

    const std::uint32_t address = sectorAddress(idx) + static_cast<std::uint32_t>(kSectorStateOffset);
    if (!device_.write(address, raw)) {
        return std::unexpected(LoggerError::Hal);
    }
    return verify(address, raw);
}

void RingLogger::markBad(std::uint32_t idx)
{
    bad_.set(idx);
    pendingBad_ = idx;

    // Спроба лишити слід у самому секторі; вона цілком може не вдатися —
    // саме тому маска дефектів живе в RAM. Сектор, який не тримає даних,
    // не втримає й мітки про власну несправність.
    static_cast<void>(writeState(idx, SectorState::Dirty));
}

std::expected<void, LoggerError> RingLogger::openSector(std::uint32_t idx, std::uint32_t eraseCount,
                                                        std::uint32_t seq)
{
    if (!device_.eraseSector(sectorAddress(idx))) {
        return std::unexpected(LoggerError::Hal);
    }

    const SectorHeader header{
        .magic = kSectorMagic,
        .version = kFormatVersion,
        .seqNum = seq,
        .eraseCount = eraseCount,
        .state = SectorState::Active,
    };
    const SectorHeaderBytes raw = header.encode();

    if (!device_.write(sectorAddress(idx), raw)) {
        return std::unexpected(LoggerError::Hal);
    }
    return verify(sectorAddress(idx), raw);
}

// Спершу Full на старому, потім стирання нового: знеструмлення посередині
// лишає щонайбільше один активний сектор, а не два.
std::expected<void, LoggerError> RingLogger::rotate()
{
    if (!bad_.test(active_)) {
        static_cast<void>(writeState(active_, SectorState::Full));
    }

    std::uint32_t idx = active_;
    for (std::uint32_t attempt = 0; attempt < kSectorCount; ++attempt) {
        idx = (idx + 1) % kSectorCount;
        if (bad_.test(idx)) {
            continue;
        }

        std::uint32_t eraseCount = 0;
        if (const auto header = readHeader(idx); header && header->magic == kSectorMagic) {
            eraseCount = header->eraseCount;
        }

        if (!openSector(idx, eraseCount + 1, seqNum_ + 1)) {
            markBad(idx);
            continue;
        }

        ++seqNum_;
        active_ = idx;
        offset_ = static_cast<std::uint32_t>(kSectorHeaderSize);

        // Голова наздогнала хвіст: щойно стертий сектор і був найстарішим
        // невивантаженим. Хвіст виштовхуємо вперед — свіжі дані важливіші
        // за старі, і система не спиняється.
        if (tail_ == idx) {
            tail_ = nextLive(idx);
        }
        return {};
    }

    return std::unexpected(LoggerError::RingExhausted);
}

// Лінійний прохід сектором до першого кадру, який не сходиться.
RingLogger::ScanResult RingLogger::scanRecords(std::uint32_t idx)
{
    ScanResult result{.endOffset = static_cast<std::uint32_t>(kSectorHeaderSize), .records = 0};
    const std::uint32_t base = sectorAddress(idx);
    std::array<std::byte, kMaxRecordSize> raw{};

    while (result.endOffset + kRecordHeaderSize + kCrcSize <= kSectorSize) {
        const std::span<std::byte> head{raw.data(), kRecordHeaderSize};
        if (!device_.read(base + result.endOffset, head)) {
            break;
        }
        if (getU16(head.subspan(0, 2)) != kRecordMagic) {
            break;  // чисті 0xFF або сміття — даних далі немає
        }

        const auto total = std::to_integer<std::size_t>(raw[2]);
        if (total < kRecordHeaderSize + kCrcSize || result.endOffset + total > kSectorSize) {
            break;
        }

        const std::span<std::byte> frame{raw.data(), total};
        if (!device_.read(base + result.endOffset, frame)) {
            break;
        }
        if (!decodeRecord(frame)) {
            break;  // CRC не зійшлася: недописаний кадр, тут і кінець даних
        }

        result.endOffset += static_cast<std::uint32_t>(total);
        ++result.records;
    }
    return result;
}

std::expected<void, LoggerError> RingLogger::init()
{
    bad_.reset();
    pendingBad_.reset();
    inServiceWrite_ = false;

    std::optional<std::uint32_t> active;
    std::uint32_t activeSeq = 0;
    std::optional<std::uint32_t> newest;
    std::uint32_t newestSeq = 0;
    std::optional<std::uint32_t> tail;
    std::uint32_t tailSeq = 0xFFFFFFFFu;

    for (std::uint32_t idx = 0; idx < kSectorCount; ++idx) {
        const auto header = readHeader(idx);
        if (!header) {
            return std::unexpected(header.error());
        }
        if (header->magic != kSectorMagic || header->version != kFormatVersion) {
            continue;  // сектор ще не наш: чистий, чужий або з битим заголовком
        }

        if (header->state != SectorState::Erased && (!newest || header->seqNum > newestSeq)) {
            newest = idx;
            newestSeq = header->seqNum;
        }

        if (header->state == SectorState::Active) {
            // Двох активних бути не мало б, але якщо кристал прокинувся
            // з половинним записом стану — беремо новіший, старіший закриваємо.
            if (!active || header->seqNum > activeSeq) {
                if (active) {
                    static_cast<void>(writeState(*active, SectorState::Full));
                }
                active = idx;
                activeSeq = header->seqNum;
            } else {
                static_cast<void>(writeState(idx, SectorState::Full));
            }
        }

        const bool holdsData =
            header->state == SectorState::Active || header->state == SectorState::Full;
        if (holdsData && header->seqNum < tailSeq) {
            tailSeq = header->seqNum;
            tail = idx;
        }
    }

    if (active) {
        active_ = *active;
        seqNum_ = newestSeq;
        offset_ = scanRecords(active_).endOffset;
    } else {
        // Активного немає: або кристал чистий, або живлення зникло між
        // закриттям старого сектора й відкриттям нового. Беремо той, що йде
        // за найновішим, — так номери послідовності лишаються зростаючими.
        const std::uint32_t start = newest ? (*newest + 1) % kSectorCount : 0;
        seqNum_ = newestSeq;

        bool opened = false;
        for (std::uint32_t step = 0; step < kSectorCount && !opened; ++step) {
            const std::uint32_t idx = (start + step) % kSectorCount;

            std::uint32_t eraseCount = 0;
            if (const auto header = readHeader(idx); header && header->magic == kSectorMagic) {
                eraseCount = header->eraseCount;
            }

            if (openSector(idx, eraseCount + 1, seqNum_ + 1)) {
                ++seqNum_;
                active_ = idx;
                offset_ = static_cast<std::uint32_t>(kSectorHeaderSize);
                opened = true;
            } else {
                markBad(idx);
            }
        }
        if (!opened) {
            return std::unexpected(LoggerError::RingExhausted);
        }

        if (tail && *tail == active_) {
            tail = nextLive(active_);  // стерли те, що було хвостом
        }
    }

    tail_ = tail.value_or(active_);
    return {};
}

// Про дефектний сектор треба сказати в самому журналі — інакше на сервері
// розрив нумерації виглядатиме як загублений зв'язок.
void RingLogger::reportPendingBad()
{
    if (!pendingBad_ || inServiceWrite_) {
        return;
    }

    std::array<std::byte, 4> payload{};
    putU32(payload, *pendingBad_);

    pendingBad_.reset();
    inServiceWrite_ = true;
    static_cast<void>(append(Level::Error, kLoggerModule, lastTimestampMs_, kTokenBadSector, payload));
    inServiceWrite_ = false;
}

std::expected<void, LoggerError> RingLogger::append(Level level, std::uint8_t moduleId,
                                                    std::uint32_t timestampMs, std::uint32_t tokenId,
                                                    std::span<const std::byte> payload)
{
    std::array<std::byte, kMaxRecordSize> buffer{};
    const RecordHeader header{
        .length = 0,  // заповнить кодувальник
        .level = level,
        .moduleId = moduleId,
        .timestampMs = timestampMs,
        .tokenId = tokenId,
    };

    const auto encoded = encodeRecord(header, payload, buffer);
    if (!encoded) {
        return std::unexpected(LoggerError::PayloadTooBig);
    }
    const std::span<const std::byte> frame = *encoded;

    if (!inServiceWrite_) {
        lastTimestampMs_ = timestampMs;
    }

    for (std::uint32_t attempt = 0; attempt < kSectorCount; ++attempt) {
        if (offset_ + frame.size() > kSectorSize) {
            if (const auto rotated = rotate(); !rotated) {
                return std::unexpected(rotated.error());
            }
        }

        const std::uint32_t address = sectorAddress(active_) + offset_;

        if (!device_.write(address, frame)) {
            markBad(active_);  // кристал відмовив на записі
            offset_ = static_cast<std::uint32_t>(kSectorSize);  // змусити ротацію
            continue;
        }

        if (!verify(address, frame)) {
            // Прочиталося не те, що писали. Найчастіша причина — під нами
            // байти кадру, обірваного знеструмленням: NOR уміє лише гасити
            // біти, тож поверх сміття валідного кадру не покласти. Сектор
            // закриваємо як Full. Дефектним не звемо: кристал команду виконав.
            static_cast<void>(writeState(active_, SectorState::Full));
            offset_ = static_cast<std::uint32_t>(kSectorSize);
            continue;
        }

        offset_ += recordSize(payload.size());
        reportPendingBad();
        return {};
    }

    return std::unexpected(LoggerError::Hal);
}

std::expected<Batch, LoggerError> RingLogger::readBatch(std::span<std::byte> buffer)
{
    for (std::uint32_t step = 0; step < kSectorCount; ++step) {
        const std::uint32_t idx = (tail_ + step) % kSectorCount;
        if (bad_.test(idx)) {
            continue;
        }

        const auto header = readHeader(idx);
        if (!header) {
            return std::unexpected(header.error());
        }
        if (header->magic != kSectorMagic || header->state != SectorState::Full) {
            continue;  // чистий, вже вивантажений або ще активний
        }

        const ScanResult scan = scanRecords(idx);
        const std::size_t length = scan.endOffset - kSectorHeaderSize;
        if (length > buffer.size()) {
            return std::unexpected(LoggerError::BufferTooSmall);
        }

        // Віддаємо сирі кадри як вони лежать: розбирає їх сервер, у якого є
        // таблиця токенів. Модем передає рівно ці байти, без переупакування.
        const std::span<std::byte> window = buffer.subspan(0, length);
        if (!device_.read(sectorAddress(idx) + static_cast<std::uint32_t>(kSectorHeaderSize), window)) {
            return std::unexpected(LoggerError::Hal);
        }

        tail_ = idx;
        return Batch{.sector = idx, .bytes = window, .records = scan.records};
    }

    return std::unexpected(LoggerError::NothingToUpload);
}

std::expected<void, LoggerError> RingLogger::commitTail(std::uint32_t sectorIdx)
{
    if (sectorIdx >= kSectorCount) {
        return std::unexpected(LoggerError::SectorRange);
    }
    if (sectorIdx == active_) {
        return {};  // активний ще росте, ховати його зарано
    }

    if (const auto marked = writeState(sectorIdx, SectorState::Dirty); !marked) {
        markBad(sectorIdx);
        return std::unexpected(marked.error());
    }

    if (sectorIdx == tail_) {
        tail_ = nextLive(sectorIdx);
    }
    return {};
}

}  // namespace fl
