#include <ESP8266WiFi.h>
extern "C" {
  #include "lwip/raw32/espconn.h"
}

static struct espconn nativeConn;
static esp_tcp nativeTcp;

// Callback прийому даних без блокування циклу
void onDataReceived(void *arg, char *pdata, unsigned short len) {
    struct espconn *conn = (struct espconn *)arg;
    // Обробка отриманого пакета pdata довжиною len
    espconn_sent(conn, (uint8_t*)"OK

", 4);
}

void initRawAsyncSocket() {
    nativeConn.type = ESPCONN_TCP;
    nativeConn.state = ESPCONN_NONE;
    nativeConn.proto.tcp = &nativeTcp;
    nativeTcp.local_port = 8080;
    
    espconn_regist_recvcb(&nativeConn, onDataReceived);
    espconn_accept(&nativeConn);
}
