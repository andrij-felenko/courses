// Модель кільця секторів SPI NOR у пам'яті і три сценарії відновлення.
//
// Тут навмисно немає ані черги вивантаження, ані політики витіснення —
// предмет цього прикладу один: що бачить прошивка на старті після того,
// як живлення зникло посеред запису.
#include <algorithm>
#include <array>
#include <cstdint>
#include <expected>
#include <functional>
#include <limits>
#include <print>
#include <ranges>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include "sf/frame.hpp"
#include "sf/recovery.hpp"

namespace {

constexpr std::uint32_t kSectorSize  = 4096;
constexpr std::uint32_t kSectorCount = 4;
constexpr std::uint16_t kPayloadLen  = 96;
constexpr std::size_t   kFrameLen    = sf::frame_size(kPayloadLen);

// --- модель носія --------------------------------------------------------

class RamNor {
public:
    RamNor(std::uint32_t sector_size, std::uint32_t sector_count)
        : sector_size_{sector_size}
        , cells_(static_cast<std::size_t>(sector_size) * sector_count, std::byte{0xFF})
    {}

    [[nodiscard]] std::uint32_t sector_size() const noexcept { return sector_size_; }

    [[nodiscard]] std::uint32_t sector_count() const noexcept
    {
        return static_cast<std::uint32_t>(cells_.size() / sector_size_);
    }

    [[nodiscard]] std::expected<void, sf::IoError> read(std::uint32_t addr,
                                                        std::span<std::byte> dst) const
    {
        if (addr > cells_.size() || dst.size() > cells_.size() - addr) {
            return std::unexpected(sf::IoError{addr, dst.size()});
        }
        std::ranges::copy(std::span{cells_}.subspan(addr, dst.size()), dst.begin());
        return {};
    }

    void erase(std::uint32_t sector)
    {
        std::ranges::fill(sector_span(sector), std::byte{0xFF});
    }

    void erase_all() { std::ranges::fill(cells_, std::byte{0xFF}); }

    // Запис у NOR лише гасить біти (1 → 0); підняти біт може тільки
    // стирання цілого сектора. Модель тримає це правило, щоб обірваний
    // кадр виглядав так само, як на живому кристалі: заголовок є, а
    // хвіст — суцільні 0xFF.
    void program(std::uint32_t addr, std::span<const std::byte> src)
    {
        for (std::size_t i = 0; i < src.size(); ++i) {
            cells_[addr + i] &= src[i];
        }
    }

    // Збій запису або деградація комірок: кілька бітів упали в нуль.
    void disturb(std::uint32_t addr, std::byte mask) { cells_[addr] &= mask; }

private:
    std::span<std::byte> sector_span(std::uint32_t sector)
    {
        return std::span{cells_}.subspan(static_cast<std::size_t>(sector) * sector_size_,
                                         sector_size_);
    }

    std::uint32_t          sector_size_;
    std::vector<std::byte> cells_;
};

static_assert(sf::FlashArea<RamNor>);

// --- письменник черги ----------------------------------------------------

class Writer {
public:
    explicit Writer(RamNor& flash) : flash_{flash}, valid_(flash.sector_count(), 0) {}

    void reset()
    {
        flash_.erase_all();
        std::ranges::fill(valid_, 0u);
        sector_ = 0;
        offset_ = 0;
        seq_    = 1;
        ts_ms_  = kEpochStart;
    }

    // cut_at — скільки байтів кадру встигло лягти на носій до
    // знеструмлення; за замовчуванням кадр записується цілком.
    void append(sf::Kind kind, std::size_t cut_at = std::numeric_limits<std::size_t>::max())
    {
        std::array<std::byte, kPayloadLen>  payload{};
        std::array<std::byte, sf::kMaxFrame> frame{};

        for (std::uint16_t i = 0; i < kPayloadLen; ++i) {
            payload[i] = static_cast<std::byte>(seq_ + i);
        }

        const sf::Header header{
            .seq = seq_, .ts_ms = ts_ms_, .len = kPayloadLen, .kind = kind
        };
        const auto encoded = sf::encode(frame, header, payload);
        if (!encoded) {
            throw std::runtime_error{std::string{sf::describe(encoded.error())}};
        }

        if (offset_ + *encoded > flash_.sector_size()) {
            // Кадр не ріжеться між секторами — переходимо на наступний.
            // Справжня черга стерла б його заздалегідь і лише
            // переконавшись, що це не сектор хвоста; тут витіснення нас
            // не цікавить.
            sector_ = (sector_ + 1) % flash_.sector_count();
            offset_ = 0;
            flash_.erase(sector_);
            valid_[sector_] = 0;
        }

        const std::size_t written = std::min(cut_at, *encoded);
        flash_.program(sector_ * flash_.sector_size() + offset_,
                       std::span{frame}.first(written));

        if (written == *encoded) {
            ++valid_[sector_];
        }
        offset_ += static_cast<std::uint32_t>(written);
        ++seq_;
        ts_ms_ += 20; // 50 Гц
    }

