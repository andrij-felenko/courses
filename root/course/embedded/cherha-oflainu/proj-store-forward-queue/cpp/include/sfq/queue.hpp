// queue.hpp — черга «збережи-й-перешли» поверх кільця секторів NOR.
//
// Кільце з N секторів по 4 КіБ. Кадри дозаписуються в сектор голови
// підряд; кадр ніколи не ділиться між секторами, бо стирання працює
// секторами, і половинка кадру в стертому сусіді — це втрачений кадр.
//
// Дві колії вивантаження:
//   жива    — свіжий кадр пішов у ефір одразу після push(), квитанція
//             приходить окремо: ack_live();
//   історія — drain() віддає пачку старих кадрів від хвоста, сервер
//             квитує пачку одним номером: commit_ack().
//
// Хвіст рухається тільки по квитанціях і тільки суцільно: перший
// неквитований кадр його зупиняє, навіть якщо далі лежать квитовані
// живою колією. Ті чекають в AckSet, поки історія доповзе.
//
// Динамічної пам'яті немає жодного байта: увесь стан усередині об'єкта,
// робочий буфер кадру теж.
#pragma once

#include <algorithm>
#include <array>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <utility>

#include "sfq/ack_set.hpp"
#include "sfq/batch.hpp"
#include "sfq/flash.hpp"
#include "sfq/frame.hpp"

namespace sfq {

enum class QueueError {
    BadParameter,  // безглузді межі або довжина навантаження
    Full,          // кільце повне, а кадр не вартий витіснення історії
    Io,            // носій не відповів
    Empty,         // віддавати нічого
};

// push() приходить із високопріоритетного завдання збору даних (а то й
// прямо з переривання таймера), drain()/commit_ack() — із мережевого.
// Вони діляться курсорами й ЄДИНИМ робочим буфером кадру.
template <class L>
concept BasicLockable = requires(L& lock) {
    { lock.lock() };
    { lock.unlock() };
};

// Однопотоковий вузол: замок є, коштує нуль команд.
struct NullLock {
    void lock() noexcept {}
    void unlock() noexcept {}
};

struct QueueStats {
    std::uint32_t records_written{};
    std::uint32_t bytes_written{};
    std::uint32_t sectors_erased{};
    std::uint32_t sectors_evicted{};     // витіснено під важливіші дані
    std::uint32_t dropped_full{};        // відмовлено низькому пріоритету
    std::uint32_t corrupt_records{};     // биті CRC або чужа преамбула
    std::uint32_t recovered_records{};   // знайдено цілими при скануванні
    std::uint32_t flash_errors{};
    std::uint32_t skipped_live_acked{};  // історія не читала вдруге те, що доїхало живцем
};

struct Cursor {
    std::uint32_t sector{};
    std::uint32_t offset{};

    friend bool operator==(const Cursor&, const Cursor&) = default;
};

// payload дивиться у внутрішній буфер черги й чинний до наступного
// виклику: мережеве завдання або віддає його в сокет одразу, або копіює.
struct Record {
    FrameHeader header{};
    std::span<const std::byte> payload{};
    std::size_t stride{};
    Cursor at{};
};

template <FlashDevice Dev, BasicLockable Lock = NullLock>
class StoreForwardQueue {
public:
    struct Config {
        std::uint32_t base_addr{};
        std::uint32_t sector_count{};
    };

    StoreForwardQueue(Dev& device, Config config) noexcept
        : device_{device},
          base_addr_{config.base_addr},
          sector_count_{config.sector_count},
          sector_size_{device.geometry().sector_size}
    {
    }

    StoreForwardQueue(const StoreForwardQueue&) = delete;
    StoreForwardQueue& operator=(const StoreForwardQueue&) = delete;

