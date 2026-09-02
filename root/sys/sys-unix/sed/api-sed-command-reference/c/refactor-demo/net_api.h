/* net_api.h — застарілий C-інтерфейс мережевого стека.
 *
 * Це «було» для рецепта масової міграції: покажчик і довжина йдуть окремими
 * аргументами, прапорці й таймаут — двома безіменними числами в хвості, а
 * помилка повертається як int зі знаком. Саме такі виклики розшукує й
 * переписує sed/migrate_api.sed. */
#ifndef NET_API_H
#define NET_API_H

#include <stddef.h>
#include <stdint.h>

#define NET_FLAG_URGENT   0x01u
#define NET_FLAG_NODELAY  0x02u

typedef struct net_conn net_conn_t;

/* Повертає кількість надісланих байтів або -1, причина лишається в errno.
   Пара (data, len) нічим не зв'язана: якщо довжина лишиться від попереднього
   буфера, компілятор не скаже жодного слова. */
int net_send_packet(net_conn_t *conn, const uint8_t *data, size_t len,
                    uint32_t flags, uint32_t timeout_ms);

#endif /* NET_API_H */
