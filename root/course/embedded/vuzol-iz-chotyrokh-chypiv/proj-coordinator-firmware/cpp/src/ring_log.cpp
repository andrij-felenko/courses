#include <algorithm>

#include "ring_log.hpp"

namespace node {

void RingLog::resetPageBuffer() noexcept {
    page_.fill(std::byte{0xFF});
    pageUsed_ = 0;
    pageRecords_ = 0;
}

// Дешева перевірка «сектор чистий»: перший слот увесь в одиницях. Повного
// доказу вона не дає, але журнал пише сектор строго з початку — якщо перший
// слот незайманий, незайманий і весь сектор.
bool RingLog::sectorIsErased(std::uint32_t sectorAddr) noexcept {
    RecordBytes raw{};
    if (!flash_.read(sectorAddr, raw)) return false;
    return erased(raw);
}

void RingLog::beginErase(std::uint32_t sectorAddr) noexcept {
    if (flash_.startSectorErase(sectorAddr)) {
        state_ = State::Erasing;
        opStartedMs_ = mcu::time::millis();
        ++sectorsErased_;
    } else {
        ++writeErrors_;
        lastWriteOk_ = false;
    }
}

std::expected<std::optional<Record>, LogError> RingLog::mount() noexcept {
    resetPageBuffer();

    if (!flash_.probe()) return std::unexpected{LogError::NoChip};

    // Крок 1. Заголовок кожного сектора — його перший запис. Найновіший той,
    // у кого більша мітка часу: кільце пише послідовно, тож далі йде або
    // чистий сектор, або найстаріші дані, які пора затирати.
    std::uint32_t bestSector = 0;
    std::uint32_t bestTime = 0;
    bool anyValid = false;

    for (std::uint32_t s = 0; s < kSectorCount; ++s) {
        if ((s & 0xFFu) == 0u) {
            mcu::Watchdog::kick();   // скан 16 МБ триває довше двох секунд
        }

        RecordBytes raw{};
        if (!flash_.read(s * kFlashSectorSize, raw)) {
            return std::unexpected{LogError::ReadFailed};
        }
        if (erased(raw)) continue;

        const Record head = fromBytes(raw);
        if (!valid(head)) continue;

        if (!anyValid || head.timestamp >= bestTime) {
            bestTime = head.timestamp;
            bestSector = s;
            anyValid = true;
        }
    }

    if (!anyValid) {
        // Чистий чип або чип із самим сміттям: починаємо з нуля.
        writeAddr_ = 0;
        if (!sectorIsErased(0)) beginErase(0);
        mounted_ = true;
        return std::nullopt;
    }

    // Крок 2. Усередині знайденого сектора шукаємо першу вільну сторінку
    // і заразом останній справжній запис — з нього триває нумерація.
    const std::uint32_t sectorAddr = bestSector * kFlashSectorSize;
    std::uint32_t freePage = kPagesPerSector;
    std::optional<Record> newest;

    for (std::uint32_t p = 0; p < kPagesPerSector; ++p) {
        std::array<std::byte, kFlashPageSize> raw{};
        if (!flash_.read(sectorAddr + p * kFlashPageSize, raw)) {
            return std::unexpected{LogError::ReadFailed};
        }

        if (erased(std::span<const std::byte>{raw}.first(kRecordSize))) {
            freePage = p;
            break;
        }

        for (std::uint32_t r = 0; r < kRecordsPerPage; ++r) {
            RecordBytes slot{};
            std::copy_n(raw.begin() + r * kRecordSize, kRecordSize, slot.begin());

            if (erased(slot)) break;

            const Record rec = fromBytes(slot);
            if (!valid(rec)) continue;

            ++records_;
            newest = rec;
        }
    }

    if (freePage < kPagesPerSector) {
        writeAddr_ = sectorAddr + freePage * kFlashPageSize;
    } else {
        // Сектор дописаний до кінця — переходимо на наступний по кільцю.
        writeAddr_ = nextSector(sectorAddr);
        if (!sectorIsErased(writeAddr_)) beginErase(writeAddr_);
    }

    // Крок 3. Сектор попереду має бути чистим ще до того, як туди дійде
    // запис: інакше перша ж сторінка нового сектора чекатиме стирання.
    if (state_ == State::Idle) {
        const std::uint32_t ahead = nextSector(writeAddr_);
        if (!sectorIsErased(ahead)) beginErase(ahead);
    }

    mounted_ = true;
    return newest;
}

bool RingLog::append(const Record& rec) noexcept {
    if (!mounted_) return false;

    if (pagePending_) {
        poll();   // дамо автомату шанс дожати попередню сторінку просто зараз
        if (pagePending_) {
            ++writeErrors_;
            lastWriteOk_ = false;
            return false;
        }
    }

    const RecordBytes raw = toBytes(rec);
    std::copy(raw.begin(), raw.end(), page_.begin() + pageUsed_);
    pageUsed_ += kRecordSize;
    ++pageRecords_;
    ++records_;

    if (pageRecords_ >= kRecordsPerPage) {
        // Хвіст сторінки лишається 0xFF: він і є ознакою «далі порожньо».
        pagePending_ = true;
    }
    return true;
}

void RingLog::poll() noexcept {
    if (!mounted_) return;

    if (state_ != State::Idle) {
        if (flash_.busy()) {
            const std::uint32_t limit =
                (state_ == State::Erasing) ? kEraseLimitMs : kProgramLimitMs;

            if (mcu::time::elapsed(opStartedMs_, limit)) {
                // Чип не звільнився за паспортний час: це вже несправність,
                // а не затримка. Далі не пишемо — вирішить сторожовий таймер.
                ++writeErrors_;
                lastWriteOk_ = false;
                state_ = State::Idle;
            }
            return;
        }

        const bool accepted = flash_.lastOperationAccepted();
        const State finished = state_;

        state_ = State::Idle;
        lastWriteOk_ = accepted;
        if (!accepted) ++writeErrors_;

        if (finished == State::Programming) {
            const std::uint32_t previous = writeAddr_;

            writeAddr_ += kFlashPageSize;
            if (writeAddr_ >= kFlashTotalSize) writeAddr_ = 0;   // кільце замкнулося

            // Перейшли в новий сектор — час стерти той, що за ним. Попереду
            // ще шістнадцять сторінок, тобто близько трьох хвилин: жоден
            // запис на стирання чекати не буде.
            if (previous / kFlashSectorSize != writeAddr_ / kFlashSectorSize) {
                beginErase(nextSector(writeAddr_));
                events_.push(Event::FlashIdle);
                return;
            }
        }
        events_.push(Event::FlashIdle);
    }

    if (state_ == State::Idle && pagePending_) {
        if (flash_.startPageProgram(writeAddr_, page_)) {
            state_ = State::Programming;
            opStartedMs_ = mcu::time::millis();
            pagePending_ = false;
            resetPageBuffer();
        } else if (!flash_.busy()) {
            // Чип відкинув команду: сторінку втрачено, буфер звільняємо, щоб
            // наступні зрізи не пропали разом з нею.
            ++writeErrors_;
            lastWriteOk_ = false;
            pagePending_ = false;
            resetPageBuffer();
        }
    }
}

}  // namespace node
