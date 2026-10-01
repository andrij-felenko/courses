#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

WiFiUDP udp;
char packetBuffer[255];

void setup_udp() {
    udp.begin(4210);
}

void process_udp() {
    int packetSize = udp.parsePacket();
    if (packetSize) {
        int len = udp.read(packetBuffer, 255);
        if (len > 0) {
            packetBuffer[len] = 0;
        }
        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.write("ACK");
        udp.endPacket();
    }
}