    [[nodiscard]] std::uint32_t valid_frames() const
    {
        return std::ranges::fold_left(valid_, 0u, std::plus<>{});
    }

    void set_valid(std::uint32_t sector, std::uint32_t frames) { valid_[sector] = frames; }

private:
    static constexpr std::uint64_t kEpochStart = 1735689600000ull; // 2025-01-01Z

    RamNor&                    flash_;
    std::vector<std::uint32_t> valid_; // очікуване, для звірки
    std::uint32_t              sector_{0};
    std::uint32_t              offset_{0};
    std::uint32_t              seq_{1};
    std::uint64_t              ts_ms_{kEpochStart};
};

// Заповнює кільце так, що воно робить повний оберт: голова опиняється
// в секторі 0, а хвіст — у секторі 1. Останній кадр за бажанням рветься.
void fill_wrapped(Writer& writer, std::uint32_t frames, bool tear_last)
{
    writer.reset();
    for (std::uint32_t i = 0; i < frames; ++i) {
        const auto kind = (i % 50 == 0) ? sf::Kind::Status : sf::Kind::Raw;
        if (tear_last && i + 1 == frames) {
            writer.append(kind, sf::kHeaderSize + 40);
        } else {
            writer.append(kind);
        }
    }
}

// --- звіт і звірка -------------------------------------------------------

int g_failures = 0;

void expect(bool condition, std::string_view what)
{
    if (!condition) {
        std::println("    ПОМИЛКА: {}", what);
        ++g_failures;
    }
}

void report(std::string_view title, const sf::QueueState& state)
{
    std::println("{}", title);
    if (state.empty) {
        std::println("    кільце порожнє, писати з сектора 0, seq = {}", state.next_seq);
        return;
    }
    std::println("    голова:  сектор {}, зсув {}, наступний seq {}",
                 state.head_sector, state.head_offset, state.next_seq);
    std::println("    хвіст:   сектор {}, найстаріший seq {}",
                 state.tail_sector, state.tail_seq);
    std::println("    кадрів:  {}, пошкоджених секторів {}, обірваний запис: {}",
                 state.valid_frames, state.damaged_sectors,
                 state.torn_tail ? "так" : "ні");
}

} // namespace

int main()
{
    RamNor flash{kSectorSize, kSectorCount};
    Writer writer{flash};

    // 1. Знеструмлення посеред запису після обороту кільця.
    fill_wrapped(writer, 150, true);
    auto state = sf::recover(flash);
    if (!state) {
        std::println("сканування не вдалося: збій читання за адресою {}", state.error().addr);
        return 1;
    }
    report("Сценарій 1: живлення зникло посеред кадру seq 150", *state);
    expect(!state->empty, "кільце мало містити дані");
    expect(state->torn_tail, "обірваний кадр мав бути помічений");
    expect(state->head_sector == 0, "голова мала лишитись у секторі 0");
    expect(state->tail_sector == 1, "хвіст мав вказувати на сектор 1");
    expect(state->next_seq == 150, "наступний кадр мав дістати номер 150");
    expect(state->valid_frames == writer.valid_frames(), "кількість кадрів не зійшлася");
    expect(state->head_offset % kFrameLen == 0,
           "голова мала стати рівно за останнім валідним кадром");

    // 2. Свіжий, повністю стертий носій.
    writer.reset();
    state = sf::recover(flash);
    if (!state) {
        std::println("сканування не вдалося: збій читання за адресою {}", state.error().addr);
        return 1;
    }
    report("\nСценарій 2: перший старт, носій стертий", *state);
    expect(state->empty, "кільце мало виявитись порожнім");
    expect(state->next_seq == 1, "нумерація мала початися з одиниці");
    expect(state->valid_frames == 0, "кадрів не мало бути взагалі");

    // 3. Деградована комірка посеред сектора. Кадр не проходить CRC, і
    //    все, що лежить у цьому секторі за ним, стає недосяжним: сканер
    //    не може відрізнити наступний запис від сміття минулого циклу.
    fill_wrapped(writer, 150, false);
    const auto victim = static_cast<std::uint32_t>(2 * kSectorSize + 5 * kFrameLen
                                                   + sf::kHeaderSize + 8);
    flash.disturb(victim, std::byte{0xF0});
    writer.set_valid(2, 5);

    state = sf::recover(flash);
    if (!state) {
        std::println("сканування не вдалося: збій читання за адресою {}", state.error().addr);
        return 1;
    }
    report("\nСценарій 3: биті комірки в шостому кадрі сектора 2", *state);
    expect(state->valid_frames == writer.valid_frames(),
           "після битого кадру хвіст сектора мав стати недосяжним");
    expect(state->head_sector == 0, "голова не мала зрушити з сектора 0");
    expect(!state->torn_tail, "голова була ціла, обірваного запису тут немає");

    std::println("\n{}", g_failures == 0 ? "усі перевірки пройдено"
                                         : "є розбіжності, див. вище");
    return g_failures == 0 ? 0 : 1;
}