    // Сканує кільце й відновлює голову, хвіст і лічильник номерів.
    [[nodiscard]] std::expected<void, QueueError> mount() noexcept
    {
        const auto geom = device_.geometry();
        if (sector_count_ < 2 || geom.sector_size < kRecordMax ||
            base_addr_ + sector_count_ * geom.sector_size > geom.capacity) {
            return std::unexpected(QueueError::BadParameter);
        }

        const Guard guard{lock_};

        head_ = tail_ = drain_ = Cursor{};
        next_seq_ = 1;
        acks_.clear();
        // mount() — це старт вузла, а не «перечитати про всяк випадок».
        // Лічильники рахують життя після ввімкнення живлення, інакше
        // після відновлення вони показували б суму двох різних сеансів.
        stats_ = QueueStats{};

        bool found = false;
        std::uint32_t highest = 0;
        Cursor head{};

        // У кожному секторі кадри лежать підряд від нуля, тому перший
        // розрив — стерта область, битий CRC, обірваний хвіст — закінчує
        // сектор. Голова стає за кадром із найбільшим номером.
        for (std::uint32_t sector = 0; sector < sector_count_; ++sector) {
            for (Cursor at{sector, 0};;) {
                const auto record = read_record(at);
                if (!record) {
                    if (record.error() == RecordFault::Io) {
                        return std::unexpected(QueueError::Io);
                    }
                    break;
                }

                ++stats_.recovered_records;
                if (!found || seq_after(record->header.seq, highest)) {
                    found = true;
                    highest = record->header.seq;
                    head = Cursor{sector,
                                  at.offset + static_cast<std::uint32_t>(record->stride)};
                }
                at.offset += static_cast<std::uint32_t>(record->stride);
            }
        }

        if (!found) {
            // Чистий кристал або суцільне сміття: стираємо перший сектор
            // і починаємо журнал з нуля.
            if (!device_.erase_sector(sector_addr(0))) {
                ++stats_.flash_errors;
                return std::unexpected(QueueError::Io);
            }
            ++stats_.sectors_erased;
            return {};
        }

        head_ = head;
        next_seq_ = highest + 1;

        // Хвіст — найстарші дані: перший сектор із валідним кадром, якщо
        // йти по кільцю ВІД голови вперед.
        tail_ = Cursor{head_.sector, 0};
        for (std::uint32_t step = 1; step < sector_count_; ++step) {
            const Cursor probe{(head_.sector + step) % sector_count_, 0};
            if (read_record(probe)) {
                tail_ = probe;
                break;
            }
        }
        drain_ = tail_;

        // Квитанції живуть в ОЗП і знеструмлення не переживають, тому
        // все, що лежить у флеші, після старту вважається недоставленим.
        // Частина кадрів поїде вдруге; дублі відсіє сервер за номером —
        // це чесніша ціна, ніж витрачати цикли стирання на позначки.
        return {};
    }

    // Кладе кадр у флеш і повертає присвоєний номер — саме його потім
    // називає квитанція живої колії.
    [[nodiscard]] std::expected<std::uint32_t, QueueError> push(
        RecordType type, Priority priority, std::uint64_t timestamp_ms,
        std::span<const std::byte> payload) noexcept
    {
        if (payload.empty() || payload.size() > kMaxPayload) {
            return std::unexpected(QueueError::BadParameter);
        }

        const Guard guard{lock_};
        const std::size_t stride = frame_stride(static_cast<std::uint16_t>(payload.size()));

        if (head_.offset + stride > sector_size_) {
            if (auto rolled = roll_head(priority); !rolled) {
                return std::unexpected(rolled.error());
            }
        } else if (!area_is_blank(head_, stride)) {
            // Місце під головою не чисте: попередній запис обірвався на
            // півслові. Дописувати туди не можна — кидаємо решту сектора.
            ++stats_.corrupt_records;
            if (auto rolled = roll_head(priority); !rolled) {
                return std::unexpected(rolled.error());
            }
        }

        const FrameHeader header{
            .type = type,
            .priority = priority,
            .seq = next_seq_,
            .timestamp_ms = timestamp_ms,
            .payload_len = static_cast<std::uint16_t>(payload.size()),
        };
        const std::size_t packed = frame_pack(scratch_, header, payload);

        if (!device_.program(address_of(head_), std::span{scratch_}.first(packed))) {
            // Кадр не доїхав у кристал цілим. Голову НЕ рухаємо:
            // сканування побачить тут розрив і зупиниться, а наступний
            // push помітить нечисту область і перескочить сектор.
            ++stats_.flash_errors;
            return std::unexpected(QueueError::Io);
        }

        head_.offset += static_cast<std::uint32_t>(stride);
        ++next_seq_;
        ++stats_.records_written;
        stats_.bytes_written += static_cast<std::uint32_t>(stride);
        return header.seq;
    }

