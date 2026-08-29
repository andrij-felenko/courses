#include <cstdint>

#include "board.hpp"
#include "firmware_descriptor.hpp"
#include "release_verifier.hpp"

/* Точка входу завантажувача: перевірити реліз, зафіксувати рівень безпеки
   й передати керування застосунку. Нічого іншого тут не робиться. */

namespace {

volatile std::uint32_t& scb_vtor     = *reinterpret_cast<volatile std::uint32_t*>(0xE000ED08u);
volatile std::uint32_t& systick_ctrl = *reinterpret_cast<volatile std::uint32_t*>(0xE000E010u);
auto* const nvic_icer = reinterpret_cast<volatile std::uint32_t*>(0xE000E180u);
auto* const nvic_icpr = reinterpret_cast<volatile std::uint32_t*>(0xE000E280u);

/* Останню відмову лишаємо в RAM під фіксованим іменем: у полі плата
   мовчить, а на столі відлагоджувач читає цей рядок за символом. */
volatile const char* g_last_boot_error = nullptr;

[[noreturn]] void halt_with_code(fw::VerifyError error) noexcept
{
    g_last_boot_error = fw::describe(error).data();

    /* Пристрій лишається в завантажувачі й моргає номером відмови. Стрибати
       в неперевірений образ не можна ні за яких обставин: саме це й було
       причиною задимлених транзисторів. */
    for (;;) {
        for (unsigned i = 0; i < static_cast<unsigned>(error); ++i) {
            board::led(true);
            board::delay_ms(200);
            board::led(false);
            board::delay_ms(200);
        }
        board::delay_ms(1500);
    }
}

[[noreturn]] void jump_to_application(std::uint32_t payload_address,
                                      std::uint32_t payload_size) noexcept
{
    /* Перші два слова образу — це початок таблиці векторів: верхівка стека
       й адреса Reset_Handler. */
    const auto* vectors = reinterpret_cast<volatile const std::uint32_t*>(payload_address);
    const std::uint32_t stack_top = vectors[0];
    const std::uint32_t reset_pc  = vectors[1];

    if (stack_top < board::ram_base || stack_top > board::ram_base + board::ram_size) {
        halt_with_code(fw::VerifyError::BadGeometry);
    }
    /* Молодший біт адреси на Cortex-M мусить бути одиницею — це ознака
       набору Thumb; нуль означав би миттєвий HardFault. */
    if ((reset_pc & 1u) == 0u ||
        reset_pc < payload_address || reset_pc >= payload_address + payload_size) {
        halt_with_code(fw::VerifyError::BadGeometry);
    }

    /* Гасимо все, що встиг увімкнути завантажувач: інакше перше ж
       переривання прилетить у застосунок, який ще не готовий його прийняти. */
    asm volatile("cpsid i" ::: "memory");
    systick_ctrl = 0;
    for (unsigned i = 0; i < 8; ++i) {
        nvic_icer[i] = 0xFFFFFFFFu;
        nvic_icpr[i] = 0xFFFFFFFFu;
    }

    scb_vtor = payload_address;                    // вектори тепер застосунку
    asm volatile("dsb" ::: "memory");
    asm volatile("isb" ::: "memory");
    asm volatile("cpsie i" ::: "memory");

    /* Стек перемикаємо й одразу стрибаємо: після запису MSP наш власний
       кадр стека вже не існує, торкатися локальних змінних не можна. */
    asm volatile(
        "msr msp, %0\n\t"
        "bx  %1\n"
        :
        : "r"(stack_top), "r"(reset_pc)
        : "memory");

    __builtin_unreachable();
}

}  // namespace

extern "C" int main()
{
    board::early_init();

    const auto& descriptor =
        *reinterpret_cast<const fw::Descriptor*>(board::app_header_address);

    if (const auto verdict = fw::verify_release(descriptor); !verdict) {
        halt_with_code(verdict.error());
    }

    /* Образ визнано справжнім — тепер підіймаємо апаратний лічильник до
       рівня цього релізу. Палимо ПІСЛЯ повної перевірки: пропалена комірка
       не відкочується, а образ, що не пройшов перевірку, не має права
       закривати шлях старим версіям. */
    if (descriptor.security_version > board::security_counter()) {
        if (!board::burn_security_counter(descriptor.security_version)) {
            halt_with_code(fw::VerifyError::FlashIo);
        }
    }

    jump_to_application(board::app_payload_address, descriptor.payload_size);
}
