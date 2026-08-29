// Прошивка стенда: серія з 256 оптичних спалахів, вимір інтервалу «спалах ->
// поява плями на екрані», зведення по вибірці у послідовний порт.
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <random>
#include <span>
#include <string_view>

#include "board.hpp"
#include "rig.hpp"
#include "statistics.hpp"

namespace {

constexpr std::size_t kTrials = 256;
// Стільки втрачених кадрів поспіль означає, що тракт мертвий, а не повільний.
constexpr std::size_t kGiveUpStreak = 16;

void print_trial(std::size_t index, std::optional<board::Microseconds> result) noexcept
{
    board::print("#");
    board::print(static_cast<std::uint32_t>(index + 1));
    if (result) {
        board::print("  ");
        board::print(*result);
        board::print(" мс\n");
    } else {
        board::print("  ВТРАЧЕНО КАДР\n");
    }
}

void print_line(std::string_view label, board::Microseconds value) noexcept
{
    board::print(label);
    board::print(value);
    board::print(" мс\n");
}

void print_report(const std::optional<latency::Summary> &summary, std::size_t lost) noexcept
{
    board::print("\n--- Бюджет затримки тракту ---\n");

    if (!summary) {
        board::print("Втрачено:  ");
        board::print(static_cast<std::uint32_t>(lost));
        board::print("\nЖодного відгуку. Перевірте поріг компаратора, засвітку\n"
                     "фотодіода та наявність картинки на екрані.\n");
        return;
    }

    board::print("Вимірів:   ");
    board::print(static_cast<std::uint32_t>(summary->count));
    board::print(" з ");
    board::print(static_cast<std::uint32_t>(kTrials));
    board::print("\nВтрачено:  ");
    board::print(static_cast<std::uint32_t>(summary->lost));
    board::print("\n");

    print_line("Мінімум:   ", summary->min);
    print_line("Медіана:   ", summary->p50);
    print_line("Середнє:   ", summary->mean);
    print_line("P95:       ", summary->p95);
    print_line("P99:       ", summary->p99);
    print_line("Максимум:  ", summary->max);
    print_line("Джитер:    ", summary->jitter);

    // Втрати самі по собі затримки не міряють, але без них зведення бреше:
    // тракт, що загубив кожен десятий кадр, має чудову медіану й непридатне
    // керування.
    if (summary->lost * 10u > summary->count + summary->lost) {
        board::print("УВАГА: втрачено понад 10% кадрів — зведення не характеризує тракт.\n");
    }
}

} // namespace

int main()
{
    board::init();

    board::print("\nСтенд вимірювання затримки: серія з ");
    board::print(static_cast<std::uint32_t>(kTrials));
    board::print(" спалахів\n");

    std::array<board::Microseconds, kTrials> samples{};
    std::size_t count = 0;
    std::size_t lost = 0;
    std::size_t lost_streak = 0;

    // Зерно беремо з часової бази: між подачею живлення й першим спалахом
    // завжди лежить різна кількість мікросекунд.
    std::minstd_rand rng{board::now().count() | 1u};
    // Пауза між випробуваннями випадкова: фіксована рано чи пізно ляже в
    // резонанс із кадровою розгорткою камери, і всі 256 спалахів потраплять
    // в одну фазу кадру — вибірка вийде красива й брехлива.
    std::uniform_int_distribution<std::uint32_t> cooldown{80000, 160000};

    for (std::size_t i = 0; i < kTrials; ++i) {
        const auto result = latency::rig().run_trial();

        if (result) {
            samples[count++] = *result;
            lost_streak = 0;
        } else {
            ++lost;
            ++lost_streak;
        }

        // Друкуємо лише поза вікном виміру: один символ на 115200 бод — це
        // 87 мкс блокувального очікування, і вони лягли б у сам інтервал.
        print_trial(i, result);

        if (lost_streak >= kGiveUpStreak) {
            board::print("\nПоспіль втрачено ");
            board::print(static_cast<std::uint32_t>(lost_streak));
            board::print(" кадрів — серію обірвано.\n");
            break;
        }

        board::wait(board::Microseconds{cooldown(rng)});
    }

    const auto summary = latency::analyse(std::span{samples}.first(count), lost);
    print_report(summary, lost);

    // Прошивка стенда нікуди не повертається: результат має лишитися на екрані
    // термінала, а світлодіод — погашеним.
    board::halt();
}
