uint32_t lastTelemetry = 0;

float readBattery();   // ваш давач: напруга акумулятора у вольтах

void loop() {
    // 1) читати команди (як вище)
    while (btSerial.available()) handleCommand(btSerial.read());

    // 2) раз на секунду слати телеметрію — БЕЗ delay
    uint32_t now = millis();
    if (now - lastTelemetry >= 1000) {
        lastTelemetry = now;

        float bat = readBattery();
        // "BAT:7.42 SPD:6\r\n" — той самий формат, що читає застосунок телефона
        btSerial.print("BAT:");
        btSerial.print(bat, 2);          // два знаки після коми
        btSerial.print(" SPD:");
        btSerial.print(speedLevel);
        btSerial.print("\r\n");          // кінець рядка — застосунок ріже потік по ньому
    }
}
