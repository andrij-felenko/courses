void loop() {
    // 1) блимати рівно раз на 500 мс — неблокувально, на millis()
    static uint32_t last = 0;
    if (millis() - last >= 500) {
        last += 500;
        digitalWrite(LED, !digitalRead(LED));
    }
    // 2) відповісти на запит — а ця бібліотека блокує зсередини
    if (server.hasRequest()) {
        handleRequest();      // всередині ~200 мс: читає, рахує, шле
    }
}
