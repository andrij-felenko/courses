/* Драйвер передавача USART поверх регістрової карти.
 *
 * Тут і тільки тут живе логіка: обчислення дільника, обхід дефекту з
 * Errata Sheet, очікування з верхньою межею, гасіння прапорців через W1C.
 */
#ifndef USART_DRIVER_H
#define USART_DRIVER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "silicon_rev.h"
#include "usart_regs.h"

typedef enum {
    USART_OK = 0,
    USART_ERR_BAUD,     /* дільник не влазить у BRR — швидкість недосяжна */
    USART_ERR_TIMEOUT,  /* передавач не звільнив буфер за відведений час  */
    USART_ERR_LINE      /* апаратура підняла прапорець помилки лінії      */
} usart_status_t;

typedef struct {
    usart_regs_t     *regs;
    uint32_t          spin_limit;    /* стеля очікування TXE/TC у прохідках циклу */
    volatile uint32_t sticky_errors; /* помилки, зняті обробником переривання     */
} usart_t;

/* Налаштувати передавач: дільник, UE|TE, обхід дефекту за ревізією.
 * Повертає USART_ERR_BAUD, якщо потрібна швидкість недосяжна від pclk_hz. */
usart_status_t usart_init_tx(usart_t *dev, usart_regs_t *regs,
                             uint32_t pclk_hz, uint32_t baud);

/* Дозволити переривання по прийому (CR1.RXNEIE) */
void usart_enable_rx_irq(usart_t *dev);

/* Відправити один байт, дочекавшись вільного буфера передачі */
usart_status_t usart_send_byte(usart_t *dev, uint8_t byte);

/* Відправити буфер. У *sent (якщо не NULL) лягає кількість відданих байтів:
 * при таймауті посеред рядка це єдиний спосіб дізнатися, де воно стало. */
usart_status_t usart_send(usart_t *dev, const uint8_t *data, size_t len,
                          size_t *sent);

/* Дочекатися, поки останній байт вийде в лінію, і погасити TC.
 * Без цього скидання живлення чи зміна швидкості обрізає символ на льоту. */
usart_status_t usart_flush(usart_t *dev);

/* Забрати накопичені помилки лінії: і ті, що обробник переривання вже
 * погасив у ICR та відклав у sticky_errors, і ті, що стоять у ISR просто
 * зараз. Повертає маску бітів ISR (0 — помилок не було) і лишає лічильник
 * порожнім. Викликається з головного циклу, не з переривання. */
uint32_t usart_take_errors(usart_t *dev);

/* Обробник переривання блока. sink викликається на кожен прийнятий байт;
 * NULL означає «байт прочитати й викинути» — читати RDR однаково треба,
 * інакше наступний символ дасть переповнення. */
void usart_irq_handler(usart_t *dev, void (*sink)(uint8_t byte));

#endif /* USART_DRIVER_H */
