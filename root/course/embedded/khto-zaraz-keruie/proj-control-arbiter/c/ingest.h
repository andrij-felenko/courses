#ifndef INGEST_H
#define INGEST_H

#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

#include "arbiter.h"

/* Поштова скринька на один кадр уставки: пише обробник переривання UART/DMA,
   читає польотний цикл. М'ютекса тут бути не може — цикл не має права стати
   на замок, узятий перериванням, а переривання не має права чекати взагалі.
   Тому подвійний буфер (ping-pong): ISR заповнює тіньовий слот і атомарно
   перемикає індекс, а цикл забирає той, що вже опубліковано. */
typedef struct {
    setpoint_t           slot[2];
    atomic_uint_fast32_t seq;    /* лічильник публікацій; зростає з кожним кадром */
    atomic_uint_fast32_t front;  /* який слот зараз читати */
    uint32_t             seen;   /* поля нижче — тільки для споживача, без атомів */
    uint32_t             dropped;/* кадри, які цикл не встиг забрати */
    uint32_t             torn;   /* копії, перервані новою публікацією */
} sp_mailbox_t;

void     sp_mailbox_init(sp_mailbox_t *mb);
void     sp_mailbox_publish(sp_mailbox_t *mb, const setpoint_t *sp);  /* з переривання */
bool     sp_mailbox_take(sp_mailbox_t *mb, setpoint_t *out);          /* з циклу */
uint32_t sp_mailbox_dropped(const sp_mailbox_t *mb);
uint32_t sp_mailbox_torn(const sp_mailbox_t *mb);

#endif /* INGEST_H */
