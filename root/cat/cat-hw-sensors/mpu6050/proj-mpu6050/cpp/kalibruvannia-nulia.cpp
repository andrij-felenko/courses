void calibrateGyro() {
    const int N = 2000;              // скільки зразків усереднити
    long sumX = 0, sumY = 0, sumZ = 0;

    Serial.println(F("Калібрую гіроскоп — НЕ РУХАЙ плату 5 секунд..."));
    delay(1000);                     // дати руці прибратись, платі — заспокоїтись

    for (int i = 0; i < N; i++) {
        mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
        sumX += gx;  sumY += gy;  sumZ += gz;
        delay(2);                    // ~2 мс між зразками
    }

    gyroBiasX = sumX / (float)N;     // середнє = сталий зсув нуля
    gyroBiasY = sumY / (float)N;
    // gyroBiasZ = sumZ / (float)N;  // за потреби

    Serial.print(F("Зсув нуля гіроскопа: "));
    Serial.print(gyroBiasX); Serial.print(' ');
    Serial.println(gyroBiasY);
}
