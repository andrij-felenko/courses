/* net_client.c — місця виклику застарілого API.
 *
 * Це вхід для sed/migrate_api.sed: виклики навмисно розірвані переносами,
 * мають довільні відступи й коментарі всередині списку аргументів — саме так
 * вони й виглядають у реальній кодовій базі. */
#include "net_api.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    const uint8_t *bytes;
    size_t         length;
} net_frame_t;

/* Багаторядковий виклик: сам по собі жоден рядок повного виклику не містить,
   тому однорядковий s/// тут безсилий. */
int send_urgent(net_conn_t *conn, net_frame_t frame) {
    int rc = net_send_packet(conn,
                             frame.bytes,      /* тіло кадру */
                             frame.length,
                             NET_FLAG_URGENT | NET_FLAG_NODELAY,
                             500);
    if (rc < 0) {
        fprintf(stderr, "net_client: кадр не пішов: %s\n", strerror(errno));
        return -1;
    }
    return rc;
}

/* Однорядковий виклик — той самий інтерфейс, інше форматування. */
int send_keepalive(net_conn_t *conn) {
    static const uint8_t ping[] = { 0x00 };
    int rc = net_send_packet(conn, ping, sizeof ping, 0u, 100);
    return rc < 0 ? -1 : 0;
}
