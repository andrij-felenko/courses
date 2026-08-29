// Прогін аудиту бюджетів на двох ревізіях автономного реєстратора.
//
// Ревізія A — плата зі столу: лінійний стабілізатор 12 В → 3.3 В, буфер
// 100 мкФ, 512 КБ Flash під образ 380 КБ, цикл передавання 60 с.
// Ревізія B — та сама схема після перерахунку бюджетів: імпульсний
// перетворювач, більший буфер, вдвічі більший Flash, довший цикл.

#include "budget/monitor.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <format>
#include <iostream>
#include <memory_resource>
#include <new>
#include <span>
#include <string_view>
#include <vector>

namespace {

using namespace budget;
using namespace std::chrono_literals;

constexpr std::size_t kKiB = 1024;

// Профіль струму фаз циклу, мікроампери.
constexpr EnergyLedger::Profile kProfile{
    15u,      // 15 мкА глибокого сну
    8500u,    // 8.5 мА опитування по I2C
    22000u,   // 22 мА обробки та шифрування
    140000u   // 140 мА сплеску радіопередачі
};

struct Revision {
    std::string_view          title;
    double                    regulator_loss_w;   // теплові втрати стабілізатора
    double                    bulk_f;             // буферна ємність шини
    std::size_t               radio_stack_bytes;  // стек задачі радіо
    bool                      heap_churn;         // безладні виділення пам'яті
    std::uint32_t             flash_total_kib;
    std::chrono::microseconds sleep;              // сон між сеансами
    std::chrono::microseconds section_deadline;   // термін критичної секції
};

// Імітація зайнятої глибини стеку: задача затирає шаблон згори вниз.
void burn_stack(std::span<std::uint32_t> region, std::size_t used_bytes)
{
    const std::size_t used_words =
        std::min(region.size(), (used_bytes + sizeof(std::uint32_t) - 1) /
                                    sizeof(std::uint32_t));
    std::ranges::fill(region.last(used_words), 0xEEEEEEEEu);
}

// Корисне навантаження критичної секції: згортка Флетчера над буфером.
std::uint32_t fletcher32(std::span<const std::byte> data) noexcept
{
    std::uint32_t sum1 = 0xFFFFu;
    std::uint32_t sum2 = 0xFFFFu;

    for (std::size_t i = 0; i + 1 < data.size(); i += 2) {
        const auto word = static_cast<std::uint32_t>(std::to_integer<int>(data[i])) |
                          (static_cast<std::uint32_t>(std::to_integer<int>(data[i + 1])) << 8);
        sum1 = (sum1 + word) % 0xFFFFu;
        sum2 = (sum2 + sum1) % 0xFFFFu;
    }
    return (sum2 << 16) | sum1;
}

// Ревізія A виділяє й звільняє пакети вроздріб тижнями: вільного лишається
// чимало, але суцільним він уже не буває.
void churn_heap(FragmentAwareResource& heap, std::vector<void*>& held)
{
    std::vector<void*> blocks;
    try {
        while (true) {
            blocks.push_back(heap.allocate(496));
        }
    } catch (const std::bad_alloc&) {
        // Арену вичерпано — саме цього ми й домагалися.
    }

    for (std::size_t i = 0; i < blocks.size(); ++i) {
        if (i % 2 == 0) {
            heap.deallocate(blocks[i], 496);
        } else {
            held.push_back(blocks[i]);
        }
    }
}

Action audit_revision(const Revision& rev)
{
    std::cout << std::format("=== {} ===\n", rev.title);

    // 1. Стеки задач.
    std::array<std::uint32_t, 512> stack_radio{};
    std::array<std::uint32_t, 128> stack_sense{};
    std::array<std::uint32_t, 128> stack_log{};

    const auto radio_region =
        std::span{stack_radio}.first(rev.radio_stack_bytes / sizeof(std::uint32_t));

    std::vector<StackGuard> guards;
    guards.reserve(3);
    guards.emplace_back("радіо", radio_region, 256);
    guards.emplace_back("сенсори", std::span{stack_sense}, 128);
    guards.emplace_back("журнал", std::span{stack_log}, 128);

    // Рукостискання TLS з'їдає 900 Б незалежно від ревізії плати.
    burn_stack(radio_region, 900);
    burn_stack(stack_sense, 220);
    burn_stack(stack_log, 180);

    // 2. Куча.
    std::array<std::byte, 16 * kKiB> arena{};
    FragmentAwareResource heap{arena};

    std::vector<void*>                     raw_blocks;
    std::vector<std::pmr::vector<std::byte>> buffers;

    if (rev.heap_churn) {
        churn_heap(heap, raw_blocks);
    } else {
        // Буфери виділені один раз на старті — розривів не буде взагалі.
        buffers.reserve(3);
        for (int i = 0; i < 3; ++i) {
            buffers.emplace_back(1500, std::byte{0}, &heap);
        }
    }

    // 3. Заряд за фазами: п'ять повних циклів.
    EnergyLedger energy{kProfile};
    for (int cycle = 0; cycle < 5; ++cycle) {
        energy.account(Phase::Sleep, rev.sleep);
        energy.account(Phase::Sense, 300ms);
        energy.account(Phase::Process, 100ms);
        energy.account(Phase::Transmit, 400ms);
    }

    // 4. Шина живлення: сплеск 350 мА протягом 120 мкс, ESR буфера 50 мОм.
    RailMonitor rail{RailMonitor::Limits{.nominal_v = 3.3, .warn_v = 3.0, .bor_v = 2.9}};

    const double droop = RailMonitor::estimated_droop_v(0.350, 0.050, rev.bulk_f, 120us);
    const double under_load = std::max(0.0, rail.limits().nominal_v - droop);
    std::cout << std::format(
        "  розрахункове просідання на сплеску: {:.3f} В → {:.3f} В на шині "
        "(BOR {:.3f} В)\n",
        droop, under_load, rail.limits().bor_v);

    rail.sample(rail.limits().nominal_v);
    rail.sample(under_load);
    rail.sample(3.15);

    // 5. Тепло: усередині герметичного корпусу під сонцем 75 °C.
    ThermalModel thermal{ThermalModel::Limits{.tj_max_c       = 125.0,
                                              .warn_margin_c  = 15.0,
                                              .hysteresis_c   = 5.0,
                                              .rth_ja_c_per_w = 200.0}};
    constexpr double kAmbient = 75.0;
    std::cout << std::format(
        "  тепловий стелаж корпусу: {:.3f} Вт, тобто {:.1f} мА при перепаді "
        "8.7 В; вузол розсіює {:.3f} Вт\n",
        thermal.max_power(kAmbient), thermal.ldo_max_current(kAmbient, 8.7) * 1000.0,
        rev.regulator_loss_w);
    thermal.sample(kAmbient, rev.regulator_loss_w);

    // 6. Критичні секції.
    std::array<std::byte, 4 * kKiB> payload{};
    for (std::size_t i = 0; i < payload.size(); ++i) {
        payload[i] = static_cast<std::byte>(i * 31 + 7);
    }

    std::vector<SectionBudget> sections;
    sections.reserve(2);
    sections.emplace_back("підпис пакета", rev.section_deadline);
    sections.emplace_back("запис у журнал", 20ms);

    volatile std::uint32_t sink = 0;
    for (int run = 0; run < 8; ++run) {
        {
            const auto scope = sections[0].measure();
            sink = sink ^ fletcher32(payload);
        }
        {
            const auto scope = sections[1].measure();
            sink = sink ^ fletcher32(std::span{payload}.first(256));
        }
    }

    const BudgetMonitor monitor{
        BudgetMonitor::Sources{
            .stacks   = guards,
            .heap     = &heap,
            .rail     = &rail,
            .thermal  = &thermal,
            .energy   = &energy,
            .sections = sections,
            .flash = FlashLayout{.total_bytes      = static_cast<std::uint32_t>(
                                     rev.flash_total_kib * kKiB),
                                 .sector_bytes     = 2 * kKiB,
                                 .bootloader_bytes = 32 * kKiB,
                                 .nvs_bytes        = 32 * kKiB,
                                 .image_bytes      = 380 * kKiB}},
        BudgetMonitor::Limits{
            .heap_min_free    = 8 * kKiB,
            .heap_min_largest = 2 * kKiB, // найтовстіший мережевий буфер
            .battery_mah      = 2000.0,   // літієвий елемент 2000 мА·год
            .required_life    = std::chrono::hours{8760}}};

    const auto report = monitor.run();
    std::cout << to_text(report) << '\n';

    // Сира пам'ять ревізії A повертається арені перед виходом з області.
    for (void* block : raw_blocks) {
        heap.deallocate(block, 496);
    }

    return report.action;
}

} // namespace

int main()
{
    const std::array<Revision, 2> revisions{
        Revision{.title             = "Ревізія A: LDO, 512 КБ Flash, цикл 60 с",
                 .regulator_loss_w  = 0.870, // (12 - 3.3) В * 100 мА
                 .bulk_f            = 100e-6,
                 .radio_stack_bytes = 1024,
                 .heap_churn        = true,
                 .flash_total_kib   = 512,
                 .sleep             = 59'200ms,
                 .section_deadline  = 5us},
        Revision{.title             = "Ревізія B: Buck 92 %, 1 МБ Flash, цикл 10 хв",
                 .regulator_loss_w  = 0.029, // втрати імпульсного перетворювача
                 .bulk_f            = 470e-6,
                 .radio_stack_bytes = 2048,
                 .heap_churn        = false,
                 .flash_total_kib   = 1024,
                 .sleep             = 599'200ms,
                 .section_deadline  = 5ms}};

    Action final_action = Action::Run;
    for (const Revision& revision : revisions) {
        final_action = audit_revision(revision);
    }

    // Плата, яка після аудиту не виходить у штатний режим, у серію не йде.
    return (final_action == Action::Run) ? 0 : 1;
}
