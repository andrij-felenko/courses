#include "sfdp.hpp"

#include <algorithm>

namespace flash {
namespace {

/* Читання таблиці параметрів: опкод, три байти адреси всередині SFDP-ROM
   і обов'язковий холостий такт перед даними. */
void read_at(SpiLink &link, std::uint32_t addr, std::span<std::uint8_t> dst)
{
    const std::array<std::uint8_t, 5> cmd{
        kCmdReadSfdp,
        static_cast<std::uint8_t>(addr >> 16),
        static_cast<std::uint8_t>(addr >> 8),
        static_cast<std::uint8_t>(addr),
        0x00  /* dummy byte */
    };
    std::ranges::fill(dst, std::uint8_t{0});
    command(link, cmd, dst);
}

std::uint32_t le32(std::span<const std::uint8_t> b)
{
    return static_cast<std::uint32_t>(b[0]) | (static_cast<std::uint32_t>(b[1]) << 8) |
           (static_cast<std::uint32_t>(b[2]) << 16) | (static_cast<std::uint32_t>(b[3]) << 24);
}

/* Часи стирання в DWORD10 упаковані по 7 бітів на тип: п'ять бітів лічильника
   й два біти одиниці виміру. Час = (лічильник + 1) × одиниця. */
std::chrono::milliseconds erase_time(std::uint32_t dword10, std::size_t index)
{
    constexpr std::array<std::uint32_t, 4> kUnitMs{1, 16, 128, 1000};
    const std::uint32_t field = (dword10 >> (4 + 7 * index)) & 0x7FU;
    return std::chrono::milliseconds{((field & 0x1FU) + 1) * kUnitMs[(field >> 5) & 0x3U]};
}

}  // namespace

std::string_view describe(SfdpError error) noexcept
{
    switch (error) {
    case SfdpError::BadSignature: return "сигнатури SFDP немає: кристал стандарту не підтримує";
    case SfdpError::NoBasicTable: return "базової таблиці параметрів у заголовках немає";
    case SfdpError::Truncated:    return "таблиця коротша за обов'язкові поля";
    }
    return "невідомий стан";
}

std::string_view describe(QuadEnable scheme) noexcept
{
    switch (scheme) {
    case QuadEnable::None:           return "біта QE немає: чотирилінійні команди вмикаються самим опкодом";
    case QuadEnable::Sr2Bit1Write01: return "QE — біт 1 у SR2, запис командою 0x01 двома байтами";
    case QuadEnable::Sr1Bit6Write01: return "QE — біт 6 у SR1, запис командою 0x01 одним байтом";
    case QuadEnable::Sr2Bit7Cmd3E:   return "QE — біт 7 у SR2, читання 0x3F, запис 0x3E";
    case QuadEnable::Sr2Bit1Read35:  return "QE — біт 1 у SR2, читання 0x35, запис 0x01 двома байтами";
    case QuadEnable::Sr2Bit1Write31: return "QE — біт 1 у SR2, читання 0x35, запис 0x31 одним байтом";
    case QuadEnable::Unknown:        break;
    }
    return "схема QE нестандартна або таблиця її не оголошує";
}

std::expected<Parameters, SfdpError> read_parameters(SpiLink &link)
{
    std::array<std::uint8_t, 8> header{};
    read_at(link, 0, header);
    if (header[0] != 'S' || header[1] != 'F' || header[2] != 'D' || header[3] != 'P') {
        return std::unexpected{SfdpError::BadSignature};
    }

    Parameters params;
    params.minor = header[4];
    params.major = header[5];

    /* Байт 6 — кількість заголовків параметрів мінус один. Шукаємо базову
       таблицю: молодший байт ідентифікатора 0x00, старший 0xFF. */
    const unsigned headers = static_cast<unsigned>(header[6]) + 1U;
    std::uint32_t table_addr = 0;
    std::size_t   table_dwords = 0;
    for (unsigned i = 0; i < headers; ++i) {
        std::array<std::uint8_t, 8> ph{};
        read_at(link, 8U + 8U * i, ph);
        if (ph[0] == 0x00 && ph[7] == 0xFF) {
            table_dwords = ph[3];
            table_addr = static_cast<std::uint32_t>(ph[4]) |
                         (static_cast<std::uint32_t>(ph[5]) << 8) |
                         (static_cast<std::uint32_t>(ph[6]) << 16);
            break;
        }
    }
    if (table_dwords == 0) {
        return std::unexpected{SfdpError::NoBasicTable};
    }
    /* Типи стирання лежать у DWORD8 і DWORD9 — коротша таблиця не годиться. */
    if (table_dwords < 9) {
        return std::unexpected{SfdpError::Truncated};
    }

    const std::size_t count = std::min(table_dwords, kSfdpMaxDwords);
    std::array<std::uint8_t, kSfdpMaxDwords * 4> bytes{};
    read_at(link, table_addr, std::span{bytes}.first(count * 4));

    std::array<std::uint32_t, kSfdpMaxDwords> dw{};
    for (std::size_t i = 0; i < count; ++i) {
        dw[i] = le32(std::span{bytes}.subspan(i * 4, 4));
    }
    params.dwords = count;

    /* DWORD1: скільки байтів адреси й чи оголошено швидкі чотирилінійні читання. */
    switch ((dw[0] >> 17) & 0x3U) {
    case 0: params.address_bytes = 3; break;
    case 1: params.address_bytes = 3; params.four_byte_capable = true; break;
    default: params.address_bytes = 4; params.four_byte_capable = true; break;
    }

    /* DWORD2: щільність. Старший біт скинуто — значення це «кількість бітів
       мінус один», піднято — це степінь двійки в бітах (кристали від 4 Гбіт). */
    params.density_bits = (dw[1] & 0x8000'0000U) == 0
                              ? static_cast<std::uint64_t>(dw[1]) + 1
                              : std::uint64_t{1} << (dw[1] & 0x7FFF'FFFFU);
    params.density_bytes = params.density_bits / 8;

    /* DWORD3: опкоди й холості такти обох чотирилінійних читань. */
    if ((dw[0] & (1U << 21)) != 0) {
        params.read_1_4_4 = FastRead{static_cast<std::uint8_t>((dw[2] >> 8) & 0xFFU),
                                     static_cast<std::uint8_t>(dw[2] & 0x1FU),
                                     static_cast<std::uint8_t>((dw[2] >> 5) & 0x7U)};
    }
    if ((dw[0] & (1U << 22)) != 0) {
        params.read_1_1_4 = FastRead{static_cast<std::uint8_t>((dw[2] >> 24) & 0xFFU),
                                     static_cast<std::uint8_t>((dw[2] >> 16) & 0x1FU),
                                     static_cast<std::uint8_t>((dw[2] >> 21) & 0x7U)};
    }

    /* DWORD8 і DWORD9: чотири типи стирання, розмір як степінь двійки. */
    const std::array<std::uint8_t, 4> sizes{
        static_cast<std::uint8_t>(dw[7] & 0xFFU), static_cast<std::uint8_t>((dw[7] >> 16) & 0xFFU),
        static_cast<std::uint8_t>(dw[8] & 0xFFU), static_cast<std::uint8_t>((dw[8] >> 16) & 0xFFU)};
    const std::array<std::uint8_t, 4> opcodes{
        static_cast<std::uint8_t>((dw[7] >> 8) & 0xFFU), static_cast<std::uint8_t>((dw[7] >> 24) & 0xFFU),
        static_cast<std::uint8_t>((dw[8] >> 8) & 0xFFU), static_cast<std::uint8_t>((dw[8] >> 24) & 0xFFU)};
    for (std::size_t i = 0; i < sizes.size(); ++i) {
        if (sizes[i] == 0) {
            continue;  /* нульовий степінь означає «типу немає» */
        }
        params.erase_types.push_back(EraseType{
            opcodes[i],
            std::uint32_t{1} << sizes[i],
            count >= 10 ? erase_time(dw[9], i) : std::chrono::milliseconds{0}});
    }

    /* DWORD11: розмір сторінки програмування як степінь двійки. */
    if (count >= 11) {
        params.page_size = std::uint32_t{1} << ((dw[10] >> 4) & 0xFU);
    }
    /* DWORD15: поле QER. */
    if (count >= 15) {
        const auto qer = static_cast<std::uint8_t>((dw[14] >> 20) & 0x7U);
        params.quad_enable = qer <= 5 ? static_cast<QuadEnable>(qer) : QuadEnable::Unknown;
    }
    return params;
}

}  // namespace flash
