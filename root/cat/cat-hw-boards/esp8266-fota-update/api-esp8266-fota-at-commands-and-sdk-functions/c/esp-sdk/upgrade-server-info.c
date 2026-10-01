#include "upgrade.h"

void start_fota_update(const char *server_ip, uint16_t port) {
    struct upgrade_server_info *server = 
        (struct upgrade_server_info *)os_zalloc(sizeof(struct upgrade_server_info));
    
    uint8_t user_bin = system_upgrade_userbin_check();
    if (user_bin == UPGRADE_FW_BIN1) {
        os_sprintf(server->url, "GET /v1/user2.bin HTTP/1.1\r\nHost: %s\r\n\r\n", server_ip);
    } else {
        os_sprintf(server->url, "GET /v1/user1.bin HTTP/1.1\r\nHost: %s\r\n\r\n", server_ip);
    }

    server->sockaddrin.sin_port = htons(port);
    server->check_cb = fota_callback;
    server->check_times = 120000; // таймаут 120 с
    
    system_upgrade_start(server);
}
