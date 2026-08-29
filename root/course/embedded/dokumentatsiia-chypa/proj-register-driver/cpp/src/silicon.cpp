#include "usart/silicon.hpp"

#include "mmio/register.hpp"
#include "usart/registers.hpp"

namespace usart {
namespace {

/* Регістр ідентифікації кремнію: DEV_ID [11:0], REV_ID [31:16] */
struct DbgMcuBlock {
    mmio::Register<std::uint32_t> idcode; // +0x00
};

static_assert(sizeof(DbgMcuBlock) == 4, "IDCODE — одне 32-бітне слово");

[[nodiscard]] std::uint32_t idcode() noexcept
{
    return mmio::block<DbgMcuBlock>(dbgmcu_address).idcode.load();
}

} // namespace

std::uint16_t device_id() noexcept
{
    return static_cast<std::uint16_t>(idcode() & 0x0FFFu);
}

Revision revision() noexcept
{
    const std::uint32_t id = idcode();

    if ((id & 0x0FFFu) != expected_device_id) {
        return Revision::unknown;
    }

    switch (id >> 16) {
    case static_cast<std::uint32_t>(Revision::rev_a):
        return Revision::rev_a;
    case static_cast<std::uint32_t>(Revision::rev_b):
        return Revision::rev_b;
    default:
        /* Ревізія, якої не було на час написання прошивки: її Errata ми
         * не читали, тож поводимося з нею як з невідомою. */
        return Revision::unknown;
    }
}

} // namespace usart