    // Найстаріший кадр черги, БЕЗ зсуву хвоста.
    [[nodiscard]] std::expected<Record, QueueError> peek_tail() noexcept
    {
        const Guard guard{lock_};

        for (std::uint32_t step = 0; step <= sector_count_; ++step) {
            if (is_empty()) {
                return std::unexpected(QueueError::Empty);
            }

            const auto record = read_record(tail_);
            if (record) {
                return *record;
            }
            switch (record.error()) {
                case RecordFault::Io:
                    return std::unexpected(QueueError::Io);
                case RecordFault::Blank:
                    if (tail_.sector == head_.sector) {
                        return std::unexpected(QueueError::Empty);
                    }
                    roll_tail();
                    break;
                case RecordFault::Corrupt:
                    // Битий кадр не має права заклинити чергу назавжди.
                    skip_bad_tail();
                    break;
            }
        }
        return std::unexpected(QueueError::Empty);
    }

    // Пачка історії від курсора вивантаження. Кадри, уже квитовані
    // живою колією, пропускаються мовчки.
    [[nodiscard]] std::expected<std::size_t, QueueError> drain(DrainBatch& batch) noexcept
    {
        const Guard guard{lock_};

        batch.clear();
        sync_drain();

        const auto guard_steps =
            sector_count_ + static_cast<std::uint32_t>(DrainBatch::kMaxRecords) * 2 + 8;

        for (std::uint32_t step = 0; step < guard_steps; ++step) {
            if (drain_at_head()) {
                break;  // історію вичерпано, далі тільки жива колія
            }

            const auto record = read_record(drain_);
            if (!record) {
                if (record.error() == RecordFault::Io) {
                    break;
                }
                if (record.error() == RecordFault::Corrupt) {
                    ++stats_.corrupt_records;
                }
                if (drain_.sector == head_.sector) {
                    drain_.offset = head_.offset;
                } else {
                    drain_ = Cursor{next_sector(drain_.sector), 0};
                }
                continue;
            }

            // Ось воно, розділення колій: кадр, який щойно поїхав живцем
            // і був квитований, історія не читає вдруге.
            if (acks_.contains(record->header.seq)) {
                ++stats_.skipped_live_acked;
                drain_.offset += static_cast<std::uint32_t>(record->stride);
                continue;
            }

            if (!batch.try_append(record->header, record->payload)) {
                break;  // радіокадр добито, решта поїде наступною пачкою
            }

            drain_.offset += static_cast<std::uint32_t>(record->stride);
            if (drain_.offset + kHeaderSize > sector_size_ && drain_.sector != head_.sector) {
                drain_ = Cursor{next_sector(drain_.sector), 0};
            }
        }

        if (batch.empty()) {
            return std::unexpected(QueueError::Empty);
        }
        return batch.size();
    }

    // Пачка не долетіла: курсор історії назад на хвіст.
    void drain_rewind() noexcept
    {
        const Guard guard{lock_};
        drain_ = tail_;
    }

    // Пакетне квитування: сервер має все до acked_seq включно.
    void commit_ack(std::uint32_t acked_seq) noexcept
    {
        const Guard guard{lock_};
        // Нижня межа умовна: зайве однаково зріже prune_below.
        acks_.add(AckSet::Range{1, acked_seq});
        advance_tail();
    }

    // Квитанція живої колії на один кадр.
    void ack_live(std::uint32_t seq) noexcept
    {
        const Guard guard{lock_};
        acks_.add(seq);
        advance_tail();
    }

    [[nodiscard]] bool empty() noexcept
    {
        const Guard guard{lock_};
        return is_empty();
    }

    [[nodiscard]] std::uint32_t bytes_pending() noexcept
    {
        const Guard guard{lock_};
        return pos_from_tail(head_) - tail_.offset;
    }

