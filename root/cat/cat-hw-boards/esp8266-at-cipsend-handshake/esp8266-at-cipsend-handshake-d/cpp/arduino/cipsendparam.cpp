#include <Arduino.h>

struct CipsendParam {
    bool isMultiplex;
    uint8_t linkId;
    uint16_t length;
    String remoteIp;
    uint16_t remotePort;
};

String buildCipsendCommand(const CipsendParam& param) {
    String cmd = "AT+CIPSEND=";
    
    if (param.isMultiplex) {
        cmd += String(param.linkId) + ",";
    }
    
    cmd += String(param.length);
    
    if (param.remoteIp.length() > 0) {
        cmd += ",\"" + param.remoteIp + "\"," + String(param.remotePort);
    }
    
    cmd += "\r\n";
    return cmd;
}
