#include "bsp.h"
#include "fw_header.h"
#include "fw_verify.h"

#include <stdint.h>

/* Точка входу завантажувача: перевірити реліз, зафіксувати рівень безпеки
   й передати керування застосунку. Нічого іншого тут не робиться. */

#define SCB_VTOR      (*(volatile uint32_t *)0xE000ED08u)
#define SYSTICK_CTRL  (*(volatile uint32_t *)0xE000E010u)
#define NVIC_ICER     ((volatile uint32_t *)0xE000E180u)
#define NVIC_ICPR     ((volatile uint32_t *)0xE000E280u)

/* Останню відмову лишаємо в RAM під фіксованим іменем: у полі плата
   мовчить, а на столі відлагоджувач читає цей рядок за символом. */
volatile const char *g_last_boot_error = 0;

static void halt_with_code(fw_verify_t code)
{
    g_last_boot_error = fw_verify_message(code);

    /* Пристрій лишається в завантажувачі й моргає номером відмови. Стрибати
       в неперевірений образ не можна ні за яких обставин: саме це й було
       причиною задимлених транзисторів. */
    for (;;) {
        for (unsigned i = 0; i < (unsigned)code; i++) {
            bsp_led(1);
            bsp_delay_ms(200u);
            bsp_led(0);
            bsp_delay_ms(200u);
        }
        bsp_delay_ms(1500u);
    }
}

static void jump_to_application(uint32_t payload_addr, uint32_t payload_size)
{
    /* Перші два слова образу — це початок таблиці векторів: верхівка стека
       й адреса Reset_Handler. */
    const uint32_t stack_top = *(volatile uint32_t *)(uintptr_t)payload_addr;
    const uint32_t reset_pc  = *(volatile uint32_t *)(uintptr_t)(payload_addr + 4u);

    if (stack_top < BSP_RAM_BASE || stack_top > BSP_RAM_BASE + BSP_RAM_SIZE) {
        halt_with_code(FW_ERR_BAD_GEOMETRY);
    }
    /* Молодший біт адреси на Cortex-M мусить бути одиницею — це ознака
       набору Thumb; нуль означав би миттєвий HardFault. */
    if ((reset_pc & 1u) == 0u ||
        reset_pc < payload_addr || reset_pc >= payload_addr + payload_size) {
        halt_with_code(FW_ERR_BAD_GEOMETRY);
    }

    /* Гасимо все, що встиг увімкнути завантажувач: інакше перше ж
       переривання прилетить у застосунок, який ще не готовий його прийняти. */
    __asm volatile ("cpsid i" ::: "memory");
    SYSTICK_CTRL = 0u;
    for (unsigned i = 0; i < 8u; i++) {
        NVIC_ICER[i] = 0xFFFFFFFFu;
        NVIC_ICPR[i] = 0xFFFFFFFFu;
    }

    SCB_VTOR = payload_addr;                       /* вектори тепер застосунку */
    __asm volatile ("dsb" ::: "memory");
    __asm volatile ("isb" ::: "memory");
    __asm volatile ("cpsie i" ::: "memory");

    /* Стек перемикаємо й одразу стрибаємо: після запису MSP наш власний
       кадр стека вже не існує, торкатися локальних змінних не можна. */
    __asm volatile (
        "msr msp, %0\n\t"
        "bx  %1\n"
        :
        : "r" (stack_top), "r" (reset_pc)
        : "memory");

    for (;;) {
    }
}

int main(void)
{
    const fw_header_t *hdr = (const fw_header_t *)(uintptr_t)BSP_APP_HEADER_ADDR;
    fw_verify_t rc;

    bsp_early_init();

    rc = fw_verify_release(hdr, BSP_APP_PAYLOAD_ADDR);
    if (rc != FW_OK) {
        halt_with_code(rc);
    }

    /* Образ визнано справжнім — тепер підіймаємо апаратний лічильник до
       рівня цього релізу. Палимо ПІСЛЯ повної перевірки: пропалена комірка
       не відкочується, а образ, що не пройшов перевірку, не має права
       закривати шлях старим версіям. */
    if (hdr->security_version > bsp_security_counter()) {
        if (bsp_security_counter_commit(hdr->security_version) != 0) {
            halt_with_code(FW_ERR_FLASH_IO);
        }
    }

    jump_to_application(BSP_APP_PAYLOAD_ADDR, hdr->payload_size);
    return 0;
}
