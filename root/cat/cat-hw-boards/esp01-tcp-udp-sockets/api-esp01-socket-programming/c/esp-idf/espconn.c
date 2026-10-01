#include "espconn.h"

static struct espconn user_conn;
static esp_tcp user_tcp_proto;

static void ICACHE_FLASH_ATTR user_recv_cb(void *arg, char *pdata, unsigned short len) {
    struct espconn *pespconn = (struct espconn *)arg;
    /* Асинхронне відправлення відповіді у зворотній сокет */
    espconn_send(pespconn, (uint8_t *)"ACK", 3);
}

void user_socket_init(void) {
    user_conn.type = ESPCONN_TCP;
    user_conn.state = ESPCONN_NONE;
    user_conn.proto.tcp = &user_tcp_proto;
    user_tcp_proto.local_port = 8080;
    
    espconn_regist_recvcb(&user_conn, user_recv_cb);
    espconn_accept(&user_conn);
}
