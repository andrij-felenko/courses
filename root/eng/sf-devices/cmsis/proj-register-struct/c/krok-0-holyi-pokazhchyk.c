#include <stdint.h>

#define RCC_AHB1ENR   (*(volatile uint32_t *) 0x40023830u)  /* тактування шини AHB1 */
#define GPIOA_MODER   (*(volatile uint32_t *) 0x40020000u)  /* режим виводів порту A */
#define GPIOA_BSRR    (*(volatile uint32_t *) 0x40020018u)  /* атомарний set/reset   */
#define GPIOC_IDR     (*(volatile uint32_t *) 0x40020810u)  /* вхідні дані порту C   */

int main(void)
{
    RCC_AHB1ENR |= (1u << 0) | (1u << 2);   /* увімкнути такт GPIOA і GPIOC */

    GPIOA_MODER &= ~(3u << (5 * 2));        /* очистити двобітове поле MODER5 */
    GPIOA_MODER |=  (1u << (5 * 2));        /* 01 = цифровий вихід            */

    GPIOA_BSRR = (1u << 5);                 /* підняти PA5 */

    uint32_t pc13 = (GPIOC_IDR >> 13) & 1u; /* прочитати PC13 */
    (void) pc13;

    for (;;) { }
}
