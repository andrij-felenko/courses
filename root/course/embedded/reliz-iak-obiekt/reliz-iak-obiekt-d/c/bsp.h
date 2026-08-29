#ifndef BSP_H
#define BSP_H

#include <stdint.h>
#include <stddef.h>

/* Геометрія Flash конкретного виробу. Ці числа — не «налаштування»:
   вони зашиті в лінкерний скрипт застосунку, і дескриптор мусить із ними
   збігатися, інакше образ зібрано під іншу карту пам'яті. */
#define BSP_FLASH_BASE        0x08000000u
#define BSP_FLASH_SIZE        (2048u * 1024u)

#define BSP_APP_HEADER_ADDR   0x08020000u                        /* 128 КБ під завантажувач */
#define BSP_APP_PAYLOAD_ADDR  (BSP_APP_HEADER_ADDR + 128u)       /* тіло — одразу за дескриптором */
#define BSP_APP_MAX_PAYLOAD   (896u * 1024u)                     /* решта банку A */

#define BSP_RAM_BASE          0x20000000u
#define BSP_RAM_SIZE          (128u * 1024u)

/* Ідентифікатор виробу зашивається на збірці завантажувача: одна плата —
   один код. Зміна коду означає новий виріб, а не нову опцію. */
#ifndef BSP_HW_PLATFORM_ID
#define BSP_HW_PLATFORM_ID    0x0000A110u   /* датчик тиску */
#endif

void     bsp_early_init(void);

uint32_t bsp_hw_platform_id(void);

/* Ревізія плати, зчитана зі strapping-виводів. */
uint8_t  bsp_pcb_revision(void);

/* Монотонний лічильник безпеки в OTP: скільки рівнів уже пропалено. */
uint32_t bsp_security_counter(void);

/* Пропалює OTP до рівня level. 0 — успіх, -1 — відмова Flash або
   спроба зменшити лічильник. Операція незворотна. */
int      bsp_security_counter_commit(uint32_t level);

/* Кореневий відкритий ключ (32 байти) з OTP. NULL — пристрій не
   персоналізований на заводі, ключа немає. */
const uint8_t *bsp_root_public_key(void);

/* Читання з внутрішньої Flash із контролем меж. 0 — успіх. */
int      bsp_flash_read(uint32_t address, void *dst, size_t len);

void     bsp_led(int on);
void     bsp_delay_ms(uint32_t ms);

#endif /* BSP_H */
