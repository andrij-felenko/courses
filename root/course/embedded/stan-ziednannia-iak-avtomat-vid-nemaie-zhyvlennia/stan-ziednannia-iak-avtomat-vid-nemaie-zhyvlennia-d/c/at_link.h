#ifndef AT_LINK_H
#define AT_LINK_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Рівень лінії: кільцевий буфер UART, апаратний контроль потоку та
   неблокуючий розбір рядків. Про стани автомата не знає нічого —
   віддає класифіковані повідомлення модема. */

typedef enum {
    AT_MSG_OK = 0,
    AT_MSG_ERROR,      /* голий ERROR без коду */
    AT_MSG_CME_ERROR,  /* value = числовий код CME/CMS */
    AT_MSG_PROMPT,     /* '>' від AT+CIPSEND, без CRLF */
    AT_MSG_BOOT,       /* RDY / *ATREADY — модем стартував САМ */
    AT_MSG_CPIN,       /* value = CPIN_* */
    AT_MSG_CREG,       /* value = <stat> реєстрації */
    AT_MSG_CSQ,        /* value = рівень сигналу в дБм */
    AT_MSG_IP_READY,   /* +CGPADDR віддав ненульову адресу */
    AT_MSG_CONNECT_OK,
    AT_MSG_SEND_OK,
    AT_MSG_CLOSED,
    AT_MSG_PDP_DEACT,
    AT_MSG_DATA,       /* тіло пакета з сокета (+IPD) */
    AT_MSG_UNKNOWN
} at_msg_kind_t;

/* Значення для AT_MSG_CPIN */
#define CPIN_READY    0
#define CPIN_NEED_PIN 1
#define CPIN_ABSENT   2

/* +CSQ: 99 означає "виміряти не вдалося" */
#define RSSI_UNKNOWN 127

typedef struct {
    at_msg_kind_t  kind;
    int32_t        value;
    const uint8_t *data; /* лише для AT_MSG_DATA */
    size_t         len;
} at_msg_t;

void at_link_init(void);

/* Викликається з переривання UART: лише кладе байт і смикає RTS. */
void at_link_rx_isr(uint8_t byte);

/* Неблокуючий розбір: true → у *out готове повідомлення. */
bool at_link_poll(at_msg_t *out);

void at_link_send_line(const char *cmd); /* дописує CR LF */
void at_link_send_raw(const uint8_t *data, size_t len);

uint32_t at_link_overflows(void); /* скільки байтів утрачено на переповненні */

#endif /* AT_LINK_H */
