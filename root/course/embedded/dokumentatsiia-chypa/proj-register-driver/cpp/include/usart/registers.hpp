/* Карта регістрів USART, знята з Reference Manual, — з типами замість
 * голих чисел. Логіки тут немає, лише таблиця й перевірки її вірності.
 */
#pragma once

#include <cstddef>
#include <cstdint>

#include "mmio/register.hpp"

namespace usart {

/* CR1 — керування блоком */
enum class Cr1 : std::uint32_t {
    none   = 0,
    ue     = 1u << 0, // дозвіл роботи блока
    te     = 1u << 3, // дозвіл передавача
    rxneie = 1u << 5, // дозвіл переривання по прийому
};

/* ISR — стан. Читається, не пишеться: гасять прапорці через ICR. */
enum class Isr : std::uint32_t {
    none = 0,
    pe   = 1u << 0, // помилка парності
    fe   = 1u << 1, // помилка кадру
    nf   = 1u << 2, // шум у лінії
    ore  = 1u << 3, // переповнення приймача
    rxne = 1u << 5, // у RDR лежить прийнятий байт
    tc   = 1u << 6, // передачу завершено
    txe  = 1u << 7, // буфер передачі порожній
    errors = pe | fe | nf | ore,
};

/* ICR — гасіння. Запис «1» скидає названий тригер, «0» не робить нічого. */
enum class Icr : std::uint32_t {
    none  = 0,
    pecf  = 1u << 0,
    fecf  = 1u << 1,
    ncf   = 1u << 2,
    orecf = 1u << 3,
    tccf  = 1u << 6,
    errors = pecf | fecf | ncf | orecf,
};

} // namespace usart

/* Три різні набори бітів — три різні типи. Записати Isr::tc у регістр ICR
 * тепер неможливо: код просто не збереться. */
template <> struct mmio::is_flag_enum<usart::Cr1> : std::true_type {};
template <> struct mmio::is_flag_enum<usart::Isr> : std::true_type {};
template <> struct mmio::is_flag_enum<usart::Icr> : std::true_type {};

namespace usart {

/* Бітові операції живуть у mmio й самі сюди не приїдуть: асоційований
 * простір імен у Isr — це usart, а не mmio. Вносимо їх явно. */
using mmio::any;
using mmio::raw;
using mmio::operator|;
using mmio::operator&;
using mmio::operator|=;

/* Блок USART у карті пам'яті. Кожне поле — 4 байти, дірок немає, порядок
 * і зміщення строго за таблицею Reference Manual. */
struct Block {
    mmio::Register<Cr1>           cr1;  // +0x00
    mmio::Register<std::uint32_t> cr2;  // +0x04
    mmio::Register<std::uint32_t> cr3;  // +0x08
    mmio::Register<std::uint32_t> brr;  // +0x0C дільник тактової частоти
    mmio::Register<std::uint32_t> gtpr; // +0x10
    mmio::Register<std::uint32_t> rtor; // +0x14
    mmio::Register<std::uint32_t> rqr;  // +0x18
    mmio::Register<Isr>           isr;  // +0x1C
    mmio::Register<Icr>           icr;  // +0x20
    mmio::Register<std::uint32_t> rdr;  // +0x24 прийнятий байт
    mmio::Register<std::uint32_t> tdr;  // +0x28 байт на відправку
};

/* Структуру звіряє з документацією компілятор, а не уважність автора */
static_assert(offsetof(Block, cr1) == 0x00, "CR1 має стояти за +0x00");
static_assert(offsetof(Block, brr) == 0x0C, "BRR має стояти за +0x0C");
static_assert(offsetof(Block, isr) == 0x1C, "ISR має стояти за +0x1C");
static_assert(offsetof(Block, icr) == 0x20, "ICR має стояти за +0x20");
static_assert(offsetof(Block, rdr) == 0x24, "RDR має стояти за +0x24");
static_assert(offsetof(Block, tdr) == 0x28, "TDR має стояти за +0x28");
static_assert(sizeof(Block) == 0x2C, "блок USART займає 0x2C байтів");
static_assert(alignof(Block) == 4, "блок мусить бути вирівняний по 4 байти");

/* Адреси з розділу «Memory map» */
inline constexpr std::uintptr_t usart1_address = 0x4001'3800;
inline constexpr std::uintptr_t dbgmcu_address = 0xE004'2000;

/* TDR приймає 8 або 9 значущих бітів */
inline constexpr std::uint32_t tdr_mask = 0x1FF;

[[nodiscard]] inline Block &usart1() noexcept
{
    return mmio::block<Block>(usart1_address);
}

/* Гасіння прапорців: один запис у ICR і бар'єр. Read-modify-write над ISR
 * тут неможливий за побудовою — у нього просто немає такого оператора. */
inline void clear(Block &regs, Icr flags) noexcept
{
    regs.icr.store(flags);
    mmio::data_sync_barrier();
}

/* Переклад піднятих помилок ISR у біти гасіння ICR. Позиції збігаються,
 * але це властивість цього блока, а не закон — тому перекладаємо явно. */
[[nodiscard]] constexpr Icr to_clear(Isr errors) noexcept
{
    Icr result = Icr::none;

    if (any(errors & Isr::pe))  { result |= Icr::pecf;  }
    if (any(errors & Isr::fe))  { result |= Icr::fecf;  }
    if (any(errors & Isr::nf))  { result |= Icr::ncf;   }
    if (any(errors & Isr::ore)) { result |= Icr::orecf; }
    return result;
}

} // namespace usart
