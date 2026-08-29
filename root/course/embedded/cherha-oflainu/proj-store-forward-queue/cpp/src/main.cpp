// main.cpp — заняття на моделі NOR: чотири сцени життя черги.
//
//   1. Чистий кристал і перший старт.
//   2. Зв'язку немає: кільце заповнюється, низький пріоритет
//      відкидається, високий витісняє найстаріший сектор.
//   3. Живлення зникає посеред запису кадру; після подачі напруги
//      черга сама знаходить голову, хвіст і наступний номер.
//   4. Зв'язок повернувся: свіжі кадри летять живою колією, історія
//      вивантажується пачками, хвіст рухається лише по квитанціях.
//
// Збирати: c++ -std=c++23 -I include src/main.cpp -o sfq-demo
#include <array>
#include <cstdint>
#include <format>
#include <iostream>
#include <span>
#include <string_view>

#include "sfq/batch.hpp"
#include "sfq/queue.hpp"
#include "sfq/ram_nor.hpp"

namespace {

constexpr std::size_t kSectors = 16;
using Flash = sfq::RamNorFlash<kSectors>;

// Годинник вузла.
std::uint64_t g_now_ms = 1000;

std::uint64_t tick(std::uint32_t ms)
{
    g_now_ms += ms;
    return g_now_ms;
}

// Замок-сторож: на хості потік один, тож він нічого не блокує, зате
// ловить вкладений вхід — тобто ту саму помилку, через яку на живій
// RTOS черга колись прочитала б кадр посеред власного запису.
// На платі сюди підставляють обгортку над м'ютексом FreeRTOS.
class DebugLock {
public:
    void lock() noexcept
    {
        if (depth_++ != 0) {
            std::cout << "!! повторний вхід у чергу: замок не тримає\n";
        }
    }
    void unlock() noexcept { --depth_; }

private:
    int depth_{0};
};

using Queue = sfq::StoreForwardQueue<Flash, DebugLock>;

// Радіоканал: детермінована псевдовипадковість замість справжніх втрат.
std::uint32_t g_rng = 0x2A3B4C5Du;

std::uint32_t rnd()
{
    g_rng = g_rng * 1664525u + 1013904223u;
    return g_rng >> 16;
}

bool link_delivers()
{
    return (rnd() % 100) < 85;  // 15% кадрів не доїжджає
}

// Навантаження кадру: текстовий рядок змінної довжини — черзі байдуже,
// що всередині, а на екрані видно, що саме поїхало.
class SampleBuffer {
public:
    std::span<const std::byte> make(std::uint32_t n)
    {
        const auto result = std::format_to_n(chars_.begin(), chars_.size(),
                                             "t={} vbat={}mV temp={}.{}C n={}", g_now_ms,
                                             3600 + n % 40, 20 + n % 7, n % 10, n);
        const auto used = static_cast<std::size_t>(result.out - chars_.begin());
        return std::as_bytes(std::span{chars_.data(), used});
    }

private:
    std::array<char, 96> chars_{};
};

void print_state(const Queue& queue, std::string_view label)
{
    std::cout << std::format(
        "  {:<22} голова {:2}:{:<5} хвіст {:2}:{:<5} курсор {:2}:{:<5}  наступний seq {}\n", label,
        queue.head().sector, queue.head().offset, queue.tail().sector, queue.tail().offset,
        queue.drain_cursor().sector, queue.drain_cursor().offset, queue.next_seq());
}

void print_stats(const Queue& queue, const Flash& flash)
{
    const auto& s = queue.stats();
    std::cout << std::format("  записано {} кадрів ({} Б) · стерто секторів {} · витіснено {}\n",
                             s.records_written, s.bytes_written, s.sectors_erased,
                             s.sectors_evicted);
    std::cout << std::format("  відмовлено низькому пріоритету {} · битих кадрів {} · відновлено {}\n",
                             s.dropped_full, s.corrupt_records, s.recovered_records);
    std::cout << std::format(
        "  помилок носія {} · історія пропустила квитоване живцем {} · діапазонів втрачено {}\n",
        s.flash_errors, s.skipped_live_acked, queue.acks().dropped());
    std::cout << std::format("  модель носія: стирань {}, операцій програмування {}\n",
                             flash.erase_count(), flash.program_count());
}

// --- сцени ---

void scene_offline(Queue& queue)
{
    SampleBuffer sample;
    std::uint32_t stored = 0;
    std::uint32_t refused = 0;
    std::uint32_t n = 0;

    std::cout << "\n== 2. Зв'язку немає: пишемо, поки є куди ==\n";

    // 50 Гц телеметрії, раз на секунду статус, зрідка аварія.
    for (std::uint32_t i = 0; i < 4000 && refused < 40; ++i) {
        auto type = sfq::RecordType::Telemetry;
        auto priority = sfq::Priority::Low;

        if (i % 50 == 0) {
            type = sfq::RecordType::Status;
            priority = sfq::Priority::Normal;
        }
        if (i % 613 == 0) {
            type = sfq::RecordType::Alarm;
            priority = sfq::Priority::High;
        }

        const auto pushed = queue.push(type, priority, tick(20), sample.make(n++));
        if (pushed) {
            ++stored;
        } else if (pushed.error() == sfq::QueueError::Full) {
            ++refused;
        } else {
            std::cout << "  носій відмовив\n";
            break;
        }
    }

    std::cout << std::format("  збережено {} кадрів, відкинуто низькопріоритетних {}\n", stored,
                             refused);
    print_state(queue, "кільце повне");
}

void scene_power_loss(Queue& queue, Flash& flash)
{
    SampleBuffer sample;

    std::cout << "\n== 3. Знеструмлення посеред кадру ==\n";

    // Аварійний кадр піде у флеш, але напруга просяде після 24 байтів:
    // заголовок ляже, навантаження й CRC — ні.
    flash.cut_power_after(24);
    const auto pushed =
        queue.push(sfq::RecordType::Alarm, sfq::Priority::High, tick(20), sample.make(99999));

    std::cout << std::format("  push під час просідання напруги -> {}\n",
                             pushed ? "несподівано вдався" : "помилка носія, як і мало бути");

    const std::uint32_t seq_before = queue.next_seq();

    flash.power_up();
    std::cout << "  живлення подано, вузол перезавантажився\n";

    if (!queue.mount()) {
        std::cout << "  !! черга не піднялася\n";
        return;
    }

    print_state(queue, "після відновлення");
    std::cout << std::format(
        "  номер до аварії {}, після сканування {} (обірваний кадр номера не з'їв)\n", seq_before,
        queue.next_seq());
}

void scene_link_back(Queue& queue)
{
    static sfq::DrainBatch batch;  // 1 КіБ арени — на стеку задачі не місце
    SampleBuffer sample;
    std::uint32_t fresh = 0;
    std::uint32_t live_acked = 0;
    std::uint32_t history_sent = 0;

    std::cout << "\n== 4. Зв'язок повернувся: дві колії ==\n";

    for (std::uint32_t round = 1; round <= 400; ++round) {
        // Жива колія: свіжий кадр лягає у флеш і одразу йде в ефір.
        if (round % 2 == 0) {
            if (const auto seq = queue.push(sfq::RecordType::Telemetry, sfq::Priority::Normal,
                                            tick(20), sample.make(500000 + fresh))) {
                ++fresh;
                if (link_delivers()) {
                    queue.ack_live(*seq);
                    ++live_acked;
                }
                // Квитанція не прийшла — кадр нікуди не дівся: історія
                // дійде до нього сама й відправить удруге.
            }
        }

        // Колія історії: пачка старих кадрів від курсора вивантаження.
        if (!queue.drain(batch)) {
            if (queue.empty()) {
                break;
            }
            continue;
        }

        if (link_delivers()) {
            history_sent += static_cast<std::uint32_t>(batch.size());
            queue.commit_ack(batch.last_seq());
        } else {
            // Пачка загубилась — курсор назад на хвіст, поїде знову.
            queue.drain_rewind();
        }

        if (round % 40 == 0) {
            std::cout << std::format("  раунд {:3}: пачка {} кадрів [{}..{}], у черзі {} Б\n", round,
                                     batch.size(), batch.first_seq(), batch.last_seq(),
                                     queue.bytes_pending());
        }
    }

    std::cout << std::format(
        "  свіжих кадрів {} (з них квитовано живцем {}), історією віддано {}\n", fresh, live_acked,
        history_sent);
    print_state(queue, "після вивантаження");
}

}  // namespace

int main()
{
    static Flash flash;  // 64 КіБ моделі кристала — не на стеку
    static Queue queue{flash, Queue::Config{.base_addr = 0, .sector_count = kSectors}};

    std::cout << "== 1. Чистий кристал ==\n";
    flash.bulk_erase();

    if (!queue.mount()) {
        std::cout << "черга не піднялася\n";
        return 1;
    }
    print_state(queue, "порожня черга");

    scene_offline(queue);
    scene_power_loss(queue, flash);
    scene_link_back(queue);

    std::cout << "\n== Підсумок ==\n";
    print_stats(queue, flash);
    return 0;
}
