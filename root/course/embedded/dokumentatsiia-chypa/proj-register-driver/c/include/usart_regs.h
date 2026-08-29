/* Карта регістрів USART, знята з Reference Manual.
 *
 * Цей заголовок — механічний переказ таблиці регістрів з документації
 * і більше нічого: жодної логіки тут немає. Кожне поле структури мусить
 * стояти рівно за тим зміщенням, яке надрукував виробник, тому нижче
 * стоять _Static_assert — компілятор звіряє структуру з таблицею замість
 * нас. Помилка на один регістр у такій карті дає не падіння, а тихе
 * псування сусіднього блока периферії, і шукають її тижнями.
 */
#ifndef USART_REGS_H
#define USART_REGS_H

#include <stddef.h>
#include <stdint.h>

/* Карта адрес, розділ «Memory map» Reference Manual */
#define PERIPH_BASE        0x40000000UL
#define APB2PERIPH_BASE    (PERIPH_BASE + 0x00010000UL)
#define USART1_BASE        (APB2PERIPH_BASE + 0x00003800UL) /* 0x40013800 */
#define DBGMCU_BASE        0xE0042000UL

/* Регістрова карта блока USART.
 *
 * volatile на кожному полі — не прикраса: без нього оптимізатор має право
 * зчитати ISR один раз перед циклом очікування й крутити порожній `b .`
 * до кінця світу. uint32_t — бо блок відображений на APB 32-бітними
 * словами, і STRB у такий регістр дає BusFault або спотворення сусідніх
 * бітів. Дірок у структурі бути не може: усі поля йдуть підряд по 4 байти.
 */
typedef struct {
    volatile uint32_t CR1;  /* +0x00 Control register 1        R/W */
    volatile uint32_t CR2;  /* +0x04 Control register 2        R/W */
    volatile uint32_t CR3;  /* +0x08 Control register 3        R/W */
    volatile uint32_t BRR;  /* +0x0C Baud rate register        R/W */
    volatile uint32_t GTPR; /* +0x10 Guard time and prescaler  R/W */
    volatile uint32_t RTOR; /* +0x14 Receiver timeout          R/W */
    volatile uint32_t RQR;  /* +0x18 Request register          WO  */
    volatile uint32_t ISR;  /* +0x1C Interrupt and status      RO  */
    volatile uint32_t ICR;  /* +0x20 Interrupt flag clear      WO/W1C */
    volatile uint32_t RDR;  /* +0x24 Receive data register     RO  */
    volatile uint32_t TDR;  /* +0x28 Transmit data register    WO  */
} usart_regs_t;

/* Звірка структури з таблицею Reference Manual на етапі компіляції */
_Static_assert(offsetof(usart_regs_t, CR1) == 0x00, "CR1 має стояти за +0x00");
_Static_assert(offsetof(usart_regs_t, BRR) == 0x0C, "BRR має стояти за +0x0C");
_Static_assert(offsetof(usart_regs_t, ISR) == 0x1C, "ISR має стояти за +0x1C");
_Static_assert(offsetof(usart_regs_t, ICR) == 0x20, "ICR має стояти за +0x20");
_Static_assert(offsetof(usart_regs_t, RDR) == 0x24, "RDR має стояти за +0x24");
_Static_assert(offsetof(usart_regs_t, TDR) == 0x28, "TDR має стояти за +0x28");
_Static_assert(sizeof(usart_regs_t) == 0x2C, "блок USART займає 0x2C байтів");
_Static_assert(_Alignof(usart_regs_t) == 4, "блок мусить бути вирівняний по 4 байти");

/* CR1 — керування */
#define USART_CR1_UE       (1UL << 0)  /* дозвіл роботи блока            */
#define USART_CR1_TE       (1UL << 3)  /* дозвіл передавача              */
#define USART_CR1_RXNEIE   (1UL << 5)  /* дозвіл переривання по прийому  */

/* ISR — стан. Біти 3:0 — помилки, вони W1C через ICR; решта тут RO. */
#define USART_ISR_PE       (1UL << 0)  /* помилка парності               */
#define USART_ISR_FE       (1UL << 1)  /* помилка кадру                  */
#define USART_ISR_NF       (1UL << 2)  /* виявлено шум у лінії           */
#define USART_ISR_ORE      (1UL << 3)  /* переповнення приймача          */
#define USART_ISR_RXNE     (1UL << 5)  /* у RDR лежить прийнятий байт    */
#define USART_ISR_TC       (1UL << 6)  /* передачу завершено             */
#define USART_ISR_TXE      (1UL << 7)  /* буфер передачі порожній        */
#define USART_ISR_ERRORS   (USART_ISR_PE | USART_ISR_FE | USART_ISR_NF | USART_ISR_ORE)

/* ICR — гасіння прапорців. Запис «1» скидає, запис «0» не робить нічого. */
#define USART_ICR_PECF     (1UL << 0)
#define USART_ICR_FECF     (1UL << 1)
#define USART_ICR_NCF      (1UL << 2)
#define USART_ICR_ORECF    (1UL << 3)
#define USART_ICR_TCCF     (1UL << 6)
#define USART_ICR_ERRORS   (USART_ICR_PECF | USART_ICR_FECF | USART_ICR_NCF | USART_ICR_ORECF)

/* TDR приймає 8 або 9 значущих бітів; старші відкидає апаратура */
#define USART_TDR_MASK     0x1FFUL

/* Регістр ідентифікації кремнію (DBGMCU_IDCODE):
 * DEV_ID [11:0] — модель чипа, REV_ID [31:16] — ревізія кремнію. */
typedef struct {
    volatile uint32_t IDCODE; /* +0x00 */
} dbgmcu_regs_t;

_Static_assert(sizeof(dbgmcu_regs_t) == 4, "IDCODE — одне 32-бітне слово");

#define USART1  ((usart_regs_t *)USART1_BASE)
#define DBGMCU  ((dbgmcu_regs_t *)DBGMCU_BASE)

/* Бар'єр синхронізації даних.
 *
 * Запис у периферію на Cortex-M потрапляє в буфер запису й доїжджає до
 * блока асинхронно. Після гасіння прапорця в кінці обробника переривання
 * без цього бар'єра ядро встигає вийти з обробника раніше, ніж скидання
 * добіжить шиною, — NVIC бачить прапорець досі активним і викликає той
 * самий обробник удруге.
 */
static inline void usart_dsb(void)
{
    __asm__ volatile("dsb sy" ::: "memory");
}

/* Гасіння прапорців через ICR — єдиний правильний спосіб.
 *
 * Ніякого read-modify-write над ISR: між читанням і зворотним записом
 * апаратура встигає підняти інший прапорець (класично RXNE), і запис
 * стирає подію, якої програма навіть не бачила. Запис у ICR — це імпульс
 * скидання рівно для названих тригерів, решта не зачеплена.
 */
static inline void usart_clear_flags(usart_regs_t *regs, uint32_t icr_mask)
{
    regs->ICR = icr_mask;
    usart_dsb();
}

#endif /* USART_REGS_H */
