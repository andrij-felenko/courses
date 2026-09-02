#include <array>
#include <cstdint>
#include <print>
#include <span>

#include "flash_id.hpp"
#include "sfdp.hpp"
#include "simulated_flash.hpp"

namespace {

void print_raw(std::string_view label, std::span<const std::uint8_t> raw)
{
    std::print("{}:", label);
    for (std::uint8_t b : raw) {
        std::print(" {:02X}", b);
    }
    std::print("\n");
}

/* Так виглядає перша спокуса: викликати 0x9F на робочій частоті й повірити
   тому, що прийшло. */
void naive_probe(flash::SpiLink &link)
{
    const std::array<std::uint8_t, 1> cmd{flash::kCmdReadId};
    std::array<std::uint8_t, flash::kIdMaxBytes> raw{};
    flash::command(link, cmd, raw);

    std::print("— наївне опитування на {} Гц —\n", link.clock());
    print_raw("  сира відповідь", raw);
    const auto decoded = flash::decode(raw);
    std::print("  діагноз: {}\n\n",
               decoded ? std::string_view{"паспорт зчитано"} : flash::describe(decoded.error()));
}

void print_passport(const flash::Passport &p)
{
    print_raw("  сира відповідь", std::span{p.raw}.first(p.raw_len));
    std::print("  банк JEP106:     {}\n", p.bank);
    std::print("  виробник:        0x{:02X} — {}\n", p.manufacturer, p.vendor());
    std::print("  тип пам'яті:     0x{:02X}\n", p.memory_type);
    std::print("  код ємності:     0x{:02X}\n", p.capacity_code);
    std::print("  обсяг:           {} Б ({} Мбіт)\n", p.size_bytes, p.size_bytes / 131072);
    std::print("  сторінок по {}: {}\n", p.page_size, p.pages());
    std::print("  секторів по {}: {}\n", p.sector_size, p.sectors());
    std::print("  вихід із QPI:    {}\n",
               p.recovered_from_qpi ? "знадобився" : "не знадобився");
}

void print_parameters(const flash::Parameters &s)
{
    std::print("  ревізія:         JESD216, {}.{}, таблиця {} подвійних слів\n",
               s.major, s.minor, s.dwords);
    std::print("  адресація:       {} байти{}\n", s.address_bytes,
               s.four_byte_capable ? " (уміє й чотирибайтову)" : "");
    std::print("  щільність:       {} біт = {} Б\n", s.density_bits, s.density_bytes);
    std::print("  сторінка:        {} Б\n", s.page_size);
    if (s.read_1_4_4) {
        std::print("  швидке 1-4-4:    опкод 0x{:02X}, {} холостих тактів, {} тактів режиму\n",
                   s.read_1_4_4->opcode, s.read_1_4_4->dummy_clocks, s.read_1_4_4->mode_clocks);
    }
    if (s.read_1_1_4) {
        std::print("  швидке 1-1-4:    опкод 0x{:02X}, {} холостих тактів, {} тактів режиму\n",
                   s.read_1_1_4->opcode, s.read_1_1_4->dummy_clocks, s.read_1_1_4->mode_clocks);
    }
    for (std::size_t i = 0; i < s.erase_types.size(); ++i) {
        const auto &e = s.erase_types[i];
        std::print("  стирання {}:      {} Б опкодом 0x{:02X}, типово {} мс\n",
                   i + 1, e.size_bytes, e.opcode, e.typical.count());
    }
    std::print("  Quad Enable:     {}\n", flash::describe(s.quad_enable));
}

/* Перевірка самого розбору: відповідь із двома байтами продовження — виробник
   із третього банку JEP106, у нашій таблиці його немає, і це нормально. */
void continuation_selftest()
{
    const std::array<std::uint8_t, 6> answer{0x7F, 0x7F, 0x1F, 0x87, 0x18, 0xFF};
    std::print("— розбір банків продовження —\n");
    print_raw("  сира відповідь", answer);
    if (const auto p = flash::decode(answer)) {
        std::print("  банк {}, виробник 0x{:02X} ({}), обсяг {} Б\n\n",
                   p->bank, p->manufacturer, p->vendor(), p->size_bytes);
    } else {
        std::print("  діагноз: {}\n\n", flash::describe(p.error()));
    }
}

/* І окремо — чому bring-up роблять на зниженій частоті. */
void clock_limit_demo(flash::SpiLink &link)
{
    const std::array<std::uint8_t, 1> cmd{flash::kCmdReadId};
    std::array<std::uint8_t, 3> raw{};

    flash::ClockGuard fast{link, 80'000'000};
    flash::command(link, cmd, raw);
    std::print("— те саме опитування на {} Гц —\n", link.clock());
    print_raw("  сира відповідь", raw);
    std::print("  опкод 0x9F обмежений 33–50 МГц: биті такти читаються як нулі\n\n");
}

}  // namespace

int main()
{
    flash::SimulatedFlash chip;

    naive_probe(chip);

    std::print("— опитування за протоколом —\n");
    const auto passport = flash::identify(chip);
    if (!passport) {
        std::print("  ✖ {}\n", flash::describe(passport.error()));
        return 1;
    }
    std::print("  статус: паспорт зчитано\n");
    print_passport(*passport);

    std::print("\n— таблиця параметрів SFDP —\n");
    const auto params = flash::read_parameters(chip);
    if (!params) {
        std::print("  ✖ {}\n", flash::describe(params.error()));
        return 1;
    }
    print_parameters(*params);

    std::print("\n");
    clock_limit_demo(chip);
    continuation_selftest();

    /* Два незалежні джерела обсягу мусять зійтися. Розбіжність означає, що
       код ємності й таблиця параметрів описують різні кристали, — типова
       ознака перемаркованої мікросхеми. */
    std::print("— звірення джерел обсягу —\n");
    std::print("  код ємності 0x{:02X}: {} Б\n", passport->capacity_code, passport->size_bytes);
    std::print("  щільність SFDP:   {} Б\n", params->density_bytes);
    if (passport->size_bytes != params->density_bytes) {
        std::print("  ✖ джерела розходяться: кристал перемаркований або відповідь спотворена\n");
        return 1;
    }
    std::print("  ✓ джерела збігаються, геометрію можна брати в роботу\n");
    return 0;
}