    [[nodiscard]] const QueueStats& stats() const noexcept { return stats_; }
    [[nodiscard]] const AckSet& acks() const noexcept { return acks_; }
    [[nodiscard]] Cursor head() const noexcept { return head_; }
    [[nodiscard]] Cursor tail() const noexcept { return tail_; }
    [[nodiscard]] Cursor drain_cursor() const noexcept { return drain_; }
    [[nodiscard]] std::uint32_t next_seq() const noexcept { return next_seq_; }

private:
    enum class RecordFault {
        Blank,    // стерта область: далі в секторі записів немає
        Corrupt,  // чужа преамбула, немислима довжина або битий CRC
        Io,
    };

    // Замок знімається на будь-якому виході з області видимості —
    // включно з раннім return посеред десятка перевірок.
    class Guard {
    public:
        explicit Guard(Lock& lock) noexcept : lock_{lock} { lock_.lock(); }
        ~Guard() { lock_.unlock(); }
        Guard(const Guard&) = delete;
        Guard& operator=(const Guard&) = delete;

    private:
        Lock& lock_;
    };

    // Знакова різниця: коли лічильник колись перекотиться через 2^32,
    // «більший» лишиться більшим.
    [[nodiscard]] static bool seq_after(std::uint32_t a, std::uint32_t b) noexcept
    {
        return static_cast<std::int32_t>(a - b) > 0;
    }

    [[nodiscard]] std::uint32_t next_sector(std::uint32_t sector) const noexcept
    {
        return (sector + 1) % sector_count_;
    }

    [[nodiscard]] std::uint32_t sector_addr(std::uint32_t sector) const noexcept
    {
        return base_addr_ + sector * sector_size_;
    }

    [[nodiscard]] std::uint32_t address_of(Cursor at) const noexcept
    {
        return sector_addr(at.sector) + at.offset;
    }

    [[nodiscard]] bool is_empty() const noexcept
    {
        return tail_.sector == head_.sector && tail_.offset >= head_.offset;
    }

    [[nodiscard]] bool drain_at_head() const noexcept
    {
        return drain_.sector == head_.sector && drain_.offset >= head_.offset;
    }

    // Скільки байтів від хвоста до точки кільця.
    [[nodiscard]] std::uint32_t pos_from_tail(Cursor at) const noexcept
    {
        const std::uint32_t laps = (at.sector + sector_count_ - tail_.sector) % sector_count_;
        return laps * sector_size_ + at.offset;
    }

    // Витіснення сектора або пакетна квитанція можуть обігнати курсор
    // історії — тоді він просто стає на хвіст і читає ще раз.
    void sync_drain() noexcept
    {
        const std::uint32_t at = pos_from_tail(drain_);
        if (at < tail_.offset || at > pos_from_tail(head_)) {
            drain_ = tail_;
        }
    }

    [[nodiscard]] std::expected<Record, RecordFault> read_record(Cursor at) noexcept
    {
        if (at.offset + kHeaderSize > sector_size_) {
            return std::unexpected(RecordFault::Blank);  // не влізе навіть заголовок
        }

        const auto buffer = std::span{scratch_};
        if (!device_.read(address_of(at), buffer.first(kHeaderSize))) {
            ++stats_.flash_errors;
            return std::unexpected(RecordFault::Io);
        }
        if (is_blank(buffer.first(kHeaderSize))) {
            return std::unexpected(RecordFault::Blank);
        }

        const auto header = frame_parse(buffer.first(kHeaderSize));
        if (!header) {
            return std::unexpected(RecordFault::Corrupt);
        }

        const std::size_t stride = frame_stride(header->payload_len);
        if (at.offset + stride > sector_size_) {
            return std::unexpected(RecordFault::Corrupt);  // довжина обіцяє більше, ніж є
        }
        if (!device_.read(address_of(at), buffer.first(stride))) {
            ++stats_.flash_errors;
            return std::unexpected(RecordFault::Io);
        }
        if (!frame_crc_ok(buffer.first(stride), header->payload_len)) {
            return std::unexpected(RecordFault::Corrupt);
        }

        return Record{
            .header = *header,
            .payload = buffer.subspan(kHeaderSize, header->payload_len),
            .stride = stride,
            .at = at,
        };
    }

