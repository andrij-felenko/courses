#include "blackbox.hpp"

#include <algorithm>
#include <cmath>

#include "wire.hpp"

namespace cart {

std::array<std::byte, Record::kSize> Record::encode() const noexcept {
    std::array<std::byte, kSize> raw{};
    wire::putU32(raw, 0, static_cast<std::uint32_t>(stamp.count()));
    raw[4] = static_cast<std::byte>(event);
    raw[5] = static_cast<std::byte>(critical ? 1 : 0);
    wire::putU16(raw, 6, count);
    wire::putF32(raw, 8, min);
    wire::putF32(raw, 12, max);
    wire::putF32(raw, 16, avg);
    wire::putF32(raw, 20, rms);
    return raw;
}

std::optional<Record> Record::decode(std::span<const std::byte, kSize> raw) noexcept {
    if (raw[4] == std::byte{0xFF}) return std::nullopt;   // слот стерто, запису тут немає
    Record r{};
    r.stamp = Millis{wire::u32(raw, 0)};
    r.event = std::to_integer<std::uint8_t>(raw[4]);
    r.critical = raw[5] != std::byte{0};
    r.count = wire::u16(raw, 6);
    r.min = wire::f32(raw, 8);
    r.max = wire::f32(raw, 12);
    r.avg = wire::f32(raw, 16);
    r.rms = wire::f32(raw, 20);
    return r;
}

BlackBox::BlackBox(Board& board) : board_{board} {
    // Кільце рутинної телеметрії чистимо на старті...
    for (std::size_t sector = 0; sector < kRingSectors; ++sector) {
        if (!board_.erase(sector)) ++stats_.dropped;
        dirty_[sector] = false;
    }
    // ...а пул чорної скриньки НЕ чіпаємо: там лежать останні секунди перед
    // попередньою аварією. Знаходимо перший вільний слот і пишемо далі.
    crashIdx_ = scanCrashPool();
}

std::size_t BlackBox::scanCrashPool() {
    std::size_t used = 0;
    for (std::size_t pos = 0; pos < kCrashSlots; ++pos) {
        const auto sector = kRingSectors + pos / kSlotsPerSector;
        const auto slot = pos % kSlotsPerSector;
        std::array<std::byte, 1> marker{};
        if (!board_.read(sector, slot * Record::kSize + 4, marker)) break;
        if (marker[0] == std::byte{0xFF}) break;   // тут пул закінчився
        dirty_[sector] = true;
        used = pos + 1;
    }
    return used;
}

// Записи цього сектора зараз зникнуть: покажчик зливу не має на них указувати.
void BlackBox::discardSector(std::size_t sector) {
    while (readIdx_ < writeIdx_ && (readIdx_ % kRingSlots) / kSlotsPerSector == sector) {
        ++readIdx_;
        ++stats_.overwritten;
    }
}

void BlackBox::ringPut(const Record& r) {
    const auto pos = writeIdx_ % kRingSlots;
    const auto sector = pos / kSlotsPerSector;
    const auto slot = pos % kSlotsPerSector;

    if (slot == 0 && dirty_[sector]) {
        // Фонове завдання не встигло — стираємо просто зараз. Це 40–100 мс
        // блокування пам'яті посеред реального часу, тому такі випадки рахуємо.
        discardSector(sector);
        if (!board_.erase(sector)) {
            ++stats_.dropped;
            writeIdx_ += kSlotsPerSector;
            return;
        }
        dirty_[sector] = false;
        ++stats_.blockingErases;
        if (preErase_ == sector) preErase_.reset();
    }

    const auto raw = r.encode();
    if (board_.write(sector, slot * Record::kSize, raw)) {
        dirty_[sector] = true;
        ++stats_.written;
    } else {
        ++stats_.dropped;
    }
    ++writeIdx_;

    // Читач відстав більше ніж на повне коло: те, чого він не встиг злити,
    // фізично вже затерто, тож покажчик зливу підтягуємо до живих записів.
    if (writeIdx_ - readIdx_ > kRingSlots) {
        stats_.overwritten += static_cast<std::uint32_t>((writeIdx_ - readIdx_) - kRingSlots);
        readIdx_ = writeIdx_ - kRingSlots;
    }

    // Сектор заповнено на 80% — замовляємо стирання наступного у фон.
    if ((slot + 1) * 100 >= kSlotsPerSector * kPreErasePercent) {
        const auto next = (sector + 1) % kRingSectors;
        if (dirty_[next]) preErase_ = next;
    }
}

void BlackBox::crashPut(const Record& r) {
    const auto pos = crashIdx_ % kCrashSlots;
    const auto sector = kRingSectors + pos / kSlotsPerSector;
    const auto slot = pos % kSlotsPerSector;

    if (slot == 0 && dirty_[sector]) {
        // Пул теж скінченний, але витісняє його лише сам пул: рутинне кільце
        // сюди не дотягується ніколи, скільки б телеметрії не набігло.
        if (!board_.erase(sector)) {
            ++stats_.dropped;
            crashIdx_ += kSlotsPerSector;
            return;
        }
        dirty_[sector] = false;
    }

    const auto raw = r.encode();
    if (board_.write(sector, slot * Record::kSize, raw)) {
        dirty_[sector] = true;
        ++stats_.written;
    } else {
        ++stats_.dropped;
    }
    ++crashIdx_;
}

void BlackBox::sample(Millis t, float value, Millis offline) {
    // Дворівнева політика: онлайн пишемо мінімум (усе й так летить в ефір),
    // перші 10 с офлайну — повні 50 Гц, далі згортаємо секунду в одну пачку.
    std::uint16_t need = 25;
    if (offline > Millis{0}) need = offline < 10s ? 1 : static_cast<std::uint16_t>(1s / kSamplePeriod);

    if (windowCount_ == 0) {
        windowStart_ = t;
        wMin_ = value;
        wMax_ = value;
        wSum_ = 0.0f;
        wSq_ = 0.0f;
    }
    wMin_ = std::min(wMin_, value);
    wMax_ = std::max(wMax_, value);
    wSum_ += value;
    wSq_ += value * value;
    ++windowCount_;

    if (windowCount_ < need) return;

    const auto n = static_cast<float>(windowCount_);
    ringPut(Record{.stamp = windowStart_,
                   .event = kEventSample,
                   .critical = false,
                   .count = windowCount_,
                   .min = wMin_,
                   .max = wMax_,
                   .avg = wSum_ / n,
                   .rms = std::sqrt(wSq_ / n)});
    windowCount_ = 0;
}

void BlackBox::event(Millis t, std::uint8_t code, bool critical) {
    const Record r{.stamp = t, .event = code, .critical = critical};
    // Критична подія лягає в захищений пул і, копією, у чергу на злив.
    if (critical) crashPut(r);
    ringPut(r);
}

void BlackBox::backgroundErase() {
    if (!preErase_) return;
    const auto target = *preErase_;
    preErase_.reset();

    discardSector(target);
    if (board_.erase(target)) dirty_[target] = false;
    else ++stats_.dropped;
}

std::size_t BlackBox::drain(std::size_t budgetBytes) {
    std::size_t sent = 0;
    while (readIdx_ < writeIdx_ && budgetBytes >= Record::kSize) {
        const auto pos = readIdx_ % kRingSlots;
        const auto sector = pos / kSlotsPerSector;
        const auto slot = pos % kSlotsPerSector;

        std::array<std::byte, Record::kSize> raw{};
        if (!board_.read(sector, slot * Record::kSize, raw)) {
            ++readIdx_;      // битий слот пропускаємо, злив на ньому не спиняється
            continue;
        }
        if (board_.send(raw) < raw.size()) break;   // канал не прийняв — спробуємо потім

        ++readIdx_;
        budgetBytes -= Record::kSize;
        sent += Record::kSize;
    }
    return sent;
}

std::vector<Record> BlackBox::crashRecords() const {
    const auto count = std::min(crashIdx_, kCrashSlots);
    std::vector<Record> out;
    out.reserve(count);

    for (std::size_t i = 0; i < count; ++i) {
        const auto pos = (crashIdx_ - count + i) % kCrashSlots;
        const auto sector = kRingSectors + pos / kSlotsPerSector;
        const auto slot = pos % kSlotsPerSector;

        std::array<std::byte, Record::kSize> raw{};
        if (!board_.read(sector, slot * Record::kSize, raw)) continue;
        if (auto r = Record::decode(raw)) out.push_back(*r);
    }
    return out;
}

}  // namespace cart
