/* link.h — байтовий канал до шлюзу плюс кадрувальник із ресинхронізацією.
 *
 * TCP тут стоїть замість UART: обидва віддають ПОТІК байтів без меж
 * повідомлень, тож приймач мусить сам знаходити початок кадру.
 */
#ifndef LINK_H
#define LINK_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "frame.h"

#define LINK_RX_CAP 64u   /* трьох кадрів вистачає: сміття ми не накопичуємо */

typedef struct {
    int      fd;
    uint8_t  rx[LINK_RX_CAP];
    size_t   rx_len;
    uint32_t resync_drops;   /* скільки байтів довелося викинути на пошуку межі */
} link_t;

/* 0 — з'єднано, -1 — ні (причину друкує сама функція). */
int  link_connect(link_t *lk, const char *host, const char *port);
void link_close(link_t *lk);

/* Дописує кадр цілком, доганяючи часткові записи. 0 — гаразд, -1 — канал упав. */
int  link_send_frame(link_t *lk, const uint8_t frame[FRAME_SIZE]);

/* 1 — кадр у out, 0 — за timeout_ms нічого не прийшло, -1 — канал закрито.
   Усередині: пошук 0xAA, добір 15 байтів, перевірка CRC, зсув на байт при невдачі. */
int  link_read_frame(link_t *lk, uint8_t out[FRAME_SIZE], int timeout_ms);

#endif /* LINK_H */
