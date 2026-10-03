#include <Arduino.h>
#include "lwip/netconn.h"
#include "lwip/ip_addr.h"

class AtSocketTranslator {
public:
    static bool parseAndConnect(const String& args) {
        int firstComma = args.indexOf(',');
        int secondComma = args.indexOf(',', firstComma + 1);
        int thirdComma = args.indexOf(',', secondComma + 1);

        if (firstComma == -1 || secondComma == -1 || thirdComma == -1) {
            return false;
        }

        int linkId = args.substring(0, firstComma).toInt();
        String type = args.substring(firstComma + 2, secondComma - 1);
        String ipStr = args.substring(secondComma + 2, thirdComma - 1);
        uint16_t port = args.substring(thirdComma + 1).toInt();

        ip_addr_t remoteIp;
        if (!ipaddr_aton(ipStr.c_str(), &remoteIp)) {
            return false;
        }

        struct netconn* conn = netconn_new(NETCONN_TCP);
        if (!conn) {
            return false;
        }

        err_t err = netconn_connect(conn, &remoteIp, port);
        if (err != ERR_OK) {
            netconn_delete(conn);
            return false;
        }
        return true;
    }
};
