// надійно (TCP): кожен байт дійде, по порядку
WiFiClient tcp;
tcp.connect(serverIP, 1883);
tcp.print(command);            // з'єднання й повтори — усередині

// швидко (UDP): шлеш і не чекаєш
WiFiUDP udp;
udp.beginPacket(serverIP, port);
udp.write(telemetry, len);     // може загубитись — і байдуже
udp.endPacket();