    // Перерваний запис лишає нулі там, де черга чекає одиниць: дозапис
    // поверх них дав би кадр, який ніколи не зійдеться за CRC.
    [[nodiscard]] bool area_is_blank(Cursor at, std::size_t length) noexcept
    {
        std::array<std::byte, 64> probe{};
        std::uint32_t addr = address_of(at);

        while (length > 0) {
            const std::size_t chunk = std::min(length, probe.size());
            if (!device_.read(addr, std::span{probe}.first(chunk))) {
                ++stats_.flash_errors;
                return false;
            }
            if (!is_blank(std::span{probe}.first(chunk))) {
                return false;
            }
            addr += static_cast<std::uint32_t>(chunk);
            length -= chunk;
        }
        return true;
    }

    void roll_tail() noexcept
    {
        tail_ = Cursor{next_sector(tail_.sector), 0};
        sync_drain();
    }

    // Хвіст упхнувся в нечитабельне. Перескочити всередині сектора нема
    // як: межі наступного кадру знаємо тільки з попереднього заголовка.
    // Жертвуємо рештою сектора — це дешевше за вічне заклинювання.
    void skip_bad_tail() noexcept
    {
        ++stats_.corrupt_records;
        if (tail_.sector != head_.sector) {
            roll_tail();
        } else {
            tail_.offset = head_.offset;
            sync_drain();
        }
    }

    // Перехід на наступний сектор: за потреби витісняє хвіст і стирає
    // сектор наперед, щоб push уже мав куди писати.
    [[nodiscard]] std::expected<void, QueueError> roll_head(Priority priority) noexcept
    {
        const std::uint32_t next = next_sector(head_.sector);

        if (next == tail_.sector) {
            if (priority == Priority::Low) {
                // Високочастотний шум не вартий того, щоб затерти історію.
                ++stats_.dropped_full;
                return std::unexpected(QueueError::Full);
            }
            tail_ = Cursor{next_sector(tail_.sector), 0};
            ++stats_.sectors_evicted;
            sync_drain();

            if (const auto record = read_record(tail_)) {
                acks_.prune_below(record->header.seq);
            }
        }

        if (!device_.erase_sector(sector_addr(next))) {
            ++stats_.flash_errors;
            return std::unexpected(QueueError::Io);
        }
        ++stats_.sectors_erased;

        head_ = Cursor{next, 0};
        sync_drain();
        return {};
    }

    // Просунути хвіст по всіх квитованих кадрах підряд.
    void advance_tail() noexcept
    {
        const std::uint32_t guard_steps =
            sector_count_ * (sector_size_ / static_cast<std::uint32_t>(kHeaderSize)) + 8;

        for (std::uint32_t step = 0; step < guard_steps; ++step) {
            if (is_empty()) {
                acks_.prune_below(next_seq_);
                return;
            }

            const auto record = read_record(tail_);
            if (!record) {
                switch (record.error()) {
                    case RecordFault::Io:
                        return;
                    case RecordFault::Blank:
                        if (tail_.sector == head_.sector) {
                            return;
                        }
                        roll_tail();
                        continue;
                    case RecordFault::Corrupt:
                        skip_bad_tail();
                        continue;
                }
                continue;
            }

            if (!acks_.contains(record->header.seq)) {
                // Найстаріший неквитований — далі хвіст не йде.
                acks_.prune_below(record->header.seq);
                return;
            }

            tail_.offset += static_cast<std::uint32_t>(record->stride);
            acks_.prune_below(record->header.seq + 1);

            if (tail_.offset + kHeaderSize > sector_size_ && tail_.sector != head_.sector) {
                roll_tail();
            } else {
                sync_drain();
            }
        }
    }

    Dev& device_;
    Lock lock_{};

    std::uint32_t base_addr_{};
    std::uint32_t sector_count_{};
    std::uint32_t sector_size_{};

    Cursor head_{};
    Cursor tail_{};
    // Читальний курсор історії: біжить попереду хвоста, поки пачки
    // летять у ефір і ще не квитовані.
    Cursor drain_{};

    std::uint32_t next_seq_{1};
    AckSet acks_{};
    QueueStats stats_{};

    std::array<std::byte, kRecordMax> scratch_{};
};

}  // namespace sfq
